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
    from gamesimulator.world.farm import FarmState
    from gamesimulator.loader import build_global_bindings
    from gamesimulator.parser.parser import parse
    from gamesimulator.runtime.py_values import PyDict, PyNumber, PyString
    from gamesimulator.runtime.simulation import Simulation
    from gamesimulator.common.side_effects import SideEffect
    from gamesimulator.parser.tokenizer import tokenize
    from gamesimulator.unlock_snapshot import DEFAULT_UNLOCK_LEVELS
else:
    from .config import REPO_ROOT, resolve_save_root
    from .common.duration import Duration
    from .runtime.execution import Execution
    from .world.farm import FarmState
    from .loader import build_global_bindings
    from .parser.parser import parse
    from .runtime.py_values import PyDict, PyNumber, PyString
    from .runtime.simulation import Simulation
    from .common.side_effects import SideEffect
    from .parser.tokenizer import tokenize
    from .unlock_snapshot import DEFAULT_UNLOCK_LEVELS


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
    progress_text: str


def resolve_target_path(target: str, save_root: str | Path | None) -> Path:
    save_root = resolve_save_root(save_root)
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
    )


def run_file_with_context(
    target: str,
    save_root: str | Path | None = None,
    seed: int = 1,
    unlock_levels: dict[object, int] | None = None,
    items: dict[object, float] | None = None,
    globals_override: dict[str, object] | None = None,
    log_sink: Callable[[str], None] | None = None,
    capture_logs: bool = True,
) -> RunResult:
    resolved_save_root = resolve_save_root(save_root)
    path = resolve_target_path(target, resolved_save_root)
    code = path.read_text(encoding="utf-8")
    has_unknown, stream = tokenize(code)
    if has_unknown:
        raise ValueError(f"tokenizer found unknown token(s) in {path.name}")
    program = parse(stream)
    sim = Simulation(seed=seed)
    sim.save_root = str(resolved_save_root)
    sim.log_sink = log_sink
    sim.capture_logs = capture_logs
    bindings = build_global_bindings(resolved_save_root)
    global_bindings = dict(bindings)
    if globals_override:
        global_bindings.update(globals_override)
    sim.farm = FarmState(
        bindings,
        unlock_levels=dict(_default_unlock_levels(bindings) if unlock_levels is None else unlock_levels),
        items=dict(_default_items(path.stem, bindings) if items is None else items),
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


def _default_unlock_levels(bindings: dict[str, object]) -> dict[object, int]:
    levels: dict[object, int] = {}
    for unlock_name, level in DEFAULT_UNLOCK_LEVELS.items():
        try:
            unlock = bindings["Unlocks"].evaluate(unlock_name)
        except Exception:
            continue
        levels[unlock] = int(level)
    return levels


def _default_items(target_name: str, bindings: dict[str, object]) -> dict[object, float]:
    items: dict[object, float] = {}
    item_bag = bindings["Items"]
    if not target_name.startswith("lb_") or target_name == "lb_fastest_reset":
        return items
    base_name = target_name[:-7] if target_name.endswith("_single") else target_name
    prereq_map = {
        "lb_hay": (),
        "lb_wood": (),
        "lb_carrots": ("Hay", "Wood"),
        "lb_pumpkins": ("Carrot",),
        "lb_cactus": ("Pumpkin",),
        "lb_dinosaur": ("Cactus",),
        "lb_maze": ("Weird_Substance",),
        "lb_sunflowers": ("Carrot",),
    }
    for item_name in prereq_map.get(base_name, ()):
        items[item_bag.evaluate(item_name)] = 1_000_000_000.0
    if target_name not in ("lb_sunflowers", "lb_sunflowers_single"):
        items[item_bag.evaluate("Power")] = 1_000_000_000.0
    return items


_LEADERBOARD_GOALS: dict[str, tuple[str, str, int]] = {
    "lb_fastest_reset": ("unlock", "Leaderboard", 1),
    "lb_hay": ("item", "Hay", 2_000_000_000),
    "lb_hay_single": ("item", "Hay", 200_000_000),
    "lb_wood": ("item", "Wood", 10_000_000_000),
    "lb_wood_single": ("item", "Wood", 1_000_000_000),
    "lb_carrots": ("item", "Carrot", 2_000_000_000),
    "lb_carrots_single": ("item", "Carrot", 200_000_000),
    "lb_pumpkins": ("item", "Pumpkin", 200_000_000),
    "lb_pumpkins_single": ("item", "Pumpkin", 20_000_000),
    "lb_cactus": ("item", "Cactus", 33_554_432),
    "lb_cactus_single": ("item", "Cactus", 131_072),
    "lb_dinosaur": ("item", "Bone", 33_488_928),
    "lb_maze": ("item", "Gold", 9_863_168),
    "lb_maze_single": ("item", "Gold", 616_448),
    "lb_sunflowers": ("item", "Power", 100_000),
    "lb_sunflowers_single": ("item", "Power", 10_000),
}


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
    # 本地 leaderboard_run 要靠最终农场状态判断这一轮是否真正达标。
    if farm is None:
        return None, "goal=missing-farm"
    goal = _LEADERBOARD_GOALS.get(Path(target_name).stem)
    if goal is None:
        return None, "goal=untracked"
    goal_type, resource_name, amount = goal
    if goal_type == "item":
        current = int(farm.num_items(farm.item(resource_name)))
    else:
        current = int(farm.num_unlocked(farm.unlock(resource_name)))
    return current >= amount, f"{resource_name}={current}/{amount}"


def run_leaderboard_iteration(target: str, save_root: str | Path | None, seed: int) -> LeaderboardIterationResult:
    # 子进程只返回 summary，避免把整轮脚本明细日志来回复制。
    nested = run_file_with_context(
        target,
        save_root,
        seed=seed,
        capture_logs=False,
    )
    _, progress_text = leaderboard_goal_status(target, nested.final_farm)
    return LeaderboardIterationResult(
        seed=seed,
        elapsed_seconds=nested.elapsed_seconds,
        terminated=nested.terminated,
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
        result: dict[object, int] = {}
        for key, boxed in source.items.items():
            result[_coerce_bag_key(key, "Unlocks", bindings)] = int(float(boxed.obj.num))
        return result
    defaults = _default_unlock_levels(bindings)
    result = {}
    for unlock in source:
        current_unlock = _coerce_bag_key(unlock, "Unlocks", bindings)
        result[current_unlock] = defaults.get(current_unlock, 1)
    return result


def coerce_items(source, bindings: dict[str, object]) -> dict[object, float]:
    if isinstance(source, PyDict):
        result: dict[object, float] = {}
        for key, boxed in source.items.items():
            result[_coerce_bag_key(key, "Items", bindings)] = float(boxed.obj.num)
        return result
    return {}


def coerce_globals(source) -> dict[str, object]:
    if isinstance(source, PyDict):
        result: dict[str, object] = {}
        for key, boxed in source.items.items():
            key_text = key.text if isinstance(key, PyString) else str(key)
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
