from __future__ import annotations

import math
from typing import Any

from .farm_object import FarmObjectView
from .growable import GrowableView


class GenericGrowableView(GrowableView):
    def harvest(self, drone) -> bool:
        return self.generic_harvest()


class BushView(GenericGrowableView):
    def generate_maze(self, desired_size: int) -> bool:
        size = min(desired_size, self.farm.grid.world_size[0], self.farm.grid.world_size[1])
        if size <= 0:
            return False
        low_x = max(0, min(self.pos[0] - size // 2, self.farm.grid.world_size[0] - size))
        low_y = max(0, min(self.pos[1] - size // 2, self.farm.grid.world_size[1] - size))
        rng = self.farm.random_source("maze")
        treasure_pos = (low_x + rng.randrange(size), low_y + rng.randrange(size))
        for x in range(low_x, low_x + size):
            for y in range(low_y, low_y + size):
                cell = self.farm.grid.get_cell((x, y))
                cell.clear_entity_state()
                cell.entity = self.farm.entity("Treasure") if (x, y) == treasure_pos else self.farm.entity("Hedge")
                cell.mature = True
                cell.maze_size = size
                cell.maze_low_left = (low_x, low_y)
                cell.maze_walls = [False, False, False, False]
                cell.treasure_factor = 1
        treasure_cell = self.farm.grid.get_cell(treasure_pos)
        treasure_cell.treasure_next_pos = treasure_pos
        return True


class SunflowerView(GrowableView):
    def measure(self):
        if self.cell.petals <= 0:
            self.cell.petals = self.farm.random_source("sunflower").randint(7, 15)
        return self.cell.petals

    def harvest(self, drone) -> bool:
        petals = max(1, self.measure())
        count = 0
        max_petals = 0
        width, height = self.farm.grid.world_size
        sunflower = self.farm.entity("Sunflower")
        for x in range(width):
            for y in range(height):
                cell = self.farm.grid.get_cell((x, y))
                if cell.entity != sunflower:
                    continue
                count += 1
                max_petals = max(max_petals, max(1, cell.petals or 0))
        get_boost = count >= 10 and petals == max_petals
        if self.farm.grid.had_incorrect_sunflower_harvest:
            get_boost = False
        self.farm.grid.had_incorrect_sunflower_harvest = not get_boost
        amount = float(petals * (8 if get_boost else 1))
        amount, weird_amount = self.apply_weird_split(amount)
        if amount > 0.0:
            self.farm.add_items(self.farm.item("Power"), amount)
        if weird_amount > 0.0:
            self.farm.add_items(self.farm.item("Weird_Substance"), weird_amount)
        self.clear_after_harvest()
        return True


class CactusView(GrowableView):
    def _ensure_variant(self) -> int:
        if self.cell.variant is None or self.cell.variant < 0:
            self.cell.variant = self.farm.random_source("cactus").randrange(10)
        return self.cell.variant

    def measure(self):
        return self._ensure_variant()

    def harvest(self, drone) -> bool:
        cluster = self.farm.cactus_cluster(self.pos)
        if not cluster:
            cluster = [self.pos]
        num_weird = 0
        for pos in cluster:
            if self.farm.grid.get_cell(pos).weird:
                num_weird += 1
        total = float(len(cluster) * len(cluster))
        weird_amount = float(math.floor(0.5 * num_weird * len(cluster)))
        cactus_amount = total - weird_amount
        if cactus_amount > 0.0:
            self.farm.add_items(self.farm.item("Cactus"), cactus_amount)
        if weird_amount > 0.0:
            self.farm.add_items(self.farm.item("Weird_Substance"), weird_amount)
        for pos in cluster:
            self.farm.clear_entity_at(pos)
        return True


class PumpkinView(GrowableView):
    def on_fully_grown(self) -> None:
        if self.farm.random_source("pumpkin").random() <= 0.2:
            cell = self.cell
            cell.clear_entity_state()
            cell.entity = self.farm.entity("Dead_Pumpkin")
            return
        self.cell.mature = True
        self._assign_group_number()

    def _assign_group_number(self) -> float:
        group, _ = self.farm.pumpkin_square_group(self.pos)
        if not group:
            group = [self.pos]
        number = None
        for pos in group:
            existing = self.farm.grid.get_cell(pos).mysterious_number
            if existing is not None:
                number = existing
                break
        if number is None:
            number = float(self.farm.random_source("pumpkin").randrange(1, 2**31))
        for pos in group:
            self.farm.grid.get_cell(pos).mysterious_number = number
        return number

    def measure(self):
        if self.cell.mysterious_number is None:
            return self._assign_group_number()
        return self.cell.mysterious_number

    def harvest(self, drone) -> bool:
        group, size = self.farm.pumpkin_square_group(self.pos)
        if not group:
            group = [self.pos]
            size = 1
        num = float(min(size, 6))
        num_weird = 0
        for pos in group:
            if self.farm.grid.get_cell(pos).weird:
                num_weird += 1
        weird_amount = float(math.floor(num_weird * 0.5 * num))
        pumpkin_amount = float(size * size) * num - weird_amount
        if pumpkin_amount > 0.0:
            self.farm.add_items(self.farm.item("Pumpkin"), pumpkin_amount)
        if weird_amount > 0.0:
            self.farm.add_items(self.farm.item("Weird_Substance"), weird_amount)
        for pos in group:
            self.farm.clear_entity_at(pos)
        return True


class AppleView(GrowableView):
    @property
    def harvestable(self) -> bool:
        return False

    def measure(self):
        return self.cell.apple_next_pos

    def harvest(self, drone) -> bool:
        self.farm.clear_entity_at(self.pos)
        return True


class HedgeView(FarmObjectView):
    def _walls(self) -> list[bool]:
        return list(self.cell.maze_walls or [False, False, False, False])

    def can_move_to_from(self, direction: Any) -> bool:
        return not self._walls()[self.farm.direction_index(direction)]

    def can_move_away_to(self, direction: Any) -> bool:
        return not self._walls()[self.farm.direction_index(direction)]

    def measure(self):
        size = self.cell.maze_size
        low = self.cell.maze_low_left
        if not size or low is None:
            return None
        for x in range(low[0], low[0] + size):
            for y in range(low[1], low[1] + size):
                if self.farm.grid.get_entity((x, y)) == self.farm.entity("Treasure"):
                    return (x, y)
        return None

    def harvest(self, drone) -> bool:
        size = self.cell.maze_size
        low = self.cell.maze_low_left
        if not size or low is None:
            self.farm.clear_entity_at(self.pos)
            return True
        for x in range(low[0], low[0] + size):
            for y in range(low[1], low[1] + size):
                cell = self.farm.grid.get_cell((x, y))
                if cell.entity in (self.farm.entity("Hedge"), self.farm.entity("Treasure")):
                    self.farm.clear_entity_at((x, y))
        return True


class TreasureView(HedgeView):
    def measure(self):
        return self.pos

    def harvest(self, drone) -> bool:
        amount = float((self.cell.maze_size or 1) ** 2)
        if amount > 0.0:
            self.farm.add_items(self.farm.item("Gold"), amount)
        self.farm.clear_entity_at(self.pos)
        return True

    def reposition_treasure(self, desired_size: int) -> tuple[bool, bool]:
        size = self.cell.maze_size
        low = self.cell.maze_low_left
        if not size or low is None or size <= 1 or desired_size < size or self.cell.treasure_factor >= 301:
            return False, False
        rng = self.farm.random_source("maze")
        candidates = [
            (x, y)
            for x in range(low[0], low[0] + size)
            for y in range(low[1], low[1] + size)
            if (x, y) != self.pos
        ]
        if not candidates:
            return False, True
        next_pos = candidates[rng.randrange(len(candidates))]
        old_cell = self.cell
        old_walls = list(old_cell.maze_walls or [False, False, False, False])
        old_factor = old_cell.treasure_factor + 1
        self.farm.add_items(self.farm.item("Gold"), float(size * size))
        old_cell.clear_entity_state()
        old_cell.entity = self.farm.entity("Hedge")
        old_cell.mature = True
        old_cell.maze_size = size
        old_cell.maze_low_left = low
        old_cell.maze_walls = old_walls
        next_cell = self.farm.grid.get_cell(next_pos)
        next_walls = list(next_cell.maze_walls or [False, False, False, False])
        next_cell.clear_entity_state()
        next_cell.entity = self.farm.entity("Treasure")
        next_cell.mature = True
        next_cell.maze_size = size
        next_cell.maze_low_left = low
        next_cell.maze_walls = next_walls
        next_cell.treasure_factor = old_factor
        return True, True


class DinosaurTailView(FarmObjectView):
    def can_move_to_from(self, direction: Any) -> bool:
        return bool(self.cell.can_move_to)

    def harvest(self, drone) -> bool:
        self.farm.clear_entity_at(self.pos)
        return True


def create_entity_view(farm: Any, pos: tuple[int, int]):
    cell = farm.grid.get_cell(pos)
    name = "" if cell.entity is None else str(cell.entity).split(".")[-1]
    if name == "Bush":
        return BushView(farm, pos)
    if name in {"Grass", "Tree", "Carrot"}:
        return GenericGrowableView(farm, pos)
    if name == "Sunflower":
        return SunflowerView(farm, pos)
    if name == "Cactus":
        return CactusView(farm, pos)
    if name == "Pumpkin":
        return PumpkinView(farm, pos)
    if name == "Apple":
        return AppleView(farm, pos)
    if name == "Treasure":
        return TreasureView(farm, pos)
    if name == "Hedge":
        return HedgeView(farm, pos)
    if name == "Dinosaur":
        return DinosaurTailView(farm, pos)
    if name == "Dead_Pumpkin":
        return FarmObjectView(farm, pos)
    return FarmObjectView(farm, pos) if cell.entity is not None else None
