"""有界运行受支持的游戏脚本；CPython 执行控制流，世界负责 API 机制。"""

import argparse
import ast
import hashlib
from contextlib import suppress
from functools import lru_cache
import json
import multiprocessing
from multiprocessing.connection import wait
import os
from pathlib import Path
from typing import Any
import sys
import time

from .world import FarmWorld, UnsupportedMechanism
from .catalog import DATA, Direction, Entities, Grounds, Items, Hats, Unlocks, Leaderboards, UNDERGROUND
from .language import BUILTINS, game_iter
from .execution import Api, Drone, Request, Scheduler, API_NAMES, Module, ReturnedValue, attribute, compile_script, dispatch, elapsed, evaluate


class BudgetExceeded(RuntimeError):
    pass


ALLOWED_NODES = (
    ast.Module, ast.Global, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Assign,
    ast.Import, ast.ImportFrom, ast.alias,
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
        isinstance(node, ast.ImportFrom) and node.module in ('__builtins__', 'builtins'))]
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise UnsupportedMechanism(f'第 {getattr(node, "lineno", "?")} 行：尚未支持 {type(node).__name__}')
        if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
            raise UnsupportedMechanism(f'第 {node.lineno} 行：尚未支持属性 {node.attr}')
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and (node.level or not node.module or not node.module.isidentifier()):
                raise UnsupportedMechanism(f'第 {node.lineno} 行：仅支持同目录游戏模块')
            if any(alias.asname or not alias.name.isidentifier() or alias.name.startswith('_') for alias in node.names):
                raise UnsupportedMechanism(f'第 {node.lineno} 行：模块导入暂不支持通配、别名或私有名称')
        names = ([node.id] if isinstance(node, ast.Name) else [node.name] if isinstance(node, ast.FunctionDef)
                 else [node.arg] if isinstance(node, ast.arg) else node.names if isinstance(node, ast.Global) else [])
        reserved = {'_budget', '_dispatch', '_Request', '_elapsed', '_operation', '_slice', '_missing', '_entry',
                    '_modules', '_import', '_export', '_attribute', '_game_script', '_iterate'}
        if any(name in reserved or name.startswith('_timing_') for name in names):
            raise UnsupportedMechanism(f'第 {getattr(node, "lineno", "?")} 行：名称与本地执行器保留名称冲突')
        if isinstance(node, ast.Name) and node.id.startswith('__') and node.id != '__name__':
            raise UnsupportedMechanism(f'第 {node.lineno} 行：不支持名称 {node.id}')
        if isinstance(node, ast.Global) and len(node.names) != 1:
            raise UnsupportedMechanism(f'第 {node.lineno} 行：游戏每条global只接受一个名称')
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            raise UnsupportedMechanism(f'第 {node.lineno} 行：尚未支持模块属性赋值')
        if isinstance(node, ast.FunctionDef) and (node.decorator_list or node.returns):
            raise UnsupportedMechanism(f'第 {node.lineno} 行：不支持装饰器或返回类型注解')
    return compile_script(tree, path), hashlib.sha256(source.encode()).hexdigest()


