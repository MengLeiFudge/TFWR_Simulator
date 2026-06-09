from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from .config import load_local_env, resolve_bepinex_log_path, resolve_game_root, resolve_output_path, to_windows_path
from .output_capture import (
    CapturedOutputs,
    OutputBaseline,
    capture_output_baseline,
    capture_request_outputs,
    file_signature,
    read_appended_lines,
)


load_local_env()


ORACLE_STATE_FILE_NAME = "mlj.tfwr.oracle-runner.state.json"
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "启动或复用真实 TFWR 游戏，通过 state.json 请求 Unity 模组执行目标脚本，"
            "并在结束后读取游戏 output.txt 与 BepInEx/LogOutput.log。"
        )
    )
    parser.add_argument("--game-root", default=None, help="显式指定游戏安装目录。")
    parser.add_argument("--save-root", default=None, help="显式指定 Save0 目录。")
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
        help="等待游戏与模组进入 ready/idle 的最长时间，默认 30 秒。",
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
        help="只写入运行请求并立即退出；不等待完成、不轮询日志，适合长流程后台打榜。",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help=(
            "只读取 state.json 与 BepInEx 日志尾部；state=running 时默认跳过游戏 output.txt，"
            "避免和游戏 Logger 抢文件句柄。"
        ),
    )
    parser.add_argument(
        "--status-lines",
        type=int,
        default=80,
        help="--status-only 输出每个日志文件的尾部行数，默认 80。",
    )
    parser.add_argument(
        "--include-game-output",
        action="store_true",
        help="--status-only 即使 state=running 也读取游戏 output.txt；仅在确认游戏不在写日志时使用。",
    )
    return parser.parse_args(argv)


def normalize_target_script_name(target_script: str | None) -> str | None:
    if target_script is None:
        return None
    value = target_script.strip()
    if not value:
        return None
    if value.endswith(".py"):
        value = value[:-3]
    return value or None


def resolve_oracle_state_path(game_root: str | Path | None = None) -> Path:
    root = resolve_game_root(game_root)
    return (root / "BepInEx" / "config" / ORACLE_STATE_FILE_NAME).resolve()


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
        "request_id": int(current_state.get("request_id", 0)),
        "status": "stop_requested",
        "target_script": normalize_target_script_name(str(current_state.get("target_script") or "")),
        "timeout_seconds": current_state.get("timeout_seconds"),
        "started_at": current_state.get("started_at"),
        "finished_at": None,
        "last_error": message,
    }


def read_tail_lines(path: Path | None, max_lines: int) -> tuple[str, ...]:
    if path is None or max_lines <= 0 or not path.exists():
        return ()
    return tuple(read_text_with_retries(path).splitlines()[-max_lines:])


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
    if current_state is None:
        return 1
    raw = current_state.get("request_id", 0)
    try:
        return int(raw) + 1
    except (TypeError, ValueError):
        return 1


def resolve_game_executable(game_root: str | Path | None = None) -> Path:
    root = resolve_game_root(game_root)
    candidates = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() == ".exe" and "CrashHandler" not in path.name
    )
    if not candidates:
        raise FileNotFoundError(f"游戏目录下未找到可执行文件: {root}")
    return candidates[0]


def read_state_file(state_path: Path) -> dict[str, object] | None:
    for attempt in range(STATE_IO_MAX_ATTEMPTS):
        try:
            if not state_path.exists():
                return None
            return json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, PermissionError):
            if attempt + 1 >= STATE_IO_MAX_ATTEMPTS:
                return None
            time.sleep(STATE_IO_RETRY_SECONDS)
    return None


def write_state_file(state_path: Path, state: dict[str, object]) -> None:
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
    completed = subprocess.run(["tasklist.exe", "/FI", f"IMAGENAME eq {process_name}"], check=False, capture_output=True)
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


def ensure_game_running(exe_path: Path) -> tuple[int, bool]:
    existing_pid = find_game_process_id(exe_path.name)
    if existing_pid is not None:
        return (existing_pid, False)
    return launch_windows_game(exe_path)


