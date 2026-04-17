from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Duration:
    """Python port of Utils.Duration.

    The game stores time as integer nanoseconds and derives all script-visible
    time values from that representation.
    """

    nanoseconds: int

    @property
    def seconds(self) -> float:
        return self.nanoseconds / 1_000_000_000.0

    @classmethod
    def from_seconds(cls, seconds: float) -> "Duration":
        return cls(int(seconds * 1_000_000_000.0))

    @staticmethod
    def min(a: "Duration", b: "Duration") -> "Duration":
        return Duration(min(a.nanoseconds, b.nanoseconds))

    def __add__(self, other: "Duration") -> "Duration":
        return Duration(self.nanoseconds + other.nanoseconds)

    def __sub__(self, other: "Duration") -> "Duration":
        return Duration(self.nanoseconds - other.nanoseconds)

    def __mul__(self, factor: float) -> "Duration":
        return Duration(int(self.nanoseconds * factor))

    def __rmul__(self, factor: float) -> "Duration":
        return self.__mul__(factor)

    def __truediv__(self, other: object) -> object:
        if isinstance(other, Duration):
            return self.nanoseconds / other.nanoseconds
        if isinstance(other, (int, float)):
            return Duration(int(self.nanoseconds / other))
        return NotImplemented

    def __str__(self) -> str:
        return str(self.seconds)
