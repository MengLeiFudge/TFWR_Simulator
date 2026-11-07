"""地层与特征占用包围盒；边界为左闭右开，不自动归一化原版反向盒。"""
import struct
from dataclasses import dataclass
from .catalog import Grounds


def single(value):
    """复刻 Unity 地层计算中的每次 Single 舍入。"""
    return struct.unpack('<f', struct.pack('<f', value))[0]


@dataclass(frozen=True)
class Ground:
    """一块地层的类型、挖掘硬度、稳定性及可选蘑菇颜色。"""
    kind: Grounds
    hardness: int
    stability: int
    color: int = -1
    stratum: int = -1


@dataclass(frozen=True)
class Bounds:
    """三维整数占用盒；max 不包含在占用范围内。"""
    low: tuple
    high: tuple

    def contains(self, point):
        """检查点是否处于全部坐标轴的半开范围内。"""
        return all(a <= p < b for a, p, b in zip(self.low, point, self.high))

    def overlaps(self, other):
        """使用原版严格相交规则，包括反向盒输入。"""
        return all(a < d and b > c for a, b, c, d in zip(self.low, self.high, other.low, other.high))

    @classmethod
    def enclosing(cls, points):
        """包围点集；空集合保留原版 ReverseMaxBounds。"""
        points = list(points)
        if not points:
            return cls((2147483647,) * 3, (-2147483648,) * 3)
        return cls(tuple(min(p[d] for p in points) for d in range(3)),
                   tuple(max(p[d] for p in points) + 1 for d in range(3)))
