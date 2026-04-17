from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common.helper import world_size_scale


@dataclass
class CellState:
    ground: Any
    entity: Any
    water: float = 0.0
    age: float = 0.0
    mature: bool = False
    growth_seconds: float = 0.0
    companion: Any = None
    petals: int = 0
    natural_grass_age: float = 0.0
    variant: int | None = None
    weird: bool = False
    mysterious_number: float | None = None
    maze_size: int = 0
    maze_low_left: tuple[int, int] | None = None
    maze_walls: list[bool] | None = None
    removed: bool = False
    treasure_factor: int = 1
    treasure_next_pos: tuple[int, int] | None = None
    apple_next_pos: tuple[int, int] | None = None
    can_move_to: bool = False
    tail_owner_id: int | None = None

    def clear_entity_state(self) -> None:
        self.entity = None
        self.age = 0.0
        self.mature = False
        self.growth_seconds = 0.0
        self.companion = None
        self.petals = 0
        self.natural_grass_age = 0.0
        self.variant = None
        self.weird = False
        self.mysterious_number = None
        self.maze_size = 0
        self.maze_low_left = None
        self.maze_walls = None
        self.removed = False
        self.treasure_factor = 1
        self.treasure_next_pos = None
        self.apple_next_pos = None
        self.can_move_to = False
        self.tail_owner_id = None


ENTITY_STATE_FIELDS = [
    "entity",
    "age",
    "mature",
    "growth_seconds",
    "companion",
    "petals",
    "natural_grass_age",
    "variant",
    "weird",
    "mysterious_number",
    "maze_size",
    "maze_low_left",
    "maze_walls",
    "removed",
    "treasure_factor",
    "treasure_next_pos",
    "apple_next_pos",
    "can_move_to",
    "tail_owner_id",
]


@dataclass
class GridState:
    expand_level: int
    ground_grassland: Any
    ground_soil: Any
    entity_grass: Any

    def __post_init__(self) -> None:
        self.size_limit = 0
        self.had_incorrect_sunflower_harvest = False
        self._init_arrays()

    @property
    def world_size(self) -> tuple[int, int]:
        size = world_size_scale(self.expand_level)
        if self.size_limit > 2 and self.size_limit < size:
            return (self.size_limit, self.size_limit)
        if size == 2:
            return (1, 3)
        return (size, size)

    def _new_cell(self, ground: Any, entity: Any) -> CellState:
        return CellState(ground=ground, entity=entity)

    def set_size_limit(self, value: int) -> None:
        old_size = self.world_size
        if value > 2:
            self.size_limit = value
        else:
            self.size_limit = 0
        if self.world_size != old_size:
            self._init_arrays()

    def reset_for_expand(self, expand_level: int) -> None:
        self.expand_level = expand_level
        self.size_limit = 0
        self._init_arrays()

    def wrap(self, pos: tuple[int, int]) -> tuple[int, int]:
        width, height = self.world_size
        return (pos[0] % width, pos[1] % height)

    def is_within_bounds(self, pos: tuple[int, int]) -> bool:
        width, height = self.world_size
        return 0 <= pos[0] < width and 0 <= pos[1] < height

    def get_ground(self, pos: tuple[int, int]) -> Any:
        return self.cells[pos[0]][pos[1]].ground

    def set_ground(self, pos: tuple[int, int], value: Any) -> None:
        self.cells[pos[0]][pos[1]].ground = value

    def get_entity(self, pos: tuple[int, int]) -> Any:
        return self.cells[pos[0]][pos[1]].entity

    def set_entity(self, pos: tuple[int, int], value: Any) -> None:
        cell = self.cells[pos[0]][pos[1]]
        cell.clear_entity_state()
        cell.entity = value

    def set_water_volume(self, pos: tuple[int, int], value: float) -> None:
        self.cells[pos[0]][pos[1]].water = max(0.0, min(1.0, value))

    def get_water_volume(self, pos: tuple[int, int]) -> float:
        return self.cells[pos[0]][pos[1]].water

    def get_cell(self, pos: tuple[int, int]) -> CellState:
        return self.cells[pos[0]][pos[1]]

    def swap_cells(self, pos: tuple[int, int], other: tuple[int, int]) -> bool:
        if not self.is_within_bounds(other):
            return False
        left = self.get_cell(pos)
        right = self.get_cell(other)
        left_values = {name: getattr(left, name) for name in ENTITY_STATE_FIELDS}
        right_values = {name: getattr(right, name) for name in ENTITY_STATE_FIELDS}
        for name in ENTITY_STATE_FIELDS:
            setattr(left, name, right_values[name])
            setattr(right, name, left_values[name])
        return True

    def decay_water(self, rng) -> None:
        width, height = self.world_size
        for x in range(width):
            for y in range(height):
                if rng.random() < 0.1:
                    self.set_water_volume((x, y), self.get_water_volume((x, y)) * 0.99)

    def clear_grid(self, spawn_grass: bool = True) -> None:
        width, height = self.world_size
        for x in range(width):
            for y in range(height):
                self.cells[x][y] = self._new_cell(
                    ground=self.ground_grassland,
                    entity=self.entity_grass if spawn_grass else None,
                )
                if spawn_grass:
                    cell = self.cells[x][y]
                    cell.mature = True
                    cell.age = 0.5
                    cell.growth_seconds = 0.5
        self.had_incorrect_sunflower_harvest = False

    def _init_arrays(self) -> None:
        width, height = self.world_size
        self.cells = [
            [self._new_cell(self.ground_grassland, self.entity_grass) for _ in range(height)]
            for _ in range(width)
        ]
        for column in self.cells:
            for cell in column:
                cell.mature = True
                cell.age = 0.5
                cell.growth_seconds = 0.5
