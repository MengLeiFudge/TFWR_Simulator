"""跑满指定游戏时长的本地场均会话，口径与排行榜完整统计一致。

累计各轮游戏时间到会话预算（默认7200游戏秒）为止，均分只算达成目标的轮；
任一轮未达成目标即按原版 `StopLeaderboardRun` 规则作废整场并立即停止。
每批seed由模拟器自己开独立进程并行，本工具只负责排队、累计与汇总。
"""
import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
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


def runbatch(root, assemblies, script, args, seeds, output):
    command = [args.dotnet, str(assemblies), str(script), '--seeds', ','.join(str(seed) for seed in seeds),
               '--jobs', str(min(args.jobs, len(seeds))), '--seconds', f'{args.run_seconds:g}',
               '--wall-seconds', f'{args.wall_seconds:g}', '--max-api-calls', str(args.max_api_calls),
               '--max-nodes', str(args.max_nodes), '--json', output]
    for item in args.extra:
        command.extend(item.split())
    started = time.monotonic()
    process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8-sig',
                             timeout=args.wall_seconds * 2 + 60)
    elapsed = time.monotonic() - started
    path = root / output
    if process.returncode != 0 or not path.exists():
        raise SystemExit(f'模拟器执行失败（{elapsed:.1f}秒）：{process.stdout[-800:]}{process.stderr[-800:]}')
    report = json.loads(path.read_text(encoding='utf-8-sig'))
    path.unlink()
    return (report['reports'] if 'reports' in report else [report]), elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path, help='入口脚本，相对于仓库根目录')
    parser.add_argument('--leaderboard', help='排行榜盘面名，省略则用preset')
    parser.add_argument('--session-seconds', type=float, default=7200.0, help='会话预算，默认7200游戏秒')
    parser.add_argument('--jobs', type=int, default=None, help='并行工作进程数，默认取CPU核数与目标轮数的较小值')
    parser.add_argument('--seed-start', type=int, default=1)
    parser.add_argument('--max-runs', type=int, default=1200, help='轮数上限，防止短轮无限续跑')
    parser.add_argument('--run-seconds', type=float, default=7200.0, help='单轮游戏时间上限，默认与会话预算相同')
    parser.add_argument('--wall-seconds', type=float, default=300.0, help='每一批的墙钟上限，默认300秒')
    parser.add_argument('--max-api-calls', type=int, default=100000000, help='单轮内置调用上限，默认1亿次')
    parser.add_argument('--max-nodes', type=int, default=5000000000, help='单轮解释器节点上限，默认50亿')
    parser.add_argument('--extra', action='append', default=[], help='透传给模拟器的额外参数，如 "--size 32"')
    parser.add_argument('--expect-seconds', type=float, help='单轮预估游戏秒，用来限制首批并发')
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', type=Path, help='会话报告路径，默认写 .codex/tmp/sessions/<榜单或脚本>-session.json，同名覆盖')
    parser.add_argument('--no-output', action='store_true', help='只在标准输出打印结论，不写报告文件')
    args = parser.parse_args()
    args.jobs = args.jobs or (os.cpu_count() or 1)
    if args.no_output:
        args.output = None
    elif args.output is None:
        args.output = Path('.codex/tmp/sessions') / f'{args.leaderboard or args.script.stem}-session.json'
    root = Path(__file__).resolve().parents[2]
    warn_stale_source(root)
    assembly = Path(__file__).resolve().parent / 'bin/Release/net10.0/TFWRSimulator.dll'
    assemblies = assembly.relative_to(root)
    if not (root / assemblies).exists():
        raise SystemExit('未找到已构建的模拟器，先运行 dotnet build simulator/headless/TFWRSimulator.csproj -c Release')
    script = args.script if args.script.is_absolute() else root / args.script
    script = script.relative_to(root)
    if args.leaderboard:
        args.extra = args.extra + [f'--leaderboard {args.leaderboard}']
    (root / '.codex').mkdir(exist_ok=True)
    runs = []
    total = 0.0
    wall = 0.0
    seed = args.seed_start
    reason = None
    while total < args.session_seconds and len(runs) < args.max_runs:
        # 首轮按会话预算的八分之一估轮数，之后按实测均值只补差额。
        mean = statistics.fmean(run['game_seconds'] for run in runs if run['goal_reached']) if any(
            run['goal_reached'] for run in runs) else args.session_seconds / 8
        want = max(1, min(args.jobs, args.max_runs - len(runs), 100))
        if args.expect_seconds:
            # 已知单轮量级时按预算只开必要并发，避免长轮白白超额。
            want = max(1, min(want, int(args.session_seconds / max(args.expect_seconds, 1e-6)) + 1))
        if runs:
            want = max(1, min(want, int((args.session_seconds - total) / max(mean, 1e-6)) + 1))
        seeds = list(range(seed, seed + want))
        seed += want
        reports, elapsed = runbatch(root, assemblies, script, args, seeds, f'.codex/session-batch-{seeds[0]}.json')
        wall += elapsed
        for report in reports:
            reached = report.get('goal_reached') is True and report.get('stop_reason') == 'finished'
            runs.append({'seed': report.get('seed'), 'game_seconds': report.get('game_seconds'),
                         'goal_reached': report.get('goal_reached'), 'stop_reason': report.get('stop_reason'),
                         'error': report.get('error')})
            if reached:
                total += report.get('game_seconds') or 0.0
            elif reason is None:
                reason = (f"seed={report.get('seed')} stop_reason={report.get('stop_reason')} "
                          f"error={report.get('error')}")
        print(f'批次 seed={seeds[0]}..{seeds[-1]} 墙钟={elapsed:.1f}秒 累计={total:.1f}/{args.session_seconds:.0f}游戏秒 '
              f'轮数={len(runs)}', file=sys.stderr)
        if reason is not None:
            break
    times = [run['game_seconds'] for run in runs if run['goal_reached']]
    valid = reason is None and total >= args.session_seconds
    summary = {
        'script': str(script), 'leaderboard': args.leaderboard, 'session_seconds': args.session_seconds,
        'runs': len(runs), 'runs_reached': len(times), 'total_game_seconds': round(total, 6),
        'valid': valid, 'invalid_reason': reason,
        'mean_game_seconds': statistics.fmean(times) if times else None,
        'stdev_game_seconds': statistics.pstdev(times) if len(times) > 1 else None,
        'stderr_game_seconds': statistics.pstdev(times) / len(times) ** 0.5 if len(times) > 1 else None,
        'min_game_seconds': min(times) if times else None, 'max_game_seconds': max(times) if times else None,
        'mean_clock': clocktext(statistics.fmean(times)) if times else None,
        'wall_seconds': round(wall, 2), 'detail': runs}
    if args.output:
        path = args.output if args.output.is_absolute() else root / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'detail'}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


if __name__ == '__main__':
    sys.exit(main())
