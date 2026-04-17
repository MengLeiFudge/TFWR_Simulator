from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleState:
    global_scope: Any = None
    call_stack: list[Any] = field(default_factory=list)
    return_value: Any = None
    is_expression_static: bool = False
    current_executing_node: Any = None