def acknowledge_terminal_state(state_path: Path) -> dict[str, object]:
    current = read_state_file(state_path)
    if current is None:
        raise FileNotFoundError(f"状态文件不存在: {state_path}")
    idle_state = build_idle_state(request_id=int(current.get("request_id", 0)))
    write_state_file(state_path, idle_state)
    return idle_state


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
    stop_requested_for_stall = False
    controlled_stop_message: str | None = None
    last_live_progress_at = 0.0
    last_live_progress_line = ""
    loop_now = time.monotonic()
    while loop_now < deadline:
        if not is_windows_process_running(pid):
            raise RuntimeError(f"游戏进程已退出: pid={pid}")
        current = read_state_file(state_path)
        if current is not None:
            current_request_id = int(current.get("request_id", 0))
            status = str(current.get("status", ""))
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
            if (
                (output_stall_timeout > 0 or max_leaderboard_runs > 0)
                and current_request_id == request_id
                and status == "running"
            ):
                mod_output_lines = read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature)
                mod_output_count = len(mod_output_lines)
                if mod_output_count > last_mod_output_count:
                    last_mod_output_count = mod_output_count
                    last_output_activity_at = loop_now

                if loop_now - last_live_progress_at >= 5.0:
                    live_outputs = CapturedOutputs(
                        game_output_lines=(),
                        mod_output_lines=tuple(mod_output_lines),
                    )
                    live_lines = build_leaderboard_average_lines(live_outputs)
                    if not live_lines:
                        live_lines = build_progress_estimate_lines(live_outputs, None)
                    if live_lines and live_lines[-1] != last_live_progress_line:
                        last_live_progress_line = live_lines[-1]
                        last_live_progress_at = loop_now
                        print(f"real_game_runner live {last_live_progress_line}", flush=True)

                run_times = parse_leaderboard_run_times(tuple(mod_output_lines))
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
                    write_state_file(state_path, build_stop_requested_state(current, message))
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
                    write_state_file(state_path, build_stop_requested_state(current, message))
                    stop_requested_for_stall = True
                    print(f"real_game_runner output_stall request_id={request_id} {message}")
        sleep_interval = 0.05 if max_leaderboard_runs > 0 else max(0.05, poll_interval)
        time.sleep(sleep_interval)
        loop_now = time.monotonic()
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
                acknowledge_terminal_state(state_path)
            elif status == "idle":
                return current
        time.sleep(max(0.05, poll_interval))
    raise TimeoutError(f"等待模组进入 idle 超时: state_path={state_path}")


def request_script_run(
    *,
    state_path: Path,
    target_script: str,
    timeout_seconds: float,
) -> int:
    request_id = next_request_id(read_state_file(state_path))
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
    completed = subprocess.run(command, check=False, capture_output=True)
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
    if parse_leaderboard_run_times((*outputs.game_output_lines, *outputs.mod_output_lines), include_summary=True):
        return ()
    script = infer_progress_script(outputs, target_script)
    if script is None or script not in RESOURCE_TARGETS_BY_SCRIPT:
        return ()
    snapshots = [
        snapshot
        for line in outputs.mod_output_lines
        if (snapshot := parse_item_snapshot(line))
        and normalize_target_script_name(snapshot.get("leaderboard_script")) == script
    ]
    if len(snapshots) < 2:
        return ()

    lines: list[str] = []
    first = snapshots[0]
    latest = snapshots[-1]
    first_time = to_float(first.get("game_time") or first.get("sim_time"))
    latest_time = to_float(latest.get("game_time") or latest.get("sim_time"))
    if first_time is None or latest_time is None or latest_time <= first_time:
        for item, target in RESOURCE_TARGETS_BY_SCRIPT[script]:
            latest_value = to_float(latest.get(item))
            lines.append(
                "progress_estimate "
                f"script={script} item={item} current={latest_value or 0:.0f} target={target:.0f} "
                "unavailable reason=invalid_game_time"
            )
        return tuple(lines)
    first_real_elapsed = to_float(first.get("real_elapsed"))
    latest_real_elapsed = to_float(latest.get("real_elapsed"))
    real_elapsed_delta = None
    if (
        first_real_elapsed is not None
        and latest_real_elapsed is not None
        and latest_real_elapsed > first_real_elapsed
    ):
        real_elapsed_delta = latest_real_elapsed - first_real_elapsed
    first_tick = to_float(first.get("game_tick"))
    latest_tick = to_float(latest.get("game_tick"))
    tick_delta = None
    if first_tick is not None and latest_tick is not None and latest_tick > first_tick:
        tick_delta = latest_tick - first_tick

    for item, target in RESOURCE_TARGETS_BY_SCRIPT[script]:
        first_value = to_float(first.get(item))
        latest_value = to_float(latest.get(item))
        if first_value is None or latest_value is None:
            lines.append(
                "progress_estimate "
                f"script={script} item={item} current={latest_value or 0:.0f} target={target:.0f} "
                "unavailable reason=missing_item_value"
            )
            continue
        if latest_value >= target:
            latest_time_text = ""
            if latest_time is not None:
                latest_time_text = f" game_time={latest_time:.3f}"
            lines.append(
                "progress_estimate "
                f"script={script} item={item} current={latest_value:.0f} target={target:.0f}"
                f"{latest_time_text} target_reached=true"
            )
            continue
        if latest_value <= first_value:
            lines.append(
                "progress_estimate "
                f"script={script} item={item} current={latest_value:.0f} target={target:.0f} "
                "unavailable reason=no_positive_rate"
            )
            continue
        rate = (latest_value - first_value) / (latest_time - first_time)
        if rate <= 0:
            lines.append(
                "progress_estimate "
                f"script={script} item={item} current={latest_value:.0f} target={target:.0f} "
                "unavailable reason=no_positive_rate"
            )
            continue
        remaining = max(0.0, target - latest_value)
        eta_seconds = remaining / rate
        fields = [
            "progress_estimate "
            f"script={script} item={item} current={latest_value:.0f} target={target:.0f}",
            f"game_time={latest_time:.3f} rate_per_game_second={rate:.3f} "
            f"eta_game_seconds={eta_seconds:.3f} eta_game_time={format_seconds(eta_seconds)}",
        ]
        if real_elapsed_delta is not None:
            game_seconds_per_real_second = (latest_time - first_time) / real_elapsed_delta
            fields.append(f"game_seconds_per_real_second={game_seconds_per_real_second:.3f}")
            if game_seconds_per_real_second > 0:
                eta_real_seconds = eta_seconds / game_seconds_per_real_second
                fields.append(
                    f"eta_real_seconds={eta_real_seconds:.3f} eta_real_time={format_seconds(eta_real_seconds)}"
                )
        if tick_delta is not None:
            tick_per_game_second = tick_delta / (latest_time - first_time)
            fields.append(f"tick_per_game_second={tick_per_game_second:.3f}")
            if real_elapsed_delta is not None:
                fields.append(f"tick_per_real_second={tick_delta / real_elapsed_delta:.3f}")
        lines.append(" ".join(fields))
    return tuple(lines)


