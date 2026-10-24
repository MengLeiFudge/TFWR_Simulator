"""在脚本操作与 API 边界调度无人机；作用域复制，棋盘与时间共享。"""

import ast
import copy
from dataclasses import dataclass
from collections.abc import Generator
import inspect
import math
import types

from .catalog import Hats, Items, Leaderboards, Unlocks
from .language import game_str, BUILTINS
from .randomness import MonoRandom
from .timing import Timing, operation, builtin_cost, equals, compare


@dataclass(frozen=True)
class Api:
    name: str


@dataclass
class Request:
    name: str
    args: tuple


@dataclass(eq=False)
class Drone:
    """句柄保留终态；ticks、start_ticks、consumed均为执行器的操作计数。"""
    id: int
    task: Generator
    rng: MonoRandom
    pos: tuple = (0, 0)
    hat: Hats = Hats.Straw_Hat
    result: object = None
    done: bool = False
    cancelled: bool = False
    waiting: object = None
    response: object = None
    owner: object = None
    ticks: int = 0
    start_ticks: int = 0
    consumed: int = 0
    pending: object = None

    def __deepcopy__(self, _memo):
        # 句柄身份可跨作用域传递，任务和完成状态不能被复制成另一个无人机。
        return self


class BudgetChecks(ast.NodeTransformer):
    """在源语句和循环边界计步；检查不yield，也不增加虚拟游戏时间。"""

    @staticmethod
    def call(line):
        return ast.Call(ast.Name('_budget', ast.Load()), [ast.Constant(line)], [])

    def generic_visit(self, node):
        super().generic_visit(node)
        for field, values in ast.iter_fields(node):
            if not isinstance(values, list):
                continue
            statements = []
            for value in values:
                if isinstance(value, ast.stmt) and hasattr(value, 'lineno') and not isinstance(value, ast.Global):
                    statements.append(ast.copy_location(ast.Expr(self.call(value.lineno)), value))
                statements.append(value)
            setattr(node, field, statements)
        if isinstance(node, ast.While):
            node.test = ast.copy_location(ast.BoolOp(ast.And(), [self.call(node.lineno), node.test]), node.test)
        elif isinstance(node, ast.For):
            node.body.insert(0, ast.copy_location(ast.Expr(self.call(node.lineno)), node))
        return node


