from __future__ import annotations

from functools import lru_cache
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess


PACKAGE_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = PACKAGE_DIR.parent
PROJECT_ROOT = SOURCE_ROOT.parent
REPO_ROOT = PROJECT_ROOT.parent

GAMESAVE_LINK = REPO_ROOT / "gamesave"
REFERENCES_ROOT = REPO_ROOT / "references"
LEADERBOARD_REFERENCE_ROOT = REFERENCES_ROOT / "leaderboard_scripts"
DECOMPILED_SOURCE_ROOT = REFERENCES_ROOT / "DecompiledSource"

DEFAULT_ENV_FILE = REPO_ROOT / ".env"
DEFAULT_ENV_EXAMPLE_FILE = REPO_ROOT / ".env.example"
DEFAULT_GAME_ROOT_TEXT = r"D:\Steam\steamapps\common\The Farmer Was Replaced"
GAME_ROOT_ENV_VAR = "TFWR_GAME_ROOT"
SAVE_ROOT_ENV_VAR = "TFWR_SAVE_ROOT"
BEPINEX_ROOT_ENV_VAR = "TFWR_BEPINEX_ROOT"
ORACLE_STATE_FILE_NAME = "mlj.tfwr.oracle-runner.state.json"


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


def _resolve_config_root(
    explicit_path: str | Path | None,
    env_var_name: str,
    *,
    default_path: str | Path | None = None,
    required: bool = True,
    missing_message: str,
) -> Path | None:
    if explicit_path is None:
        load_local_env()
        configured = os.environ.get(env_var_name, "").strip()
        if configured:
            resolved = _resolve_normalized_path(configured)
        elif default_path is not None:
            resolved = _resolve_normalized_path(str(default_path))
        else:
            if required:
                raise RuntimeError(missing_message)
            return None
    else:
        resolved = _resolve_normalized_path(str(explicit_path))
    if required and not resolved.exists():
        raise FileNotFoundError(f"{env_var_name} 指向的目录不存在: {resolved}")
    return resolved


def resolve_save_root(save_root: str | Path | None = None, required: bool = True) -> Path | None:
    return _resolve_config_root(
        save_root,
        SAVE_ROOT_ENV_VAR,
        required=required,
        missing_message=f"{SAVE_ROOT_ENV_VAR} 未配置。请在 {DEFAULT_ENV_FILE} 中设置，或显式传入 save_root。",
    )


def resolve_persistent_data_root(save_root: str | Path | None = None, required: bool = True) -> Path | None:
    root = resolve_save_root(save_root, required=required)
    if root is None:
        return None

    persistent_root = root.parent.parent
    if required and not persistent_root.is_dir():
        raise FileNotFoundError(f"无法从 Save0 路径推导 persistentDataPath: {root}")
    return persistent_root


def resolve_output_path(save_root: str | Path | None = None, required: bool = True) -> Path | None:
    persistent_root = resolve_persistent_data_root(save_root, required=required)
    if persistent_root is None:
        return None
    return persistent_root / "output.txt"


def resolve_unity_log_path(save_root: str | Path | None = None, required: bool = True) -> Path | None:
    """Unity Player.log 与 output.txt 同属游戏持久数据目录，不位于 BepInEx profile。"""
    root = resolve_persistent_data_root(save_root, required=required)
    if root is None:
        return None
    path = root / "Player.log"
    if required and not path.is_file():
        raise FileNotFoundError(f"未找到 Unity 日志文件: {path}")
    return path


def resolve_game_root(game_root: str | Path | None = None, required: bool = True) -> Path | None:
    return _resolve_config_root(
        game_root,
        GAME_ROOT_ENV_VAR,
        default_path=DEFAULT_GAME_ROOT_TEXT,
        required=required,
        missing_message=f"{GAME_ROOT_ENV_VAR} 未配置。请在 {DEFAULT_ENV_FILE} 中设置，或显式传入 game_root。",
    )


