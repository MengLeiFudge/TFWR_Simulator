from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tfwr_orchestrator import real_game_runner as runner_module
from tfwr_orchestrator.output_capture import (
    EMPTY_SIGNATURE,
    OutputBaseline,
    capture_output_baseline,
    capture_request_outputs,
    file_signature,
    read_appended_lines,
)


class OutputCaptureTests(unittest.TestCase):
    def test_file_signature_tracks_size_and_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            target = Path(temp_text) / "output.txt"
            self.assertEqual(file_signature(target), EMPTY_SIGNATURE)
            target.write_text("hello\n", encoding="utf-8")
            signature = file_signature(target)
            self.assertTrue(signature.exists)
            self.assertEqual(signature.size, len("hello\n"))
            self.assertGreater(signature.mtime_ns, 0)

    def test_capture_request_outputs_reads_appended_lines_from_both_paths(self) -> None:
        with tempfile.TemporaryDirectory() as root_text:
            root = Path(root_text)
            save_root = root / "Saves" / "Save0"
            save_root.mkdir(parents=True)
            game_output_path = root / "output.txt"
            game_output_path.write_text("old-game\n", encoding="utf-8")

            with tempfile.TemporaryDirectory() as game_root_text:
                game_root = Path(game_root_text)
                mod_log_path = game_root / "BepInEx" / "LogOutput.log"
                mod_log_path.parent.mkdir(parents=True)
                mod_log_path.write_text("old-mod\n", encoding="utf-8")

                baseline = capture_output_baseline(save_root=save_root, game_root=game_root)
                game_output_path.write_text("old-game\nnew-game-1\nnew-game-2\n", encoding="utf-8")
                mod_log_path.write_text("old-mod\nnew-mod-1\nnew-mod-2\n", encoding="utf-8")

                outputs = capture_request_outputs(baseline)

        self.assertEqual(outputs.game_output_lines, ("new-game-1", "new-game-2"))
        self.assertEqual(outputs.mod_output_lines, ("new-mod-1", "new-mod-2"))

    def test_read_appended_lines_retries_when_file_is_temporarily_locked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            target = Path(temp_text) / "output.txt"
            target.write_text("old\n", encoding="utf-8")
            signature = file_signature(target)
            target.write_text("old\nnew\n", encoding="utf-8")
            original_read_bytes = Path.read_bytes
            attempts = {"count": 0}

            def flaky_read_bytes(path: Path) -> bytes:
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise PermissionError("sharing violation")
                return original_read_bytes(path)

            with mock.patch.object(Path, "read_bytes", flaky_read_bytes), mock.patch(
                "tfwr_orchestrator.output_capture.time.sleep"
            ):
                lines = read_appended_lines(target, signature)

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(lines, ("new",))


