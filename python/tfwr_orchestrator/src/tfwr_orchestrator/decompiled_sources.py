from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess

from .config import DECOMPILED_SOURCE_ROOT, normalize_config_path, resolve_game_managed_root, resolve_game_root


DECOMPILE_TARGETS = ("Assembly-CSharp.dll", "Core.dll", "mscorlib.dll")


def resolve_output_root(output_root: str | Path | None) -> Path:
    if output_root is None:
        return DECOMPILED_SOURCE_ROOT
    return normalize_config_path(output_root).resolve()


def resolve_decompile_jobs(managed_root: Path, output_root: Path) -> list[tuple[Path, Path]]:
    jobs: list[tuple[Path, Path]] = []
    missing: list[str] = []
    for assembly_name in DECOMPILE_TARGETS:
        assembly_path = managed_root / assembly_name
        if not assembly_path.is_file():
            missing.append(assembly_name)
            continue
        jobs.append((assembly_path, output_root / assembly_path.stem))

    if missing:
        raise FileNotFoundError(f"Managed 目录缺少目标 DLL: {', '.join(missing)}")
    return jobs


def clear_output_root(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for child in output_root.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def build_ilspy_command(assembly_path: Path, output_dir: Path, managed_root: Path) -> list[str]:
    return [
        "ilspycmd",
        "--disable-updatecheck",
        "-r",
        str(managed_root),
        "-o",
        str(output_dir),
        str(assembly_path),
    ]


def decompile_assembly(assembly_path: Path, output_dir: Path, managed_root: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_ilspy_command(assembly_path, output_dir, managed_root), check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="清空 DecompiledSource 并重新反编译三个核心 DLL")
    parser.add_argument(
        "game_root",
        nargs="?",
        default=None,
        help="游戏根目录；不传时优先读取 TFWR_GAME_ROOT，再回退到默认 Steam 安装路径",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="反编译输出目录；默认使用 references/DecompiledSource",
    )
    args = parser.parse_args(argv)

    game_root = resolve_game_root(args.game_root)
    managed_root = resolve_game_managed_root(game_root)
    output_root = resolve_output_root(args.output_root)
    jobs = resolve_decompile_jobs(managed_root, output_root)

    clear_output_root(output_root)
    print(f"game_root {game_root}")
    print(f"managed_root {managed_root}")
    print(f"output_root {output_root}")
    for assembly_path, target_dir in jobs:
        decompile_assembly(assembly_path, target_dir, managed_root)
        print(f"decompiled {assembly_path.name} -> {target_dir}")
    return 0
