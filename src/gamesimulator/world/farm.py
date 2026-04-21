from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common.dotnet_random import DotNetRandom
from ..common.helper import just_sha256_it
from .drone import DroneState
from .entities import (
    AppleView,
    BushView,
    CactusView,
    DinosaurTailView,
    GenericGrowableView,
    HedgeView,
    PumpkinView,
    SunflowerView,
    TreasureView,
    create_entity_view,
)
from .farm_object import FarmObjectView
from .grid import GridState
from ..common.duration import Duration
from ..common.helper import num_drones
from ..unlock_snapshot import (
    DEFAULT_UNLOCK_LEVELS,
    get_unlock_metadata,
    is_default_available_dependency,
    resolve_dependency_unlock,
)
from ..runtime.py_values import GridDirection
from ..runtime.execute_exception import ExecuteException
from ..common.resource_tables import COMPANION_ENTITIES, ENTITY_ALLOWED_GROUNDS, ENTITY_GROWTH_RANGES


_DIRECTION_INDEX = {
    GridDirection.NORTH: 0,
    GridDirection.EAST: 1,
    GridDirection.SOUTH: 2,
    GridDirection.WEST: 3,
}

WATER_DECAY_INTERVAL = Duration.from_seconds(0.1)
_GROWABLE_ON_RESTART_BASE_DRAWS = {
    "Grass": 2,
    "Bush": 2,
    "Tree": 2,
    "Carrot": 1,
    "Sunflower": 1,
    "Cactus": 2,
    "Pumpkin": 2,
    "Apple": 2,
}


