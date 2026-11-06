"""脚本枚举、原版作物资源参数与科技成本；本地运行不依赖游戏安装。"""

from enum import StrEnum
import json
from pathlib import Path


class Direction(StrEnum):
    """原版方向枚举顺序同时用于迷宫墙和随机方向排序。"""
    North = 'North'
    East = 'East'
    South = 'South'
    West = 'West'


DATA = json.loads(Path(__file__).with_name('resources.json').read_text())
UNDERGROUND = json.loads(Path(__file__).with_name('underground_resources.json').read_text())
DATA['crops'].update(UNDERGROUND['crops'])
DATA['special'].update(UNDERGROUND['special'])
for crop, spec in DATA['crops'].items():
    spec['grounds'] = UNDERGROUND['crop_grounds'][crop]
Grounds = StrEnum('Grounds', {key: 'Grounds.' + key for key in UNDERGROUND['grounds']})
Entities = StrEnum('Entities', {key: 'Entities.' + key for key in (*DATA['crops'], *DATA['special'])})
Items = StrEnum('Items', {key: 'Items.' + key for key in UNDERGROUND['item_order']})
Hats = StrEnum('Hats', {key: 'Hats.' + key for key in (*DATA['hats'], *UNDERGROUND['hats'])})
Leaderboards = StrEnum('Leaderboards', {key: 'Leaderboards.' + key for key in (*DATA['leaderboards'], *UNDERGROUND['leaderboards'])})
CROPS = {Entities[key]: value for key, value in DATA['crops'].items()}
OBJECTS = {Entities[key]: value for key, value in (DATA['crops'] | DATA['special']).items()}
UNLOCK_DATA = json.loads((Path(__file__).resolve().parents[2]
                          / 'references/unlocks/unlock_snapshot.json').read_text())
UNLOCK_DATA.update(UNDERGROUND['unlocks'])
Unlocks = StrEnum('Unlocks', {key.title(): 'Unlocks.' + key.title() for key in UNLOCK_DATA})
VECTORS = {Direction.North: (0, 1), Direction.East: (1, 0),
           Direction.South: (0, -1), Direction.West: (-1, 0)}
