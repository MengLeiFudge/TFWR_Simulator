"""有界运行受支持的游戏脚本；CPython 执行控制流，世界负责 API 机制。"""

import argparse
import ast
import hashlib
from functools import lru_cache
import json
import multiprocessing
from pathlib import Path
import sys
import time

from .world import FarmWorld, UnsupportedMechanism
from .catalog import Direction, Entities, Grounds, Items, Hats, Unlocks, Leaderboards
from .language import BUILTINS
from .execution import Api, Drone, Request, Scheduler, API_NAMES, compile_script, dispatch, elapsed, evaluate


class BudgetExceeded(RuntimeError):
    pass


ALLOWED_NODES = (
    ast.Module, ast.Global, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Assign,
    ast.AugAssign, ast.Expr, ast.If, ast.For, ast.While, ast.Break, ast.Continue,
    ast.Pass, ast.Name, ast.Constant, ast.Load, ast.Store, ast.Call, ast.keyword,
    ast.Attribute, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Subscript, ast.Slice,
    ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or, ast.Eq, ast.NotEq,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
)


def load_script(path: Path):
    """移除游戏类型提示导入；其余不支持语法在执行前拒绝。不是安全沙箱。"""
    source = path.read_text(encoding='utf-8-sig')
    return compile_source(source, str(path))


@lru_cache(maxsize=16)
def compile_source(source, filename):
    """以源码内容和路径为键复用编译产物；源码变化自动失效，每轮执行环境仍独立。"""
    path = Path(filename)
    tree = ast.parse(source, filename=filename)
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module == '__builtins__'
        and node.level == 0 and len(node.names) == 1 and node.names[0].name == '*')]
    attributes = {value.name for enum in (Entities, Grounds, Items, Hats, Unlocks, Leaderboards) for value in enum}
    attributes.update(('append', 'pop', 'add', 'insert', 'remove'))
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise UnsupportedMechanism(f'第 {getattr(node, "lineno", "?")} 行：尚未支持 {type(node).__name__}')
        if isinstance(node, ast.Attribute) and (node.attr.startswith('_') or node.attr not in attributes):
            raise UnsupportedMechanism(f'第 {node.lineno} 行：尚未支持属性 {node.attr}')
        names = ([node.id] if isinstance(node, ast.Name) else [node.name] if isinstance(node, ast.FunctionDef)
                 else [node.arg] if isinstance(node, ast.arg) else node.names if isinstance(node, ast.Global) else [])
        reserved = {'_budget', '_dispatch', '_Request', '_elapsed', '_operation', '_slice', '_missing', '_entry'}
        if any(name in reserved or name.startswith('_timing_') for name in names):
            raise UnsupportedMechanism(f'第 {getattr(node, "lineno", "?")} 行：名称与本地执行器保留名称冲突')
        if isinstance(node, ast.Name) and node.id.startswith('__') and node.id != '__name__':
            raise UnsupportedMechanism(f'第 {node.lineno} 行：不支持名称 {node.id}')
        if isinstance(node, ast.FunctionDef) and (node.decorator_list or node.returns):
            raise UnsupportedMechanism(f'第 {node.lineno} 行：不支持装饰器或返回类型注解')
    return compile_script(tree, path), hashlib.sha256(source.encode()).hexdigest()


