from __future__ import annotations

import math
from typing import Any

from .farm_object import FarmObjectView


class GrowableView(FarmObjectView):
    @property
    def harvestable(self) -> bool:
        return bool(self.cell.mature)

    def water_factor(self) -> float:
        if self.cell.ground in (self.farm.ground_grassland, self.farm.ground_soil):
            return 1.0 + self.cell.water * 4.0
        return 1.0

    def tree_factor(self) -> float:
        if self.entity_name != "Tree":
            return 1.0
        factor = 1.0
        tree = self.farm.entity("Tree")
        for neighbor_pos in self.farm.adjacent_positions(self.pos, wrap=False):
            neighbor = self.farm.grid.get_cell(neighbor_pos)
            if neighbor.entity == tree:
                factor *= 2.0
        return factor

    def growth_multiplier(self) -> float:
        return self.water_factor() / self.tree_factor()

    def advance_growth(self, seconds: float) -> None:
        if self.cell.mature or self.cell.entity is None:
            return
        self.cell.age += seconds * self.growth_multiplier()
        if self.cell.age >= self.cell.growth_seconds:
            self.cell.age = self.cell.growth_seconds
            self.on_fully_grown()

    def on_fully_grown(self) -> None:
        self.cell.mature = True

    def toggle_weird(self) -> None:
        new_value = not self.is_weird
        self.is_weird = new_value
        for neighbor_pos in self.farm.adjacent_positions(self.pos, wrap=False):
            neighbor = self.farm.get_entity_object(neighbor_pos)
            if isinstance(neighbor, GrowableView):
                neighbor.is_weird = new_value

    def fertilize(self, number: int) -> bool:
        if self.cell.entity is None or self.cell.mature:
            return False
        self.cell.age += (2.0 * number) * self.growth_multiplier()
        if self.cell.age >= self.cell.growth_seconds:
            self.cell.age = self.cell.growth_seconds
            self.on_fully_grown()
            self.farm.reschedule_grow_timer(self.pos)
            return True
        self.farm.reschedule_grow_timer(self.pos)
        return True

    def get_companion(self):
        if self.entity_name not in {"Grass", "Bush", "Tree", "Carrot"}:
            return None
        if self.cell.companion is None:
            self.cell.companion = self.farm._sample_companion(self.pos, self.entity_name)
        return self.cell.companion

    def apply_weird_split(self, amount: float) -> tuple[float, float]:
        if not self.is_weird:
            return amount, 0.0
        weird_amount = math.trunc(amount * 0.5)
        main_amount = math.ceil(amount * 0.5)
        return float(main_amount), float(weird_amount)

    def clear_after_harvest(self) -> None:
        self.farm.clear_entity_at(self.pos)

    def generic_harvest(self) -> bool:
        if not self.harvestable:
            self.clear_after_harvest()
            return True
        item, amount = self.farm.entity_yield(self.entity, self.cell)
        if item is None:
            self.clear_after_harvest()
            return True
        companion = self.get_companion()
        if companion is not None:
            companion_entity, companion_pos = companion
            if self.farm.grid.get_entity(companion_pos) == companion_entity:
                amount *= self.farm.companion_multiplier()
        amount, weird_amount = self.apply_weird_split(amount)
        if amount > 0.0:
            self.farm.add_items(item, amount)
        if weird_amount > 0.0:
            self.farm.add_items(self.farm.item("Weird_Substance"), weird_amount)
        self.clear_after_harvest()
        return True
