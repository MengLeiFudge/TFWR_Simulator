"""读取常规和地下公开榜，核对当前账号，并从同一份数据生成进度文档。"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import OpenerDirector, ProxyHandler, Request, build_opener
import xml.etree.ElementTree as ET

from .config import (
    LEADERBOARD_CACHE_PATH,
    LEADERBOARD_DOCS_ROOT,
    LEADERBOARD_LOCAL_PROGRESS_PATH,
    LEADERBOARD_PROGRESS_PATH,
    LEADERBOARD_SNAPSHOT_PATH,
    normalize_config_path,
    resolve_steam_manifest_path,
)

APP_ID = 2060160
SCHEMA_VERSION = 2
PAGE_SIZE = 100
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
# Steam社区榜单ID，与游戏Leaderboards枚举及lb_*.py对应。
BOARD_IDS = {
    "lb_cactus": 17869881,
    "lb_cactus_single": 17827398,
    "lb_carrots": 17869887,
    "lb_carrots_single": 17827400,
    "lb_dinosaur": 17869889,
    "lb_fastest_reset": 17869903,
    "lb_hay": 17869890,
    "lb_hay_single": 17827401,
    "lb_maze": 17869891,
    "lb_maze_single": 17827402,
    "lb_pumpkins": 17869892,
    "lb_pumpkins_single": 17827408,
    "lb_sunflowers": 17869894,
    "lb_sunflowers_single": 17827413,
    "lb_wood": 17869895,
    "lb_wood_single": 17827415,
    "lb_bamboo": 21488263,
    "lb_bamboo_single": 21444624,
    "lb_rice": 21444638,
    "lb_rice_single": 21444639,
    "lb_ores": 21444636,
    "lb_ores_single": 21444637,
    "lb_mushrooms": 21444618,
    "lb_mushrooms_single": 21444535,
    "lb_dynamite": 21444631,
    "lb_dynamite_single": 21444632,
    "lb_pyramids": 21488014,
    "lb_pyramids_single": 21488443,
    "lb_treasure_map": 21469574,
    "lb_fastest_underground_reset": 21444633,
}
RESET_BOARDS = {"lb_fastest_reset", "lb_fastest_underground_reset"}
# 兼容保留：若 leaderboard_progress.md 含扩展附录则原样保留，缺省不附加。
HISTORY_HEADING = "## 历史完整统计与研究\n"


@dataclass(frozen=True)
class RankEntry:
    """公开排名及整数毫秒成绩，不含玩家身份。"""

    rank: int
    time_ms: int


@dataclass(frozen=True)
class AccountSnapshot:
    """账号核对事实；identity仅为LastOwner摘要，用于阻止不同账号混用缓存。"""

    status: str = "unverified"
    retrieved_at: str | None = None
    rank: int | None = None
    time_ms: int | None = None
    identity: str | None = None
    refresh_error: str | None = None


@dataclass(frozen=True)
class BoardSnapshot:
    """连续前N名及实际抓取时间；刷新失败时保留原事实和日期。"""

    script: str
    source: str
    retrieved_at: str
    total_entries: int
    entries: tuple[RankEntry, ...]
    limit: int = 100
    account: AccountSnapshot = AccountSnapshot()
    refresh_error: str | None = None
    transport: str = "steam_xml"


@dataclass(frozen=True)
class LocalProgress:
    """研究记录中的最好有效模拟时间、依据和下一步方向。"""

    label: str
    simulation_seconds: float | None
    simulation_basis: str
    evidence: str
    direction: str


def board_url(script: str) -> str:
    return f"https://steamcommunity.com/stats/{APP_ID}/leaderboards/{BOARD_IDS[script]}/"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_date(value: str) -> None:
    if datetime.fromisoformat(value).utcoffset() is None:
        raise ValueError("抓取时间必须包含时区。")


def validate_snapshot(board: BoardSnapshot, limit: int | None = None) -> None:
    """拒绝缺页、乱序、非法成绩及互相矛盾的账号记录。"""
    if board.script not in BOARD_IDS or board.source != board_url(board.script):
        raise ValueError(f"{board.script}: 来源与榜单ID不一致。")
    if board.transport not in {"steam_xml", "steamworks"}:
        raise ValueError(f"{board.script}: 排行榜读取来源无效。")
    limit = board.limit if limit is None else limit
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError(f"{board.script}: limit必须在1..1000。")
    if type(board.total_entries) is not int or board.total_entries < 0:
        raise ValueError(f"{board.script}: 总人数必须是非负整数。")
    validate_date(board.retrieved_at)
    if len(board.entries) != min(limit, board.total_entries):
        raise ValueError(f"{board.script}: 排名覆盖不完整。")
    previous = 0
    for rank, entry in enumerate(board.entries, start=1):
        if type(entry.rank) is not int or entry.rank != rank:
            raise ValueError(f"{board.script}: 排名必须从1连续递增。")
        if type(entry.time_ms) is not int or entry.time_ms <= 0 or entry.time_ms < previous:
            raise ValueError(f"{board.script}: #{rank}成绩必须为正整数毫秒并按时间升序。")
        previous = entry.time_ms
    account = board.account
    if account.status not in {"listed", "not_listed", "unverified"}:
        raise ValueError(f"{board.script}: 账号核对状态无效。")
    if account.status == "unverified":
        if any(value is not None for value in (account.rank, account.time_ms, account.retrieved_at, account.identity)):
            raise ValueError(f"{board.script}: 未核实账号不能携带成绩或查询时间。")
        return
    if account.retrieved_at is None or account.identity is None or not re.fullmatch(r"[a-f0-9]{64}", account.identity):
        raise ValueError(f"{board.script}: 已核实账号缺少日期或身份摘要。")
    validate_date(account.retrieved_at)
    if account.status == "not_listed":
        if account.rank is not None or account.time_ms is not None:
            raise ValueError(f"{board.script}: 未上榜账号不能携带成绩。")
        return
    if (type(account.rank) is not int or not 1 <= account.rank <= board.total_entries
            or type(account.time_ms) is not int or account.time_ms <= 0):
        raise ValueError(f"{board.script}: 账号成绩或名次无效。")
    if account.rank <= len(board.entries) and board.entries[account.rank - 1].time_ms != account.time_ms:
        raise ValueError(f"{board.script}: 账号成绩与公开排名不一致。")


def read_public_page(opener: OpenerDirector, url: str, timeout: float) -> bytes:
    """有限重试只读请求；不在日志中输出含账号的请求地址。"""
    request = Request(url, headers={
        "User-Agent": "TFWR-Orchestrator/0.2", "Accept": "application/xml",
        "Cache-Control": "no-cache", "Pragma": "no-cache",
    })
    for attempt in range(3):
        try:
            with opener.open(request, timeout=timeout) as response:
                payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise ValueError("响应超过2MiB上限。")
            return payload
        except (OSError, URLError) as exc:
            if attempt == 2 or (isinstance(exc, HTTPError) and exc.code not in {429, 500, 502, 503, 504}):
                raise
            print(f"公开请求中断（{type(exc).__name__}），重试{attempt + 2}/3。", file=sys.stderr, flush=True)
            time.sleep(attempt + 1)
    raise AssertionError("unreachable retry state")


def read_entries(opener: OpenerDirector, script: str, query: dict[str, str | int], timeout: float) -> tuple[int, list[ET.Element]]:
    """每次请求使用新查询标记，校验XML归属与返回条数后才读取成绩。"""
    url = board_url(script) + "?" + urlencode({"xml": 1, **query, "refresh": time.time_ns()})
    root = ET.fromstring(read_public_page(opener, url, timeout))
    if root.findtext("appID") != str(APP_ID) or root.findtext("leaderboardID") != str(BOARD_IDS[script]):
        raise ValueError("响应不是请求的TFWR榜单。")
    total = int(root.findtext("totalLeaderboardEntries", ""))
    rows = root.findall("./entries/entry")
    if total < 0 or int(root.findtext("resultCount", "")) != len(rows):
        raise ValueError("响应总人数或条目计数无效。")
    return total, rows


def account_identity(owner: str) -> str:
    return hashlib.sha256(owner.encode("ascii")).hexdigest()


def error_text(exc: Exception, owner: str | None) -> str:
    text = f"{type(exc).__name__}: {exc}"
    return text.replace(owner, "[account]") if owner else text


def fetch_board(script: str, limit: int, timeout: float, proxy: str | None,
                owner: str | None, previous: BoardSnapshot | None) -> BoardSnapshot:
    """公开事实和账号核对独立更新；账号查询失败保留同身份的旧账号日期。"""
    opener = build_opener(ProxyHandler({"http": proxy, "https": proxy}) if proxy else ProxyHandler())
    entries: list[RankEntry] = []
    own_rows: list[ET.Element] = []
    total: int | None = None
    for start in range(1, limit + 1, PAGE_SIZE):
        end = min(limit, start + PAGE_SIZE - 1)
        page_total, rows = read_entries(opener, script, {"start": start, "end": end}, timeout)
        if len(rows) != max(0, min(end, page_total) - start + 1):
            raise ValueError("公开响应缺页。")
        if total is not None and total != page_total:
            raise ValueError("分页期间榜单人数变化。")
        total = page_total
        entries.extend(RankEntry(int(row.findtext("rank", "")), int(row.findtext("score", ""))) for row in rows)
        if owner:
            own_rows.extend(row for row in rows if row.findtext("steamid") == owner)
        if end >= total:
            break
    assert total is not None
    board = BoardSnapshot(script, board_url(script), utc_now(), total, tuple(entries), limit)
    validate_snapshot(board)
    if not owner:
        return board
    try:
        if not own_rows and len(entries) < total:
            account_total, rows = read_entries(opener, script, {"steamid": owner}, timeout)
            if account_total != total:
                raise ValueError("账号查询期间榜单人数变化。")
            own_rows = [row for row in rows if row.findtext("steamid") == owner]
            if rows and not own_rows:
                raise ValueError("账号响应未包含请求的账号，不能判定未上榜。")
        if len(own_rows) > 1:
            raise ValueError("同榜出现多条当前账号记录。")
        if own_rows:
            row = own_rows[0]
            account = AccountSnapshot("listed", utc_now(), int(row.findtext("rank", "")),
                                      int(row.findtext("score", "")), account_identity(owner))
        else:
            account = AccountSnapshot("not_listed", utc_now(), identity=account_identity(owner))
        board = replace(board, account=account)
        validate_snapshot(board)
    except (OSError, URLError, ValueError, ET.ParseError) as exc:
        account = previous.account if previous and previous.account.identity == account_identity(owner) else AccountSnapshot()
        # 旧名次可能已越界或与新公开成绩冲突；此时不能继续称为当前账号记录。
        try:
            validate_snapshot(replace(board, account=account))
        except ValueError:
            account = AccountSnapshot()
        board = replace(board, account=replace(account, refresh_error=error_text(exc, owner)))
    return board


def load_cache(path: Path, identity: str | None) -> dict[str, BoardSnapshot]:
    """读取事实缓存；兼容旧16榜结构，缺榜保持缺失，不伪造空榜。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw["schema_version"] not in {1, SCHEMA_VERSION} or raw["app_id"] != APP_ID:
        raise ValueError("缓存版本或游戏ID不匹配。")
    boards = {}
    for row in raw["boards"]:
        account = AccountSnapshot(**row.get("account", {}))
        board = BoardSnapshot(
            row["script"], row["source"], row["retrieved_at"], row["total_entries"],
            tuple(RankEntry(**entry) for entry in row["entries"]), row.get("limit", raw.get("limit", 100)),
            account, row.get("refresh_error"), row.get("transport", "steam_xml"),
        )
        validate_snapshot(board)
        if board.script in boards:
            raise ValueError(f"重复缓存榜单：{board.script}。")
        if identity is None or account.identity != identity:
            board = replace(board, account=AccountSnapshot())
        boards[board.script] = board
    return boards


