from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Iterator


class GridDirection(Enum):
    NORTH = "North"
    EAST = "East"
    SOUTH = "South"
    WEST = "West"

    def __str__(self) -> str:
        return self.value


class PyValue:
    def deep_copy(self, copies: dict[int, Any]) -> "PyValue":
        return deepcopy(self)

    def size(self) -> int:
        return 1


class PyNone(PyValue):
    _instance: "PyNone | None" = None

    def __new__(cls) -> "PyNone":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PyNone)

    def __hash__(self) -> int:
        return 12903874

    def __repr__(self) -> str:
        return "None"

    def deep_copy(self, copies: dict[int, Any]) -> "PyNone":
        return self


@dataclass(frozen=True)
class PyNumber(PyValue):
    num: float

    def __float__(self) -> float:
        return float(self.num)

    @staticmethod
    def modulo(lhs: "PyNumber", rhs: "PyNumber") -> "PyNumber":
        value = lhs.num % rhs.num
        if value * rhs.num < 0.0:
            value += rhs.num
        return PyNumber(value)

    @staticmethod
    def floor_division(lhs: "PyNumber", rhs: "PyNumber") -> "PyNumber":
        return PyNumber(math.floor(lhs.num / rhs.num))

    def deep_copy(self, copies: dict[int, Any]) -> "PyNumber":
        return self


class PyTickNumber(PyNumber):
    display_as_int = True


class PyBool(PyNumber):
    def __init__(self, value: bool):
        super().__init__(1.0 if value else 0.0)

    def __bool__(self) -> bool:
        return self.num != 0.0

    def __repr__(self) -> str:
        return "True" if self.num != 0.0 else "False"


@dataclass(frozen=True)
class PyString(PyValue):
    text: str

    def __repr__(self) -> str:
        return self.text

    def __iter__(self) -> Iterator["PyString"]:
        for char in self.text:
            yield PyString(char)

    def __len__(self) -> int:
        return len(self.text)

    def __getitem__(self, index: int) -> "PyString":
        return PyString(self.text[index])

    def size(self) -> int:
        return max(1, len(self.text) // 8)

    def deep_copy(self, copies: dict[int, Any]) -> "PyString":
        return self


@dataclass
class PyTuple(PyValue):
    elements: list[Any]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def __getitem__(self, index: int) -> Any:
        return self.elements[index]

    def size(self) -> int:
        return sum(getattr(item, "size", lambda: 1)() for item in self.elements)

    def __hash__(self) -> int:
        normalized = []
        for item in self.elements:
            if isinstance(item, PyTuple):
                normalized.append(hash(item))
            elif isinstance(item, PyList):
                normalized.append(tuple(item.items))
            else:
                normalized.append(item)
        return hash(tuple(normalized))

    def deep_copy(self, copies: dict[int, Any]) -> "PyTuple":
        key = id(self.elements)
        if key in copies:
            return copies[key]
        clone = PyTuple([])
        copies[key] = clone
        clone.elements.extend(_deep_copy_value(item, copies) for item in self.elements)
        return clone


@dataclass
class PyList(PyValue):
    items: list[Any]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> Any:
        return self.items[index]

    def __setitem__(self, index: int, value: Any) -> None:
        self.items[index] = value

    def append(self, value: Any) -> None:
        self.items.append(value)

    def evaluate(self, name: str):
        return _method_function(name, self)

    def size(self) -> int:
        return sum(getattr(item, "size", lambda: 1)() for item in self.items)

    def deep_copy(self, copies: dict[int, Any]) -> "PyList":
        key = id(self.items)
        if key in copies:
            return copies[key]
        clone = PyList([])
        copies[key] = clone
        clone.items.extend(_deep_copy_value(item, copies) for item in self.items)
        return clone


@dataclass
class PySet(PyValue):
    items: set[Any]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def size(self) -> int:
        return sum(getattr(item, "size", lambda: 1)() for item in self.items)

    def deep_copy(self, copies: dict[int, Any]) -> "PySet":
        key = id(self.items)
        if key in copies:
            return copies[key]
        clone = PySet(set())
        copies[key] = clone
        for item in self.items:
            clone.items.add(_deep_copy_value(item, copies))
        return clone

    def evaluate(self, name: str):
        return _method_function(name, self)


@dataclass
class PyObjectBox:
    obj: Any


@dataclass
class PyDict(PyValue):
    items: dict[Any, PyObjectBox]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.items.keys())

    def __len__(self) -> int:
        return len(self.items)

    def at(self, key: Any, value_to_set: Any | None = None) -> Any:
        if value_to_set is not None:
            if key in self.items:
                self.items[key].obj = value_to_set
            else:
                self.items[key] = PyObjectBox(value_to_set)
        if key not in self.items:
            raise KeyError(key)
        return self.items[key].obj

    def size(self) -> int:
        return sum(getattr(key, "size", lambda: 1)() for key in self.items.keys())

    def deep_copy(self, copies: dict[int, Any]) -> "PyDict":
        key = id(self.items)
        if key in copies:
            return copies[key]
        clone = PyDict({})
        copies[key] = clone
        for item_key, value in self.items.items():
            clone.items[_deep_copy_value(item_key, copies)] = PyObjectBox(_deep_copy_value(value.obj, copies))
        return clone

    def evaluate(self, name: str):
        return _method_function(name, self)


