from __future__ import annotations

import argparse
import json
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


from .config import resolve_game_root


Number = int | float


MULTI_UNLOCK_MODE_NAMES = {
    0: "none",
    1: "additive_percent",
    2: "grid_size",
    3: "megafarm",
    4: "per_10_seconds",
}


def snake_to_const_name(name: str) -> str:
    return "_".join(part.capitalize() for part in name.split("_"))


def normalize_number(value: float) -> Number:
    rounded = round(float(value), 3)
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def normalize_item_block(raw: dict) -> tuple[tuple[str, Number], ...]:
    rows = raw.get("serializeList", ()) if isinstance(raw, dict) else ()
    return tuple((snake_to_const_name(row["name"]), normalize_number(row["nr"])) for row in rows)


def item_block_to_dict(block: tuple[tuple[str, Number], ...]) -> dict[str, Number]:
    return {name: amount for name, amount in block}


def scale_item_block(block: tuple[tuple[str, Number], ...], factor: float) -> tuple[tuple[str, Number], ...]:
    result = []
    for name, amount in block:
        result.append((name, normalize_number(amount * factor)))
    return tuple(result)


def cost_for_level(unlock: dict, level: int) -> tuple[tuple[str, Number], ...]:
    if level <= 1:
        return unlock["unlock_cost"]
    num_unlocked = level - 1
    multi_cost = unlock["multi_unlock_cost"]
    if not multi_cost:
        return ()
    if len(multi_cost) >= num_unlocked:
        return multi_cost[num_unlocked - 1]
    factor_power = num_unlocked - len(multi_cost)
    return scale_item_block(multi_cost[-1], unlock["multi_unlock_factor"] ** factor_power)


def world_size_for_expand_level(level: int) -> str:
    sizes = {
        0: "1x1",
        1: "1x3",
        2: "3x3",
        3: "4x4",
        4: "6x6",
        5: "8x8",
        6: "12x12",
        7: "16x16",
        8: "24x24",
        9: "32x32",
    }
    return sizes.get(level, "")


def effect_for_level(unlock: dict, level: int) -> str:
    mode = unlock["multi_unlock_descr_mode"]
    if unlock["max_unlock_level"] <= 1:
        symbols = ", ".join(unlock["unlocks"])
        return f"解锁符号/能力：{symbols}" if symbols else "一次性解锁"
    if mode == 1:
        percent = (unlock["additive_percent_factor"] ** (level - 1)) * (100.0 + unlock["additive_percent_start"])
        multiplier = percent / 100.0
        return f"{percent:g}%（约 {multiplier:g}x）"
    if mode == 2:
        return world_size_for_expand_level(level)
    if mode == 3:
        return f"最多 {2 ** level} 架无人机"
    if mode == 4:
        per_second = (2 ** max(0, level - 1)) * 0.1
        per_10_seconds = per_second * 10
        return f"{per_second:g}/s（每 10s {per_10_seconds:g} 个）"
    return ""


def enrich_unlock(unlock: dict) -> dict:
    levels = []
    for level in range(1, unlock["max_unlock_level"] + 1):
        levels.append(
            {
                "level": level,
                "cost": item_block_to_dict(cost_for_level(unlock, level)),
                "effect": effect_for_level(unlock, level),
            }
        )
    result = dict(unlock)
    result["levels"] = tuple(levels)
    return result


def format_number(value: Number) -> str:
    if isinstance(value, int):
        return str(value)
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def format_item_block(block: dict[str, Number]) -> str:
    if not block:
        return "-"
    parts = []
    for name, amount in block.items():
        parts.append(f"{name} {format_number(amount)}")
    return ", ".join(parts)


