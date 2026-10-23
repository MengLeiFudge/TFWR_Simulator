from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os
import time

from .config import (normalize_config_path, to_windows_path, resolve_bepinex_log_path,
                     resolve_output_path, resolve_unity_log_path)


@dataclass(frozen=True)
class FileSignature:
    exists: bool
    size: int
    mtime_ns: int
    device: int = 0
    inode: int = 0


@dataclass(frozen=True)
class OutputBaseline:
    game_output_path: Path | None
    game_output_signature: FileSignature
    mod_output_path: Path | None
    mod_output_signature: FileSignature
    unity_log_path: Path | None = None
    unity_log_signature: FileSignature = FileSignature(False, 0, 0)


@dataclass(frozen=True)
class CapturedOutputs:
    game_output_lines: tuple[str, ...]
    mod_output_lines: tuple[str, ...]
    unity_log_lines: tuple[str, ...] = ()


EMPTY_SIGNATURE = FileSignature(False, 0, 0)
FILE_READ_MAX_ATTEMPTS = 20
FILE_READ_RETRY_SECONDS = 0.05

def serialize_baseline(baseline: OutputBaseline) -> dict:
    """保存三份输出起点；Windows路径形式允许同一profile由WSL或Windows客户端恢复。"""
    values = asdict(baseline)
    for name in ('game_output_path', 'mod_output_path', 'unity_log_path'):
        path = values[name]
        values[name] = to_windows_path(path) if path is not None else None
    return values


def deserialize_baseline(values: dict) -> OutputBaseline:
    """恢复请求投递时的文件身份和偏移，不用当前文件末尾替代历史起点。"""
    fields = dict(values)
    for name in ('game_output', 'mod_output', 'unity_log'):
        path = fields[name + '_path']
        fields[name + '_path'] = normalize_config_path(path) if path is not None else None
        fields[name + '_signature'] = FileSignature(**fields[name + '_signature'])
    return OutputBaseline(**fields)


def read_log_tail(path: Path | None, max_lines: int, max_bytes: int = 1048576) -> tuple[str, ...]:
    """从尾部读取展示用日志，最多1MiB；不把截断的首行当成完整记录。"""
    if path is None or max_lines <= 0:
        return ()
    for attempt in range(FILE_READ_MAX_ATTEMPTS):
        try:
            with path.open('rb') as stream:
                end = stream.seek(0, os.SEEK_END)
                start = end
                chunks = []
                lines = 0
                while start > 0 and lines <= max_lines and end - start < max_bytes:
                    count = min(8192, start, max_bytes - (end - start))
                    start -= count
                    stream.seek(start)
                    chunk = stream.read(count)
                    chunks.append(chunk)
                    lines += chunk.count(b'\n')
                rows = b''.join(reversed(chunks)).splitlines()
                if start and rows:
                    rows.pop(0)
                return tuple(row.decode('utf-8', errors='replace') for row in rows[-max_lines:])
        except FileNotFoundError:
            return ()
        except OSError:
            if attempt + 1 == FILE_READ_MAX_ATTEMPTS:
                raise
            time.sleep(FILE_READ_RETRY_SECONDS)
    return ()


def file_signature(path: Path | None) -> FileSignature:
    if path is None or not path.exists():
        return EMPTY_SIGNATURE
    stat = path.stat()
    return FileSignature(True, stat.st_size, stat.st_mtime_ns, stat.st_dev, stat.st_ino)


def _read_appended_bytes(path: Path | None, start_signature: FileSignature) -> bytes:
    if path is None or not path.exists():
        return b""

    return read_bytes_with_retries(path, start_signature)


