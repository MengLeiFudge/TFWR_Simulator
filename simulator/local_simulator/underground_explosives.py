"""炸药六邻传播与扫雷层控制，使用原版 Single 能量运算顺序。"""
from collections import deque
import math

from .catalog import Entities, Grounds, Items, UNDERGROUND
from .underground_types import Ground, single


def explosion_energy(world):
    return single(1000 * single(single(1.3) ** max(0, world.unlocks['dynamite'] - 1)))


def ground_drop_data(block):
    """原版已清除/损坏路径克隆没有复制非序列化物品ID，实际掉落Hay。"""
    data = UNDERGROUND['grounds'][block.kind.name]
    if block.kind == Grounds.Treasure_Path and block.color >= 0:
        return dict(data, dropItem='hay')
    return data


def ground_drops(world, block):
    """地面掉落独立于作物与爆炸实体；爆破钻只收集实际清除的块。"""
    data = ground_drop_data(block)
    if not data['dropItem']:
        return
    level = world.unlocks.get(data['yieldUpgradeName'], 0)
    factor = 1 << max(0, level - (data['yieldUpgradeName'] != 'ore_boost'))
    world.add_item(Items[data['dropItem'].title()], data['dropAmount'] * factor)


def explode(underground, origin, energy, collect=False):
    """按队列累积未访问邻块能量，已访问块以 NaN 封闭；最后一层并不清除。"""
    world = underground.world
    pending, energies, cleared = deque([origin]), {origin: energy}, []
    while pending:
        point = pending.popleft()
        x, y, z = point
        block = underground.ground_at((x, y), z)
        value = single(energies[point] - block.hardness)
        energies[point] = float('nan')
        if value >= 0 and underground.present(point):
            if point != origin:
                crop = world.entities.get((x, y))
                if ((crop is not None and crop.kind == Entities.Dynamite and underground.depths[x, y] == z)
                        or underground.sweeper.is_mine(point) or block.kind == Grounds.Soot):
                    value = energy
            if collect:
                cleared.append(point)
            else:
                underground.clear_with_caveins((x, y), z)
        spread = single(value * single(0.2))
        if spread <= 0:
            continue
        for neighbor in ((x, y + 1, z), (x + 1, y, z), (x, y - 1, z),
                         (x - 1, y, z), (x, y, z + 1), (x, y, z - 1)):
            if not world.in_bounds(neighbor[:2]) or neighbor[2] < 0:
                continue
            if neighbor not in energies:
                energies[neighbor] = 0.0
                pending.append(neighbor)
            if not math.isnan(energies[neighbor]):
                energies[neighbor] = single(energies[neighbor] + spread)
    if collect:
        for x, y, z in cleared:
            for depth in range(underground.depths[x, y], z):
                if (x, y, depth) != origin and underground.present((x, y, depth)):
                    ground_drops(world, underground.ground_at((x, y), depth))
            underground.clear_column((x, y), z)
        for x, y, z in cleared:
            underground.clear_with_caveins((x, y), z)


class Sweeper:
    """扫雷盘在第一次挖开时抽雷；地形生成不消耗这段 worldGen 随机流。"""

    def __init__(self, underground):
        self.underground = underground
        self.world = underground.world
        self.strata = {}

    def neighbors(self, pos):
        x, y = pos
        for dx, dy in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)):
            point = x + dx, y + dy
            if self.world.in_bounds(point):
                yield point

    def generate(self, point):
        """首次点击周围3×3无雷，每颗雷最多抽100次。"""
        x, y, z = point
        ratio = single(single(0.1) + single(single(single(0.17) - single(0.1)) * single(min(1, max(0, single((z - 20) / 580))))))
        if self.world.leaderboard and self.world.leaderboard['leaderboardType'] == 3:
            ratio = single(single(single(0.1) + single(0.17)) / 2)
        count = max(round(single(self.world.width * self.world.size * ratio)), 1)
        mines = set()
        rng = self.world.rng['worldGen']
        for _ in range(count):
            for _ in range(100):
                pos = rng.next(self.world.width), rng.next(self.world.size)
                if (abs(x - pos[0]) > 1 or abs(y - pos[1]) > 1) and pos not in mines:
                    mines.add(pos)
                    break
        numbers = dict.fromkeys(self.underground.depths, 0)
        for px in range(self.world.width):
            for py in range(self.world.size):
                block = self.underground.ground_at((px, py), z)
                self.underground.placed[px, py, z] = Ground(Grounds.Dynamite, block.hardness, block.stability, int((px, py) in mines))
                if (px, py) in mines:
                    for neighbor in self.neighbors((px, py)):
                        numbers[neighbor] += 1
        puzzle = {'numbers': numbers, 'mine_count': count, 'revealed': 0}
        self.strata[z] = puzzle
        return puzzle

    def measure(self, pos, depth):
        puzzle = self.strata.get(depth - 1)
        return puzzle['numbers'][pos] if puzzle else None

    def dig(self, pos):
        """处理挖开的安全格、踩雷及烟灰层提前结算。"""
        underground = self.underground
        z = underground.depths[pos]
        block = underground.ground_at(pos)
        if block.kind == Grounds.Soot:
            if z - 1 in self.strata:
                self.score((*pos, z - 1), failed=True)
            return
        if block.kind != Grounds.Dynamite:
            return
        puzzle = self.strata.get(z) or self.generate((*pos, z))
        if self.is_mine((*pos, z)):
            return
        underground.removed.add((*pos, z))
        if puzzle['numbers'][pos] == 0:
            visited, pending = {pos}, deque(self.neighbors(pos))
            while pending:
                neighbor = pending.popleft()
                if neighbor in visited or not underground.present((*neighbor, z)):
                    continue
                visited.add(neighbor)
                if underground.ground_at(neighbor, z).kind != Grounds.Dynamite:
                    continue
                underground.clear_with_caveins(neighbor, z)
                if self.is_mine((*neighbor, z)) or puzzle['numbers'][neighbor] > 0:
                    continue
                pending.extend(p for p in self.neighbors(neighbor) if p not in visited)
        puzzle['revealed'] += 1
        self.world.add_item(Items.Dynamite, 1 << max(0, self.world.unlocks['dynamite'] - 1))
        if puzzle['revealed'] >= self.world.width * self.world.size - puzzle['mine_count']:
            self.score((*pos, z), failed=False)

    def after_dig(self, pos):
        depth = self.underground.depths[pos]
        if self.is_mine((*pos, depth - 1)):
            self.world.set_entity(pos, Entities.Dynamite)

    def score(self, point, failed):
        """奖励已完全暴露邻格的剩余雷数量平方；失败先结算再爆炸。"""
        z = point[2]
        if z not in self.strata:
            return
        underground = self.underground
        count = 0
        for x in range(self.world.width):
            for y in range(self.world.size):
                pos = x, y
                if not underground.present((*pos, z)) or not self.is_mine((*pos, z)):
                    continue
                if not any(underground.present((*p, z)) and not self.is_mine((*p, z)) and p != point[:2]
                           for p in self.neighbors(pos)):
                    count += 1
        self.world.add_item(Items.Dynamite, count * count * (1 << max(0, self.world.unlocks['dynamite'] - 1)))
        if failed:
            explode(underground, point, single(1000))
        else:
            for x in range(self.world.width):
                for y in range(self.world.size):
                    underground.clear_with_caveins((x, y), z + 1)
        self.strata.pop(z, None)

    def is_mine(self, point):
        block = self.underground.ground_at(point[:2], point[2])
        return block.kind == Grounds.Dynamite and block.color != 0
