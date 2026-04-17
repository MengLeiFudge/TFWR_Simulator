from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from .duration import Duration


@dataclass(order=True)
class TimerRecord:
    finish_time: Duration
    func: Callable[[], None] = field(compare=False)
    stopped: bool = field(default=False, compare=False)


@dataclass
class RuntimeMailbox:
    all_messages: deque[tuple[Any, int]]
    per_channel: list[deque[Any]]


@dataclass
class RuntimePlaceholders:
    current_side_effect_argument: Any = None
    current_side_effect_argument2: Any = None
    current_execute_exception: Exception | None = None

