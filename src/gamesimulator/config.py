from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
import re


PACKAGE_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = PACKAGE_DIR.parent
REPO_ROOT = SOURCE_ROOT.parent
LEADERBOARD_LINK = REPO_ROOT / "leaderboard"
REFERENCES_ROOT = REPO_ROOT / "references"
LEADERBOARD_REFERENCE_ROOT = REFERENCES_ROOT / "leaderboard_scripts"
DEFAULT_ENV_FILE = REPO_ROOT / ".env"
DEFAULT_ENV_EXAMPLE_FILE = REPO_ROOT / ".env.example"


def _strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def load_local_env(env_file: str | Path | None = None) -> None:
    path = DEFAULT_ENV_FILE if env_file is None else Path(env_file)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = _strip_wrapping_quotes(value.strip())


def normalize_config_path(path_text: str | Path) -> Path:
    text = str(path_text).strip()
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", text)
    if match and os.name != "nt":
        drive = match.group(1).lower()
        tail = re.sub(r"[\\/]+", "/", match.group(2))
        return Path(f"/mnt/{drive}/{tail}")
    return Path(text).expanduser()


def to_windows_path(path_text: str | Path) -> str:
    text = str(Path(path_text)).strip()
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", text)
    if match:
        drive = match.group(1).upper()
        tail = match.group(2).replace("/", "\\")
        return f"{drive}:\\{tail}"
    return text


@lru_cache(maxsize=128)
def _resolve_normalized_path(path_text: str) -> Path:
    return normalize_config_path(path_text).resolve()


def resolve_save_root(save_root: str | Path | None = None, required: bool = True) -> Path | None:
    if save_root is None:
        load_local_env()
        configured = os.environ.get("TFWR_SAVE_ROOT", "").strip()
        if not configured:
            if required:
                raise RuntimeError(
                    f"TFWR_SAVE_ROOT 未配置。请在 {DEFAULT_ENV_FILE} 中设置，或显式传入 save_root。"
                )
            return None
        resolved = _resolve_normalized_path(configured)
    else:
        resolved = _resolve_normalized_path(str(save_root))
    if required and not resolved.exists():
        raise FileNotFoundError(f"配置的 Save0 目录不存在: {resolved}")
    return resolved
