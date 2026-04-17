from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable

from ..runtime.execute_exception import BreakStatement, ContinueStatement, ExecuteException, ReturnStatement
from ..runtime.py_function import PyFunction
from ..runtime.py_values import PyBool, PyDict, PyList, PyNone, PyObjectBox, PySet, PyString, PyTuple
from ..runtime.scope import Scope
from ..common.side_effects import SideEffect


@dataclass
class BoxedNodeParams:
    code_window: Any = None
    word_start: int = 0
    word_end: int = 0
    execution_id: int = -1
    is_breakpoint: bool = False


class Node(ABC):
    TICKS_PER_OP = 1

    def __init__(self, boxed_params: BoxedNodeParams | None = None):
        self.slots: list[Node | None] = []
        self.boxed_params = boxed_params or BoxedNodeParams()

    @property
    def node_name(self) -> str:
        return ""

    def blink(self, state: Any, execution: Any) -> None:
        return None

    def errors_and_breakpoints(self, state: Any, execution: Any, depth: int) -> None:
        if depth > 1100:
            raise ExecuteException("error_max_stack_size_reached")
        state.current_executing_node = self

    def check_increment_op_count(self, state: Any, execution: Any, ops: float) -> bool:
        state.op_count += ops
        if state.op_count >= state.target_op_count or state.hit_breakpoint or state.hit_stopping_point:
            return True
        return state.current_side_effect != SideEffect.NONE

    @abstractmethod
    def execute(self, state: Any, execution: Any, depth: int) -> Iterable[float]:
        raise NotImplementedError

    @abstractmethod
    def deep_copy(self, copies: dict[int, Any]) -> "Node":
        raise NotImplementedError


