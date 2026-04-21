from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
import math
import os
import time
from typing import Any

from ..common.dotnet_random import DotNetRandom
from .builtins_api import default_functions
from ..common.duration import Duration
from .program_state import ProgramState
from .py_function import PyFunction
from .py_values import PyList
from .py_values import PyBool, PyNone, PyNumber
from .scope import Scope
from ..common.side_effects import SideEffect


MIN_LEADERBOARD_TOTAL_SECONDS = 2.0 * 60.0 * 60.0
MAX_LEADERBOARD_RUNS = 20_000


def resolve_leaderboard_worker_count() -> int:
    configured = os.environ.get("TFWR_MAX_LEADERBOARD_WORKERS", "").strip()
    if configured:
        try:
            return max(1, int(configured))
        except ValueError:
            pass
    return max(1, os.cpu_count() or 1)


MAX_LEADERBOARD_WORKERS = resolve_leaderboard_worker_count()
# 父层 heartbeat 默认低频输出，避免日志本身反过来拖慢长跑吞吐。
LEADERBOARD_HEARTBEAT_INTERVAL_SECONDS = 5.0
# 等待 future 的轮询粒度需要比 heartbeat 更细，这样才能及时打出进度而不长期阻塞。
LEADERBOARD_WAIT_TIMEOUT_SECONDS = 0.25


def should_schedule_more_prefetch(
    total_seconds: float,
    run_count: int,
    pending_count: int,
    min_total_seconds: float,
) -> bool:
    if run_count <= 0:
        return True
    average_seconds = total_seconds / run_count
    buffered_projection = total_seconds + average_seconds * pending_count
    return buffered_projection < min_total_seconds


def shutdown_process_pool_fast(executor: Any) -> None:
    processes = list(getattr(executor, "_processes", {}).values())
    executor.shutdown(wait=False, cancel_futures=True)
    for process in processes:
        if process.is_alive():
            process.terminate()
    for process in processes:
        if process.is_alive():
            process.join(timeout=0.2)
    for process in processes:
        if process.is_alive():
            process.kill()
    for process in processes:
        if process.is_alive():
            process.join(timeout=0.2)