def build_leaderboard_average_lines(outputs: CapturedOutputs) -> tuple[str, ...]:
    run_times = parse_leaderboard_run_times((*outputs.game_output_lines, *outputs.mod_output_lines), include_summary=True)
    if not run_times:
        return ()
    average_time = sum(run_times) / len(run_times)
    stable = leaderboard_runs_are_stable(run_times, LEADERBOARD_STABILITY_THRESHOLD)
    fields = [
        "leaderboard_average",
        f"runs={len(run_times)}",
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
    state_path = resolve_oracle_state_path(args.game_root)
    state = read_state_file(state_path)
    game_output_path = resolve_output_path(args.save_root, required=False)
    mod_output_path = resolve_bepinex_log_path(args.game_root, required=False)
    max_lines = max(0, int(args.status_lines))
    should_read_game_output = bool(args.include_game_output) or not (
        isinstance(state, dict) and state.get("status") == "running"
    )
    outputs = CapturedOutputs(
        game_output_lines=read_tail_lines(game_output_path, max_lines) if should_read_game_output else (),
        mod_output_lines=read_tail_lines(mod_output_path, max_lines),
    )

    print(f"real_game_runner status state={state_path}")
    print(f"real_game_runner status game_output={game_output_path}")
    print(f"real_game_runner status mod_output={mod_output_path}")
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
    for line in build_leaderboard_average_lines(outputs):
        print(line)
    for line in build_progress_estimate_lines(outputs, args.target_script):
        print(line)
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
    state_path = resolve_oracle_state_path(args.game_root)

    if args.status_only:
        return print_status_only(args)

    exe_path = resolve_game_executable(args.game_root)

    pid, launched_by_helper = ensure_game_running(exe_path)
    print(f"real_game_runner start pid={pid} exe={exe_path} launched={launched_by_helper}")
    print(f"real_game_runner state={state_path}")

    if args.request_only:
        request_id = request_script_run(
            state_path=state_path,
            target_script=args.target_script,
            timeout_seconds=args.request_timeout,
        )
        print(
            f"real_game_runner requested request_id={request_id} "
            f"target_script={normalize_target_script_name(args.target_script)} "
            f"timeout={args.request_timeout:g} mode=request_only"
        )
        return 0

    wait_for_ready_state(
        state_path=state_path,
        pid=pid,
        timeout_seconds=args.startup_timeout,
        poll_interval=args.poll_interval,
    )
    baseline = capture_output_baseline(save_root=args.save_root, game_root=args.game_root)
    request_id = request_script_run(
        state_path=state_path,
        target_script=args.target_script,
        timeout_seconds=args.request_timeout,
    )
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
    outputs = capture_request_outputs(baseline)
    print(
        f"real_game_runner result request_id={request_id} status={result.get('status')} "
        f"error={result.get('last_error')}"
    )
    _print_captured_outputs(outputs)
    for line in build_leaderboard_average_lines(outputs):
        print(line)
    for line in build_progress_estimate_lines(outputs, args.target_script):
        print(line)
    acknowledge_terminal_state(state_path)
    if result.get("status") == "done":
        if target_requires_leaderboard_summary(args.target_script) and not has_successful_leaderboard_summary(outputs):
            print("real_game_runner leaderboard_summary_missing")
            return 5
        return 0
    if result.get("status") == "failed" and is_controlled_stop(result):
        return 0
    if result.get("status") == "superseded":
        return 4
    return 5
