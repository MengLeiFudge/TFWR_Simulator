from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entities import AppleView, GrowableView, HedgeView, TreasureView
from ..runtime.py_values import GridDirection


_DIR_TO_DELTA = {
    GridDirection.NORTH: (0, 1),
    GridDirection.EAST: (1, 0),
    GridDirection.SOUTH: (0, -1),
    GridDirection.WEST: (-1, 0),
}


@dataclass
class DroneState:
    farm: Any
    x: int = 0
    y: int = 0
    prevent_wrapping: bool = False
    current_hat: Any = None
    dino_tail: list[tuple[int, int]] = field(default_factory=list)
    apple_target: tuple[int, int] | None = None
    dino_move_ticks: int = 400

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    def move(self, direction: Any) -> tuple[bool, float]:
        if not self.can_move(direction):
            return False, 1.0
        dx, dy = _DIR_TO_DELTA[_unwrap_direction(direction)]
        raw = (self.x + dx, self.y + dy)
        wrapped = self.farm.grid.wrap(raw)
        old_pos = self.pos
        self.x, self.y = wrapped
        ops = 200.0
        if self._is_dinosaur_hat():
            ops = float(self.dino_move_ticks)
            self._after_dinosaur_move(old_pos)
        return True, ops

    def _after_dinosaur_move(self, old_pos: tuple[int, int]) -> None:
        current_obj = self.farm.get_entity_object(old_pos)
        ate_apple = isinstance(current_obj, AppleView)
        if ate_apple:
            self.farm.clear_entity_at(old_pos, regrow_grass=False)
        if ate_apple or self.dino_tail:
            self._spawn_tail_segment(old_pos)
            if not ate_apple and self.dino_tail:
                tail = self.dino_tail.pop()
                self.farm.clear_entity_at(tail, regrow_grass=False)
        if ate_apple:
            self.dino_move_ticks -= int(self.dino_move_ticks * 0.03)
            self._spawn_dinosaur_apple(force_under_drone=False)
        self._refresh_tail_passability()

    def _spawn_tail_segment(self, pos: tuple[int, int]) -> None:
        cell = self.farm.grid.get_cell(pos)
        cell.clear_entity_state()
        cell.entity = self.farm.entity("Dinosaur")
        cell.mature = True
        cell.tail_owner_id = id(self)
        cell.can_move_to = False
        self.dino_tail.insert(0, pos)

    def _refresh_tail_passability(self) -> None:
        for pos in self.dino_tail:
            self.farm.grid.get_cell(pos).can_move_to = False
        if len(self.dino_tail) > 1:
            self.farm.grid.get_cell(self.dino_tail[-1]).can_move_to = True

    def _spawn_dinosaur_apple(self, force_under_drone: bool) -> bool:
        if not self._is_dinosaur_hat():
            self.apple_target = None
            return False
        cost = self.farm.get_entity_cost(self.farm.entity("Apple"))
        if cost and not self.farm.pay_cost(cost):
            self.apple_target = None
            return False
        spawn_pos = self.pos
        rng = self.farm.random_source("snake")
        if not force_under_drone:
            candidates = []
            width, height = self.farm.grid.world_size
            for x in range(width):
                for y in range(height):
                    obj = self.farm.get_entity_object((x, y))
                    if obj is None or obj.entity_name not in {"Dinosaur", "Apple"}:
                        candidates.append((x, y))
            if not candidates:
                self.apple_target = None
                return False
            spawn_pos = candidates[rng.randrange(len(candidates))]
        self.apple_target = self._choose_next_apple_target(exclude=spawn_pos)
        cell = self.farm.grid.get_cell(spawn_pos)
        if cell.entity not in (None, self.farm.entity("Grass"), self.farm.entity("Apple")):
            return False
        cell.clear_entity_state()
        cell.entity = self.farm.entity("Apple")
        cell.mature = True
        cell.apple_next_pos = self.apple_target
        return True

    def _choose_next_apple_target(self, exclude: tuple[int, int]) -> tuple[int, int] | None:
        width, height = self.farm.grid.world_size
        if height <= 1:
            return None
        rng = self.farm.random_source("snake")
        candidates = []
        for x in range(width):
            for y in range(height):
                if (x, y) == exclude:
                    continue
                obj = self.farm.get_entity_object((x, y))
                if obj is None or obj.entity_name not in {"Dinosaur", "Apple"}:
                    candidates.append((x, y))
        if not candidates:
            return None
        return candidates[rng.randrange(len(candidates))]

    def _clear_dinosaur_state(self) -> None:
        for pos in list(self.dino_tail):
            self.farm.clear_entity_at(pos, regrow_grass=False)
        self.dino_tail = []
        self.dino_move_ticks = 400
        self.apple_target = None
        width, height = self.farm.grid.world_size
        for x in range(width):
            for y in range(height):
                if self.farm.grid.get_entity((x, y)) == self.farm.entity("Apple"):
                    self.farm.clear_entity_at((x, y), regrow_grass=False)

    def _is_dinosaur_hat(self) -> bool:
        return str(self.current_hat).split(".")[-1] == "Dinosaur_Hat"

    def can_move(self, direction: Any) -> bool:
        dx, dy = _DIR_TO_DELTA[_unwrap_direction(direction)]
        raw = (self.x + dx, self.y + dy)
        wrapped = self.farm.grid.wrap(raw)
        if self.prevent_wrapping and raw != wrapped:
            return False
        dest_obj = self.farm.get_entity_object(wrapped)
        current_obj = self.farm.get_entity_object(self.pos)
        if dest_obj is not None and not dest_obj.can_move_to_from(direction):
            return False
        if current_obj is not None and not current_obj.can_move_away_to(direction):
            return False
        return True

    def get_ground_type(self) -> Any:
        return self.farm.grid.get_ground(self.pos)

    def get_entity_type(self) -> Any:
        return self.farm.grid.get_entity(self.pos)

    def till(self) -> None:
        if self.get_ground_type() == self.farm.ground_grassland:
            self.farm.grid.set_ground(self.pos, self.farm.ground_soil)
            if not isinstance(self.farm.get_entity_object(self.pos), HedgeView):
                self.farm.grid.set_entity(self.pos, None)
        else:
            self.farm.grid.set_ground(self.pos, self.farm.ground_grassland)
            if not isinstance(self.farm.get_entity_object(self.pos), HedgeView):
                self.farm.grid.set_entity(self.pos, self.farm.entity_grass)
                cell = self.farm.grid.get_cell(self.pos)
                cell.mature = True
                cell.age = 0.5
                cell.growth_seconds = 0.5

    def get_water(self) -> float:
        return self.farm.grid.get_water_volume(self.pos)

    def can_harvest(self) -> bool:
        obj = self.farm.get_entity_object(self.pos)
        return bool(obj is not None and obj.harvestable and obj.entity_name != "Dead_Pumpkin")

    def harvest(self) -> bool:
        obj = self.farm.get_entity_object(self.pos)
        if obj is None or obj.entity_name == "Dead_Pumpkin":
            return False
        return obj.harvest(self)

    def plant(self, entity: Any) -> bool:
        allowed = self.farm.entity_allowed_grounds.get(entity, set())
        if allowed and str(self.get_ground_type()) not in allowed:
            return False
        current = self.farm.get_entity_object(self.pos)
        if current is not None and current.entity_name not in {"Grass", "Dead_Pumpkin", "Apple"}:
            return False
        cost = self.farm.get_entity_cost(entity)
        if cost and not self.farm.pay_cost(cost):
            return False
        cell = self.farm.grid.get_cell(self.pos)
        cell.clear_entity_state()
        cell.entity = entity
        cell.age = 0.0
        cell.mature = False
        cell.growth_seconds = self.farm.sample_growth_seconds(entity)
        if entity in self.farm.entities_with_companion:
            self.farm._assign_initial_companion(self.pos, entity)
        if str(entity).split(".")[-1] == "Sunflower":
            cell.petals = self.farm.random_source("sunflower").randint(7, 15)
        if str(entity).split(".")[-1] == "Cactus":
            cell.variant = self.farm.random_source("cactus").randrange(10)
        return True

    def water(self, amount: int) -> bool:
        water_item = self.farm.item("Water")
        if not self.farm.consume_items(water_item, amount):
            return False
        self.farm.grid.set_water_volume(self.pos, self.get_water() + 0.25 * amount)
        return True

    def fertilize(self, amount: int) -> bool:
        fertilizer_item = self.farm.item("Fertilizer")
        if not self.farm.consume_items(fertilizer_item, amount):
            return False
        obj = self.farm.get_entity_object(self.pos)
        if not isinstance(obj, GrowableView):
            return False
        return obj.fertilize(amount)

    def get_companion(self):
        obj = self.farm.get_entity_object(self.pos)
        if not isinstance(obj, GrowableView):
            return None
        return obj.get_companion()

    def measure(self, direction: Any = None):
        pos = self.pos
        if direction is not None:
            dx, dy = _DIR_TO_DELTA[_unwrap_direction(direction)]
            pos = self.farm.grid.wrap((self.x + dx, self.y + dy))
        obj = self.farm.get_entity_object(pos)
        if obj is None:
            return None
        return obj.measure()

    def change_hat(self, hat: Any) -> None:
        old_hat = self.current_hat
        if str(old_hat).split(".")[-1] == "Dinosaur_Hat" and str(hat).split(".")[-1] != "Dinosaur_Hat":
            bonus = float((len(self.dino_tail) ** 2) * max(1, 2 ** max(self.farm.num_unlocked(self.farm.unlock("Dinosaurs")) - 1, 0)))
            if bonus > 0.0:
                self.farm.add_items(self.farm.item("Bone"), bonus)
            self._clear_dinosaur_state()
        self.current_hat = hat
        self.prevent_wrapping = str(hat).split(".")[-1] == "Dinosaur_Hat"
        if self.prevent_wrapping:
            self._spawn_dinosaur_apple(force_under_drone=True)

    def swap(self, direction: Any) -> bool:
        dx, dy = _DIR_TO_DELTA[_unwrap_direction(direction)]
        other = (self.x + dx, self.y + dy)
        if not self.farm.grid.is_within_bounds(other):
            return False
        return self.farm.grid.swap_cells(self.pos, other)

    def apply_weird_substance(self, amount: int) -> tuple[bool, bool]:
        obj = self.farm.get_entity_object(self.pos)
        if obj is None:
            return False, False
        mazes_level = max(self.farm.num_unlocked(self.farm.unlock("Mazes")) - 1, 0)
        divisor = 1 << mazes_level
        if obj.entity_name == "Bush" and self.farm.num_unlocked(self.farm.unlock("Mazes")) > 0:
            desired_size = amount // divisor
            if desired_size < 1:
                obj.toggle_weird()
                return False, False
            return obj.generate_maze(desired_size), True
        if isinstance(obj, TreasureView) and self.farm.num_unlocked(self.farm.unlock("Mazes")) > 0:
            desired_size = amount // divisor
            if desired_size < 1:
                return False, False
            return obj.reposition_treasure(desired_size)
        if isinstance(obj, GrowableView):
            obj.toggle_weird()
            return True, True
        return False, False


def _unwrap_direction(direction: Any) -> GridDirection:
    if hasattr(direction, "direction"):
        return direction.direction
    return direction
