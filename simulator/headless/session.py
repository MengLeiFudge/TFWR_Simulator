"""用完整模拟轮次估计单轮期望时间。"""
import argparse
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time


MIN_GAME_SECONDS = 7200.0
TARGET_RELATIVE_MARGIN = 0.005
ADAPTIVE_CONFIDENCE_LEVEL = 0.99
FIXED_CONFIDENCE_LEVEL = 0.95
DEFAULT_FIXED_SAMPLE_RUNS = 30


def clocktext(seconds):
    """把秒数写成 分:秒.毫秒，便于和公开成绩直接对照。"""
    total = round(seconds, 3)
    return f'{int(total // 60)}:{total % 60:06.3f}'


def student_t_critical(alpha, degrees):
    def two_sided_tail(t):
        # 代换 x = √df · cot(角度)，双尾概率化为 sin^(df-1) 积分之比。
        angle = math.atan2(math.sqrt(degrees), t)
        sine = math.sin(angle)
        cosine = math.cos(angle)
        power = degrees - 1
        base = power % 2
        partial = 2 * math.sin(angle / 2) ** 2 if base else angle
        full = 1.0 if base else math.pi / 2
        boundary = sine ** (base + 1) * cosine
        for exponent in range(base + 2, power + 1, 2):
            factor = (exponent - 1) / exponent
            partial = factor * partial - boundary / exponent
            full *= factor
            boundary *= sine * sine
        return partial / full

    low, high = 0.0, 1.0
    while two_sided_tail(high) > alpha:
        high *= 2
    for _ in range(40):
        middle = (low + high) / 2
        if two_sided_tail(middle) > alpha:
            low = middle
        else:
            high = middle
    return high