@dataclass(frozen=True)
class PyRange(PyValue):
    start: float
    end: float
    step: float = 1.0

    def __post_init__(self) -> None:
        if abs(self.step) < 0.01:
            raise ValueError("error_zero_step_size")

    def __len__(self) -> int:
        return int(math.ceil(max((self.end - self.start) / self.step, 0.0)))

    def __getitem__(self, index: int) -> PyNumber:
        if index < 0 or index >= len(self):
            raise IndexError(index)
        return PyNumber(self.start + index * self.step)

    def __iter__(self) -> Iterator[PyNumber]:
        current = self.start
        if self.step >= 0.0:
            while current < self.end:
                yield PyNumber(current)
                current += self.step
        else:
            while current > self.end:
                yield PyNumber(current)
                current += self.step

    def deep_copy(self, copies: dict[int, Any]) -> "PyRange":
        return self


@dataclass
class PyDroneHandle(PyValue):
    drone_id: int
    generation: int = 0
    return_value: Any = None

    def __int__(self) -> int:
        return self.drone_id

    def __repr__(self) -> str:
        return f"<drone {self.generation}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PyDroneHandle) and other.generation == self.generation

    def __hash__(self) -> int:
        return hash(self.generation)

    def deep_copy(self, copies: dict[int, Any]) -> "PyDroneHandle":
        return self


@dataclass(frozen=True)
class PyGridDirection(PyValue):
    direction: GridDirection

    def __repr__(self) -> str:
        return str(self.direction)

    def deep_copy(self, copies: dict[int, Any]) -> "PyGridDirection":
        return self


class PyUnassigned(PyValue):
    def __repr__(self) -> str:
        return "<unassigned>"


class PyModule(PyValue):
    def __init__(self, name: str, scope: Any = None):
        self.name = name
        self.scope = scope

    def __repr__(self) -> str:
        return f"<module {self.name}>"


class PyConstBag(PyValue):
    def __init__(self, elements: dict[str, Any], name: str):
        self.elements = elements
        self.name = name

    def evaluate(self, name: str) -> Any:
        if name not in self.elements:
            raise KeyError(name)
        return self.elements[name]

    def __repr__(self) -> str:
        return self.name

    def __iter__(self):
        return iter(self.elements.values())

    def __len__(self) -> int:
        return len(self.elements)


def _deep_copy_value(value: Any, copies: dict[int, Any]) -> Any:
    if hasattr(value, "deep_copy"):
        return value.deep_copy(copies)
    return deepcopy(value)


def _method_function(name: str, method_object: Any):
    from .builtins_api import default_methods

    methods = default_methods()
    if name not in methods:
        raise KeyError(name)
    func = methods[name]
    bound = func.deep_copy({})
    bound.method_object = method_object
    return bound
