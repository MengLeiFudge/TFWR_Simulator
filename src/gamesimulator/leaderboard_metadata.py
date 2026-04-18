from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

from .leaderboard_snapshot import LEADERBOARD_SNAPSHOT


@dataclass(frozen=True)
class LeaderboardMetadata:
    target_name: str
    leaderboard_name: str
    steam_leaderboard_name: str
    leaderboard_type: str
    single_drone: bool
    everything_unlocked: bool
    goal_type: str
    goal_resource: str
    goal_amount: int
    start_items: tuple[tuple[str, float], ...]


_ENTRY_PATTERN = re.compile(
    r"^\s*(?P<name>[A-Za-z_]+):\s*Leaderboard\s*\n\s*\"\"\"\s*(?P<doc>.*?)\s*\"\"\"",
    re.MULTILINE | re.DOTALL,
)
_GOAL_PATTERN = re.compile(
    r"Farm\s+(?P<amount>[0-9_]+)[ _]+(?P<resource>[A-Za-z_]+)\s+with\s+(?:a\s+)?(?P<kind>single|multiple)\s+drone(?:s)?",
    re.IGNORECASE,
)

_RESOURCE_NAME_MAP = {
    "hay": "Hay",
    "wood": "Wood",
    "carrots": "Carrot",
    "pumpkins": "Pumpkin",
    "cacti": "Cactus",
    "bones": "Bone",
    "gold": "Gold",
    "power": "Power",
}

@lru_cache(maxsize=16)
def load_leaderboard_metadata(save_root: str | Path) -> dict[str, LeaderboardMetadata]:
    save_root = Path(save_root).resolve()
    builtins_text = (save_root / "__builtins__.py").read_text(encoding="utf-8")

    entries: dict[str, LeaderboardMetadata] = {}
    for target_name, payload in LEADERBOARD_SNAPSHOT.items():
        entries[target_name] = LeaderboardMetadata(
            target_name=target_name,
            leaderboard_name=payload["leaderboard_name"],
            steam_leaderboard_name=payload["steam_leaderboard_name"],
            leaderboard_type=payload["leaderboard_type"],
            single_drone=payload["single_drone"],
            everything_unlocked=payload["everything_unlocked"],
            goal_type=payload["goal_type"],
            goal_resource=payload["goal_resource"],
            goal_amount=payload["goal_amount"],
            start_items=tuple(payload["start_items"]),
        )

    for match in _ENTRY_PATTERN.finditer(builtins_text):
        enum_name = match.group("name")
        script_name = f"lb_{enum_name.lower()}"
        if script_name in entries:
            continue
        goal_match = _GOAL_PATTERN.search(match.group("doc"))
        if goal_match is None:
            continue
        amount = int(goal_match.group("amount").replace("_", ""))
        resource_key = goal_match.group("resource").lower().strip("_")
        goal_resource = _RESOURCE_NAME_MAP.get(resource_key)
        if goal_resource is None:
            continue
        entries[script_name] = LeaderboardMetadata(
            target_name=script_name,
            leaderboard_name=enum_name.lower(),
            steam_leaderboard_name=enum_name.lower(),
            leaderboard_type="farm_resources",
            single_drone=(goal_match.group("kind").lower() == "single"),
            everything_unlocked=True,
            goal_type="item",
            goal_resource=goal_resource,
            goal_amount=amount,
            start_items=(),
        )

    return entries


def resolve_leaderboard_metadata(target_name: str, save_root: str | Path) -> LeaderboardMetadata | None:
    target_stem = Path(target_name).stem
    if not target_stem.startswith("lb_"):
        target_stem = f"lb_{target_stem.lower()}"
    return load_leaderboard_metadata(save_root).get(target_stem)


def default_start_items(target_name: str, save_root: str | Path) -> tuple[tuple[str, float], ...]:
    metadata = resolve_leaderboard_metadata(target_name, save_root)
    if metadata is None:
        return ()
    return metadata.start_items
