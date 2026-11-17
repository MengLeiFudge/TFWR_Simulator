from __future__ import annotations

import subprocess
import sys

from _bootstrap_tfwr_orchestrator import add_orchestrator_src_to_path

add_orchestrator_src_to_path()

from tfwr_orchestrator.config import REPO_ROOT, resolve_bepinex_root, resolve_game_root, to_windows_path


def main() -> int:
    game_root = resolve_game_root()
    assert game_root is not None
    bepinex_root = resolve_bepinex_root(game_root)
    return subprocess.call(
        [
            'dotnet.exe', 'build',
            to_windows_path(REPO_ROOT / 'game_mod' / 'TFWROracleRunner.csproj'),
            '-c', 'Release', '-t:PackageThunderstore',
            f'-p:TFWRGameRoot={to_windows_path(game_root)}',
            f'-p:TFWRBepInExRoot={to_windows_path(bepinex_root)}',
            *sys.argv[1:],
        ],
        cwd=REPO_ROOT,
        timeout=120,
    )


if __name__ == '__main__':
    raise SystemExit(main())
