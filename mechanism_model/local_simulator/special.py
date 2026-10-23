"""南瓜分组、迷宫和恐龙的状态机；农田与资源仍由 FarmWorld 持有。"""

from collections import deque
import heapq

from .catalog import Direction, Entities, Grounds, Items


def update_pumpkin_squares(world, pos):
    """单格变化只刷新依赖它的西南正方形；按x+y降序保证先更新依赖。"""
    dp = world.pumpkin_squares
    pending = [(-(pos[0] + pos[1]), pos)]
    queued = {pos}
    while pending:
        _, current = heapq.heappop(pending)
        x, y = current
        crop = world.entities.get(current)
        value = 0
        if crop is not None and crop.kind == Entities.Pumpkin and crop.grown:
            value = 1 + min(dp.get((x + 1, y), 0), dp.get((x, y + 1), 0), dp.get((x + 1, y + 1), 0))
        if value == dp.get(current, 0):
            continue
        if value:
            dp[current] = value
        else:
            dp.pop(current, None)
        for neighbor in ((x - 1, y), (x, y - 1), (x - 1, y - 1)):
            if world.in_bounds(neighbor) and neighbor not in queued:
                queued.add(neighbor)
                heapq.heappush(pending, (-(neighbor[0] + neighbor[1]), neighbor))


def merge_pumpkin(world, plant):
    """选择包含新成熟南瓜的最大正方形，已有合并组不能被部分切开。"""
    size = world.size
    update_pumpkin_squares(world, plant.pos)
    dp = world.pumpkin_squares
    maximum = max(dp.values(), default=1)
    px, py = plant.pos
    for side in range(maximum, 0, -1):
        for y in range(max(0, py - side + 1), min(py + 1, size - side + 1)):
            for x in range(max(0, px - side + 1), min(px + 1, world.width - side + 1)):
                if dp.get((x, y), 0) < side:
                    continue
                positions = [(a, b) for a in range(x, x + side) for b in range(y, y + side)]
                if any(c.group and not (x <= c.group[0] and y <= c.group[1]
                       and c.group[0] + c.group[2] <= x + side and c.group[1] + c.group[2] <= y + side)
                       for c in (world.entities[p] for p in positions)):
                    continue
                number = world.entities[x, y].number
                for pos in positions:
                    crop = world.entities[pos]
                    crop.group = (x, y, side)
                    crop.number = number
                return


