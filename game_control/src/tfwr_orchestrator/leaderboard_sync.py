from __future__ import annotations

import ast
import argparse
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
import shutil
from uuid import uuid4

from .config import GAMESAVE_LINK, LEADERBOARD_SCRIPT_ROOT, REPO_ROOT, resolve_oracle_state_path
from .real_game_runner import read_state_file, state_transaction


DEFAULT_LEADERBOARD_ITERATIONS = 10_000
FASTEST_RESET_ITERATIONS = 200
SCRIPT_ITERATION_OVERRIDES = {
    "lb_dinosaur": 1_000,
    "lb_maze_single": 1_000,
    "lb_pumpkins": 20_000,
    "lb_sunflowers_single": 1_000,
}


UNSUPPORTED_GAME_SYNTAX = {
    ast.LShift: "<<",
    ast.RShift: ">>",
}


class UnsupportedGameSyntaxError(ValueError):
    pass


def normalize_target_script_name(target_script: str) -> str:
    value = target_script.strip()
    if not value:
        raise ValueError("目标脚本名不能为空")
    if not value.endswith(".py"):
        value = f"{value}.py"
    if not value.startswith("lb_"):
        raise ValueError(f"目标脚本必须是 lb_*.py：{value}")
    if value == "lb_start.py":
        raise ValueError("目标脚本不能是 lb_start.py；请传实际榜单脚本名")
    return value


def resolve_sync_paths(direction: str) -> tuple[Path, Path]:
    if direction == "cur2save":
        return (LEADERBOARD_SCRIPT_ROOT, GAMESAVE_LINK)
    if direction == "save2cur":
        return (GAMESAVE_LINK, LEADERBOARD_SCRIPT_ROOT)
    raise ValueError(f"未知同步方向: {direction}")


def ensure_source_dir(path: Path) -> None:
    if path.is_dir():
        return
    raise FileNotFoundError(f"同步源目录不存在: {path}")


def ensure_target_dir(path: Path) -> None:
    if path == GAMESAVE_LINK:
        if path.is_dir():
            return
        raise FileNotFoundError(
            f"gamesave 目录不存在: {path}。请先运行 python3 game_control/tools/refresh_gamesave_link.py"
        )
    path.mkdir(parents=True, exist_ok=True)


def leaderboard_enum_name_for_script(script_name: str) -> str:
    stem = Path(script_name).stem
    suffix = stem[3:] if stem.startswith("lb_") else stem
    return "_".join(part.capitalize() for part in suffix.split("_"))


def default_iterations_for_script(script_name: str) -> int:
    stem = Path(script_name).stem
    if stem == "lb_fastest_reset":
        # 真实 lb_start.py 当前为 fastest_reset 使用 200，其余榜单默认 10000；个别榜单按实测覆盖。
        return FASTEST_RESET_ITERATIONS
    if stem in SCRIPT_ITERATION_OVERRIDES:
        return SCRIPT_ITERATION_OVERRIDES[stem]
    return DEFAULT_LEADERBOARD_ITERATIONS


def render_lb_start(target_script_name: str) -> str:
    script_name = normalize_target_script_name(target_script_name)
    script_stem = Path(script_name).stem
    leaderboard_enum = leaderboard_enum_name_for_script(script_name)
    iterations = default_iterations_for_script(script_name)
    return (
        "from __builtins__ import *\n\n"
        f'leaderboard_run(Leaderboards.{leaderboard_enum}, "{script_stem}", {iterations})\n'
    )


def validate_game_compatible_script(path: Path) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        raise

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            operator = UNSUPPORTED_GAME_SYNTAX.get(type(node.op))
            if operator is not None:
                raise UnsupportedGameSyntaxError(
                    f"游戏脚本不支持运算符 {operator}: {path.name}:L{node.lineno}"
                )


