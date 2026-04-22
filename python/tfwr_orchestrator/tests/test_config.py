from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tfwr_orchestrator import config


class LayoutConfigTests(unittest.TestCase):
    def test_leaderboard_paths_stay_at_repo_root(self) -> None:
        self.assertEqual(config.LEADERBOARD_LINK, config.REPO_ROOT / "leaderboard")
        self.assertEqual(config.LEADERBOARD_REFERENCE_ROOT, config.REPO_ROOT / "references" / "leaderboard_scripts")
        self.assertEqual(config.REFERENCES_ROOT, config.REPO_ROOT / "references")

    def test_decompiled_source_root_stays_under_references(self) -> None:
        self.assertEqual(config.DECOMPILED_SOURCE_ROOT, config.REPO_ROOT / "references" / "DecompiledSource")

    def test_resolve_game_root_uses_explicit_path(self) -> None:
        with tempfile.TemporaryDirectory() as game_root_text:
            game_root = Path(game_root_text)
            self.assertEqual(config.resolve_game_root(game_root), game_root.resolve())

    def test_resolve_game_root_reads_env_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as game_root_text:
            game_root = Path(game_root_text)
            with mock.patch.dict(os.environ, {"TFWR_GAME_ROOT": str(game_root)}, clear=False):
                self.assertEqual(config.resolve_game_root(None), game_root.resolve())

    def test_resolve_persistent_data_root_uses_save_root_parent(self) -> None:
        with tempfile.TemporaryDirectory() as persistent_text:
            persistent_root = Path(persistent_text)
            save_root = persistent_root / "Saves" / "Save0"
            save_root.mkdir(parents=True)
            self.assertEqual(config.resolve_persistent_data_root(save_root), persistent_root.resolve())

    def test_resolve_output_path_points_to_output_txt_beside_saves(self) -> None:
        with tempfile.TemporaryDirectory() as persistent_text:
            persistent_root = Path(persistent_text)
            save_root = persistent_root / "Saves" / "Save0"
            save_root.mkdir(parents=True)
            self.assertEqual(config.resolve_output_path(save_root), persistent_root.resolve() / "output.txt")

    def test_resolve_bepinex_log_path_points_to_game_root_log(self) -> None:
        with tempfile.TemporaryDirectory() as game_root_text:
            game_root = Path(game_root_text)
            log_path = game_root / "BepInEx" / "LogOutput.log"
            log_path.parent.mkdir(parents=True)
            log_path.write_text("hello\n", encoding="utf-8")
            self.assertEqual(config.resolve_bepinex_log_path(game_root), log_path.resolve())


if __name__ == "__main__":
    unittest.main()
