from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

PACKAGE_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = PACKAGE_DIR.parent
REPO_ROOT = SOURCE_ROOT.parent

if __package__ in (None, ""):
    # 兼容 `python .../src/runner.py` 直跑入口。
    sys.path.insert(0, str(SOURCE_ROOT))
    from gamesimulator.config import REPO_ROOT, resolve_save_root
    from gamesimulator.common.duration import Duration
    from gamesimulator.runtime.execution import Execution
    from gamesimulator.runtime.execute_exception import ExecuteException
    from gamesimulator.world.farm import FarmState
    from gamesimulator.leaderboard_metadata import default_start_items, resolve_leaderboard_metadata
    from gamesimulator.loader import build_global_bindings
    from gamesimulator.parser.parser import parse
    from gamesimulator.runtime.py_values import PyDict, PyNumber, PyString, PyTuple
    from gamesimulator.runtime.simulation import Simulation
    from gamesimulator.common.side_effects import SideEffect
    from gamesimulator.parser.tokenizer import tokenize
    from gamesimulator.unlock_snapshot import DEFAULT_UNLOCK_LEVELS, RESET_UNLOCK_LEVELS
else:
    from .config import REPO_ROOT, resolve_save_root
    from .common.duration import Duration
    from .runtime.execution import Execution
    from .runtime.execute_exception import ExecuteException
    from .world.farm import FarmState
    from .leaderboard_metadata import default_start_items, resolve_leaderboard_metadata
    from .loader import build_global_bindings
    from .parser.parser import parse
    from .runtime.py_values import PyDict, PyNumber, PyString, PyTuple
    from .runtime.simulation import Simulation
    from .common.side_effects import SideEffect
    from .parser.tokenizer import tokenize
    from .unlock_snapshot import DEFAULT_UNLOCK_LEVELS, RESET_UNLOCK_LEVELS

_PROGRAM_CACHE: dict[tuple[str, int, int], object] = {}
_GLOBAL_BINDINGS_CACHE: dict[tuple[str, int, int], dict[str, object]] = {}


@dataclass
class RunResult:
    target: str
    elapsed_seconds: float
    logs: list[str]
    terminated: bool
    final_farm: FarmState | None = None


@dataclass
class LeaderboardIterationResult:
    seed: int
    elapsed_seconds: float
    terminated: bool
    goal_reached: bool | None
    progress_text: str


