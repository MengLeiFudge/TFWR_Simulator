from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from .config import GAMESAVE_LINK, LEADERBOARD_REFERENCE_ROOT


DEFAULT_LEADERBOARD_ITERATIONS = 10_000
FASTEST_RESET_ITERATIONS = 200


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
        return (LEADERBOARD_REFERENCE_ROOT, GAMESAVE_LINK)
    if direction == "save2cur":
        return (GAMESAVE_LINK, LEADERBOARD_REFERENCE_ROOT)
    raise ValueError(f"未知同步方向: {direction}")


def ensure_source_dir(path: Path) -> None:
    if path.is_dir():
        return
    raise FileNotFoundError(f"同步源目录不存在: {path}")


def ensure_target_dir(path: Path) -> None:
    if path == GAMESAVE_LINK:
        if path.is_dir():
            return
        raise FileNotFoundError(f"gamesave 目录不存在: {path}。请先运行 python3 tools/refresh_gamesave_link.py")
    path.mkdir(parents=True, exist_ok=True)


def leaderboard_enum_name_for_script(script_name: str) -> str:
    stem = Path(script_name).stem
    suffix = stem[3:] if stem.startswith("lb_") else stem
    return "_".join(part.capitalize() for part in suffix.split("_"))


def default_iterations_for_script(script_name: str) -> int:
    if Path(script_name).stem == "lb_fastest_reset":
        # 真实 lb_start.py 当前为 fastest_reset 使用 200 次，其余榜单统一 10000 次。
        return FASTEST_RESET_ITERATIONS
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


def sync_single_leaderboard_file(source_dir: Path, target_dir: Path, target_script_name: str) -> list[str]:
    ensure_source_dir(source_dir)
    ensure_target_dir(target_dir)
    normalized_name = normalize_target_script_name(target_script_name)
    source_file = source_dir / normalized_name
    if not source_file.is_file():
        raise FileNotFoundError(f"未找到目标脚本: {source_file}")

    copied: list[str] = []
    shutil.copy2(source_file, target_dir / normalized_name)
    copied.append(normalized_name)
    if target_dir == GAMESAVE_LINK:
        (target_dir / "lb_start.py").write_text(render_lb_start(normalized_name), encoding="utf-8")
        copied.append("lb_start.py")
    return copied


def sync_all_leaderboard_files(source_dir: Path, target_dir: Path) -> list[str]:
    ensure_source_dir(source_dir)
    ensure_target_dir(target_dir)

    copied: list[str] = []
    for source_file in sorted(source_dir.glob("lb_*.py")):
        if not source_file.is_file():
            continue
        shutil.copy2(source_file, target_dir / source_file.name)
        copied.append(source_file.name)
    return copied


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