def sync_single_leaderboard_file(source_dir: Path, target_dir: Path, target_script_name: str) -> list[str]:
    ensure_source_dir(source_dir)
    ensure_target_dir(target_dir)
    normalized_name = normalize_target_script_name(target_script_name)
    source_file = source_dir / normalized_name
    if not source_file.is_file():
        raise FileNotFoundError(f"未找到目标脚本: {source_file}")
    validate_game_compatible_script(source_file)

    names = [normalized_name, 'lb_start.py'] if target_dir == GAMESAVE_LINK else [normalized_name]
    with save_sync_transaction(target_dir, names):
        shutil.copy2(source_file, target_dir / normalized_name)
        if target_dir == GAMESAVE_LINK:
            (target_dir / 'lb_start.py').write_text(render_lb_start(normalized_name), encoding='utf-8')
    return names


def sync_all_leaderboard_files(source_dir: Path, target_dir: Path) -> list[str]:
    ensure_source_dir(source_dir)
    ensure_target_dir(target_dir)

    sources = [path for path in sorted(source_dir.glob('lb_*.py')) if path.is_file()]
    for source_file in sources:
        validate_game_compatible_script(source_file)
    names = [path.name for path in sources]
    with save_sync_transaction(target_dir, names):
        for source_file in sources:
            shutil.copy2(source_file, target_dir / source_file.name)
    return names


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="同步 leaderboard 脚本；默认只同步单个目标脚本。")
    parser.add_argument(
        "direction",
        nargs="?",
        default="cur2save",
        choices=("cur2save", "save2cur"),
        help="同步方向，默认 cur2save。",
    )
    parser.add_argument(
        "--script",
        dest="target_script",
        default=None,
        help="单个目标脚本名，可带或不带 .py。",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="显式同步全部 lb_*.py；未传时默认要求提供 --script。",
    )
    return parser


@contextmanager
def save_sync_transaction(target_dir: Path, names: list[str]) -> Iterator[None]:
    """写真实存档时持有请求锁，拒绝活动或未知状态；反向同步不占用游戏。"""
    if target_dir != GAMESAVE_LINK or not names:
        yield
        return
    state_path = resolve_oracle_state_path()
    with state_transaction(state_path):
        state = read_state_file(state_path)
        legacy_idle = state is not None and state.get('protocol_version', 1) in (1, 2)
        live_keys = ('executing', 'leaderboard_running', 'leaderboard_screen', 'saving')
        # 旧模组发布的前三个实时字段；缺 saving 才说明是版本能力不足。
        published_live_keys = live_keys[:3]
        if state is None or state.get('status') != 'idle' or any(
            state.get(key, False if legacy_idle else None) is not False for key in live_keys
        ) or state.get('busy_windows'):
            if (state is not None and state.get('status') == 'idle' and not legacy_idle
                    and all(key in state for key in published_live_keys) and 'saving' not in state):
                raise RuntimeError('模组版本过旧，未发布后台保存状态 saving，无法确认写盘已结束；'
                                   '先把 TFWR Oracle Runner 升级到 0.3.1 并重启游戏，再同步存档脚本。')
            raise RuntimeError('模组尚未确认空闲，不能覆盖存档脚本；先停止并回收请求，并等待实时空闲状态刷新。')
        for name in names:
            if not (target_dir / name).is_file():
                raise FileNotFoundError(f'存档缺少已有脚本，不允许同步新增文件：{name}')
        backup_dir = REPO_ROOT / '.codex' / 'tmp' / 'leaderboard-sync' / uuid4().hex
        backup_dir.mkdir(parents=True)
        for name in names:
            shutil.copy2(target_dir / name, backup_dir / name)
        yield


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    source_dir, target_dir = resolve_sync_paths(args.direction)

    if args.all:
        copied = sync_all_leaderboard_files(source_dir, target_dir)
    else:
        if not args.target_script:
            raise SystemExit("默认只同步单个脚本；请传 --script lb_xxx，或显式使用 --all。")
        copied = sync_single_leaderboard_file(source_dir, target_dir, args.target_script)

    print(f"sync_direction {args.direction}")
    print(f"sync_source {source_dir}")
    print(f"sync_target {target_dir}")
    for name in copied:
        print(f"copied {name}")
    return 0