def _file_signature(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return (str(path), stat.st_mtime_ns, stat.st_size)


def _clone_program(program):
    copies: dict[int, object] = {}
    return type(program)(
        syntax_tree=program.syntax_tree.deep_copy(copies),
        global_vars=set(program.global_vars),
        all_vars=set(program.all_vars),
        imported_modules=set(program.imported_modules),
    )


def _load_program(path: Path):
    signature = _file_signature(path)
    cached = _PROGRAM_CACHE.get(signature)
    if cached is None:
        code = path.read_text(encoding="utf-8")
        has_unknown, stream = tokenize(code)
        if has_unknown:
            raise ValueError(f"tokenizer found unknown token(s) in {path.name}")
        cached = parse(stream, file_name=path.name, source_text=code)
        _PROGRAM_CACHE.clear()
        _PROGRAM_CACHE[signature] = cached
    return _clone_program(cached)


def _load_global_bindings(save_root: Path) -> dict[str, object]:
    signature = _file_signature(save_root / "__builtins__.py")
    cached = _GLOBAL_BINDINGS_CACHE.get(signature)
    if cached is None:
        cached = build_global_bindings(save_root)
        _GLOBAL_BINDINGS_CACHE.clear()
        _GLOBAL_BINDINGS_CACHE[signature] = cached
    return cached


def resolve_target_path(target: str, save_root: str | Path | None) -> Path:
    save_root = save_root if isinstance(save_root, Path) else resolve_save_root(save_root)
    if target.endswith(".py"):
        return save_root / target
    return save_root / f"{target}.py"


def run_file(
    target: str,
    save_root: str | Path | None = None,
    seed: int = 1,
    log_sink: Callable[[str], None] | None = None,
    capture_logs: bool = True,
) -> RunResult:
    return run_file_with_context(
        target,
        save_root,
        seed=seed,
        unlock_levels=None,
        items=None,
        globals_override=None,
        log_sink=log_sink,
        capture_logs=capture_logs,
        run_kind="auto",
    )


def run_file_with_context(
    target: str,
    save_root: str | Path | None = None,
    seed: int = 1,
    unlock_levels: dict[object, int] | None = None,
    unlock_strings: list[str] | None = None,
    items: dict[object, float] | None = None,
    globals_override: dict[str, object] | None = None,
    log_sink: Callable[[str], None] | None = None,
    capture_logs: bool = True,
    run_kind: str = "auto",
    leaderboard_key: str | None = None,
) -> RunResult:
    resolved_save_root = resolve_save_root(save_root)
    path = resolve_target_path(target, resolved_save_root)
    program = _load_program(path)
    metadata = None
    if run_kind == "leaderboard" or (run_kind == "auto" and path.stem.startswith("lb_")):
        metadata = resolve_leaderboard_metadata(leaderboard_key or path.stem, resolved_save_root)
    leaderboard_type = "simulation" if run_kind == "simulation" else (metadata.leaderboard_type if metadata is not None else "none")
    leaderboard_name = "" if metadata is None else metadata.leaderboard_name
    single_drone = False if metadata is None else metadata.single_drone
    sim = Simulation(
        seed=seed,
        leaderboard_name=leaderboard_name,
        leaderboard_type=leaderboard_type,
        single_drone=single_drone,
    )
    sim.save_root = str(resolved_save_root)
    sim.log_sink = log_sink
    sim.capture_logs = capture_logs
    bindings = _load_global_bindings(resolved_save_root)
    global_bindings = dict(bindings)
    if globals_override:
        global_bindings.update(globals_override)
    farm_items = dict(_default_items(path.stem, bindings, resolved_save_root, metadata) if items is None else items)
    if unlock_strings is not None:
        sim.farm = _farm_from_unlock_strings(sim, bindings, unlock_strings, farm_items)
    else:
        sim.farm = FarmState(
            bindings,
            unlock_levels=dict(_default_unlock_levels(bindings, metadata) if unlock_levels is None else unlock_levels),
            items=farm_items,
        )
    sim.farm.random = sim.random_various
    execution = Execution(sim, program.syntax_tree, 1, global_bindings=global_bindings)
    _run_until_terminal(execution)
    terminated = all(
        state is None or state.current_side_effect == SideEffect.TERMINATED
        for state in execution.states
    )
    return RunResult(
        target=path.name,
        elapsed_seconds=sim.current_time.seconds,
        logs=list(sim.logs),
        terminated=terminated,
        final_farm=sim.farm,
    )


def _default_unlock_levels(bindings: dict[str, object], metadata=None) -> dict[object, int]:
    if metadata is not None and not metadata.everything_unlocked:
        return _reset_unlock_levels(bindings)
    levels: dict[object, int] = {}
    for unlock_name, level in DEFAULT_UNLOCK_LEVELS.items():
        if metadata is not None and metadata.single_drone:
            if unlock_name == "Megafarm":
                continue
            if unlock_name == "Expand":
                level = min(int(level), 5)
        try:
            unlock = bindings["Unlocks"].evaluate(unlock_name)
        except Exception:
            continue
        levels[unlock] = int(level)
    return levels


def _reset_unlock_levels(bindings: dict[str, object]) -> dict[object, int]:
    levels: dict[object, int] = {}
    for unlock_name, level in RESET_UNLOCK_LEVELS.items():
        try:
            unlock = bindings["Unlocks"].evaluate(unlock_name)
        except Exception:
            continue
        levels[unlock] = int(level)
    return levels


def _default_items(target_name: str, bindings: dict[str, object], save_root: str | Path, metadata=None) -> dict[object, float]:
    items: dict[object, float] = {}
    item_bag = bindings["Items"]
    if not target_name.startswith("lb_") or target_name == "lb_fastest_reset":
        return items
    for item_name, amount in default_start_items(target_name, save_root):
        items[item_bag.evaluate(item_name)] = float(amount)
    return items


def format_clock_time(seconds: float) -> str:
    total_milliseconds = max(0, int(round(seconds * 1000)))
    milliseconds = total_milliseconds % 1000
    total_seconds = total_milliseconds // 1000
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    return f"{minutes}:{secs:02d}.{milliseconds:03d}"


def leaderboard_goal_status(target_name: str, farm: FarmState | None) -> tuple[bool | None, str]:
    if farm is None:
        return None, "goal=missing-farm"
    save_root = getattr(getattr(farm, "sim", None), "save_root", None) or resolve_save_root()
    sim_leaderboard_name = getattr(getattr(farm, "sim", None), "leaderboard_name", "")
    metadata = resolve_leaderboard_metadata(sim_leaderboard_name or Path(target_name).stem, save_root)
    if metadata is None:
        return None, "goal=untracked"
    if metadata.goal_type == "item":
        resource_name = metadata.goal_resource
        amount = metadata.goal_amount
        current = int(farm.num_items(farm.item(resource_name)))
    else:
        resource_name = metadata.goal_resource
        amount = metadata.goal_amount
        current = int(farm.num_unlocked(farm.unlock(resource_name)))
    return current >= amount, f"{resource_name}={current}/{amount}"


def run_leaderboard_iteration(
    target: str,
    save_root: str | Path | None,
    seed: int,
    leaderboard_key: str | None = None,
) -> LeaderboardIterationResult:
    # 子进程只返回 summary，避免把整轮脚本明细日志来回复制。
    nested = run_file_with_context(
        target,
        save_root,
        seed=seed,
        capture_logs=False,
        run_kind="leaderboard",
        leaderboard_key=leaderboard_key,
    )
    goal_reached, progress_text = leaderboard_goal_status(target, nested.final_farm)
    return LeaderboardIterationResult(
        seed=seed,
        elapsed_seconds=nested.elapsed_seconds,
        terminated=nested.terminated,
        goal_reached=goal_reached,
        progress_text=progress_text,
    )


def _coerce_bag_key(key, bag_name: str, bindings: dict[str, object]):
    bag = bindings.get(bag_name)
    if bag is None or not hasattr(bag, "evaluate"):
        return key
    candidate_names = []
    name = getattr(key, "name", None)
    if isinstance(name, str) and name:
        candidate_names.append(name)
    if isinstance(key, PyString):
        candidate_names.append(key.text)
    text = str(key)
    if text:
        candidate_names.append(text.split(".")[-1])
        candidate_names.append(text)
    for candidate in candidate_names:
        try:
            return bag.evaluate(candidate)
        except Exception:
            continue
    return key


def coerce_unlock_levels(source, bindings: dict[str, object]) -> dict[object, int]:
    if isinstance(source, PyDict):
        result: dict[object, int] = _reset_unlock_levels(bindings)
        for key, boxed in source.items.items():
            if isinstance(key, PyString):
                raise ExecuteException("error_invalid_sim_unlocks")
            unlock = _coerce_bag_key(key, "Unlocks", bindings)
            level = int(float(boxed.obj.num))
            if level == 0:
                continue
            max_level = DEFAULT_UNLOCK_LEVELS.get(str(unlock).split(".")[-1], level)
            if level < 0:
                result[unlock] = int(max_level)
            else:
                result[unlock] = min(level, int(max_level))
        return result
    defaults = _default_unlock_levels(bindings)
    result = _reset_unlock_levels(bindings)
    for unlock in source:
        if isinstance(unlock, PyString):
            raise ExecuteException("error_invalid_sim_unlocks")
        current_unlock = _coerce_bag_key(unlock, "Unlocks", bindings)
        if isinstance(current_unlock, PyTuple) and len(current_unlock) == 2:
            if isinstance(current_unlock[0], PyString):
                raise ExecuteException("error_invalid_sim_unlocks")
            key = _coerce_bag_key(current_unlock[0], "Unlocks", bindings)
            level = int(float(current_unlock[1].num))
            if level == 0:
                continue
            max_level = DEFAULT_UNLOCK_LEVELS.get(str(key).split(".")[-1], level)
            if level < 0:
                result[key] = int(max_level)
            else:
                result[key] = min(level, int(max_level))
            continue
        result[current_unlock] = defaults.get(current_unlock, 1)
    return result


def coerce_unlock_strings(source, bindings: dict[str, object], single_drone: bool = False) -> list[str]:
    result = [name.lower() for name in RESET_UNLOCK_LEVELS.keys()]

    def unlock_name_of(value) -> str:
        if isinstance(value, PyString):
            raise ExecuteException("error_invalid_sim_unlocks")
        unlock = _coerce_bag_key(value, "Unlocks", bindings)
        return str(unlock).split(".")[-1]

    if isinstance(source, PyDict):
        for key, boxed in source.items.items():
            name = unlock_name_of(key)
            level = int(float(boxed.obj.num))
            if level == 0:
                continue
            max_level = int(DEFAULT_UNLOCK_LEVELS.get(name, max(level, 1)))
            if level < 0:
                level = max_level
            else:
                level = min(level, max_level)
            result.append(name.lower())
            if max_level > 1:
                if single_drone and name == "Expand":
                    level = min(level, 5)
                result.append(f"{name.lower()}_{level}")
        return result

    defaults = _default_unlock_levels(bindings)
    for unlock in source:
        if isinstance(unlock, PyString):
            raise ExecuteException("error_invalid_sim_unlocks")
        current_unlock = _coerce_bag_key(unlock, "Unlocks", bindings)
        if isinstance(current_unlock, PyTuple) and len(current_unlock) == 2:
            name = unlock_name_of(current_unlock[0])
            level = int(float(current_unlock[1].num))
            if level == 0:
                continue
            max_level = int(DEFAULT_UNLOCK_LEVELS.get(name, max(level, 1)))
            if level < 0:
                level = max_level
            else:
                level = min(level, max_level)
            result.append(name.lower())
            if max_level > 1:
                if single_drone and name == "Expand":
                    level = min(level, 5)
                result.append(f"{name.lower()}_{level}")
            continue
        name = str(current_unlock).split(".")[-1]
        result.append(name.lower())
        max_level = defaults.get(current_unlock, 1)
        if max_level > 1:
            if single_drone and name == "Expand":
                result.append(f"{name.lower()}_5")
            elif not (single_drone and name == "Megafarm"):
                result.append(f"{name.lower()}_{int(max_level)}")
    return result


def _farm_from_unlock_strings(
    sim: Simulation,
    bindings: dict[str, object],
    unlock_strings: list[str],
    items: dict[object, float],
) -> FarmState:
    farm = FarmState(bindings, unlock_levels=_reset_unlock_levels(bindings), items=items)
    sim.farm = farm
    unlock_name_map = {
        key.lower(): key
        for key in DEFAULT_UNLOCK_LEVELS.keys()
    }
    for raw_unlock in unlock_strings:
        name = raw_unlock
        level = 1
        if "_" in raw_unlock and not raw_unlock.startswith("debug_"):
            maybe_name, maybe_level = raw_unlock.rsplit("_", 1)
            if maybe_level.isdigit():
                name = maybe_name
                level = int(maybe_level)
        canonical_name = unlock_name_map.get(name, name)
        unlock = bindings["Unlocks"].evaluate(canonical_name)
        current = farm.num_unlocked(unlock)
        if current == level:
            continue
        farm.unlock_levels[unlock] = level
        farm.refresh_entity_costs()
        if name == "expand":
            farm.grid.reset_for_expand(level)
            farm.restart_world_grass()
        elif name == "speed":
            sim.change_execution_speed(farm.max_speed_factor())
    sim._timers.clear()
    farm._resource_timers_started = False
    farm.start_runtime_timers()
    sim.change_execution_speed(farm.max_speed_factor())
    return farm


def coerce_items(source, bindings: dict[str, object]) -> dict[object, float]:
    if isinstance(source, PyDict):
        result: dict[object, float] = {}
        for key, boxed in source.items.items():
            if isinstance(key, PyString):
                raise ExecuteException("error_invalid_sim_items")
            result[_coerce_bag_key(key, "Items", bindings)] = max(0.0, float(boxed.obj.num))
        return result
    return {}


def coerce_globals(source) -> dict[str, object]:
    if isinstance(source, PyDict):
        result: dict[str, object] = {}
        for key, boxed in source.items.items():
            if not isinstance(key, PyString):
                raise ExecuteException("error_invalid_sim_globals")
            key_text = key.text
            result[key_text] = boxed.obj
        return result
    return {}


def _run_until_terminal(execution: Execution, max_cycles: int = 200000) -> None:
    cycles = 0
    sim = execution.sim
    sim.start_program_execution(execution)
    while cycles < max_cycles:
        if not sim.is_executing():
            return
        sim.run_next_step(sim.current_time + Duration.from_seconds(1.0), stop_on_finished=True)
        cycles += 1
    raise RuntimeError("runner reached max_cycles before termination")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m gamesimulator.runner <target> [seed] [speedup] [save_root]")
        return 2
    target = argv[0]
    seed = int(argv[1]) if len(argv) >= 2 else 1
    if len(argv) >= 4:
        save_root = argv[3]
    elif len(argv) >= 3:
        save_root = argv[2]
    else:
        save_root = None
    result = run_file(
        target,
        save_root,
        seed=seed,
        log_sink=lambda line: print(line, flush=True),
        capture_logs=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
