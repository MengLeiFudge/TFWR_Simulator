"""藏宝图随机路线、所属无人机与20毫秒路径完整性检查。"""
import math
from typing import TypedDict

from .catalog import Entities, Grounds, UNDERGROUND
from .underground_types import Ground, single


PATH_GROUNDS = (Grounds.Treasure_Path, Grounds.Treasure_Goal)


class TreasurePath(TypedDict):
    """一张地图的路径、所属无人机及完整性检查游标。"""
    path: list[tuple[int, int, int]]
    drone: int
    furthest: int
    minimum: int


class TreasureMaps:
    """生成路径时保留原地层硬度和稳定性，仅替换地面类型。"""

    def __init__(self, underground):
        self.underground = underground
        self.world = underground.world
        self.path_depth = 4 + self.world.unlocks['treasure_map']
        self.paths: list[TreasurePath] = []

    def set_kind(self, point, kind, broken=None):
        block = self.underground.ground_at(point[:2], point[2])
        self.underground.placed[point] = Ground(kind, block.hardness, block.stability, -1 if broken is None else int(broken))
        if self.underground.depths[point[:2]] == point[2]:
            self.world.grounds[point[:2]] = kind

    def generate(self, start):
        """逐深度组合随机目标、往返和回路；拒绝已挖空或带控制器的块。"""
        world, underground = self.world, self.underground
        rng = world.rng['worldGen']
        size = world.width, world.size
        t = single(min(1, max(0, single((size[0] - 4) / 28))))
        features = math.ceil(single(5 + single(20 * t)))
        repeats = math.ceil(single(10 + single(-5 * t)))
        path, steps = [start], []

        def last():
            return steps[-1] if steps else path[-1]

        def down():
            x, y, z = last()
            steps.append((x, y, z + 1))

        def target(goal, axis=None):
            current = list(last())
            axis = rng.next(2) if axis is None else axis
            for a in (axis, 1 - axis):
                sign = 1 if goal[a] > current[a] else -1
                while current[a] != goal[a]:
                    current[a] += sign
                    steps.append(tuple(current))

        def random_target():
            goal = rng.next(size[0]), rng.next(size[1]), last()[2]
            target(goal)

        def back_and_forth():
            current = list(last())
            axis = rng.next(2)
            distance = rng.next(1, size[axis] // 2 + 1)
            sign = 1 if current[axis] < distance else (1 if rng.next(2) else -1) if current[axis] + distance < size[axis] else -1
            for direction in (sign, -sign):
                for _ in range(distance):
                    current[axis] += direction
                    steps.append(tuple(current))

        def loop():
            origin = last()
            x = (origin[0] + rng.next(2, size[0] // 2) * (1 if rng.next(2) else -1)) % size[0]
            y = (origin[1] + rng.next(2, size[1] // 2) * (1 if rng.next(2) else -1)) % size[1]
            axis = rng.next(2)
            target((x, y, origin[2]), axis)
            target(origin, axis)

        def repeat(generator, maximum):
            count = rng.next(1, maximum + 1)
            begin = len(steps)
            generator()
            block = steps[begin:]
            steps.extend(block * (count - 1))

        def attempt(generator):
            steps.clear()
            generator()
            for point in steps:
                kind = underground.ground_at(point[:2], point[2]).kind
                if (not underground.present(point) or UNDERGROUND['grounds'][kind.name]['controller']
                        or kind in PATH_GROUNDS):
                    return False
            path.extend(steps)
            return True

        def combined():
            random_target()
            down()

        for _ in range(1, self.path_depth):
            if not attempt(down) and not any(attempt(combined) for _ in range(10)):
                raise ValueError('藏宝图无法生成下降路径')
            for _ in range(rng.next(1, features + 1)):
                for _ in range(10):
                    choice = rng.double()
                    generator = random_target if choice < 0.5 else (lambda: repeat(back_and_forth, repeats // 2)) if choice < 0.8 else (lambda: repeat(loop, repeats))
                    if attempt(generator):
                        break
                else:
                    raise ValueError('藏宝图无法生成路径片段')
        attempt(down)
        for index, point in enumerate(path[1:], start=1):
            self.set_kind(point, Grounds.Treasure_Goal if index == len(path) - 1 else Grounds.Treasure_Path)
        return path

    def measure(self, pos, depth):
        kind = self.underground.ground_at(pos, depth).kind
        if kind == Grounds.Basalt:
            for x in range(self.world.width):
                for y in range(self.world.size):
                    if self.underground.ground_at((x, y), depth + 1).kind == Grounds.Treasure_Map:
                        return x, y
            return None
        if kind != Grounds.Treasure_Map:
            return None
        start = (*pos, depth)
        data: TreasurePath | None = next((p for p in self.paths if p['path'][0] == start), None)
        if data is None:
            data = {'path': self.generate(start), 'drone': -1, 'furthest': 0, 'minimum': 1}
            self.paths.append(data)
            self.world.timers.start(self.world.now_ns + 20000000, self.check_paths)
        directions = {(1, 0, 0): 'E', (-1, 0, 0): 'W', (0, 1, 0): 'N', (0, -1, 0): 'S', (0, 0, 1): 'D'}
        return ''.join(directions[b[0] - a[0], b[1] - a[1], b[2] - a[2]]
                       for a, b in zip(data['path'], data['path'][1:]))

    def clear_block(self, point, broken):
        if self.underground.ground_at(point[:2], point[2]).kind in PATH_GROUNDS:
            self.set_kind(point, Grounds.Treasure_Path, broken)

    def clear(self, data, broken=True):
        for point in data['path']:
            self.clear_block(point, broken)
        self.paths.remove(data)

    def check_paths(self):
        for data in list(reversed(self.paths)):
            minimum = data['minimum']
            for index in range(minimum, len(data['path'])):
                point = data['path'][index]
                if not self.underground.present(point) or self.underground.ground_at(point[:2], point[2]).kind not in PATH_GROUNDS:
                    if index >= data['furthest']:
                        self.clear(data)
                        break
                    minimum = index
            else:
                for point in data['path'][data['minimum']:minimum]:
                    self.clear_block(point, False)
                data['minimum'] = minimum
        if self.paths:
            self.world.timers.start(self.world.now_ns + 20000000, self.check_paths)

    def after_dig(self, pos):
        depth = self.underground.depths[pos]
        if self.underground.ground_at(pos, depth - 1).kind == Grounds.Treasure_Map:
            data = next((p for p in self.paths if p['path'][0] == (*pos, depth - 1)), None)
            if data is None or data['drone'] >= 0:
                return
            data['drone'] = self.world.current_drone
        self.check_position(self.world.current_drone, (*pos, depth), reveal=True)

    def remove_drone(self, drone):
        data = next((p for p in self.paths if p['drone'] == drone), None)
        if data:
            self.clear(data)

    def check_position(self, drone, point, reveal=False):
        data = next((p for p in self.paths if p['drone'] == drone), None)
        if data is None:
            return
        indices = [i for i, p in enumerate(data['path']) if p == point]
        block = self.underground.ground_at(point[:2], point[2])
        if not indices or block.kind not in PATH_GROUNDS:
            self.clear(data)
            return
        index = indices[-1]
        if index == len(data['path']) - 1 and block.kind == Grounds.Treasure_Goal:
            self.clear(data, broken=False)
            crop = self.world.set_entity(point[:2], Entities.Underground_Treasure)
            crop.number = len(data['path'])
            crop.grown = True
            return
        data['furthest'] = index
        if reveal and block.kind == Grounds.Treasure_Path and block.color != 1:
            for target in data['path'][data['minimum']:]:
                if target[2] == point[2]:
                    self.underground.clear_with_caveins(target[:2], target[2])
