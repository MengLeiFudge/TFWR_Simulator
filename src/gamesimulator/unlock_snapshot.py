from __future__ import annotations


# 对齐 Farm.cs 里的 startUnlocks / allKeyWords：这些名字在脚本入口默认可用，
# dependency gate 不该再把它们当成需要额外 UnlockSO 的符号。
START_UNLOCK_DEPENDENCIES = frozenset(
    {
        "grass",
        "soil",
        "harvest",
        "pass",
        "do_a_flip",
        "pet_the_piggy",
        "grassland",
        "hay",
        "straw_hat",
        "tap",
    }
)

ALWAYS_AVAILABLE_DEPENDENCIES = frozenset(
    {
        "def",
        "while",
        "for",
        "if",
        "else",
        "elif",
        "and",
        "or",
        "not",
        "true",
        "false",
        "none",
        "entities",
        "grounds",
        "items",
        "unlocks",
        "leaderboards",
        "hats",
        "north",
        "south",
        "west",
        "east",
        "pass",
        "break",
        "continue",
        "return",
        "global",
        "import",
        "from",
    }
)


UNLOCK_METADATA = {
    "auto_unlock": {
        "parent_unlock": "costs",
        "max_unlock_level": 1,
        "unlocks": ("Unlocks", "unlock", "num_unlocked"),
        "unlock_cost": (("Pumpkin", 5000.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "cactus": {
        "parent_unlock": "pumpkins",
        "max_unlock_level": 6,
        "unlocks": ("swap", "cactus_seed", "measure"),
        "unlock_cost": (("Pumpkin", 5000.0),),
        "multi_unlock_cost": ((("Pumpkin", 20000.0),),),
        "multi_unlock_factor": 6.0,
    },
    "carrots": {
        "parent_unlock": "plant",
        "max_unlock_level": 10,
        "unlocks": ("carrot", "till", "can_trade", "trade", "Items", "carrot_seed"),
        "unlock_cost": (("Wood", 50.0),),
        "multi_unlock_cost": ((("Wood", 250.0),),),
        "multi_unlock_factor": 5.0,
    },
    "costs": {
        "parent_unlock": "dictionaries",
        "max_unlock_level": 1,
        "unlocks": ("get_cost", "Unlocks"),
        "unlock_cost": (("Pumpkin", 2500.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "debug": {
        "parent_unlock": "plant",
        "max_unlock_level": 1,
        "unlocks": ("print", "quick_print", "Unlocks", "str"),
        "unlock_cost": (("Hay", 50.0), ("Wood", 50.0)),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "debug_2": {
        "parent_unlock": "debug",
        "max_unlock_level": 1,
        "unlocks": ("set_execution_speed", "set_world_size"),
        "unlock_cost": (("Gold", 500.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "dictionaries": {
        "parent_unlock": "lists",
        "max_unlock_level": 1,
        "unlocks": ("dicts", "sets", "add", "dict", "set"),
        "unlock_cost": (("Pumpkin", 2500.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "dinosaurs": {
        "parent_unlock": "cactus",
        "max_unlock_level": 6,
        "unlocks": ("dinosaur", "egg", "bone", "change_hat", "hats", "dinosaur_hat", "apple", "can_move"),
        "unlock_cost": (("Cactus", 2000.0),),
        "multi_unlock_cost": ((("Cactus", 12000.0),),),
        "multi_unlock_factor": 6.0,
    },
    "expand": {
        "parent_unlock": "speed",
        "max_unlock_level": 9,
        "unlocks": ("move", "North", "South", "East", "West", "2for", "2range", "2get_world_size"),
        "unlock_cost": (("Hay", 30.0),),
        "multi_unlock_cost": (
            (("Wood", 20.0),),
            (("Wood", 30.0), ("Carrot", 20.0)),
            (("Wood", 100.0), ("Carrot", 50.0)),
            (("Pumpkin", 1000.0),),
        ),
        "multi_unlock_factor": 8.0,
    },
    "fertilizer": {
        "parent_unlock": "watering",
        "max_unlock_level": 4,
        "unlocks": ("use_item", "weird_substance"),
        "unlock_cost": (("Wood", 500.0),),
        "multi_unlock_cost": ((("Wood", 1500.0),),),
        "multi_unlock_factor": 6.0,
    },
    "functions": {
        "parent_unlock": "variables",
        "max_unlock_level": 1,
        "unlocks": ("functions", "def", "return", "global"),
        "unlock_cost": (("Carrot", 40.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "grass": {
        "parent_unlock": "loops",
        "max_unlock_level": 10,
        "unlocks": (),
        "unlock_cost": (("Hay", 100.0),),
        "multi_unlock_cost": ((("Hay", 300.0),), (("Wood", 500.0),)),
        "multi_unlock_factor": 5.0,
    },
    "hats": {
        "parent_unlock": "loops",
        "max_unlock_level": 1,
        "unlocks": ("change_hat", "gray_hat", "purple_hat", "green_hat", "brown_hat"),
        "unlock_cost": (("Hay", 50.0),),
        "multi_unlock_cost": ((),),
        "multi_unlock_factor": 4.0,
    },
    "import": {
        "parent_unlock": "functions",
        "max_unlock_level": 1,
        "unlocks": ("from",),
        "unlock_cost": (("Carrot", 80.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "leaderboard": {
        "parent_unlock": "simulation",
        "max_unlock_level": 1,
        "unlocks": ("leaderboard_run", "Leaderboards"),
        "unlock_cost": (("Gold", 1000000.0), ("Bone", 2000000.0)),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "lists": {
        "parent_unlock": "variables",
        "max_unlock_level": 1,
        "unlocks": ("append", "remove", "pop", "insert", "len", "list"),
        "unlock_cost": (("Carrot", 500.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "loops": {
        "parent_unlock": None,
        "max_unlock_level": 1,
        "unlocks": ("while", "True", "False", "break", "continue"),
        "unlock_cost": (("Hay", 5.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "mazes": {
        "parent_unlock": "fertilizer",
        "max_unlock_level": 6,
        "unlocks": ("hedge", "treasure", "gold", "measure", "can_move"),
        "unlock_cost": (("Weird_Substance", 1000.0),),
        "multi_unlock_cost": ((("Cactus", 12000.0),),),
        "multi_unlock_factor": 6.0,
    },
    "megafarm": {
        "parent_unlock": "mazes",
        "max_unlock_level": 5,
        "unlocks": ("get_drone_id", "num_drones", "max_drones", "wait_for", "spawn_drone", "has_finished"),
        "unlock_cost": (("Gold", 2000.0),),
        "multi_unlock_cost": ((("Gold", 8000.0),),),
        "multi_unlock_factor": 4.0,
    },
    "operators": {
        "parent_unlock": "plant",
        "max_unlock_level": 1,
        "unlocks": ("and", "or", "not"),
        "unlock_cost": (("Hay", 150.0), ("Wood", 10.0)),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "plant": {
        "parent_unlock": "speed",
        "max_unlock_level": 1,
        "unlocks": ("wood", "bush", "Entities", "clear"),
        "unlock_cost": (("Hay", 50.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "polyculture": {
        "parent_unlock": "pumpkins",
        "max_unlock_level": 5,
        "unlocks": ("get_companion",),
        "unlock_cost": (("Pumpkin", 3000.0),),
        "multi_unlock_cost": ((("Bone", 10000.0),),),
        "multi_unlock_factor": 5.0,
    },
    "pumpkins": {
        "parent_unlock": "trees",
        "max_unlock_level": 10,
        "unlocks": ("pumpkin", "pumpkin_seed", "dead_pumpkin"),
        "unlock_cost": (("Wood", 500.0), ("Carrot", 200.0)),
        "multi_unlock_cost": ((("Carrot", 1000.0),),),
        "multi_unlock_factor": 4.0,
    },
    "senses": {
        "parent_unlock": "operators",
        "max_unlock_level": 1,
        "unlocks": ("get_entity_type", "get_ground_type", "Grounds", "get_pos_x", "get_pos_y", "None", "num_items", "Items", "num_unlocked"),
        "unlock_cost": (("Hay", 100.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "simulation": {
        "parent_unlock": "timing",
        "max_unlock_level": 1,
        "unlocks": ("simulate",),
        "unlock_cost": (("Gold", 5000.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "speed": {
        "parent_unlock": "loops",
        "max_unlock_level": 5,
        "unlocks": ("can_harvest", "if", "else", "elif"),
        "unlock_cost": (("Hay", 20.0),),
        "multi_unlock_cost": (
            (("Wood", 20.0),),
            (("Wood", 50.0), ("Carrot", 50.0)),
            (("Carrot", 500.0),),
        ),
        "multi_unlock_factor": 2.0,
    },
    "sunflowers": {
        "parent_unlock": "watering",
        "max_unlock_level": 1,
        "unlocks": ("sunflower_seed", "sunflower", "power", "get_active_power", "measure"),
        "unlock_cost": (("Carrot", 500.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 0.0,
    },
    "the_farmers_remains": {
        "parent_unlock": "dinosaurs",
        "max_unlock_level": 1,
        "unlocks": ("change_hat",),
        "unlock_cost": (("Bone", 100000000.0),),
        "multi_unlock_cost": ((),),
        "multi_unlock_factor": 4.0,
    },
    "timing": {
        "parent_unlock": "debug",
        "max_unlock_level": 1,
        "unlocks": ("get_time", "get_tick_count"),
        "unlock_cost": (("Pumpkin", 1000.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "top_hat": {
        "parent_unlock": "mazes",
        "max_unlock_level": 1,
        "unlocks": ("change_hat",),
        "unlock_cost": (("Gold", 100000000.0), ("Cactus", 1000000000.0), ("Hay", 1000000000.0), ("Carrot", 1000000000.0), ("Wood", 10000000000.0)),
        "multi_unlock_cost": ((),),
        "multi_unlock_factor": 4.0,
    },
    "trees": {
        "parent_unlock": "carrots",
        "max_unlock_level": 10,
        "unlocks": ("tree",),
        "unlock_cost": (("Wood", 50.0), ("Carrot", 70.0)),
        "multi_unlock_cost": ((("Hay", 300.0),),),
        "multi_unlock_factor": 4.0,
    },
    "utilities": {
        "parent_unlock": "functions",
        "max_unlock_level": 1,
        "unlocks": ("min", "max", "abs", "random"),
        "unlock_cost": (("Pumpkin", 1000.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "variables": {
        "parent_unlock": "operators",
        "max_unlock_level": 1,
        "unlocks": (),
        "unlock_cost": (("Carrot", 35.0),),
        "multi_unlock_cost": (),
        "multi_unlock_factor": 2.0,
    },
    "watering": {
        "parent_unlock": "carrots",
        "max_unlock_level": 9,
        "unlocks": ("water", "use_item", "get_water"),
        "unlock_cost": (("Wood", 50.0),),
        "multi_unlock_cost": ((("Wood", 200.0),),),
        "multi_unlock_factor": 4.0,
    },
}

RESET_UNLOCK_NAMES = (
    "auto_unlock",
    "costs",
    "debug",
    "debug_2",
    "dictionaries",
    "functions",
    "import",
    "lists",
    "loops",
    "operators",
    "senses",
    "simulation",
    "timing",
    "utilities",
    "variables",
)


def _to_const_name(asset_name: str) -> str:
    return "_".join(part.capitalize() for part in asset_name.split("_"))


DEFAULT_UNLOCK_LEVELS = {
    _to_const_name(name): data["max_unlock_level"]
    for name, data in UNLOCK_METADATA.items()
}

RESET_UNLOCK_LEVELS = {
    _to_const_name(name): 1
    for name in RESET_UNLOCK_NAMES
}


def normalize_unlock_name(name: str) -> str:
    return name.lower()


def get_unlock_metadata(name: str) -> dict | None:
    return UNLOCK_METADATA.get(normalize_unlock_name(name))


def is_default_available_dependency(name: str) -> bool:
    normalized = normalize_unlock_name(name)
    return (
        normalized in START_UNLOCK_DEPENDENCIES
        or normalized in ALWAYS_AVAILABLE_DEPENDENCIES
    )


def resolve_dependency_unlock(name: str) -> tuple[str, int] | None:
    target = normalize_unlock_name(name)
    for unlock_name, metadata in UNLOCK_METADATA.items():
        if unlock_name == target:
            return (unlock_name, 1)
        for dependency in metadata["unlocks"]:
            raw = normalize_unlock_name(dependency)
            digits = ""
            while raw and raw[0].isdigit():
                digits += raw[0]
                raw = raw[1:]
            required_level = int(digits) if digits else 1
            if raw == target:
                return (unlock_name, required_level)
    return None