class Calls(ast.NodeTransformer):
    """把普通调用改成可暂停调用；每个用户函数都变为协程，包括无 API 的函数。"""

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in ('_budget', '_elapsed', '_operation', '_slice'):
            return node
        return ast.copy_location(ast.YieldFrom(ast.Call(
            ast.Name('_dispatch', ast.Load()), [node.func, *node.args], node.keywords)), node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.body.insert(0, ast.If(ast.Constant(False), [ast.Expr(ast.Yield(ast.Constant(None)))], []))
        return node


def compile_script(tree, path):
    """顶层脚本也是一个可暂停任务；不引入真实线程或墙钟等待。"""
    class Bindings(ast.NodeVisitor):
        def __init__(self):
            self.names = set()

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                self.names.add(node.id)

        def visit_FunctionDef(self, node):
            self.names.add(node.name)

    bindings = Bindings()
    bindings.visit(tree)
    tree = Timing().visit(tree)
    if bindings.names:
        tree.body.insert(0, ast.Global(sorted(bindings.names)))
    entry = ast.FunctionDef('_entry', ast.arguments(posonlyargs=[], args=[], kwonlyargs=[],
                           kw_defaults=[], defaults=[]), tree.body, [], returns=None, type_params=[])
    tree.body = [entry]
    tree = BudgetChecks().visit(tree)
    tree = Calls().visit(tree)
    return compile(ast.fix_missing_locations(tree), str(path), 'exec')


def dispatch(function, *args, **kwargs):
    """API交给调度器；用户函数和容器内建分别收取原版调用成本。"""
    if isinstance(function, Api):
        if kwargs:
            raise TypeError('游戏 API 不接受关键字参数')
        return (yield Request(function.name, args))
    if inspect.isgeneratorfunction(function):
        yield Request('_ops', (1,))
        return (yield from function(*args, **kwargs))
    owner = getattr(function, '__self__', None)
    name = next((key for key, value in BUILTINS.items() if value is function),
                getattr(function, '__name__', ''))
    if isinstance(owner, (list, set, dict)) and name in ('append', 'pop', 'insert', 'remove', 'add'):
        args = (owner, *args)
        function = BUILTINS[name]
    before = len(args[0]) if args and isinstance(args[0], (list, set, dict)) else 0
    counter = [0]
    if name == 'remove' and args and isinstance(args[0], list):
        for index, value in enumerate(args[0]):
            if equals(value, args[1], counter):
                counter[0] += len(args[0]) - index - 1
                break
    elif name in ('min', 'max'):
        values = args[0] if len(args) == 1 else args
        iterator = iter(values)
        try:
            best = next(iterator)
        except StopIteration:
            raise ValueError(f'{name} 需要非空序列') from None
        # 原版还会将首项与自身比较一次。
        compare(best, best, counter)
        for value in iterator:
            order = compare(value, best, counter)
            if (order > 0 if name == 'max' else order < 0):
                best = value
    result = function(*args, **kwargs)
    cost = counter[0] if name in ('min', 'max') or (name == 'remove' and isinstance(args[0], list)) else builtin_cost(name, args, result, before)
    return (yield from elapsed(result, cost))


def elapsed(value, ticks):
    """提交已执行操作的成本，恢复后返回原值。"""
    if ticks:
        yield Request('_ops', (ticks,))
    return value


def evaluate(name, *args):
    """运行原版表达式规则，再向调度器提交操作数。"""
    value, ticks = operation(name, *args)
    return (yield from elapsed(value, ticks))


def clone_function(function, args):
    """复制函数闭包及可变参数，保留同一副本内的别名和递归函数关系。"""
    memo = {}

    def clone(value):
        if id(value) in memo:
            return memo[id(value)]
        if isinstance(value, dict):
            result = {}
            memo[id(value)] = result
            result.update((clone(k), clone(v)) for k, v in value.items())
            return result
        if isinstance(value, list):
            result = []
            memo[id(value)] = result
            result.extend(clone(v) for v in value)
            return result
        if isinstance(value, types.FunctionType) and value.__code__.co_filename == function.__code__.co_filename:
            cells = tuple(types.CellType(None) for _ in (value.__closure__ or ()))
            global_env = memo.get(id(value.__globals__))
            owns_globals = global_env is None
            if owns_globals:
                global_env = {'__builtins__': value.__globals__['__builtins__']}
                memo[id(value.__globals__)] = global_env
            result = types.FunctionType(value.__code__, global_env, value.__name__,
                                        None, cells or None)
            memo[id(value)] = result
            if owns_globals:
                global_env.update((key, clone(item)) for key, item in value.__globals__.items())
            for old, new in zip(value.__closure__ or (), cells):
                new.cell_contents = clone(old.cell_contents)
            result.__defaults__ = clone(value.__defaults__)
            return result
        return copy.deepcopy(value, memo)

    return clone(function), clone(args)


class Scheduler:
    """按原版199t批次与无人机编号推进；定时事件先于同刻副作用。"""

    def __init__(self, world, observe, check):
        self.world = world
        self.observe = observe
        self.check = check
        self.main = None
        self.active = {}
        self.global_ticks = 0
        self.handle_owner = object()
        self.outputs = []

    def run(self, entry):
        """操作计数可领先世界时间；到达定时事件之前结束本批执行。"""
        self.main = Drone(0, entry(), self.world.script_rng, owner=self.handle_owner)
        self.active = {0: self.main}
        next_time = 0
        world = self.world
        try:
            while self.active:
                world.advance_to(next_time)
                target = math.floor(self.global_ticks + min(199, (world.timers.next_time() - 1 - world.now_ns) / world.tick_ns))
                while self.active:
                    previous = self.global_ticks
                    for drone in sorted(self.active.values(), key=lambda d: d.id):
                        if drone.pending is None and drone.waiting is None and drone.ticks <= target:
                            self.resume(drone, target)
                    runnable = [d for d in self.active.values() if d.waiting is None]
                    if not runnable:
                        raise RuntimeError('无人机相互等待，无法继续')
                    self.global_ticks = min(d.ticks for d in runnable)
                    reached = min(target, self.global_ticks)
                    world.advance_to(world.now_ns + int((reached - previous) * world.tick_ns))
                    used = sum(d.ticks - d.consumed for d in self.active.values())
                    for drone in self.active.values():
                        drone.consumed = drone.ticks
                    if self.global_ticks <= target:
                        # 副作用可能创建或清除无人机；以当前编号集合的快照逐个处理。
                        for drone in sorted(list(self.active.values()), key=lambda d: d.id):
                            if drone.id not in self.active or drone.waiting is not None or drone.ticks > self.global_ticks:
                                continue
                            request = drone.pending
                            if request is None:
                                continue
                            drone.pending = None
                            if request.name == '_finished':
                                self.finish(drone, request.args[0])
                            else:
                                self.perform(drone, request)
                                used += drone.ticks - drone.consumed
                                drone.consumed = drone.ticks
                    world.consume_power(used)
                    self.global_ticks = min((d.ticks for d in self.active.values() if d.waiting is None), default=target)
                    next_time = world.now_ns + int((self.global_ticks - reached) * world.tick_ns)
                    world.advance_to(world.now_ns + int((min(self.global_ticks, target) - reached) * world.tick_ns))
                    if self.global_ticks > target:
                        break
        finally:
            for drone in self.active.values():
                drone.task.close()

    def resume(self, drone, target):
        """纯操作可以执行到批次边界；世界读写留到共同操作时刻应用。"""
        while drone.ticks <= target:
            try:
                request = drone.task.send(drone.response)
            except StopIteration as end:
                drone.pending = Request('_finished', (end.value,))
                return
            if not isinstance(request, Request):
                raise TypeError('脚本产生了无效调度请求')
            if request.name not in ('_ops', 'get_tick_count', 'quick_print', 'random'):
                drone.pending = request
                return
            self.perform(drone, request)

    def perform(self, drone, request):
        """应用一个调用并登记计费；动画及print操作按原版排除Power消耗。"""
        world = self.world
        world.current_drone = drone.id
        world.pos, world.script_rng = drone.pos, drone.rng
        if request.name != '_ops':
            self.check()
        result, ticks = self.invoke(drone, request.name, request.args)
        world.calls[request.name] += 1
        world.costs[request.name] += ticks
        drone.pos, drone.hat = world.pos, world.hat
        drone.response = result
        drone.ticks += ticks
        if request.name in ('print', 'do_a_flip', 'pet_the_piggy'):
            drone.consumed += ticks
        if request.name != '_ops' and self.observe is not None:
            self.observe(drone, request, result, ticks)

    def finish(self, drone, result):
        drone.done = True
        drone.result = copy.deepcopy(result)
        self.active.pop(drone.id)
        if self.active:
            dinosaur = self.world.dinosaur
            if dinosaur is not None and dinosaur.owner == drone.id:
                dinosaur.finish()
            self.world.hats.pop(drone.id, None)
        if self.main is drone:
            self.main = next(iter(self.active.values()), None)
        for waiter in self.active.values():
            if waiter.waiting is drone:
                waiter.waiting = None
                waiter.response = copy.deepcopy(drone.result)
                waiter.ticks = self.global_ticks

    def invoke(self, drone, name, args):
        world = self.world
        if name == '_ops':
            return None, args[0]
        if name == 'get_tick_count':
            if args:
                raise TypeError('get_tick_count 不接受参数')
            return drone.ticks - drone.start_ticks, 0
        if name in ('quick_print', 'print'):
            if len(self.outputs) >= 100:
                raise RuntimeError('输出超过100条，请减少日志')
            self.outputs.append(' '.join(game_str(v) for v in args)[:4096])
            return None, 0 if name == 'quick_print' else 1000000000 // world.tick_ns
        if name == 'spawn_drone':
            function, *params = args
            if not inspect.isgeneratorfunction(function):
                raise TypeError('spawn_drone 需要脚本函数')
            if len(self.active) >= 2 ** world.unlocks['megafarm']:
                return None, 1
            function, params = clone_function(function, tuple(params))
            child_id = next(index for index in range(len(self.active) + 1) if index not in self.active)
            start = self.global_ticks + 200
            child = Drone(child_id, function(*params),
                          MonoRandom(world.random_rng.sample_int()), world.pos,
                          ticks=start, start_ticks=start, consumed=start, owner=self.handle_owner)
            self.active[child.id] = child
            return child, 200
        if name in ('has_finished', 'wait_for'):
            if len(args) != 1 or not isinstance(args[0], Drone) or args[0].owner is not self.handle_owner:
                raise TypeError(f'{name} 需要当前模拟的无人机句柄')
            target = args[0]
            if name == 'has_finished':
                return target.done and not target.cancelled, 1
            if target.cancelled:
                raise RuntimeError('等待的无人机已被 clear 取消，无法返回结果')
            if target.done:
                return copy.deepcopy(target.result), 1
            drone.waiting = target
            return None, 1
        if name in ('num_drones', 'max_drones'):
            if args:
                raise TypeError(f'{name} 不接受参数')
            return (len(self.active) if name == 'num_drones'
                    else 2 ** world.unlocks['megafarm']), 1
        if name in ('simulate', 'leaderboard_run'):
            # 本地运行器执行的是模拟中的脚本；原版在此环境拒绝递归启动。
            if name == 'simulate':
                if drone is not self.main:
                    raise ValueError('simulate can only be called from the main execution')
                if len(args) != 6 or not isinstance(args[0], str) or not isinstance(args[2], dict) or not isinstance(args[3], dict):
                    raise TypeError('simulate 需要脚本、科技、库存、全局变量、seed、速度六个参数')
                if args[1] is not Unlocks and not isinstance(args[1], (dict, list, tuple, set)):
                    raise TypeError('simulate 科技参数无效')
                if any(not isinstance(k, Items) for k in args[2]):
                    raise TypeError('simulate 库存键必须是 Items')
            elif len(args) != 3 or not isinstance(args[0], Leaderboards) or not isinstance(args[1], str):
                raise TypeError('leaderboard_run 需要榜单、脚本名、速度三个参数')
            world.warnings.append(f'{name}: 模拟内部不能再次启动模拟或排行榜')
            return None, 200
        reset_positions = name == 'set_world_size' and bool(args) and int(args[0]) != world.size
        if name == 'clear':
            self.main = drone
            for other in self.active.values():
                if other is not drone:
                    other.task.close()
                    other.cancelled = True
                    other.done = True
            self.active = {drone.id: drone}
        result, ticks = getattr(world, 'api_' + name)(*args)
        if reset_positions:
            for other in self.active.values():
                other.pos = (0, 0)
        return result, ticks


API_NAMES = ('quick_print', 'print', 'spawn_drone', 'wait_for', 'has_finished',
             'num_drones', 'max_drones', 'simulate', 'leaderboard_run')
