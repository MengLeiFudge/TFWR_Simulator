from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = REPO_ROOT / "src"

# 本地常用入口：直接改这里，然后运行 `py runner.py`
DEFAULT_TARGET = "lb_start.py"
DEFAULT_SEED = "1"
DEFAULT_SPEEDUP = "10000"
# 留空表示继续走 `.env` 里的 TFWR_SAVE_ROOT
DEFAULT_SAVE_ROOT = None

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from gamesimulator.config import load_local_env


load_local_env()

from gamesimulator.runner import main


if __name__ == "__main__":
    cli_args = sys.argv[1:]
    if not cli_args:
        cli_args = [DEFAULT_TARGET, DEFAULT_SEED]
        if DEFAULT_SAVE_ROOT:
            cli_args.extend([DEFAULT_SPEEDUP, str(DEFAULT_SAVE_ROOT)])
    raise SystemExit(main(cli_args))
