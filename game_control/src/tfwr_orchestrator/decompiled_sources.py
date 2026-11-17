from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from .config import DECOMPILED_SOURCE_ROOT, normalize_config_path, resolve_game_managed_root, resolve_game_root


DECOMPILE_TARGETS = ("Assembly-CSharp.dll", "Core.dll", "mscorlib.dll")
MANIFEST_NAME = "source-manifest.json"
STEAM_MANIFEST_NAME = "appmanifest_2060160.acf"
MANIFEST_SCOPE = "现有三个程序集的完整反编译；源文件保留反编译器原始输出。"


@dataclass(frozen=True)
class StaleReason:
    """反编译事实源与当前游戏不一致的具体原因。"""

    assembly: str
    installed_sha256: str
    recorded_sha256: str | None

    def describe(self) -> str:
        recorded = self.recorded_sha256 or "未记录"
        return f"{self.assembly}: 游戏 {self.installed_sha256[:12]} ≠ 记录 {recorded[:12]}"


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ilspy_version() -> str:
    try:
        completed = subprocess.run(["ilspycmd", "--version"], check=False, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return "ilspycmd"
    version = (completed.stdout or completed.stderr).strip().splitlines()
    return f"ilspycmd {version[0].strip()}" if version else "ilspycmd"


def read_manifest(output_root: Path) -> dict[str, object] | None:
    path = output_root / MANIFEST_NAME
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def recorded_hashes(manifest: dict[str, object] | None) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item in (manifest or {}).get("assemblies", []):  # type: ignore[union-attr]
        if isinstance(item, dict) and item.get("assembly") and item.get("assembly_sha256"):
            hashes[str(item["assembly"])] = str(item["assembly_sha256"])
    return hashes


def find_stale(managed_root: Path, manifest: dict[str, object] | None) -> list[StaleReason]:
    """比较已安装 DLL 与清单记录；缺清单或哈希不同都算需要重新反编译。"""
    recorded = recorded_hashes(manifest)
    stale: list[StaleReason] = []
    for assembly_name in DECOMPILE_TARGETS:
        assembly_path = managed_root / assembly_name
        if not assembly_path.is_file():
            continue
        installed = sha256_file(assembly_path)
        if recorded.get(assembly_name) != installed:
            stale.append(StaleReason(assembly_name, installed, recorded.get(assembly_name)))
    return stale


def steam_build_id(game_root: Path) -> str | None:
    """从 Steam 的 appmanifest 读构建号；找不到时返回 None，不阻塞反编译。"""
    for parent in (game_root, *game_root.parents):
        candidate = parent / "steamapps" / STEAM_MANIFEST_NAME
        if not candidate.is_file():
            continue
        try:
            match = re.search(r'"buildid"\s+"(\d+)"', candidate.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            return None
        return match.group(1) if match else None
    return None


def write_manifest(output_root: Path, game_root: Path, managed_root: Path, jobs: list[tuple[Path, Path]]) -> Path:
    """按本次反编译结果重写来源清单，记录 DLL 与生成源码的哈希。"""
    assemblies = []
    for assembly_path, target_dir in jobs:
        sources = sorted(target_dir.rglob("*.cs"))
        if len(sources) != 1:
            raise RuntimeError(f"反编译输出不是单文件: {target_dir} -> {[path.name for path in sources]}")
        assemblies.append(
            {
                "assembly": assembly_path.name,
                "assembly_sha256": sha256_file(assembly_path),
                "source": f"{target_dir.name}/{sources[0].name}",
                "source_sha256": sha256_file(sources[0]),
            }
        )
    manifest = {
        "steam_app_id": 2060160,
        "steam_build_id": steam_build_id(game_root),
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "decompiler": ilspy_version(),
        "source_hash_line_endings": "LF",
        "scope": MANIFEST_SCOPE,
        "assemblies": assemblies,
    }
    path = output_root / MANIFEST_NAME
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def report_status(managed_root: Path, output_root: Path, manifest: dict[str, object] | None) -> bool:
    """打印是否与当前游戏一致；返回 True 表示最新。"""
    stale = find_stale(managed_root, manifest)
    recorded = recorded_hashes(manifest)
    build_id = (manifest or {}).get("steam_build_id") or "未记录"
    current = steam_build_id_from_managed(managed_root)
    print(f"managed_root {managed_root}")
    print(f"output_root {output_root}")
    print(f"记录构建 {build_id}；本机游戏构建 {current or '未知'}")
    for assembly_name in DECOMPILE_TARGETS:
        state = "过期" if any(item.assembly == assembly_name for item in stale) else "一致"
        print(f"  {assembly_name}: {state}（记录 {recorded.get(assembly_name, '无')[:12]}）")
    if not stale:
        print("反编译事实源已是最新。")
        return True
    print("反编译事实源落后于游戏，执行下面的命令更新：")
    print("  python3 game_control/tools/refresh_decompiled_sources.py")
    for item in stale:
        print(f"  {item.describe()}")
    return False


def steam_build_id_from_managed(managed_root: Path) -> str | None:
    """Managed 目录向上找到游戏根目录后读构建号，用于状态报告。"""
    for parent in (managed_root, *managed_root.parents):
        if (parent / "TheFarmerWasReplaced.exe").is_file():
            return steam_build_id(parent)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="核对或刷新反编译事实源（默认发现过期就重新反编译）")
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
    parser.add_argument("--check", action="store_true", help="只核对是否最新，不做反编译")
    parser.add_argument("--force", action="store_true", help="即使哈希一致也重新反编译")
    args = parser.parse_args(argv)

    game_root = resolve_game_root(args.game_root)
    managed_root = resolve_game_managed_root(game_root)
    output_root = resolve_output_root(args.output_root)
    manifest = read_manifest(output_root)

    if args.check:
        return 0 if report_status(managed_root, output_root, manifest) else 1

    if not args.force and not find_stale(managed_root, manifest):
        report_status(managed_root, output_root, manifest)
        print("无需重新反编译。")
        return 0

    jobs = resolve_decompile_jobs(managed_root, output_root)
    clear_output_root(output_root)
    print(f"game_root {game_root}")
    print(f"managed_root {managed_root}")
    print(f"output_root {output_root}")
    for assembly_path, target_dir in jobs:
        decompile_assembly(assembly_path, target_dir, managed_root)
        print(f"decompiled {assembly_path.name} -> {target_dir}")
    manifest_path = write_manifest(output_root, game_root, managed_root, jobs)
    print(f"清单 {manifest_path}")
    print("下一步：按 diff 更新 simulator/headless/Native/ 并重跑有代表性的模拟会话。")
    return 0
