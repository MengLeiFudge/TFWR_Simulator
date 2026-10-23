"""在 API 边界协作调度无人机；脚本作用域复制，棋盘共享，动作时间重叠。"""

import ast
import copy
from dataclasses import dataclass
from collections.abc import Generator
import inspect
import types

from .catalog import Hats, Items, Leaderboards, Unlocks
from .language import game_str, BUILTINS
from .randomness import MonoRandom


@dataclass(frozen=True)
class Api:
    name: str


@dataclass
class Request:
    name: str
    args: tuple


@dataclass(eq=False)
class Drone:
    """句柄在任务结束后仍保留返回值；ready 是下一次运行的游戏纳秒。"""
    id: int
    task: Generator
    rng: MonoRandom
    pos: tuple = (0, 0)
    hat: Hats = Hats.Straw_Hat
    ready: int = 0
    result: object = None
    done: bool = False
    cancelled: bool = False
    waiting: object = None
    response: object = None
    owner: object = None

    def __deepcopy__(self, _memo):
        # 句柄身份可跨作用域传递，任务和完成状态不能被复制成另一个无人机。
        return self


class Calls(ast.NodeTransformer):
    """把普通调用改成可暂停调用；每个用户函数都变为协程，包括无 API 的函数。"""

    def visit_Call(self, node):
        self.generic_visit(node)
        return ast.copy_location(ast.YieldFrom(ast.Call(
            ast.Name('_dispatch', ast.Load()), [node.func, *node.args], node.keywords)), node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.body.insert(0, ast.If(ast.Constant(False), [ast.Expr(ast.Yield(ast.Constant(None)))], []))
        return node

    def visit_While(self, node):
        """每次循环给一个近似脚本tick，让无动作的成熟/时钟等待能推进。"""
        self.generic_visit(node)
        step = ast.Expr(ast.Yield(ast.Call(ast.Name('_Request', ast.Load()),
                             [ast.Constant('_step'), ast.Tuple([], ast.Load())], [])))
        node.body.insert(0, ast.copy_location(step, node))
        return node

    visit_For = visit_While

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
    if bindings.names:
        tree.body.insert(0, ast.Global(sorted(bindings.names)))
    entry = ast.FunctionDef('_entry', ast.arguments(posonlyargs=[], args=[], kwonlyargs=[],
                           kw_defaults=[], defaults=[]), tree.body, [], returns=None, type_params=[])
    tree.body = [entry]
    tree = Calls().visit(tree)
    return compile(ast.fix_missing_locations(tree), str(path), 'exec')


def dispatch(function, *args, **kwargs):
    """API 交给调度器，用户函数串接协程，纯 Python 内建仍同步执行。"""
    if isinstance(function, Api):
        if kwargs:
            raise TypeError('游戏 API 不接受关键字参数')
        return (yield Request(function.name, args))
    owner = getattr(function, '__self__', None)
    name = getattr(function, '__name__', '')
    if isinstance(owner, (list, set, dict)) and name in ('append', 'pop', 'insert', 'remove', 'add'):
        result = BUILTINS[name](owner, *args, **kwargs)
    else:
        result = function(*args, **kwargs)
    if inspect.isgenerator(result):
        return (yield from result)
    return result


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
    """按下一次可运行时间排序；wait_for 阻塞调用者，不阻塞其他无人机。"""

    def __init__(self, world, observe, check):
        self.world = world
        self.observe = observe
        self.check = check
        self.main = None
        self.active = {}
        self.next_id = 1
        self.handle_owner = object()
        self.outputs = []

    def run(self, entry):
        self.main = Drone(0, entry(), self.world.script_rng, owner=self.handle_owner)
        self.active = {0: self.main}
        try:
            while self.active:
                ready = [d for d in self.active.values() if d.waiting is None]
                if not ready:
                    raise RuntimeError('无人机相互等待，无法继续')
                drone = min(ready, key=lambda d: (d.ready, d.id))
                self.world.advance_to(max(self.world.now_ns, drone.ready))
                self.world.current_drone = drone.id
                self.world.pos, self.world.script_rng = drone.pos, drone.rng
                try:
                    request = drone.task.send(drone.response)
                except StopIteration as end:
                    self.finish(drone, end.value)
                    continue
                if not isinstance(request, Request):
                    raise TypeError('脚本产生了无效调度请求')
                if request.name != '_step':
                    self.check()
                old_tick = self.world.tick_ns
                result, ticks = self.invoke(drone, request.name, request.args)
                self.world.consume_power(ticks)
                if old_tick != self.world.tick_ns:
                    for other in self.active.values():
                        remaining = max(0, other.ready - self.world.now_ns) / old_tick
                        other.ready = self.world.now_ns + round(remaining * self.world.tick_ns)
                self.world.calls[request.name] += 1
                self.world.costs[request.name] += ticks
                drone.pos, drone.hat = self.world.pos, self.world.hat
                drone.response = result
                drone.ready = self.world.now_ns + ticks * self.world.tick_ns
                if request.name != '_step' and self.observe is not None:
                    self.observe(drone, request, result, ticks)
        finally:
            for drone in self.active.values():
                drone.task.close()

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
                waiter.ready = max(waiter.ready, self.world.now_ns)

    def invoke(self, drone, name, args):
        world = self.world
        if name == '_step':
            return None, 1
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
            child = Drone(self.next_id, function(*params),
                          MonoRandom(world.random_rng.sample_int()), world.pos,
                          ready=world.now_ns + 200 * world.tick_ns, owner=self.handle_owner)
            self.next_id += 1
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
