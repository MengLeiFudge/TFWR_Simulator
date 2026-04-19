from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .runtime.py_values import GridDirection, PyConstBag, PyGridDirection

_BUILTINS_MODULE_CACHE: dict[tuple[str, int, int], Any] = {}
_GLOBAL_BINDINGS_CACHE: dict[tuple[str, int, int], dict[str, Any]] = {}


def _path_signature(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return (str(path), stat.st_mtime_ns, stat.st_size)


def load_tfwr_builtins(save_root: str | Path):
    save_root = Path(save_root)
    builtins_path = save_root / "__builtins__.py"
    signature = _path_signature(builtins_path)
    cached = _BUILTINS_MODULE_CACHE.get(signature)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location("tfwr_builtins_runtime", builtins_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    _BUILTINS_MODULE_CACHE.clear()
    _BUILTINS_MODULE_CACHE[signature] = module
    return module


def build_global_bindings(save_root: str | Path) -> dict[str, Any]:
    save_root = Path(save_root)
    signature = _path_signature(save_root / "__builtins__.py")
    cached = _GLOBAL_BINDINGS_CACHE.get(signature)
    if cached is not None:
        return cached
    module = load_tfwr_builtins(save_root)
    bindings: dict[str, Any] = {}
    for name in ("Items", "Entities", "Grounds", "Unlocks", "Hats", "Leaderboards"):
        if hasattr(module, name):
            bindings[name] = PyConstBag(_export_namespace(getattr(module, name)), name)
    bindings["North"] = PyGridDirection(GridDirection.NORTH)
    bindings["East"] = PyGridDirection(GridDirection.EAST)
    bindings["South"] = PyGridDirection(GridDirection.SOUTH)
    bindings["West"] = PyGridDirection(GridDirection.WEST)
    _GLOBAL_BINDINGS_CACHE.clear()
    _GLOBAL_BINDINGS_CACHE[signature] = bindings
    return bindings


def _export_namespace(namespace: Any) -> dict[str, Any]:
    exported = {}
    namespace_name = getattr(namespace, "__name__", namespace.__class__.__name__)
    for attr in dir(namespace):
        if attr.startswith("_"):
            continue
        value = getattr(namespace, attr)
        if callable(value):
            continue
        exported[attr] = value
    for attr, annotation in getattr(namespace, "__annotations__", {}).items():
        if attr.startswith("_") or attr in exported:
            continue
        exported[attr] = _materialize_annotation_value(namespace_name, attr, annotation)
    return exported


def _materialize_annotation_value(namespace_name: str, name: str, annotation: Any) -> Any:
    return _GeneratedConst(namespace_name, name)


class _GeneratedConst:
    def __init__(self, namespace_name: str, name: str):
        self.namespace_name = namespace_name
        self.name = name

    def __repr__(self) -> str:
        return f"{self.namespace_name}.{self.name}"

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash((self.namespace_name, self.name))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, _GeneratedConst)
            and other.namespace_name == self.namespace_name
            and other.name == self.name
        )
