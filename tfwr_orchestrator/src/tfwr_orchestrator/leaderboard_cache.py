"""读取 Steam 公开排行榜，只缓存排名/毫秒成绩，按与第十名的差距生成研究参考。"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import OpenerDirector, ProxyHandler, Request, build_opener
import xml.etree.ElementTree as ET

from .config import (
    LEADERBOARD_CACHE_PATH,
    LEADERBOARD_REFERENCE_ROOT,
    LEADERBOARD_REPORT_PATH,
    REPO_ROOT,
    normalize_config_path,
)

APP_ID = 2060160
SCHEMA_VERSION = 1
PAGE_SIZE = 100
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
# Steam 社区榜单 ID；与游戏 Leaderboards 枚举和 lb_*.py 一一对应。
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
}


@dataclass(frozen=True)
class RankEntry:
    """公开排名及游戏时间，time_ms 为整数毫秒，不含玩家身份。"""

    rank: int
    time_ms: int


@dataclass(frozen=True)
class BoardSnapshot:
    """单榜连续前 N 名快照，保留来源、实际总人数及 UTC 抓取时间。"""

    script: str
    source: str
    retrieved_at: str
    total_entries: int
    entries: tuple[RankEntry, ...]


@dataclass(frozen=True)
class LocalResult:
    """仓库复跑索引中的参考成绩及来源行；不表示本次重新实测。"""

    time_ms: int
    line: int


def board_url(script: str) -> str:
    """从固定榜单映射生成 Steam 官方来源地址。"""
    return f"https://steamcommunity.com/stats/{APP_ID}/leaderboards/{BOARD_IDS[script]}/"


def validate_snapshot(board: BoardSnapshot, limit: int) -> None:
    """拒绝缺页、乱序和非法时间，防止不完整响应成为新的有效缓存。"""
    if board.source != board_url(board.script):
        raise ValueError(f"{board.script}: 缓存来源与榜单 ID 不一致，请重新刷新。")
    if type(board.total_entries) is not int or board.total_entries < 0:
        raise ValueError(f"{board.script}: total_entries 必须是非负整数。")
    if datetime.fromisoformat(board.retrieved_at).utcoffset() is None:
        raise ValueError(f"{board.script}: retrieved_at 必须包含时区。")
    if len(board.entries) != min(limit, board.total_entries):
        raise ValueError(f"{board.script}: 排名覆盖不完整，请保留旧缓存并重试刷新。")
    previous = 0
    for rank, entry in enumerate(board.entries, start=1):
        if type(entry.rank) is not int or entry.rank != rank:
            raise ValueError(f"{board.script}: 排名必须从 1 连续递增，异常位置 {rank}。")
        if type(entry.time_ms) is not int or entry.time_ms <= 0 or entry.time_ms < previous:
            raise ValueError(f"{board.script}: #{rank} 成绩必须是正整数毫秒且按时间升序。")
        previous = entry.time_ms


def read_public_page(opener: OpenerDirector, url: str, timeout: float) -> bytes:
    """只对网络中断、限流和临时服务错误最多尝试三次；不重试格式错误。"""
    request = Request(url, headers={"User-Agent": "TFWR-Orchestrator/0.1", "Accept": "application/xml"})
    for attempt in range(3):
        try:
            with opener.open(request, timeout=timeout) as response:
                payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise ValueError("响应超过 2 MiB 上限")
            return payload
        except (OSError, URLError) as exc:
            if attempt == 2 or (isinstance(exc, HTTPError) and exc.code not in {429, 500, 502, 503, 504}):
                raise
            # 公开只读请求可重试；短退避避免瞬时 TLS 中断让整份缓存无法更新。
            print(f"网络读取中断，将重试 {attempt + 2}/3：{url}；{exc}", file=sys.stderr, flush=True)
            time.sleep(attempt + 1)
    raise AssertionError("unreachable retry state")


def fetch_leaderboards(limit: int, timeout: float, proxy: str | None) -> tuple[BoardSnapshot, ...]:
    """有界读取全部榜单；任一请求失败则向上传播，不写入部分刷新结果。"""
    handler = ProxyHandler({"http": proxy, "https": proxy}) if proxy else ProxyHandler()
    opener = build_opener(handler)
    boards = []
    for script in BOARD_IDS:
        source = board_url(script)
        entries: list[RankEntry] = []
        total: int | None = None
        for start in range(1, limit + 1, PAGE_SIZE):
            end = min(limit, start + PAGE_SIZE - 1)
            url = f"{source}?xml=1&start={start}&end={end}"
            print(f"读取 {script} #{start}–#{end}", file=sys.stderr, flush=True)
            try:
                root = ET.fromstring(read_public_page(opener, url, timeout))
                if root.findtext("appID") != str(APP_ID) or root.findtext("leaderboardID") != str(BOARD_IDS[script]):
                    raise ValueError("返回内容不是请求的 TFWR 榜单")
                page_total = int(root.findtext("totalLeaderboardEntries", ""))
                page = tuple(
                    RankEntry(int(row.findtext("rank", "")), int(row.findtext("score", "")))
                    for row in root.findall("./entries/entry")
                )
                expected = max(0, min(end, page_total) - start + 1)
                if len(page) != expected or int(root.findtext("resultCount", "")) != len(page):
                    raise ValueError(f"响应缺页：预期 {expected} 条，实际 {len(page)} 条")
                if total is not None and page_total != total:
                    raise ValueError("分页期间榜单总条目数变化，请重新刷新")
                total = page_total
                entries.extend(page)
                if end >= total:
                    break
            except (OSError, URLError, ValueError, ET.ParseError) as exc:
                raise RuntimeError(f"读取 {url} 失败：{exc}；旧缓存未更新，可检查网络或 --proxy 后重试。") from exc
        assert total is not None
        board = BoardSnapshot(script, source, datetime.now(timezone.utc).isoformat(), total, tuple(entries))
        validate_snapshot(board, limit)
        boards.append(board)
        print(f"已读取 {script}: {len(entries)}/{total} 条", file=sys.stderr, flush=True)
    return tuple(boards)


def load_cache(path: Path) -> tuple[int, tuple[BoardSnapshot, ...]]:
    """加载并校验完整缓存；旧版或损坏内容明确失败，不冒充空榜。"""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["schema_version"] != SCHEMA_VERSION or raw["app_id"] != APP_ID:
            raise ValueError("缓存版本或游戏 ID 不匹配")
        limit = raw["limit"]
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("缓存 limit 必须在 1..1000")
        boards = []
        for row in raw["boards"]:
            board = BoardSnapshot(
                row["script"], row["source"], row["retrieved_at"], row["total_entries"],
                tuple(RankEntry(entry["rank"], entry["time_ms"]) for entry in row["entries"]),
            )
            validate_snapshot(board, limit)
            boards.append(board)
        if len(boards) != len(BOARD_IDS) or {board.script for board in boards} != set(BOARD_IDS):
            raise ValueError("缓存没有完整覆盖当前 16 个榜单")
        return limit, tuple(boards)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise RuntimeError(f"读取排行榜缓存 {path} 失败：{exc}；请联网运行刷新命令。") from exc


def load_local_results(path: Path) -> dict[str, LocalResult]:
    """读取 lb_start.py 的当前版本复跑列，忽略左侧历史 #1，不执行脚本。"""
    results: dict[str, LocalResult] = {}
    script: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        entry = re.search(r'leaderboard_run\(Leaderboards\.\w+,\s*"(lb_\w+)"', line)
        if entry:
            script = entry.group(1)
        if line.startswith("# 用时（#1/当前版本复跑）："):
            match = re.fullmatch(r"# 用时（#1/当前版本复跑）：[^/]+/\s*(\d+):([0-5]\d)\.(\d{3})\s*", line)
            if match is None or script is None or script in results:
                raise ValueError(f"复跑索引 {path}:{number} 格式无效或重复，请填写 分:秒.毫秒。")
            minutes, seconds, milliseconds = map(int, match.groups())
            value = minutes * 60_000 + seconds * 1000 + milliseconds
            if value <= 0:
                raise ValueError(f"复跑索引 {path}:{number} 成绩必须大于零。")
            results[script] = LocalResult(value, number)
    return results