class LiteralNode(Node):
    def __init__(self, value: Any, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.value = value

    @property
    def node_name(self) -> str:
        return "literal"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        state.return_value = self.value
        state.is_expression_static = False
        if False:
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "LiteralNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = LiteralNode(self.value, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class ValueNode(Node):
    def __init__(self, value: str, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.value = value

    @property
    def node_name(self) -> str:
        return "value"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        result = state.current_scope.evaluate(self.value)
        state.return_value = result.val
        state.is_expression_static = result.is_static
        if False:
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "ValueNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = ValueNode(self.value, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class SequenceNode(Node):
    def __init__(self, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)

    @property
    def node_name(self) -> str:
        return "seq"

    def execute(self, state: Any, execution: Any, depth: int):
        values: list[Any] = []
        for slot in self.slots:
            if slot is None:
                continue
            for item in slot.execute(state, execution, depth + 1):
                yield item
            values.append(state.return_value)
        state.return_value = values

    def deep_copy(self, copies: dict[int, Any]) -> "SequenceNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = SequenceNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class BracketNode(Node):
    @property
    def node_name(self) -> str:
        return "bracket"

    def execute(self, state: Any, execution: Any, depth: int):
        if self.slots:
            for item in self.slots[0].execute(state, execution, depth + 1):
                yield item

    def deep_copy(self, copies: dict[int, Any]) -> "BracketNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = BracketNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class NoOpNode(Node):
    @property
    def node_name(self) -> str:
        return "noop"

    def execute(self, state: Any, execution: Any, depth: int):
        if False:
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "NoOpNode":
        return self


class ListNode(Node):
    @property
    def node_name(self) -> str:
        return "list"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        items = list(state.return_value)
        state.return_value = PyList(items)
        state.is_expression_static = False
        if self.check_increment_op_count(state, execution, max(1, len(items))):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "ListNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = ListNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class DictNode(Node):
    @property
    def node_name(self) -> str:
        return "dict"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        elements = list(state.return_value)
        mapping = {}
        for index in range(0, len(elements), 2):
            mapping[elements[index]] = PyObjectBox(elements[index + 1])
        state.return_value = PyDict(mapping)
        state.is_expression_static = False
        self.blink(state, execution)
        if self.check_increment_op_count(state, execution, 1 + len(mapping)):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "DictNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = DictNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class SetNode(Node):
    @property
    def node_name(self) -> str:
        return "set"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        elements = set(state.return_value)
        state.return_value = PySet(elements)
        state.is_expression_static = False
        self.blink(state, execution)
        if self.check_increment_op_count(state, execution, max(1, len(elements))):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "SetNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = SetNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class TupleNode(Node):
    @property
    def node_name(self) -> str:
        return "tuple"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        state.return_value = PyTuple(list(state.return_value))
        state.is_expression_static = False
        if self.check_increment_op_count(state, execution, 1.0):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "TupleNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = TupleNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class FunctionNode(Node):
    def __init__(self, param_names: list[str], func_name: str, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.param_names = param_names
        self.func_name = func_name
        self.vars: set[str] | None = None
        self.arguments: list[Any] = []

    @property
    def node_name(self) -> str:
        return "func"

    def execute(self, state: Any, execution: Any, depth: int):
        argument_values = list(self.arguments or [])
        missing_count = len(self.param_names) - len(argument_values)
        default_count = len(self.slots) - 1
        if missing_count < 0 or missing_count > default_count:
            raise ExecuteException(f"error_wrong_number_args:{self.func_name}")
        self.errors_and_breakpoints(state, execution, depth)
        try:
            for index in range(default_count - missing_count, default_count):
                for item in self.slots[index + 1].execute(state, execution, depth + 1):
                    yield item
                argument_values.append(state.return_value)
            for name, value in zip(self.param_names, argument_values):
                state.current_scope.set_var(name, value)
            self.blink(state, execution)
            if self.slots:
                for item in self.slots[0].execute(state, execution, depth + 1):
                    yield item
        except ReturnStatement:
            state.pop_scope()
            return
        state.return_value = PyNone()
        state.is_expression_static = False
        state.pop_scope()

    def deep_copy(self, copies: dict[int, Any]) -> "FunctionNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = FunctionNode(self.param_names[:], self.func_name, self.boxed_params)
        copies[key] = clone
        clone.vars = set(self.vars) if self.vars is not None else None
        clone.arguments = list(self.arguments)
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class DefNode(Node):
    def __init__(self, func_name: str, is_static: bool, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.func_name = func_name
        self.is_static = is_static

    @property
    def node_name(self) -> str:
        return "def"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        state.current_scope.set_var(self.func_name, PyFunction(self.func_name, self.slots[0], state.current_scope), True, self.is_static)
        state.return_value = PyNone()
        if self.check_increment_op_count(state, execution, 1.0):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "DefNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = DefNode(self.func_name, self.is_static, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class BinaryExprNode(Node):
    def __init__(self, op: str, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.op = op

    @property
    def node_name(self) -> str:
        return "binary"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        lhs = state.return_value
        lhs_is_static = state.is_expression_static
        if self.op == ".":
            if not hasattr(lhs, "evaluate"):
                raise ExecuteException("error_unknown_method")
            rhs = self.slots[1]
            if not isinstance(rhs, ValueNode):
                raise ExecuteException("error_invalid_const2")
            state.return_value = lhs.evaluate(rhs.value)
            state.is_expression_static = lhs_is_static
            if self.check_increment_op_count(state, execution, 0.0 if lhs_is_static else 1.0):
                yield 0.0
            return
        if self.op == "and" and not state.current_scope.is_true_value(lhs):
            self.blink(state, execution)
            state.return_value = lhs
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        if self.op == "or" and state.current_scope.is_true_value(lhs):
            self.blink(state, execution)
            state.return_value = lhs
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        for item in self.slots[1].execute(state, execution, depth + 1):
            yield item
        rhs = state.return_value
        self.blink(state, execution)
        if self.op == "+":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs)(float(lhs.num) + float(rhs.num))
            elif isinstance(lhs, PyString) and isinstance(rhs, PyString):
                state.return_value = PyString(lhs.text + rhs.text)
            else:
                raise ExecuteException(f"error_bad_bin_operator:{self.op}")
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        if self.op == "-":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs)(float(lhs.num) - float(rhs.num))
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op == "*":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs)(float(lhs.num) * float(rhs.num))
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op == "/":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs)(float(lhs.num) / float(rhs.num))
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op == "//":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs).floor_division(lhs, rhs)
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op == "%":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs).modulo(lhs, rhs)
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op == "**":
            if hasattr(lhs, "num") and hasattr(rhs, "num"):
                state.return_value = type(lhs)(float(lhs.num) ** float(rhs.num))
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException(f"error_bad_bin_operator:{self.op}")
        if self.op in ("==", "!=", "<", "<=", ">", ">="):
            lv = float(lhs.num) if hasattr(lhs, "num") else lhs
            rv = float(rhs.num) if hasattr(rhs, "num") else rhs
            if self.op == "==":
                result = lv == rv
            elif self.op == "!=":
                result = lv != rv
            elif self.op == "<":
                result = lv < rv
            elif self.op == "<=":
                result = lv <= rv
            elif self.op == ">":
                result = lv > rv
            else:
                result = lv >= rv
            state.return_value = PyBool(result)
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        if self.op in ("in", "not in"):
            if isinstance(rhs, list):
                result = lhs in rhs
            elif isinstance(rhs, PyList):
                result = lhs in rhs.items
            elif isinstance(rhs, PyTuple):
                result = lhs in rhs.elements
            elif isinstance(rhs, PySet):
                result = lhs in rhs.items
            elif isinstance(rhs, PyDict):
                result = lhs in rhs.items
            elif isinstance(rhs, PyString) and isinstance(lhs, PyString):
                result = lhs.text in rhs.text
            elif hasattr(rhs, "__iter__"):
                result = lhs in list(rhs)
            else:
                raise ExecuteException("error_bad_unary_operator:in")
            if self.op == "not in":
                result = not result
            state.return_value = PyBool(result)
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        if self.op == "[]":
            if isinstance(rhs, list):
                if len(rhs) == 0:
                    raise ExecuteException("error_invalid_index")
                if len(rhs) == 1:
                    rhs = rhs[0]
                else:
                    rhs = PyTuple(rhs)
            if isinstance(lhs, (PyList, PyTuple)):
                if isinstance(rhs, PyTuple):
                    if len(rhs.elements) != 1:
                        raise ExecuteException("error_invalid_index")
                    rhs = rhs.elements[0]
                index = int(float(rhs.num))
                state.return_value = lhs[index]
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            if isinstance(lhs, PyDict):
                key = rhs
                if isinstance(rhs, PyTuple):
                    if len(rhs.elements) != 1:
                        raise ExecuteException("error_invalid_index")
                    key = rhs.elements[0]
                state.return_value = lhs.at(key)
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                return
            raise ExecuteException("error_index_on_non_indexable")
        if self.op == "and" or self.op == "or":
            state.return_value = rhs
            if self.check_increment_op_count(state, execution, 1.0):
                yield 0.0
            return
        raise ExecuteException(f"error_unsupported_operator:{self.op}")

    def deep_copy(self, copies: dict[int, Any]) -> "BinaryExprNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = BinaryExprNode(self.op, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class UnaryExprNode(Node):
    def __init__(self, op: str, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.op = op

    @property
    def node_name(self) -> str:
        return "unary"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        value = state.return_value
        if self.op == "+":
            if not hasattr(value, "num"):
                raise ExecuteException(f"error_bad_unary_operator:{self.op}")
            state.return_value = value
        elif self.op == "-":
            if not hasattr(value, "num"):
                raise ExecuteException(f"error_bad_unary_operator:{self.op}")
            state.return_value = type(value)(0.0 - float(value.num))
        elif self.op == "not":
            state.return_value = PyBool(not state.current_scope.is_true_value(value))
        else:
            raise ExecuteException(f"error_bad_unary_operator:{self.op}")
        self.blink(state, execution)

    def deep_copy(self, copies: dict[int, Any]) -> "UnaryExprNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = UnaryExprNode(self.op, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class AssignmentNode(Node):
    def __init__(self, op: str, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.op = op

    @property
    def node_name(self) -> str:
        return "assign"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[1].execute(state, execution, depth + 1):
            yield item
        rhs = state.return_value
        self.blink(state, execution)
        for item in self.assign(state, execution, depth, self.slots[0], rhs, self.op):
            yield item
        state.return_value = PyNone()

    @staticmethod
    def assign(state: Any, execution: Any, depth: int, lhs: Node, rhs: Any, op: str):
        if isinstance(lhs, ValueNode):
            name = lhs.value
            before = None if op == "=" else state.current_scope.evaluate(name).val
            value, exec_time = AssignmentNode._get_value_to_assign(before, rhs, op)
            state.current_scope.set_var(name, value)
            lhs.blink(state, execution)
            if lhs.check_increment_op_count(state, execution, exec_time):
                yield 0.0
            return
        if isinstance(lhs, BinaryExprNode) and lhs.op == "[]":
            for item in lhs.slots[0].execute(state, execution, depth + 1):
                yield item
            target = state.return_value
            for item in lhs.slots[1].execute(state, execution, depth + 1):
                yield item
            indices = state.return_value
            index_values = _normalize_indices(indices)
            if len(index_values) != 1:
                raise ExecuteException("error_assign_type_mismatch")
            index_value = index_values[0]
            if isinstance(target, PyList):
                before = None if op == "=" else target.items[int(float(index_value.num))]
                value, exec_time = AssignmentNode._get_value_to_assign(before, rhs, op)
                target.items[int(float(index_value.num))] = value
                if lhs.check_increment_op_count(state, execution, exec_time + 1.0):
                    yield 0.0
                return
            if isinstance(target, PyDict):
                before = None if op == "=" else target.at(index_value)
                value, exec_time = AssignmentNode._get_value_to_assign(before, rhs, op)
                target.at(index_value, value)
                if lhs.check_increment_op_count(state, execution, exec_time + 1.0):
                    yield 0.0
                return
            raise ExecuteException("error_assign_type_mismatch")
        if isinstance(lhs, TupleNode):
            if not isinstance(rhs, PyTuple):
                raise ExecuteException("error_assign_type_mismatch")
            left_nodes = lhs.slots[0].slots
            if len(left_nodes) != len(rhs.elements):
                raise ExecuteException("error_not_enough_values")
            for left_node, right_value in zip(left_nodes, rhs.elements):
                for item in AssignmentNode.assign(state, execution, depth, left_node, right_value, op):
                    yield item
            return
        if isinstance(lhs, BracketNode):
            if not lhs.slots or lhs.slots[0] is None:
                raise ExecuteException("error_assign_type_mismatch")
            for item in AssignmentNode.assign(state, execution, depth, lhs.slots[0], rhs, op):
                yield item
            return
        raise ExecuteException("error_assign_type_mismatch")

    @staticmethod
    def _get_value_to_assign(before: Any, rhs: Any, op: str):
        if op == "=":
            return rhs, 0.0
        if op == "+=":
            if hasattr(before, "num") and hasattr(rhs, "num"):
                return type(before)(float(before.num) + float(rhs.num)), 1.0
            raise ExecuteException("error_arith_assign_not_used_on_number")
        raise ExecuteException("error_arith_assign_not_used_on_number")

    def deep_copy(self, copies: dict[int, Any]) -> "AssignmentNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = AssignmentNode(self.op, self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


def _normalize_indices(indices: Any) -> list[Any]:
    if isinstance(indices, BracketNode):
        if not indices.slots:
            return []
        return _normalize_indices(indices.slots[0])
    if isinstance(indices, list):
        return indices
    if isinstance(indices, PyTuple):
        return list(indices.elements)
    return [indices]


class CallNode(Node):
    @property
    def node_name(self) -> str:
        return "call"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        func = state.return_value
        if not isinstance(func, PyFunction):
            raise ExecuteException("error_not_a_function")
        func_is_static = state.is_expression_static
        for item in self.slots[1].execute(state, execution, depth + 1):
            yield item
        parameters = list(state.return_value)
        self.blink(state, execution)
        if func.method_object is not None:
            parameters.insert(0, func.method_object)
        if func.syntax_tree is not None:
            if self.check_increment_op_count(state, execution, 0.0 if func_is_static else 1.0):
                yield 0.0
            function_node = func.syntax_tree
            function_node.arguments = parameters
            state.push_scope(Scope(function_node, state.current_executing_node, func.parent_scope, function_node.vars or set()))
            state.push_onto_execution_stack(func.syntax_tree.execute(state, execution, 0))
            yield 0.0
            return
        if func.binding is None:
            raise ExecuteException(f"error_name_not_defined:{func.function_name}")
        ops = func.binding(parameters, getattr(execution, "sim", None), execution, state.drone_id)
        if self.check_increment_op_count(state, execution, ops):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "CallNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = CallNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class PassNode(Node):
    @property
    def node_name(self) -> str:
        return "pass"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        if self.check_increment_op_count(state, execution, 1.0):
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "PassNode":
        return PassNode(self.boxed_params)


class BreakNode(Node):
    @property
    def node_name(self) -> str:
        return "break"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        raise BreakStatement()
        if False:
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "BreakNode":
        return BreakNode(self.boxed_params)


class ContinueNode(Node):
    @property
    def node_name(self) -> str:
        return "continue"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        self.blink(state, execution)
        raise ContinueStatement()
        if False:
            yield 0.0

    def deep_copy(self, copies: dict[int, Any]) -> "ContinueNode":
        return ContinueNode(self.boxed_params)


class ReturnNode(Node):
    @property
    def node_name(self) -> str:
        return "return"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        if self.slots:
            for item in self.slots[0].execute(state, execution, depth + 1):
                yield item
        else:
            state.return_value = PyNone()
        self.blink(state, execution)
        if self.check_increment_op_count(state, execution, 0.0):
            yield 0.0
        state.current_executing_node = self
        raise ReturnStatement(self.boxed_params.word_start, self.boxed_params.word_end)

    def deep_copy(self, copies: dict[int, Any]) -> "ReturnNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = ReturnNode(self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class BranchNode(Node):
    def __init__(self, boxed_params: BoxedNodeParams | None = None, looping: bool = False):
        super().__init__(boxed_params)
        self.looping = looping

    @property
    def node_name(self) -> str:
        return "while" if self.looping else "if"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        first_loop = True
        while True:
            for item in self.slots[0].execute(state, execution, depth + 1):
                yield item
            condition = state.current_scope.is_true_value(state.return_value)
            self.blink(state, execution)
            if first_loop:
                if self.check_increment_op_count(state, execution, 1.0):
                    yield 0.0
                first_loop = False
            if not condition:
                break
            try:
                for item in self.slots[1].execute(state, execution, depth + 1):
                    yield item
            except BreakStatement:
                if not self.looping:
                    raise
                return
            except ContinueStatement:
                if not self.looping:
                    raise
            if not self.looping:
                state.return_value = PyNone()
                return
            self.errors_and_breakpoints(state, execution, depth)
            yield 0.0
        if len(self.slots) > 2 and self.slots[2] is not None:
            for item in self.slots[2].execute(state, execution, depth + 1):
                yield item
        state.return_value = PyNone()

    def deep_copy(self, copies: dict[int, Any]) -> "BranchNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = BranchNode(self.boxed_params, self.looping)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone


class ForNode(Node):
    def __init__(self, pattern: Node, boxed_params: BoxedNodeParams | None = None):
        super().__init__(boxed_params)
        self.pattern = pattern

    @property
    def node_name(self) -> str:
        return "for"

    def execute(self, state: Any, execution: Any, depth: int):
        self.errors_and_breakpoints(state, execution, depth)
        for item in self.slots[0].execute(state, execution, depth + 1):
            yield item
        iterable = state.return_value
        if not hasattr(iterable, "__iter__"):
            raise ExecuteException("error_for_requires_iterable")
        if self.check_increment_op_count(state, execution, 1.0):
            yield 0.0
        for current in iterable:
            for item in AssignmentNode.assign(state, execution, depth, self.pattern, current, "="):
                yield item
            self.blink(state, execution)
            try:
                for item in self.slots[1].execute(state, execution, depth + 1):
                    yield item
            except BreakStatement:
                return
            except ContinueStatement:
                continue
            self.errors_and_breakpoints(state, execution, depth)

    def deep_copy(self, copies: dict[int, Any]) -> "ForNode":
        key = id(self)
        if key in copies:
            return copies[key]
        clone = ForNode(self.pattern.deep_copy(copies), self.boxed_params)
        copies[key] = clone
        clone.slots = [slot.deep_copy(copies) if slot is not None else None for slot in self.slots]
        return clone
