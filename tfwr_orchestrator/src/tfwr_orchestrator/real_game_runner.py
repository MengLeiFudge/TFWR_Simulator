from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
from collections.abc import Iterator
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import sys
from typing import Any, cast

from .config import (
    load_local_env,
    resolve_bepinex_log_path,
    resolve_bepinex_root,
    resolve_game_root,
    resolve_oracle_state_path,
    resolve_output_path,
    resolve_request_record_path,
    resolve_request_key_path,
    resolve_unity_log_path,
    to_windows_path,
)
from .output_capture import (
    CapturedOutputs,
    LogCursor,
    OutputBaseline,
    capture_output_baseline,
    capture_request_outputs,
    file_signature,
    read_appended_lines,
    read_log_tail,
    serialize_baseline,
    deserialize_baseline,
)


load_local_env()


STATE_IO_MAX_ATTEMPTS = 20
STATE_IO_RETRY_SECONDS = 0.05
LEADERBOARD_SUCCESS_SUMMARY_RE = re.compile(
    r"\[lb_[^\]]+(?:\.py)?\]\s+finished=true\s+runs=[1-9][0-9]*\s+average="
)
LEADERBOARD_SUMMARY_RE = re.compile(
    r"\[lb_[^\]]+(?:\.py)?\]\s+finished=(true|false)\s+runs=([1-9][0-9]*)\s+average=([0-9]+:[0-9]{2}\.[0-9]{3})"
)
LEADERBOARD_RUN_RE = re.compile(
    r"\[lb_[^\]]+(?:\.py)?\]\s+run=([1-9][0-9]*)\s+time=([0-9]+:[0-9]{2}\.[0-9]{3})"
)
CONTROLLED_STOP_PREFIXES = ("reached stable leaderboard runs",)
LEADERBOARD_STABILITY_THRESHOLD = 0.10
RESOURCE_TARGETS_BY_SCRIPT = {
    "lb_hay": (("hay", 2_000_000_000.0),),
    "lb_hay_single": (("hay", 100_000_000.0),),
    "lb_wood": (("wood", 10_000_000_000.0),),
    "lb_wood_single": (("wood", 500_000_000.0),),
    "lb_carrots": (("carrot", 2_000_000_000.0),),
    "lb_carrots_single": (("carrot", 100_000_000.0),),
    "lb_pumpkins": (("pumpkin", 200_000_000.0),),
    "lb_pumpkins_single": (("pumpkin", 10_000_000.0),),
    "lb_cactus": (("cactus", 33554432.0),),
    "lb_cactus_single": (("cactus", 131072.0),),
    "lb_dinosaur": (("bone", 33_488_928.0),),
    "lb_maze": (("gold", 9863168.0),),
    "lb_maze_single": (("gold", 616448.0),),
    "lb_sunflowers": (("power", 100_000.0),),
    "lb_sunflowers_single": (("power", 10_000.0),),
}
ITEM_SNAPSHOT_RE = re.compile(r"\bitem_snapshot\b(?P<body>.*)$")
LEADERBOARD_SCRIPT_RE = re.compile(r"\[(lb_[^\]]+?)(?:\.py)?\]")
REPO_ROOT = Path(__file__).resolve().parents[3]
LEGACY_REPO_ROOT = REPO_ROOT.with_name("tfwr_simulator")
SUSPICIOUS_PYTHON_CPU_SECONDS = 300.0

class TaskError(RuntimeError):
    """携带稳定错误码的任务接口错误；details用于机器读取。"""

    def __init__(self, code, message, **details):
        super().__init__(message)
        self.code = code
        self.details = details


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "启动或复用真实 TFWR 游戏，通过 state.json 请求 Unity 模组执行目标脚本，"
            "并在结束后分别读取脚本 output.txt、BepInEx/LogOutput.log 和 Unity Player.log。"
        )
    )
    parser.add_argument('--action', choices=('run', 'submit', 'status', 'wait', 'cancel', 'result', 'health'),
                        help='AI任务操作；指定后stdout只输出一个JSON对象')
    parser.add_argument('--json', action='store_true', help='使用JSON任务接口；默认执行run')
    parser.add_argument('--request-id', type=int, help='查询、等待、取消或收取的请求ID')
    parser.add_argument('--idempotency-key', help='提交重试键；相同键和参数复用原请求，不重复启动')
    parser.add_argument('--replace', action='store_true', help='明确允许新请求停止并替换当前活动请求')
    parser.add_argument("--game-root", default=None, help="显式指定游戏安装目录。")
    parser.add_argument("--save-root", default=None, help="显式指定 Save0 目录。")
    parser.add_argument(
        "--bepinex-root",
        default=None,
        help="BepInEx 目录，可指向 R2 profile/BepInEx；也可设置 TFWR_BEPINEX_ROOT。R2 模式请先通过 R2 启动游戏。",
    )
    parser.add_argument(
        "--target-script",
        default="lb_start",
        help="要请求执行的脚本窗口名，可带或不带 .py。",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=20.0,
        help="单次请求在模组内运行的超时时间，默认 20 秒。",
    )
    parser.add_argument(
        "--startup-timeout",
        type=float,
        default=30.0,
        help="旧版文本流程等待模组进入idle的最长时间，默认30秒；JSON提交遇忙立即返回。",
    )
    parser.add_argument(
        "--total-timeout",
        type=float,
        default=300.0,
        help="整次等待的最大墙钟时间，默认 300 秒。",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.5,
        help="轮询状态机并在结束后读取 output/log 输出的时间间隔，默认 0.5 秒。",
    )
    parser.add_argument(
        "--output-stall-timeout",
        type=float,
        default=30.0,
        help="请求运行后 BepInEx 日志连续无新增输出的最长墙钟秒数，默认 30 秒；设为 0 可关闭。",
    )
    parser.add_argument(
        "--max-leaderboard-runs",
        type=int,
        default=2,
        help=(
            "打榜迭代验证时至少等待的完成轮数；默认 2。达到该轮数后，"
            "只有最近两轮时间差异不超过 10%% 才主动停止；设为 0 表示不按轮次停止。"
        ),
    )
    parser.add_argument(
        "--request-only",
        action="store_true",
        help="只提交请求并返回；默认拒绝覆盖活动请求，替换须显式加 --replace。"
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help=(
            "读取 state.json、BepInEx 与 Unity 日志尾部；请求尚未结束时默认跳过游戏 output.txt，"
            "避免和游戏 Logger 抢文件句柄。"
        ),
    )
    parser.add_argument(
        "--status-lines",
        type=int,
        default=80,
        help="文本状态和JSON回执中每份输出的尾部行数，默认80；完整结果仍留存。",
    )
    parser.add_argument(
        "--include-game-output",
        action="store_true",
        help="--status-only 即使 state=running 也读取游戏 output.txt；仅在确认游戏不在写日志时使用。",
    )
    args = parser.parse_args(argv)
    for name in ('request_timeout', 'startup_timeout', 'total_timeout', 'poll_interval', 'output_stall_timeout'):
        value = getattr(args, name)
        if not math.isfinite(value) or value < 0 or (name in ('startup_timeout', 'total_timeout', 'poll_interval') and value == 0):
            parser.error(f'{name} 必须是有效的非负秒数；启动/等待/轮询须大于0')
    if args.request_id is not None and not 0 <= args.request_id <= 2147483647:
        parser.error('request-id须为非负Int32')
    if args.max_leaderboard_runs < 0 or args.status_lines < 0:
        parser.error('max-leaderboard-runs和status-lines不能为负数')
    if args.idempotency_key is not None and not 1 <= len(args.idempotency_key.strip()) <= 200:
        parser.error('idempotency-key须为1～200个字符')
    if args.request_only and args.status_only:
        parser.error('request-only与status-only不能同时使用')
    if args.action and (args.request_only or args.status_only):
        parser.error('action不能与request-only/status-only同时使用')
    if args.request_id is not None and args.action not in ('status', 'wait', 'cancel', 'result'):
        parser.error('request-id只能用于status/wait/cancel/result')
    if args.idempotency_key and args.action not in (None, 'run', 'submit'):
        parser.error('idempotency-key只能用于run/submit')
    if args.include_game_output and (args.action or args.json or args.idempotency_key):
        parser.error('JSON任务接口仅在收取终态时读取output.txt，不支持include-game-output')
    if args.idempotency_key and args.status_only:
        parser.error('idempotency-key不能用于status-only')
    if args.replace and (args.status_only or args.action not in (None, 'run', 'submit')):
        parser.error('replace只能用于run/submit')
    return args


