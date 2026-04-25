from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tfwr_orchestrator import leaderboard_sync


class LeaderboardSyncTests(unittest.TestCase):
    def test_render_lb_start_uses_expected_enum_and_default_iterations(self) -> None:
        text = leaderboard_sync.render_lb_start("lb_hay_single")
        self.assertIn('leaderboard_run(Leaderboards.Hay_Single, "lb_hay_single", 10000)', text)

    def test_render_lb_start_uses_fastest_reset_iterations(self) -> None:
        text = leaderboard_sync.render_lb_start("lb_fastest_reset")
        self.assertIn('leaderboard_run(Leaderboards.Fastest_Reset, "lb_fastest_reset", 200)', text)

    def test_sync_single_cur2save_copies_only_requested_script_and_generates_lb_start(self) -> None:
        with tempfile.TemporaryDirectory() as source_text, tempfile.TemporaryDirectory() as target_text:
            source_dir = Path(source_text)
            target_dir = Path(target_text)
            (source_dir / "lb_alpha.py").write_text("alpha = 1\n", encoding="utf-8")
            (source_dir / "lb_beta.py").write_text("beta = 2\n", encoding="utf-8")
            (source_dir / "simulate.py").write_text("simulate = True\n", encoding="utf-8")

            original_link = leaderboard_sync.GAMESAVE_LINK
            try:
                leaderboard_sync.GAMESAVE_LINK = target_dir
                copied = leaderboard_sync.sync_single_leaderboard_file(source_dir, target_dir, "lb_beta")
            finally:
                leaderboard_sync.GAMESAVE_LINK = original_link

            self.assertEqual(copied, ["lb_beta.py", "lb_start.py"])
            self.assertFalse((target_dir / "lb_alpha.py").exists())
            self.assertEqual((target_dir / "lb_beta.py").read_text(encoding="utf-8"), "beta = 2\n")
            self.assertIn(
                'leaderboard_run(Leaderboards.Beta, "lb_beta", 10000)',
                (target_dir / "lb_start.py").read_text(encoding="utf-8"),
            )

    def test_sync_single_rejects_unsupported_shift_operator(self) -> None:
        with tempfile.TemporaryDirectory() as source_text, tempfile.TemporaryDirectory() as target_text:
            source_dir = Path(source_text)
            target_dir = Path(target_text)
            (source_dir / "lb_bad.py").write_text("value = 1 << 2\n", encoding="utf-8")

            with self.assertRaisesRegex(
                leaderboard_sync.UnsupportedGameSyntaxError,
                r"游戏脚本不支持运算符 <<: lb_bad.py:L1",
            ):
                leaderboard_sync.sync_single_leaderboard_file(source_dir, target_dir, "lb_bad")

    def test_sync_all_copies_only_lb_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as source_text, tempfile.TemporaryDirectory() as target_text:
            source_dir = Path(source_text)
            target_dir = Path(target_text)
            (source_dir / "lb_alpha.py").write_text("alpha = 1\n", encoding="utf-8")
            (source_dir / "lb_beta.py").write_text("beta = 2\n", encoding="utf-8")
            (source_dir / "simulate.py").write_text("simulate = True\n", encoding="utf-8")
            (source_dir / "lb_note.txt").write_text("not python\n", encoding="utf-8")

            copied = leaderboard_sync.sync_all_leaderboard_files(source_dir, target_dir)

            self.assertEqual(sorted(copied), ["lb_alpha.py", "lb_beta.py"])
            self.assertEqual((target_dir / "lb_alpha.py").read_text(encoding="utf-8"), "alpha = 1\n")
            self.assertEqual((target_dir / "lb_beta.py").read_text(encoding="utf-8"), "beta = 2\n")
            self.assertFalse((target_dir / "simulate.py").exists())
            self.assertFalse((target_dir / "lb_note.txt").exists())


if __name__ == "__main__":
    unittest.main()
