from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

from .builtins_api import default_functions
from ..common.duration import Duration
from .program_state import ProgramState
from .py_function import PyFunction
from .py_values import PyList
from .py_values import PyBool, PyNone, PyNumber
from .scope import Scope
from ..common.side_effects import SideEffect


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
        if state.current_side_effect == SideEffect.GET_TIME:
            state.return_value = PyNumber(self.sim.current_time.seconds)
        elif state.current_side_effect == SideEffect.GET_POS_X:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].x)
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_POS_Y:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].y)
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_WORLD_SIZE:
            state.return_value = PyNumber(self.sim.farm.grid.world_size[1])
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.MOVE:
            ok, ops = self.sim.farm.drones[state.drone_id].move(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(ops)
        elif state.current_side_effect == SideEffect.SWAP:
            ok = self.sim.farm.drones[state.drone_id].swap(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.CAN_MOVE:
            ok = self.sim.farm.drones[state.drone_id].can_move(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.HARVEST:
            ok = self.sim.farm.drones[state.drone_id].harvest()
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.CAN_HARVEST:
            ok = self.sim.farm.drones[state.drone_id].can_harvest()
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.PLANT:
            ok = self.sim.farm.drones[state.drone_id].plant(state.current_side_effect_argument)
            state.return_value = PyBool(ok)
            state.add_and_consume_ops(200.0 if ok else 1.0)
        elif state.current_side_effect == SideEffect.TILL:
            self.sim.farm.drones[state.drone_id].till()
            state.return_value = PyNone()
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.GET_GROUND_TYPE:
            state.return_value = self.sim.farm.drones[state.drone_id].get_ground_type()
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_ENTITY_TYPE:
            entity = self.sim.farm.drones[state.drone_id].get_entity_type()
            state.return_value = entity if entity is not None else PyNone()
            state.add_and_consume_ops(1.0)
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
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_WATER:
            state.return_value = PyNumber(self.sim.farm.drones[state.drone_id].get_water())
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.GET_COMPANION:
            companion = self.sim.farm.drones[state.drone_id].get_companion()
            if companion is None:
                state.return_value = PyNone()
            else:
                entity, (cx, cy) = companion
                state.return_value = __import__("gamesimulator.runtime.py_values", fromlist=["PyTuple"]).PyTuple(
                    [entity, __import__("gamesimulator.runtime.py_values", fromlist=["PyTuple", "PyNumber"]).PyTuple([PyNumber(cx), PyNumber(cy)])]
                )
            state.add_and_consume_ops(1.0)
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
            state.add_and_consume_ops(200.0 if use_action_ticks else 1.0)
        elif state.current_side_effect == SideEffect.SPAWN_DRONE:
            payload = state.current_side_effect_argument
            active_count = len([program_state for program_state in self.states if program_state is not None])
            if active_count >= self.sim.farm.max_drones():
                state.return_value = PyNone()
                state.add_and_consume_ops(1.0)
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
                state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.AWAIT:
            handle = state.current_side_effect_argument
            if handle.return_value is not None:
                state.return_value = handle.return_value
                state.add_and_consume_ops(1.0)
            else:
                state.awaited_drone_id = int(handle.drone_id if hasattr(handle, "drone_id") else handle.id)
                state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.HAS_FINISHED:
            handle = state.current_side_effect_argument
            state.return_value = PyBool(handle.return_value is not None)
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.CLEAR:
            if self.sim.farm.drones:
                main = self.sim.farm.drones[0]
                main.x = 0
                main.y = 0
            self.sim.farm.grid.clear_grid()
            self.states = [self.states[state.drone_id]]
            self.states[0].drone_id = 0
            self.sim.farm.drones = [self.sim.farm.drones[0]]
            state.awaited_drone_id = -1
            state.return_value = PyNone()
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.UNLOCK:
            unlock = state.current_side_effect_argument
            current = self.sim.farm.num_unlocked(unlock)
            self.sim.farm.unlock_levels[unlock] = current + 1
            if str(unlock).split(".")[-1] == "Expand":
                self.sim.farm.grid.reset_for_expand(self.sim.farm.num_unlocked(unlock))
            state.return_value = PyBool(True)
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.DO_A_FLIP:
            state.return_value = PyNone()
            state.add_and_consume_ops(math.floor(1.0 / self.sim.op_duration.seconds))
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
        elif state.current_side_effect == SideEffect.SIMULATE:
            from ..runner import coerce_globals, coerce_items, coerce_unlock_levels, run_file_with_context

            payload = state.current_side_effect_argument
            target = payload.items[0].text
            unlock_levels = coerce_unlock_levels(payload.items[1], self.global_bindings or {})
            items = coerce_items(payload.items[2], self.global_bindings or {})
            globals_override = coerce_globals(payload.items[3])
            seed = int(float(payload.items[4].num))
            nested = run_file_with_context(
                target,
                getattr(self.sim, "save_root", None),
                seed=seed,
                unlock_levels=unlock_levels,
                items=items,
                globals_override=globals_override,
            )
            for line in nested.logs:
                self.log(line)
            state.return_value = PyNumber(nested.elapsed_seconds)
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.SET_WORLD_SIZE:
            value = int(float(state.current_side_effect_argument.num))
            self.sim.farm.grid.set_size_limit(value)
            for drone in self.sim.farm.drones:
                drone.x = 0
                drone.y = 0
            state.return_value = PyNone()
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.SET_EXECUTION_SPEED:
            value = float(state.current_side_effect_argument.num)
            if value > self.sim.farm.max_speed_factor() or value < 0.1:
                self.sim.change_execution_speed(self.sim.farm.max_speed_factor())
            else:
                self.sim.change_execution_speed(value)
            state.return_value = PyNone()
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.CHANGE_HAT:
            self.sim.farm.drones[state.drone_id].change_hat(state.current_side_effect_argument)
            state.return_value = PyNone()
            state.add_and_consume_ops(200.0)
        elif state.current_side_effect == SideEffect.NUM_ITEMS:
            state.return_value = PyNumber(self.sim.farm.num_items(state.current_side_effect_argument))
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.NUM_UNLOCKED:
            state.return_value = PyNumber(self.sim.farm.num_unlocked(state.current_side_effect_argument))
            state.add_and_consume_ops(1.0)
        elif state.current_side_effect == SideEffect.PRINT:
            text = state.current_side_effect_argument.text
            self.log(text)
            state.return_value = PyNone()
            state.add_and_consume_ops(math.floor(1.0 / self.sim.op_duration.seconds))
        elif state.current_side_effect == SideEffect.ERROR:
            raise state.current_execute_exception or RuntimeError("execution error")
        state.current_side_effect = SideEffect.NONE
        state.current_side_effect_argument = None
        state.current_side_effect_argument2 = None

    def log(self, message: str) -> None:
        self.sim.log(message)
