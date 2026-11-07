from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR_SOURCE_ROOT = PROJECT_ROOT / "src"


def add_orchestrator_src_to_path() -> Path:
    if str(ORCHESTRATOR_SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(ORCHESTRATOR_SOURCE_ROOT))
    return ORCHESTRATOR_SOURCE_ROOT