def load_local_progress(path: Path) -> dict[str, LocalProgress]:
    """只读取结构化研究状态，不把历史正式复跑当成账号成绩或模拟。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw["schema_version"] != 1 or set(raw["boards"]) != set(BOARD_IDS):
        raise ValueError("本地研究状态必须完整覆盖当前30榜。")
    results = {}
    for script, row in raw["boards"].items():
        result = LocalProgress(**row)
        seconds = result.simulation_seconds
        if seconds is not None and (type(seconds) not in {int, float} or not math.isfinite(seconds) or seconds <= 0):
            raise ValueError(f"{script}: 模拟时间须为正的有限游戏秒或null。")
        if not all(isinstance(text, str) and text.strip() for text in
                   (result.label, result.simulation_basis, result.evidence, result.direction)):
            raise ValueError(f"{script}: 缺少榜名、模拟依据、证据或改进方向。")
        results[script] = result
    return results


def format_time(milliseconds: int) -> str:
    minutes, remainder = divmod(milliseconds, 60_000)
    seconds, fraction = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{fraction:03d}"


def format_account(account: AccountSnapshot) -> str:
    if account.status == "not_listed":
        return "未上榜"
    if account.time_ms is not None:
        return f"{format_time(account.time_ms)}（#{account.rank}）"
    return "未核实"


def checkpoint(board: BoardSnapshot | None, rank: int, best_seconds: float | None = None) -> str:
    if board is None or not board.entries:
        return "未取得"
    if rank <= len(board.entries):
        entry = board.entries[rank - 1]
        suffix = ""
    elif rank > board.total_entries:
        entry = board.entries[-1]
        suffix = f"（#{entry.rank}，末名）"
    else:
        return "未缓存"
    label = format_time(entry.time_ms)
    if best_seconds is not None:
        label += f"（{(best_seconds * 1000 / entry.time_ms - 1) * 100:+.1f}%）"
    return label + suffix


def best_time(board: BoardSnapshot | None, result: LocalProgress) -> float | None:
    values = [result.simulation_seconds] if result.simulation_seconds is not None else []
    if board is not None and board.account.time_ms is not None:
        values.append(board.account.time_ms / 1000)
    return min(values) if values else None


def relative_time(board: BoardSnapshot | None, result: LocalProgress) -> float | None:
    if board is None or not board.entries:
        return None
    seconds = best_time(board, result)
    return seconds * 1000 / board.entries[0].time_ms if seconds is not None else None


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def document_link(path: Path, output: Path) -> str:
    return Path(os.path.relpath(path, output.parent)).as_posix()


def render_report(boards: dict[str, BoardSnapshot], results: dict[str, LocalProgress],
                  refreshed: set[str], output: Path, title: str, offline: bool,
                  local_path: Path = LEADERBOARD_LOCAL_PROGRESS_PATH,
                  snapshot_path: Path = LEADERBOARD_SNAPSHOT_PATH) -> str:
    """从公开缓存与研究状态生成七列进度表；门槛判断使用原始精度。"""
    dates = sorted(datetime.fromisoformat(board.retrieved_at).astimezone(timezone.utc).isoformat() for board in boards.values())
    ratios = {script: relative_time(boards.get(script), result) for script, result in results.items()}
    reached = sum(ratio is not None and ratio <= 2 for script, ratio in ratios.items() if script not in RESET_BOARDS)
    mode = "公开缓存离线重建" if offline else f"本次联网刷新 {len(refreshed)}/30 榜"
    date_note = f"公开数据 UTC 范围：`{dates[0]}` 至 `{dates[-1]}`。" if dates else "尚无有效公开数据。"
    lines = [f"# {title}", "", f"{mode}。{date_note}每榜查询时间与账号核对见[公开快照]({document_link(snapshot_path, output)})。", "",
             "时间为游戏时间 `分钟:秒.毫秒`。`实机` 为当前账号公开最高记录及排名，`模拟` 为本地最佳有效预估。#1、#3、#10 时间后的百分比为 `(min(实机,模拟)/该名次时间-1)×100%`，正数表示我们更慢，负数表示我们更快；名次不足时按显示的末名时间计算，无可比实机和模拟时只显示公开时间。", "",
             f"28 个非重置榜中 {reached} 榜在 2×#1 以内；执行顺序见[三阶段计划]({document_link(LEADERBOARD_DOCS_ROOT / 'strategy_review.md', output)}#三阶段计划)，本地模拟与研究方向编辑入口为[研究状态 JSON]({document_link(local_path, output)})。", ""]
    for underground, heading in ((False, "常规排行榜"), (True, "地下排行榜")):
        lines.extend([f"## {heading}", "", "| 排行榜 | 实机 | 模拟 | #1 | #3 | #10 | 改进方向 |",
                      "| --- | ---: | ---: | ---: | ---: | ---: | --- |"])
        scripts = [script for script in BOARD_IDS if (BOARD_IDS[script] >= 21000000) == underground]
        scripts.sort(key=lambda script: (script in RESET_BOARDS, -(ratios[script] or -1), script))
        for script in scripts:
            board, result = boards.get(script), results[script]
            best_seconds = best_time(board, result)
            simulation = format_time(round(result.simulation_seconds * 1000)) if result.simulation_seconds is not None else "未取得"
            name = f"[{cell(result.label)}]({document_link(LEADERBOARD_DOCS_ROOT / (script + '.md'), output)})"
            lines.append("| " + " | ".join((name, format_account(board.account) if board else "未核实", simulation,
                         checkpoint(board, 1, best_seconds), checkpoint(board, 3, best_seconds),
                         checkpoint(board, 10, best_seconds), cell(result.direction))) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_snapshot(boards: dict[str, BoardSnapshot], refreshed: set[str], offline: bool,
                    output: Path = LEADERBOARD_SNAPSHOT_PATH,
                    cache_path: Path = LEADERBOARD_CACHE_PATH,
                    progress_path: Path = LEADERBOARD_PROGRESS_PATH) -> str:
    mode = "公开缓存离线重建。" if offline else f"本次联网刷新 {len(refreshed)}/30 榜。"
    lines = ["# 排行榜公开成绩与当前账号快照", "",
             f"{mode}事实真源为[公开缓存]({document_link(cache_path, output)})（仅存名次、毫秒成绩、查询时间与账号摘要），模拟与改进方向见[排行榜进度]({document_link(progress_path, output)})。", "",
             "| 脚本 | 公开来源 | 公开查询UTC | 公开人数 | #1 | #3 | #10 | 账号最高 | 账号核对UTC |",
             "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for script in BOARD_IDS:
        board = boards.get(script)
        if board is None:
            lines.append(f"| {script} | [Steam]({board_url(script)}) | 未取得 | — | 未取得 | 未取得 | 未取得 | 未核实 | 未取得 |")
            continue
        account = board.account
        source = "Steam SDK" if board.transport == "steamworks" else "Steam网页"
        lines.append(f"| {script} | [{source}]({board.source}) | {board.retrieved_at} | {board.total_entries} | "
                     f"{checkpoint(board, 1)} | {checkpoint(board, 3)} | {checkpoint(board, 10)} | {format_account(account)} | {account.retrieved_at or '未核实'} |")
    errors = [(script, kind, error) for script, board in boards.items()
              for kind, error in (("公开成绩", board.refresh_error), ("账号核对", board.account.refresh_error)) if error]
    if errors:
        lines.extend(["", "最近刷新未完成项：", ""])
        lines.extend(f"- {script} {kind}：{cell(error)}" for script, kind, error in errors)
    lines.append("")
    return "\n".join(lines)


def write_atomic(path: Path, text: str) -> None:
    """同目录临时文件写完后原子替换；JSON是事实真源，文档可离线重建。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="刷新TFWR常规及地下30榜，核对账号并同步七列进度文档。")
    parser.add_argument("--script", action="append", choices=tuple(BOARD_IDS), help="仅刷新指定榜，可重复；默认全部30榜。")
    parser.add_argument("--limit", type=int, default=100, help="每榜前N名，默认100，范围1..1000。")
    parser.add_argument("--offline", action="store_true", help="不联网，使用事实缓存及研究状态重建进度与公开快照。")
    parser.add_argument("--steam", action="store_true", help="通过游戏随附Steam SDK只读刷新；需要64位Windows Python及已登录的Steam客户端，无需启动游戏。")
    parser.add_argument("--timeout", type=float, default=20, help="每次网络操作超时，默认20秒，范围(0,60]。")
    parser.add_argument("--proxy", help="HTTP/HTTPS代理URL；省略时使用系统或环境代理。")
    parser.add_argument("--cache", default=str(LEADERBOARD_CACHE_PATH), help="公开事实JSON路径。")
    parser.add_argument("--progress", default=str(LEADERBOARD_PROGRESS_PATH), help="进度Markdown路径。")
    parser.add_argument("--snapshot", default=str(LEADERBOARD_SNAPSHOT_PATH), help="公开来源及账号查询日期Markdown路径。")
    parser.add_argument("--local-progress", default=str(LEADERBOARD_LOCAL_PROGRESS_PATH), help="本地模拟与研究方向JSON路径。")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 1000:
        parser.error("--limit必须在1..1000。")
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 60:
        parser.error("--timeout必须是(0,60]内的有限秒数。")
    if args.offline and (args.script or args.steam):
        parser.error("--offline不接受--script或--steam；离线重建包含缓存中全部榜。")
    if args.steam and args.proxy:
        parser.error("--steam由Steam客户端联网，不接受--proxy。")
    if args.proxy and urlsplit(args.proxy).scheme not in {"http", "https"}:
        parser.error("--proxy必须是HTTP/HTTPS代理URL。")
    paths = [normalize_config_path(value) for value in (args.cache, args.progress, args.snapshot, args.local_progress)]
    cache_path, progress_path, snapshot_path, local_path = paths
    if len({path.resolve() for path in paths}) != len(paths):
        parser.error("输入与输出路径必须互不相同。")
    try:
        results = load_local_progress(local_path)
        history = ""
        if progress_path.exists():
            existing = progress_path.read_text(encoding="utf-8")
            _, separator, tail = existing.partition(HISTORY_HEADING)
            if separator:
                history = "\n" + separator + tail
        owner = None
        try:
            match = re.search(r'"LastOwner"\s+"([0-9]{17})"', resolve_steam_manifest_path().read_text(encoding="utf-8"))
            owner = match.group(1) if match else None
            if owner is None:
                print("安装清单缺少LastOwner，账号成绩显示未核实。", file=sys.stderr)
        except (OSError, RuntimeError) as exc:
            print(f"无法读取当前账号：{exc}；公开榜仍可读取。", file=sys.stderr)
        if args.offline and not cache_path.is_file():
            raise FileNotFoundError(f"离线模式缺少公开缓存：{cache_path}；请先联网刷新。")
        boards = load_cache(cache_path, account_identity(owner) if owner else None) if cache_path.exists() else {}
        refreshed: set[str] = set()
        failures = 0
        attempted_at = utc_now()
        if not args.offline:
            selected = list(dict.fromkeys(args.script or BOARD_IDS))
            from .leaderboard_steam import SteamLeaderboardReader

            context = SteamLeaderboardReader(owner, args.timeout) if args.steam else nullcontext()
            with context as reader, ThreadPoolExecutor(max_workers=1 if reader else 4) as pool:
                pending = {
                    (pool.submit(reader.fetch, script, args.limit) if reader else
                     pool.submit(fetch_board, script, args.limit, args.timeout, args.proxy,
                                 owner, boards.get(script))): script for script in selected
                }
                for future in as_completed(pending):
                    script = pending[future]
                    try:
                        board = future.result()
                        boards[script] = board
                        refreshed.add(script)
                        if board.account.refresh_error:
                            failures += 1
                        print(f"已刷新{script}：{len(board.entries)}/{board.total_entries}条，账号{board.account.status}。", flush=True)
                    except (OSError, URLError, ValueError, RuntimeError, ET.ParseError) as exc:
                        failures += 1
                        error = error_text(exc, owner)
                        if script in boards:
                            boards[script] = replace(boards[script], refresh_error=error)
                        print(f"{script}刷新失败，保留旧数据及日期：{error}", file=sys.stderr, flush=True)
        if not boards:
            raise RuntimeError("没有有效公开缓存；既有报告未改写。请检查网络或--proxy后刷新。")
        progress = render_report(boards, results, refreshed, progress_path, "排行榜进度", args.offline,
                                 local_path, snapshot_path) + history
        snapshot = render_snapshot(boards, refreshed, args.offline, snapshot_path, cache_path, progress_path)
        if not args.offline:
            payload = {"schema_version": SCHEMA_VERSION, "app_id": APP_ID, "last_attempt_at": attempted_at,
                       "boards": [asdict(boards[script]) for script in BOARD_IDS if script in boards]}
            write_atomic(cache_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        write_atomic(progress_path, progress)
        write_atomic(snapshot_path, snapshot)
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError) as exc:
        print(f"排行榜更新失败：{exc}", file=sys.stderr)
        return 1
    print(f"公开缓存：{cache_path}\n进度：{progress_path}\n公开快照：{snapshot_path}\n有效缓存：{len(boards)}/30榜；本次联网刷新：{len(refreshed)}榜。")
    return 1 if failures else 0
