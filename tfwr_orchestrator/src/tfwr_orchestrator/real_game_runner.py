from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from .config import load_local_env, resolve_game_root, to_windows_path
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
LEADERBOARD_RUN_RE = re.compile(r"\[lb_[^\]]+(?:\.py)?\]\s+run=([1-9][0-9]*)\s+time=")
CONTROLLED_STOP_PREFIXES = ("reached max leaderboard runs",)
RESOURCE_TARGETS_BY_SCRIPT = {
    "lb_cactus": (("cactus", 33554432.0),),
    "lb_cactus_single": (("cactus", 131072.0),),
    "lb_maze": (("gold", 9863168.0),),
    "lb_maze_single": (("gold", 616448.0),),
}
ITEM_SNAPSHOT_RE = re.compile(r"\bitem_snapshot\b(?P<body>.*)$")
LEADERBOARD_SCRIPT_RE = re.compile(r"\[(lb_[^\]]+?)(?:\.py)?\]")


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
        help="请求运行后游戏 output.txt 与 BepInEx 日志都连续无新增输出的最长墙钟秒数，默认 30 秒；设为 0 可关闭。",
    )
    parser.add_argument(
        "--max-leaderboard-runs",
        type=int,
        default=2,
        help="打榜迭代验证时，看到 output.txt 新增 run 达到该数量后主动停止；默认 2，设为 0 表示不按轮次停止。",
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
    last_game_output_count = 0
    last_mod_output_count = 0
    stop_requested_for_stall = False
    controlled_stop_message: str | None = None
    while time.monotonic() < deadline:
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
                game_output_lines = read_appended_lines(baseline.game_output_path, baseline.game_output_signature)
                mod_output_lines = read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature)
                game_output_count = len(game_output_lines)
                mod_output_count = len(mod_output_lines)
                if game_output_count > last_game_output_count:
                    last_game_output_count = game_output_count
                    last_output_activity_at = time.monotonic()
                if mod_output_count > last_mod_output_count:
                    last_mod_output_count = mod_output_count
                    last_output_activity_at = time.monotonic()

                completed_runs = count_leaderboard_runs(game_output_lines)
                if max_leaderboard_runs > 0 and completed_runs >= max_leaderboard_runs:
                    message = f"reached max leaderboard runs {max_leaderboard_runs}"
                    write_state_file(state_path, build_stop_requested_state(current, message))
                    print(f"real_game_runner max_runs request_id={request_id} {message}")
                    controlled_stop_message = message
                    max_leaderboard_runs = 0
                elif (
                    output_stall_timeout > 0
                    and
                    not stop_requested_for_stall
                    and time.monotonic() - last_output_activity_at >= output_stall_timeout
                ):
                    message = (
                        f"game output and mod log stalled for {output_stall_timeout:g}s "
                        f"after game_lines={last_game_output_count} mod_lines={last_mod_output_count}"
                    )
                    write_state_file(state_path, build_stop_requested_state(current, message))
                    stop_requested_for_stall = True
                    print(f"real_game_runner output_stall request_id={request_id} {message}")
        sleep_interval = 0.05 if max_leaderboard_runs > 0 else max(0.05, poll_interval)
        time.sleep(sleep_interval)
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


def _print_captured_outputs(outputs: CapturedOutputs) -> None:
    print(f"game_output_lines={len(outputs.game_output_lines)}")
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
    count = 0
    for line in lines:
        if LEADERBOARD_RUN_RE.search(line):
            count += 1
    return count


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
    for line in (*outputs.game_output_lines, *outputs.mod_output_lines):
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
        return ()

    for item, target in RESOURCE_TARGETS_BY_SCRIPT[script]:
        first_value = to_float(first.get(item))
        latest_value = to_float(latest.get(item))
        if first_value is None or latest_value is None or latest_value <= first_value:
            continue
        rate = (latest_value - first_value) / (latest_time - first_time)
        if rate <= 0:
            continue
        remaining = max(0.0, target - latest_value)
        eta_seconds = remaining / rate
        lines.append(
            "progress_estimate "
            f"script={script} item={item} current={latest_value:.0f} target={target:.0f} "
            f"game_time={latest_time:.3f} rate_per_game_second={rate:.3f} "
            f"eta_game_seconds={eta_seconds:.3f} eta_game_time={format_seconds(eta_seconds)}"
        )
    return tuple(lines)


def is_controlled_stop(result: dict[str, object]) -> bool:
    error = str(result.get("last_error") or "")
    return any(error.startswith(prefix) for prefix in CONTROLLED_STOP_PREFIXES)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    exe_path = resolve_game_executable(args.game_root)
    state_path = resolve_oracle_state_path(args.game_root)

    pid, launched_by_helper = ensure_game_running(exe_path)
    print(f"real_game_runner start pid={pid} exe={exe_path} launched={launched_by_helper}")
    print(f"real_game_runner state={state_path}")

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
