"""地下特殊地形生成；每个特征独占随机流，返回其占用包围盒。"""
from collections import deque
import math

from .catalog import Grounds, UNDERGROUND
from .noise import OpenSimplexNoise
from .underground_types import Bounds, Ground, single


def ground(kind, **values):
    """按资产默认值创建块，保留调用方显式覆盖的硬度或颜色。"""
    row = UNDERGROUND['grounds'][kind.name]
    return Ground(kind, values.get('hardness', row['maxHardness']),
                  values.get('stability', row['stability']), values.get('color', -1), values.get('stratum', -1))


class Features:
    """当前区块的生成上下文；已生成特征的包围盒影响后续放置。"""

    def __init__(self, underground, tiles, index, rng, feature, previous):
        self.underground = underground
        self.world = underground.world
        self.tiles, self.index, self.rng, self.feature, self.previous = tiles, index, rng, feature, previous
        self.start = index * 16
        self.end = self.start + 16

    def contains(self, point, ignored=()):
        """忽略原版明确允许重叠的特征类型。"""
        return any(kind not in ignored and box.contains(point) for kind, box in self.previous)

    def overlaps(self, box, ignored=()):
        """按前序特征的盒判定，未按已填充单个方块缩小占用。"""
        return any(kind not in ignored and box.overlaps(old) for kind, old in self.previous)

    def try_place(self, size, ignored=(), attempts=100):
        """三个坐标均抽随机数，包括没有水平余量时的 Next(0, 1)。"""
        room = (self.world.width - size[0], self.world.size - size[1], 16 - size[2])
        if min(room) < 0 or room == (0, 0, 0):
            return None
        for _ in range(attempts):
            low = (self.rng.next(room[0] + 1), self.rng.next(room[1] + 1),
                   self.start + self.rng.next(room[2] + 1))
            box = Bounds(low, tuple(low[i] + size[i] for i in range(3)))
            if not self.overlaps(box, ignored):
                return box
        return None

    def mushrooms(self):
        """整层蘑菇逐列拒绝与上一层同色的抽样。"""
        feature, rng = self.feature, self.rng
        size = (self.world.width, self.world.size, rng.next(feature['heightMin'], feature['heightMax'] + 1))
        box = self.try_place(size, ('OreVeinFeature', 'HardPatchesFeature', 'QuartzVeinFeature', 'PetrifiedPumpkinsFeature'))
        if box is None:
            return []
        colors = min(6, max(2, round(feature['typesMax'])))
        previous = {}
        for z in range(box.low[2], box.high[2]):
            for x in range(self.world.width):
                for y in range(self.world.size):
                    color = rng.next(colors)
                    while color == previous.get((x, y), -1):
                        color = rng.next(colors)
                    previous[x, y] = color
                    self.tiles[x, y, z] = ground(Grounds.Mushroom, color=color)
        return [box]

    def treasure_map(self):
        """玄武岩层下一格地图，预留本次清图时确定的路径深度。"""
        box = self.try_place((self.world.width, self.world.size, 2 + min(self.underground.treasure.path_depth, 16)),
                             ('HardPatchesFeature', 'PetrifiedPumpkinsFeature'))
        if box is None:
            return []
        for x in range(self.world.width):
            for y in range(self.world.size):
                self.tiles[x, y, box.low[2]] = ground(Grounds.Basalt)
        padding_x, padding_y = min(2, self.world.width // 4), min(2, self.world.size // 4)
        point = (self.rng.next(padding_x, self.world.width - padding_x),
                 self.rng.next(padding_y, self.world.size - padding_y), box.low[2] + 1)
        self.tiles[point] = ground(Grounds.Treasure_Map)
        return [box, Bounds.enclosing([point])]

    def sweeper(self):
        """两层扫雷地形，雷的位置延后到首挖才生成。"""
        box = self.try_place((self.world.width, self.world.size, 2),
                             ('OreVeinFeature', 'HardPatchesFeature', 'QuartzVeinFeature', 'PetrifiedPumpkinsFeature'))
        if box is None:
            return []
        for x in range(self.world.width):
            for y in range(self.world.size):
                self.tiles[x, y, box.low[2]] = ground(Grounds.Dynamite)
                self.tiles[x, y, box.low[2] + 1] = ground(Grounds.Soot)
        return [box]

    def pyramid(self):
        """奇数边长沙金字塔，随机侵蚀若干整列并覆盖薄土。"""
        rng = self.rng
        limit = self.world.width if self.world.width % 2 else self.world.width - 1
        ignored = tuple(kind for kind, _ in self.previous
                        if kind not in ('TreasureMapFeature', 'SweeperStratumFeature', 'MushroomFeature'))
        while limit >= 5:
            size = 5 + rng.next(max((limit - 5) // 2, 0) + 1) * 2
            height = size // 2 + 1
            box = self.try_place((size, size, height + 1), ignored, 20)
            if box is None:
                limit = limit // 2 + 1
                continue
            px, py = box.low[:2]
            foundation = box.high[2] - 1
            bottom = foundation - 1
            self.underground.pyramids.append((px, py, bottom, size))
            eroded = set()
            for _ in range(rng.next(3, 7)):
                point = rng.next(size), rng.next(size)
                while point in eroded:
                    point = rng.next(size), rng.next(size)
                eroded.add(point)
            for x in range(size):
                for y in range(size):
                    self.tiles[px + x, py + y, foundation] = ground(Grounds.Limestone)
                    column_height = 1 + min(x, y, size - 1 - x, size - 1 - y)
                    z = bottom
                    if (x, y) not in eroded:
                        while z > bottom - column_height:
                            self.tiles[px + x, py + y, z] = ground(Grounds.Sand)
                            z -= 1
                    cap = rng.next(1, 3)
                    while z > bottom - column_height - cap and z >= self.start:
                        self.tiles[px + x, py + y, z] = ground(Grounds.Dirt, hardness=1, stability=1)
                        z -= 1
            return [box]
        return []

    def special_soils(self):
        """珍珠岩或壤土的两层噪声地形。"""
        rng, feature = self.rng, self.feature
        noise = OpenSimplexNoise(rng.next())
        start = self.start + feature['startOffset'] + rng.next(feature['randomStartOffsetMin'], feature['randomStartOffsetMax'])
        kind = Grounds.Perlite if feature['m_Name'].endswith('perlite') else Grounds.Loam
        scale = feature['noiseSamplingScale']
        points = []
        for x in range(self.world.width):
            for y in range(self.world.size):
                z = start + int((noise.evaluate(single(x * scale), single(y * scale)) + 1) * 0.5 * feature['hillRange'])
                for depth in (z, z + 1):
                    self.tiles[x, y, depth] = ground(kind)
                    points.append((x, y, depth))
        return [Bounds.enclosing(points)]

    def iron(self):
        """在分区内抽矿脉起点，以随机排序的六邻 BFS 生长矿脉。"""
        rng, feature = self.rng, self.feature
        period = math.ceil(single(single((feature['veinSize'] * 2) ** single(1 / 3)) * single(1.5))) + 1
        first = True
        boxes = []
        cache = self.underground.ore_cache.setdefault(self.index, {}).setdefault('iron', [])
        for x in range(0, self.world.width, period):
            for y in range(0, self.world.size, period):
                for z in range(self.start, self.end, period):
                    if rng.double() >= feature['veinProbability']:
                        continue
                    ex, ey, ez = min(x + period, self.world.width), min(y + period, self.world.size), min(z + period, self.end)
                    initial = rng.next(x, ex), rng.next(y, ey), rng.next(z, ez)
                    fraction = single((ex - x) * (ey - y) * (ez - z) / period ** 3)
                    if not first and rng.double() >= fraction:
                        continue
                    size = feature['veinSize'] * (1 << self.world.unlocks['ore_boost']) + rng.next(feature['randomAdditionalVeinSizeMin'], feature['randomAdditionalVeinSizeMax'])
                    pending, visited, points = deque([initial]), set(), []
                    while pending and len(points) < size:
                        pos = pending.popleft()
                        if not self.start <= pos[2] < self.end or not self.world.in_bounds(pos[:2]) or pos in visited:
                            continue
                        visited.add(pos)
                        if self.contains(pos):
                            continue
                        points.append(pos)
                        cache.append(pos)
                        self.tiles[pos] = ground(Grounds.Iron)
                        px, py, pz = pos
                        adjacent = ((px, py + 1, pz), (px + 1, py, pz), (px, py - 1, pz), (px - 1, py, pz), (px, py, pz + 1), (px, py, pz - 1))
                        pending.extend(sorted(adjacent, key=lambda _: rng.next()))
                    if points:
                        boxes.append(Bounds.enclosing(points))
                        first = False
        return boxes

    def quartz(self):
        """生成竖直石英针，允许覆盖硬块、铁矿和石化南瓜。"""
        rng, feature = self.rng, self.feature
        amount = single(single(feature['veinRollsPer4x4WorldSize'] * self.world.width) * self.world.size)
        count = int(amount) + (rng.double() < single(amount - int(amount)))
        boxes = []
        cache = self.underground.ore_cache.setdefault(self.index, {}).setdefault('quartz', [])
        for _ in range(count):
            if rng.double() > feature['veinChance']:
                continue
            size = feature['veinSize'] * (1 << self.world.unlocks['ore_boost']) + rng.next(feature['randomAdditionalVeinSizeMin'], feature['randomAdditionalVeinSizeMax'])
            bend = rng.next(2, size) if rng.double() < feature['changeNeedleXYChance'] else 2147483647
            x, y, z = rng.next(self.world.width), rng.next(self.world.size), rng.next(self.start, self.end - size)
            points = []
            for index in range(size):
                if index == bend:
                    x = min(self.world.width - 1, max(0, x + rng.next(-1, 2)))
                    y = min(self.world.size - 1, max(0, y + rng.next(-1, 2)))
                pos = x, y, z + index
                if not self.contains(pos, ('PetrifiedPumpkinsFeature', 'OreVeinFeature', 'HardPatchesFeature')):
                    self.tiles[pos] = ground(Grounds.Quartz)
                    points.append(pos)
                    cache.append(pos)
            boxes.append(Bounds.enclosing(points))
        return boxes

    def petrified(self):
        """石化南瓜立方体及其不稳定的顶土；装饰网格不参与模拟。"""
        rng, feature = self.rng, self.feature
        large = self.world.width > 5
        period = feature['periodHorizontalSmall' if large else 'periodHorizontalLarge']
        boxes = []
        for x in range(0, self.world.width, period):
            size = (5 if rng.double() < feature['largePumpkinChance'] else 3) if large else 3
            room_x = min(period, self.world.width - x) - size
            if room_x < 0:
                continue
            for y in range(0, self.world.size, period):
                room_y = min(period, self.world.size - y) - size
                if room_y < 0:
                    continue
                for z in range(self.start + 1, self.end, feature['periodVertical']):
                    room_z = min(feature['periodVertical'], self.end - z) - size
                    if room_z < 0 or rng.double() < feature['skipSpawnChance']:
                        continue
                    px, py, pz = x + rng.next(room_x + 1), y + rng.next(room_y + 1), z + rng.next(room_z + 1)
                    for dx in range(size):
                        for dy in range(size):
                            top = px + dx, py + dy, pz - 1
                            if not self.contains(top):
                                self.tiles[top] = ground(Grounds.Dirt, hardness=1, stability=0)
                            for dz in range(size):
                                self.tiles[px + dx, py + dy, pz + dz] = ground(Grounds.Petrified_Pumpkin)
                    boxes.append(Bounds((px, py, pz), (px + size, py + size, pz + size)))
        return boxes
