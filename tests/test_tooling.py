from __future__ import annotations

import importlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from gamesimulator import config


def load_sync_module():
    try:
        return importlib.import_module("tools.sync_leaderboard_scripts")
    except ModuleNotFoundError:
        return None


class LayoutConfigTests(unittest.TestCase):
    def test_leaderboard_paths_move_to_repo_root(self) -> None:
        leaderboard_link = getattr(config, "LEADERBOARD_LINK", None)
        reference_root = getattr(config, "LEADERBOARD_REFERENCE_ROOT", None)
        self.assertEqual(leaderboard_link, config.REPO_ROOT / "leaderboard")
        self.assertEqual(reference_root, config.REPO_ROOT / "references" / "leaderboard_scripts")
        self.assertEqual(config.REFERENCES_ROOT, config.REPO_ROOT / "references")


class SyncDirectionTests(unittest.TestCase):
    def test_cli_argument_cur2save_is_supported(self) -> None:
        sync_module = load_sync_module()
        if sync_module is None or not hasattr(sync_module, "resolve_direction"):
            self.fail("tools.sync_leaderboard_scripts.resolve_direction 应该存在")
        self.assertEqual(sync_module.resolve_direction(["cur2save"]), "cur2save")

    def test_cli_argument_save2cur_is_supported(self) -> None:
        sync_module = load_sync_module()
        if sync_module is None or not hasattr(sync_module, "resolve_direction"):
            self.fail("tools.sync_leaderboard_scripts.resolve_direction 应该存在")
        self.assertEqual(sync_module.resolve_direction(["save2cur"]), "save2cur")

    def test_interactive_mode_requires_prompt_when_no_args(self) -> None:
        sync_module = load_sync_module()
        if sync_module is None or not hasattr(sync_module, "resolve_direction"):
            self.fail("tools.sync_leaderboard_scripts.resolve_direction 应该存在")
        with mock.patch("builtins.input", return_value="1"):
            self.assertEqual(sync_module.resolve_direction([]), "cur2save")
        with mock.patch("builtins.input", return_value="2"):
            self.assertEqual(sync_module.resolve_direction([]), "save2cur")


class SyncCopyTests(unittest.TestCase):
    def test_sync_only_copies_lb_python_files(self) -> None:
        sync_module = load_sync_module()
        if sync_module is None or not hasattr(sync_module, "sync_leaderboard_files"):
            self.fail("tools.sync_leaderboard_scripts.sync_leaderboard_files 应该存在")

        with tempfile.TemporaryDirectory() as source_dir_text, tempfile.TemporaryDirectory() as target_dir_text:
            source_dir = Path(source_dir_text)
            target_dir = Path(target_dir_text)

            (source_dir / "lb_alpha.py").write_text("alpha = 1\n", encoding="utf-8")
            (source_dir / "lb_beta.py").write_text("beta = 2\n", encoding="utf-8")
            (source_dir / "simulate.py").write_text("simulate = True\n", encoding="utf-8")
            (source_dir / "save.json").write_text("{\"k\": 1}\n", encoding="utf-8")
            (source_dir / "lb_note.txt").write_text("not python\n", encoding="utf-8")

            (target_dir / "lb_beta.py").write_text("old = True\n", encoding="utf-8")
            (target_dir / "simulate.py").write_text("keep = True\n", encoding="utf-8")
            (target_dir / "save.json").write_text("{\"keep\": true}\n", encoding="utf-8")

            copied = sync_module.sync_leaderboard_files(source_dir, target_dir)

            self.assertEqual(sorted(copied), ["lb_alpha.py", "lb_beta.py"])
            self.assertEqual((target_dir / "lb_alpha.py").read_text(encoding="utf-8"), "alpha = 1\n")
            self.assertEqual((target_dir / "lb_beta.py").read_text(encoding="utf-8"), "beta = 2\n")
            self.assertEqual((target_dir / "simulate.py").read_text(encoding="utf-8"), "keep = True\n")
            self.assertEqual((target_dir / "save.json").read_text(encoding="utf-8"), "{\"keep\": true}\n")
            self.assertFalse((target_dir / "lb_note.txt").exists())


if __name__ == "__main__":
    unittest.main()