def run_script(path: Path, seed=1, max_calls=100000, max_steps=2000000, seconds=10.0, trace=None, scenario=None):
    """返回预测报告；CLI 另用子进程墙钟限制兜住 C 层长操作。"""
    started = time.monotonic()
    deadline = started + seconds
    code, source_hash = load_script(path)
    world = FarmWorld(seed, scenario)
    trace_hash = hashlib.sha256() if trace else None
    calls = 0
    steps = 0
    last_line = None
    trace_file = None

    def check():
        """执行副作用之前检查预算，避免上限之外多扣一次资源。"""
        nonlocal calls
        if calls >= max_calls:
            raise BudgetExceeded(f'达到 API 调用上限 {max_calls}')
        if time.monotonic() >= deadline:
            raise BudgetExceeded(f'达到墙钟上限 {seconds:g}s')
        calls += 1

    def observe(drone, request, result, _ticks):
        """记录调用时刻及预计返回时刻，避免并行动作被错误地累加到墙钟。"""
        entity = world.entities.get(world.pos)
        row = {'index': calls, 'drone': drone.id, 'api': request.name,
               'args': request.args, 'result': result,
               'pos': world.pos, 'cactus': world.items[Items.Cactus],
               'pumpkin': world.items[Items.Pumpkin],
               'number': getattr(entity, 'number', None),
               'grown': getattr(entity, 'grown', None),
               'api_ticks': world.ticks, 'api_time_ns': world.now_ns,
               'ready_ns': world.now_ns + (drone.ticks - scheduler.global_ticks) * world.tick_ns}
        def encode(value):
            if isinstance(value, Drone):
                return {'drone_id': value.id}
            if callable(value):
                return {'function': value.__name__}
            if isinstance(value, set):
                return sorted(value, key=str)
            raise TypeError(f'轨迹不支持的值：{type(value).__name__}')
        encoded = json.dumps(row, ensure_ascii=False, separators=(',', ':'), default=encode) + '\n'
        assert trace_hash is not None
        trace_hash.update(encoded.encode())
        if trace_file:
            trace_file.write(encoded)

    env = {'__builtins__': BUILTINS, '__name__': '__main__', '_missing': object(),
           'Entities': Entities, 'Grounds': Grounds, 'Items': Items,
           'Hats': Hats, 'Unlocks': Unlocks, 'Leaderboards': Leaderboards,
           '_dispatch': dispatch, '_Request': Request,
           '_elapsed': elapsed, '_operation': evaluate, '_slice': slice}
    env.update({d.value: d for d in Direction})
    for name in dir(world):
        if name.startswith('api_'):
            env[name[4:]] = Api(name[4:])
    env.update({name: Api(name) for name in API_NAMES})
    scheduler = Scheduler(world, observe if trace else None, check)

    def budget(line):
        """编译检查点限制源语句与循环次数；API检查和父进程另行兜住墙钟。"""
        nonlocal steps, last_line
        steps += 1
        last_line = line
        if steps > max_steps:
            raise BudgetExceeded(f'达到脚本执行步数上限 {max_steps}')
        if steps % 1024 == 0 and time.monotonic() >= deadline:
            raise BudgetExceeded(f'达到墙钟上限 {seconds:g}s')
        return True

    env['_budget'] = budget

    status = 'completed'
    error = None
    try:
        if trace:
            trace_file = Path(trace).open('w', encoding='utf-8', newline='\n')
        exec(code, env)
        scheduler.run(env['_entry'])
    except (Exception, KeyboardInterrupt) as exc:
        status = 'stopped'
        error = {'type': type(exc).__name__, 'message': str(exc), 'line': last_line}
    finally:
        if trace_file:
            trace_file.close()
    return {
        'kind': 'prediction', 'status': status, 'error': error,
        'scenario': scenario or 'max_unlocks', 'script': str(path),
        'script_sha256': source_hash, 'seed': seed, 'stream_seeds': world.seeds,
        'goal_reached': world.items[world.goal[0]] >= world.goal[1] if world.goal else None,
        'api_ticks': world.ticks, 'tick_ns': world.tick_ns,
        'predicted_game_seconds': world.now_ns / 1000000000,
        'predicted_api_seconds': world.now_ns / 1000000000,
        'interpreter_ticks': world.costs.get('_ops', 0), 'script_steps': steps, 'step_basis': 'compiled_checkpoint',
        'api_calls': {k:v for k,v in world.calls.items() if k != '_ops'},
        'api_ticks_by_function': {k:v for k,v in world.costs.items() if k != '_ops'},
        'estimated_loop_ticks': 0,
        'state': world.snapshot(), 'harvests': world.harvests,
        'trace_sha256': trace_hash.hexdigest() if trace_hash else None, 'output': scheduler.outputs,
        'warnings': world.warnings,
        'wall_seconds': time.monotonic() - started,
        'limitations': [
            '全作物主要机制采用原版参数；成熟共享随机事件和罕见交互不保证逐次一致。',
            '脚本操作及199t无人机批次按原版规则实现；语言边界与单seed精度仍需实机对照。',
            '水分、成熟和Power使用定时事件；长窗口同seed精度尚待真实游戏对照。',
            'simulate/leaderboard_run 只实现模拟内部拒绝递归入口；真实启动仍由协调器负责。',
            '预测不是实测成绩；靠近成熟边界或依赖 get_time/get_tick_count 的策略须实机对照。',
        ],
    }


