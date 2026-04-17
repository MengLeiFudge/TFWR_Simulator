from __future__ import annotations

from collections import deque
import random
from typing import Any

from .execute_exception import BreakStatement, ContinueStatement, ExecuteException, ReturnStatement
from .module_state import ModuleState
from .py_values import PyString
from ..common.runtime_types import RuntimeMailbox
from .scope import Scope
from ..common.side_effects import SideEffect


class ProgramState:
    """Minimal Python port of Core.ProgramState for scheduler bring-up.

    Scope, parser, and node execution are ported later; this class already
    preserves the op-count and side-effect surface expected by Execution.
    """

    def __init__(self, op_count: float, random_source: random.Random, drone_id: int):
        global_scope = Scope(None, None, None, set())
        global_scope.import_var("__name__", PyString("__main__"))
        self.module_state = ModuleState(global_scope=global_scope)
        self.awaited_drone_id = -1
        self.current_side_effect = SideEffect.NONE
        self.current_side_effect_argument: Any = None
        self.current_side_effect_argument2: Any = None
        self.hit_breakpoint = False
        self.hit_stopping_point = False
        self.current_execute_exception: Exception | None = None
        self.current_dependencies: list[tuple[str, int, int]] = []
        self.execution_stack: list[Any] = []
        self.execution_stack_index = -1
        self.all_messages_queue = deque()
        self.message_queues = [deque() for _ in range(36)]
        self.module_cache: dict[str, Any] = {}
        self.op_count = op_count
        self.start_op_count = op_count
        self._last_consumed_op_count = op_count
        self.drone_id = drone_id
        self.drone_handle = None
        self.target_op_count = 0.0
        self.random_random = random.Random(random_source.randrange(0, 2**31))
        self.mailbox = RuntimeMailbox(self.all_messages_queue, self.message_queues)

    @property
    def current_scope(self) -> Any:
        if self.module_state.call_stack:
            return self.module_state.call_stack[-1]
        return self.module_state.global_scope

    @property
    def return_value(self) -> Any:
        return self.module_state.return_value

    @return_value.setter
    def return_value(self, value: Any) -> None:
        self.module_state.return_value = value

    @property
    def is_expression_static(self) -> bool:
        return self.module_state.is_expression_static

    @is_expression_static.setter
    def is_expression_static(self, value: bool) -> None:
        self.module_state.is_expression_static = value

    @property
    def current_executing_node(self) -> Any:
        return self.module_state.current_executing_node

    @current_executing_node.setter
    def current_executing_node(self, value: Any) -> None:
        self.module_state.current_executing_node = value

    def push_scope(self, scope: Any) -> None:
        self.module_state.call_stack.append(scope)

    def pop_scope(self) -> Any:
        return self.module_state.call_stack.pop()

    def add_and_consume_ops(self, ops: float) -> None:
        self.op_count += ops
        self._last_consumed_op_count += ops

    def consume_ops(self) -> float:
        result = self.op_count - self._last_consumed_op_count
        self._last_consumed_op_count = self.op_count
        return result

    def perform_execution_step(self, target_op_count: float) -> bool:
        self.target_op_count = target_op_count
        if self.execution_stack_index < 0:
            self.current_side_effect = SideEffect.TERMINATED
            return False
        if self.awaited_drone_id >= 0:
            self.op_count += 1.0
            self._last_consumed_op_count += 1.0
            return False
        active_drone_executed_step = False
        try:
            steps = 0
            while True:
                if self.execution_stack_index >= 0:
                    current_iter = self.execution_stack[self.execution_stack_index]
                    try:
                        next(current_iter)
                    except StopIteration:
                        self.execution_stack[self.execution_stack_index] = None
                        self.execution_stack.pop()
                        self.execution_stack_index -= 1
                        continue
                steps += 1
                if (
                    self.execution_stack_index < 0
                    or self.op_count > target_op_count
                    or self.current_side_effect != SideEffect.NONE
                    or self.hit_breakpoint
                    or self.hit_stopping_point
                    or steps >= 1000
                ):
                    break
            if self.hit_stopping_point or self.hit_breakpoint:
                self.hit_stopping_point = False
                active_drone_executed_step = True
        except BreakStatement:
            self.current_execute_exception = ExecuteException("error_no_loop_to_break")
            self.current_side_effect = SideEffect.ERROR
        except ContinueStatement:
            self.current_execute_exception = ExecuteException("error_no_loop_to_continue")
            self.current_side_effect = SideEffect.ERROR
        except ReturnStatement:
            self.current_execute_exception = ExecuteException("error_no_function_to_return_from")
            self.current_side_effect = SideEffect.ERROR
        except ExecuteException as exc:
            self.current_execute_exception = exc
            self.current_side_effect = SideEffect.ERROR
        return active_drone_executed_step

    def push_onto_execution_stack(self, exec_iterable: Any) -> None:
        self.execution_stack.append(iter(exec_iterable))
        self.execution_stack_index = len(self.execution_stack) - 1