@dataclass
class FarmState:
    global_bindings: dict[str, Any]
    unlock_levels: dict[Any, int] | None = None
    items: dict[Any, float] | None = None

    def __post_init__(self) -> None:
        self.unlock_levels = dict(self.unlock_levels or {})
        self.items = dict(self.items or {})
        self.random = DotNetRandom(0)
        self.sim = None
        self._resource_timers_started = False
        self.items_bag = self.global_bindings.get("Items")
        self.entities_bag = self.global_bindings.get("Entities")
        self.grounds_bag = self.global_bindings.get("Grounds")
        self.unlocks_bag = self.global_bindings.get("Unlocks")
        self.hats_bag = self.global_bindings.get("Hats")
        self.unlock_levels = self._normalize_bag_mapping(self.unlock_levels, self.unlocks_bag)
        self.items = self._normalize_bag_mapping(self.items, self.items_bag)
        self.ground_grassland = self._bag_value(self.grounds_bag, "Grassland", "Grounds.Grassland")
        self.ground_soil = self._bag_value(self.grounds_bag, "Soil", "Grounds.Soil")
        self.entity_grass = self._bag_value(self.entities_bag, "Grass", "Entities.Grass")
        expand_unlock = self.unlock("Expand")
        self.grid = GridState(self.num_unlocked(expand_unlock), self.ground_grassland, self.ground_soil, self.entity_grass)
        self.drones = [DroneState(self, 0, 0)]
        self.main_drone_id = 0
        self.drone_generation = 0
        self.used_power = 0.0
        self.entity_allowed_grounds = {
            self.entity(name): grounds
            for name, grounds in ENTITY_ALLOWED_GROUNDS.items()
        }
        self.entity_growth_ranges = {
            self.entity(name): growth
            for name, growth in ENTITY_GROWTH_RANGES.items()
        }
        self.entities_with_companion = {self.entity(name) for name in COMPANION_ENTITIES}
        self._entity_view_cache: dict[tuple[int, int], tuple[Any, Any]] = {}
        self._entity_view_factories = {
            self.entity("Bush"): BushView,
            self.entity("Grass"): GenericGrowableView,
            self.entity("Tree"): GenericGrowableView,
            self.entity("Carrot"): GenericGrowableView,
            self.entity("Sunflower"): SunflowerView,
            self.entity("Cactus"): CactusView,
            self.entity("Pumpkin"): PumpkinView,
            self.entity("Apple"): AppleView,
            self.entity("Treasure"): TreasureView,
            self.entity("Hedge"): HedgeView,
            self.entity("Dinosaur"): DinosaurTailView,
            self.entity("Dead_Pumpkin"): FarmObjectView,
        }
        self._growable_entities = {
            self.entity("Grass"),
            self.entity("Bush"),
            self.entity("Tree"),
            self.entity("Carrot"),
            self.entity("Sunflower"),
            self.entity("Cactus"),
            self.entity("Pumpkin"),
            self.entity("Apple"),
        }
        self.refresh_entity_costs()

    def refresh_entity_costs(self) -> None:
        carrots_level = max(self.num_unlocked(self.unlock("Carrots")) - 1, 0)
        cactus_level = max(self.num_unlocked(self.unlock("Cactus")), 0)
        dinosaur_level = max(self.num_unlocked(self.unlock("Dinosaurs")) - 1, 0)
        self.entity_cost = {
            self.entity("Carrot"): {
                self.item("Hay"): 2 ** carrots_level,
                self.item("Wood"): 2 ** carrots_level,
            },
            self.entity("Cactus"): {
                self.item("Pumpkin"): max(1, 2 ** cactus_level),
            },
            self.entity("Sunflower"): {
                self.item("Carrot"): 1,
            },
            self.entity("Pumpkin"): {
                self.item("Carrot"): 2 ** max(self.num_unlocked(self.unlock("Pumpkins")) - 1, 0),
            },
            self.entity("Apple"): {
                self.item("Cactus"): 2 * max(1, 2 ** dinosaur_level),
            },
        }

    def seed_initial_grass_companions(self) -> None:
        if self.sim is None:
            return
        width, height = self.grid.world_size
        for x in range(width):
            for y in range(height):
                cell = self.grid.get_cell((x, y))
                if cell.entity == self.entity_grass and cell.companion is None:
                    self._assign_initial_companion((x, y), self.entity_grass)

    def restart_world_grass(self) -> None:
        if self.sim is None:
            return
        width, height = self.grid.world_size
        for x in range(width):
            for y in range(height):
                pos = (x, y)
                if self.grid.get_entity(pos) == self.entity_grass:
                    self.restart_entity(pos, self.entity_grass)

    def restart_entity(self, pos: tuple[int, int], entity: Any) -> None:
        cell = self.grid.get_cell(pos)
        cell.clear_entity_state()
        cell.entity = entity
        self._entity_view_cache.pop(pos, None)
        if entity is None:
            return
        if entity in self._growable_entities:
            self._restart_growable_entity(pos, entity)
            return
        entity_name = self._bag_key_name(entity)
        if entity_name == "Dinosaur":
            cell.mature = True
            cell.can_move_to = False

    def _restart_growable_entity(self, pos: tuple[int, int], entity: Any) -> None:
        cell = self.grid.get_cell(pos)
        various_rng = self.random_source("various")
        entity_name = self._bag_key_name(entity) or ""
        # 对齐原版 FarmObject.OnRestart + Growable.OnRestart 在 randomFactor 前的
        # randomVarious 消费。当前 v07 growth probe 证据显示该消费并非所有作物都一致。
        for _ in range(_GROWABLE_ON_RESTART_BASE_DRAWS.get(entity_name, 2)):
            various_rng.randrange(4)
        if entity in self.entities_with_companion:
            self._assign_initial_companion(pos, entity)
        cell.age = 0.0
        cell.mature = False
        cell.growth_seconds = self.sample_growth_seconds(entity)
        if entity_name == "Sunflower":
            cell.petals = self.random_source("sunflower").randint(7, 15)
        elif entity_name == "Cactus":
            cell.variant = self.random_source("cactus").randrange(10)
        elif entity_name == "Pumpkin":
            cell.mysterious_number = float(just_sha256_it(self.random_source("pumpkin")))
        self.reschedule_grow_timer(pos)

    def growth_multiplier_at(self, pos: tuple[int, int]) -> float:
        obj = self.get_entity_object(pos)
        if hasattr(obj, "growth_multiplier"):
            return obj.growth_multiplier()
        return 1.0

    def reschedule_grow_timer(self, pos: tuple[int, int]) -> None:
        if self.sim is None or not self.grid.is_within_bounds(pos):
            return
        cell = self.grid.get_cell(pos)
        if cell.grow_timer is not None:
            cell.grow_timer.stopped = True
            cell.grow_timer = None
        if cell.entity not in self._growable_entities or cell.mature:
            return
        multiplier = self.growth_multiplier_at(pos)
        if multiplier <= 0.0:
            return
        remaining = max(0.0, cell.growth_seconds - cell.age)
        duration = Duration.from_seconds(remaining / multiplier)
        entity = cell.entity
        cell.grow_timer = self.sim.start_timer(
            lambda pos=pos, entity=entity: self._finish_grow_timer(pos, entity),
            duration,
        )

    def _finish_grow_timer(self, pos: tuple[int, int], entity: Any) -> None:
        if not self.grid.is_within_bounds(pos):
            return
        cell = self.grid.get_cell(pos)
        if cell.entity is not entity or cell.mature:
            return
        cell.grow_timer = None
        cell.age = cell.growth_seconds
        obj = self.get_entity_object(pos)
        if hasattr(obj, "on_fully_grown"):
            obj.on_fully_grown()
            return
        cell.mature = True

    def entity(self, name: str) -> Any:
        return self._bag_value(self.entities_bag, name, f"Entities.{name}")

    def item(self, name: str) -> Any:
        return self._bag_value(self.items_bag, name, f"Items.{name}")

    def unlock(self, name: str) -> Any:
        return self._bag_value(self.unlocks_bag, name, f"Unlocks.{name}")

    def hat(self, name: str) -> Any:
        return self._bag_value(self.hats_bag, name, f"Hats.{name}")

    def direction_index(self, direction: Any) -> int:
        if hasattr(direction, "direction"):
            direction = direction.direction
        return _DIRECTION_INDEX[direction]

    def random_source(self, kind: str):
        if self.sim is None:
            return self.random
        mapping = {
            "various": self.sim.random_various,
            "misc": self.sim.random_misc,
            "water_decay": self.sim.random_water_decay,
            "grow_time": self.sim.random_grow_time,
            "companion_type": self.sim.random_companion_type,
            "companion_offset": self.sim.random_companion_offset,
            "grass_respawn": self.sim.random_grass_respawn,
            "maze": self.sim.random_maze,
            "snake": self.sim.random_snake,
            "cactus": self.sim.random_cactus_variant,
            "sunflower": self.sim.random_sunflower_petals,
            "pumpkin": self.sim.random_pumpkin,
            "poly": self.sim.random_poly,
            "random": self.sim.random_random,
        }
        return mapping.get(kind, self.sim.random_various)

    def num_unlocked(self, unlock: Any) -> int:
        if unlock in self.unlock_levels:
            return self.unlock_levels[unlock]
        unlock_name = self._bag_key_name(unlock)
        if unlock_name is not None:
            for key, value in self.unlock_levels.items():
                key_name = self._bag_key_name(key)
                if key_name is not None and key_name.lower() == unlock_name.lower():
                    return value
        return 0

    def num_items(self, item: Any) -> float:
        if item in self.items:
            return float(self.items[item])
        item_name = self._bag_key_name(item)
        if item_name is not None:
            for key, value in self.items.items():
                key_name = self._bag_key_name(key)
                if key_name is not None and key_name.lower() == item_name.lower():
                    return float(value)
        return 0.0

    def get_unlock_of(self, name: str) -> tuple[str, int] | None:
        return resolve_dependency_unlock(name)

    def is_unlocked_name(self, name: str, required_level: int = 1) -> bool:
        if is_default_available_dependency(name):
            return True
        unlock = self.get_unlock_of(name)
        if unlock is None:
            return False
        unlock_name, unlock_level = unlock
        required = max(required_level, unlock_level)
        return self.num_unlocked(self.unlock(_to_const_name(unlock_name))) >= required

    def assert_unlocked(self, dependency: str, word_start: int = -1, word_end: int = -1) -> None:
        if is_default_available_dependency(dependency):
            return
        unlock = self.get_unlock_of(dependency)
        if unlock is None:
            raise ExecuteException("error_missing_unlock")
        unlock_name, required_level = unlock
        if self.num_unlocked(self.unlock(_to_const_name(unlock_name))) >= required_level:
            return
        raise ExecuteException(f"error_missing_x_unlock:{_to_const_name(unlock_name)}")

    def set_num_items(self, item: Any, value: float) -> None:
        self.items[item] = float(value)
        self._sync_speed_if_needed(item)

    def add_items(self, item: Any, amount: float) -> None:
        self.items[item] = self.num_items(item) + float(amount)
        self._sync_speed_if_needed(item)

    def consume_items(self, item: Any, amount: float) -> bool:
        current = self.num_items(item)
        if current < amount:
            return False
        self.items[item] = current - amount
        self._sync_speed_if_needed(item)
        return True

    def can_afford(self, cost: dict[Any, float]) -> bool:
        for item, amount in cost.items():
            if self.num_items(item) < amount:
                return False
        return True

    def pay_cost(self, cost: dict[Any, float]) -> bool:
        if not self.can_afford(cost):
            return False
        for item, amount in cost.items():
            self.consume_items(item, amount)
        return True

    def get_entity_cost(self, entity: Any) -> dict[Any, float]:
        return dict(self.entity_cost.get(entity, {}))

    def get_unlock_cost(self, unlock: Any, num_unlocked: int = -1) -> dict[Any, float] | None:
        unlock_name = self._bag_key_name(unlock)
        if unlock_name is None:
            return None
        metadata = get_unlock_metadata(unlock_name)
        if metadata is None:
            return None
        current = self.num_unlocked(unlock) if num_unlocked < 0 else int(num_unlocked)
        max_level = int(metadata["max_unlock_level"])
        if current >= max_level:
            return {}
        if current > 0 and metadata["multi_unlock_cost"]:
            costs = metadata["multi_unlock_cost"]
            if current <= len(costs):
                return self._materialize_cost(costs[current - 1])
            factor = float(metadata["multi_unlock_factor"]) ** (current - len(costs))
            return {
                item: round(amount * factor, 3)
                for item, amount in self._materialize_cost(costs[-1]).items()
            }
        return self._materialize_cost(metadata["unlock_cost"])

    def _normalize_bag_mapping(self, mapping: dict[Any, Any], bag: Any) -> dict[Any, Any]:
        if bag is None or not hasattr(bag, "evaluate"):
            return dict(mapping)
        normalized: dict[Any, Any] = {}
        for key, value in mapping.items():
            normalized[self._canonical_bag_key(bag, key)] = value
        return normalized

    def _canonical_bag_key(self, bag: Any, key: Any) -> Any:
        key_name = self._bag_key_name(key)
        if key_name is None:
            return key
        try:
            return bag.evaluate(key_name)
        except Exception:
            return key

    @staticmethod
    def _bag_key_name(key: Any) -> str | None:
        if isinstance(key, str):
            return key
        name = getattr(key, "name", None)
        if isinstance(name, str) and name:
            return name
        text = str(key)
        if not text:
            return None
        return text.split(".")[-1]

    def _materialize_cost(self, pairs) -> dict[Any, float]:
        return {self.item(name): float(amount) for name, amount in pairs}

    def entity_yield(self, entity: Any, cell=None) -> tuple[Any, float]:
        if entity == self.entity("Grass"):
            return self.item("Hay"), 2 ** max(self.num_unlocked(self.unlock("Grass")) - 1, 0)
        if entity == self.entity("Bush"):
            return self.item("Wood"), 2 ** max(self.num_unlocked(self.unlock("Trees")) - 1, 0)
        if entity == self.entity("Tree"):
            return self.item("Wood"), 5 * (2 ** max(self.num_unlocked(self.unlock("Trees")) - 1, 0))
        if entity == self.entity("Carrot"):
            return self.item("Carrot"), 2 ** max(self.num_unlocked(self.unlock("Carrots")) - 2, 0)
        if entity == self.entity("Sunflower"):
            petals = max(1, 0 if cell is None else (cell.petals or 0))
            return self.item("Power"), float(petals)
        if entity == self.entity("Cactus"):
            return self.item("Cactus"), 1.0
        if entity == self.entity("Pumpkin"):
            return self.item("Pumpkin"), 1.0
        if entity == self.entity("Treasure"):
            return self.item("Gold"), 1.0
        return None, 0.0

    def companion_multiplier(self) -> float:
        return float(5 << self.num_unlocked(self.unlock("Polyculture")))

    def adjacent_positions(self, pos: tuple[int, int], wrap: bool = False) -> list[tuple[int, int]]:
        candidates = [
            (pos[0], pos[1] + 1),
            (pos[0] + 1, pos[1]),
            (pos[0], pos[1] - 1),
            (pos[0] - 1, pos[1]),
        ]
        if wrap:
            return [self.grid.wrap(candidate) for candidate in candidates]
        return [candidate for candidate in candidates if self.grid.is_within_bounds(candidate)]

    def get_entity_object(self, pos: tuple[int, int]):
        if not self.grid.is_within_bounds(pos):
            return None
        cell = self.grid.get_cell(pos)
        entity = cell.entity
        if entity is None:
            return None
        cached = self._entity_view_cache.get(pos)
        if cached is not None and cached[0] is entity:
            return cached[1]
        view_factory = self._entity_view_factories.get(entity, FarmObjectView)
        view = view_factory(self, pos)
        self._entity_view_cache[pos] = (entity, view)
        return view

    def sunflower_bonus_multiplier(self, pos: tuple[int, int]) -> float:
        obj = self.get_entity_object(pos)
        if not isinstance(obj, SunflowerView):
            return 1.0
        width, height = self.grid.world_size
        count = 0
        max_petals = 0
        current_petals = max(1, obj.cell.petals or 0)
        sunflower = self.entity("Sunflower")
        for x in range(width):
            for y in range(height):
                cell = self.grid.get_cell((x, y))
                if cell.entity != sunflower:
                    continue
                count += 1
                max_petals = max(max_petals, max(1, cell.petals or 0))
        if count >= 10 and current_petals == max_petals:
            return 8.0
        return 1.0

    def is_sorted_cactus(self, pos: tuple[int, int]) -> bool:
        obj = self.get_entity_object(pos)
        if not isinstance(obj, CactusView) or not obj.harvestable:
            return False
        value = obj.measure()
        for neighbor_pos, compare in [
            ((pos[0], pos[1] + 1), lambda a, b: a >= b),
            ((pos[0] + 1, pos[1]), lambda a, b: a >= b),
            ((pos[0], pos[1] - 1), lambda a, b: a <= b),
            ((pos[0] - 1, pos[1]), lambda a, b: a <= b),
        ]:
            if not self.grid.is_within_bounds(neighbor_pos):
                continue
            neighbor_obj = self.get_entity_object(neighbor_pos)
            if not isinstance(neighbor_obj, CactusView) or not neighbor_obj.harvestable:
                continue
            if not compare(neighbor_obj.measure(), value):
                return False
        return True

    def cactus_cluster(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        obj = self.get_entity_object(pos)
        if not isinstance(obj, CactusView) or not obj.harvestable:
            return []
        if not self.is_sorted_cactus(pos):
            return [pos]
        visited = set()
        stack = [pos]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            if not self.is_sorted_cactus(current):
                continue
            visited.add(current)
            for neighbor_pos in self.adjacent_positions(current, wrap=False):
                neighbor_obj = self.get_entity_object(neighbor_pos)
                if isinstance(neighbor_obj, CactusView) and neighbor_obj.harvestable:
                    stack.append(neighbor_pos)
        return list(visited) if visited else [pos]

    def pumpkin_square_group(self, pos: tuple[int, int]) -> tuple[list[tuple[int, int]], int]:
        obj = self.get_entity_object(pos)
        if not isinstance(obj, PumpkinView) or not obj.harvestable:
            return ([], 0)
        width, height = self.grid.world_size
        pumpkin = self.entity("Pumpkin")
        best_group: list[tuple[int, int]] = []
        best_size = 0
        max_size = min(width, height)
        for size in range(1, max_size + 1):
            for start_x in range(pos[0] - size + 1, pos[0] + 1):
                for start_y in range(pos[1] - size + 1, pos[1] + 1):
                    if start_x < 0 or start_y < 0 or start_x + size > width or start_y + size > height:
                        continue
                    if not (start_x <= pos[0] < start_x + size and start_y <= pos[1] < start_y + size):
                        continue
                    group = []
                    ok = True
                    for x in range(start_x, start_x + size):
                        for y in range(start_y, start_y + size):
                            cell = self.grid.get_cell((x, y))
                            if cell.entity != pumpkin or not cell.mature:
                                ok = False
                                break
                            group.append((x, y))
                        if not ok:
                            break
                    if ok and size > best_size:
                        best_size = size
                        best_group = group
        return (best_group, best_size)

    def sample_growth_seconds(self, entity: Any) -> float:
        lower, upper = self.entity_growth_ranges.get(entity, (0.0, 0.0))
        # 对齐原版 Growable.OnRestart -> randomFactor，成长随机走 randomVarious 域。
        rng = self.random_source("various")
        factor = rng.random()
        if lower == upper:
            return lower
        return lower + (upper - lower) * factor

    def clear_entity_at(self, pos: tuple[int, int], regrow_grass: bool = True) -> None:
        cell = self.grid.get_cell(pos)
        ground = cell.ground
        cell.clear_entity_state()
        self._entity_view_cache.pop(pos, None)
        if regrow_grass and ground == self.ground_grassland:
            self._respawn_grass_after_harvest(pos, cell)

    # 对齐原版 GridManager.RemoveEntity(..., regrowGrass=True) -> SetEntity("grass") -> OnRestart()。
    def _respawn_grass_after_harvest(self, pos: tuple[int, int], cell) -> None:
        self.restart_entity(pos, self.entity_grass)

    def _assign_initial_companion(self, pos: tuple[int, int], entity: Any) -> None:
        if entity not in self.entities_with_companion:
            return
        cell = self.grid.get_cell(pos)
        entity_name = str(entity).split(".")[-1]
        cell.companion = self._sample_companion(pos, entity_name)

    # 对齐原版 Growable.ChooseCompanion():
    # 1. companion 位置和 companion 类型共用同一条 randomPoly 随机流
    # 2. 先抽位置，再抽类型
    # 3. 类型包含自身候选，但若与自身实体相同则继续重抽
    def _sample_companion(self, pos: tuple[int, int], entity_name: str) -> tuple[Any, tuple[int, int]]:
        rng = self.random_source("poly")
        while True:
            dx = rng.randint(-3, 3)
            dy = rng.randint(-3, 3)
            target_pos = self.grid.wrap((pos[0] + dx, pos[1] + dy))
            if self.grid.world_size[1] != 1 and (target_pos == pos or abs(dx) + abs(dy) > 3):
                continue
            break
        index_to_name = {
            0: "Grass",
            1: "Bush",
            2: "Carrot",
            3: "Tree",
        }
        while True:
            companion_entity = self.entity(index_to_name[rng.randrange(4)])
            if str(companion_entity).split(".")[-1] != entity_name:
                return (companion_entity, target_pos)

    def advance_passive_world(self, start_time: Duration, target_time: Duration, rng) -> None:
        if target_time <= start_time:
            return
        current_time = start_time
        while current_time < target_time:
            next_decay_time = self.grid.next_water_decay_time
            if next_decay_time <= current_time:
                self.grid.decay_water(rng)
                self.grid.next_water_decay_time = next_decay_time + WATER_DECAY_INTERVAL
                continue
            segment_end = Duration.min(target_time, next_decay_time)
            segment_seconds = (segment_end - current_time).seconds
            if segment_seconds > 0.0:
                self._passive_update_segment(segment_seconds)
                current_time = segment_end
            if current_time >= self.grid.next_water_decay_time:
                self.grid.decay_water(rng)
                self.grid.next_water_decay_time = self.grid.next_water_decay_time + WATER_DECAY_INTERVAL

    def passive_update(self, seconds: float, rng) -> None:
        start_time = self.sim.current_time if self.sim is not None else Duration(0)
        self.advance_passive_world(start_time, start_time + Duration.from_seconds(seconds), rng)

    def _passive_update_segment(self, seconds: float) -> None:
        width, height = self.grid.world_size
        for x in range(width):
            for y in range(height):
                cell = self.grid.get_cell((x, y))
                if cell.entity is None:
                    if cell.ground == self.ground_grassland:
                        cell.natural_grass_age += seconds
                        if cell.natural_grass_age >= ENTITY_GROWTH_RANGES["Grass"][0]:
                            cell.entity = self.entity_grass
                            cell.mature = True
                            cell.age = 0.5
                            cell.growth_seconds = 0.5
                    continue
                if cell.mature or cell.entity not in self._growable_entities:
                    continue
                obj = self.get_entity_object((x, y))
                if obj is None:
                    continue
                obj.advance_growth(seconds)

    def max_speed_factor(self) -> float:
        speed_level = self.num_unlocked(self.unlock("Speed")) if self.unlocks_bag is not None else 0
        factor = 1.5 ** speed_level
        power_item = self.item("Power") if self.items_bag is not None else None
        if power_item is not None and self.num_items(power_item) > 0.0:
            factor *= 2.0
        return factor

    def max_drones(self) -> int:
        if self.sim is not None and getattr(self.sim, "single_drone", False):
            return 1
        if self.unlocks_bag is None:
            return 1
        return num_drones(self.num_unlocked(self.unlock("Megafarm")))

    def unlock_or_upgrade(self, unlock: Any) -> bool:
        unlock_name = self._bag_key_name(unlock)
        if unlock_name is None:
            return False
        if self.sim is not None and getattr(self.sim, "single_drone", False) and unlock_name in ("Megafarm", "Expand"):
            return False
        current = self.num_unlocked(unlock)
        max_level = int(DEFAULT_UNLOCK_LEVELS.get(unlock_name, max(current, 1)))
        if current >= max_level:
            return False
        self.unlock_levels[unlock] = current + 1
        self.refresh_entity_costs()
        if unlock_name == "Expand":
            self.grid.reset_for_expand(self.num_unlocked(unlock))
            self.restart_world_grass()
        elif unlock_name == "Speed" and self.sim is not None:
            self.sim.change_execution_speed(self.max_speed_factor())
        return True

    def add_drone(self, parent_id: int) -> int:
        self.drone_generation += 1
        for index, drone in enumerate(self.drones):
            if drone is None:
                parent = self.drones[parent_id]
                self.drones[index] = DroneState(self, parent.x, parent.y)
                return index
        if len(self.drones) >= self.max_drones():
            raise RuntimeError("error_max_drones_reached")
        parent = self.drones[parent_id]
        self.drones.append(DroneState(self, parent.x, parent.y))
        return len(self.drones) - 1

    def remove_drone(self, drone_id: int) -> None:
        if 0 <= drone_id < len(self.drones) and drone_id != self.main_drone_id:
            self.drones[drone_id] = None

    def _sync_speed_if_needed(self, item: Any) -> None:
        if self.sim is None or item != self.item("Power"):
            return
        self.sim.change_execution_speed(self.max_speed_factor())

    def start_runtime_timers(self) -> None:
        if self.sim is None or self._resource_timers_started:
            return
        self._resource_timers_started = True
        self._schedule_use_power()
        self._schedule_receive_water()
        self._schedule_receive_fertilizer()

    def _schedule_use_power(self) -> None:
        if self.sim is None:
            return
        self.sim.start_timer(self._use_power, Duration.from_seconds(0.2))

    def _schedule_receive_water(self) -> None:
        if self.sim is None:
            return
        level = self.num_unlocked(self.unlock("Watering"))
        interval = 20.0 / float(1 << level)
        self.sim.start_timer(self._receive_water, Duration.from_seconds(interval))

    def _schedule_receive_fertilizer(self) -> None:
        if self.sim is None:
            return
        level = self.num_unlocked(self.unlock("Fertilizer"))
        interval = 20.0 / float(1 << level)
        self.sim.start_timer(self._receive_fertilizer, Duration.from_seconds(interval))

    # 对齐原版 Farm.ReceiveWater/ReceiveFertilizer：按当前解锁等级周期补给，并在每次触发后重排下一次。
    def _use_power(self) -> None:
        power_item = self.item("Power")
        if self.num_items(power_item) > 0.0 and not self.consume_items(power_item, self.used_power):
            self.set_num_items(power_item, 0.0)
        self.used_power = 0.0
        self._schedule_use_power()

    def _receive_water(self) -> None:
        if self.num_unlocked(self.unlock("Watering")) > 0:
            self.add_items(self.item("Water"), 1.0)
        self._schedule_receive_water()

    def _receive_fertilizer(self) -> None:
        if self.num_unlocked(self.unlock("Fertilizer")) > 0:
            self.add_items(self.item("Fertilizer"), 1.0)
        self._schedule_receive_fertilizer()

    @staticmethod
    def _bag_value(bag: Any, name: str, fallback: Any) -> Any:
        if bag is None:
            return fallback
        try:
            return bag.evaluate(name)
        except Exception:
            return fallback


def _to_const_name(asset_name: str) -> str:
    return "_".join(part.capitalize() for part in asset_name.split("_"))
