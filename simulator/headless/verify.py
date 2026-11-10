"""重放已归档的实机观测；只启动C#模拟器，不启动游戏或旧Python模型。"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    folder = Path(__file__).resolve().parent
    assembly = folder / 'bin/Release/net10.0/TFWRSimulator.dll'
    cases = json.loads((folder / 'fixtures/expected.json').read_text())
    started = time.monotonic()

    def replay(case):
        name = case['name']
        source = folder / 'fixtures' / name / 'probe.py'
        if hashlib.sha256(source.read_bytes()).hexdigest() != case['script_sha256']:
            return {'case': name, 'passed': False, 'error': 'Fixture source hash changed'}
        # 相对参数也能供WSL中的Windows dotnet识别。
        command = [args.dotnet, str(assembly.relative_to(root)), str(source.relative_to(root)),
                   '--scenario', str((source.parent / 'scenario.json').relative_to(root)),
                   '--seed', str(case['seed']), '--seconds', '24000', '--wall-seconds', '8']
        try:
            process = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                     encoding='utf-8-sig', timeout=11)
            report = json.loads(process.stdout)
            messages_equal = report.get('messages') == case['messages']
            time_equal = case['nanoseconds'] is None or report.get('nanoseconds') == case['nanoseconds']
            row = {'case': name, 'archive_build': case['build'], 'request_id': case['request_id'],
                   'passed': process.returncode == 0 and report.get('stop_reason') == 'finished'
                             and messages_equal and time_equal,
                   'messages_equal': messages_equal, 'messages': len(report.get('messages', [])),
                   'nanoseconds_equal': time_equal if case['nanoseconds'] is not None else None,
                   'nanoseconds': report.get('nanoseconds'), 'wall_seconds': report.get('wall_seconds'),
                   'source_sha256': case['script_sha256'], 'error': report.get('error')}
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as error:
            row = {'case': name, 'passed': False, 'error': str(error)}
        print(f"{name}: {'PASS' if row['passed'] else 'FAIL'}", flush=True)
        return row

    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(replay, cases))
    result = {'kind': 'archived_game_replay', 'fresh_game_run': False,
              'passed': all(row['passed'] for row in rows), 'cases': rows,
              'wall_seconds': time.monotonic() - started,
              'assembly_sha256': hashlib.sha256(assembly.read_bytes()).hexdigest(),
              'resources_sha256': hashlib.sha256((folder / 'data/assets.json').read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