def run_script(path: Path, seed=1, max_calls=100000, max_steps=2000000, seconds=10.0, trace=None, scenario=None, progress=False):
    """返回预测报告；progress启用限频stderr进度，CLI另用子进程兜住长操作。"""
    started = time.monotonic()
    deadline = started + seconds
    next_progress = started + 5
    code, source_hash = load_script(path)
    world = FarmWorld(seed, scenario)
    trace_hash = hashlib.sha256() if trace else None
    calls = 0
    steps = 0
    last_line = None
    trace_file = None

    def check():
        """执行副作用之前检查预算，避免上限之外多扣一次资源。"""
        nonlocal calls, next_progress
        if calls >= max_calls:
            raise BudgetExceeded(f'达到 API 调用上限 {max_calls}')
        now = time.monotonic()
        if now >= deadline:
            raise BudgetExceeded(f'达到墙钟上限 {seconds:g}s')
        if progress and now >= next_progress:
            goal = ''
            if world.goal:
                item, amount = world.goal
                goal = f' goal_item={item.name} goal_current={world.items[item]:g} goal_target={amount:g}'
            print(f'local_simulator seed={seed} game_seconds={world.now_ns / 1000000000:.3f}'
                  f' api_calls={calls} wall_seconds={now - started:.1f}{goal}', file=sys.stderr, flush=True)
            next_progress = now + 5
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

    env: dict[str, Any] = {'__builtins__': BUILTINS, '__name__': '__main__', '_missing': object(),
           'Entities': Entities, 'Grounds': Grounds, 'Items': Items,
           'Hats': Hats, 'Unlocks': Unlocks, 'Leaderboards': Leaderboards,
           '_dispatch': dispatch, '_Request': Request, '_timing_returned': ReturnedValue,
           '_elapsed': elapsed, '_operation': evaluate, '_slice': slice, '_iterate': game_iter,
           '_attribute': attribute, '_export': Module.export, '_modules': {}, '_game_script': True}
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
    dependencies = {}

    def import_module(cache, name):
        """模块首次导入执行一次；只读取入口同目录文件，报告记录每个依赖哈希。"""
        if name in cache:
            return cache[name]
        dependency = path.resolve().parent / (name + '.py')
        if dependency.is_symlink() or dependency.resolve().parent != path.resolve().parent:
            raise UnsupportedMechanism('游戏模块必须位于入口同目录且不能是符号链接')
        module_code, module_hash = load_script(dependency)
        dependencies[name] = {'path': str(dependency), 'sha256': module_hash}
        module_env = dict(template, __name__=name, _modules=cache)
        module = Module(module_env)
        cache[name] = module
        exec(module_code, module_env)
        yield from module_env['_entry']()
        return module

    env['_import'] = import_module
    template = dict(env)
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
        'model_version': DATA['game_version'], 'random_mode': 'seeded_simulate',
        'underground_model_version': UNDERGROUND['game_version'],
        'scenario': scenario or 'max_unlocks', 'script': str(path),
        'script_sha256': source_hash, 'seed': seed, 'stream_seeds': world.seeds,
        'module_dependencies': dependencies,
        'goal_reached': world.goal_reached(),
        'leaderboard_profile': world.leaderboard,
        'leaderboard_validation': 'asset_and_source_only' if world.leaderboard else None,
        'api_ticks': world.ticks, 'tick_ns': world.tick_ns,
        'predicted_game_seconds': world.now_ns / 1000000000,
        'predicted_api_seconds': world.now_ns / 1000000000,
        'interpreter_ticks': world.costs.get('_ops', 0), 'script_steps': steps, 'step_basis': 'compiled_checkpoint',
        'api_calls': {k:v for k,v in world.calls.items() if k != '_ops'},
        'api_ticks_by_function': {k:v for k,v in world.costs.items() if k != '_ops'},
        'estimated_loop_ticks': 0,
        'state': world.snapshot(), 'harvests': world.harvests,
        'immature_harvests': dict(world.immature_harvests),
        'immature_companion_harvests': dict(world.immature_companion_harvests),
        'trace_sha256': trace_hash.hexdigest() if trace_hash else None, 'output': list(scheduler.outputs),
        'output_dropped': scheduler.output_dropped,
        'warnings': world.warnings,
        'wall_seconds': time.monotonic() - started,
        'limitations': [
            '基础作物主要机制按model_version源码与资产对齐；新版尚未完成实机精度验收。',
            '固定seed对应simulate随机流；正式资源榜与Reset使用系统加密随机源，不能由该seed复现。',
            '脚本操作及199t无人机批次按原版规则实现；完整语言边界和任意并发组合未全面验证。',
            '水分、成熟和Power使用定时事件；旧版长窗口验收与新版边界分别见validation.md。',
            'simulate/leaderboard_run 只实现模拟内部拒绝递归入口；真实启动仍由协调器负责。',
            '地下地形、作物与解谜的逐项同seed实机对照见underground-validation.md；不代表所有并发组合或长程误差已通过。',
            '地下排行榜专用地形按资产和源码实现；固定seed是本地筛选流，不能重放正式榜的加密随机盘面。',
            '预测不是实测成绩；靠近成熟边界或依赖 get_time/get_tick_count 的策略须实机对照。',
        ],
    }


