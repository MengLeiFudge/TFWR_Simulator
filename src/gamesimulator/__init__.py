"""Game-parity simulator package.

This package is the new implementation path for reproducing TFWR script
execution locally from decompiled game logic. The old local runtime remains
reference material only.
"""

from .common.duration import Duration
from .common.helper import just_sha256_it, num_drones, world_size_scale
from .common.side_effects import SideEffect

__all__ = [
    "Duration",
    "SideEffect",
    "just_sha256_it",
    "num_drones",
    "world_size_scale",
]