def format_markdown(snapshot: dict[str, dict]) -> str:
    lines = [
        "# TFWR 科技事实表",
        "",
        "本文件由真实游戏资源 `UnlockSO` 提取并按反编译逻辑展开。",
        "",
        "## 事实源",
        "",
        "- `UnlockSO` 字段定义：`Core.decompiled.cs` 的 `UnlockSO`。",
        "- 每级成本：`Farm.GetUnlockCost()`；多级科技先使用 `multiUnlockCost`，超出后按 `multiUnlockFactor` 放大最后一档成本。",
        "- 前置判断：`Farm.UnlockOrUpgrade()` 会检查 `parentUnlock`。",
        "- 每级效果显示：`TooltipUtils.UnlockTooltip()` 的 `MultiUnlockDescrMode`。",
        "- 实际速度：`Farm.MaxSpeedFactor()` 为 `1.5 ** speed_level`，有 Power 时再乘 `2`。",
        "- 水和肥料：`ReceiveWater()` / `ReceiveFertilizer()` 为 `20 / (1 << level)` 秒获得 1 个。",
        "- 作物 / 迷宫 / 恐龙产量类升级：`Growable.YieldFactor` 使用 `1 << (level - 1)`。",
        "- 地图大小：`GridManager.WorldSize` 调 `Helper.WorldSizeScale(expand_level)`；一级扩张特判为 `1x3`。",
        "- 多无人机：`max_drones()` / `spawn_drone()` 使用 `Helper.NumDrones(megafarm_level)`，即 `2 ** level`。",
        "",
        "## 科技总览",
        "",
        "| 科技 | 前置 | 最高级 | 首次成本 | 解锁符号 / 能力 |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for name, unlock in snapshot.items():
        first_cost = format_item_block(unlock["levels"][0]["cost"])
        symbols = ", ".join(unlock["unlocks"]) or "-"
        parent = unlock["parent_unlock"] or "-"
        lines.append(f"| `{name}` | `{parent}` | {unlock['max_unlock_level']} | {first_cost} | {symbols} |")

    lines.extend(["", "## 每级成本与效果", ""])
    for name, unlock in snapshot.items():
        parent = unlock["parent_unlock"] or "-"
        mode = unlock["multi_unlock_descr_mode_name"]
        lines.extend(
            [
                f"### `{name}`",
                "",
                f"- 前置：`{parent}`",
                f"- 最高级：`{unlock['max_unlock_level']}`",
                f"- 效果模式：`{mode}`",
                f"- 描述键：`{unlock['description_key']}` / `{unlock['multi_unlock_descr_key']}`",
                "",
                "| 等级 | 成本 | 效果 |",
                "| ---: | --- | --- |",
            ]
        )
        for level in unlock["levels"]:
            lines.append(f"| {level['level']} | {format_item_block(level['cost'])} | {level['effect']} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


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
        mode = int(data["multiUnlockDescrMode"])
        snapshot[data["unlockName"]] = {
            "parent_unlock": data["parentUnlock"] or None,
            "max_unlock_level": int(data["maxUnlockLevel"]),
            "description_key": data["description"],
            "multi_unlock_descr_key": data["multiUnlockDescr"],
            "multi_unlock_descr_mode": mode,
            "multi_unlock_descr_mode_name": MULTI_UNLOCK_MODE_NAMES.get(mode, f"unknown_{mode}"),
            "additive_percent_start": float(data["additivePercentStart"]),
            "additive_percent_factor": float(data["additivePercentFactor"]),
            "unlocks": tuple(data["unlocks"]),
            "unlock_cost": normalize_item_block(data["unlockCost"]),
            "multi_unlock_cost": tuple(normalize_item_block(block) for block in data["multiUnlockCost"]),
            "multi_unlock_factor": float(data["multiUnlockFactor"]),
        }

    return {name: enrich_unlock(unlock) for name, unlock in sorted(snapshot.items())}


def json_ready(value):
    if isinstance(value, tuple):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从真实游戏资源提取 UnlockSO snapshot")
    parser.add_argument(
        "game_root",
        nargs="?",
        default=None,
        help="游戏根目录；不传时优先读取 TFWR_GAME_ROOT，再回退到默认 Steam 安装路径",
    )
    parser.add_argument(
        "--format",
        choices=("python", "json", "markdown"),
        default="python",
        help="输出格式",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径；不传则写到 stdout",
    )
    args = parser.parse_args(argv)
    snapshot = extract_snapshot(resolve_game_root(args.game_root))
    if args.format == "json":
        output = json.dumps(json_ready(snapshot), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    elif args.format == "markdown":
        output = format_markdown(json_ready(snapshot))
    else:
        output = pprint.pformat(snapshot, sort_dicts=False) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0