def normalize_target_script_name(target_script: str | None) -> str | None:
    if target_script is None:
        return None
    value = target_script.strip()
    if not value:
        return None
    if value.endswith(".py"):
        value = value[:-3]
    return value or None


def build_requested_state(
    *,
    request_id: int,
    target_script: str,
    timeout_seconds: float,
) -> dict[str, object]:
    return {
        "request_id": request_id,
        "status": "requested",
        "target_script": normalize_target_script_name(target_script),
        "timeout_seconds": float(timeout_seconds),
        "started_at": None,
        "finished_at": None,
        "last_error": None,
    }


def build_idle_state(*, request_id: int) -> dict[str, object]:
    return {
        "request_id": request_id,
        "status": "idle",
        "target_script": None,
        "timeout_seconds": None,
        "started_at": None,
        "finished_at": None,
        "last_error": None,
    }


def build_stop_requested_state(current_state: dict[str, object], message: str) -> dict[str, object]:
    return {
        "request_id": cast(int, current_state["request_id"]),
        "status": "stop_requested",
        "target_script": normalize_target_script_name(str(current_state.get("target_script") or "")),
        "timeout_seconds": current_state.get("timeout_seconds"),
        "started_at": current_state.get("started_at"),
        "finished_at": None,
        "last_error": message,
    }


def read_tail_lines(path: Path | None, max_lines: int) -> tuple[str, ...]:
    return read_log_tail(path, max_lines)


def read_text_with_retries(path: Path) -> str:
    last_error: BaseException | None = None
    for attempt in range(STATE_IO_MAX_ATTEMPTS):
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError) as exc:
            last_error = exc
            if attempt + 1 >= STATE_IO_MAX_ATTEMPTS:
                break
            time.sleep(STATE_IO_RETRY_SECONDS)
    raise RuntimeError(f"读取文件失败: {path}") from last_error


def next_request_id(current_state: dict[str, object] | None) -> int:
    """在文件事务内分配递增 ID；缺失状态不能视为新会话。"""
    if current_state is None:
        raise RuntimeError("模组状态文件尚未生成，请先通过对应的 BepInEx/profile 启动游戏。")
    request_id = cast(int, current_state["request_id"]) + 1
    if request_id > 2_147_483_647:
        raise RuntimeError("请求编号已耗尽，请停止客户端和游戏后归档并移除状态文件，再启动游戏。")
    return request_id


def resolve_game_executable(game_root: str | Path | None = None) -> Path:
    root = resolve_game_root(game_root)
    assert root is not None
    candidates = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() == ".exe" and "CrashHandler" not in path.name
    )
    if not candidates:
        raise FileNotFoundError(f"游戏目录下未找到可执行文件: {root}")
    return candidates[0]


def read_state_file(state_path: Path) -> dict[str, object] | None:
    """只有文件不存在时返回 None；损坏或占用不能触发请求编号重置。"""
    last_error: Exception | None = None
    for attempt in range(STATE_IO_MAX_ATTEMPTS):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("状态必须是 JSON 对象")
            request_id = state.get("request_id")
            if type(request_id) is not int or not 0 <= request_id <= 2_147_483_647:
                raise ValueError("request_id 必须是非负的 32 位整数")
            status = state.get("status")
            if not isinstance(status, str) or status not in {"idle", "requested", "running", "stop_requested", "done", "failed", "superseded"}:
                raise ValueError("未知状态 status")
            return state
        except FileNotFoundError:
            return None
        except (ValueError, OSError) as exc:
            last_error = exc
            if attempt + 1 < STATE_IO_MAX_ATTEMPTS:
                time.sleep(STATE_IO_RETRY_SECONDS)
    raise RuntimeError(f"读取状态文件失败，请检查内容和权限: {state_path}") from last_error


@contextmanager
def state_transaction(state_path: Path) -> Iterator[None]:
    """与模组共用独占创建的短时锁；锁内只读改写状态，不等待游戏执行。"""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(str(state_path) + ".lock")
    for attempt in range(STATE_IO_MAX_ATTEMPTS):
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if attempt + 1 >= STATE_IO_MAX_ATTEMPTS:
                raise RuntimeError(
                    f"状态文件锁持续被占用: {lock_path}。若进程异常退出，请先停止游戏和全部客户端，再移除残留锁。"
                ) from None
            time.sleep(STATE_IO_RETRY_SECONDS)
    try:
        os.close(fd)
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def write_state_file(state_path: Path, state: dict[str, object]) -> None:
    """原子替换协议状态或客户端回执；调用方须持有所属状态文件的事务锁。"""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    last_error: BaseException | None = None

    for attempt in range(STATE_IO_MAX_ATTEMPTS):
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                dir=state_path.parent,
                prefix=f"{state_path.name}.",
                suffix=".tmp",
            ) as handle:
                handle.write(payload)
                temp_path = Path(handle.name)
            os.replace(str(temp_path), str(state_path))
            return
        except (OSError, PermissionError) as exc:
            last_error = exc
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            if attempt + 1 >= STATE_IO_MAX_ATTEMPTS:
                break
            time.sleep(STATE_IO_RETRY_SECONDS)

    raise RuntimeError(f"写入状态文件失败: {state_path}") from last_error


def launch_windows_game(exe_path: Path) -> tuple[int, bool]:
    if os.name == "nt":
        process = subprocess.Popen([str(exe_path)])
        return (process.pid, False)

    windows_exe = to_windows_path(exe_path)
    command = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        f"$p = Start-Process -FilePath '{windows_exe}' -PassThru; $p.Id",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    pid_text = completed.stdout.strip().splitlines()[-1]
    return (int(pid_text), True)