class RealGameRunnerToolTests(unittest.TestCase):
    def test_parse_args_accepts_timeout_flags(self) -> None:
        args = runner_module.parse_args(
            [
                "--target-script",
                "lb_start.py",
                "--request-timeout",
                "12",
                "--startup-timeout",
                "30",
                "--total-timeout",
                "99",
                "--poll-interval",
                "0.2",
                "--output-stall-timeout",
                "13",
                "--max-leaderboard-runs",
                "2",
            ]
        )
        self.assertEqual(args.target_script, "lb_start.py")
        self.assertEqual(args.request_timeout, 12.0)
        self.assertEqual(args.startup_timeout, 30.0)
        self.assertEqual(args.total_timeout, 99.0)
        self.assertEqual(args.poll_interval, 0.2)
        self.assertEqual(args.output_stall_timeout, 13.0)
        self.assertEqual(args.max_leaderboard_runs, 2)

    def test_parse_args_defaults_to_two_leaderboard_runs(self) -> None:
        args = runner_module.parse_args([])
        self.assertEqual(args.max_leaderboard_runs, 2)
        self.assertFalse(args.request_only)
        self.assertFalse(args.status_only)
        self.assertEqual(args.status_lines, 80)

    def test_resolve_game_executable_prefers_non_crash_handler(self) -> None:
        with tempfile.TemporaryDirectory() as game_root_text:
            game_root = Path(game_root_text)
            (game_root / "UnityCrashHandler64.exe").write_text("", encoding="utf-8")
            target = game_root / "TheFarmerWasReplaced.exe"
            target.write_text("", encoding="utf-8")
            self.assertEqual(runner_module.resolve_game_executable(game_root), target.resolve())

    def test_extract_pid_from_tasklist_output_reads_ascii_process_line(self) -> None:
        sample = (
            "\u4fe1\u606f...\r\n"
            "TheFarmerWasReplaced.exe      1234 Console                    1     10,240 K\r\n"
        )
        self.assertEqual(runner_module.extract_pid_from_tasklist_output(sample, "TheFarmerWasReplaced.exe"), 1234)

    def test_resolve_oracle_state_path_uses_bepinex_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as game_root_text:
            game_root = Path(game_root_text)
            expected = game_root / "BepInEx" / "config" / "mlj.tfwr.oracle-runner.state.json"
            self.assertEqual(runner_module.resolve_oracle_state_path(game_root), expected.resolve())

    def test_build_requested_state_uses_requested_status_and_null_timestamps(self) -> None:
        state = runner_module.build_requested_state(
            request_id=7,
            target_script="lb_start.py",
            timeout_seconds=20.0,
        )
        self.assertEqual(state["request_id"], 7)
        self.assertEqual(state["status"], "requested")
        self.assertEqual(state["target_script"], "lb_start")
        self.assertEqual(state["timeout_seconds"], 20.0)
        self.assertIsNone(state["started_at"])
        self.assertIsNone(state["finished_at"])
        self.assertIsNone(state["last_error"])

    def test_build_idle_state_resets_status_but_keeps_last_request_id(self) -> None:
        state = runner_module.build_idle_state(request_id=9)
        self.assertEqual(state["request_id"], 9)
        self.assertEqual(state["status"], "idle")
        self.assertIsNone(state["target_script"])
        self.assertIsNone(state["started_at"])
        self.assertIsNone(state["finished_at"])
        self.assertIsNone(state["last_error"])

    def test_ensure_game_running_reuses_existing_process_without_relaunch(self) -> None:
        with mock.patch.object(runner_module, "find_game_process_id", return_value=321), mock.patch.object(
            runner_module, "launch_windows_game"
        ) as launch:
            pid, launched = runner_module.ensure_game_running(Path("/tmp/TheFarmerWasReplaced.exe"))
        self.assertEqual(pid, 321)
        self.assertFalse(launched)
        launch.assert_not_called()

    def test_acknowledge_terminal_state_rewrites_file_back_to_idle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            state_path = Path(temp_text) / "state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "request_id": 5,
                        "status": "done",
                        "target_script": "lb_start",
                        "timeout_seconds": 20.0,
                        "started_at": "2026-04-22T00:00:00Z",
                        "finished_at": "2026-04-22T00:00:01Z",
                        "last_error": None,
                    }
                ),
                encoding="utf-8",
            )
            runner_module.acknowledge_terminal_state(state_path)
            state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["request_id"], 5)
        self.assertEqual(state["status"], "idle")
        self.assertIsNone(state["target_script"])
        self.assertIsNone(state["started_at"])
        self.assertIsNone(state["finished_at"])
        self.assertIsNone(state["last_error"])

    def test_next_request_id_increments_existing_state_counter(self) -> None:
        self.assertEqual(runner_module.next_request_id(None), 1)
        self.assertEqual(runner_module.next_request_id({"request_id": 4}), 5)

    def test_wait_for_status_returns_matching_request_state(self) -> None:
        states = iter(
            [
                {"request_id": 2, "status": "idle"},
                {"request_id": 3, "status": "requested"},
                {"request_id": 3, "status": "running"},
                {"request_id": 3, "status": "done"},
            ]
        )
        with mock.patch.object(runner_module, "read_state_file", side_effect=lambda _: next(states)), mock.patch.object(
            runner_module, "is_windows_process_running", return_value=True
        ), mock.patch.object(runner_module.time, "sleep"):
            result = runner_module.wait_for_status(
                state_path=Path("/tmp/state.json"),
                pid=123,
                request_id=3,
                accepted_statuses={"done"},
                timeout_seconds=5.0,
                poll_interval=0.01,
                baseline=OutputBaseline(None, EMPTY_SIGNATURE, None, EMPTY_SIGNATURE),
                output_stall_timeout=0,
                max_leaderboard_runs=0,
            )
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["request_id"], 3)

    def test_wait_for_status_treats_higher_request_id_as_superseded(self) -> None:
        states = iter(
            [
                {"request_id": 3, "status": "running"},
                {"request_id": 4, "status": "requested", "target_script": "lb_start"},
            ]
        )
        with mock.patch.object(runner_module, "read_state_file", side_effect=lambda _: next(states)), mock.patch.object(
            runner_module, "is_windows_process_running", return_value=True
        ), mock.patch.object(runner_module.time, "sleep"):
            result = runner_module.wait_for_status(
                state_path=Path("/tmp/state.json"),
                pid=123,
                request_id=3,
                accepted_statuses={"done", "failed", "superseded"},
                timeout_seconds=5.0,
                poll_interval=0.01,
                baseline=OutputBaseline(None, EMPTY_SIGNATURE, None, EMPTY_SIGNATURE),
                output_stall_timeout=0,
                max_leaderboard_runs=0,
            )
        self.assertEqual(result["status"], "superseded")
        self.assertEqual(result["request_id"], 3)
        self.assertEqual(result["last_error"], "superseded by request_id=4")

    def test_leaderboard_summary_accepts_lines_without_py_suffix(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=(),
            mod_output_lines=("[lb_dinosaur] finished=true runs=7 average=15:26.925",),
        )

        self.assertTrue(runner_module.has_successful_leaderboard_summary(outputs))

    def test_leaderboard_summary_accepts_game_output_lines(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=("[lb_fastest_reset] finished=true runs=1 average=376:11.397",),
            mod_output_lines=(),
        )

        self.assertTrue(runner_module.has_successful_leaderboard_summary(outputs))

    def test_wait_for_status_requests_stop_when_game_output_and_mod_log_stall(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            output_path = Path(temp_text) / "output.txt"
            output_path.write_text("old\n", encoding="utf-8")
            baseline = OutputBaseline(output_path, file_signature(output_path), None, EMPTY_SIGNATURE)
            state_holder = {
                "request_id": 3,
                "status": "running",
                "target_script": "lb_start",
                "timeout_seconds": 90.0,
                "started_at": "2026-04-25T00:00:00Z",
                "finished_at": None,
                "last_error": None,
            }
            written_states: list[dict[str, object]] = []

            def read_state(_: Path) -> dict[str, object]:
                return state_holder

            def write_state(_: Path, state: dict[str, object]) -> None:
                written_states.append(state)
                state_holder.update(
                    {
                        "request_id": 3,
                        "status": "failed",
                        "target_script": "lb_start",
                        "timeout_seconds": 90.0,
                        "started_at": "2026-04-25T00:00:00Z",
                        "finished_at": "2026-04-25T00:00:31Z",
                        "last_error": "leaderboard cancelled",
                    }
                )

            with mock.patch.object(runner_module, "read_state_file", side_effect=read_state), mock.patch.object(
                runner_module, "write_state_file", side_effect=write_state
            ), mock.patch.object(
                runner_module, "is_windows_process_running", return_value=True
            ), mock.patch.object(
                runner_module.time, "monotonic", side_effect=[0.0, 0.0, 31.0, 31.0, 31.1]
            ), mock.patch.object(
                runner_module.time, "sleep"
            ):
                result = runner_module.wait_for_status(
                    state_path=Path("/tmp/state.json"),
                    pid=123,
                    request_id=3,
                    accepted_statuses={"done", "failed", "superseded"},
                    timeout_seconds=60.0,
                    poll_interval=0.01,
                    baseline=baseline,
                    output_stall_timeout=30.0,
                    max_leaderboard_runs=0,
                )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(written_states[0]["status"], "stop_requested")
        self.assertIn("mod log stalled for 30s", str(written_states[0]["last_error"]))

    def test_wait_for_status_keeps_running_when_mod_log_advances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            output_path = root / "output.txt"
            mod_log_path = root / "LogOutput.log"
            output_path.write_text("old\n", encoding="utf-8")
            mod_log_path.write_text("old\n", encoding="utf-8")
            baseline = OutputBaseline(
                output_path,
                file_signature(output_path),
                mod_log_path,
                file_signature(mod_log_path),
            )
            state_holder = {
                "request_id": 3,
                "status": "running",
                "target_script": "lb_start",
                "timeout_seconds": 90.0,
                "started_at": "2026-04-25T00:00:00Z",
                "finished_at": None,
                "last_error": None,
            }
            written_states: list[dict[str, object]] = []
            read_count = 0

            def read_state(_: Path) -> dict[str, object]:
                nonlocal read_count
                read_count += 1
                if read_count == 1:
                    mod_log_path.write_text("old\nitem_snapshot elapsed=31.0\n", encoding="utf-8")
                if read_count >= 3:
                    state_holder.update(
                        {
                            "status": "failed",
                            "finished_at": "2026-04-25T00:00:32Z",
                            "last_error": "leaderboard cancelled",
                        }
                    )
                return state_holder

            with mock.patch.object(runner_module, "read_state_file", side_effect=read_state), mock.patch.object(
                runner_module, "write_state_file", side_effect=lambda *_: written_states.append(_[1])
            ), mock.patch.object(
                runner_module, "is_windows_process_running", return_value=True
            ), mock.patch.object(
                runner_module.time, "monotonic", side_effect=[0.0, 0.0, 31.0, 31.0, 31.1, 31.2, 31.3, 31.4]
            ), mock.patch.object(
                runner_module.time, "sleep"
            ):
                result = runner_module.wait_for_status(
                    state_path=Path("/tmp/state.json"),
                    pid=123,
                    request_id=3,
                    accepted_statuses={"done", "failed", "superseded"},
                    timeout_seconds=60.0,
                    poll_interval=0.01,
                    baseline=baseline,
                    output_stall_timeout=30.0,
                    max_leaderboard_runs=0,
                )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(written_states, [])

    def test_wait_for_status_does_not_poll_game_output_while_request_is_running(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            output_path = root / "output.txt"
            mod_log_path = root / "LogOutput.log"
            output_path.write_text("old\n", encoding="utf-8")
            mod_log_path.write_text("old\n", encoding="utf-8")
            baseline = OutputBaseline(
                output_path,
                file_signature(output_path),
                mod_log_path,
                file_signature(mod_log_path),
            )
            state_holder = {
                "request_id": 3,
                "status": "running",
                "target_script": "lb_start",
                "timeout_seconds": 90.0,
                "started_at": "2026-05-30T00:00:00Z",
                "finished_at": None,
                "last_error": None,
            }
            read_count = 0

            def read_state(_: Path) -> dict[str, object]:
                nonlocal read_count
                read_count += 1
                if read_count == 1:
                    mod_log_path.write_text(
                        "old\n[lb_hay] run=1 time=2:00.000\n[lb_hay] run=2 time=2:05.000\n",
                        encoding="utf-8",
                    )
                return state_holder

            def fail_on_game_output_read(path: Path, start_signature: object) -> tuple[str, ...]:
                if path == output_path:
                    raise AssertionError("running poll must not read game output")
                return ("[lb_hay] run=1 time=2:00.000", "[lb_hay] run=2 time=2:05.000")

            written_states: list[dict[str, object]] = []

            def write_state(_: Path, state: dict[str, object]) -> None:
                written_states.append(state)
                state_holder.update(
                    {
                        "status": "failed",
                        "finished_at": "2026-05-30T00:00:31Z",
                        "last_error": state["last_error"],
                    }
                )

            with mock.patch.object(runner_module, "read_state_file", side_effect=read_state), mock.patch.object(
                runner_module, "write_state_file", side_effect=write_state
            ), mock.patch.object(
                runner_module, "is_windows_process_running", return_value=True
            ), mock.patch.object(
                runner_module, "read_appended_lines", side_effect=fail_on_game_output_read
            ), mock.patch.object(
                runner_module.time, "sleep"
            ):
                result = runner_module.wait_for_status(
                    state_path=Path("/tmp/state.json"),
                    pid=123,
                    request_id=3,
                    accepted_statuses={"done", "failed", "superseded"},
                    timeout_seconds=60.0,
                    poll_interval=0.01,
                    baseline=baseline,
                    output_stall_timeout=30.0,
                    max_leaderboard_runs=2,
                )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(written_states[0]["last_error"], "reached stable leaderboard runs 2 avg=2:02.500")

    def test_wait_for_status_requests_stop_after_stable_minimum_leaderboard_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            output_path = Path(temp_text) / "output.txt"
            mod_log_path = Path(temp_text) / "LogOutput.log"
            output_path.write_text("old\n", encoding="utf-8")
            mod_log_path.write_text("old\n", encoding="utf-8")
            baseline = OutputBaseline(
                output_path,
                file_signature(output_path),
                mod_log_path,
                file_signature(mod_log_path),
            )
            mod_log_path.write_text(
                "old\n[lb_dinosaur] run=1 time=15:35.976\n[lb_dinosaur] run=2 time=15:42.382\n",
                encoding="utf-8",
            )
            state_holder = {
                "request_id": 3,
                "status": "running",
                "target_script": "lb_start",
                "timeout_seconds": 90.0,
                "started_at": "2026-04-25T00:00:00Z",
                "finished_at": None,
                "last_error": None,
            }
            written_states: list[dict[str, object]] = []

            def read_state(_: Path) -> dict[str, object]:
                return state_holder

            def write_state(_: Path, state: dict[str, object]) -> None:
                written_states.append(state)
                state_holder.update(
                    {
                        "request_id": 3,
                        "status": "failed",
                        "target_script": "lb_start",
                        "timeout_seconds": 90.0,
                        "started_at": "2026-04-25T00:00:00Z",
                        "finished_at": "2026-04-25T00:00:31Z",
                        "last_error": state["last_error"],
                    }
                )

            with mock.patch.object(runner_module, "read_state_file", side_effect=read_state), mock.patch.object(
                runner_module, "write_state_file", side_effect=write_state
            ), mock.patch.object(
                runner_module, "is_windows_process_running", return_value=True
            ), mock.patch.object(
                runner_module.time, "sleep"
            ):
                result = runner_module.wait_for_status(
                    state_path=Path("/tmp/state.json"),
                    pid=123,
                    request_id=3,
                    accepted_statuses={"done", "failed", "superseded"},
                    timeout_seconds=60.0,
                    poll_interval=0.01,
                    baseline=baseline,
                    output_stall_timeout=30.0,
                    max_leaderboard_runs=2,
                )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["last_error"], "reached stable leaderboard runs 2 avg=15:39.179")
        self.assertEqual(written_states[0]["status"], "stop_requested")
        self.assertEqual(written_states[0]["last_error"], "reached stable leaderboard runs 2 avg=15:39.179")

    def test_wait_for_status_keeps_running_when_first_two_runs_are_unstable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            output_path = Path(temp_text) / "output.txt"
            mod_log_path = Path(temp_text) / "LogOutput.log"
            output_path.write_text("old\n", encoding="utf-8")
            mod_log_path.write_text("old\n", encoding="utf-8")
            baseline = OutputBaseline(
                output_path,
                file_signature(output_path),
                mod_log_path,
                file_signature(mod_log_path),
            )
            mod_log_path.write_text(
                "old\n[lb_maze_single] run=1 time=4:30.000\n[lb_maze_single] run=2 time=5:30.000\n",
                encoding="utf-8",
            )
            state_holder = {
                "request_id": 3,
                "status": "running",
                "target_script": "lb_start",
                "timeout_seconds": 90.0,
                "started_at": "2026-04-25T00:00:00Z",
                "finished_at": None,
                "last_error": None,
            }
            read_count = 0
            written_states: list[dict[str, object]] = []

            def read_state(_: Path) -> dict[str, object]:
                nonlocal read_count
                read_count += 1
                if read_count == 2:
                    mod_log_path.write_text(
                        "old\n"
                        "[lb_maze_single] run=1 time=4:30.000\n"
                        "[lb_maze_single] run=2 time=5:30.000\n"
                        "[lb_maze_single] run=3 time=5:00.000\n",
                        encoding="utf-8",
                    )
                return state_holder

            def write_state(_: Path, state: dict[str, object]) -> None:
                written_states.append(state)
                state_holder.update(
                    {
                        "request_id": 3,
                        "status": "failed",
                        "target_script": "lb_start",
                        "timeout_seconds": 90.0,
                        "started_at": "2026-04-25T00:00:00Z",
                        "finished_at": "2026-04-25T00:00:31Z",
                        "last_error": state["last_error"],
                    }
                )

            with mock.patch.object(runner_module, "read_state_file", side_effect=read_state), mock.patch.object(
                runner_module, "write_state_file", side_effect=write_state
            ), mock.patch.object(
                runner_module, "is_windows_process_running", return_value=True
            ), mock.patch.object(
                runner_module.time, "sleep"
            ):
                result = runner_module.wait_for_status(
                    state_path=Path("/tmp/state.json"),
                    pid=123,
                    request_id=3,
                    accepted_statuses={"done", "failed", "superseded"},
                    timeout_seconds=60.0,
                    poll_interval=0.01,
                    baseline=baseline,
                    output_stall_timeout=30.0,
                    max_leaderboard_runs=2,
                )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(written_states), 1)
        self.assertEqual(written_states[0]["last_error"], "reached stable leaderboard runs 3 avg=5:00.000")

    def test_build_progress_estimate_uses_item_snapshot_sim_time(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=(),
            mod_output_lines=(
                "[Info] item_snapshot request_id=7 real_elapsed=0.0 game_time=0 game_tick=0 gold=999999999",
                "[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 game_tick=4000 leaderboard_script=lb_maze gold=1000",
                "[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 game_tick=8000 leaderboard_script=lb_maze gold=11000",
            ),
        )

        lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(len(lines), 1)
        self.assertIn("script=lb_maze", lines[0])
        self.assertIn("item=gold", lines[0])
        self.assertIn("rate_per_game_second=1000.000", lines[0])

    def test_build_progress_estimate_uses_latest_leaderboard_script(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=(
                "[lb_maze_single] finished=false runs=31 average=3:04.233",
                "maze_multi gold= 32768 time= 19.72",
            ),
            mod_output_lines=(
                "[Info] item_snapshot request_id=1 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_maze_single gold=100",
                "[Info] item_snapshot request_id=2 real_elapsed=1.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_maze gold=1000",
                "[Info] item_snapshot request_id=2 real_elapsed=2.0 game_time=30 "
                "game_tick=12000 leaderboard_script=lb_maze gold=11000",
            ),
        )

        lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(len(lines), 1)
        self.assertIn("script=lb_maze", lines[0])
        self.assertIn("target=9863168", lines[0])

    def test_build_progress_estimate_covers_all_resource_leaderboards(self) -> None:
        cases = {
            "lb_hay": "hay",
            "lb_hay_single": "hay",
            "lb_wood": "wood",
            "lb_wood_single": "wood",
            "lb_carrots": "carrot",
            "lb_carrots_single": "carrot",
            "lb_pumpkins": "pumpkin",
            "lb_pumpkins_single": "pumpkin",
            "lb_cactus": "cactus",
            "lb_cactus_single": "cactus",
            "lb_dinosaur": "bone",
            "lb_maze": "gold",
            "lb_maze_single": "gold",
            "lb_sunflowers": "power",
            "lb_sunflowers_single": "power",
        }

        for script, item in cases.items():
            with self.subTest(script=script):
                outputs = runner_module.CapturedOutputs(
                    game_output_lines=(),
                    mod_output_lines=(
                        f"[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 "
                        f"game_tick=4000 leaderboard_script={script} {item}=100",
                        f"[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 "
                        f"game_tick=8000 leaderboard_script={script} {item}=1100",
                    ),
                )

                lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

                self.assertEqual(len(lines), 1)
                self.assertIn(f"script={script}", lines[0])
                self.assertIn(f"item={item}", lines[0])

    def test_build_progress_estimate_reports_unavailable_when_target_item_does_not_grow(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=(),
            mod_output_lines=(
                "[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_dinosaur bone=0",
                "[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_dinosaur bone=0",
            ),
        )

        lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(len(lines), 1)
        self.assertIn("script=lb_dinosaur", lines[0])
        self.assertIn("item=bone", lines[0])
        self.assertIn("unavailable", lines[0])
        self.assertIn("reason=no_positive_rate", lines[0])

    def test_build_progress_estimate_reports_target_reached_when_item_is_at_goal(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=(),
            mod_output_lines=(
                "[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_pumpkins pumpkin=200028160",
                "[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_pumpkins pumpkin=200028160",
            ),
        )

        lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(len(lines), 1)
        self.assertIn("script=lb_pumpkins", lines[0])
        self.assertIn("current=200028160", lines[0])
        self.assertIn("target_reached=true", lines[0])

    def test_leaderboard_summary_suppresses_resource_estimate_and_reports_average(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=("[lb_wood] finished=true runs=1 average=141:32.734",),
            mod_output_lines=(
                "[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_wood wood=100",
                "[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_wood wood=1100",
            ),
        )

        average_lines = runner_module.build_leaderboard_average_lines(outputs)
        estimate_lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(average_lines, ("leaderboard_average runs=1 average=141:32.734 stable=false",))
        self.assertEqual(estimate_lines, ())

    def test_finished_false_summary_does_not_count_as_completed_run(self) -> None:
        outputs = runner_module.CapturedOutputs(
            game_output_lines=("[lb_carrots] finished=false runs=1 average=12:42.618",),
            mod_output_lines=(
                "[Info] item_snapshot request_id=7 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_carrots carrot=100",
                "[Info] item_snapshot request_id=7 real_elapsed=2.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_carrots carrot=1100",
            ),
        )

        average_lines = runner_module.build_leaderboard_average_lines(outputs)
        estimate_lines = runner_module.build_progress_estimate_lines(outputs, "lb_start")

        self.assertEqual(average_lines, ())
        self.assertEqual(len(estimate_lines), 1)
        self.assertIn("progress_estimate script=lb_carrots", estimate_lines[0])

    def test_wait_for_ready_state_acknowledges_stale_terminal_state(self) -> None:
        states = iter(
            [
                {"request_id": 4, "status": "done"},
                {"request_id": 4, "status": "idle"},
            ]
        )
        with mock.patch.object(runner_module, "read_state_file", side_effect=lambda _: next(states)), mock.patch.object(
            runner_module, "is_windows_process_running", return_value=True
        ), mock.patch.object(runner_module, "acknowledge_terminal_state") as acknowledge, mock.patch.object(
            runner_module.time, "sleep"
        ):
            result = runner_module.wait_for_ready_state(
                state_path=Path("/tmp/state.json"),
                pid=123,
                timeout_seconds=5.0,
                poll_interval=0.01,
            )
        acknowledge.assert_called_once_with(Path("/tmp/state.json"))
        self.assertEqual(result["status"], "idle")

    def test_request_script_run_writes_incremented_requested_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            state_path = Path(temp_text) / "state.json"
            state_path.write_text(json.dumps({"request_id": 4, "status": "idle"}), encoding="utf-8")
            request_id = runner_module.request_script_run(
                state_path=state_path,
                target_script="lb_start.py",
                timeout_seconds=25.0,
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(request_id, 5)
        self.assertEqual(state["request_id"], 5)
        self.assertEqual(state["status"], "requested")
        self.assertEqual(state["target_script"], "lb_start")
        self.assertEqual(state["timeout_seconds"], 25.0)

    def test_write_state_file_retries_when_replace_is_temporarily_locked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            state_path = Path(temp_text) / "state.json"
            original_replace = runner_module.os.replace
            attempts = {"count": 0}

            def flaky_replace(src: str, dst: str) -> None:
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise PermissionError("sharing violation")
                original_replace(src, dst)

            with mock.patch.object(runner_module.os, "replace", side_effect=flaky_replace), mock.patch.object(
                runner_module.time, "sleep"
            ):
                runner_module.write_state_file(state_path, {"request_id": 1, "status": "idle"})
            written = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(attempts["count"], 2)
        self.assertEqual(written["request_id"], 1)
        self.assertEqual(written["status"], "idle")

    def test_main_collects_dual_output_and_acknowledges_done(self) -> None:
        done_state = {
            "request_id": 8,
            "status": "done",
            "target_script": "lb_start",
            "timeout_seconds": 20.0,
            "started_at": "2026-04-22T00:00:00Z",
            "finished_at": "2026-04-22T00:00:01Z",
            "last_error": None,
        }
        fake_outputs = runner_module.CapturedOutputs(
            game_output_lines=("game-a", "game-b"),
            mod_output_lines=("mod-a", "[lb_hay.py] finished=true runs=3 average=1:02.003"),
        )

        stream = io.StringIO()
        with mock.patch.object(
            runner_module, "resolve_game_executable", return_value=Path("/tmp/TheFarmerWasReplaced.exe")
        ), mock.patch.object(
            runner_module, "resolve_oracle_state_path", return_value=Path("/tmp/state.json")
        ), mock.patch.object(
            runner_module, "ensure_game_running", return_value=(456, False)
        ), mock.patch.object(
            runner_module, "wait_for_ready_state", return_value={"request_id": 7, "status": "idle"}
        ), mock.patch.object(
            runner_module, "capture_output_baseline", return_value=object()
        ), mock.patch.object(
            runner_module, "request_script_run", return_value=8
        ), mock.patch.object(
            runner_module, "wait_for_status", return_value=done_state
        ), mock.patch.object(
            runner_module, "capture_request_outputs", return_value=fake_outputs
        ), mock.patch.object(
            runner_module, "acknowledge_terminal_state"
        ) as acknowledge, contextlib.redirect_stdout(stream):
            result = runner_module.main(["--target-script", "lb_start", "--request-timeout", "20"])

        self.assertEqual(result, 0)
        acknowledge.assert_called_once_with(Path("/tmp/state.json"))
        text = stream.getvalue()
        self.assertIn("game_output_lines=2", text)
        self.assertIn("game_output game-a", text)
        self.assertIn("mod_output_lines=2", text)
        self.assertIn("mod_output mod-a", text)

    def test_main_request_only_writes_request_without_waiting_for_status(self) -> None:
        stream = io.StringIO()
        with mock.patch.object(
            runner_module, "resolve_game_executable", return_value=Path("/tmp/TheFarmerWasReplaced.exe")
        ), mock.patch.object(
            runner_module, "resolve_oracle_state_path", return_value=Path("/tmp/state.json")
        ), mock.patch.object(
            runner_module, "ensure_game_running", return_value=(456, False)
        ), mock.patch.object(
            runner_module, "wait_for_ready_state"
        ) as wait_for_ready, mock.patch.object(
            runner_module, "capture_output_baseline"
        ) as capture_baseline, mock.patch.object(
            runner_module, "request_script_run", return_value=8
        ) as request_run, mock.patch.object(
            runner_module, "wait_for_status"
        ) as wait_for_status, contextlib.redirect_stdout(stream):
            result = runner_module.main(
                [
                    "--target-script",
                    "lb_start",
                    "--request-timeout",
                    "90",
                    "--request-only",
                ]
            )

        self.assertEqual(result, 0)
        wait_for_ready.assert_not_called()
        capture_baseline.assert_not_called()
        request_run.assert_called_once()
        wait_for_status.assert_not_called()
        self.assertIn("mode=request_only", stream.getvalue())

    def test_main_status_only_reads_three_files_without_starting_game(self) -> None:
        stream = io.StringIO()
        state = {
            "request_id": 9,
            "status": "running",
            "target_script": "lb_start",
            "timeout_seconds": 90.0,
            "started_at": "2026-04-26T00:00:00Z",
            "finished_at": None,
            "last_error": None,
        }
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            save_root = root / "Saves" / "Save0"
            save_root.mkdir(parents=True)
            output_path = root / "output.txt"
            output_path.write_text("[lb_pumpkins] run=1 time=6:40.664\n", encoding="utf-8")
            game_root = root / "Game"
            log_path = game_root / "BepInEx" / "LogOutput.log"
            log_path.parent.mkdir(parents=True)
            log_path.write_text(
                "[Info] item_snapshot request_id=9 real_elapsed=1.0 game_time=10 "
                "game_tick=4000 leaderboard_script=lb_pumpkins pumpkin=100\n"
                "[Info] item_snapshot request_id=9 real_elapsed=2.0 game_time=20 "
                "game_tick=8000 leaderboard_script=lb_pumpkins pumpkin=1100\n",
                encoding="utf-8",
            )

            with mock.patch.object(
                runner_module, "resolve_oracle_state_path", return_value=Path("/tmp/state.json")
            ), mock.patch.object(
                runner_module, "read_state_file", return_value=state
            ), mock.patch.object(
                runner_module, "resolve_output_path", return_value=output_path
            ), mock.patch.object(
                runner_module, "resolve_bepinex_log_path", return_value=log_path
            ), mock.patch.object(
                runner_module, "resolve_game_executable"
            ) as resolve_exe, mock.patch.object(
                runner_module, "ensure_game_running"
            ) as ensure_game, contextlib.redirect_stdout(stream):
                result = runner_module.main(["--status-only", "--target-script", "lb_start", "--status-lines", "20"])

        self.assertEqual(result, 0)
        resolve_exe.assert_not_called()
        ensure_game.assert_not_called()
        text = stream.getvalue()
        self.assertIn("state request_id=9 status=running target_script=lb_start", text)
        self.assertIn("game_output [lb_pumpkins] run=1 time=6:40.664", text)
        self.assertIn("mod_output [Info] item_snapshot request_id=9", text)
        self.assertIn("leaderboard_average runs=1 average=6:40.664", text)

    def test_main_rejects_lb_start_done_without_leaderboard_summary(self) -> None:
        done_state = {
            "request_id": 8,
            "status": "done",
            "target_script": "lb_start",
            "timeout_seconds": 20.0,
            "started_at": "2026-04-22T00:00:00Z",
            "finished_at": "2026-04-22T00:00:01Z",
            "last_error": None,
        }
        fake_outputs = runner_module.CapturedOutputs(
            game_output_lines=(),
            mod_output_lines=("mod-a",),
        )

        stream = io.StringIO()
        with mock.patch.object(
            runner_module, "resolve_game_executable", return_value=Path("/tmp/TheFarmerWasReplaced.exe")
        ), mock.patch.object(
            runner_module, "resolve_oracle_state_path", return_value=Path("/tmp/state.json")
        ), mock.patch.object(
            runner_module, "ensure_game_running", return_value=(456, False)
        ), mock.patch.object(
            runner_module, "wait_for_ready_state", return_value={"request_id": 7, "status": "idle"}
        ), mock.patch.object(
            runner_module, "capture_output_baseline", return_value=object()
        ), mock.patch.object(
            runner_module, "request_script_run", return_value=8
        ), mock.patch.object(
            runner_module, "wait_for_status", return_value=done_state
        ), mock.patch.object(
            runner_module, "capture_request_outputs", return_value=fake_outputs
        ), mock.patch.object(
            runner_module, "acknowledge_terminal_state"
        ), contextlib.redirect_stdout(stream):
            result = runner_module.main(["--target-script", "lb_start", "--request-timeout", "20"])

        self.assertEqual(result, 5)
        self.assertIn("real_game_runner leaderboard_summary_missing", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