def read_bytes_with_retries(path: Path, start_signature: FileSignature = EMPTY_SIGNATURE) -> bytes:
    """从基准偏移读取；日志被替换或截断时从头读取新文件。"""
    last_error: BaseException | None = None
    for attempt in range(FILE_READ_MAX_ATTEMPTS):
        try:
            with path.open("rb") as handle:
                stat = os.fstat(handle.fileno())
                same_file = not start_signature.inode or (
                    stat.st_dev == start_signature.device and stat.st_ino == start_signature.inode
                )
                if start_signature.exists and same_file and stat.st_size >= start_signature.size:
                    handle.seek(start_signature.size)
                return handle.read()
        except (OSError, PermissionError) as exc:
            last_error = exc
            if attempt + 1 >= FILE_READ_MAX_ATTEMPTS:
                break
            time.sleep(FILE_READ_RETRY_SECONDS)
    raise RuntimeError(f"读取文件失败: {path}") from last_error


def read_appended_lines(path: Path | None, start_signature: FileSignature) -> tuple[str, ...]:
    payload = _read_appended_bytes(path, start_signature)
    if not payload:
        return ()
    return tuple(payload.decode("utf-8", errors="ignore").splitlines())


@dataclass
class LogCursor:
    """运行中日志游标；只返回新完成的行，跨轮询保留 UTF-8 字节和半行。"""

    path: Path | None
    signature: FileSignature
    pending: bytes = b""

    def read_lines(self) -> tuple[str, ...]:
        """读取新增完整行；文件替换或缩短时清除上一文件的半行。"""
        if self.path is None:
            return ()
        last_error: OSError | None = None
        for attempt in range(FILE_READ_MAX_ATTEMPTS):
            try:
                with self.path.open("rb") as handle:
                    stat = os.fstat(handle.fileno())
                    same_file = not self.signature.inode or (
                        stat.st_dev == self.signature.device and stat.st_ino == self.signature.inode
                    )
                    reset = not same_file or stat.st_size < self.signature.size
                    offset = 0 if reset else self.signature.size
                    handle.seek(offset)
                    payload = handle.read()
                    position = handle.tell()
                pending = b"" if reset else self.pending
                parts = (pending + payload).split(b"\n")
                self.pending = parts.pop()
                self.signature = FileSignature(True, position, stat.st_mtime_ns, stat.st_dev, stat.st_ino)
                return tuple(line.rstrip(b"\r").decode("utf-8", errors="replace") for line in parts)
            except FileNotFoundError:
                return ()
            except OSError as exc:
                last_error = exc
                if attempt + 1 < FILE_READ_MAX_ATTEMPTS:
                    time.sleep(FILE_READ_RETRY_SECONDS)
        raise RuntimeError(f"增量读取日志失败: {self.path}") from last_error


def capture_output_baseline(
    *,
    save_root: str | Path | None = None,
    game_root: str | Path | None = None,
    bepinex_root: str | Path | None = None,
) -> OutputBaseline:
    game_output_path = resolve_output_path(save_root, required=False)
    mod_output_path = resolve_bepinex_log_path(game_root, required=False, bepinex_root=bepinex_root)
    unity_log_path = resolve_unity_log_path(save_root, required=False)
    return OutputBaseline(
        game_output_path=game_output_path,
        game_output_signature=file_signature(game_output_path),
        mod_output_path=mod_output_path,
        mod_output_signature=file_signature(mod_output_path),
        unity_log_path=unity_log_path,
        unity_log_signature=file_signature(unity_log_path),
    )


def capture_request_outputs(baseline: OutputBaseline, *, execution_started: bool = False) -> CapturedOutputs:
    """已启动脚本的 output.txt 从头读；启动前失败只读追加诊断，避免混入上次输出。"""
    return CapturedOutputs(
        game_output_lines=read_appended_lines(
            baseline.game_output_path, EMPTY_SIGNATURE if execution_started else baseline.game_output_signature
        ),
        mod_output_lines=read_appended_lines(baseline.mod_output_path, baseline.mod_output_signature),
        unity_log_lines=read_appended_lines(baseline.unity_log_path, baseline.unity_log_signature),
    )
