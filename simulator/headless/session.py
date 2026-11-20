"""按游戏会话口径累计轮时，或用固定轮数估计单轮期望时间。"""
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


def clocktext(seconds):
    """把秒数写成 分:秒.毫秒，便于和公开成绩直接对照。"""
    total = round(seconds, 3)
    return f'{int(total // 60)}:{total % 60:06.3f}'


def warn_stale_source(root):
    """反编译事实源落后于本机游戏时提示更新命令，不阻塞会话。"""
    checker = root / 'game_control' / 'tools' / 'refresh_decompiled_sources.py'
    if not checker.is_file():
        return
    result = subprocess.run([sys.executable, str(checker), '--check'], cwd=root,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
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
                             timeout=args.wall_seconds * 2 + 60)
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path, help='入口脚本，相对于仓库根目录')
    parser.add_argument('--leaderboard', help='排行榜盘面名，省略则用preset')
    duration = parser.add_mutually_exclusive_group()
    duration.add_argument('--session-seconds', type=float, default=7200.0, help='会话预算，默认7200游戏秒')
    duration.add_argument('--sample-runs', type=int, help='固定抽样轮数，用完整轮估算单轮期望时间')
    parser.add_argument('--jobs', type=int, default=None, help='并行工作进程数，默认取CPU核数与目标轮数的较小值')
    parser.add_argument('--seed-start', type=int, default=None,
                        help='给定起始种子时按其重放随机（配对筛选）；默认不给，由模拟器按游戏方式随机取种子')
    parser.add_argument('--max-runs', type=int, default=1200, help='轮数上限，防止短轮无限续跑')
    parser.add_argument('--run-seconds', type=float, default=7200.0, help='单轮游戏时间上限，默认与会话预算相同')
    parser.add_argument('--wall-seconds', type=float, default=300.0, help='每一批的墙钟上限，默认300秒')
    parser.add_argument('--max-api-calls', type=int, default=100000000, help='单轮内置调用上限，默认1亿次')
    parser.add_argument('--max-nodes', type=int, default=5000000000, help='单轮解释器节点上限，默认50亿')
    parser.add_argument('--extra', action='append', default=[], help='透传给模拟器的额外参数，如 "--size 32"')
    parser.add_argument('--expect-seconds', type=float, help='单轮预估游戏秒，用来限制首批并发')
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', type=Path, help='报告路径，默认写 .codex/tmp/sessions/<榜单或脚本>-{session,sample}.json')
    parser.add_argument('--no-output', action='store_true', help='只在标准输出打印结论，不写报告文件')
    args = parser.parse_args()
    args.jobs = args.jobs or min(os.cpu_count() or 1, 64)
    if not 1 <= args.jobs <= 64:
        parser.error('--jobs 须在1～64之间（模拟器单批并行上限）')
    if args.max_runs < 1 or (args.sample_runs is not None and not 1 <= args.sample_runs <= args.max_runs):
        parser.error('--sample-runs 须在 1 到 --max-runs 之间，--max-runs 须为正数')
    if not math.isfinite(args.session_seconds) or args.session_seconds <= 0:
        parser.error('--session-seconds 须为有限正数')
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
    sample = args.sample_runs is not None
    mode_name = 'sample' if sample else 'session'
    if args.no_output:
        args.output = None
    elif args.output is None:
        args.output = temp_root / f'{args.leaderboard or script.stem}-{mode_name}.json'
    limit = args.sample_runs if sample else args.max_runs
    runs = []
    total = 0.0
    wall = 0.0
    seed = args.seed_start if args.seed_start is not None else (None if board else 1)
    reason = None
    while len(runs) < limit and (sample or total < args.session_seconds):
        want = min(args.jobs, limit - len(runs))
        if not sample:
            estimate = total / len(runs) if runs else args.expect_seconds
            if estimate and estimate > 0:
                want = min(want, max(1, math.ceil((args.session_seconds - total) / estimate)))
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
            if reached:
                total += report.get('game_seconds') or 0.0
            elif reason is None:
                reason = (f"seed={report.get('seed')} stop_reason={report.get('stop_reason')} "
                          f"error={report.get('error')}")
            if not sample and (not reached or total >= args.session_seconds):
                break
        label = f'seed={seeds[0]}..{seeds[-1]}' if seeds else '游戏随机'
        progress = f'抽样={len(runs)}/{limit}轮' if sample else f'累计={total:.1f}/{args.session_seconds:.0f}游戏秒'
        print(f'批次 {label} 墙钟={elapsed:.1f}秒 {progress} 轮数={len(runs)}', file=sys.stderr)
        if not sample and reason is not None:
            break
    times = [run['game_seconds'] for run in runs if run['goal_reached']]
    enough = len(runs) == limit if sample else total >= args.session_seconds
    valid = reason is None and enough
    mean = statistics.fmean(times) if times else None
    sd = statistics.stdev(times) if len(times) > 1 else None
    se = sd / math.sqrt(len(times)) if sd is not None else None
    modes = {run['random_mode'] for run in runs if run['random_mode'] is not None}
    mode = next(iter(modes)) if len(modes) == 1 else None
    margin = 1.96 * se if sample and valid and len(times) >= 30 and mode == 'game_leaderboard_random' else None
    summary = {
        'script': str(script), 'leaderboard': board, 'random_mode': mode,
        'mode': mode_name,
        'session_seconds': None if sample else args.session_seconds, 'sample_runs': args.sample_runs,
        'runs': len(runs), 'runs_reached': len(times), 'total_game_seconds': round(total, 6),
        'valid': valid, 'invalid_reason': reason or (None if enough else '达到轮数上限，未跑满会话'),
        'runs_with_warnings': sum(bool(run['warnings']) for run in runs),
        'output_dropped': sum(run['output_dropped'] for run in runs),
        'mean_game_seconds': mean if valid else None,
        'successful_mean_game_seconds': mean,
        'stdev_game_seconds': sd, 'stderr_game_seconds': se,
        'mean_ci95_half_width_game_seconds': margin,
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
