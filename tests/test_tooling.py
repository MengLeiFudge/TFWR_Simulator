from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SUBPROJECT_SOURCE_ROOT = REPO_ROOT / "python" / "tfwr_orchestrator" / "src"
SUBPROJECT_TEST_ROOT = REPO_ROOT / "python" / "tfwr_orchestrator" / "tests"

for path in (SUBPROJECT_SOURCE_ROOT, SUBPROJECT_TEST_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


from test_config import *  # noqa: F401,F403
from test_real_game_runner import *  # noqa: F401,F403
from test_sync import *  # noqa: F401,F403
