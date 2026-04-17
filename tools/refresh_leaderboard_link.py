from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from gamesimulator.config import LEADERBOARD_LINK, resolve_save_root, to_windows_path


def _cmd_exe() -> str | None:
    if os.name == "nt":
        return "cmd"
    candidate = shutil.which("cmd.exe")
    return candidate


def _remove_existing_link(link_path: Path) -> None:
    if not link_path.exists() and not link_path.is_symlink():
        return
    cmd = _cmd_exe()
    if cmd:
        subprocess.run(
            [cmd, "/c", "rmdir", to_windows_path(link_path)],
            check=True,
        )
        return
    if link_path.is_symlink():
        link_path.unlink()
        return
    raise RuntimeError(f"{link_path} 已存在且无法安全移除，请手动检查。")


def _create_link(link_path: Path, target_path: Path) -> None:
    cmd = _cmd_exe()
    if cmd:
        subprocess.run(
            [cmd, "/c", "mklink", "/J", to_windows_path(link_path), to_windows_path(target_path)],
            check=True,
        )
        return
    os.symlink(target_path, link_path, target_is_directory=True)


def main() -> int:
    target = resolve_save_root()
    link_path = LEADERBOARD_LINK
    _remove_existing_link(link_path)
    _create_link(link_path, target)
    print(f"leaderboard_link {link_path} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
