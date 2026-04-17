from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class PyFunction:
    function_name: str
    syntax_tree: Any = None
    parent_scope: Any = None
    binding: Callable[..., float] | None = None
    method_object: Any = None
    is_free: bool = False

    def deep_copy(self, copies: dict[int, Any]) -> "PyFunction":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = PyFunction(
            self.function_name,
            syntax_tree=self.syntax_tree.deep_copy(copies) if hasattr(self.syntax_tree, "deep_copy") and self.syntax_tree is not None else self.syntax_tree,
            parent_scope=self.parent_scope.deep_copy(copies) if hasattr(self.parent_scope, "deep_copy") and self.parent_scope is not None else self.parent_scope,
            binding=self.binding,
            method_object=self.method_object.deep_copy(copies) if hasattr(self.method_object, "deep_copy") and self.method_object is not None else self.method_object,
            is_free=self.is_free,
        )
        copies[key] = clone
        return clone

    def __repr__(self) -> str:
        return self.function_name