def warn_stale_source(root):
    """反编译事实源落后于本机游戏时提示更新命令，不阻塞会话。"""
    checker = root / 'game_control' / 'tools' / 'refresh_decompiled_sources.py'
    if not checker.is_file():
        return
    result = subprocess.run([sys.executable, str(checker), '--check'], cwd=root,
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode == 0:
        return
    for line in result.stdout.splitlines():
        if '落后' in line or '≠' in line:
            print(f'⚠ {line}')


def runbatch(root, assemblies, script, args, count, seeds, output):
    command = [args.dotnet, str(assemblies), str(script), '--jobs', str(count)]
    if seeds:
        command += ['--seeds', ','.join(str(seed) for seed in seeds)]
    command += ['--seconds', f'{args.run_seconds:g}', '--wall-seconds', f'{args.wall_seconds:g}',
                '--max-api-calls', str(args.max_api_calls), '--max-nodes', str(args.max_nodes), '--json', output]
    command.extend(args.extra)
    started = time.monotonic()
    process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8-sig',
                             timeout=args.wall_seconds * 2 + 60,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    elapsed = time.monotonic() - started
    path = root / output
    if not path.is_file():
        raise SystemExit(f'模拟器执行失败（{elapsed:.1f}秒）：{process.stdout[-800:]}{process.stderr[-800:]}')
    report = json.loads(path.read_text(encoding='utf-8-sig'))
    reports = report.get('reports', [report])
    if len(reports) != count or any('seed' not in row for row in reports):
        raise SystemExit(f'模拟器未返回 {count} 轮报告：{process.stdout[-800:]}{process.stderr[-800:]}')
    return reports, elapsed


def main():
    started = time.monotonic()
    first_7200_wall_seconds = None
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path, help='入口脚本，相对于仓库根目录')
    parser.add_argument('--leaderboard', help='排行榜盘面名，省略则用preset')
    parser.add_argument('--sample-runs', type=int, help='指定固定轮数用于筛选，排行榜默认自动决定轮数')
    parser.add_argument('--jobs', type=int, default=None, help='并行工作进程数，默认取CPU核数与目标轮数的较小值')
    parser.add_argument('--seed-start', type=int, default=None,
                        help='给定起始种子时按其重放随机（配对筛选）；默认不给，由模拟器按游戏方式随机取种子')
    parser.add_argument('--run-seconds', type=float, default=7200.0, help='单轮游戏时间上限，默认7200秒')
    parser.add_argument('--wall-seconds', type=float, default=300.0, help='每一批的墙钟上限，默认300秒')
    parser.add_argument('--max-api-calls', type=int, default=100000000, help='单轮内置调用上限，默认1亿次')
    parser.add_argument('--max-nodes', type=int, default=5000000000, help='单轮解释器节点上限，默认50亿')
    parser.add_argument('--extra', action='append', default=[], help='透传给模拟器的额外参数，如 "--size 32"')
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', type=Path, help='报告路径，默认写 .codex/tmp/sessions/<榜单或脚本>-sample.json')
    parser.add_argument('--no-output', action='store_true', help='只在标准输出打印结论，不写报告文件')
    args = parser.parse_args()
    args.jobs = args.jobs or min(os.cpu_count() or 1, 64)
    if not 1 <= args.jobs <= 64:
        parser.error('--jobs 须在1～64之间（模拟器单批并行上限）')
    if args.sample_runs is not None and args.sample_runs < 1:
        parser.error('--sample-runs 须为正整数')
    root = Path(__file__).resolve().parents[2]
    warn_stale_source(root)
    assembly = Path(__file__).resolve().parent / 'bin/Release/net10.0/TFWRSimulator.dll'
    assemblies = assembly.relative_to(root)
    if not (root / assemblies).exists():
        raise SystemExit('未找到已构建的模拟器，先运行 dotnet build simulator/headless/TFWRSimulator.csproj -c Release')
    script = args.script if args.script.is_absolute() else root / args.script
    script = script.relative_to(root)
    args.extra = [part for item in args.extra for part in item.split()]
    board = args.leaderboard
    if board:
        args.extra.extend(['--leaderboard', board])
    elif '--leaderboard' in args.extra:
        board = args.extra[args.extra.index('--leaderboard') + 1]
    elif '--scenario' in args.extra:
        try:
            scenario = root / args.extra[args.extra.index('--scenario') + 1]
            data = json.loads(scenario.read_text(encoding='utf-8-sig'))
            board = data.get('leaderboard') if isinstance(data, dict) else None
        except (IndexError, ValueError, OSError) as error:
            parser.error(f'无法读取 --scenario：{error}')
    temp_root = root / '.codex/tmp/sessions'
    temp_root.mkdir(parents=True, exist_ok=True)
    if args.no_output:
        args.output = None
    elif args.output is None:
        args.output = temp_root / f'{args.leaderboard or script.stem}-sample.json'
    adaptive = bool(board) and args.sample_runs is None and args.seed_start is None
    if adaptive and {'--seed', '--seeds'}.intersection(args.extra):
        parser.error('固定种子筛选请使用 --seed-start 或显式指定 --sample-runs')
    limit = args.sample_runs or DEFAULT_FIXED_SAMPLE_RUNS
    checkpoint = 0
    confidence = ADAPTIVE_CONFIDENCE_LEVEL if adaptive else FIXED_CONFIDENCE_LEVEL
    alpha = 1 - confidence
    margin = None
    runs = []
    times = []
    total = 0.0
    wall = 0.0
    seed = args.seed_start if args.seed_start is not None else (None if board else 1)
    reason = None
    precision_met = None
    modes = set()
    while adaptive or len(runs) < limit:
        want = args.jobs if adaptive else min(args.jobs, limit - len(runs))
        seeds = list(range(seed, seed + want)) if seed is not None else []
        if seed is not None:
            seed += want
        with tempfile.TemporaryDirectory(prefix='batch-', dir=temp_root) as directory:
            reports, elapsed = runbatch(root, assemblies, script, args, want, seeds,
                                        str(Path(directory) / 'report.json'))
        wall += elapsed
        for report in reports:
            reached = report.get('goal_reached') is True and report.get('stop_reason') == 'finished'
            runs.append({'seed': report.get('seed'), 'game_seconds': report.get('game_seconds'),
                         'goal_reached': reached, 'stop_reason': report.get('stop_reason'),
                         'random_mode': report.get('random_mode'),
                         'error': report.get('error'),
                         'warnings': [m for m in report.get('messages', []) if m.startswith('Warning: ')],
                         'output_dropped': report.get('output_dropped', 0)})
            modes.add(report.get('random_mode'))
            if reached:
                times.append(report['game_seconds'])
                total += times[-1]
                if first_7200_wall_seconds is None and reason is None and total >= MIN_GAME_SECONDS:
                    first_7200_wall_seconds = round(time.monotonic() - started, 3)
                    print(f'累计7200游戏秒 墙钟={first_7200_wall_seconds:.3f}秒', file=sys.stderr)
            elif reason is None:
                reason = (f"seed={report.get('seed')} stop_reason={report.get('stop_reason')} "
                          f"error={report.get('error')}")
        label = f'seed={seeds[0]}..{seeds[-1]}' if seeds else '游戏随机'
        print(f'批次 {label} 墙钟={elapsed:.1f}秒 已抽样={len(runs)}轮 累计={total:.1f}游戏秒', file=sys.stderr)
        if not adaptive:
            continue
        if reason is not None:
            break
        if modes != {'game_leaderboard_random'}:
            reason = '自动抽样需要游戏随机模式，固定种子筛选请指定 --seed-start 或 --sample-runs'
            break
        if len(times) < 2:
            continue
        checkpoint += 1
        # 各次检查的错误概率预算之和为 alpha。
        check_alpha = alpha / (checkpoint * (checkpoint + 1))
        if total < MIN_GAME_SECONDS:
            continue
        mean = statistics.fmean(times)
        se = statistics.stdev(times) / math.sqrt(len(times))
        margin = student_t_critical(check_alpha, len(times) - 1) * se
        target_margin = TARGET_RELATIVE_MARGIN * mean
        precision_met = margin <= target_margin
        print(f'均值={mean:.3f}游戏秒 区间半宽={margin:.3f} 目标半宽={target_margin:.3f}', file=sys.stderr)
        if precision_met:
            break
    valid = reason is None
    mean = statistics.fmean(times) if times else None
    sd = statistics.stdev(times) if len(times) > 1 else None
    se = sd / math.sqrt(len(times)) if sd is not None else None
    mode = next(iter(modes)) if len(modes) == 1 else None
    if not valid:
        margin = None
    elif not adaptive and se is not None and mode == 'game_leaderboard_random':
        margin = student_t_critical(alpha, len(times) - 1) * se
    margin95 = margin
    if adaptive and margin is not None:
        alpha95 = (1 - FIXED_CONFIDENCE_LEVEL) / (checkpoint * (checkpoint + 1))
        margin95 = student_t_critical(alpha95, len(times) - 1) * se
    summary = {
        'script': str(script), 'leaderboard': board, 'random_mode': mode,
        'mode': 'sample', 'sample_runs': args.sample_runs,
        'sampling_policy': 'adaptive' if adaptive else 'fixed',
        'minimum_game_seconds': MIN_GAME_SECONDS if adaptive else None,
        'first_7200_wall_seconds': first_7200_wall_seconds,
        'target_relative_margin': TARGET_RELATIVE_MARGIN if adaptive else None,
        'confidence_level': confidence if margin is not None else None,
        'precision_met': precision_met if adaptive and margin is not None else None,
        'runs': len(runs), 'runs_reached': len(times), 'total_game_seconds': round(total, 6),
        'valid': valid, 'invalid_reason': reason,
        'runs_with_warnings': sum(bool(run['warnings']) for run in runs),
        'output_dropped': sum(run['output_dropped'] for run in runs),
        'mean_game_seconds': mean if valid else None,
        'successful_mean_game_seconds': mean,
        'stdev_game_seconds': sd, 'stderr_game_seconds': se,
        'mean_ci_half_width_game_seconds': margin,
        'mean_ci95_half_width_game_seconds': margin95,
        'min_game_seconds': min(times) if times else None, 'max_game_seconds': max(times) if times else None,
        'mean_clock': clocktext(mean) if valid and mean is not None else None,
        'wall_seconds': round(wall, 2), 'detail': runs}
    if args.output:
        path = args.output if args.output.is_absolute() else root / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'detail'}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


if __name__ == '__main__':
    sys.exit(main())
