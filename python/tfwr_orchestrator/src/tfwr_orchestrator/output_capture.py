from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import resolve_bepinex_log_path, resolve_output_path


@dataclass(frozen=True)
class FileSignature:
    exists: bool
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class OutputBaseline:
    game_output_path: Path | None
    game_output_signature: FileSignature
    mod_output_path: Path | None
    mod_output_signature: FileSignature


@dataclass(frozen=True)
class CapturedOutputs:
    game_output_lines: tuple[str, ...]
    mod_output_lines: tuple[str, ...]


EMPTY_SIGNATURE = FileSignature(False, 0, 0)


def file_signature(path: Path | None) -> FileSignature:
    if path is None or not path.exists():
        return EMPTY_SIGNATURE
    stat = path.stat()
    return FileSignature(True, stat.st_size, stat.st_mtime_ns)


def _read_appended_bytes(path: Path | None, start_signature: FileSignature) -> bytes:
    if path is None or not path.exists():
        return b""

    payload = path.read_bytes()
    if not start_signature.exists:
        return payload
    if len(payload) < start_signature.size:
        return payload
    return payload[start_signature.size :]


def read_appended_lines(path: Path | None, start_signature: FileSignature) -> tuple[str, ...]:
    payload = _read_appended_bytes(path, start_signature)
    if not payload:
        return ()
    return tuple(payload.decode("utf-8", errors="ignore").splitlines())


def capture_output_baseline(
    *,
    save_root: str | Path | None = None,
    game_root: str | Path | None = None,
) -> OutputBaseline:
    game_output_path = resolve_output_path(save_root, required=False)
    mod_output_path = resolve_bepinex_log_path(game_root, required=False)
    return OutputBaseline(
        game_output_path=game_output_path,
        game_output_signature=file_signature(game_output_path),
        mod_output_path=mod_output_path,
        mod_output_signature=file_signature(mod_output_path),
    )


def capture_request_outputs(baseline: OutputBaseline) -> CapturedOutputs:
    return CapturedOutputs(
        game_output_lines=read_appended_lines(baseline.game_output_path, baseline.game_output_signature),
        mod_output_lines=read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature),
    )