class Maze:
    """一块不环绕的迷宫；再利用先结算金币，200t后移动宝藏并随机开墙。"""

    def __init__(self, world, pos, desired_size):
        self.world = world
        self.size = min(desired_size, world.width)
        size = self.size
        self.origin = tuple(max(0, min(value - size // 2, extent - size))
                            for value, extent in zip(pos, (world.width, world.size)))
        rng = world.rng['maze']
        start = rng.next(size * size)
        walls = {start: [True] * 4}
        stack, leaves, backing = [start], [], False
        while stack:
            current = stack[-1]
            x, y = current % size, current // size
            for index in sorted(range(4), key=lambda _: rng.next()):
                dx, dy = tuple(world.vectors.values())[index]
                nx, ny = x + dx, y + dy
                target = nx + size * ny
                if 0 <= nx < size and 0 <= ny < size and target not in walls:
                    stack.append(target)
                    walls[target] = [True] * 4
                    walls[target][(index + 2) % 4] = False
                    walls[current][index] = False
                    backing = False
                    break
            if stack[-1] == current:
                stack.pop()
                if not backing:
                    leaves.append(current)
                    backing = True
        treasure = leaves[rng.next(len(leaves) - 1)]
        self.walls = {(self.origin[0] + i % size, self.origin[1] + i // size): value for i, value in walls.items()}
        self.treasure = (self.origin[0] + treasure % size, self.origin[1] + treasure // size)
        self.next_pos = self.treasure
        self.factor = 1
        self.relocate_at = None
        self.removed = False
        # 先清理重叠旧实体/迷宫，再安装新迷宫，防止新旧对象相互删除。
        for p in self.walls:
            world.remove(p, regrow=False)
        for p in sorted(self.walls):
            world.grounds[p] = Grounds.Grassland
            tile = world.set_entity(p, Entities.Treasure if p == self.treasure else Entities.Hedge)
            tile.maze = self
        self.choose_next()

    def choose_next(self):
        if self.size <= 1:
            return
        rng = self.world.rng['maze']
        while True:
            self.next_pos = (self.origin[0] + rng.next(self.size), self.origin[1] + rng.next(self.size))
            if self.next_pos != self.treasure:
                return

    def reward(self):
        return self.size ** 2 * self.world.yield_factor(Entities.Treasure)

    def reuse(self, desired_size):
        if self.size <= 1 or desired_size < self.size or self.factor >= 301:
            return False, 1
        if self.relocate_at is not None:
            return False, 200
        self.world.add_item(Items.Gold, self.reward())
        self.relocate_at = self.world.now_ns + 200 * self.world.tick_ns
        return True, 200

    def relocate(self):
        """保留墙和累计再利用次数；随机开墙按原版棋盘奇偶顺序抽样。"""
        self.relocate_at = None
        if self.removed:
            return
        old = self.world.entities[self.treasure]
        target = self.world.entities[self.next_pos]
        old.kind, target.kind = Entities.Hedge, Entities.Treasure
        self.treasure = self.next_pos
        self.factor += 1
        self.choose_next()
        rng = self.world.rng['maze']
        for pos in sorted(self.walls):
            if sum(pos) % 2:
                continue
            for i, direction in enumerate(Direction):
                neighbor = self.world.neighbor(pos, direction)
                if rng.double() <= 0.002 and neighbor in self.walls:
                    self.walls[pos][i] = False
                    self.walls[neighbor][(i + 2) % 4] = False

    def remove(self):
        """移除任意树篱都会清除整块迷宫，随后按地面恢复草。"""
        if self.removed:
            return
        self.removed = True
        if self in self.world.mazes:
            self.world.mazes.remove(self)
        for pos in sorted(self.walls):
            crop = self.world.entities.get(pos)
            if crop is not None and crop.maze is self:
                crop.maze = None
                self.world.remove(pos)


class Dinosaur:
    """唯一恐龙帽子的尾巴与苹果；吃苹果发生在离开旧格时。"""

    def __init__(self, world, owner):
        self.world = world
        self.owner = owner
        self.tail = deque()
        self.target = None
        self.ops = 400
        if world.overplantable(world.entities.get(world.pos)) and world.pay(world.cost(Entities.Apple)):
            self.target = world.set_entity(world.pos, Entities.Apple)
            self.choose_target()

    def choose_target(self):
        """按原版分别抽x/y并拒绝苹果/尾巴格；无空格时停止避免无界重抽。"""
        world = self.world
        if self.target is None:
            raise RuntimeError('没有苹果时不能选择下一个目标')
        if world.size <= 1:
            self.target.number = None
            return
        if world.snake_counts[Entities.Apple] + world.snake_counts[Entities.Dinosaur] == world.width * world.size:
            self.target.number = None
            return
        for _ in range(100000):
            pos = (world.rng['snake'].next(world.width), world.rng['snake'].next(world.size))
            crop = world.entities.get(pos)
            if crop is None or crop.kind not in (Entities.Apple, Entities.Dinosaur):
                self.target.number = pos
                return
        raise RuntimeError('苹果位置重抽超过本地上限')

    def move(self, old, new):
        world = self.world
        ate = self.target is not None and self.target.pos == old and world.entities.get(old) is self.target
        max_tail = world.width * world.size - 2
        if ate:
            pos = self.target.number
            if len(self.tail) < max_tail and pos is not None and world.overplantable(world.entities.get(pos)) and world.pay(world.cost(Entities.Apple)):
                self.target = world.set_entity(pos, Entities.Apple)
                self.choose_target()
                self.ops -= self.ops * 3 // 100
            else:
                self.target = None
        if ate or self.tail:
            segment = world.set_entity(old, Entities.Dinosaur, internal=True)
            world.grounds[old] = Grounds.Soil
            if self.tail and not ate:
                last = self.tail.pop()
                world.remove(last.pos, internal=True)
            self.tail.appendleft(segment)
            if len(self.tail) < max_tail and len(self.tail) > 1 and world.entities.get(new) is not self.target:
                self.tail[-1].passable = True
        for _ in range(100000):
            if self.target is None or self.target.number != old or len(self.tail) >= max_tail:
                return self.ops
            self.choose_target()
        raise RuntimeError('苹果目标重抽超过本地上限')

    def finish(self):
        """换帽或破坏尾巴时结算当前棋盘的恐龙数量平方，然后清理尾巴和苹果。"""
        world = self.world
        world.dinosaur = None
        if self.tail:
            count = world.snake_counts[Entities.Dinosaur]
            world.add_item(Items.Bone, count * count * world.yield_factor(Entities.Dinosaur))
        for segment in self.tail:
            world.remove(segment.pos, internal=True)
        if self.target is not None:
            world.remove(self.target.pos, internal=True)
        self.tail.clear()