def worker(connection, options, deadline, seeds=None):
    """共享父进程截止时间，预留报告回传时间；各seed不复用世界状态。"""
    try:
        report_margin = min(1.0, options['seconds'] / 10)
        remaining = deadline - report_margin - time.monotonic()
        if remaining <= 0:
            raise BudgetExceeded('工作进程启动已用完执行预算')
        options = dict(options, seconds=remaining)
        if seeds is None:
            connection.send(run_script(**options, progress=True))
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
                report = run_script(**current, progress=True)
                completed += 1
                succeeded = succeeded and report['status'] == 'completed'
                connection.send({'seed_report': report})
                print(f'local_simulator completed={completed}/{len(seeds)} seed={seed}', file=sys.stderr, flush=True)
            connection.send({'kind': 'prediction_batch', 'seeds': seeds,
                             'status': 'completed' if completed == len(seeds) and succeeded else 'stopped'})
    except (BrokenPipeError, EOFError):
        # 父进程已结束接收，不向同一关闭管道再次发送错误。
        pass
    except Exception as exc:
        with suppress(BrokenPipeError, EOFError):
            connection.send({'kind': 'prediction', 'status': 'stopped',
                             'error': {'type': type(exc).__name__, 'message': str(exc)}})
    finally:
        connection.close()


def run_workers(options, seeds, deadline, jobs):
    """隔离seed分组并按输入顺序收集；所有进程共享截止时间且由本次调用回收。"""
    context = multiprocessing.get_context('spawn')
    count = min(jobs, len(seeds)) if seeds is not None else 1
    processes = []
    connections = []
    pending = set()
    reports = {}
    summaries = []
    error = None
    try:
        for index in range(count):
            parent, child = context.Pipe(duplex=False)
            connections.append(parent)
            group = seeds[index::count] if seeds is not None else None
            process = context.Process(target=worker, args=(child, options, deadline, group))
            processes.append(process)
            try:
                process.start()
            finally:
                child.close()
            pending.add(parent)
        while pending:
            remaining = deadline - time.monotonic()
            ready = wait(pending, timeout=max(0, remaining)) if remaining > 0 else []
            if not ready:
                error = f'工作进程超过 {options["seconds"]:g}s，已终止'
                break
            for connection in pending.copy():
                if connection not in ready:
                    continue
                try:
                    message = connection.recv()
                except EOFError:
                    error = '工作进程异常退出'
                    pending.remove(connection)
                    connection.close()
                    continue
                if 'seed_report' in message:
                    report = message['seed_report']
                    reports[report['seed']] = report
                else:
                    summaries.append(message)
                    if message.get('error') is not None:
                        error = message['error']
                    pending.remove(connection)
                    connection.close()
    finally:
        for connection in connections:
            connection.close()
        # 先给正常退出留出短暂时间；终止信号发给全部进程后，再逐个等待回收。
        for process in processes:
            if process.pid is not None:
                process.join(timeout=0.2)
        for process in processes:
            if process.is_alive():
                process.terminate()
        for process in processes:
            if process.pid is not None:
                process.join(timeout=1)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1)
                process.close()
    if seeds is None:
        return summaries[0] if summaries else {'kind': 'prediction', 'status': 'stopped', 'error': error}
    ordered = [reports[seed] for seed in seeds if seed in reports]
    complete = (error is None and len(ordered) == len(seeds) and len(summaries) == count
                and all(report['status'] == 'completed' for report in ordered))
    result = {'kind': 'prediction_batch', 'seeds': seeds,
              'status': 'completed' if complete else 'stopped',
              'reports': ordered, 'completed_seeds': len(ordered)}
    if error is not None:
        result['error'] = error
    return result