def find_game_process_id(process_name: str = "TheFarmerWasReplaced.exe") -> int | None:
    completed = subprocess.run(["tasklist.exe", "/FI", f"IMAGENAME eq {process_name}"], check=False, capture_output=True, timeout=5)
    if completed.returncode != 0:
        return None
    return extract_pid_from_tasklist_output(completed.stdout.decode("utf-8", errors="ignore"), process_name)


def extract_pid_from_tasklist_output(text: str, process_name: str) -> int | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith(process_name):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1])
    return None


def ensure_game_running(exe_path: Path, *, bepinex_root: Path | None = None) -> tuple[int, bool]:
    """手动安装可自动启动；外置 profile 由 R2 负责启动参数。"""
    existing_pid = find_game_process_id(exe_path.name)
    if existing_pid is not None:
        return (existing_pid, False)
    if bepinex_root is not None and bepinex_root.resolve() != (exe_path.parent / "BepInEx").resolve():
        raise RuntimeError(f"请先通过 R2 启动对应 profile 的模组游戏，再连接: {bepinex_root}")
    return launch_windows_game(exe_path)


def acknowledge_terminal_state(state_path: Path, request_id: int | None = None) -> dict[str, object]:
    """只确认锁内仍属于指定请求的终态，不能把后来的请求清成 idle。"""
    with state_transaction(state_path):
        current = read_state_file(state_path)
        if current is None:
            raise FileNotFoundError(f"状态文件不存在: {state_path}")
        if request_id is not None and current["request_id"] != request_id:
            return current
        if current["status"] not in {"done", "failed", "superseded"}:
            return current
        idle_state = build_idle_state(request_id=cast(int, current["request_id"]))
        write_state_file(state_path, idle_state)
        return idle_state


def request_script_stop(state_path: Path, request_id: int, message: str) -> bool:
    """取消仍待启动或正在运行的指定请求；已完成或已被替换时不写入。"""
    with state_transaction(state_path):
        current = read_state_file(state_path)
        if current is None or current["request_id"] != request_id:
            return False
        if current["status"] not in {"requested", "running"}:
            return False
        write_state_file(state_path, build_stop_requested_state(current, message))
        return True


