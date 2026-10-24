"""共享农田、全部实体与资源时间；特殊状态机由 special 模块持有。"""

from collections import Counter
from dataclasses import dataclass
import hashlib
import math
import struct

from .catalog import Direction, Entities, Grounds, Items, Hats, Unlocks, UNLOCK_DATA, VECTORS, CROPS, OBJECTS
from .randomness import MonoRandom, stream_seeds
from .special import Dinosaur, Maze, merge_pumpkin, update_pumpkin_squares
from .clock import Timers


def float32(value):
    """原版作物随机倍率的每一步使用Single精度。"""
    return struct.unpack('<f', struct.pack('<f', value))[0]


class UnsupportedMechanism(ValueError):
    """不能可靠预测的脚本语义明确停止，不返回占位成功值。"""


@dataclass(eq=False)
class Plant:
    """一个实际实体；成熟进度是0..1比例，分组/迷宫对象表达共享生命周期。"""
    kind: Entities
    pos: tuple
    seconds: float = 0
    progress: float = 0
    grown: bool = False
    weird: bool = False
    number: object = None
    companion: object = None
    group: object = None
    maze: object = None
    passable: bool = False
    tree_factor: int = 1
    order: int = 0
    random_factor: float = 1
    grow_ns: int = 0
    grow_start: int = 0
    grow_factor: float = 0
    timer: object = None


