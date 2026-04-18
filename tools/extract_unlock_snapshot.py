from __future__ import annotations

import argparse
from pathlib import Path
import pprint


try:
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    from UnityPy.helpers.TypeTreeNode import TypeTreeNode
except Exception as exc:  # pragma: no cover - optional tooling dependency
    UnityPy = None
    TypeTreeGenerator = None
    TypeTreeNode = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def snake_to_const_name(name: str) -> str:
    return "_".join(part.capitalize() for part in name.split("_"))


def normalize_item_block(raw: dict) -> tuple[tuple[str, float], ...]:
    rows = raw.get("serializeList", ()) if isinstance(raw, dict) else ()
    return tuple((snake_to_const_name(row["name"]), float(row["nr"])) for row in rows)


def extract_snapshot(game_root: Path) -> dict[str, dict]:
    if UnityPy is None or TypeTreeGenerator is None or TypeTreeNode is None:
        raise RuntimeError(
            "UnityPy / TypeTreeGeneratorAPI 未安装，无法提取 unlock snapshot。"
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

    unlock_script_id = next(
        obj.path_id
        for obj in env.objects
        if obj.type.name == "MonoScript" and getattr(obj.read(check_read=False), "m_Name", "") == "UnlockSO"
    )

    snapshot: dict[str, dict] = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        head = obj.parse_monobehaviour_head()
        if getattr(head.m_Script, "path_id", None) != unlock_script_id:
            continue

        full = obj.generate_monobehaviour_node()
        fixed_children = []
        for child in full.m_Children:
            if child.m_Name == "unlocks":
                child = TypeTreeNode(
                    child.m_Level,
                    "vector",
                    child.m_Name,
                    child.m_ByteSize,
                    child.m_Version,
                    child.m_Children,
                    m_TypeFlags=child.m_TypeFlags,
                    m_VariableCount=child.m_VariableCount,
                    m_Index=child.m_Index,
                    m_MetaFlag=child.m_MetaFlag,
                    m_RefTypeHash=child.m_RefTypeHash,
                )
            fixed_children.append(child)

        fixed_root = TypeTreeNode(
            full.m_Level,
            full.m_Type,
            full.m_Name,
            full.m_ByteSize,
            full.m_Version,
            fixed_children,
            m_TypeFlags=full.m_TypeFlags,
            m_VariableCount=full.m_VariableCount,
            m_Index=full.m_Index,
            m_MetaFlag=full.m_MetaFlag,
            m_RefTypeHash=full.m_RefTypeHash,
        )

        data = obj.parse_as_dict(node=fixed_root, check_read=False)
        snapshot[data["unlockName"]] = {
            "parent_unlock": data["parentUnlock"] or None,
            "max_unlock_level": int(data["maxUnlockLevel"]),
            "unlocks": tuple(data["unlocks"]),
            "unlock_cost": normalize_item_block(data["unlockCost"]),
            "multi_unlock_cost": tuple(normalize_item_block(block) for block in data["multiUnlockCost"]),
            "multi_unlock_factor": float(data["multiUnlockFactor"]),
        }

    return dict(sorted(snapshot.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从真实游戏资源提取 UnlockSO snapshot")
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
