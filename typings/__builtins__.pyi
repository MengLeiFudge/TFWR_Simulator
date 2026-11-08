# TFWR 编辑器类型声明；从 Save0 的同源模板提取，省略说明字符串与函数体。
# 来源 SHA256：7c3d23a03b49816eb9080a957f2afbdca1e8cbe52d0c8ac47e2c4466396df1c7。
# 原贡献者：Noon、KlingonDragon、dieckie、Flekay、Zoroark-Zwart、Rat、SCD-3。
# 地下枚举补充依据 simulator/local_simulator/underground_resources.json。
# 游戏不是 Python；模板对部分可选返回省略 None，详见 README.md。

from typing import Any, Literal, overload
from collections.abc import Callable, Iterable
from types import ModuleType
from builtins import bool, int, float, str as string, tuple, range as range_class, list, set, dict
from builtins import bool as _bool, int as _int, float as _float, range as _range, tuple as _tuple, list as _list, set as _set, dict as _dict
from enum import Enum as _Enum

type Primitive = _bool | _int | _float | string | None
type Enums = Entity | Entities | Ground | Grounds | Hat | Hats | Item | Items | Leaderboard | Leaderboards | Unlock | Unlocks
type Hashable = Primitive | range_class | tuple[Hashable, ...] | Enums | Drone[AnyTFWR]
type _AnyCollection = dict[Hashable, AnyTFWR] | _dict[Hashable, AnyTFWR] | set[Hashable] | _set[Hashable] | list[AnyTFWR] | _list[AnyTFWR] | _tuple[AnyTFWR, ...]
type AnyTFWR = Primitive | range_class | _range | Callable[..., AnyTFWR] | ModuleType | _AnyCollection | Direction | Enums | Drone[AnyTFWR]
type AnyIterable = string | range_class | _range | _AnyCollection | Entities | Grounds | Hats | Items | Leaderboards | Unlocks

@overload
def range(stop: _float, /) -> range_class: ...
@overload
def range(start: _float, stop: _float, /) -> range_class: ...
@overload
def range(start: _float, stop: _float, step: _float, /) -> range_class: ...
def add[K: Hashable](given_set: set[K] | _set[K], object: K, /) -> None: ...
def append[V: Any](given_list: list[V] | _list[V], object: V, /) -> None: ...
def insert[V: Any](given_list: list[V] | _list[V], index: _float, object: V, /) -> None: ...
def len[K: Hashable, V: Any](object: string | dict[K, V] | _dict[K, V] | list[V] | _list[V] | set[K] | _set[K] | tuple[V] | range_class, /) -> _int: ...
@overload
def pop[K: Hashable, V: Any](collection: dict[K, V] | _dict[K, V], key: K, /) -> V: ...
@overload
def pop[V: Any](collection: list[V] | _list[V], index: _float = -1, /) -> V: ...
def remove[K: Hashable, V: Any](collection: list[V] | _list[V] | set[K] | _set[K], object: V, /) -> None: ...
def str(object: Any, /) -> string: ...

class Direction: ...
North: Direction
East: Direction
South: Direction
West: Direction

class Entity: ...
class Entities(_Enum):
    Apple: Entity
    Bamboo: Entity
    Bush: Entity
    Cactus: Entity
    Carrot: Entity
    Dead_Pumpkin: Entity
    Dinosaur: Entity
    Dynamite: Entity
    Grass: Entity
    Hedge: Entity
    Pumpkin: Entity
    Rice: Entity
    Sunflower: Entity
    Treasure: Entity
    Tree: Entity
    Underground_Treasure: Entity

class Ground: ...
class Grounds(_Enum):
    Basalt: Ground
    Bedrock: Ground
    Blue_Block: Ground
    Clay: Ground
    Coal: Ground
    Dirt: Ground
    Dry_Rice_Terrace: Ground
    Dynamite: Ground
    Grassland: Ground
    Green_Block: Ground
    Iron: Ground
    Limestone: Ground
    Loam: Ground
    Mushroom: Ground
    Perlite: Ground
    Petrified_Pumpkin: Ground
    Quartz: Ground
    Red_Block: Ground
    Rice_Terrace: Ground
    Rock: Ground
    Sand: Ground
    Soil: Ground
    Soot: Ground
    Treasure_Goal: Ground
    Treasure_Map: Ground
    Treasure_Path: Ground

