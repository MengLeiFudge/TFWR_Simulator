from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def entity_name_of(entity: Any) -> str:
    if entity is None:
        return ""
    return str(entity).split(".")[-1]


@dataclass
class FarmObjectView:
    farm: Any
    pos: tuple[int, int]

    @property
    def cell(self):
        return self.farm.grid.get_cell(self.pos)

    @property
    def entity(self) -> Any:
        return self.cell.entity

    @property
    def entity_name(self) -> str:
        return entity_name_of(self.entity)

    @property
    def is_weird(self) -> bool:
        return bool(self.cell.weird)

    @is_weird.setter
    def is_weird(self, value: bool) -> None:
        self.cell.weird = bool(value)

    @property
    def harvestable(self) -> bool:
        return self.entity is not None

    @property
    def grown_percent(self) -> float:
        if self.cell.growth_seconds <= 0.0:
            return 1.0 if self.cell.mature else 0.0
        return max(0.0, min(1.0, self.cell.age / self.cell.growth_seconds))

    def can_move_to_from(self, direction: Any) -> bool:
        return True

    def can_move_away_to(self, direction: Any) -> bool:
        return True

    def measure(self):
        return None

    def toggle_weird(self) -> None:
        self.is_weird = not self.is_weird

    def harvest(self, drone) -> bool:
        return False