def worker(connection, options, seeds=None):
    """同一隔离进程按seed顺序复用编译缓存；批次共享墙钟上限，不复用世界状态。"""
    try:
        if seeds is None:
            connection.send(run_script(**options))
        else:
            completed = 0
            succeeded = True
            deadline = time.monotonic() + options['seconds']
            for seed in seeds:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                current = dict(options, seed=seed, seconds=remaining)
                if current.get('trace'):
                    trace = Path(current['trace'])
                    current['trace'] = trace.with_name(f'{trace.stem}.seed-{seed}{trace.suffix}')
                report = run_script(**current)
                completed += 1
                succeeded = succeeded and report['status'] == 'completed'
                connection.send({'seed_report': report})
                print(f'local_simulator completed={completed}/{len(seeds)} seed={seed}', file=sys.stderr, flush=True)
            connection.send({'kind': 'prediction_batch', 'seeds': seeds,
                             'status': 'completed' if completed == len(seeds) and succeeded else 'stopped'})
    except Exception as exc:
        connection.send({'kind': 'prediction', 'status': 'stopped',
                         'error': {'type': type(exc).__name__, 'message': str(exc)}})
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description='本地运行农场 API 脚本，输出预测而非真实榜单成绩')
    parser.add_argument('script', type=Path)
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument('--seed', type=int, default=1)
    seed_group.add_argument('--seeds', type=int, nargs='+', help='顺序运行1～100个不同seed，复用编译缓存；共享timeout预算')
    parser.add_argument('--scenario', type=Path, help='JSON：preset=max/reset、items库存、unlocks等级及可选goal目标')
    parser.add_argument('--trace', type=Path, help='写入逐 API JSONL；会覆盖指定文件')
    parser.add_argument('--output', type=Path, help='写入 JSON 报告；会覆盖指定文件')
    parser.add_argument('--max-api-calls', type=int, default=100000)
    parser.add_argument('--max-steps', type=int, default=2000000, help='编译后源语句/循环预算检查点上限，不是游戏tick')
    parser.add_argument('--timeout', type=float, default=10, help='整个工作进程的墙钟上限，默认 10 秒')
    args = parser.parse_args()
    seeds = args.seeds or [args.seed]
    if len(seeds) > 100 or len(set(seeds)) != len(seeds) or any(not 0 <= seed <= 2147483647 for seed in seeds):
        parser.error('seeds须为1～100个不同的非负Int32')
    if not (0 <= args.seed <= 2147483647 and 0 < args.timeout <= 60
            and args.max_api_calls > 0 and args.max_steps > 0):
        parser.error('seed 须为非负 Int32，timeout 须在 (0, 60] 内，调用/步数上限须为正数')
    paths = [p.resolve() for p in (args.script, args.scenario, args.trace, args.output) if p is not None]
    if args.trace and args.seeds:
        paths.extend(args.trace.with_name(f'{args.trace.stem}.seed-{seed}{args.trace.suffix}').resolve() for seed in seeds)
    if len(paths) != len(set(paths)):
        parser.error('脚本、轨迹和报告必须使用不同文件')
    options = {'path': args.script.resolve(), 'seed': args.seed, 'trace': args.trace,
               'max_calls': args.max_api_calls, 'max_steps': args.max_steps, 'seconds': args.timeout,
               'scenario': json.loads(args.scenario.read_text()) if args.scenario else None}
    context = multiprocessing.get_context('spawn')
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(child, options, args.seeds))
    process.start()
    child.close()
    reports = []
    deadline = time.monotonic() + args.timeout
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not parent.poll(remaining):
                report = {'kind': 'prediction', 'status': 'stopped', 'error': f'工作进程超过 {args.timeout:g}s，已终止'}
                break
            try:
                message = parent.recv()
            except EOFError:
                report = {'kind': 'prediction', 'status': 'stopped', 'error': '工作进程异常退出'}
                break
            if 'seed_report' in message:
                reports.append(message['seed_report'])
            else:
                report = message
                break
    finally:
        parent.close()
        process.join(timeout=0.2)
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join(timeout=1)
    if args.seeds:
        report = {**report, 'kind': 'prediction_batch', 'seeds': args.seeds,
                  'reports': reports, 'completed_seeds': len(reports)}
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return 0 if report['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