def wait_for_status(
    *,
    state_path: Path,
    pid: int,
    request_id: int,
    accepted_statuses: set[str],
    timeout_seconds: float,
    poll_interval: float,
    baseline: OutputBaseline,
    output_stall_timeout: float,
    max_leaderboard_runs: int,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout_seconds
    last_output_activity_at = time.monotonic()
    last_mod_output_count = 0
    log_cursor = LogCursor(baseline.mod_output_path, baseline.mod_output_signature)
    mod_output_lines: list[str] = []
    run_times: tuple[float, ...] = ()
    next_process_check_at = 0.0
    stop_requested_for_stall = False
    controlled_stop_message: str | None = None
    last_live_progress_at = 0.0
    last_live_progress_line = ""
    request_pattern = re.compile(rf'\brequest_id={request_id}\b')
    while time.monotonic() < deadline:
        loop_now = time.monotonic()
        if loop_now >= next_process_check_at:
            if not is_windows_process_running(pid):
                raise RuntimeError(f"游戏进程已退出: pid={pid}")
            next_process_check_at = loop_now + 1.0
        current = read_state_file(state_path)
        if current is not None:
            current_request_id = cast(int, current["request_id"])
            status = str(current.get("status", ""))
            if current_request_id > request_id or (current_request_id == request_id and status == 'idle'):
                receipt = read_record(resolve_request_record_path(state_path, request_id))
                if receipt and receipt.get('result') is not None:
                    return receipt['result']
            if current_request_id > request_id and "superseded" in accepted_statuses:
                return {
                    "request_id": request_id,
                    "status": "superseded",
                    "target_script": None,
                    "timeout_seconds": None,
                    "started_at": None,
                    "finished_at": current.get("finished_at"),
                    "last_error": f"superseded by request_id={current_request_id}",
                }
            if current_request_id == request_id and status in accepted_statuses:
                if controlled_stop_message is not None and status == "failed":
                    current = dict(current)
                    current["last_error"] = controlled_stop_message
                return current
            if current_request_id == request_id and status == "running":
                appended = log_cursor.read_lines()
                if appended:
                    last_output_activity_at = loop_now
                new_lines = tuple(line for line in appended if request_pattern.search(line))
                if new_lines:
                    mod_output_lines.extend(new_lines)
                    last_mod_output_count += len(new_lines)
                    run_times += parse_leaderboard_run_times(new_lines)

                if loop_now - last_live_progress_at >= 5.0:
                    last_live_progress_at = loop_now
                    live_outputs = CapturedOutputs(
                        game_output_lines=(),
                        mod_output_lines=tuple(mod_output_lines),
                    )
                    live_lines = build_leaderboard_average_lines(live_outputs)
                    if not live_lines:
                        live_lines = build_progress_estimate_lines(live_outputs, None)
                    if live_lines and live_lines[-1] != last_live_progress_line:
                        last_live_progress_line = live_lines[-1]
                        print(f"real_game_runner live {last_live_progress_line}", flush=True)

                completed_runs = len(run_times)
                if (
                    max_leaderboard_runs > 0
                    and completed_runs >= max_leaderboard_runs
                    and leaderboard_runs_are_stable(run_times, LEADERBOARD_STABILITY_THRESHOLD)
                ):
                    average_time = sum(run_times) / completed_runs
                    message = (
                        f"reached stable leaderboard runs {completed_runs} "
                        f"avg={format_leaderboard_seconds(average_time)}"
                    )
                    if not request_script_stop(state_path, request_id, message):
                        continue
                    print(f"real_game_runner stable_runs request_id={request_id} {message}")
                    controlled_stop_message = message
                    max_leaderboard_runs = 0
                elif (
                    output_stall_timeout > 0
                    and
                    not stop_requested_for_stall
                    and loop_now - last_output_activity_at >= output_stall_timeout
                ):
                    message = (
                        f"mod log stalled for {output_stall_timeout:g}s "
                        f"after mod_lines={last_mod_output_count}"
                    )
                    if not request_script_stop(state_path, request_id, message):
                        continue
                    stop_requested_for_stall = True
                    print(f"real_game_runner output_stall request_id={request_id} {message}")
        time.sleep(min(max(0.05, poll_interval), max(0, deadline - time.monotonic())))
    raise TimeoutError(f"等待状态 {sorted(accepted_statuses)} 超时: request_id={request_id} state_path={state_path}")


def wait_for_ready_state(
    *,
    state_path: Path,
    pid: int,
    timeout_seconds: float,
    poll_interval: float,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not is_windows_process_running(pid):
            raise RuntimeError(f"游戏进程已退出: pid={pid}")
        current = read_state_file(state_path)
        if current is not None:
            status = str(current.get("status", ""))
            if status in {"done", "failed", "superseded"}:
                raise RuntimeError(f"请求{current['request_id']}尚未回收；先执行 --action result --request-id {current['request_id']}")
            elif status == "idle":
                return current
        time.sleep(max(0.05, poll_interval))
    raise TimeoutError(f"等待模组进入 idle 超时: state_path={state_path}")


def request_script_run(
    *,
    state_path: Path,
    target_script: str,
    timeout_seconds: float,
    replace_current: bool = False,
) -> int:
    """锁内检查空闲再提交；显式替换才允许覆盖活动请求。"""
    if not math.isfinite(timeout_seconds) or timeout_seconds < 0:
        raise ValueError("request-timeout 必须是非负有限秒数；0 表示不限时。")
    if not normalize_target_script_name(target_script):
        raise ValueError("target-script 不能为空。")
    with state_transaction(state_path):
        current = read_state_file(state_path)
        require_available(current, replace_current)
        request_id = allocate_request_id(state_path, current)
        write_state_file(
            state_path,
            build_requested_state(
                request_id=request_id,
                target_script=target_script,
                timeout_seconds=timeout_seconds,
            ),
        )
        return request_id


def is_windows_process_running(pid: int) -> bool:
    command = ["tasklist" if os.name == "nt" else "tasklist.exe", "/FI", f"PID eq {pid}"]
    completed = subprocess.run(command, check=False, capture_output=True, timeout=5)
    text = completed.stdout.decode("utf-8", errors="ignore")
    return completed.returncode == 0 and str(pid) in text


def terminate_windows_process(pid: int) -> None:
    command = ["taskkill" if os.name == "nt" else "taskkill.exe", "/PID", str(pid), "/T", "/F"]
    subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _print_captured_outputs(outputs: CapturedOutputs, *, game_output_skipped: bool = False) -> None:
    print(f"game_output_lines={len(outputs.game_output_lines)}")
    if game_output_skipped:
        print("game_output skipped state=running reason=avoid_output_lock")
    for line in outputs.game_output_lines:
        print(f"game_output {line}")
    print(f"mod_output_lines={len(outputs.mod_output_lines)}")
    for line in outputs.mod_output_lines:
        print(f"mod_output {line}")
    print(f"unity_log_lines={len(outputs.unity_log_lines)}")
    for line in outputs.unity_log_lines:
        print(f"unity_log {line}")

def target_requires_leaderboard_summary(target_script: str | None) -> bool:
    return normalize_target_script_name(target_script) == "lb_start"


def has_successful_leaderboard_summary(outputs: CapturedOutputs) -> bool:
    return any(
        LEADERBOARD_SUCCESS_SUMMARY_RE.search(line)
        for line in (*outputs.game_output_lines, *outputs.mod_output_lines)
    )


def count_leaderboard_runs(lines: tuple[str, ...]) -> int:
    return len(parse_leaderboard_run_times(lines))


def parse_leaderboard_run_times(lines: tuple[str, ...], include_summary: bool = False) -> tuple[float, ...]:
    run_times: list[float] = []
    for line in lines:
        match = LEADERBOARD_RUN_RE.search(line)
        if match is not None:
            seconds = parse_leaderboard_clock(match.group(2))
            if seconds is not None:
                run_times.append(seconds)
            continue
        if include_summary:
            summary_match = LEADERBOARD_SUMMARY_RE.search(line)
            if summary_match is None:
                continue
            if summary_match.group(1) != "true":
                continue
            seconds = parse_leaderboard_clock(summary_match.group(3))
            if seconds is not None:
                run_times = [seconds] * int(summary_match.group(2))
    return tuple(run_times)


def parse_leaderboard_clock(value: str) -> float | None:
    minute_text, separator, second_text = value.partition(":")
    if separator != ":":
        return None
    try:
        return int(minute_text) * 60.0 + float(second_text)
    except ValueError:
        return None


def format_leaderboard_seconds(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    total_milliseconds = int(seconds * 1000 + 0.5)
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    minutes, second = divmod(total_seconds, 60)
    return f"{minutes}:{second:02d}.{milliseconds:03d}"


def leaderboard_runs_are_stable(run_times: tuple[float, ...], threshold: float) -> bool:
    if len(run_times) < 2:
        return False
    previous_time, latest_time = run_times[-2], run_times[-1]
    baseline = min(previous_time, latest_time)
    if baseline <= 0:
        return False
    return abs(latest_time - previous_time) / baseline <= threshold


def parse_item_snapshot(line: str) -> dict[str, str]:
    match = ITEM_SNAPSHOT_RE.search(line)
    if match is None:
        return {}
    values: dict[str, str] = {}
    for token in match.group("body").strip().split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        values[key] = value
    return values


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def infer_progress_script(outputs: CapturedOutputs, target_script: str | None) -> str | None:
    normalized = normalize_target_script_name(target_script)
    if normalized and normalized != "lb_start":
        return normalized
    combined_lines = (*outputs.game_output_lines, *outputs.mod_output_lines)
    for line in reversed(combined_lines):
        snapshot = parse_item_snapshot(line)
        script = snapshot.get("leaderboard_script")
        if script:
            return normalize_target_script_name(script)
        match = LEADERBOARD_SCRIPT_RE.search(line)
        if match is not None:
            return normalize_target_script_name(match.group(1))
    return None


def format_seconds(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    whole_seconds = int(seconds + 0.5)
    minutes, second = divmod(whole_seconds, 60)
    hours, minute = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minute:02d}:{second:02d}"
    return f"{minute}:{second:02d}"


def build_progress_estimate_lines(outputs: CapturedOutputs, target_script: str | None) -> tuple[str, ...]:
    """首轮按库存净增长估算剩余和总游戏秒数；批量收获前明确返回不可估算。"""
    if parse_leaderboard_run_times(outputs.mod_output_lines, include_summary=True):
        return ()
    script = infer_progress_script(outputs, target_script)
    if script == "lb_fastest_reset":
        return ("progress_estimate script=lb_fastest_reset prediction=true unavailable reason=unlock_objective",)
    if script is None or script not in RESOURCE_TARGETS_BY_SCRIPT:
        return ()
    snapshots = [
        snapshot for line in outputs.mod_output_lines
        if (snapshot := parse_item_snapshot(line))
        and normalize_target_script_name(snapshot.get("leaderboard_script")) == script
    ]
    if not snapshots:
        return ()
    latest = snapshots[-1]
    # 状态查看可能只读日志尾部；不能跨请求或跨轮次计算速率。
    snapshots = [s for s in snapshots if s.get("request_id") == latest.get("request_id")
                 and s.get("leaderboard_runs") == latest.get("leaderboard_runs")]
    if (to_float(latest.get("leaderboard_runs")) or 0) > 0:
        return ()
    first = snapshots[0]
    first_time = to_float(first.get("game_time") or first.get("sim_time"))
    latest_time = to_float(latest.get("game_time") or latest.get("sim_time"))
    first_real = to_float(first.get("real_elapsed"))
    latest_real = to_float(latest.get("real_elapsed"))
    lines: list[str] = []
    for item, target in RESOURCE_TARGETS_BY_SCRIPT[script]:
        value = to_float(latest.get(item))
        initial = to_float(first.get(item))
        prefix = f"progress_estimate script={script} item={item} target={target:.0f} prediction=true"
        if value is None or initial is None:
            lines.append(f"{prefix} unavailable reason=missing_item_value")
            continue
        percent = min(100.0, max(0.0, value / target * 100.0))
        prefix += f" current={value:.0f} progress_percent={percent:.3f}"
        if latest_time is not None:
            prefix += f" game_time={latest_time:.3f}"
        if value >= target:
            lines.append(f"{prefix} target_reached=true awaiting_settlement=true")
            continue
        if first_time is None or latest_time is None or latest_time <= first_time:
            lines.append(f"{prefix} unavailable reason=insufficient_game_time")
            continue
        if value <= initial:
            lines.append(f"{prefix} unavailable reason=no_positive_rate")
            continue
        rate = (value - initial) / (latest_time - first_time)
        remaining = (target - value) / rate
        total = latest_time + remaining
        fields = [prefix, "basis=inventory_linear",
                  f"rate_per_game_second={rate:.3f}",
                  f"eta_game_seconds={remaining:.3f} eta_game_time={format_seconds(remaining)}",
                  f"estimated_total_game_seconds={total:.3f} estimated_total_game_time={format_seconds(total)}"]
        if first_real is not None and latest_real is not None and latest_real > first_real:
            speed = (latest_time - first_time) / (latest_real - first_real)
            fields.extend([f"game_seconds_per_real_second={speed:.3f}",
                           f"eta_real_seconds={remaining / speed:.3f} eta_real_time={format_seconds(remaining / speed)}"])
        first_tick = to_float(first.get("game_tick"))
        latest_tick = to_float(latest.get("game_tick"))
        if first_tick is not None and latest_tick is not None and latest_tick >= first_tick:
            fields.append(f"tick_per_game_second={(latest_tick - first_tick) / (latest_time - first_time):.3f}")
        lines.append(" ".join(fields))
    return tuple(lines)


def build_leaderboard_average_lines(outputs: CapturedOutputs) -> tuple[str, ...]:
    # 模组日志为追加式完成轮真源；output.txt 可能复写或重复包含相同行，不能相加。
    run_times = parse_leaderboard_run_times(outputs.mod_output_lines)
    summaries = [match for line in outputs.mod_output_lines
                 if (match := LEADERBOARD_SUMMARY_RE.search(line)) and match.group(1) == "true"]
    if not run_times and not summaries:
        return ()
    run_count = len(run_times)
    average_time = sum(run_times) / run_count if run_count else 0.0
    if summaries:
        run_count = int(summaries[-1].group(2))
        average_time = parse_leaderboard_clock(summaries[-1].group(3)) or 0.0
    # 总均值不能复制成 N 条相同单轮数据，否则会伪造 stable=true。
    stable = leaderboard_runs_are_stable(run_times, LEADERBOARD_STABILITY_THRESHOLD)
    fields = [
        "leaderboard_average",
        f"runs={run_count}",
        f"average={format_leaderboard_seconds(average_time)}",
        f"stable={str(stable).lower()}",
    ]
    if len(run_times) >= 2:
        previous_time, latest_time = run_times[-2], run_times[-1]
        baseline = min(previous_time, latest_time)
        if baseline > 0:
            fields.append(f"last_two_delta_ratio={abs(latest_time - previous_time) / baseline:.3f}")
    return (" ".join(fields),)


def is_controlled_stop(result: dict[str, object]) -> bool:
    error = str(result.get("last_error") or "")
    return any(error.startswith(prefix) for prefix in CONTROLLED_STOP_PREFIXES)


def print_status_only(args: argparse.Namespace) -> int:
    state_path = resolve_oracle_state_path(args.game_root, bepinex_root=args.bepinex_root)
    state = read_state_file(state_path)
    game_output_path = resolve_output_path(args.save_root, required=False)
    mod_output_path = resolve_bepinex_log_path(args.game_root, required=False, bepinex_root=args.bepinex_root)
    unity_log_path = resolve_unity_log_path(args.save_root, required=False)
    max_lines = max(0, int(args.status_lines))
    should_read_game_output = bool(args.include_game_output) or not (
        isinstance(state, dict) and state.get("status") in {"requested", "running", "stop_requested"}
    )
    # 有回执时从请求起点统计；旧请求只有有界日志尾部，不能据此宣称完整均值。
    receipt = None
    if state and state['request_id']:
        with state_transaction(state_path):
            receipt = read_record(resolve_request_record_path(state_path, cast(int, state['request_id'])))
    if receipt and receipt.get('result') is not None:
        mod_lines = tuple(receipt['result']['outputs']['mod_output_lines'])
    elif receipt and 'baseline' in receipt:
        baseline = deserialize_baseline(receipt['baseline'])
        mod_lines = read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature)
    else:
        mod_lines = read_log_tail(mod_output_path, max(1000, max_lines))
    outputs = CapturedOutputs(
        game_output_lines=read_tail_lines(game_output_path, max_lines) if should_read_game_output else (),
        mod_output_lines=mod_lines[-max_lines:] if max_lines else (),
        unity_log_lines=read_tail_lines(unity_log_path, max_lines),
    )

    print(f"real_game_runner status state={state_path}")
    print(f"real_game_runner status game_output={game_output_path}")
    print(f"real_game_runner status mod_output={mod_output_path}")
    print(f"real_game_runner status unity_log={unity_log_path}")
    if state is None:
        print("state missing")
    else:
        print(
            "state "
            f"request_id={state.get('request_id')} "
            f"status={state.get('status')} "
            f"target_script={state.get('target_script')} "
            f"timeout={state.get('timeout_seconds')} "
            f"last_error={state.get('last_error')}"
        )
    request_pattern = re.compile(rf"\brequest_id={state['request_id']}\b") if state else None
    progress_outputs = CapturedOutputs((), tuple(
        line for line in mod_lines if request_pattern and request_pattern.search(line)
    ))
    if receipt:
        for line in build_leaderboard_average_lines(progress_outputs):
            print(line)
        for line in build_progress_estimate_lines(progress_outputs, args.target_script):
            print(line)
    else:
        print('statistics unavailable reason=request_receipt_missing')
    for line in build_suspicious_python_process_lines():
        print(line)
    _print_captured_outputs(outputs, game_output_skipped=not should_read_game_output)
    return 0


@dataclass(frozen=True)
class ProcessSnapshot:
    pid: int
    ppid: int
    cpu_seconds: float
    cwd: Path | None
    cmdline: str


def read_process_snapshots(proc_root: Path = Path("/proc")) -> tuple[ProcessSnapshot, ...]:
    if not proc_root.exists():
        return ()
    snapshots: list[ProcessSnapshot] = []
    for process_dir in proc_root.iterdir():
        if not process_dir.name.isdigit():
            continue
        snapshot = read_process_snapshot(process_dir)
        if snapshot is not None:
            snapshots.append(snapshot)
    return tuple(snapshots)


def read_process_snapshot(process_dir: Path) -> ProcessSnapshot | None:
    try:
        status_text = (process_dir / "status").read_text(encoding="utf-8", errors="ignore")
        stat_fields = (process_dir / "stat").read_text(encoding="utf-8", errors="ignore").split()
        raw_cmdline = (process_dir / "cmdline").read_bytes()
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        return None

    ppid = parse_status_int(status_text, "PPid")
    if ppid is None or len(stat_fields) <= 15:
        return None
    try:
        pid = int(process_dir.name)
        user_seconds = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        cpu_seconds = (int(stat_fields[13]) + int(stat_fields[14])) / user_seconds
    except (KeyError, ValueError, OSError):
        return None

    try:
        cwd = (process_dir / "cwd").resolve()
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        cwd = None
    cmdline = raw_cmdline.replace(b"\0", b" ").decode("utf-8", errors="replace").strip()
    return ProcessSnapshot(pid=pid, ppid=ppid, cpu_seconds=cpu_seconds, cwd=cwd, cmdline=cmdline)


def parse_status_int(status_text: str, key: str) -> int | None:
    prefix = f"{key}:"
    for line in status_text.splitlines():
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :].strip().split(maxsplit=1)[0]
        try:
            return int(value)
        except ValueError:
            return None
    return None


def is_path_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def is_suspicious_python_process(snapshot: ProcessSnapshot, roots: tuple[Path, ...]) -> bool:
    if snapshot.cwd is None:
        return False
    if not snapshot.cmdline.startswith("python3 -"):
        return False
    if snapshot.ppid != 1 and snapshot.cpu_seconds < SUSPICIOUS_PYTHON_CPU_SECONDS:
        return False
    return any(is_path_relative_to(snapshot.cwd, root) for root in roots)


def build_suspicious_python_process_lines(
    snapshots: tuple[ProcessSnapshot, ...] | None = None,
    roots: tuple[Path, ...] = (REPO_ROOT, LEGACY_REPO_ROOT),
) -> tuple[str, ...]:
    if snapshots is None:
        snapshots = read_process_snapshots()
    suspicious = [
        snapshot
        for snapshot in snapshots
        if is_suspicious_python_process(snapshot, tuple(root.resolve() for root in roots))
    ]
    if not suspicious:
        return ("process_guard suspicious_python=0",)
    lines = [f"process_guard suspicious_python={len(suspicious)}"]
    for snapshot in suspicious:
        cwd = str(snapshot.cwd) if snapshot.cwd is not None else ""
        lines.append(
            "process_guard suspicious_python "
            f"pid={snapshot.pid} ppid={snapshot.ppid} "
            f"cpu_seconds={snapshot.cpu_seconds:.1f} cwd={cwd} cmd={snapshot.cmdline}"
        )
    return tuple(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.action or args.json or args.idempotency_key:
        return task_main(args)
    state_path = resolve_oracle_state_path(args.game_root, bepinex_root=args.bepinex_root)

    if args.status_only:
        return print_status_only(args)

    exe_path = resolve_game_executable(args.game_root)

    bepinex_root = resolve_bepinex_root(args.game_root, bepinex_root=args.bepinex_root)
    pid, launched_by_helper = ensure_game_running(exe_path, bepinex_root=bepinex_root)
    print(f"real_game_runner start pid={pid} exe={exe_path} launched={launched_by_helper}")
    print(f"real_game_runner state={state_path}")

    if args.request_only:
        request_id = request_script_run(
            state_path=state_path,
            target_script=args.target_script,
            timeout_seconds=args.request_timeout,
            replace_current=args.replace,
        )
        print(
            f"real_game_runner requested request_id={request_id} "
            f"target_script={normalize_target_script_name(args.target_script)} "
            f"timeout={args.request_timeout:g} mode=request_only"
        )
        return 0

    if not args.replace:
        wait_for_ready_state(
            state_path=state_path,
            pid=pid,
            timeout_seconds=args.startup_timeout,
            poll_interval=args.poll_interval,
        )
    baseline = capture_output_baseline(
        save_root=args.save_root, game_root=args.game_root, bepinex_root=args.bepinex_root
    )
    request_id = request_script_run(
        state_path=state_path,
        target_script=args.target_script,
        timeout_seconds=args.request_timeout,
        replace_current=args.replace,
    )
    try:
        result = wait_for_status(
            state_path=state_path,
            pid=pid,
            request_id=request_id,
            accepted_statuses={"done", "failed", "superseded"},
            timeout_seconds=args.total_timeout,
            poll_interval=args.poll_interval,
            baseline=baseline,
            output_stall_timeout=args.output_stall_timeout,
            max_leaderboard_runs=args.max_leaderboard_runs,
        )
    except (TimeoutError, KeyboardInterrupt):
        request_script_stop(state_path, request_id, "client wait cancelled or timed out")
        result = wait_for_status(
            state_path=state_path, pid=pid, request_id=request_id,
            accepted_statuses={"done", "failed", "superseded"}, timeout_seconds=10,
            poll_interval=args.poll_interval, baseline=baseline,
            output_stall_timeout=0, max_leaderboard_runs=0,
        )
    if result.get("status") == "superseded":
        # 新请求可能正在写 output.txt；旧客户端不再读取输出或确认其他请求的状态。
        print(f"real_game_runner result request_id={request_id} status=superseded error={result.get('last_error')}")
        return 4
    with state_transaction(state_path):
        current = read_state_file(state_path)
        if current is None or current["request_id"] != request_id or current["status"] not in {"done", "failed"}:
            print(f"real_game_runner result request_id={request_id} status=superseded reason=state_changed_before_capture")
            return 4
        # 持锁读取最终输出，阻止新客户端在读取期间启动另一个请求并清空 output.txt。
        outputs = capture_request_outputs(baseline, execution_started=bool(current.get("started_at")))
        write_state_file(state_path, build_idle_state(request_id=request_id))
    print(
        f"real_game_runner result request_id={request_id} status={result.get('status')} "
        f"error={result.get('last_error')}"
    )
    _print_captured_outputs(outputs)
    for line in build_leaderboard_average_lines(outputs):
        print(line)
    for line in build_progress_estimate_lines(outputs, args.target_script):
        print(line)
    if result.get("status") == "done":
        if target_requires_leaderboard_summary(args.target_script) and not has_successful_leaderboard_summary(outputs):
            print("real_game_runner leaderboard_summary_missing")
            return 5
        return 0
    if result.get("status") == "failed" and is_controlled_stop(result):
        return 0
    return 5


def read_record(path: Path) -> dict[str, Any] | None:
    """读取客户端回执，缺失与损坏分开处理；调用者持有所属状态文件锁。"""
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    if not isinstance(value, dict):
        raise TaskError('invalid_record', f'请求记录不是JSON对象: {path}')
    return value


def require_available(current: dict | None, replace_current: bool) -> None:
    """终态必须先取结果；只允许明确替换requested/running/stop_requested。"""
    if current is None:
        raise TaskError('not_connected', '模组状态文件尚未生成，请启动对应profile的游戏')
    status = current['status']
    if status == 'idle' or (replace_current and status in ('requested', 'running', 'stop_requested')):
        return
    raise TaskError('busy', '当前请求尚未回收；先按ID等待并取结果，替换活动请求须显式指定--replace',
                    request_id=current['request_id'], status=status)


def allocate_request_id(state_path: Path, current: dict | None) -> int:
    """锁内持久预留ID；状态写入失败也不复用已有回执的编号。编号0保存计数器。"""
    next_id = next_request_id(current)
    counter_path = resolve_request_record_path(state_path, 0)
    counter = read_record(counter_path)
    if counter:
        next_id = max(next_id, int(counter['last_id']) + 1)
    if next_id > 2147483647:
        raise TaskError('request_id_exhausted', '请求ID已达到Int32上限')
    write_state_file(counter_path, {'last_id': next_id})
    return next_id


def submit_task(args: argparse.Namespace, state_path: Path) -> int:
    """幂等回执先于投递落盘；重试只读取原ID，模糊投递不会自动再次启动。"""
    target = normalize_target_script_name(args.target_script)
    if not target:
        raise TaskError('invalid_target', 'target-script不能为空')
    baseline = capture_output_baseline(save_root=args.save_root, game_root=args.game_root, bepinex_root=args.bepinex_root)
    paths = serialize_baseline(baseline)
    fingerprint = {'target_script': target, 'timeout_seconds': args.request_timeout,
                   'paths': {key: value for key, value in paths.items() if key.endswith('_path')}}
    key_path = resolve_request_key_path(state_path, args.idempotency_key) if args.idempotency_key else None
    # 两次锁内复核夹住进程预检；不在持锁期间启动进程或等待游戏。
    for phase in (0, 1):
        with state_transaction(state_path):
            if key_path is not None:
                previous = read_record(key_path)
                if previous is not None:
                    if previous.get('fingerprint') != fingerprint:
                        raise TaskError('idempotency_conflict', '幂等键已用于不同参数，请复用原参数或换一个键')
                    return int(previous['request_id'])
            current = read_state_file(state_path)
            require_available(current, args.replace)
            if phase == 1:
                request_id = allocate_request_id(state_path, current)
                baseline = capture_output_baseline(save_root=args.save_root, game_root=args.game_root, bepinex_root=args.bepinex_root)
                receipt: dict[str, Any] = {'schema_version': 1, 'request_id': request_id, 'fingerprint': fingerprint,
                           'baseline': serialize_baseline(baseline), 'submitted_at': time.time(),
                           'result': None}
                write_state_file(resolve_request_record_path(state_path, request_id), receipt)
                if key_path is not None:
                    write_state_file(key_path, {'request_id': request_id, 'fingerprint': fingerprint})
                write_state_file(state_path, build_requested_state(
                    request_id=request_id, target_script=target, timeout_seconds=args.request_timeout))
                return request_id
        exe = resolve_game_executable(args.game_root)
        ensure_game_running(exe, bepinex_root=resolve_bepinex_root(args.game_root, bepinex_root=args.bepinex_root))
    raise AssertionError('请求未进入投递阶段')


def build_task_report(state: dict, outputs: CapturedOutputs, *, output_complete: bool) -> dict[str, Any]:
    """执行状态、完成轮和完整统计分别报告，不把取消摘要当成真实完成轮。"""
    pattern = re.compile(rf"\brequest_id={state['request_id']}\b")
    scoped = CapturedOutputs((), tuple(line for line in outputs.mod_output_lines if pattern.search(line)))
    run_times = parse_leaderboard_run_times(scoped.mod_output_lines)
    full_statistics = has_successful_leaderboard_summary(scoped)
    reason = str(state.get('last_error') or '')
    reasons = (('reached stable leaderboard runs', 'sample_limit'),
               ('client cancelled', 'cancelled'), ('client wait', 'client_timeout'),
               ('request timed out', 'request_timeout'), ('mod log stalled', 'log_stall'),
               ('script runtime error', 'script_error'))
    reason_code = next((code for prefix, code in reasons if reason.startswith(prefix)), None)
    if state['status'] == 'done':
        outcome = 'completed'
        if target_requires_leaderboard_summary(state.get('target_script')) and not full_statistics:
            outcome = 'missing_leaderboard_summary'
    elif state['status'] == 'failed':
        outcome = 'stopped' if is_controlled_stop(state) or reason.startswith('client ') else 'failed'
    else:
        outcome = str(state['status'])
    progress = []
    for line in build_progress_estimate_lines(scoped, state.get('target_script')):
        fields = {}
        for key, value in re.findall(r'(\w+)=([^\s]+)', line):
            number = to_float(value)
            fields[key] = number if number is not None else value
        progress.append(fields)
    return {'schema_version': 1, 'kind': 'real_game', **state, 'outcome': outcome, 'reason_code': reason_code,
            'full_statistics': full_statistics, 'completed_runs': len(run_times),
            'run_game_seconds': list(run_times),
            'average_game_seconds': sum(run_times) / len(run_times) if run_times else None,
            'progress': {'prediction': True, 'estimates': progress},
            'output_complete': output_complete, 'outputs': asdict(outputs)}


def task_result(state_path: Path, request_id: int, *, collect: bool = False, max_lines: int = 80) -> dict[str, Any]:
    """同一事务内取结果、留存、确认；只在当前ID终态时读取output.txt。"""
    with state_transaction(state_path):
        current = read_state_file(state_path)
        record_path = resolve_request_record_path(state_path, request_id)
        receipt = read_record(record_path) if request_id else None
        if receipt and receipt.get('result') is not None:
            result = receipt['result']
            # 允许恢复“结果已落盘、idle写入失败”的中断。
            if collect and current and current['request_id'] == request_id and current['status'] in ('done', 'failed'):
                write_state_file(state_path, build_idle_state(request_id=request_id))
            return present_task_report(result, record_path, max_lines)
        if current is None:
            raise TaskError('not_connected', '找不到模组状态文件', request_id=request_id)
        if current['request_id'] != request_id:
            if receipt is None:
                raise TaskError('result_unavailable', '没有该请求的客户端回执或留存结果', request_id=request_id)
            status = 'superseded' if cast(int, current['request_id']) > request_id else 'submission_unknown'
            result = build_task_report({'request_id': request_id, 'status': status,
                'target_script': receipt['fingerprint']['target_script'],
                'last_error': '状态已不属于该请求，未读取其他请求的输出'}, CapturedOutputs((), ()), output_complete=False)
            if collect and status == 'superseded':
                receipt['result'] = result
                write_state_file(record_path, receipt)
            return present_task_report(result, record_path, max_lines)
        terminal = current['status'] in ('done', 'failed')
        if collect and not terminal:
            raise TaskError('not_terminal', '请求尚未结束，请使用wait或cancel', request_id=request_id, status=current['status'])
        if receipt:
            baseline = deserialize_baseline(receipt['baseline'])
            if terminal and collect:
                outputs = capture_request_outputs(baseline, execution_started=bool(current.get('started_at')))
            else:
                outputs = CapturedOutputs((), read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature),
                                          read_log_tail(baseline.unity_log_path, max_lines))
        else:
            # 旧客户端没有保存偏移，显式取结果可回收状态，但不能伪造完整日志。
            outputs = CapturedOutputs((), ())
        report = build_task_report(current, outputs, output_complete=bool(receipt and terminal and collect))
        if terminal and collect:
            receipt = receipt or {'schema_version': 1, 'request_id': request_id}
            receipt['result'] = report
            write_state_file(record_path, receipt)
            write_state_file(state_path, build_idle_state(request_id=request_id))
        return present_task_report(report, record_path, max_lines)


def present_task_report(report: dict, record_path: Path, max_lines: int) -> dict[str, Any]:
    """终端只显示有限日志，完整结果留在回执文件中；截断不改变统计样本。"""
    result = dict(report)
    outputs = report.get('outputs', {})
    result['output_lines'] = {key: len(lines) for key, lines in outputs.items()}
    result['outputs'] = {key: list(lines[-max_lines:]) if max_lines else [] for key, lines in outputs.items()}
    result['outputs_truncated'] = any(len(lines) > max_lines for lines in outputs.values())
    result['result_path'] = str(record_path) if record_path.exists() else None
    return result


def wait_task(args: argparse.Namespace, state_path: Path, request_id: int, *, cancel_on_timeout: bool) -> dict[str, Any]:
    """run超时停止自己的任务；独立wait超时只结束等待，可随后按同一ID继续。"""
    report = task_result(state_path, request_id, max_lines=args.status_lines)
    if report['status'] in ('done', 'failed', 'superseded'):
        return task_result(state_path, request_id, collect=True, max_lines=args.status_lines)
    if report['status'] not in ('requested', 'running', 'stop_requested'):
        raise TaskError('not_active', '该请求没有可等待的活动状态', request_id=request_id, status=report['status'])
    with state_transaction(state_path):
        receipt = read_record(resolve_request_record_path(state_path, request_id))
    if receipt is None:
        raise TaskError('receipt_missing', '该请求来自旧客户端，缺少监控起点；可使用status/cancel/result', request_id=request_id)
    baseline = deserialize_baseline(receipt['baseline'])
    pid = find_game_process_id()
    if pid is None:
        if cancel_on_timeout:
            request_script_stop(state_path, request_id, 'client game process unavailable')
        raise TaskError('game_not_running', '游戏进程未运行；请检查对应profile', request_id=request_id)
    try:
        wait_for_status(state_path=state_path, pid=pid, request_id=request_id,
                        accepted_statuses={'done', 'failed', 'superseded'}, timeout_seconds=args.total_timeout,
                        poll_interval=args.poll_interval, baseline=baseline,
                        output_stall_timeout=args.output_stall_timeout, max_leaderboard_runs=args.max_leaderboard_runs)
    except (TimeoutError, KeyboardInterrupt) as exc:
        if not cancel_on_timeout:
            raise TaskError('wait_interrupted', '等待已结束，任务仍由模组管理；使用同一ID继续等待或取消', request_id=request_id) from exc
        request_script_stop(state_path, request_id, 'client wait cancelled or timed out')
        wait_for_status(state_path=state_path, pid=pid, request_id=request_id,
                        accepted_statuses={'done', 'failed', 'superseded'}, timeout_seconds=10,
                        poll_interval=args.poll_interval, baseline=baseline, output_stall_timeout=0, max_leaderboard_runs=0)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        if cancel_on_timeout:
            request_script_stop(state_path, request_id, 'client monitor failed')
        raise TaskError('monitor_failed', str(exc), request_id=request_id) from exc
    return task_result(state_path, request_id, collect=True, max_lines=args.status_lines)


def task_health(args: argparse.Namespace, state_path: Path) -> dict[str, Any]:
    """只查询连接线索；状态文件存在不代表工作区已就绪，也不代替实时心跳。"""
    with state_transaction(state_path):
        state = read_state_file(state_path)
    baseline = capture_output_baseline(save_root=args.save_root, game_root=args.game_root, bepinex_root=args.bepinex_root)
    lines = read_log_tail(baseline.mod_output_path, 500)
    versions = [match.group(1) for line in lines
                if (match := re.search(r'Loading \[TFWR Oracle Runner ([^\]]+)\]', line))]
    return {'schema_version': 1, 'kind': 'connection', 'state': state,
            'process_id': find_game_process_id(), 'state_path': str(state_path),
            'paths': {key: value for key, value in serialize_baseline(baseline).items() if key.endswith('_path')},
            'mod_version_from_log': versions[-1] if versions else None,
            'workspace_ready': None, 'note': '工作区就绪由模组接收请求后判断；版本来自有限日志尾部，缺失时为null'}


def task_main(args: argparse.Namespace) -> int:
    """stdout为一个JSON回执，监控文本走stderr；退出码与outcome一起解释。"""
    action = args.action or ('status' if args.status_only else 'submit' if args.request_only else 'run')
    request_id = args.request_id
    try:
        with redirect_stdout(sys.stderr):
            state_path = resolve_oracle_state_path(args.game_root, bepinex_root=args.bepinex_root)
            if action == 'health':
                result = task_health(args, state_path)
            elif action in ('run', 'submit'):
                request_id = submit_task(args, state_path)
                result = (wait_task(args, state_path, request_id, cancel_on_timeout=True) if action == 'run'
                          else task_result(state_path, request_id, max_lines=args.status_lines))
            else:
                request_id = args.request_id
                if request_id is None:
                    if action != 'status':
                        raise TaskError('request_id_required', f'{action}需要--request-id')
                    with state_transaction(state_path):
                        state = read_state_file(state_path)
                    if state is None:
                        raise TaskError('not_connected', '模组状态文件尚未生成')
                    request_id = cast(int, state['request_id'])
                if action == 'wait':
                    result = wait_task(args, state_path, request_id, cancel_on_timeout=False)
                elif action == 'cancel':
                    changed = request_script_stop(state_path, request_id, 'client cancelled request')
                    result = task_result(state_path, request_id, max_lines=args.status_lines)
                    result['cancel_requested'] = changed
                else:
                    result = task_result(state_path, request_id, collect=action == 'result', max_lines=args.status_lines)
    except TaskError as exc:
        result = {'schema_version': 1, 'kind': 'request_error', 'error': {'code': exc.code, 'message': str(exc), **exc.details}}
        print(json.dumps(result, ensure_ascii=False))
        return 3 if exc.code == 'busy' else 5
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {'schema_version': 1, 'kind': 'request_error',
                  'error': {'code': type(exc).__name__, 'message': str(exc), 'request_id': request_id}}
        print(json.dumps(result, ensure_ascii=False))
        return 5
    print(json.dumps(result, ensure_ascii=False))
    return 5 if result.get('outcome') in ('failed', 'missing_leaderboard_summary', 'submission_unknown', 'superseded') else 0