@dataclass
class Execution:
    sim: Any
    syntax_tree: Any
    execution_id: int
    global_bindings: dict[str, Any] | None = None
    states: list[ProgramState] = field(default_factory=list)
    active_drone_executed_step: bool = False
    stopped: bool = False
    global_op_count: float = 0.0
    is_performing_a_step: bool = False
    next_execution_time: Duration | None = None
    main_state: ProgramState | None = None
    completed_main_state: ProgramState | None = None

    ACTION_OPS = 200.0
    OPERATION_OPS = 1.0

    def __post_init__(self) -> None:
        self.add_program_state(0, self.syntax_tree, 0.0)
        self.main_state = self.states[0]
        self.next_execution_time = self.sim.current_time

    def stop_execution(self) -> None:
        if not self.stopped:
            self.stopped = True
            if self.sim.is_executing():
                self.sim.stop_program_execution()

    def add_program_state(self, drone_id: int, syntax_tree: Any, op_count: float) -> None:
        program_state = ProgramState(op_count, self.sim.random_random, drone_id)
        for function in default_functions().values():
            program_state.module_state.global_scope.set_var(function.function_name, function, check_shadow=False, is_static=True)
        for name, value in (self.global_bindings or {}).items():
            program_state.module_state.global_scope.set_var(name, value, check_shadow=False, is_static=True)
        if syntax_tree is not None:
            program_state.push_onto_execution_stack(syntax_tree.execute(program_state, self, 0))
        if drone_id >= len(self.states):
            self.states.extend([None] * (drone_id - len(self.states) + 1))
        self.states[drone_id] = program_state

    def execute(self, target_run_time: Duration) -> None:
        self.is_performing_a_step = True
        if self.next_execution_time is not None and self.sim.current_time < self.next_execution_time:
            self.sim.current_time = self.next_execution_time
        cap = math.floor(self.global_op_count + min(199.0, target_run_time / self.sim.op_duration))
        while True:
            previous_global = self.global_op_count
            if self.stopped:
                break
            for index in range(len(self.states)):
                state = self.states[index]
                if state is None:
                    continue
                if state.current_side_effect == SideEffect.NONE and state.op_count <= cap and state.awaited_drone_id < 0:
                    self.active_drone_executed_step |= state.perform_execution_step(cap)
            active_states = [state for state in self.states if state is not None and state.awaited_drone_id < 0]
            self.global_op_count = min((state.op_count for state in active_states), default=cap)

            consumed_ops = 0.0
            num3 = cap
            for state in self.states:
                if state is None or state.awaited_drone_id >= 0:
                    continue
                num3 = min(num3, state.op_count)
            self.sim.add_ops_to_current_time(num3 - previous_global)

            if not self.stopped and not self.sim.paused:
                for state in self.states:
                    if state is not None:
                        consumed_ops += state.consume_ops()
                for index in range(len(self.states)):
                    if self.global_op_count > cap:
                        break
                    state = self.states[index]
                    if state is None or state.awaited_drone_id >= 0:
                        continue
                    if state.current_side_effect != SideEffect.NONE and state.op_count <= self.global_op_count:
                        self._apply_side_effect(state)
                        if index < len(self.states) and self.states[index] is not None:
                            consumed_ops += self.states[index].consume_ops()
                            self.states[index].current_side_effect = SideEffect.NONE
                            self.states[index].current_side_effect_argument = None
                            self.states[index].current_side_effect_argument2 = None
                if self.sim.farm is not None:
                    self.sim.farm.used_power += consumed_ops / 200.0 / 30.0
                if self.stopped:
                    self.next_execution_time = self.sim.current_time
                    break

            active_states = [state for state in self.states if state is not None and state.awaited_drone_id < 0]
            self.global_op_count = min((state.op_count for state in active_states), default=cap)
            self.next_execution_time = self.sim.current_time + (self.sim.op_duration * (self.global_op_count - num3))
            self.sim.add_ops_to_current_time(min(self.global_op_count, cap) - num3)

            if self.global_op_count > cap or self.sim.paused or self.stopped:
                break
        self.is_performing_a_step = False
        if self.stopped and self.completed_main_state is not None:
            self.global_op_count = max(self.global_op_count, float(cap))
            self.next_execution_time = self.sim.current_time
            if self.states and self.states[0] is None:
                self.states[0] = self.completed_main_state

    def _apply_side_effect(self, state: ProgramState) -> None:
        def apply_ops(ops: float, consume_immediately: bool = False) -> None:
            if consume_immediately:
                state.add_and_consume_ops(ops)
            else:
                state.op_count += ops

        if state.current_side_effect == SideEffect.GET_TIME:
            state.return_value = PyNumber(self.sim.current_time.seconds)
        elif state.current_side_effect == SideEffect.GET_POS_X:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].x)
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_POS_Y:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].y)
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_WORLD_SIZE:
            state.return_value = PyNumber(self.sim.farm.grid.world_size[1])
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.MOVE:
            ok, ops = self.sim.farm.drones[state.drone_id].move(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            apply_ops(ops)
        elif state.current_side_effect == SideEffect.SWAP:
            ok = self.sim.farm.drones[state.drone_id].swap(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            apply_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.CAN_MOVE:
            ok = self.sim.farm.drones[state.drone_id].can_move(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.HARVEST:
            ok = self.sim.farm.drones[state.drone_id].harvest()
            state.return_value = PyBool(ok)
            apply_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.CAN_HARVEST:
            ok = self.sim.farm.drones[state.drone_id].can_harvest()
            state.return_value = PyBool(ok)
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.PLANT:
            ok = self.sim.farm.drones[state.drone_id].plant(state.current_side_effect_argument, state)
            state.return_value = PyBool(ok)
            apply_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.TILL:
            self.sim.farm.drones[state.drone_id].till()
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.GET_GROUND_TYPE:
            state.return_value = self.sim.farm.drones[state.drone_id].get_ground_type()
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_ENTITY_TYPE:
            entity = self.sim.farm.drones[state.drone_id].get_entity_type()
            state.return_value = entity if entity is not None else PyNone()
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.MEASURE:
            direction = state.current_side_effect_argument
            if isinstance(direction, PyNone):
                direction = None
            value = self.sim.farm.drones[state.drone_id].measure(direction)
            if value is None:
                state.return_value = PyNone()
            elif isinstance(value, tuple):
                state.return_value = __import__("gamesimulator.runtime.py_values", fromlist=["PyTuple", "PyNumber"]).PyTuple([PyNumber(value[0]), PyNumber(value[1])])
            elif isinstance(value, (int, float)):
                state.return_value = PyNumber(value)
            else:
                state.return_value = value
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_WATER:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].get_water())
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_COMPANION:
            companion = self.sim.farm.drones[state.drone_id].get_companion()
            if companion is None:
                state.return_value = PyNone()
            else:
                entity, (cx, cy) = companion
                state.return_value = __import__("gamesimulator.runtime.py_values", fromlist=["PyTuple"]).PyTuple(
                    [entity, __import__("gamesimulator.runtime.py_values", fromlist=["PyTuple", "PyNumber"]).PyTuple([PyNumber(cx), PyNumber(cy)])]
                )
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.USE_ITEM:
            item = state.current_side_effect_argument
            amount = int(float(state.current_side_effect_argument2.num))
            item_name = str(item).split(".")[-1]
            ok = False
            use_action_ticks = False
            if item_name == "Water":
                ok = self.sim.farm.drones[state.drone_id].water(amount)
                use_action_ticks = ok
            elif item_name == "Fertilizer":
                ok = self.sim.farm.drones[state.drone_id].fertilize(amount)
                use_action_ticks = ok
            elif item_name == "Weird_Substance":
                if self.sim.farm.num_items(item) < amount:
                    ok = False
                    use_action_ticks = False
                else:
                    ok, use_action_ticks = self.sim.farm.drones[state.drone_id].apply_weird_substance(amount)
                    if ok:
                        self.sim.farm.consume_items(item, amount)
            state.return_value = PyBool(ok)
            apply_ops(200.0 if use_action_ticks else 1.0)
        elif state.current_side_effect == SideEffect.SPAWN_DRONE:
            payload = state.current_side_effect_argument
            active_count = len([program_state for program_state in self.states if program_state is not None])
            if active_count >= self.sim.farm.max_drones():
                state.return_value = PyNone()
                apply_ops(1.0)
            else:
                func = payload.items[0]
                child_id = self.sim.farm.add_drone(state.drone_id)
                function_node = func.syntax_tree
                args = [item.deep_copy({}) if hasattr(item, "deep_copy") else item for item in payload.items[1:]]
                function_node.arguments = args
                child_op_count = state.op_count + self.ACTION_OPS + self.OPERATION_OPS
                self.add_program_state(child_id, function_node, child_op_count)
                child_state = self.states[child_id]
                child_state.push_scope(Scope(function_node, None, func.parent_scope, function_node.vars or set()))
                handle = __import__("gamesimulator.runtime.py_values", fromlist=["PyDroneHandle"]).PyDroneHandle(child_id, self.sim.farm.drone_generation)
                child_state.drone_handle = handle
                state.return_value = handle
                apply_ops(200.0)
        elif state.current_side_effect == SideEffect.AWAIT:
            handle = state.current_side_effect_argument
            if handle.return_value is not None:
                state.return_value = handle.return_value
                apply_ops(1.0)
            else:
                state.awaited_drone_id = int(handle.drone_id if hasattr(handle, "drone_id") else handle.id)
                apply_ops(1.0)
        elif state.current_side_effect == SideEffect.HAS_FINISHED:
            handle = state.current_side_effect_argument
            state.return_value = PyBool(handle.return_value is not None)
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.CLEAR:
            if self.sim.farm.drones:
                main = self.sim.farm.drones[0]
                main.x = 0
                main.y = 0
            self.sim.farm.grid.clear_grid()
            self.sim.farm.restart_world_grass()
            self.states = [self.states[state.drone_id]]
            self.states[0].drone_id = 0
            self.sim.farm.drones = [self.sim.farm.drones[0]]
            state.awaited_drone_id = -1
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.UNLOCK:
            unlock = state.current_side_effect_argument
            ok = self.sim.farm.unlock_or_upgrade(unlock)
            state.return_value = PyBool(ok)
            apply_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.DO_A_FLIP:
            state.return_value = PyNone()
            apply_ops(math.floor(1.0 / self.sim.op_duration.seconds), consume_immediately=True)
        elif state.current_side_effect == SideEffect.PET_THE_PIGGY:
            state.return_value = PyNone()
            apply_ops(math.floor(1.0 / self.sim.op_duration.seconds), consume_immediately=True)
        elif state.current_side_effect == SideEffect.TERMINATED:
            was_main = state is self.main_state
            for other_state in self.states:
                if other_state is None:
                    continue
                if other_state.awaited_drone_id == state.drone_id:
                    other_state.awaited_drone_id = -1
                    other_state.op_count = self.global_op_count
                    other_state.return_value = state.return_value.deep_copy({}) if hasattr(state.return_value, "deep_copy") else state.return_value
            if state.drone_handle is not None:
                state.drone_handle.return_value = state.return_value
            if was_main:
                self.completed_main_state = state
                self.main_state = None
            self.states[state.drone_id] = None
            if all(program_state is None for program_state in self.states):
                self.is_performing_a_step = False
                self.stop_execution()
            elif not was_main:
                self.sim.farm.remove_drone(state.drone_id)
            return
        elif state.current_side_effect == SideEffect.RUN_LEADERBOARD:
            from ..runner import format_clock_time, run_leaderboard_iteration

            if getattr(self.sim, "leaderboard_type", "none") != "none":
                state.return_value = PyNone()
                apply_ops(200.0)
                return

            payload = state.current_side_effect_argument
            target = payload.items[1].text
            leaderboard_key = str(payload.items[0]).split(".")[-1]
            total_seconds = 0.0
            run_count = 0
            finished = True
            min_seconds: float | None = None
            max_seconds: float | None = None
            save_root = getattr(self.sim, "save_root", None)
            pending: dict[int, tuple[int, Any]] = {}
            next_order_to_schedule = 0
            next_order_to_consume = 0
            prefetch_random = DotNetRandom(0)
            prefetch_random.setstate(self.sim.random_random.getstate())
            start_wall_time = time.monotonic()
            last_heartbeat_time = start_wall_time

            def schedule_one(executor: ProcessPoolExecutor) -> None:
                nonlocal next_order_to_schedule
                seed = prefetch_random.randrange(1, 2**31)
                pending[next_order_to_schedule] = (
                    seed,
                    executor.submit(run_leaderboard_iteration, target, save_root, seed, leaderboard_key),
                )
                next_order_to_schedule += 1

            self.log(f"leaderboard_run {target}.py start")

            # 本地模拟器没有动画显示，直接并行预跑多轮，再按固定 seed 顺序消费结果。
            executor = ProcessPoolExecutor(max_workers=MAX_LEADERBOARD_WORKERS)
            try:
                while (
                    len(pending) < MAX_LEADERBOARD_WORKERS
                    and next_order_to_schedule < MAX_LEADERBOARD_RUNS
                    and should_schedule_more_prefetch(
                        total_seconds=total_seconds,
                        run_count=run_count,
                        pending_count=len(pending),
                        min_total_seconds=MIN_LEADERBOARD_TOTAL_SECONDS,
                    )
                ):
                    schedule_one(executor)
                while total_seconds < MIN_LEADERBOARD_TOTAL_SECONDS and next_order_to_consume < MAX_LEADERBOARD_RUNS:
                    scheduled_seed, future = pending[next_order_to_consume]
                    try:
                        iteration = future.result(timeout=LEADERBOARD_WAIT_TIMEOUT_SECONDS)
                        pending.pop(next_order_to_consume)
                    except FutureTimeoutError:
                        now = time.monotonic()
                        if now - last_heartbeat_time >= LEADERBOARD_HEARTBEAT_INTERVAL_SECONDS:
                            average_seconds = total_seconds / run_count if run_count > 0 else 0.0
                            heartbeat_eta = None
                            if total_seconds > 0.0:
                                heartbeat_eta = max(0.0, MIN_LEADERBOARD_TOTAL_SECONDS - total_seconds) * (
                                    (now - start_wall_time) / total_seconds
                                )
                            buffered_done = sum(1 for _, buffered_future in pending.values() if buffered_future.done())
                            eta_text = (
                                f" eta={format_clock_time(heartbeat_eta)}"
                                if heartbeat_eta is not None
                                else " eta=unknown"
                            )
                            self.log(
                                "leaderboard_run heartbeat"
                                f" completed={next_order_to_consume}"
                                f" scheduled={next_order_to_schedule}"
                                f" pending={len(pending)}"
                                f" buffered_done={buffered_done}"
                                f" avg={format_clock_time(average_seconds)}"
                                f" total={format_clock_time(total_seconds)}"
                                f" wall={format_clock_time(now - start_wall_time)}"
                                f"{eta_text}"
                                f" waiting_seed={scheduled_seed}"
                            )
                            last_heartbeat_time = now
                        continue
                    actual_seed = self.sim.random_random.randrange(1, 2**31)
                    if actual_seed != scheduled_seed or iteration.seed != scheduled_seed:
                        raise RuntimeError("leaderboard seed ordering drifted")
                    next_order_to_consume += 1
                    run_count += 1
                    total_seconds += iteration.elapsed_seconds
                    min_seconds = iteration.elapsed_seconds if min_seconds is None else min(min_seconds, iteration.elapsed_seconds)
                    max_seconds = iteration.elapsed_seconds if max_seconds is None else max(max_seconds, iteration.elapsed_seconds)
                    self.log(
                        "leaderboard_run"
                        f" run={run_count}"
                        f" seed={scheduled_seed}"
                        f" time={format_clock_time(iteration.elapsed_seconds)}"
                        f" seconds={iteration.elapsed_seconds:.3f}"
                        f" total={format_clock_time(total_seconds)}"
                        f" progress={iteration.progress_text}"
                    )
                    if not iteration.terminated or iteration.elapsed_seconds <= 0.0 or not iteration.goal_reached:
                        finished = False
                        break
                    while (
                        total_seconds < MIN_LEADERBOARD_TOTAL_SECONDS
                        and len(pending) < MAX_LEADERBOARD_WORKERS
                        and next_order_to_schedule < MAX_LEADERBOARD_RUNS
                        and should_schedule_more_prefetch(
                            total_seconds=total_seconds,
                            run_count=run_count,
                            pending_count=len(pending),
                            min_total_seconds=MIN_LEADERBOARD_TOTAL_SECONDS,
                        )
                    ):
                        schedule_one(executor)
            finally:
                shutdown_process_pool_fast(executor)

            if next_order_to_consume >= MAX_LEADERBOARD_RUNS and total_seconds < MIN_LEADERBOARD_TOTAL_SECONDS:
                finished = False
            average_seconds = total_seconds / run_count if run_count > 0 else 0.0
            if run_count == 0:
                finished = False
                min_seconds = 0.0
                max_seconds = 0.0
            status_word = "pass" if finished else "fail"
            self.log(
                f"leaderboard_run {target}.py"
                f" {status_word}"
                f" average={format_clock_time(average_seconds)}"
                f" min={format_clock_time(min_seconds or 0.0)}"
                f" max={format_clock_time(max_seconds or 0.0)}"
            )
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.SIMULATE:
            from ..runner import coerce_globals, coerce_items, coerce_unlock_levels, coerce_unlock_strings, run_file_with_context

            if getattr(self.sim, "leaderboard_type", "none") != "none":
                state.return_value = PyNone()
                apply_ops(200.0)
                return

            payload = state.current_side_effect_argument
            target = payload.items[0].text
            unlock_levels = coerce_unlock_levels(payload.items[1], self.global_bindings or {})
            unlock_strings = coerce_unlock_strings(payload.items[1], self.global_bindings or {})
            items = coerce_items(payload.items[2], self.global_bindings or {})
            globals_override = coerce_globals(payload.items[3])
            seed = int(float(payload.items[4].num))
            nested = run_file_with_context(
                target,
                getattr(self.sim, "save_root", None),
                seed=seed,
                unlock_levels=unlock_levels,
                unlock_strings=unlock_strings,
                items=items,
                globals_override=globals_override,
                run_kind="simulation",
            )
            for line in nested.logs:
                self.log(line)
            state.return_value = PyNumber(nested.elapsed_seconds)
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.SET_WORLD_SIZE:
            value = int(float(state.current_side_effect_argument.num))
            world_size_changed = value != self.sim.farm.grid.world_size[1]
            self.sim.farm.grid.set_size_limit(value)
            if world_size_changed:
                self.sim.farm.restart_world_grass()
            for drone in self.sim.farm.drones:
                drone.x = 0
                drone.y = 0
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.SET_EXECUTION_SPEED:
            value = float(state.current_side_effect_argument.num)
            if value > self.sim.farm.max_speed_factor() or value < 0.1:
                self.sim.change_execution_speed(self.sim.farm.max_speed_factor())
            else:
                self.sim.change_execution_speed(value)
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.CHANGE_HAT:
            self.sim.farm.drones[state.drone_id].change_hat(state.current_side_effect_argument)
            state.return_value = PyNone()
            apply_ops(200.0)
        elif state.current_side_effect == SideEffect.NUM_ITEMS:
            state.return_value = PyNumber(self.sim.farm.num_items(state.current_side_effect_argument))
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.NUM_UNLOCKED:
            state.return_value = PyNumber(self.sim.farm.num_unlocked(state.current_side_effect_argument))
            apply_ops(1.0)
        elif state.current_side_effect == SideEffect.PRINT:
            text = state.current_side_effect_argument.text
            self.log(text)
            state.return_value = PyNone()
            apply_ops(math.floor(1.0 / self.sim.op_duration.seconds), consume_immediately=True)
        elif state.current_side_effect == SideEffect.ERROR:
            raise state.current_execute_exception or RuntimeError("execution error")
        state.current_side_effect = SideEffect.NONE
        state.current_side_effect_argument = None
        state.current_side_effect_argument2 = None

    def log(self, message: str) -> None:
        self.sim.log(message)