class Hat: ...
class Hats(_Enum):
    Brown_Hat: Hat
    Cactus_Hat: Hat
    Carrot_Hat: Hat
    Dinosaur_Hat: Hat
    Dynamite_Hat: Hat
    Gold_Hat: Hat
    Gold_Trophy_Hat: Hat
    Golden_Cactus_Hat: Hat
    Golden_Carrot_Hat: Hat
    Golden_Gold_Hat: Hat
    Golden_Pumpkin_Hat: Hat
    Golden_Sunflower_Hat: Hat
    Golden_Tree_Hat: Hat
    Gray_Hat: Hat
    Green_Hat: Hat
    Mining_Hat: Hat
    Pumpkin_Hat: Hat
    Purple_Hat: Hat
    Silver_Trophy_Hat: Hat
    Straw_Hat: Hat
    Sunflower_Hat: Hat
    The_Farmers_Remains: Hat
    Top_Hat: Hat
    Traffic_Cone: Hat
    Traffic_Cone_Stack: Hat
    Tree_Hat: Hat
    Wizard_Hat: Hat
    Wood_Trophy_Hat: Hat
    Bamboo_Hat: Hat
    Bucket: Hat
    Coal_Hat: Hat
    Explosive_Drill: Hat
    Mushroom_Hat: Hat
    Quartz_Hat: Hat
    Rice_Hat: Hat

class Item: ...
class Items(_Enum):
    Bamboo: Item
    Block: Item
    Bone: Item
    Cactus: Item
    Carrot: Item
    Coal: Item
    Dynamite: Item
    Fertilizer: Item
    Gold: Item
    Hay: Item
    Iron: Item
    Mushroom: Item
    Piggy: Item
    Power: Item
    Pumpkin: Item
    Quartz: Item
    Rice: Item
    Water: Item
    Weird_Substance: Item
    Wood: Item

class Leaderboard: ...
class Leaderboards(_Enum):
    Cactus: Leaderboard
    Cactus_Single: Leaderboard
    Carrots: Leaderboard
    Carrots_Single: Leaderboard
    Dinosaur: Leaderboard
    Fastest_Reset: Leaderboard
    Hay: Leaderboard
    Hay_Single: Leaderboard
    Maze: Leaderboard
    Maze_Single: Leaderboard
    Pumpkins: Leaderboard
    Pumpkins_Single: Leaderboard
    Sunflowers: Leaderboard
    Sunflowers_Single: Leaderboard
    Wood: Leaderboard
    Wood_Single: Leaderboard
    Bamboo: Leaderboard
    Bamboo_Single: Leaderboard
    Dynamite: Leaderboard
    Dynamite_Single: Leaderboard
    Fastest_Underground_Reset: Leaderboard
    Mushrooms: Leaderboard
    Mushrooms_Single: Leaderboard
    Ores: Leaderboard
    Ores_Single: Leaderboard
    Pyramids: Leaderboard
    Pyramids_Single: Leaderboard
    Rice: Leaderboard
    Rice_Single: Leaderboard
    Treasure_Map: Leaderboard

class Unlock: ...
class Unlocks(_Enum):
    Auto_Unlock: Unlock
    Bamboo: Unlock
    Cactus: Unlock
    Carrots: Unlock
    Coal: Unlock
    Costs: Unlock
    Debug: Unlock
    Debug_2: Unlock
    Debug_Place: Unlock
    Dictionaries: Unlock
    Dinosaurs: Unlock
    Dynamite: Unlock
    Expand: Unlock
    Fertilizer: Unlock
    Functions: Unlock
    Grass: Unlock
    Hats: Unlock
    Import: Unlock
    Iron: Unlock
    Jump: Unlock
    Leaderboard: Unlock
    Lists: Unlock
    Loops: Unlock
    Mazes: Unlock
    Megafarm: Unlock
    Mining: Unlock
    Mushrooms: Unlock
    Ore_Boost: Unlock
    Operators: Unlock
    Petrified_Pumpkins: Unlock
    Plant: Unlock
    Polyculture: Unlock
    Prospecting: Unlock
    Pumpkins: Unlock
    Pyramid: Unlock
    Quartz: Unlock
    Rice: Unlock
    Senses: Unlock
    Simulation: Unlock
    Special_Soils: Unlock
    Speed: Unlock
    Sunflowers: Unlock
    The_Farmers_Remains: Unlock
    Timing: Unlock
    Top_Hat: Unlock
    Treasure_Map: Unlock
    Trees: Unlock
    Underground_Senses: Unlock
    Utilities: Unlock
    Variables: Unlock
    Watering: Unlock
    Explosive_Drill: Unlock
    Underground_Leaderboard: Unlock

