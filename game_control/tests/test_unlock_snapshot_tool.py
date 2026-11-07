from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tfwr_orchestrator import unlock_snapshot_tool


class UnlockSnapshotToolTests(unittest.TestCase):
    def test_cost_for_level_uses_multi_cost_then_factor(self) -> None:
        unlock = {
            "unlock_cost": (("Hay", 5),),
            "multi_unlock_cost": ((("Wood", 20),), (("Wood", 30), ("Carrot", 20))),
            "multi_unlock_factor": 8,
        }

        self.assertEqual(unlock_snapshot_tool.cost_for_level(unlock, 1), (("Hay", 5),))
        self.assertEqual(unlock_snapshot_tool.cost_for_level(unlock, 2), (("Wood", 20),))
        self.assertEqual(unlock_snapshot_tool.cost_for_level(unlock, 3), (("Wood", 30), ("Carrot", 20)))
        self.assertEqual(unlock_snapshot_tool.cost_for_level(unlock, 4), (("Wood", 240), ("Carrot", 160)))

    def test_effect_for_level_matches_known_modes(self) -> None:
        additive = {
            "max_unlock_level": 5,
            "multi_unlock_descr_mode": 1,
            "additive_percent_start": 50,
            "additive_percent_factor": 1.5,
            "unlocks": (),
        }
        grid = {"max_unlock_level": 9, "multi_unlock_descr_mode": 2, "unlocks": ()}
        megafarm = {"max_unlock_level": 5, "multi_unlock_descr_mode": 3, "unlocks": ()}
        per_10_seconds = {"max_unlock_level": 9, "multi_unlock_descr_mode": 4, "unlocks": ()}

        self.assertEqual(unlock_snapshot_tool.effect_for_level(additive, 5), "759.375%（约 7.59375x）")
        self.assertEqual(unlock_snapshot_tool.effect_for_level(grid, 7), "16x16")
        self.assertEqual(unlock_snapshot_tool.effect_for_level(megafarm, 3), "最多 8 架无人机")
        self.assertEqual(unlock_snapshot_tool.effect_for_level(per_10_seconds, 4), "0.8/s（每 10s 8 个）")

    def test_main_creates_output_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root_text:
            output_path = Path(temp_root_text) / "nested" / "snapshot.json"
            with mock.patch.object(unlock_snapshot_tool, "extract_snapshot", return_value={}):
                with mock.patch.object(unlock_snapshot_tool, "resolve_game_root", return_value=Path(temp_root_text)):
                    self.assertEqual(
                        unlock_snapshot_tool.main(["--format", "json", "--output", str(output_path)]),
                        0,
                    )

            self.assertEqual(output_path.read_text(encoding="utf-8"), "{}\n")


if __name__ == "__main__":
    unittest.main()
