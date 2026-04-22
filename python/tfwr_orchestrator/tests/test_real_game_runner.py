from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tfwr_orchestrator import real_game_runner as runner_module
from tfwr_orchestrator.output_capture import EMPTY_SIGNATURE, capture_output_baseline, capture_request_outputs, file_signature


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
            ]
        )
        self.assertEqual(args.target_script, "lb_start.py")
        self.assertEqual(args.request_timeout, 12.0)
        self.assertEqual(args.startup_timeout, 30.0)
        self.assertEqual(args.total_timeout, 99.0)
        self.assertEqual(args.poll_interval, 0.2)

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
            )
        self.assertEqual(result["status"], "superseded")
        self.assertEqual(result["request_id"], 3)
        self.assertEqual(result["last_error"], "superseded by request_id=4")

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
        ) as acknowledge, contextlib.redirect_stdout(stream):
            result = runner_module.main(["--target-script", "lb_start", "--request-timeout", "20"])

        self.assertEqual(result, 0)
        acknowledge.assert_called_once_with(Path("/tmp/state.json"))
        text = stream.getvalue()
        self.assertIn("game_output_lines=2", text)
        self.assertIn("game_output game-a", text)
        self.assertIn("mod_output_lines=1", text)
        self.assertIn("mod_output mod-a", text)


if __name__ == "__main__":
    unittest.main()
