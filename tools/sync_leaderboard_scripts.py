from __future__ import annotations

from pathlib import Path
import shutil
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from gamesimulator.config import LEADERBOARD_LINK, LEADERBOARD_REFERENCE_ROOT


VALID_DIRECTIONS = {"cur2save", "save2cur"}


def resolve_direction(argv: list[str], input_func=None) -> str:
    if input_func is None:
        input_func = input
    if argv:
        direction = argv[0].strip()
        if direction in VALID_DIRECTIONS:
            return direction
        raise SystemExit(
            "usage: python tools/sync_leaderboard_scripts.py [cur2save|save2cur]"
        )

    print("请选择同步方向：")
    print(f"1. cur2save  ({LEADERBOARD_REFERENCE_ROOT} -> {LEADERBOARD_LINK})")
    print(f"2. save2cur  ({LEADERBOARD_LINK} -> {LEADERBOARD_REFERENCE_ROOT})")
    while True:
        choice = input_func("请输入 1 或 2: ").strip()
        if choice == "1":
            return "cur2save"
        if choice == "2":
            return "save2cur"
        print("无效输入，请重新输入 1 或 2。")


def resolve_sync_paths(direction: str) -> tuple[Path, Path]:
    if direction == "cur2save":
        return LEADERBOARD_REFERENCE_ROOT, LEADERBOARD_LINK
    if direction == "save2cur":
        return LEADERBOARD_LINK, LEADERBOARD_REFERENCE_ROOT
    raise ValueError(f"未知同步方向: {direction}")


def ensure_source_dir(path: Path) -> None:
    if path.is_dir():
        return
    raise FileNotFoundError(f"同步源目录不存在: {path}")


def ensure_target_dir(path: Path) -> None:
    if path == LEADERBOARD_LINK:
        if path.is_dir():
            return
        raise FileNotFoundError(
            f"leaderboard 目录不存在: {path}。请先运行 python tools/refresh_leaderboard_link.py"
        )
    path.mkdir(parents=True, exist_ok=True)


def sync_leaderboard_files(source_dir: Path, target_dir: Path) -> list[str]:
    ensure_source_dir(source_dir)
    ensure_target_dir(target_dir)

    copied: list[str] = []
    for source_file in sorted(source_dir.glob("lb_*.py")):
        if not source_file.is_file():
            continue
        shutil.copy2(source_file, target_dir / source_file.name)
        copied.append(source_file.name)
    return copied


def main(argv: list[str] | None = None) -> int:
    direction = resolve_direction(list(sys.argv[1:] if argv is None else argv))
    source_dir, target_dir = resolve_sync_paths(direction)
    copied = sync_leaderboard_files(source_dir, target_dir)
    print(f"sync_direction {direction}")
    print(f"sync_source {source_dir}")
    print(f"sync_target {target_dir}")
    if copied:
        for name in copied:
            print(f"copied {name}")
    else:
        print("copied 0 files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