def harvest() -> _bool: ...
def can_harvest() -> _bool: ...
def plant(entity: Entity | Entities, /) -> _bool: ...
def swap(direction: Direction, /) -> _bool: ...
def till() -> None: ...
def use_item(item: Item | Items, n: _int = 1, /) -> _bool: ...
def place(ground: Ground | Grounds, /) -> _bool: ...
def clear() -> None: ...
def change_hat(hat: Hat | Hats, /) -> None: ...
def move(direction: Direction, /) -> _bool: ...
def can_move(direction: Direction, /) -> _bool: ...
def get_pos_x() -> _int: ...
def get_pos_y() -> _int: ...
def hover(height: _float, /) -> _bool: ...
def get_hover() -> _int: ...
def get_pos_z(direction: Direction | None = None, /) -> _int: ...
type WorldSizes = Literal[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
def get_world_size() -> WorldSizes: ...
def get_entity_type(direction: Direction | None = None, /) -> Entity: ...
def get_ground_type(direction: Direction | None = None, /) -> Ground: ...
def get_water() -> _float: ...
def num_items(item: Item | Items, /) -> _float: ...
type Companion = _tuple[Entity, _tuple[_int, _int]]
def get_companion() -> _tuple[Entity, _tuple[_int, _int]]: ...
type Measure = _int | _tuple[_int, _int] | string
def measure(direction: Direction | None = None, /) -> Measure: ...
def dig() -> _bool: ...
def get_hardness(direction: Direction | None = None, /) -> _float: ...
def get_stability(direction: Direction | None = None, /) -> _float: ...
def prospect_iron() -> Direction: ...
def prospect_quartz() -> _float: ...
def push(direction: Direction, /) -> _bool: ...
def can_push(direction: Direction, /) -> _bool: ...
def jump(unlock: Unlock | Unlocks, /) -> None: ...

class Drone[R: Any]: ...
def spawn_drone[*P, R: Any](task: Callable[[*P], R], /, *args: *P) -> Drone[R]: ...
def wait_for[R: Any](drone: Drone[R], /) -> R: ...
def has_finished[R: Any](drone: Drone[R], /) -> _bool: ...
def max_drones() -> _int: ...
def num_drones() -> _int: ...
def get_time() -> _float: ...
def get_tick_count() -> _int: ...
def set_execution_speed(speed: _float, /) -> None: ...
def set_world_size(size: WorldSizes, /) -> None: ...
type _SimulateUnlocksPair = _tuple[Unlock, _int]
type SimulateUnlocks = dict[Unlock, _int] | _dict[Unlock, _int] | list[_SimulateUnlocksPair] | _list[_SimulateUnlocksPair] | _tuple[_SimulateUnlocksPair, ...] | _tuple[Unlock, ...] | _list[Unlock] | Unlocks
type SimulateItems = dict[Item, _float] | _dict[Item, _float]
type SimulateGlobals = dict[string, AnyTFWR] | _dict[string, AnyTFWR]
def simulate(filename: string, sim_unlocks: SimulateUnlocks, sim_items: dict[Item, _float] | _dict[Item, _float], sim_globals: dict[string, AnyTFWR] | _dict[string, AnyTFWR], seed: _float, speedup: _float, /) -> _float: ...
type Cost = dict[Item, _int] | _dict[Item, _int]
def get_cost(thing: Entity | Entities | Unlock | Unlocks, level: _int = 0, /) -> dict[Item, _int] | _dict[Item, _int]: ...
def unlock(unlock: Unlock | Unlocks, /) -> _bool: ...
def num_unlocked(thing: Enums, /) -> _int: ...
def random() -> _float: ...

@overload
def min(sequence: range_class, /) -> _int: ...
@overload
def min(sequence: Iterable[_float], /) -> _float: ...
@overload
def min(sequence: Iterable[string], /) -> string: ...
@overload
def min(*args: range_class) -> range_class: ...
@overload
def min(*args: _float) -> _float: ...
@overload
def min(*args: Iterable[_float]) -> Iterable[_float]: ...
@overload
def min(*args: string) -> string: ...
@overload
def min(*args: Iterable[string]) -> Iterable[string]: ...
@overload
def max(sequence: range_class, /) -> _int: ...
@overload
def max(sequence: Iterable[_float], /) -> _float: ...
@overload
def max(sequence: Iterable[string], /) -> string: ...
@overload
def max(*args: range_class) -> range_class: ...
@overload
def max(*args: _float) -> _float: ...
@overload
def max(*args: Iterable[_float]) -> Iterable[_float]: ...
@overload
def max(*args: string) -> string: ...
@overload
def max(*args: Iterable[string]) -> Iterable[string]: ...
def abs(x: _float, /) -> _float: ...
def print(*something: Any) -> None: ...
def quick_print(*something: Any) -> None: ...
def do_a_flip() -> None: ...
def pet_the_piggy() -> None: ...
def leaderboard_run(leaderboard: Leaderboard, file_name: string, speedup: _float, /) -> None: ...
