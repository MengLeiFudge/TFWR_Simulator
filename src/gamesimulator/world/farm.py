from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from .drone import DroneState
from .entities import CactusView, PumpkinView, SunflowerView, TreasureView, create_entity_view
from .grid import GridState
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


@dataclass
class FarmState:
    global_bindings: dict[str, Any]
    unlock_levels: dict[Any, int] | None = None
    items: dict[Any, float] | None = None

    def __post_init__(self) -> None:
        self.unlock_levels = dict(self.unlock_levels or {})
        self.items = dict(self.items or {})
        self.random = random.Random(0)
        self.sim = None
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
            self.entity("Apple"): {
                self.item("Cactus"): max(1, 2 ** dinosaur_level),
            },
        }

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
            "maze": self.sim.random_maze,
            "snake": self.sim.random_snake,
            "cactus": self.sim.random_cactus,
            "sunflower": self.sim.random_sunflower,
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
        return create_entity_view(self, pos)

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
        if lower == upper:
            return lower
        name = str(entity).split(".")[-1]
        kind = {
            "Cactus": "cactus",
            "Sunflower": "sunflower",
            "Pumpkin": "pumpkin",
        }.get(name, "various")
        rng = self.random_source(kind)
        return lower + (upper - lower) * rng.random()

    def clear_entity_at(self, pos: tuple[int, int], regrow_grass: bool = True) -> None:
        cell = self.grid.get_cell(pos)
        ground = cell.ground
        cell.clear_entity_state()
        if regrow_grass and ground == self.ground_grassland:
            cell.entity = self.entity_grass
            cell.mature = True
            cell.age = 0.5
            cell.growth_seconds = 0.5

    def passive_update(self, seconds: float, rng) -> None:
        width, height = self.grid.world_size
        trials = int(seconds / 0.1)
        if rng.random() < ((seconds - trials * 0.1) / 0.1 if seconds > 0 else 0.0):
            trials += 1
        for x in range(width):
            for y in range(height):
                cell = self.grid.get_cell((x, y))
                if cell.water > 0.0:
                    for _ in range(trials):
                        if rng.random() < 0.1:
                            cell.water = max(0.0, min(1.0, cell.water * 0.99))
                if cell.entity is None:
                    if cell.ground == self.ground_grassland:
                        cell.natural_grass_age += seconds
                        if cell.natural_grass_age >= ENTITY_GROWTH_RANGES["Grass"][0]:
                            cell.entity = self.entity_grass
                            cell.mature = True
                            cell.age = 0.5
                            cell.growth_seconds = 0.5
                    continue
                obj = self.get_entity_object((x, y))
                if obj is None:
                    continue
                if hasattr(obj, "advance_growth") and not obj.harvestable:
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
        if unlock_name == "Expand":
            self.grid.reset_for_expand(self.num_unlocked(unlock))
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