def resolve_bepinex_root(
    game_root: str | Path | None = None,
    required: bool = True,
    *,
    bepinex_root: str | Path | None = None,
) -> Path | None:
    """优先使用显式 BepInEx/profile 路径；未配置时回退到游戏目录/BepInEx。"""
    load_local_env()
    configured = bepinex_root if bepinex_root is not None else os.environ.get(BEPINEX_ROOT_ENV_VAR, "").strip()
    if configured:
        return _resolve_config_root(
            configured,
            BEPINEX_ROOT_ENV_VAR,
            required=required,
            missing_message=f"{BEPINEX_ROOT_ENV_VAR} 未配置。",
        )
    root = resolve_game_root(game_root, required=required)
    if root is None:
        return None
    return _resolve_config_root(
        root / "BepInEx",
        BEPINEX_ROOT_ENV_VAR,
        required=required,
        missing_message="未找到游戏目录下的 BepInEx。",
    )


def resolve_oracle_state_path(
    game_root: str | Path | None = None, *, bepinex_root: str | Path | None = None
) -> Path:
    """状态和日志必须来自同一个 BepInEx 安装/profile。"""
    root = resolve_bepinex_root(game_root, bepinex_root=bepinex_root)
    assert root is not None
    return root / "config" / ORACLE_STATE_FILE_NAME

def resolve_request_record_path(state_path: Path, request_id: int) -> Path:
    """客户端请求回执与结果存放在profile状态文件旁，独立于游戏Save0。"""
    return state_path.with_suffix('.requests') / f'{request_id}.json'


def resolve_request_result_path(state_path: Path, request_id: int) -> Path:
    """完整终态报告独立归档，常规查询只读取轻量请求回执。"""
    return state_path.with_suffix('.requests') / f'{request_id}.result.json'


def resolve_request_key_path(state_path: Path, key: str) -> Path:
    """幂等键只作为摘要文件名，避免用户输入成为路径片段。"""
    digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
    return state_path.with_suffix('.requests') / f'key-{digest}.json'


def resolve_bepinex_log_path(
    game_root: str | Path | None = None,
    required: bool = True,
    *,
    bepinex_root: str | Path | None = None,
) -> Path | None:
    """解析手动安装或 R2 profile 的模组日志路径。"""
    root = resolve_bepinex_root(game_root, required=required, bepinex_root=bepinex_root)
    if root is None:
        return None
    log_path = root / "LogOutput.log"
    if required and not log_path.is_file():
        raise FileNotFoundError(f"未找到 BepInEx 日志文件: {log_path}")
    return log_path


def resolve_game_data_root(game_root: str | Path | None = None, required: bool = True) -> Path | None:
    root = resolve_game_root(game_root, required=required)
    if root is None:
        return None

    candidates = sorted(path for path in root.iterdir() if path.is_dir() and path.name.endswith("_Data"))
    if not candidates:
        if required:
            raise FileNotFoundError(f"游戏目录下未找到 *_Data 目录: {root}")
        return None
    return candidates[0]


def resolve_game_managed_root(game_root: str | Path | None = None, required: bool = True) -> Path | None:
    data_root = resolve_game_data_root(game_root, required=required)
    if data_root is None:
        return None
    managed_root = data_root / "Managed"
    if required and not managed_root.is_dir():
        raise FileNotFoundError(f"游戏目录下未找到 Managed 目录: {managed_root}")
    return managed_root


def _cmd_exe() -> str | None:
    if os.name == "nt":
        return "cmd"
    return shutil.which("cmd.exe")


def remove_existing_link(link_path: Path) -> None:
    if not link_path.exists() and not link_path.is_symlink():
        return
    cmd = _cmd_exe()
    if cmd:
        subprocess.run(
            [cmd, "/c", "rmdir", to_windows_path(link_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    if link_path.is_symlink():
        link_path.unlink()
        return
    raise RuntimeError(f"{link_path} 已存在且无法安全移除，请手动检查。")


def create_directory_link(link_path: Path, target_path: Path) -> None:
    cmd = _cmd_exe()
    if cmd:
        subprocess.run(
            [cmd, "/c", "mklink", "/J", to_windows_path(link_path), to_windows_path(target_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    os.symlink(target_path, link_path, target_is_directory=True)


def refresh_gamesave_link(save_root: str | Path | None = None) -> tuple[Path, Path]:
    target = resolve_save_root(save_root)
    link_path = GAMESAVE_LINK
    remove_existing_link(link_path)
    create_directory_link(link_path, target)
    return (link_path, target)
