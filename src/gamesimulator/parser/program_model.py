from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Program:
    syntax_tree: Any
    global_vars: set[str]
    all_vars: set[str]
    imported_modules: set[str] = field(default_factory=set)
