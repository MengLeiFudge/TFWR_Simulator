from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .execute_exception import ExecuteException
from .py_values import (
    GridDirection,
    PyBool,
    PyGridDirection,
    PyNone,
    PyString,
    PyUnassigned,
)


@dataclass
class ScopeEntry:
    val: Any
    is_static: bool


class Scope:
    def __init__(self, function_node: Any, call_node: Any, parent_scope: "Scope | None", variable_names: set[str] | None):
        self.function_node = function_node
        self.call_node = call_node
        self.parent_scope = parent_scope
        self.vars: dict[str, ScopeEntry] = {}
        for variable_name in variable_names or set():
            self.vars[variable_name] = ScopeEntry(PyUnassigned(), False)

    def set_var(self, var_name: str, value: Any, check_shadow: bool = True, is_static: bool = False) -> None:
        if var_name in self.vars:
            self.vars[var_name] = ScopeEntry(value, is_static)
        elif self.parent_scope is not None:
            self.parent_scope.set_var(var_name, value, check_shadow, is_static)
        else:
            self.vars[var_name] = ScopeEntry(value, is_static)

    def import_var(self, var_name: str, value: Any, is_static: bool = False) -> None:
        self.vars[var_name] = ScopeEntry(value, is_static)

    def deep_copy(self, copies: dict[int, Any]) -> "Scope":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = Scope(self.function_node, self.call_node, None, set())
        copies[key] = clone
        clone.parent_scope = self.parent_scope.deep_copy(copies) if self.parent_scope is not None else None
        for name, entry in self.vars.items():
            value = entry.val.deep_copy(copies) if hasattr(entry.val, "deep_copy") else entry.val
            clone.vars[name] = ScopeEntry(value, entry.is_static)
        return clone

    def has_var(self, var_name: str) -> bool:
        if var_name in self.vars:
            return True
        if self.parent_scope is not None:
            return self.parent_scope.has_var(var_name)
        return False

    def evaluate(self, name: str, current_file_name: str = "") -> ScopeEntry:
        if name in self.vars:
            entry = self.vars[name]
            if isinstance(entry.val, PyUnassigned):
                raise ExecuteException(f"error_use_before_assign:{name}")
            return entry
        if self.parent_scope is not None:
            return self.parent_scope.evaluate(name, current_file_name)
        constant = self.evaluate_constant(name)
        if constant is not None:
            return ScopeEntry(constant, True)
        raise ExecuteException(f"error_name_not_defined:{name}")

    @staticmethod
    def evaluate_constant(name: str) -> Any:
        if name == "True":
            return PyBool(True)
        if name == "False":
            return PyBool(False)
        if name == "None":
            return PyNone()
        if name == "North":
            return PyGridDirection(GridDirection.NORTH)
        if name == "East":
            return PyGridDirection(GridDirection.EAST)
        if name == "South":
            return PyGridDirection(GridDirection.SOUTH)
        if name == "West":
            return PyGridDirection(GridDirection.WEST)
        return None

    @staticmethod
    def is_constant(name: str) -> bool:
        return Scope.evaluate_constant(name) is not None

    @staticmethod
    def is_true_value(value: Any) -> bool:
        if isinstance(value, PyNone):
            return False
        if isinstance(value, PyBool):
            return bool(value)
        if hasattr(value, "num"):
            return float(value.num) != 0.0
        if isinstance(value, (list, tuple, set, dict, str)):
            return len(value) > 0
        return True