def default_jobs():
    """优先采用当前进程可用逻辑CPU数；旧Python按亲和性或系统CPU数回退。"""
    process_count = getattr(os, 'process_cpu_count', None)
    if process_count is not None:
        return process_count() or 1
    if hasattr(os, 'sched_getaffinity'):
        try:
            return len(os.sched_getaffinity(0)) or 1
        except OSError:
            # 接口可能存在但被运行环境限制，继续使用系统提供的CPU数。
            pass
    return os.cpu_count() or 1


def main():
    parser = argparse.ArgumentParser(description='本地运行农场 API 脚本，输出预测而非真实榜单成绩')
    parser.add_argument('script', type=Path)
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument('--seed', type=int, default=1)
    seed_group.add_argument('--seeds', type=int, nargs='+', help='运行1～100个不同seed，共享timeout预算；报告按输入顺序输出')
    parser.add_argument('--jobs', type=int, default=default_jobs(),
                        help='独立seed的工作进程数，须为正整数；默认可用逻辑CPU数（本机%(default)s），实际不超过seed数')
    parser.add_argument('--scenario', type=Path, help='JSON：preset、items、unlocks、goal；可含地下leaderboard名称')
    parser.add_argument('--leaderboard', help='地下排行榜名称，如 mushrooms_single；可用scenario覆盖库存、科技和目标')
    parser.add_argument('--trace', type=Path, help='写入逐 API JSONL；会覆盖指定文件')
    parser.add_argument('--output', type=Path, help='写入 JSON 报告；会覆盖指定文件')
    parser.add_argument('--max-api-calls', type=int, default=100000)
    parser.add_argument('--max-steps', type=int, default=2000000, help='编译后源语句/循环预算检查点上限，不是游戏tick')
    parser.add_argument('--timeout', type=float, default=10, help='整个工作进程的墙钟上限，默认 10 秒，最多 75 秒')
    args = parser.parse_args()
    seeds = args.seeds or [args.seed]
    if len(seeds) > 100 or len(set(seeds)) != len(seeds) or any(not 0 <= seed <= 2147483647 for seed in seeds):
        parser.error('seeds须为1～100个不同的非负Int32')
    if args.jobs < 1:
        parser.error('jobs须为正整数')
    if not (0 <= args.seed <= 2147483647 and 0 < args.timeout <= 75
            and args.max_api_calls > 0 and args.max_steps > 0):
        parser.error('seed 须为非负 Int32，timeout 须在 (0, 75] 内，调用/步数上限须为正数')
    paths = [p.resolve() for p in (args.script, args.scenario, args.trace, args.output) if p is not None]
    if args.trace and args.seeds:
        paths.extend(args.trace.with_name(f'{args.trace.stem}.seed-{seed}{args.trace.suffix}').resolve() for seed in seeds)
    if len(paths) != len(set(paths)):
        parser.error('脚本、轨迹和报告必须使用不同文件')
    options = {'path': args.script.resolve(), 'seed': args.seed, 'trace': args.trace,
               'max_calls': args.max_api_calls, 'max_steps': args.max_steps, 'seconds': args.timeout,
               'scenario': json.loads(args.scenario.read_text()) if args.scenario else None}
    if args.leaderboard:
        scenario = options['scenario'] or {}
        if not isinstance(scenario, dict) or 'leaderboard' in scenario:
            parser.error('--leaderboard 与场景中的 leaderboard 不能同时设置')
        options['scenario'] = dict(scenario, leaderboard=args.leaderboard)
    deadline = time.monotonic() + args.timeout
    report = run_workers(options, args.seeds, deadline, args.jobs)
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return 0 if report['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