class FarmWorld:
    """棋盘和资源共享；当前无人机仅选择位置、帽子与脚本随机流。"""

    def __init__(self, seed, scenario=None):
        scenario = scenario or {}
        if not isinstance(scenario, dict) or set(scenario) - {'items', 'unlocks', 'preset', 'goal'}:
            raise ValueError('场景只接受 items、unlocks、preset、goal 字段')
        if scenario.get('preset', 'max') not in ('max', 'reset'):
            raise ValueError('preset 必须是 max 或 reset')
        self.seeds = stream_seeds(seed)
        self.rng = {name: MonoRandom(value) for name, value in self.seeds.items()}
        self.random_rng = self.rng['random']
        self.script_rng = MonoRandom(self.random_rng.next())
        self.cactus_rng = self.rng['cactus']
        self.unlocks = {key: (row['max_unlock_level'] if scenario.get('preset', 'max') == 'max' else 0)
                        for key, row in UNLOCK_DATA.items()}
        if scenario.get('preset') == 'reset':
            self.unlocks['grass'] = 1
        for name, level in scenario.get('unlocks', {}).items():
            key = name.removeprefix('Unlocks.').lower()
            if key not in UNLOCK_DATA or type(level) is not int or not 0 <= level <= UNLOCK_DATA[key]['max_unlock_level']:
                raise ValueError(f'无效科技配置：{name}={level}')
            self.unlocks[key] = level
        self.items = dict.fromkeys(Items, 0)
        if scenario.get('preset', 'max') == 'max':
            self.items.update({Items.Pumpkin: 1000000000, Items.Power: 1000000000})
        for name, amount in scenario.get('items', {}).items():
            item = Items(name if name.startswith('Items.') else 'Items.' + name)
            if type(amount) not in (int, float) or not math.isfinite(amount) or amount < 0:
                raise ValueError(f'无效物品配置：{name}={amount}')
            self.items[item] = amount
        self.goal = None
        if 'goal' in scenario:
            goal = scenario['goal']
            if not isinstance(goal, dict) or set(goal) != {'item', 'amount'} or type(goal['amount']) not in (int, float) or not math.isfinite(goal['amount']) or goal['amount'] <= 0:
                raise ValueError('goal 需要 item 名称与正数 amount')
            self.goal = (Items[goal['item']], goal['amount'])
        self.now_ns = 0
        self.ticks = 0
        self.speed = self.max_speed()
        self.tick_ns = math.ceil(2500000 / self.speed)
        self.pos = (0, 0)
        self.current_drone = 0
        self.hats = {}
        self.dinosaur = None
        self.mazes = []
        self.vectors = VECTORS
        self.water, self.grounds, self.entities, self.cache = {}, {}, {}, {}
        self.timers = Timers()
        self.used_power = 0.0
        self.next_plant_order = 0
        self.pumpkin_squares = {}
        self.sunflower_petals = Counter()
        self.snake_counts = Counter()
        self.calls, self.costs = Counter(), Counter()
        self.harvests, self.warnings = [], []
        self.size_limit = 0
        self.width = self.size = 1
        self.reset_grid()
        self.timers.start(100000000, self.decay_water)
        # 显式科技的原版模拟先应用 Expand 1，再应用最终等级。
        if self.unlocks['expand'] > 0:
            self.width, self.size = 1, 3
            self.reset_grid()
        if self.unlocks['expand'] > 1:
            self.width = self.size = self.max_size()
            self.reset_grid()
        for item, key in ((Items.Water, 'watering'), (Items.Fertilizer, 'fertilizer')):
            self.timers.start(int(20000000000 / (1 << self.unlocks[key])),
                              lambda item=item, key=key: self.receive_supply(item, key))
        self.timers.start(200000000, self.settle_power)

    @property
    def hat(self):
        return self.hats.get(self.current_drone, Hats.Straw_Hat)

    @hat.setter
    def hat(self, value):
        self.hats[self.current_drone] = value

    def max_size(self):
        return (1, 3, 3, 4, 6, 8, 12, 16, 22, 32)[self.unlocks['expand']]

    def max_speed(self):
        return 1.5 ** self.unlocks['speed'] * (2 if self.items[Items.Power] > 0 else 1)

    def in_bounds(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.size

    def neighbor(self, pos, direction, wrap=False):
        if not isinstance(direction, Direction):
            raise UnsupportedMechanism(f'无效方向：{direction!r}')
        dx, dy = VECTORS[direction]
        result = pos[0] + dx, pos[1] + dy
        return (result[0] % self.width, result[1] % self.size) if wrap else result

    def neighbors(self, pos):
        return [self.entities.get(self.neighbor(pos, d)) for d in Direction]

    def reset_grid(self):
        """重建草地但保留范围内水量和仙人掌数字缓存。"""
        if self.dinosaur is not None:
            owner = self.dinosaur.owner
            self.dinosaur.finish()
            self.hats[owner] = Hats.Straw_Hat
        for maze in self.mazes:
            maze.removed = True
            if maze.relocate_timer is not None:
                maze.relocate_timer.stopped = True
        self.mazes.clear()
        for crop in self.entities.values():
            if crop.timer is not None:
                crop.timer.stopped = True
        self.entities.clear()
        self.pumpkin_squares.clear()
        self.sunflower_petals.clear()
        self.snake_counts.clear()
        self.grounds.clear()
        self.water = {pos: value for pos, value in self.water.items() if self.in_bounds(pos)}
        self.cache = {pos: value for pos, value in self.cache.items() if self.in_bounds(pos)}
        for x in range(self.width):
            for y in range(self.size):
                self.grounds[x, y] = Grounds.Grassland
                self.set_entity((x, y), Entities.Grass)

    def choose_companion(self, crop):
        """独立poly流先选位置，再重抽与本作物不同的类型。"""
        rng = self.rng['poly']
        while True:
            dx, dy = rng.next(-3, 4), rng.next(-3, 4)
            pos = ((crop.pos[0] + dx) % self.width, (crop.pos[1] + dy) % self.size)
            if self.size == 1 or (pos != crop.pos and abs(dx) + abs(dy) <= 3):
                break
        kinds = (Entities.Grass, Entities.Bush, Entities.Carrot, Entities.Tree)
        while True:
            kind = kinds[rng.next(4)]
            if kind != crop.kind:
                return kind, pos

    def set_entity(self, pos, kind, internal=False):
        """替换实体，统一处理南瓜组、迷宫和恐龙尾巴的连带删除。"""
        if pos in self.entities:
            self.remove(pos, regrow=False, internal=internal)
        crop = Plant(kind, pos, order=self.next_plant_order)
        self.next_plant_order += 1
        self.entities[pos] = crop
        if kind in (Entities.Apple, Entities.Dinosaur):
            self.snake_counts[kind] += 1
        rng = self.rng['various']
        if OBJECTS[kind]['random_rotation']:
            rng.next(4)
        spec = CROPS.get(kind)
        if spec:
            rng.next(spec['goo_count'] - 1)
            if spec['companion']:
                crop.companion = self.choose_companion(crop)
            deviation = float32(spec['deviation'])
            crop.random_factor = float32(float32(float32(float32(rng.double()) * deviation) * 2) + 1)
            crop.random_factor = float32(crop.random_factor - deviation)
            crop.seconds = float32(spec['seconds']) * crop.random_factor
            if kind == Entities.Cactus:
                if pos not in self.cache:
                    self.cache[pos] = self.rng['cactus'].next(10)
                crop.number = self.cache[pos]
            elif kind == Entities.Sunflower:
                crop.number = self.rng['sunflower'].next(7, 16)
                self.sunflower_petals[crop.number] += 1
            elif kind == Entities.Pumpkin:
                crop.number = int.from_bytes(hashlib.sha256(self.rng['pumpkin'].bytes(16)).digest()[:4], 'little') & 2147483647
        crop.tree_factor = self.tree_penalty(crop)
        self.track_growth(crop)
        if kind == Entities.Tree:
            self.update_neighbors(pos)
        return crop

    def remove(self, pos, regrow=True, internal=False):
        crop = self.entities.get(pos)
        if crop is None:
            return
        if crop.maze is not None and not crop.maze.removed:
            crop.maze.remove()
            return
        if crop.kind == Entities.Dinosaur and not internal and self.dinosaur is not None:
            owner = self.dinosaur.owner
            self.dinosaur.finish()
            self.hats[owner] = Hats.Straw_Hat
            return
        if crop.group is not None:
            x, y, side = crop.group
            positions = [(a, b) for a in range(x, x + side) for b in range(y, y + side)]
            for p in positions:
                member = self.entities.get(p)
                if member is not None:
                    member.group = None
            for p in positions:
                self.remove(p, regrow=regrow, internal=internal)
            return
        self.entities.pop(pos, None)
        if crop.kind in (Entities.Apple, Entities.Dinosaur):
            self.snake_counts[crop.kind] -= 1
        if crop.kind == Entities.Sunflower:
            self.sunflower_petals[crop.number] -= 1
            if self.sunflower_petals[crop.number] == 0:
                del self.sunflower_petals[crop.number]
        if crop.timer is not None:
            crop.timer.stopped = True
        if crop.kind == Entities.Pumpkin and crop.grown:
            update_pumpkin_squares(self, pos)
        if regrow and self.grounds.get(pos) == Grounds.Grassland:
            self.set_entity(pos, Entities.Grass)

    def tree_penalty(self, crop):
        return 2 ** sum(n is not None and n.kind == Entities.Tree for n in self.neighbors(crop.pos)) if crop.kind == Entities.Tree else 1

    def update_neighbors(self, pos):
        # 原版移除实体不通知邻居；种树与成熟事件才刷新邻树的生长计时。
        for neighbor in self.neighbors(pos):
            if neighbor is not None:
                self.track_growth(neighbor)

    def mature(self, crop):
        if crop.grown or self.entities.get(crop.pos) is not crop:
            return
        if crop.timer is not None:
            crop.timer.stopped = True
        crop.progress = 1
        crop.grown = True
        if crop.kind == Entities.Cactus:
            self.cache.pop(crop.pos, None)
        elif crop.kind == Entities.Pumpkin:
            if self.rng['pumpkin'].double() <= 0.2:
                self.set_entity(crop.pos, Entities.Dead_Pumpkin)
            else:
                merge_pumpkin(self, crop)
        self.update_neighbors(crop.pos)

    def growth_progress(self, crop):
        """在已排定的生长区间内读取进度，不引入积分或采样误差。"""
        if crop.grown:
            return 1
        return crop.progress + (self.now_ns - crop.grow_start) / crop.grow_ns if crop.grow_ns else crop.progress

    def sync_growth(self, crop):
        """改变生长条件之前，结算旧定时区间的进度并停止旧事件。"""
        crop.progress = self.growth_progress(crop)
        crop.grow_start = self.now_ns
        if crop.timer is not None:
            crop.timer.stopped = True

    def track_growth(self, crop, force=False):
        """水分或邻树改变倍率时，按Duration截断规则重排成熟事件。"""
        if crop.seconds <= 0 or crop.grown:
            return
        factor = 1 / (1 + 4 * self.water_at(crop.pos)) * self.tree_penalty(crop)
        if not force and crop.timer is not None and factor == crop.grow_factor:
            return
        self.sync_growth(crop)
        crop.grow_factor = factor
        crop.tree_factor = self.tree_penalty(crop)
        crop.grow_ns = int(factor * float32(CROPS[crop.kind]['seconds']) * crop.random_factor * 1000000000)
        delay = int(crop.grow_ns * (1 - crop.progress))
        if delay == 0:
            self.mature(crop)
        else:
            crop.timer = self.timers.start(self.now_ns + delay, lambda: self.mature(crop))

    def decay_water(self):
        """每0.1秒逐格抽取，包括零水格，以保持共享随机流的位置。"""
        rng = self.rng['various']
        for x in range(self.width):
            for y in range(self.size):
                if rng.double() < 0.1:
                    pos = (x, y)
                    water = self.water_at(pos)
                    if water:
                        self.water[pos] = water * 0.99
                        crop = self.entities.get(pos)
                        if crop is not None:
                            self.track_growth(crop)
        self.timers.start(self.now_ns + 100000000, self.decay_water)

    def receive_supply(self, item, key):
        """补给事件触发后才使用当前科技等级安排下一次事件。"""
        if self.unlocks[key] > 0:
            self.items[item] += 1
        self.timers.start(self.now_ns + int(20000000000 / (1 << self.unlocks[key])),
                          lambda: self.receive_supply(item, key))

    def advance_to(self, end):
        """先处理动作完成时刻之前及同刻的事件，再交还脚本执行器。"""
        if end < self.now_ns:
            raise ValueError('模拟时钟不能倒退')
        while (at := self.timers.next_time()) <= end:
            self.ticks += (at - self.now_ns) / self.tick_ns
            self.now_ns = at
            self.timers.pop().callback()
        self.ticks += (end - self.now_ns) / self.tick_ns
        self.now_ns = end

    def consume_power(self, ticks):
        """记录执行操作；Power只在0.2秒定时事件结算。"""
        self.used_power += ticks / 200 / 30

    def settle_power(self):
        """库存不足一次扣款时归零并限速，然后重新开始扣款周期。"""
        power = self.items[Items.Power]
        if power > 0:
            if power >= self.used_power:
                self.items[Items.Power] -= self.used_power
            else:
                self.items[Items.Power] = 0
                if self.speed > self.max_speed():
                    self.speed = self.max_speed()
                    self.tick_ns = math.ceil(2500000 / self.speed)
        self.used_power = 0.0
        self.timers.start(self.now_ns + 200000000, self.settle_power)

    def add_item(self, item, amount):
        """首次获得Power时，只有原本处于速度上限才自动提速。"""
        first_power = item == Items.Power and self.items[item] == 0 and amount > 0
        at_max = self.speed == self.max_speed()
        self.items[item] += amount
        if first_power and at_max:
            self.used_power = 0.0
            self.speed = self.max_speed()
            self.tick_ns = math.ceil(2500000 / self.speed)

    def yield_factor(self, kind):
        return 1 << max(0, self.unlocks.get(OBJECTS[kind]['upgrade'], 0) - 1)

    def cost(self, kind):
        return {Items[name]: value * self.yield_factor(kind) for name, value in OBJECTS[kind]['cost'].items()}

    def pay(self, cost):
        if any(self.items[item] < value for item, value in cost.items()):
            return False
        for item, value in cost.items():
            self.items[item] -= value
        return True

    def overplantable(self, crop):
        return crop is None or OBJECTS[crop.kind].get('overplant', False)

    def is_sorted(self, crop):
        for direction in Direction:
            neighbor = self.entities.get(self.neighbor(crop.pos, direction))
            if neighbor is None or neighbor.kind != Entities.Cactus:
                continue
            if not neighbor.grown:
                return False
            if direction in (Direction.North, Direction.East):
                if neighbor.number < crop.number:
                    return False
            elif neighbor.number > crop.number:
                return False
        return True

    def harvest(self):
        crop = self.entities.get(self.pos)
        if crop is None:
            return False, 1
        if crop.kind in (Entities.Apple, Entities.Dinosaur):
            return True, 200
        if crop.maze is not None:
            if crop.kind == Entities.Treasure:
                self.add_item(Items.Gold, crop.maze.reward())
            crop.maze.remove()
            return True, 200
        if not crop.grown:
            self.remove(self.pos)
            return True, 200
        factor = self.yield_factor(crop.kind)
        positions = [self.pos]
        if crop.kind == Entities.Cactus:
            popped, pending = set(), [self.pos]
            sorted_cacti = {}
            while pending:
                pos = pending.pop()
                current = self.entities.get(pos)
                if pos in popped or current is None or current.kind != Entities.Cactus or not current.grown:
                    continue
                popped.add(pos)
                neighbors = self.neighbors(pos)
                for neighbor in neighbors:
                    if neighbor is None or neighbor.kind != Entities.Cactus:
                        continue
                    if neighbor not in sorted_cacti:
                        sorted_cacti[neighbor] = self.is_sorted(neighbor)
                    if not sorted_cacti[neighbor]:
                        break
                else:
                    # 遍历期间实体不变，排序结果只在这次收获中复用。
                    pending.extend(n.pos for n in neighbors if n is not None and n.kind == Entities.Cactus)
            positions = sorted(popped)
            per_plant = len(positions) * factor
        elif crop.kind == Entities.Pumpkin:
            x, y, side = crop.group
            positions = [(a, b) for a in range(x, x + side) for b in range(y, y + side)]
            per_plant = min(side, 6) * factor
        else:
            per_plant = CROPS[crop.kind]['amount'] * factor
            if crop.companion:
                kind, pos = crop.companion
                companion = self.entities.get(pos)
                if companion is not None and companion.kind == kind:
                    per_plant *= 5 << self.unlocks['polyculture']
            if crop.kind == Entities.Sunflower:
                if sum(self.sunflower_petals.values()) >= 10 and crop.number == max(self.sunflower_petals):
                    per_plant *= 8
        weird = sum(self.entities[p].weird for p in positions)
        goo = math.floor(0.5 * weird * per_plant)
        gain = len(positions) * per_plant - goo
        self.add_item(Items[CROPS[crop.kind]['drop']], gain)
        self.add_item(Items.Weird_Substance, goo)
        self.harvests.append({'at_ns':self.now_ns, 'entity':crop.kind.value, 'plants':len(positions), 'gain':gain})
        for pos in positions:
            member = self.entities.get(pos)
            if member is not None:
                member.group = None
        for pos in positions:
            self.remove(pos)
        return True, 200

    def apply(self, name, *args):
        method = getattr(self, 'api_' + name, None)
        if method is None:
            raise UnsupportedMechanism(f'尚未实现 API：{name}')
        result, ticks = method(*args)
        self.calls[name] += 1
        self.costs[name] += ticks
        if name not in ('do_a_flip', 'pet_the_piggy'):
            self.consume_power(ticks)
        self.advance_to(self.now_ns + ticks * self.tick_ns)
        return result

    def api_set_world_size(self, size):
        if type(size) not in (int, float) or not math.isfinite(size):
            raise ValueError('set_world_size 需要有限数值')
        size = int(size)
        if size != self.size:
            self.pos = (0, 0)
            self.size_limit = size if size > 2 else 0
            actual = min(self.max_size(), self.size_limit) if self.size_limit else self.max_size()
            width = 1 if self.unlocks['expand'] == 1 and actual == 3 else actual
            if (width, actual) != (self.width, self.size):
                self.width, self.size = width, actual
                self.reset_grid()
        return None, 200

    def api_clear(self):
        self.pos = (0, 0)
        self.reset_grid()
        return None, 200

    def api_can_move(self, direction):
        pos = self.neighbor(self.pos, direction)
        if self.hat == Hats.Dinosaur_Hat and not self.in_bounds(pos):
            return False, 1
        pos = self.neighbor(self.pos, direction, wrap=True)
        here, there = self.entities.get(self.pos), self.entities.get(pos)
        index = tuple(Direction).index(direction)
        if here is not None and here.maze is not None and here.maze.walls[self.pos][index]:
            return False, 1
        if there is not None:
            if there.kind == Entities.Dinosaur and not there.passable:
                return False, 1
            if there.maze is not None and there.maze.walls[pos][(index + 2) % 4]:
                return False, 1
        return True, 1

    def api_move(self, direction):
        if not self.api_can_move(direction)[0]:
            return False, 1
        dest = self.neighbor(self.pos, direction, wrap=True)
        ticks = 200
        if self.dinosaur is not None and self.dinosaur.owner == self.current_drone:
            ticks = self.dinosaur.move(self.pos, dest)
        self.pos = dest
        return True, ticks

    def api_swap(self, direction):
        dest = self.neighbor(self.pos, direction)
        if not self.in_bounds(dest):
            return False, 1
        here, there = self.entities.get(self.pos), self.entities.get(dest)
        if any(c is not None and c.kind != Entities.Cactus for c in (here, there)):
            return False, 1
        a, b = self.cache.pop(self.pos, None), self.cache.pop(dest, None)
        if a is not None:
            self.cache[dest] = a
        if b is not None:
            self.cache[self.pos] = b
        self.entities.pop(self.pos, None)
        self.entities.pop(dest, None)
        for crop, pos in ((here, dest), (there, self.pos)):
            if crop is not None:
                crop.pos = pos
                self.entities[pos] = crop
        # 重排可能立即成熟；此时两个目标格都必须已安装到棋盘。
        for crop in (here, there):
            if crop is not None:
                self.track_growth(crop)
        return True, 200

    def api_till(self):
        crop = self.entities.get(self.pos)
        if crop is None or crop.maze is None:
            self.remove(self.pos, regrow=False)
        if self.grounds[self.pos] == Grounds.Soil:
            self.grounds[self.pos] = Grounds.Grassland
            if crop is None or crop.maze is None:
                self.set_entity(self.pos, Entities.Grass)
        else:
            self.grounds[self.pos] = Grounds.Soil
        return None, 200

    def api_plant(self, kind):
        if not isinstance(kind, Entities):
            raise UnsupportedMechanism(f'无效实体：{kind}')
        if kind not in CROPS or not self.overplantable(self.entities.get(self.pos)):
            return False, 1
        if self.grounds[self.pos].name not in CROPS[kind]['grounds']:
            return False, 1
        if self.api_num_unlocked(kind)[0] < 1:
            raise ValueError(f'尚未解锁：{kind}')
        if not self.pay(self.cost(kind)):
            return False, 1
        self.set_entity(self.pos, kind)
        return True, 200

    def api_harvest(self):
        return self.harvest()

    def api_measure(self, direction=None):
        pos = self.pos if direction is None else self.neighbor(self.pos, direction, wrap=True)
        crop = self.entities.get(pos)
        return (crop.maze.treasure if crop and crop.maze else crop.number if crop else None), 1

    def api_can_harvest(self):
        crop = self.entities.get(self.pos)
        return bool(crop and (crop.grown or crop.kind in (Entities.Hedge, Entities.Treasure, Entities.Dinosaur))), 1

    def api_get_entity_type(self):
        crop = self.entities.get(self.pos)
        return crop.kind if crop else None, 1

    def api_get_ground_type(self):
        return self.grounds[self.pos], 1

    def api_get_pos_x(self):
        return self.pos[0], 1

    def api_get_pos_y(self):
        return self.pos[1], 1

    def api_get_world_size(self):
        return self.size, 1

    def api_num_items(self, item):
        if not isinstance(item, Items):
            raise UnsupportedMechanism(f'无效库存类型：{item}')
        return self.items[item], 1

    def api_get_time(self):
        return self.now_ns / 1000000000, 0

    def api_get_tick_count(self):
        return round(self.ticks), 0

    def api_random(self):
        return self.script_rng.double(), 1

    def water_at(self, pos):
        """读取最近一次定时衰减后的水量，不消耗随机数或改变时间。"""
        return self.water.get(pos, 0.0)

    def api_get_water(self):
        return self.water_at(self.pos), 1

    def api_use_item(self, item, amount=1):
        if not isinstance(item, Items) or type(amount) not in (int, float):
            raise ValueError('use_item 需要物品和数值数量')
        amount = int(amount)
        if amount < 1:
            raise ValueError('use_item 数量必须至少为1')
        if self.items[item] < amount:
            return False, 1
        crop = self.entities.get(self.pos)
        if item == Items.Water:
            self.water[self.pos] = min(1, self.water_at(self.pos) + 0.25 * amount)
            if crop is not None:
                self.track_growth(crop)
        elif item == Items.Fertilizer:
            if crop is None or crop.kind not in CROPS:
                return False, 1
            self.sync_growth(crop)
            crop.weird = True
            crop.tree_factor = self.tree_penalty(crop)
            factor = 1 / (1 + 4 * self.water_at(self.pos)) * crop.tree_factor
            duration = int(factor * float32(CROPS[crop.kind]['seconds']) * crop.random_factor * 1000000000)
            crop.progress = min(crop.progress + 2000000000 * amount / duration, 1)
            self.track_growth(crop, force=True)
        elif item == Items.Weird_Substance:
            size = amount // (1 << max(0, self.unlocks['mazes'] - 1))
            if crop and crop.kind == Entities.Bush and self.unlocks['mazes'] > 0 and size > 0:
                self.mazes.append(Maze(self, self.pos, size))
            elif crop and crop.kind == Entities.Treasure and self.unlocks['mazes'] > 0:
                success, ticks = crop.maze.reuse(size)
                if success:
                    self.items[item] -= amount
                return success, ticks
            elif crop and crop.kind in CROPS:
                for target in [crop, *self.neighbors(self.pos)]:
                    if target is not None and target.kind in CROPS:
                        target.weird = not target.weird
                        self.rng['various'].next(CROPS[target.kind]['goo_count'] - 1)
                # 原版Bush不足迷宫单位时切换感染，但返回False且不扣款。
                if crop.kind == Entities.Bush and self.unlocks['mazes'] > 0:
                    return False, 1
            else:
                return False, 1
        else:
            return False, 1
        self.items[item] -= amount
        return True, 200

    def api_get_companion(self):
        crop = self.entities.get(self.pos)
        return crop.companion if crop else None, 1

    def api_get_cost(self, kind, level=None):
        if isinstance(kind, Unlocks):
            key = kind.name.lower()
            current = self.unlocks[key] if level is None or level < 0 else int(level)
            rows = UNLOCK_DATA[key]['levels']
            cost = rows[current]['cost'] if current < len(rows) else {}
            return {Items[name]: value for name, value in cost.items()}, 1
        if not isinstance(kind, Entities) or level is not None:
            raise ValueError('get_cost 需要科技或实体；实体不接受等级参数')
        return self.cost(kind), 1

    def api_num_unlocked(self, kind):
        if not isinstance(kind, (Unlocks, Entities, Items, Hats)):
            raise ValueError('num_unlocked 需要具体枚举')
        key = kind.name.lower()
        if isinstance(kind, Unlocks) or key in self.unlocks:
            return self.unlocks.get(key, 0), 1
        for name, data in UNLOCK_DATA.items():
            for symbol in data['unlocks']:
                threshold = int(symbol[0]) if symbol[0].isdigit() else 1
                if symbol.lstrip('0123456789').lower() == key and self.unlocks[name] >= threshold:
                    return 1, 1
        return int(key in ('straw_hat', 'hay', 'grass')), 1

    def api_unlock(self, kind):
        if not isinstance(kind, Unlocks):
            raise ValueError('unlock 需要 Unlocks 枚举')
        key = kind.name.lower()
        parent = UNLOCK_DATA[key]['parent_unlock']
        if (parent and self.unlocks[parent] < 1) or self.unlocks[key] >= UNLOCK_DATA[key]['max_unlock_level']:
            return False, 1
        cost, _ = self.api_get_cost(kind)
        if not self.pay(cost):
            return False, 1
        was_max = self.speed == self.max_speed()
        self.unlocks[key] += 1
        if key == 'speed' and was_max:
            self.speed = self.max_speed()
            self.tick_ns = math.ceil(2500000 / self.speed)
        if key == 'expand':
            self.size = min(self.max_size(), self.size_limit) if self.size_limit else self.max_size()
            self.width = 1 if self.unlocks['expand'] == 1 else self.size
            self.reset_grid()
        return True, 200

    def api_set_execution_speed(self, speed):
        if type(speed) not in (int, float):
            raise ValueError('set_execution_speed 需要数值')
        self.speed = self.max_speed() if not math.isfinite(speed) or not 0.1 <= speed <= self.max_speed() else speed
        self.tick_ns = math.ceil(2500000 / self.speed)
        return None, 200

    def api_change_hat(self, hat):
        if not isinstance(hat, Hats):
            raise UnsupportedMechanism(f'无效帽子：{hat}')
        if hat == Hats.Dinosaur_Hat and self.unlocks['dinosaurs'] < 1:
            raise ValueError('尚未解锁恐龙帽')
        if self.dinosaur is not None and self.dinosaur.owner == self.current_drone:
            self.dinosaur.finish()
        if hat == Hats.Dinosaur_Hat:
            if self.dinosaur is not None:
                raise ValueError('只能有一台无人机使用恐龙帽')
            self.dinosaur = Dinosaur(self, self.current_drone)
        self.hat = hat
        return None, 200

    def api_do_a_flip(self):
        return None, 1000000000 // self.tick_ns

    def api_pet_the_piggy(self):
        return None, 1000000000 // self.tick_ns

    def snapshot(self):
        """包含全实体和分组状态；board保留原仙人掌数值矩阵以支持历史报告。"""
        return {'size':self.size, 'width':self.width, 'pos':list(self.pos),
                'items':{key.value:value for key,value in self.items.items()}, 'unlocks':self.unlocks,
                'water':{str(pos):self.water_at(pos) for pos in self.water},
                'entities':[{'pos':c.pos,'kind':c.kind.value,'grown':c.grown,'progress':self.growth_progress(c),
                             'number':c.number,'weird':c.weird,'companion':c.companion,'group':c.group}
                            for c in self.entities.values()],
                'board':[[self.entities[x,y].number if (x,y) in self.entities and self.entities[x,y].kind == Entities.Cactus else None
                          for x in range(self.width)] for y in range(self.size)],
                'cactus_draws':self.cactus_rng.draws, 'script_random_draws':self.script_rng.draws,
                'random_draws':{key:rng.draws for key,rng in self.rng.items()}}


# 保留早期证据回放脚本使用的导入名；生产入口使用FarmWorld。
CactusWorld = FarmWorld