def format_time(milliseconds: int) -> str:
    """毫秒转为与游戏一致的 分:秒.毫秒，分钟允许超过 59。"""
    minutes, remainder = divmod(milliseconds, 60_000)
    seconds, fraction = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{fraction:03d}"


def estimate_rank(board: BoardSnapshot, time_ms: int) -> str:
    """按缓存时间插入位置估计名次；同分显示区间，未覆盖的尾部只给下界。"""
    times = [entry.time_ms for entry in board.entries]
    if not times:
        return "空榜，无参照"
    lower = bisect_left(times, time_ms)
    upper = bisect_right(times, time_ms)
    if lower == len(times) and len(times) < board.total_entries:
        return f"#{len(times)} 之后"
    if lower < upper:
        if upper == len(times) and len(times) < board.total_entries:
            return f"约 #{lower + 1}–至少 #{upper}（同分）"
        return f"约 #{lower + 1}–#{upper}（同分）" if upper - lower > 1 else f"约 #{lower + 1}（同分）"
    return f"约 #{lower + 1}"


def render_report(
    boards: tuple[BoardSnapshot, ...], results: dict[str, LocalResult], limit: int, report_path: Path
) -> str:
    """生成差距降序报告；排名是成绩位置估计，不声称账户已提交该成绩。"""
    def gap(board: BoardSnapshot) -> float:
        """缺少本地或第十名成绩的榜单排在已知差距之后。"""
        result = results.get(board.script)
        return result.time_ms / board.entries[9].time_ms if result and len(board.entries) >= 10 else -1

    dates = [datetime.fromisoformat(board.retrieved_at).astimezone(timezone.utc).isoformat() for board in boards]
    index_link = Path(os.path.relpath(LEADERBOARD_REFERENCE_ROOT / "lb_start.py", report_path.parent)).as_posix()
    docs_link = Path(os.path.relpath(REPO_ROOT / "tfwr_orchestrator/README.md", report_path.parent)).as_posix()
    lines = [
        "# 排行榜成绩与提升空间", "",
        "以第十名作为可达性研究基准，按“本地复跑参考 ÷ #10 时间”降序排列，差距越大越优先研究。",
        "#1 仅供参考，不代表可达目标；#30/#100 用于判断成绩分布。#10 也不保证可达，候选仍须机制预算和实机验证。缺少 #10 时不计算差距，不回退到 #1。", "",
        f"公开数据抓取时间（UTC）：{min(dates)} 至 {max(dates)}。每榜最多前 {limit} 名；时间为游戏成绩。",
        f"我们的时间读取自 [lb_start.py]({index_link}) 的“当前版本复跑”；这是仓库记录，非本次全榜重测。",
        "估计位置按缓存中的更快成绩数量计算，不识别玩家账户；并列显示同分范围，超出缓存范围不外推。", "",
        "| 榜单 | #1（参考） | #10（基准） | #30 | #100 | 我们的复跑参考 | 估计位置 | 相对 #10 | 追平 #10 需缩短 | 缓存/总条目 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for board in sorted(boards, key=lambda item: (-gap(item), item.script)):
        checkpoints = []
        for rank in (1, 10, 30, 100):
            if rank <= len(board.entries):
                checkpoints.append(format_time(board.entries[rank - 1].time_ms))
            else:
                checkpoints.append("不足此名次" if rank > board.total_entries else "未缓存")
        result = results.get(board.script)
        if result:
            ours = f"[{format_time(result.time_ms)}]({index_link}#L{result.line})"
            position = estimate_rank(board, result.time_ms)
        else:
            ours, position = "未记录", "未知"
        ratio = gap(board)
        relative = f"{ratio:.3f}×" if ratio >= 0 else "—"
        reduction = f"{max(0.0, 1 - 1 / ratio):.1%}" if ratio > 0 else "—"
        name = board.script.removeprefix("lb_").replace("_", " ").title()
        cells = [f"[{name}]({board.source})", *checkpoints, ours, position, relative, reduction,
                 f"{len(board.entries)}/{board.total_entries}"]
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend([
        "", "此表由 `refresh_leaderboard_cache.py` 生成；修改复跑索引后可用 `--offline` 重新计算，联网刷新失败时保留旧缓存。",
        f"读取方式、缓存位置和代理配置见 [协调器说明]({docs_link}#排行榜缓存)。", "",
    ])
    return "\n".join(lines)


def write_atomic(path: Path, text: str) -> None:
    """同目录临时文件写完后原子替换单个文件，异常时清理临时文件。"""
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
    """刷新完整公共缓存或离线重建报告；不启动游戏，也不提交排行榜成绩。"""
    parser = argparse.ArgumentParser(description="缓存 TFWR 各榜前 N 名时间，比较 #1/#10/#30/#100 和本地复跑位置。")
    parser.add_argument("--limit", type=int, default=100, help="每榜最多读取条数，默认 100，范围 1..1000。")
    parser.add_argument("--offline", action="store_true", help="仅使用现有缓存和当前复跑索引重建报告，不联网。")
    parser.add_argument("--timeout", type=float, default=20, help="每次网络操作超时秒数，默认 20，范围 (0,60]。")
    parser.add_argument("--proxy", help="可选 HTTP/HTTPS 代理 URL；未指定时使用系统/环境代理。")
    parser.add_argument("--cache", default=str(LEADERBOARD_CACHE_PATH), help="排行榜 JSON 缓存路径。")
    parser.add_argument("--report", default=str(LEADERBOARD_REPORT_PATH), help="生成的 Markdown 报告路径。")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 1000:
        parser.error("--limit 必须在 1..1000。")
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 60:
        parser.error("--timeout 必须是 (0,60] 内的有限秒数。")
    cache_path = normalize_config_path(args.cache)
    report_path = normalize_config_path(args.report)
    if cache_path.resolve() == report_path.resolve():
        parser.error("--cache 与 --report 必须是不同文件。")
    try:
        results = load_local_results(LEADERBOARD_REFERENCE_ROOT / "lb_start.py")
        if args.offline:
            limit, boards = load_cache(cache_path)
        else:
            limit = args.limit
            boards = fetch_leaderboards(limit, args.timeout, args.proxy)
        # 先准备并验证全部内容，网络失败不会破坏已有缓存。JSON 是真源，报告可离线重建。
        report = render_report(boards, results, limit, report_path)
        if not args.offline:
            payload = {"schema_version": SCHEMA_VERSION, "app_id": APP_ID, "limit": limit,
                       "boards": [asdict(board) for board in boards]}
            write_atomic(cache_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        write_atomic(report_path, report)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"排行榜更新失败：{exc}", file=sys.stderr)
        return 1
    print(f"排行榜缓存：{cache_path}\n比较报告：{report_path}\n榜单数：{len(boards)}；每榜上限：{limit}")
    return 0
