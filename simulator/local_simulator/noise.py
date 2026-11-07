"""地下生成使用的 OpenSimplex 2D/3D；保留原版 Int64 洗牌和贡献项顺序。"""
import json
import math
from pathlib import Path

TABLES = json.loads(Path(__file__).with_name('noise_tables.json').read_text())


def contributions(dimensions):
    """按原版查找表构造各哈希位置的有序贡献项。"""
    suffix = str(dimensions) + 'D'
    base = TABLES['BASE_' + suffix]
    points = TABLES['POINTS_' + suffix]
    pairs = TABLES['LOOKUP_PAIRS_' + suffix]
    stride = dimensions + 1
    group_size = 4 if dimensions == 2 else 9
    squish = 0.366025403784439 if dimensions == 2 else 1.0 / 3.0
    groups = []
    for offset in range(0, len(points), group_size):
        values = base[points[offset]] + points[offset + 1:offset + group_size]
        group = []
        for index in range(0, len(values), stride):
            multiplier, *coords = values[index:index + stride]
            group.append((coords, tuple(-c - multiplier * squish for c in coords)))
        groups.append(group)
    return {pairs[i]: groups[pairs[i + 1]] for i in range(0, len(pairs), 2)}


LOOKUP_2D = contributions(2)
LOOKUP_3D = contributions(3)


class OpenSimplexNoise:
    """给定种子后仅查询，不消耗任何游戏随机流。"""

    def __init__(self, seed):
        source = list(range(256))
        self.perm = [0] * 256
        for _ in range(3):
            seed = (seed * 6364136223846793005 + 1442695040888963407) & 0xffffffffffffffff
        for index in range(255, -1, -1):
            seed = (seed * 6364136223846793005 + 1442695040888963407) & 0xffffffffffffffff
            signed = ((seed + 31 + (1 << 63)) & 0xffffffffffffffff) - (1 << 63)
            selected = signed % (index + 1)
            self.perm[index] = source[selected]
            source[selected] = source[index]
        self.perm2 = [value & 14 for value in self.perm]
        self.perm3 = [value % 24 * 3 for value in self.perm]

    def evaluate(self, x, y, z=None):
        """计算二维或三维噪声；坐标及贡献累加使用 Double。"""
        if z is None:
            stretch = (x + y) * -0.211324865405187
            bx, by = math.floor(x + stretch), math.floor(y + stretch)
            squish = (bx + by) * 0.366025403784439
            dx, dy = x - (bx + squish), y - (by + squish)
            fx, fy = x + stretch - bx, y + stretch - by
            total = fx + fy
            key = int(fx - fy + 1) | (int(total) << 1) | (int(total + fy) << 2) | (int(total + fx) << 4)
            result = 0.0
            gradients = TABLES['GRADIENTS_2D']
            for (cx, cy), (ox, oy) in LOOKUP_2D[key]:
                px, py = dx + ox, dy + oy
                attenuation = 2.0 - px * px - py * py
                if attenuation > 0:
                    index = self.perm2[(self.perm[(bx + cx) & 255] + by + cy) & 255]
                    dot = gradients[index] * px + gradients[index + 1] * py
                    attenuation *= attenuation
                    result += attenuation * attenuation * dot
            return result * (1.0 / 47.0)
        stretch = (x + y + z) * (-1.0 / 6.0)
        bx, by, bz = math.floor(x + stretch), math.floor(y + stretch), math.floor(z + stretch)
        squish = (bx + by + bz) * (1.0 / 3.0)
        dx, dy, dz = x - (bx + squish), y - (by + squish), z - (bz + squish)
        fx, fy, fz = x + stretch - bx, y + stretch - by, z + stretch - bz
        total = fx + fy + fz
        key = (int(fy - fz + 1) | (int(fx - fy + 1) << 1) | (int(fx - fz + 1) << 2)
               | (int(total) << 3) | (int(total + fz) << 5) | (int(total + fy) << 7) | (int(total + fx) << 9))
        result = 0.0
        gradients = TABLES['GRADIENTS_3D']
        for (cx, cy, cz), (ox, oy, oz) in LOOKUP_3D[key]:
            px, py, pz = dx + ox, dy + oy, dz + oz
            attenuation = 2.0 - px * px - py * py - pz * pz
            if attenuation > 0:
                index = self.perm3[(self.perm[(self.perm[(bx + cx) & 255] + by + cy) & 255] + bz + cz) & 255]
                dot = gradients[index] * px + gradients[index + 1] * py + gradients[index + 2] * pz
                attenuation *= attenuation
                result += attenuation * attenuation * dot
        return result * (1.0 / 103.0)
