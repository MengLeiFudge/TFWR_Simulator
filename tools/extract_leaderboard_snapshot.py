from __future__ import annotations

import argparse
from pathlib import Path
import pprint
import sys


try:
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
except Exception as exc:  # pragma: no cover - optional tooling dependency
    UnityPy = None
    TypeTreeGenerator = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


LEADERBOARD_FIELDS = (
    "leaderboardName",
    "steamLeaderboardName",
    "leaderboardType",
    "everythingUnlocked",
    "singleDrone",
    "startItems",
    "goalItems",
)


def normalize_item_block(raw: dict) -> tuple[tuple[str, float], ...]:
    rows = raw.get("serializeList", ()) if isinstance(raw, dict) else ()
    normalized = []
    for row in rows:
        normalized.append((snake_to_item_name(row["name"]), float(row["nr"])))
    return tuple(normalized)


def snake_to_item_name(name: str) -> str:
    return "_".join(part.capitalize() for part in name.split("_"))


def leaderboard_type_name(value: int) -> str:
    mapping = {
        0: "none",
        1: "simulation",
        2: "reset",
        3: "farm_resources",
    }
    return mapping[value]


def goal_from_item_block(raw: dict) -> tuple[str, str, int]:
    rows = raw.get("serializeList", ()) if isinstance(raw, dict) else ()
    if not rows:
        return ("unlock", "Leaderboard", 1)
    item = rows[0]
    return ("item", snake_to_item_name(item["name"]), int(float(item["nr"])))


def extract_snapshot(game_root: Path) -> dict[str, dict]:
    if UnityPy is None or TypeTreeGenerator is None:
        raise RuntimeError(
            "UnityPy / TypeTreeGeneratorAPI 未安装，无法提取 leaderboard snapshot。"
            f" 原始错误: {IMPORT_ERROR}"
        )

    data_root = next(path for path in game_root.iterdir() if path.name.endswith("_Data"))
    asset_paths = [
        data_root / "resources.assets",
        data_root / "globalgamemanagers.assets",
        data_root / "sharedassets0.assets",
    ]
    env = UnityPy.load(*(str(path) for path in asset_paths))
    generator = TypeTreeGenerator(next(iter(env.files.values())).unity_version)
    generator.load_local_game(str(game_root))
    env.typetree_generator = generator

    leaderboard_script_id = next(
        obj.path_id
        for obj in env.objects
        if obj.type.name == "MonoScript" and getattr(obj.read(check_read=False), "m_Name", "") == "LeaderboardSO"
    )

    snapshot: dict[str, dict] = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        head = obj.parse_monobehaviour_head()
        if getattr(head.m_Script, "path_id", None) != leaderboard_script_id:
            continue
        node = obj.generate_monobehaviour_node()
        data = obj.parse_as_dict(node=node, check_read=False)
        target_name = f"lb_{data['leaderboardName']}"
        goal_type, goal_resource, goal_amount = goal_from_item_block(data["goalItems"])
        snapshot[target_name] = {
            "leaderboard_name": data["leaderboardName"],
            "steam_leaderboard_name": data["steamLeaderboardName"],
            "leaderboard_type": leaderboard_type_name(int(data["leaderboardType"])),
            "everything_unlocked": bool(data["everythingUnlocked"]),
            "single_drone": bool(data["singleDrone"]),
            "goal_type": goal_type,
            "goal_resource": goal_resource,
            "goal_amount": goal_amount,
            "start_items": normalize_item_block(data["startItems"]),
        }
    return dict(sorted(snapshot.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从真实游戏资源提取 LeaderboardSO snapshot")
    parser.add_argument(
        "game_root",
        nargs="?",
        default="/mnt/d/Steam/steamapps/common/The Farmer Was Replaced",
        help="游戏根目录，默认使用当前机器上的 Steam 安装路径",
    )
    args = parser.parse_args(argv)
    snapshot = extract_snapshot(Path(args.game_root))
    pprint.pprint(snapshot, sort_dicts=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
