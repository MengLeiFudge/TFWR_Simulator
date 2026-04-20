from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import random
import time
import subprocess
from types import SimpleNamespace
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from gamesimulator import Duration, SideEffect, just_sha256_it, num_drones, world_size_scale
from gamesimulator.config import REPO_ROOT, resolve_save_root
from gamesimulator.common.dotnet_random import DotNetRandom
from gamesimulator.runtime.execute_exception import BreakStatement, ContinueStatement, ReturnStatement
from gamesimulator.runtime.execute_exception import ExecuteException
from gamesimulator.runtime.execution import Execution
from gamesimulator.world.farm import FarmState
from gamesimulator.world.entities import create_entity_view
from gamesimulator.loader import build_global_bindings as _build_global_bindings, load_tfwr_builtins as _load_tfwr_builtins
from gamesimulator.runtime.module_state import ModuleState
from gamesimulator.parser.nodes import (
    AssignmentNode,
    BinaryExprNode,
    BracketNode,
    BranchNode,
    BreakNode,
    BoxedNodeParams,
    CallNode,
    ContinueNode,
    DictNode,
    ForNode,
    FunctionNode,
    ImportNode,
    LiteralNode,
    ListNode,
    NoOpNode,
    PassNode,
    ReturnNode,
    SequenceNode,
    TupleNode,
    UnaryExprNode,
    ValueNode,
)
from gamesimulator.parser.parser import parse
from gamesimulator.parser.parse_exception import ParseException
from gamesimulator.runtime.py_function import PyFunction
from gamesimulator.parser.program_model import Program
from gamesimulator.runtime.program_state import ProgramState
from gamesimulator.runtime.py_values import (
    GridDirection,
    PyBool,
    PyConstBag,
    PyDict,
    PyDroneHandle,
    PyGridDirection,
    PyList,
    PyNone,
    PyNumber,
    PyObjectBox,
    PyRange,
    PySet,
    PyString,
    PyTuple,
)
from gamesimulator.runner import (
    _default_items,
    _default_unlock_levels,
    coerce_items,
    coerce_globals,
    coerce_unlock_levels,
    leaderboard_goal_status,
    main as runner_main,
    run_file,
    run_file_with_context,
)
from gamesimulator.leaderboard_metadata import resolve_leaderboard_metadata
from gamesimulator.common.runtime_types import RuntimeMailbox, RuntimePlaceholders, TimerRecord
from gamesimulator.runtime.simulation import Simulation
from gamesimulator.runtime.scope import Scope
from gamesimulator.parser.token_stream import Token, TokenStream
from gamesimulator.parser.token_types import TokenType
from gamesimulator.parser.tokenizer import tokenize
from gamesimulator.runner import LeaderboardIterationResult


try:
    SAVE_ROOT = resolve_save_root()
    SAVE_ROOT_ERROR = None
except Exception as exc:
    SAVE_ROOT = None
    SAVE_ROOT_ERROR = exc


def require_save_root() -> Path:
    if SAVE_ROOT is None:
        raise unittest.SkipTest(f"TFWR_SAVE_ROOT 未配置: {SAVE_ROOT_ERROR}")
    return SAVE_ROOT


def build_global_bindings(_unused=None):
    return _build_global_bindings(require_save_root())


def load_tfwr_builtins(_unused=None):
    return _load_tfwr_builtins(require_save_root())


def copy_test_builtins(target_dir: Path) -> None:
    shutil.copy(require_save_root() / "__builtins__.py", target_dir / "__builtins__.py")


def run_execution_to_termination(execution: Execution, max_cycles: int = 20) -> None:
    for _ in range(max_cycles):
        active = [
            state
            for state in execution.states
            if state is not None and state.current_side_effect != SideEffect.TERMINATED
        ]
        if not active:
            if execution.completed_main_state is not None and execution.states and execution.states[0] is None:
                execution.states[0] = execution.completed_main_state
            return
        execution.execute(Duration.from_seconds(1.0))
    raise AssertionError("execution did not terminate in test budget")


def advance_simulation_clock(sim: Simulation, seconds: float, max_steps: int = 1000) -> None:
    goal_time = sim.current_time + Duration.from_seconds(seconds)
    for _ in range(max_steps):
        if sim.current_time >= goal_time:
            return
        previous_time = sim.current_time
        sim.run_next_step(goal_time)
        if sim.current_time <= previous_time:
            raise AssertionError("simulation clock did not advance")
    raise AssertionError("simulation clock did not reach goal in test budget")


class DurationHelperTests(unittest.TestCase):
    def test_duration_port(self) -> None:
        base = Duration.from_seconds(0.0025)
        self.assertEqual(base.nanoseconds, 2_500_000)
        self.assertEqual((base + base).nanoseconds, 5_000_000)
        self.assertEqual((base * 2).nanoseconds, 5_000_000)
        self.assertEqual((base / 2).nanoseconds, 1_250_000)
        self.assertAlmostEqual((Duration.from_seconds(1.0) / base), 400.0)
        self.assertTrue(Duration.from_seconds(0.1) < Duration.from_seconds(0.2))
        self.assertEqual(Duration.min(Duration(5), Duration(9)).nanoseconds, 5)
        self.assertEqual(str(Duration.from_seconds(1.5)), "1.5")

    def test_helper_port(self) -> None:
        self.assertEqual(
            [world_size_scale(i) for i in range(10)],
            [1, 2, 3, 4, 6, 8, 12, 16, 22, 32],
        )
        self.assertEqual([num_drones(i) for i in range(6)], [1, 2, 4, 8, 16, 32])

        seed = 123456
        random_source = random.Random(seed)
        buffer = random_source.randbytes(16)
        digest = hashlib.sha256(buffer).digest()
        expected = int.from_bytes(digest[:4], byteorder="little", signed=True) & 0x7FFFFFFF
        self.assertEqual(just_sha256_it(random.Random(seed)), expected)

    def test_dotnet_random_matches_csharp_reference_outputs(self) -> None:
        rng = DotNetRandom(1)
        self.assertAlmostEqual(rng.random(), 0.24866858415709278)
        self.assertAlmostEqual(rng.random(), 0.11074397718102856)
        self.assertAlmostEqual(rng.random(), 0.46701067987224587)

        rng = DotNetRandom(1)
        self.assertEqual(rng.randbytes(16).hex("-").upper(), "46-D0-86-82-40-97-E4-A3-95-CF-FF-46-69-9C-73-C4")

        rng = DotNetRandom(1)
        self.assertEqual(just_sha256_it(rng), 441942086)
        self.assertEqual(just_sha256_it(rng), 1602955080)
        self.assertEqual(just_sha256_it(rng), 101590770)

        rng = DotNetRandom(1)
        state = rng.getstate()
        first = rng.random()
        rng.setstate(state)
        self.assertAlmostEqual(rng.random(), first)

    def test_side_effect_members(self) -> None:
        self.assertEqual(
            SideEffect.ordered_names(),
            [
                "None",
                "Harvest",
                "CanHarvest",
                "Swap",
                "Plant",
                "Move",
                "CanMove",
                "Till",
                "GetPosX",
                "GetPosY",
                "GetWorldSize",
                "GetEntityType",
                "GetGroundType",
                "UseItem",
                "GetWater",
                "ChangeHat",
                "NumItems",
                "GetCost",
                "Clear",
                "GetCompanion",
                "Unlock",
                "NumUnlocked",
                "Measure",
                "SetExecutionSpeed",
                "SetWorldSize",
                "GetTime",
                "SpawnDrone",
                "GetDroneId",
                "NumDrones",
                "MaxDrones",
                "Await",
                "HasFinished",
                "Terminated",
                "Error",
                "DoAFlip",
                "PetThePiggy",
                "Print",
                "Simulate",
                "RunLeaderboard",
            ],
        )


class PyValueTests(unittest.TestCase):
    def test_number_bool_and_none(self) -> None:
        self.assertEqual(float(PyNumber(3.5)), 3.5)
        self.assertEqual(PyNumber.floor_division(PyNumber(7), PyNumber(2)).num, 3.0)
        self.assertEqual(PyNumber.modulo(PyNumber(-1), PyNumber(5)).num, 4.0)
        self.assertTrue(bool(PyBool(True)))
        self.assertFalse(bool(PyBool(False)))
        self.assertEqual(repr(PyBool(True)), "True")
        self.assertEqual(PyNone(), PyNone())

    def test_sequence_and_mapping_shapes(self) -> None:
        py_string = PyString("ab")
        self.assertEqual(len(py_string), 2)
        self.assertEqual(repr(py_string[0]), "a")

        py_tuple = PyTuple([PyNumber(1), PyString("x")])
        py_list = PyList([PyNumber(1), py_tuple])
        self.assertEqual(len(py_tuple), 2)
        self.assertEqual(len(py_list), 2)
        clone = py_list.deep_copy({})
        self.assertIsNot(clone, py_list)
        self.assertEqual(float(clone[0]), 1.0)

        py_set = PySet({PyString("a"), PyString("b")})
        self.assertEqual(len(py_set), 2)

        py_dict = PyDict({PyString("key"): PyObjectBox(PyNumber(3))})
        self.assertEqual(float(py_dict.at(PyString("key"))), 3.0)
        py_dict.at(PyString("key"), PyNumber(5))
        self.assertEqual(float(py_dict.at(PyString("key"))), 5.0)

    def test_range_and_direction_wrappers(self) -> None:
        py_range = PyRange(0, 5, 2)
        self.assertEqual([float(value) for value in py_range], [0.0, 2.0, 4.0])
        self.assertEqual(len(py_range), 3)

        handle = PyDroneHandle(4, generation=9)
        self.assertEqual(int(handle), 4)
        self.assertEqual(repr(handle), "<drone 9>")

        direction = PyGridDirection(GridDirection.NORTH)
        self.assertEqual(repr(direction), "North")


class ProgramStateTests(unittest.TestCase):
    def test_module_state_defaults(self) -> None:
        module_state = ModuleState()
        self.assertIsNone(module_state.global_scope)
        self.assertEqual(module_state.call_stack, [])
        self.assertIsNone(module_state.return_value)
        self.assertFalse(module_state.is_expression_static)
        self.assertIsNone(module_state.current_executing_node)

    def test_program_state_runtime_surface(self) -> None:
        program_state = ProgramState(12.0, random.Random(123), 2)
        self.assertEqual(program_state.start_op_count, 12.0)
        self.assertEqual(program_state.op_count, 12.0)
        self.assertEqual(program_state.drone_id, 2)
        self.assertEqual(program_state.current_scope.evaluate("__name__").val, PyString("__main__"))
        self.assertEqual(program_state.consume_ops(), 0.0)

        program_state.op_count += 5.0
        self.assertEqual(program_state.consume_ops(), 5.0)
        self.assertEqual(program_state.consume_ops(), 0.0)

    def test_program_state_awaited_drone_tick(self) -> None:
        program_state = ProgramState(20.0, random.Random(321), 0)
        program_state.execution_stack_index = 0
        program_state.awaited_drone_id = 7
        program_state.perform_execution_step(30.0)
        self.assertEqual(program_state.op_count, 21.0)
        self.assertEqual(program_state.consume_ops(), 0.0)

    def test_program_state_runs_generator_stack(self) -> None:
        program_state = ProgramState(0.0, random.Random(7), 0)
        syntax = SequenceNode(BoxedNodeParams())
        syntax.slots = [PassNode(BoxedNodeParams())]
        execution = SimpleNamespace()
        program_state.push_onto_execution_stack(syntax.execute(program_state, execution, 0))
        program_state.perform_execution_step(10.0)
        self.assertEqual(program_state.op_count, 1.0)
        program_state.perform_execution_step(10.0)
        self.assertEqual(program_state.current_side_effect, SideEffect.TERMINATED)

    def test_runtime_type_shape(self) -> None:
        timer = TimerRecord(Duration.from_seconds(1.0), lambda: None)
        mailbox = RuntimeMailbox(deque(), [deque() for _ in range(36)])
        placeholders = RuntimePlaceholders()
        self.assertEqual(timer.finish_time.nanoseconds, 1_000_000_000)
        self.assertEqual(len(mailbox.per_channel), 36)
        self.assertIsNone(placeholders.current_side_effect_argument)

    def test_scope_lookup(self) -> None:
        parent = Scope(None, None, None, {"parent_only"})
        parent.set_var("parent_only", PyNumber(7))
        child = Scope(None, None, parent, {"child_only"})
        child.set_var("child_only", PyString("x"))
        self.assertTrue(child.has_var("child_only"))
        self.assertTrue(child.has_var("parent_only"))
        self.assertEqual(float(child.evaluate("parent_only").val), 7.0)
        self.assertEqual(child.evaluate("child_only").val, PyString("x"))
        self.assertEqual(repr(Scope.evaluate_constant("North")), "North")


class ParserTests(unittest.TestCase):
    def test_tokenizer_basics(self) -> None:
        code = "def foo(x):\n    if x not in y:\n        return x + 1\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        tokens = [(token.type, token.value) for token in stream]
        self.assertEqual(
            tokens[:12],
            [
                (TokenType.NEW_LINE, "\n"),
                (TokenType.DEF, "def"),
                (TokenType.IDENTIFIER, "foo"),
                (TokenType.BRACKET_OPEN, "("),
                (TokenType.IDENTIFIER, "x"),
                (TokenType.BRACKET_CLOSE, ")"),
                (TokenType.COLON, ":"),
                (TokenType.NEW_LINE, "\n    "),
                (TokenType.IF, "if"),
                (TokenType.IDENTIFIER, "x"),
                (TokenType.IN, "not in"),
                (TokenType.IDENTIFIER, "y"),
            ],
        )

    def test_token_stream_consume(self) -> None:
        stream = TokenStream()
        stream.add(Token(TokenType.NEW_LINE, "\n", 0))
        stream.add(Token(TokenType.DEF, "def", 1))
        stream.add(Token(TokenType.IDENTIFIER, "foo", 5))
        self.assertEqual(stream.current.type, TokenType.NEW_LINE)
        self.assertEqual(stream.look_ahead.type, TokenType.DEF)
        self.assertEqual(stream.look_ahead_ignore_newlines.type, TokenType.IDENTIFIER)
        stream.consume(TokenType.NEW_LINE)
        self.assertEqual(stream.consume(TokenType.DEF).value, "def")
        with self.assertRaises(ParseException):
            stream.consume(TokenType.RETURN)

    def test_py_function_shape(self) -> None:
        func = PyFunction("demo", is_free=True)
        self.assertEqual(repr(func), "demo")
        clone = func.deep_copy({})
        self.assertEqual(clone.function_name, "demo")
        self.assertTrue(clone.is_free)

    def test_literal_and_sequence_nodes(self) -> None:
        state = ProgramState(0.0, random.Random(1), 0)
        literal = LiteralNode(PyNumber(7), BoxedNodeParams(word_start=1, word_end=2))
        list(literal.execute(state, None, 0))
        self.assertEqual(float(state.return_value), 7.0)

        seq = SequenceNode(BoxedNodeParams())
        seq.slots = [LiteralNode(PyNumber(1)), LiteralNode(PyNumber(2))]
        list(seq.execute(state, None, 0))
        self.assertEqual([float(v) for v in state.return_value], [1.0, 2.0])

        fn = FunctionNode([], "demo", BoxedNodeParams())
        fn.slots = [SequenceNode(BoxedNodeParams())]
        state.push_scope(Scope(fn, None, state.current_scope, set()))
        list(fn.execute(state, None, 0))
        self.assertEqual(state.return_value, PyNone())

    def test_control_flow_nodes(self) -> None:
        state = ProgramState(0.0, random.Random(1), 0)

        pass_node = PassNode(BoxedNodeParams())
        yielded = list(pass_node.execute(state, None, 0))
        self.assertEqual(yielded, [0.0])

        return_node = ReturnNode(BoxedNodeParams())
        with self.assertRaises(ReturnStatement):
            list(return_node.execute(state, None, 0))

        branch = BranchNode(BoxedNodeParams(), looping=False)
        branch.slots = [LiteralNode(PyBool(True)), SequenceNode(BoxedNodeParams())]
        list(branch.execute(state, None, 0))
        self.assertEqual(state.return_value, PyNone())

        with self.assertRaises(BreakStatement):
            list(BreakNode(BoxedNodeParams()).execute(state, None, 0))
        with self.assertRaises(ContinueStatement):
            list(ContinueNode(BoxedNodeParams()).execute(state, None, 0))

    def test_assignment_and_call_nodes(self) -> None:
        state = ProgramState(0.0, random.Random(1), 0)
        execution = SimpleNamespace(sim=None, states=[state])

        assign = AssignmentNode("=", BoxedNodeParams())
        assign.slots = [ValueNode("x", BoxedNodeParams()), LiteralNode(PyNumber(5), BoxedNodeParams())]
        list(assign.execute(state, execution, 0))
        self.assertEqual(float(state.current_scope.evaluate("x").val), 5.0)

        def binding(params, sim, exec_obj, drone_id):
            exec_obj.states[drone_id].return_value = PyNumber(float(params[0].num) + 2.0)
            return 0.0

        state.current_scope.import_var("inc", PyFunction("inc", binding=binding))
        args = SequenceNode(BoxedNodeParams())
        args.slots = [LiteralNode(PyNumber(3), BoxedNodeParams())]
        call = CallNode(BoxedNodeParams())
        call.slots = [ValueNode("inc", BoxedNodeParams()), args]
        list(call.execute(state, execution, 0))
        self.assertEqual(float(state.return_value), 5.0)

        unary = UnaryExprNode("not", BoxedNodeParams())
        unary.slots = [LiteralNode(PyBool(False), BoxedNodeParams())]
        list(unary.execute(state, execution, 0))
        self.assertTrue(bool(state.return_value))

    def test_parse_small_script(self) -> None:
        code = "\n" + "def foo(x):\n" + "    if x:\n" + "        return x + 1\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        self.assertIsInstance(program, Program)
        self.assertIsInstance(program.syntax_tree, SequenceNode)
        self.assertEqual(len(program.syntax_tree.slots), 1)
        self.assertEqual(program.all_vars, {"foo", "x"})
        self.assertEqual(program.global_vars, {"foo"})
        def_node = program.syntax_tree.slots[0]
        self.assertEqual(def_node.func_name, "foo")
        function_node = def_node.slots[0]
        self.assertEqual(function_node.func_name, "foo")
        self.assertEqual(function_node.param_names, ["x"])

    def test_parse_assignment_call_and_while(self) -> None:
        code = (
            "\n"
            + "x = 1\n"
            + "inc(x)\n"
            + "while x:\n"
            + "    x = x + 1\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        self.assertEqual(len(program.syntax_tree.slots), 3)
        self.assertIsInstance(program.syntax_tree.slots[0], AssignmentNode)
        self.assertIsInstance(program.syntax_tree.slots[1], CallNode)
        self.assertIsInstance(program.syntax_tree.slots[2], BranchNode)

    def test_parse_import_and_for_range(self) -> None:
        code = (
            "\n"
            + "from __builtins__ import *\n"
            + "items = [1, 2]\n"
            + "for _ in range(2):\n"
            + "    x = x + 1\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        self.assertEqual(len(program.syntax_tree.slots), 3)
        self.assertIsInstance(program.syntax_tree.slots[0], ImportNode)
        self.assertIsInstance(program.syntax_tree.slots[1], AssignmentNode)
        self.assertIsInstance(program.syntax_tree.slots[1].slots[1], ListNode)
        self.assertIsInstance(program.syntax_tree.slots[2], ForNode)

    def test_parse_name_compare(self) -> None:
        code = "\n" + "if __name__ == \"__main__\":\n" + "    pass\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        self.assertEqual(len(program.syntax_tree.slots), 1)
        branch = program.syntax_tree.slots[0]
        self.assertIsInstance(branch, BranchNode)

    def test_parse_default_args_and_dict_literal(self) -> None:
        code = (
            "\n"
            + "def foo(count=5, data={}):\n"
            + "    return {\"x\": count}\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        def_node = program.syntax_tree.slots[0]
        function_node = def_node.slots[0]
        self.assertEqual(function_node.param_names, ["count", "data"])
        self.assertEqual(len(function_node.slots), 3)
        return_node = function_node.slots[0].slots[0]
        self.assertIsInstance(return_node.slots[0], DictNode)

    def test_parse_tuple_assign_and_dot_index(self) -> None:
        code = (
            "\n"
            + "x, y = get_pos_x(), get_pos_y()\n"
            + "item = Items.Bone\n"
            + "value = grid[x]\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        self.assertEqual(len(program.syntax_tree.slots), 3)
        self.assertIsInstance(program.syntax_tree.slots[0], AssignmentNode)
        self.assertIsInstance(program.syntax_tree.slots[0].slots[0], TupleNode)
        self.assertIsInstance(program.syntax_tree.slots[1].slots[1], BinaryExprNode)
        self.assertEqual(program.syntax_tree.slots[1].slots[1].op, ".")
        self.assertIsInstance(program.syntax_tree.slots[2].slots[1], BinaryExprNode)
        self.assertEqual(program.syntax_tree.slots[2].slots[1].op, "[]")

    def test_parse_slice_index(self) -> None:
        code = "\n" + "part = all_start_pos[1:]\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        node = program.syntax_tree.slots[0].slots[1]
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "[]")
        self.assertIsInstance(node.slots[1], BracketNode)


class SimulationTests(unittest.TestCase):
    def test_timer_ordering_and_speed(self) -> None:
        sim = Simulation(seed=1)
        fired: list[str] = []
        sim.start_timer(lambda: fired.append("late"), Duration.from_seconds(1.0))
        sim.start_timer(lambda: fired.append("early"), Duration.from_seconds(0.5))

        timer = sim.pop_due_timer(Duration.from_seconds(0.75))
        self.assertIsNotNone(timer)
        timer.func()
        self.assertEqual(fired, ["early"])
        self.assertEqual(sim.current_time.nanoseconds, 500_000_000)
        self.assertIsNone(sim.pop_due_timer(Duration.from_seconds(0.75)))

        sim.change_execution_speed(4.0)
        self.assertEqual(sim.op_duration.nanoseconds, 625_000)
        self.assertEqual(sim.speed_factor, 4.0)

    def test_seed_fanout_is_stable(self) -> None:
        left = Simulation(seed=123)
        right = Simulation(seed=123)
        self.assertEqual(left.random_water_decay.random(), right.random_water_decay.random())
        self.assertEqual(left.random_grow_time.random(), right.random_grow_time.random())
        self.assertEqual(left.random_companion_type.random(), right.random_companion_type.random())
        self.assertEqual(left.random_companion_offset.random(), right.random_companion_offset.random())
        self.assertEqual(left.random_grass_respawn.random(), right.random_grass_respawn.random())
        self.assertEqual(left.random_cactus.random(), right.random_cactus.random())
        self.assertEqual(left.random_pumpkin.random(), right.random_pumpkin.random())

    def test_random_domains_follow_original_grouping(self) -> None:
        sim = Simulation(seed=123)
        self.assertIs(sim.random_water_decay, sim.random_various)
        self.assertIs(sim.random_grow_time, sim.random_various)
        self.assertIs(sim.random_grass_respawn, sim.random_various)
        self.assertIs(sim.random_companion_type, sim.random_poly)
        self.assertIs(sim.random_companion_offset, sim.random_poly)


class ExecutionTests(unittest.TestCase):
    def test_op_scheduling_core(self) -> None:
        sim = Simulation(seed=1)
        execution = Execution(sim, None, 99)
        state = execution.states[0]
        execution.execute(Duration.from_seconds(0.5))
        self.assertEqual(state.current_side_effect, SideEffect.TERMINATED)
        self.assertEqual(execution.global_op_count, 199)
        self.assertEqual(execution.next_execution_time.nanoseconds, sim.current_time.nanoseconds)

    def test_action_side_effect_ops_remain_visible_to_consume_ops(self) -> None:
        bindings = build_global_bindings()
        farm = FarmState(bindings)
        sim = Simulation(seed=1)
        sim.farm = farm
        has_unknown, stream = tokenize("\npass\n")
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 999, global_bindings=bindings)
        state = execution.states[0]
        state.current_side_effect = SideEffect.HARVEST

        execution._apply_side_effect(state)

        self.assertEqual(state.consume_ops(), 200.0)

    def test_set_world_size_noop_does_not_reseed_initial_grass_companions(self) -> None:
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 5})
        sim = Simulation(seed=1)
        sim.farm = farm
        execution = Execution(sim, None, 1000, global_bindings=bindings)
        state = execution.states[0]
        before = farm.grid.get_cell((0, 0)).companion
        state.current_side_effect = SideEffect.SET_WORLD_SIZE
        state.current_side_effect_argument = PyNumber(8)

        execution._apply_side_effect(state)

        self.assertEqual(farm.grid.get_cell((0, 0)).companion, before)

    def test_random_builtin_uses_program_state_random_domain(self) -> None:
        code = "\n" + "value = random()\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 1001)
        state = execution.states[0]
        snapshot = state.random_random.getstate()
        expected = state.random_random.random()
        state.random_random.setstate(snapshot)

        run_execution_to_termination(execution)

        self.assertAlmostEqual(float(state.current_scope.evaluate("value").val), expected)

    def test_time_and_tick_count_surface(self) -> None:
        sim = Simulation(seed=1)
        execution = Execution(sim, None, 1)
        state = execution.states[0]
        self.assertEqual(state.start_op_count, 0.0)
        state.op_count = 42.0
        self.assertEqual(state.op_count - state.start_op_count, 42.0)
        sim.add_ops_to_current_time(10.0)
        self.assertEqual(sim.current_time.nanoseconds, sim.op_duration.nanoseconds * 10)

    def test_execution_with_minimal_builtins(self) -> None:
        code = "\n" + "x = get_tick_count()\n" + "y = get_time()\n" + "quick_print(y)\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 5)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("x").val), 0.0)
        self.assertEqual(float(state.current_scope.evaluate("y").val), 0.0)
        self.assertEqual(sim.logs, ["0.0"])

    def test_execution_with_const_bag_globals(self) -> None:
        code = "\n" + "item = Items.Bone\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        globals_map = build_global_bindings()
        execution = Execution(sim, program.syntax_tree, 6, global_bindings=globals_map)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        self.assertEqual(state.current_scope.evaluate("item").val, globals_map["Items"].evaluate("Bone"))

    def test_execution_with_user_function_call(self) -> None:
        code = (
            "\n"
            + "def inc(x):\n"
            + "    return x + 1\n"
            + "value = inc(2)\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 7)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("value").val), 3.0)

    def test_execution_with_nested_tuple_unpack(self) -> None:
        code = "\n" + "label, (x, y) = ('ok', (2, 3))\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 78)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        self.assertEqual(state.current_scope.evaluate("label").val, PyString("ok"))
        self.assertEqual(float(state.current_scope.evaluate("x").val), 2.0)
        self.assertEqual(float(state.current_scope.evaluate("y").val), 3.0)

    def test_execution_with_static_function_call_literal_arg_is_free(self) -> None:
        code = (
            "\n"
            + "def probe(x):\n"
            + "    return get_tick_count()\n"
            + "value = probe('x')\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 79)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("value").val), 1.0)

    def test_execution_with_static_dot_access_is_free(self) -> None:
        code = "\n" + "tick0 = get_tick_count()\n" + "item = Items.Hay\n" + "tick1 = get_tick_count()\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 80, global_bindings=build_global_bindings())
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("tick0").val), float(state.current_scope.evaluate("tick1").val))

    def test_execution_with_default_argument(self) -> None:
        code = (
            "\n"
            + "def add_one(x=1):\n"
            + "    return x + 1\n"
            + "value = add_one()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 8)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("value").val), 2.0)

    def test_execution_with_list_methods(self) -> None:
        code = (
            "\n"
            + "row = []\n"
            + "row.append(1)\n"
            + "append(row, 2)\n"
            + "value = row[1]\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        execution = Execution(sim, program.syntax_tree, 11)
        execution.execute(Duration.from_seconds(1.0))
        state = execution.states[0]
        row = state.current_scope.evaluate("row").val
        self.assertEqual([float(item.num) for item in row.items], [1.0, 2.0])
        self.assertEqual(float(state.current_scope.evaluate("value").val), 2.0)

    def test_execution_with_pure_builtins(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(
            bindings,
            unlock_levels={unlocks_bag.evaluate("Carrots"): 3},
            items={
                items_bag.evaluate("Hay"): 8,
                items_bag.evaluate("Wood"): 8,
            },
        )
        sim = Simulation(seed=1)
        sim.farm = farm
        code = (
            "\n"
            + "vals = list(range(3))\n"
            + "count = len(vals)\n"
            + "small = min(2, 5)\n"
            + "big = max(2, 5)\n"
            + "neg = abs(-7)\n"
            + "txt = str(big)\n"
            + "cost = get_cost(Entities.Carrot)\n"
            + "hay = cost[Items.Hay]\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 12, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("count").val), 3.0)
        self.assertEqual(float(state.current_scope.evaluate("small").val), 2.0)
        self.assertEqual(float(state.current_scope.evaluate("big").val), 5.0)
        self.assertEqual(float(state.current_scope.evaluate("neg").val), 7.0)
        self.assertEqual(state.current_scope.evaluate("txt").val, PyString("5.0"))
        self.assertEqual(float(state.current_scope.evaluate("hay").val), 4.0)

    def test_execution_with_spawn_wait_and_has_finished(self) -> None:
        code = (
            "\n"
            + "def child():\n"
            + "    return 7\n"
            + "h = spawn_drone(child)\n"
            + "count0 = num_drones()\n"
            + "done0 = has_finished(h)\n"
            + "value = wait_for(h)\n"
            + "done1 = has_finished(h)\n"
            + "count1 = num_drones()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Megafarm"): 2})
        sim = Simulation(seed=1)
        sim.farm = farm
        execution = Execution(sim, program.syntax_tree, 14, global_bindings=bindings)
        run_execution_to_termination(execution, max_cycles=50)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("count0").val), 2.0)
        self.assertFalse(bool(state.current_scope.evaluate("done0").val))
        self.assertEqual(float(state.current_scope.evaluate("value").val), 7.0)
        self.assertTrue(bool(state.current_scope.evaluate("done1").val))
        self.assertEqual(float(state.current_scope.evaluate("count1").val), 1.0)

    def test_execution_get_cost_for_unlocks(self) -> None:
        bindings = build_global_bindings()
        code = (
            "\n"
            + "loops_cost = get_cost(Unlocks.Loops)\n"
            + "loops_hay = loops_cost[Items.Hay]\n"
            + "expand0 = get_cost(Unlocks.Expand, 0)\n"
            + "expand0_hay = expand0[Items.Hay]\n"
            + "expand1 = get_cost(Unlocks.Expand, 1)\n"
            + "expand1_wood = expand1[Items.Wood]\n"
            + "expand5 = get_cost(Unlocks.Expand, 5)\n"
            + "expand5_pumpkin = expand5[Items.Pumpkin]\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        farm = FarmState(bindings)
        sim = Simulation(seed=1)
        sim.farm = farm
        execution = Execution(sim, program.syntax_tree, 15, global_bindings=bindings)
        run_execution_to_termination(execution, max_cycles=80)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("loops_hay").val), 5.0)
        self.assertEqual(float(state.current_scope.evaluate("expand0_hay").val), 30.0)
        self.assertEqual(float(state.current_scope.evaluate("expand1_wood").val), 20.0)
        self.assertEqual(float(state.current_scope.evaluate("expand5_pumpkin").val), 8000.0)


class LoaderTests(unittest.TestCase):
    def test_build_global_bindings(self) -> None:
        bindings = build_global_bindings()
        module = load_tfwr_builtins()
        self.assertIn("Items", bindings)
        self.assertIn("Entities", bindings)
        self.assertIn("North", bindings)
        self.assertIsInstance(bindings["Items"], PyConstBag)
        self.assertEqual(str(bindings["North"]), "North")
        self.assertIn("Bone", module.Items.__annotations__)
        self.assertIn("Tree", module.Entities.__annotations__)
        self.assertIn("Expand", module.Unlocks.__annotations__)
        self.assertIn("Bone", bindings["Items"].elements)
        self.assertIn("Tree", bindings["Entities"].elements)
        self.assertIn("Expand", bindings["Unlocks"].elements)

    def test_coerced_unlocks_and_items_remain_usable_across_binding_reloads(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        unlock_levels = coerce_unlock_levels(outer_bindings["Unlocks"], outer_bindings)
        farm = FarmState(inner_bindings, unlock_levels=unlock_levels, items={})
        self.assertEqual(
            farm.num_unlocked(inner_bindings["Unlocks"].evaluate("Expand")),
            _default_unlock_levels(inner_bindings)[inner_bindings["Unlocks"].evaluate("Expand")],
        )
        self.assertGreater(farm.max_drones(), 1)

        item_key_outer = outer_bindings["Items"].evaluate("Hay")
        item_levels = coerce_items(
            PyDict({item_key_outer: PyObjectBox(PyNumber(9.0))}),
            inner_bindings,
        )
        self.assertEqual(item_levels[inner_bindings["Items"].evaluate("Hay")], 9.0)

    def test_coerce_unlock_levels_for_dict_adds_reset_baseline_and_clamps(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        source = PyDict(
            {
                outer_bindings["Unlocks"].evaluate("Expand"): PyObjectBox(PyNumber(99.0)),
                outer_bindings["Unlocks"].evaluate("Speed"): PyObjectBox(PyNumber(0.0)),
            }
        )

        levels = coerce_unlock_levels(source, inner_bindings)

        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Expand")], 9)
        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Loops")], 1)
        self.assertNotIn(inner_bindings["Unlocks"].evaluate("Speed"), levels)

    def test_coerce_unlock_levels_for_iterable_adds_reset_baseline_and_uses_max_level(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        levels = coerce_unlock_levels(
            PyList([outer_bindings["Unlocks"].evaluate("Expand")]),
            inner_bindings,
        )

        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Expand")], 9)
        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Loops")], 1)

    def test_coerce_unlock_levels_for_iterable_tuple_overrides_level(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        levels = coerce_unlock_levels(
            PyList(
                [
                    PyTuple([outer_bindings["Unlocks"].evaluate("Expand"), PyNumber(3.0)]),
                    PyTuple([outer_bindings["Unlocks"].evaluate("Watering"), PyNumber(-1.0)]),
                ]
            ),
            inner_bindings,
        )

        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Expand")], 3)
        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Watering")], 9)

    def test_coerce_unlock_levels_for_dict_uses_negative_as_max_level(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        source = PyDict(
            {
                outer_bindings["Unlocks"].evaluate("Expand"): PyObjectBox(PyNumber(-1.0)),
                outer_bindings["Unlocks"].evaluate("Watering"): PyObjectBox(PyNumber(-3.0)),
            }
        )

        levels = coerce_unlock_levels(source, inner_bindings)

        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Expand")], 9)
        self.assertEqual(levels[inner_bindings["Unlocks"].evaluate("Watering")], 9)

    def test_coerce_unlock_levels_rejects_non_unlock_keys(self) -> None:
        bindings = build_global_bindings()

        with self.assertRaises(ExecuteException):
            coerce_unlock_levels(
                PyDict({PyString("Expand"): PyObjectBox(PyNumber(1.0))}),
                bindings,
            )

        with self.assertRaises(ExecuteException):
            coerce_unlock_levels(
                PyList([PyString("Expand")]),
                bindings,
            )

    def test_coerce_items_clamps_negative_values_to_zero(self) -> None:
        outer_bindings = build_global_bindings()
        inner_bindings = build_global_bindings()

        item_levels = coerce_items(
            PyDict(
                {
                    outer_bindings["Items"].evaluate("Hay"): PyObjectBox(PyNumber(-5.0)),
                    outer_bindings["Items"].evaluate("Wood"): PyObjectBox(PyNumber(9.0)),
                }
            ),
            inner_bindings,
        )

        self.assertEqual(item_levels[inner_bindings["Items"].evaluate("Hay")], 0.0)
        self.assertEqual(item_levels[inner_bindings["Items"].evaluate("Wood")], 9.0)

    def test_coerce_items_rejects_non_item_keys(self) -> None:
        with self.assertRaises(ExecuteException):
            coerce_items(
                PyDict({PyString("Hay"): PyObjectBox(PyNumber(1.0))}),
                build_global_bindings(),
            )

    def test_coerce_globals_accepts_string_keys_only(self) -> None:
        globals_map = coerce_globals(
            PyDict({PyString("seed_hint"): PyObjectBox(PyNumber(13.0))})
        )
        self.assertIn("seed_hint", globals_map)
        self.assertEqual(float(globals_map["seed_hint"].num), 13.0)

        with self.assertRaises(ExecuteException):
            coerce_globals(
                PyDict({build_global_bindings()["Items"].evaluate("Hay"): PyObjectBox(PyNumber(1.0))})
            )


class WorldCoreTests(unittest.TestCase):
    def test_dependency_gate_rejects_locked_syntax_and_builtins(self) -> None:
        bindings = build_global_bindings()

        code_assignment = "\n" + "x = 1\n"
        has_unknown, stream = tokenize(code_assignment)
        self.assertFalse(has_unknown)
        program = parse(stream)
        farm = FarmState(bindings, unlock_levels={})
        sim = Simulation(seed=1, leaderboard_type="simulation")
        sim.farm = farm
        execution = Execution(sim, program.syntax_tree, 101, global_bindings=bindings)
        with self.assertRaises(ExecuteException):
            run_execution_to_termination(execution, max_cycles=20)

        code_for = "\n" + "for i in range(1):\n" + "    pass\n"
        has_unknown, stream = tokenize(code_for)
        self.assertFalse(has_unknown)
        program = parse(stream)
        expand = bindings["Unlocks"].evaluate("Expand")

        farm_expand1 = FarmState(bindings, unlock_levels={expand: 1})
        sim_expand1 = Simulation(seed=1, leaderboard_type="simulation")
        sim_expand1.farm = farm_expand1
        execution_expand1 = Execution(sim_expand1, program.syntax_tree, 102, global_bindings=bindings)
        with self.assertRaises(ExecuteException):
            run_execution_to_termination(execution_expand1, max_cycles=40)

        farm_expand2 = FarmState(bindings, unlock_levels={expand: 2})
        sim_expand2 = Simulation(seed=1, leaderboard_type="simulation")
        sim_expand2.farm = farm_expand2
        execution_expand2 = Execution(sim_expand2, program.syntax_tree, 103, global_bindings=bindings)
        run_execution_to_termination(execution_expand2, max_cycles=40)

        code_world_size = "\n" + "x = get_world_size()\n"
        has_unknown, stream = tokenize(code_world_size)
        self.assertFalse(has_unknown)
        program = parse(stream)
        variables = bindings["Unlocks"].evaluate("Variables")

        farm_expand1_builtin = FarmState(bindings, unlock_levels={expand: 1, variables: 1})
        sim_expand1_builtin = Simulation(seed=1, leaderboard_type="simulation")
        sim_expand1_builtin.farm = farm_expand1_builtin
        execution_expand1_builtin = Execution(sim_expand1_builtin, program.syntax_tree, 104, global_bindings=bindings)
        with self.assertRaises(ExecuteException):
            run_execution_to_termination(execution_expand1_builtin, max_cycles=20)

        farm_expand2_builtin = FarmState(bindings, unlock_levels={expand: 2, variables: 1})
        sim_expand2_builtin = Simulation(seed=1, leaderboard_type="simulation")
        sim_expand2_builtin.farm = farm_expand2_builtin
        execution_expand2_builtin = Execution(sim_expand2_builtin, program.syntax_tree, 105, global_bindings=bindings)
        run_execution_to_termination(execution_expand2_builtin, max_cycles=20)

    def test_basic_world_queries_and_move(self) -> None:
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=1)
        sim.farm = farm
        code = (
            "\n"
            + "x0 = get_pos_x()\n"
            + "y0 = get_pos_y()\n"
            + "size = get_world_size()\n"
            + "ok = move(East)\n"
            + "x1 = get_pos_x()\n"
            + "c1 = can_move(West)\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 9, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("x0").val), 0.0)
        self.assertEqual(float(state.current_scope.evaluate("y0").val), 0.0)
        self.assertEqual(float(state.current_scope.evaluate("x1").val), 1.0)
        self.assertTrue(bool(state.current_scope.evaluate("ok").val))
        self.assertTrue(bool(state.current_scope.evaluate("c1").val))
        self.assertEqual(float(state.current_scope.evaluate("size").val), farm.grid.world_size[1])

    def test_num_items_num_unlocked_till_and_ground(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(
            bindings,
            unlock_levels={unlocks_bag.evaluate("Expand"): 9, unlocks_bag.evaluate("Megafarm"): 2},
            items={items_bag.evaluate("Water"): 12},
        )
        sim = Simulation(seed=1)
        sim.farm = farm
        code = (
            "\n"
            + "w = num_items(Items.Water)\n"
            + "u = num_unlocked(Unlocks.Expand)\n"
            + "g0 = get_ground_type()\n"
            + "e0 = get_entity_type()\n"
            + "till()\n"
            + "g1 = get_ground_type()\n"
            + "e1 = get_entity_type()\n"
            + "m = max_drones()\n"
            + "n = num_drones()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 10, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("w").val), 12.0)
        self.assertEqual(float(state.current_scope.evaluate("u").val), 9.0)
        self.assertEqual(state.current_scope.evaluate("g0").val, bindings["Grounds"].evaluate("Grassland"))
        self.assertEqual(state.current_scope.evaluate("e0").val, bindings["Entities"].evaluate("Grass"))
        self.assertEqual(state.current_scope.evaluate("g1").val, bindings["Grounds"].evaluate("Soil"))
        self.assertEqual(state.current_scope.evaluate("e1").val, PyNone())
        self.assertEqual(float(state.current_scope.evaluate("m").val), 4.0)
        self.assertEqual(float(state.current_scope.evaluate("n").val), 1.0)

    def test_harvest_plant_and_water(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        farm = FarmState(bindings, items={items_bag.evaluate("Water"): 4})
        sim = Simulation(seed=1)
        sim.farm = farm
        code = (
            "\n"
            + "ready0 = can_harvest()\n"
            + "harvest()\n"
            + "hay = num_items(Items.Hay)\n"
            + "till()\n"
            + "plant(Entities.Bush)\n"
            + "ready1 = can_harvest()\n"
            + "entity1 = get_entity_type()\n"
            + "use_item(Items.Water, 2)\n"
            + "water = get_water()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 11, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertFalse(bool(state.current_scope.evaluate("ready0").val))
        self.assertEqual(float(state.current_scope.evaluate("hay").val), 0.0)
        self.assertFalse(bool(state.current_scope.evaluate("ready1").val))
        self.assertEqual(state.current_scope.evaluate("entity1").val, entities_bag.evaluate("Bush"))
        self.assertEqual(float(state.current_scope.evaluate("water").val), 0.5)

    def test_grass_maturity_time(self) -> None:
        bindings = build_global_bindings()
        farm = FarmState(bindings)
        sim = Simulation(seed=1)
        sim.farm = farm
        code = (
            "\n"
            + "ready0 = can_harvest()\n"
            + "do_a_flip()\n"
            + "do_a_flip()\n"
            + "do_a_flip()\n"
            + "ready1 = can_harvest()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 11, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertFalse(bool(state.current_scope.evaluate("ready0").val))
        self.assertTrue(bool(state.current_scope.evaluate("ready1").val))

    def test_growth_companion_and_fertilizer(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        farm = FarmState(
            bindings,
            items={
                items_bag.evaluate("Water"): 8,
                items_bag.evaluate("Hay"): 8,
                items_bag.evaluate("Wood"): 8,
                items_bag.evaluate("Fertilizer"): 4,
            },
        )
        sim = Simulation(seed=1)
        sim.farm = farm
        farm.random = sim.random_various
        code = (
            "\n"
            + "till()\n"
            + "plant(Entities.Carrot)\n"
            + "comp = get_companion()\n"
            + "use_item(Items.Fertilizer, 4)\n"
            + "ready0 = can_harvest()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 13, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertTrue(bool(state.current_scope.evaluate("ready0").val))
        comp = state.current_scope.evaluate("comp").val
        self.assertIsInstance(comp, PyTuple)
        self.assertEqual(len(comp.elements), 2)

    def test_get_cost_tree_and_bush_return_empty_dict(self) -> None:
        bindings = build_global_bindings()
        code = (
            "\n"
            + "tree_cost = get_cost(Entities.Tree)\n"
            + "bush_cost = get_cost(Entities.Bush)\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        sim.farm = FarmState(bindings)
        execution = Execution(sim, program.syntax_tree, 18, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertIsInstance(state.current_scope.evaluate("tree_cost").val, PyDict)
        self.assertEqual(len(state.current_scope.evaluate("tree_cost").val.items), 0)
        self.assertIsInstance(state.current_scope.evaluate("bush_cost").val, PyDict)
        self.assertEqual(len(state.current_scope.evaluate("bush_cost").val.items), 0)

    def test_harvesting_unready_growable_clears_without_yield(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        farm = FarmState(
            bindings,
            items={
                items_bag.evaluate("Hay"): 8,
                items_bag.evaluate("Wood"): 8,
            },
        )
        sim = Simulation(seed=1)
        sim.farm = farm
        drone = farm.drones[0]
        drone.till()
        self.assertTrue(drone.plant(entities_bag.evaluate("Tree")))

        before_wood = farm.num_items(items_bag.evaluate("Wood"))
        self.assertTrue(drone.harvest())

        self.assertEqual(farm.num_items(items_bag.evaluate("Wood")), before_wood)
        self.assertIsNone(farm.grid.get_entity((0, 0)))

    def test_measure_and_hat_speed_controls(self) -> None:
        bindings = build_global_bindings()
        entities_bag = bindings["Entities"]
        hats_bag = bindings["Hats"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=1)
        sim.farm = farm
        farm.random = sim.random_various
        farm.grid.get_cell((0, 0)).entity = entities_bag.evaluate("Sunflower")
        farm.grid.get_cell((0, 0)).petals = 13
        farm.grid.get_cell((0, 0)).mature = True
        code = (
            "\n"
            + "m0 = measure()\n"
            + "set_execution_speed(0.5)\n"
            + "change_hat(Hats.Dinosaur_Hat)\n"
            + "c = can_move(West)\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 15, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("m0").val), 13.0)
        self.assertFalse(bool(state.current_scope.evaluate("c").val))
        self.assertEqual(sim.speed_factor, 0.5)

    def test_special_entity_yields(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(
            bindings,
            unlock_levels={
                unlocks_bag.evaluate("Expand"): 9,
                unlocks_bag.evaluate("Sunflowers"): 1,
            },
        )
        sim = Simulation(seed=1)
        sim.farm = farm
        farm.random = sim.random_various

        sunflower = entities_bag.evaluate("Sunflower")
        for x in range(5):
            for y in range(2):
                cell = farm.grid.get_cell((x, y))
                cell.entity = sunflower
                cell.mature = True
                cell.petals = 10
        farm.grid.get_cell((0, 0)).petals = 15

        cactus = entities_bag.evaluate("Cactus")
        farm.grid.get_cell((0, 2)).entity = cactus
        farm.grid.get_cell((0, 2)).mature = True
        farm.grid.get_cell((0, 2)).variant = 3
        farm.grid.get_cell((1, 2)).entity = cactus
        farm.grid.get_cell((1, 2)).mature = True
        farm.grid.get_cell((1, 2)).variant = 3

        pumpkin = entities_bag.evaluate("Pumpkin")
        farm.grid.get_cell((0, 3)).entity = pumpkin
        farm.grid.get_cell((0, 3)).mature = True
        farm.grid.get_cell((1, 3)).entity = pumpkin
        farm.grid.get_cell((1, 3)).mature = True

        drone = farm.drones[0]
        drone.x = 0
        drone.y = 0
        self.assertEqual(drone.harvest(), True)
        self.assertEqual(farm.num_items(items_bag.evaluate("Power")), 15.0 * 8.0)

        drone.x = 0
        drone.y = 2
        self.assertEqual(drone.harvest(), True)
        self.assertEqual(farm.num_items(items_bag.evaluate("Cactus")), 4.0)

        drone.x = 0
        drone.y = 3
        self.assertEqual(drone.harvest(), True)
        self.assertEqual(farm.num_items(items_bag.evaluate("Pumpkin")), 1.0)

    def test_swap_builtin(self) -> None:
        bindings = build_global_bindings()
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=1)
        sim.farm = farm
        farm.random = sim.random_various
        farm.grid.get_cell((0, 0)).entity = entities_bag.evaluate("Bush")
        farm.grid.get_cell((1, 0)).entity = entities_bag.evaluate("Tree")
        code = "\n" + "ok = swap(East)\n" + "e = get_entity_type()\n"
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 17, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertTrue(bool(state.current_scope.evaluate("ok").val))
        self.assertEqual(state.current_scope.evaluate("e").val, entities_bag.evaluate("Tree"))

    def test_clear_unlock_and_flip(self) -> None:
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 0})
        sim = Simulation(seed=1)
        sim.farm = farm
        farm.random = sim.random_various
        code = (
            "\n"
            + "unlock(Unlocks.Expand)\n"
            + "size1 = get_world_size()\n"
            + "move(North)\n"
            + "clear()\n"
            + "x0 = get_pos_x()\n"
            + "y0 = get_pos_y()\n"
            + "do_a_flip()\n"
        )
        has_unknown, stream = tokenize(code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(sim, program.syntax_tree, 16, global_bindings=bindings)
        run_execution_to_termination(execution)
        state = execution.states[0]
        self.assertEqual(float(state.current_scope.evaluate("size1").val), 3.0)
        self.assertEqual(float(state.current_scope.evaluate("x0").val), 0.0)
        self.assertEqual(float(state.current_scope.evaluate("y0").val), 0.0)

    def test_get_entity_object_reuses_cached_view(self) -> None:
        farm = FarmState(build_global_bindings())
        first = farm.get_entity_object((0, 0))
        second = farm.get_entity_object((0, 0))
        self.assertIs(first, second)

    def test_passive_update_skips_view_creation_for_mature_cells(self) -> None:
        farm = FarmState(build_global_bindings())
        with mock.patch("gamesimulator.world.farm.create_entity_view", wraps=create_entity_view) as create_view_mock:
            farm.passive_update(0.1, random.Random(1))
        self.assertEqual(create_view_mock.call_count, 0)


class EntityParityTests(unittest.TestCase):
    def test_companion_capable_entity_assigns_companion_on_plant(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        farm = FarmState(
            bindings,
            items={
                items_bag.evaluate("Hay"): 8,
                items_bag.evaluate("Wood"): 8,
            },
        )
        sim = Simulation(seed=7)
        sim.farm = farm
        drone = farm.drones[0]
        drone.till()

        self.assertTrue(drone.plant(entities_bag.evaluate("Tree")))

        cell = farm.grid.get_cell((0, 0))
        self.assertIsNotNone(cell.companion)

    def test_initial_grass_assigns_companion_on_farm_creation(self) -> None:
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=7)
        sim.farm = farm

        cell = farm.grid.get_cell((0, 0))
        self.assertEqual(cell.entity, farm.entity("Grass"))
        self.assertIsNotNone(cell.companion)

    def test_initial_grass_starts_unready_then_grows_ready(self) -> None:
        bindings = build_global_bindings()
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=7)
        sim.farm = farm
        drone = farm.drones[0]

        self.assertFalse(drone.can_harvest())
        advance_simulation_clock(sim, 0.5)
        self.assertTrue(drone.can_harvest())

    def test_grass_respawn_assigns_companion_immediately(self) -> None:
        bindings = build_global_bindings()
        farm = FarmState(bindings)
        sim = Simulation(seed=7)
        sim.farm = farm
        drone = farm.drones[0]

        self.assertTrue(drone.harvest())

        cell = farm.grid.get_cell((0, 0))
        self.assertEqual(cell.entity, farm.entity("Grass"))
        self.assertIsNotNone(cell.companion)

    def test_companion_selection_matches_original_randompoly_sequence(self) -> None:
        bindings = build_global_bindings()
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=7)
        sim.farm = farm
        drone = farm.drones[0]

        expected_rng = DotNetRandom(0)
        expected_rng.setstate(sim.random_poly.getstate())
        type_index_to_name = {0: "Grass", 1: "Bush", 2: "Carrot", 3: "Tree"}

        def next_expected(pos, entity):
            radius = 3
            while True:
                dx = expected_rng.randint(-radius, radius)
                dy = expected_rng.randint(-radius, radius)
                wrapped = farm.grid.wrap((pos[0] + dx, pos[1] + dy))
                if farm.grid.world_size[1] != 1 and (wrapped == pos or abs(dx) + abs(dy) > radius):
                    continue
                expected_pos = wrapped
                break
            while True:
                expected_type = farm.entity(type_index_to_name[expected_rng.randrange(4)])
                if expected_type != entity:
                    return (expected_type, expected_pos)

        tree = entities_bag.evaluate("Tree")
        bush = entities_bag.evaluate("Bush")
        expected_tree = next_expected((0, 0), tree)
        expected_bush = next_expected((1, 0), bush)

        drone.till()
        self.assertTrue(drone.plant(tree))
        self.assertEqual(farm.grid.get_cell((0, 0)).companion, expected_tree)

        self.assertTrue(drone.move(bindings["East"])[0])
        drone.till()
        self.assertTrue(drone.plant(bush))
        self.assertEqual(farm.grid.get_cell((1, 0)).companion, expected_bush)

    def test_water_decay_uses_runtime_timer_even_without_actions(self) -> None:
        farm = FarmState(build_global_bindings())
        sim = Simulation(seed=7)
        sim.farm = farm
        farm.grid.set_water_volume((0, 0), 1.0)

        with mock.patch.object(sim.random_water_decay, "random", return_value=0.0):
            advance_simulation_clock(sim, 0.1)

        self.assertAlmostEqual(farm.grid.get_water_volume((0, 0)), 0.99)

    def test_power_timer_consumes_used_power(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        farm = FarmState(bindings, items={items_bag.evaluate("Power"): 10.0})
        sim = Simulation(seed=7)
        sim.farm = farm
        farm.used_power = 3.5

        advance_simulation_clock(sim, 0.2)

        self.assertAlmostEqual(farm.num_items(items_bag.evaluate("Power")), 6.5)
        self.assertAlmostEqual(farm.used_power, 0.0)

    def test_growth_reschedules_when_water_decay_changes_speed(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        farm = FarmState(
            bindings,
            items={
                items_bag.evaluate("Hay"): 4,
                items_bag.evaluate("Wood"): 4,
            },
        )
        sim = Simulation(seed=7)
        sim.farm = farm
        drone = farm.drones[0]
        drone.till()
        with mock.patch.object(farm, "sample_growth_seconds", return_value=10.0):
            self.assertTrue(drone.plant(entities_bag.evaluate("Carrot")))
        farm.grid.set_water_volume((0, 0), 1.0)

        with mock.patch.object(sim.random_water_decay, "random", return_value=0.0):
            advance_simulation_clock(sim, 0.2)

        obj = farm.get_entity_object((0, 0))
        expected = 0.1 / (10.0 / 5.0) + 0.1 / (10.0 / (1.0 + 4.0 * 0.99))
        self.assertAlmostEqual(obj.grown_percent, expected, places=6)

    def test_growth_random_consumption_does_not_shift_water_decay_domain(self) -> None:
        left = Simulation(seed=7)
        right = Simulation(seed=7)
        left.farm = FarmState(build_global_bindings())
        right.farm = FarmState(build_global_bindings())

        _ = left.farm.sample_growth_seconds(left.farm.entity("Carrot"))
        _ = left.farm.sample_growth_seconds(left.farm.entity("Pumpkin"))
        _ = left.farm.sample_growth_seconds(left.farm.entity("Sunflower"))

        self.assertEqual(left.random_water_decay.random(), right.random_water_decay.random())

    def test_growth_random_matches_original_various_domain(self) -> None:
        bindings = build_global_bindings()
        farm = FarmState(bindings)
        sim = Simulation(seed=7)
        sim.farm = farm
        entity = farm.entity("Carrot")
        lower, upper = farm.entity_growth_ranges[entity]

        expected_rng = DotNetRandom(0)
        expected_rng.setstate(sim.random_various.getstate())
        expected_value = lower + (upper - lower) * expected_rng.random()

        value = farm.sample_growth_seconds(entity)

        self.assertAlmostEqual(value, expected_value)
        self.assertEqual(sim.random_various.getstate(), expected_rng.getstate())

    def test_growable_core(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(
            bindings,
            unlock_levels={unlocks_bag.evaluate("Expand"): 9},
            items={
                items_bag.evaluate("Hay"): 32,
                items_bag.evaluate("Wood"): 32,
                items_bag.evaluate("Fertilizer"): 1,
            },
        )
        sim = Simulation(seed=7)
        sim.farm = farm
        farm.random = sim.random_various
        drone = farm.drones[0]
        drone.till()
        self.assertTrue(drone.plant(entities_bag.evaluate("Carrot")))

        obj = farm.get_entity_object((0, 0))
        self.assertEqual(obj.entity_name, "Carrot")
        companion_entity, companion_pos = obj.get_companion()
        self.assertNotEqual(companion_pos, (0, 0))
        width, height = farm.grid.world_size
        dx = min(abs(companion_pos[0]), width - abs(companion_pos[0]))
        dy = min(abs(companion_pos[1]), height - abs(companion_pos[1]))
        self.assertLessEqual(dx + dy, 3)
        self.assertFalse(obj.is_weird)
        obj.toggle_weird()
        self.assertTrue(obj.is_weird)

        drone.fertilize(1)
        self.assertGreater(obj.grown_percent, 0.0)

    def test_pumpkin_controller(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        pumpkin = entities_bag.evaluate("Pumpkin")
        weird_item = items_bag.evaluate("Weird_Substance")
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=11)
        sim.farm = farm
        farm.random = sim.random_various

        for pos in ((0, 0), (1, 0), (0, 1), (1, 1)):
            cell = farm.grid.get_cell(pos)
            cell.entity = pumpkin
            cell.mature = True
        farm.grid.get_cell((1, 1)).weird = True

        drone = farm.drones[0]
        drone.x = 0
        drone.y = 0
        measured0 = drone.measure()
        drone.x = 1
        drone.y = 1
        measured1 = drone.measure()

        self.assertIsInstance(measured0, (int, float))
        self.assertEqual(measured0, measured1)

        drone.x = 0
        drone.y = 0
        self.assertTrue(drone.harvest())
        self.assertEqual(farm.num_items(items_bag.evaluate("Pumpkin")), 7.0)
        self.assertEqual(farm.num_items(weird_item), 1.0)

    def test_sunflower_bonus(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        farm = FarmState(
            bindings,
            unlock_levels={
                unlocks_bag.evaluate("Expand"): 9,
                unlocks_bag.evaluate("Sunflowers"): 1,
            },
        )
        sim = Simulation(seed=13)
        sim.farm = farm
        farm.random = sim.random_various
        sunflower = entities_bag.evaluate("Sunflower")
        for x in range(5):
            for y in range(2):
                cell = farm.grid.get_cell((x, y))
                cell.entity = sunflower
                cell.mature = True
                cell.petals = 10
        farm.grid.get_cell((0, 0)).petals = 15

        drone = farm.drones[0]
        drone.x = 1
        drone.y = 0
        self.assertTrue(drone.harvest())
        drone.x = 0
        drone.y = 0
        self.assertTrue(drone.harvest())
        self.assertEqual(farm.num_items(items_bag.evaluate("Power")), 25.0)

    def test_cactus_sort_and_harvest(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        cactus = entities_bag.evaluate("Cactus")
        weird_item = items_bag.evaluate("Weird_Substance")
        farm = FarmState(bindings, unlock_levels={unlocks_bag.evaluate("Expand"): 9})
        sim = Simulation(seed=17)
        sim.farm = farm
        farm.random = sim.random_various

        left = farm.grid.get_cell((0, 0))
        left.entity = cactus
        left.mature = True
        left.variant = 3
        left.weird = True
        right = farm.grid.get_cell((1, 0))
        right.entity = cactus
        right.mature = True
        right.variant = 3

        drone = farm.drones[0]
        drone.x = 0
        drone.y = 0
        self.assertTrue(drone.harvest())
        self.assertEqual(farm.num_items(items_bag.evaluate("Cactus")), 3.0)
        self.assertEqual(farm.num_items(weird_item), 1.0)

    def test_dinosaur_and_maze_surface(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]
        entities_bag = bindings["Entities"]
        unlocks_bag = bindings["Unlocks"]
        hats_bag = bindings["Hats"]

        maze_farm = FarmState(
            bindings,
            unlock_levels={
                unlocks_bag.evaluate("Expand"): 9,
                unlocks_bag.evaluate("Mazes"): 1,
            },
            items={items_bag.evaluate("Weird_Substance"): 3},
        )
        maze_sim = Simulation(seed=19)
        maze_sim.farm = maze_farm
        maze_farm.random = maze_sim.random_various
        bush_cell = maze_farm.grid.get_cell((0, 0))
        bush_cell.entity = entities_bag.evaluate("Bush")
        bush_cell.mature = True

        maze_code = "\n" + "ok = use_item(Items.Weird_Substance, 3)\n" + "probe = measure()\n"
        has_unknown, stream = tokenize(maze_code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(maze_sim, program.syntax_tree, 31, global_bindings=bindings)
        run_execution_to_termination(execution)
        maze_state = execution.states[0]
        self.assertTrue(bool(maze_state.current_scope.evaluate("ok").val))
        self.assertIsInstance(maze_state.current_scope.evaluate("probe").val, PyTuple)

        dino_farm = FarmState(
            bindings,
            unlock_levels={
                unlocks_bag.evaluate("Expand"): 9,
                unlocks_bag.evaluate("Dinosaurs"): 1,
            },
            items={items_bag.evaluate("Cactus"): 128},
        )
        dino_sim = Simulation(seed=23)
        dino_sim.farm = dino_farm
        dino_farm.random = dino_sim.random_various

        dino_code = (
            "\n"
            + "change_hat(Hats.Dinosaur_Hat)\n"
            + "entity0 = get_entity_type()\n"
            + "target = measure()\n"
            + "blocked = can_move(West)\n"
        )
        has_unknown, stream = tokenize(dino_code)
        self.assertFalse(has_unknown)
        program = parse(stream)
        execution = Execution(dino_sim, program.syntax_tree, 32, global_bindings=bindings)
        run_execution_to_termination(execution)
        dino_state = execution.states[0]
        self.assertEqual(dino_state.current_scope.evaluate("entity0").val, entities_bag.evaluate("Apple"))
        self.assertIsInstance(dino_state.current_scope.evaluate("target").val, PyTuple)
        self.assertFalse(bool(dino_state.current_scope.evaluate("blocked").val))


class RunnerTests(unittest.TestCase):
    def test_resolve_leaderboard_worker_count_uses_cpu_count_and_env_override(self) -> None:
        import gamesimulator.runtime.execution as execution_module

        with mock.patch.dict("os.environ", {}, clear=False), mock.patch("gamesimulator.runtime.execution.os.cpu_count", return_value=20):
            self.assertEqual(execution_module.resolve_leaderboard_worker_count(), 20)

        with mock.patch.dict("os.environ", {"TFWR_MAX_LEADERBOARD_WORKERS": "12"}, clear=False), mock.patch(
            "gamesimulator.runtime.execution.os.cpu_count", return_value=20
        ):
            self.assertEqual(execution_module.resolve_leaderboard_worker_count(), 12)

    def test_should_schedule_more_prefetch_stops_when_buffered_average_is_enough(self) -> None:
        import gamesimulator.runtime.execution as execution_module

        self.assertTrue(
            execution_module.should_schedule_more_prefetch(
                total_seconds=0.0,
                run_count=0,
                pending_count=8,
                min_total_seconds=7200.0,
            )
        )
        self.assertTrue(
            execution_module.should_schedule_more_prefetch(
                total_seconds=6000.0,
                run_count=10,
                pending_count=1,
                min_total_seconds=7200.0,
            )
        )
        self.assertFalse(
            execution_module.should_schedule_more_prefetch(
                total_seconds=7000.0,
                run_count=10,
                pending_count=1,
                min_total_seconds=7200.0,
            )
        )

    def test_shutdown_process_pool_fast_terminates_alive_workers(self) -> None:
        import gamesimulator.runtime.execution as execution_module

        calls: list[str] = []

        class FakeProcess:
            def __init__(self) -> None:
                self.alive = True

            def is_alive(self) -> bool:
                return self.alive

            def terminate(self) -> None:
                calls.append("terminate")

            def join(self, timeout: float | None = None) -> None:
                calls.append(f"join:{timeout}")

            def kill(self) -> None:
                calls.append("kill")
                self.alive = False

        class FakeExecutor:
            def __init__(self) -> None:
                self._processes = {1: FakeProcess()}

            def shutdown(self, wait: bool = True, *, cancel_futures: bool = False) -> None:
                calls.append(f"shutdown:{wait}:{cancel_futures}")

        execution_module.shutdown_process_pool_fast(FakeExecutor())

        self.assertIn("shutdown:False:True", calls)
        self.assertIn("terminate", calls)
        self.assertTrue(any(call.startswith("join:") for call in calls))
        self.assertIn("kill", calls)

    def test_leaderboard_metadata_uses_asset_snapshot_for_start_items_and_steam_name(self) -> None:
        save_root = require_save_root()
        hay_single = resolve_leaderboard_metadata("lb_hay_single", save_root)
        sunflowers_single = resolve_leaderboard_metadata("lb_sunflowers_single", save_root)
        fastest_reset = resolve_leaderboard_metadata("lb_fastest_reset", save_root)

        self.assertEqual(hay_single.steam_leaderboard_name, "hay_single")
        self.assertEqual(hay_single.start_items, (("Power", 1_000_000_000.0),))

        self.assertEqual(sunflowers_single.steam_leaderboard_name, "sunflowers_single")
        self.assertEqual(sunflowers_single.start_items, (("Carrot", 1_000_000_000.0),))

        self.assertEqual(fastest_reset.steam_leaderboard_name, "fastest_reset_multi")
        self.assertEqual(fastest_reset.start_items, ())
        self.assertFalse(fastest_reset.everything_unlocked)

    def test_leaderboard_goal_status_uses_game_single_goals(self) -> None:
        bindings = build_global_bindings()
        items_bag = bindings["Items"]

        hay_farm = FarmState(bindings, items={items_bag.evaluate("Hay"): 100_000_000})
        carrots_farm = FarmState(bindings, items={items_bag.evaluate("Carrot"): 100_000_000})
        pumpkins_farm = FarmState(bindings, items={items_bag.evaluate("Pumpkin"): 10_000_000})

        self.assertEqual(
            leaderboard_goal_status("lb_hay_single", hay_farm),
            (True, "Hay=100000000/100000000"),
        )
        self.assertEqual(
            leaderboard_goal_status("lb_carrots_single", carrots_farm),
            (True, "Carrot=100000000/100000000"),
        )
        self.assertEqual(
            leaderboard_goal_status("lb_pumpkins_single", pumpkins_farm),
            (True, "Pumpkin=10000000/10000000"),
        )

    def test_run_file_uses_single_leaderboard_drone_and_unlock_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_pumpkins_single.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('expand_before', num_unlocked(Unlocks.Expand))\n"
                "quick_print('mega_before', num_unlocked(Unlocks.Megafarm))\n"
                "quick_print('expand_unlock', unlock(Unlocks.Expand), num_unlocked(Unlocks.Expand), get_world_size())\n"
                "quick_print('mega_unlock', unlock(Unlocks.Megafarm), num_unlocked(Unlocks.Megafarm))\n",
                encoding="utf-8",
            )
            result = run_file("lb_pumpkins_single", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs[0], "expand_before 5.0")
            self.assertEqual(result.logs[1], "mega_before 0.0")
            self.assertEqual(result.logs[2], "expand_unlock False 5.0 8.0")
            self.assertEqual(result.logs[3], "mega_unlock False 0.0")

    def test_single_leaderboard_rejects_spawn_drone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_pumpkins_single.py").write_text(
                "from __builtins__ import *\n"
                "def child():\n"
                "    return 7\n"
                "spawn_drone(child)\n",
                encoding="utf-8",
            )
            with self.assertRaises(ExecuteException):
                run_file("lb_pumpkins_single", tmp_path, seed=1)

    def test_run_file_with_context_propagates_single_leaderboard_metadata_to_probe_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "probe.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('probe', num_unlocked(Unlocks.Expand), num_unlocked(Unlocks.Megafarm))\n",
                encoding="utf-8",
            )
            result = run_file_with_context(
                "probe",
                tmp_path,
                seed=1,
                run_kind="leaderboard",
                leaderboard_key="Pumpkins_Single",
            )
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["probe 5.0 0.0"])

    def test_simulate_does_not_recurse_inside_simulation_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "child.py").write_text(
                "from __builtins__ import *\nquick_print('child-ran')\n",
                encoding="utf-8",
            )
            (tmp_path / "simulate.py").write_text(
                "from __builtins__ import *\n"
                "run_time = simulate('child', Unlocks, {}, {}, 1, 10000)\n"
                "quick_print('simulate_done', run_time)\n",
                encoding="utf-8",
            )
            result = run_file_with_context("simulate", tmp_path, seed=1, run_kind="simulation")
            self.assertTrue(result.terminated)
            self.assertFalse(any(line == "child-ran" for line in result.logs))
            self.assertTrue(any(line.startswith("simulate_done") for line in result.logs))

    def test_leaderboard_run_does_not_recurse_inside_leaderboard_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_probe.py").write_text(
                "from __builtins__ import *\nquick_print('nested-lb-ran')\n",
                encoding="utf-8",
            )
            (tmp_path / "lb_start.py").write_text(
                "from __builtins__ import *\n"
                "leaderboard_run(Leaderboards.Hay_Single, 'lb_probe', 10000)\n",
                encoding="utf-8",
            )
            result = run_file_with_context(
                "lb_start",
                tmp_path,
                seed=1,
                run_kind="leaderboard",
                leaderboard_key="Hay_Single",
            )
            self.assertTrue(result.terminated)
            self.assertFalse(any("leaderboard_run lb_probe.py start" in line for line in result.logs))
            self.assertFalse(any(line == "nested-lb-ran" for line in result.logs))

    def test_leaderboard_context_allows_start_unlock_builtins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_probe.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('before')\n"
                "do_a_flip()\n"
                "harvest()\n"
                "quick_print('after')\n",
                encoding="utf-8",
            )
            result = run_file_with_context(
                "lb_probe",
                tmp_path,
                seed=1,
                run_kind="leaderboard",
                leaderboard_key="Hay_Single",
            )
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["before", "after"])

    def test_simulation_context_allows_start_unlock_builtins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "simulate.py").write_text(
                "from __builtins__ import *\n"
                "do_a_flip()\n"
                "harvest()\n",
                encoding="utf-8",
            )
            result = run_file_with_context(
                "simulate",
                tmp_path,
                seed=1,
                run_kind="simulation",
                unlock_levels={},
                items={},
            )
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, [])

    def test_simulation_context_allows_ui_only_builtins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            bindings = build_global_bindings()
            timing_unlock = bindings["Unlocks"].evaluate("Timing")
            debug_unlock = bindings["Unlocks"].evaluate("Debug")
            expected_pet_ticks = int(1.0 / Simulation(seed=1).op_duration.seconds)
            expected_tap_ticks = int(0.1 / Simulation(seed=1).op_duration.seconds)
            (tmp_path / "simulate.py").write_text(
                "from __builtins__ import *\n"
                "pet_the_piggy()\n"
                "quick_print('pet', get_tick_count())\n"
                "tap()\n"
                "quick_print('tap', get_tick_count())\n",
                encoding="utf-8",
            )
            result = run_file_with_context(
                "simulate",
                tmp_path,
                seed=1,
                run_kind="simulation",
                unlock_levels={timing_unlock: 1, debug_unlock: 1},
                items={},
            )
            self.assertTrue(result.terminated)
            self.assertEqual(
                result.logs,
                [f"pet {expected_pet_ticks}", f"tap {expected_pet_ticks + expected_tap_ticks}"],
            )

    def test_simulate_context_receives_water_from_watering_timer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "test.py").write_text(
                "from __builtins__ import *\n"
                "clear()\n"
                "set_world_size(3)\n"
                "move(East)\n"
                "move(North)\n"
                "harvest()\n"
                "plant(Entities.Tree)\n"
                "quick_print('use_water', use_item(Items.Water, 4))\n"
                "quick_print('water_after', get_water())\n",
                encoding="utf-8",
            )
            (tmp_path / "simulate.py").write_text(
                "from __builtins__ import *\n"
                "simulate('test', Unlocks, {}, {}, 1, 10000)\n",
                encoding="utf-8",
            )

            result = run_file("simulate", tmp_path, seed=1)

            self.assertTrue(result.terminated)
            self.assertIn("use_water True", result.logs)
            self.assertIn("water_after 1.0", result.logs)

    def test_runner_executes_dict_copy_constructor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "main.py").write_text(
                "from __builtins__ import *\n"
                "source = {Items.Hay: 1}\n"
                "copy = dict(source)\n"
                "quick_print('dict', len(copy), copy[Items.Hay])\n",
                encoding="utf-8",
            )
            result = run_file("main", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["dict 1.0 1.0"])

    def test_runner_script_path_executes_from_repo_root(self) -> None:
        require_save_root()
        game_root = REPO_ROOT
        runner_path = (game_root / "runner.py").resolve()

        completed = subprocess.run(
            [sys.executable, str(runner_path), "simulate.py"],
            cwd=game_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("simulate_probe", completed.stdout)

    def test_runner_executes_minimal_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "mini.py").write_text(
                "from __builtins__ import *\n\n"
                "x = get_tick_count()\n"
                "quick_print('mini', x)\n",
                encoding="utf-8",
            )
            result = run_file("mini", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.target, "mini.py")
            self.assertEqual(result.logs, ["mini 0"])

    def test_runner_executes_simulate_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "test.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('child', get_time(), get_tick_count())\n",
                encoding="utf-8",
            )
            (tmp_path / "simulate.py").write_text(
                "from __builtins__ import *\n"
                "run_time = simulate('test', Unlocks, {}, {}, 1, 10000)\n"
                "quick_print('simulate_done', run_time)\n",
                encoding="utf-8",
            )
            result = run_file("simulate", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.target, "simulate.py")
            self.assertTrue(any(line.startswith("child") for line in result.logs))
            self.assertTrue(any(line.startswith("simulate_done") for line in result.logs))

    def test_runner_executes_import_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "helper.py").write_text(
                "from __builtins__ import *\n"
                "x = 3\n"
                "def inc():\n"
                "    return x + 1\n",
                encoding="utf-8",
            )
            (tmp_path / "main.py").write_text(
                "from __builtins__ import *\n"
                "import helper\n"
                "quick_print('mod', helper.x)\n"
                "from helper import inc\n"
                "quick_print('fn', inc())\n",
                encoding="utf-8",
            )
            result = run_file("main", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["mod 3.0", "fn 4.0"])

    def test_runner_executes_from_import_star_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "helper.py").write_text(
                "from __builtins__ import *\n"
                "x = 3\n"
                "y = 5\n",
                encoding="utf-8",
            )
            (tmp_path / "main.py").write_text(
                "from __builtins__ import *\n"
                "from helper import *\n"
                "quick_print('vals', x, y)\n",
                encoding="utf-8",
            )
            result = run_file("main", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["vals 3.0 5.0"])

    def test_import_requires_unlock_in_simulation_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "helper.py").write_text(
                "from __builtins__ import *\n"
                "x = 3\n",
                encoding="utf-8",
            )
            (tmp_path / "main.py").write_text(
                "from __builtins__ import *\n"
                "import helper\n"
                "quick_print(helper.x)\n",
                encoding="utf-8",
            )
            with self.assertRaises(ExecuteException):
                run_file_with_context(
                    "main",
                    tmp_path,
                    seed=1,
                    run_kind="simulation",
                    unlock_levels={},
                    items={},
                )

    def test_run_file_forwards_logs_to_sink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "mini.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('one')\n"
                "quick_print('two')\n",
                encoding="utf-8",
            )
            streamed: list[str] = []
            result = run_file("mini", tmp_path, seed=1, log_sink=streamed.append)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs, ["one", "two"])
            self.assertEqual(streamed, ["one", "two"])

    def test_runner_executes_leaderboard_run_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_probe.py").write_text(
                "from __builtins__ import *\n"
                "print('tick')\n",
                encoding="utf-8",
            )
            (tmp_path / "lb_start.py").write_text(
                "from __builtins__ import *\n"
                "leaderboard_run(Leaderboards.Hay_Single, 'lb_probe', 10000)\n",
                encoding="utf-8",
            )
            with mock.patch("gamesimulator.runtime.execution.MIN_LEADERBOARD_TOTAL_SECONDS", 2.0, create=True), mock.patch(
                "gamesimulator.runtime.execution.MAX_LEADERBOARD_WORKERS", 2, create=True
            ):
                result = run_file("lb_start", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertFalse(any(line == "tick" for line in result.logs))
            self.assertEqual(result.logs[0], "leaderboard_run lb_probe.py start")
            self.assertTrue(any("leaderboard_run run=1" in line for line in result.logs))
            self.assertFalse(any("leaderboard_run run=2" in line for line in result.logs))
            average_lines = [line for line in result.logs if "leaderboard_run lb_probe.py fail average=" in line]
            self.assertTrue(average_lines)
            self.assertTrue(any("min=" in line and "max=" in line for line in average_lines))
            self.assertFalse(any("average_seconds=" in line for line in average_lines))
            self.assertFalse(any("min_seconds=" in line for line in average_lines))
            self.assertFalse(any("max_seconds=" in line for line in average_lines))
            self.assertFalse(any("finished=" in line for line in average_lines))
            self.assertFalse(any("runs=" in line for line in average_lines))
            self.assertFalse(any("total=" in line for line in average_lines))

    def test_runner_executes_failed_leaderboard_run_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_probe.py").write_text(
                "from __builtins__ import *\n",
                encoding="utf-8",
            )
            (tmp_path / "lb_start.py").write_text(
                "from __builtins__ import *\n"
                "leaderboard_run(Leaderboards.Hay_Single, 'lb_probe', 10000)\n",
                encoding="utf-8",
            )
            with mock.patch("gamesimulator.runtime.execution.MIN_LEADERBOARD_TOTAL_SECONDS", 2.0, create=True), mock.patch(
                "gamesimulator.runtime.execution.MAX_LEADERBOARD_WORKERS", 2, create=True
            ):
                result = run_file("lb_start", tmp_path, seed=1)
            self.assertTrue(result.terminated)
            self.assertEqual(result.logs[0], "leaderboard_run lb_probe.py start")
            average_lines = [line for line in result.logs if "leaderboard_run lb_probe.py fail average=" in line]
            self.assertTrue(average_lines)
            self.assertTrue(any("min=" in line and "max=" in line for line in average_lines))
            self.assertFalse(any("finished=" in line for line in average_lines))
            self.assertFalse(any("runs=" in line for line in average_lines))
            self.assertFalse(any("total=" in line for line in average_lines))

    def test_runner_executes_leaderboard_run_with_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "lb_start.py").write_text(
                "from __builtins__ import *\n"
                "leaderboard_run(Leaderboards.Hay_Single, 'lb_probe', 10000)\n",
                encoding="utf-8",
            )

            def fake_iteration(target: str, save_root: str | Path | None, seed: int, leaderboard_key: str | None = None):
                time.sleep(0.03)
                return LeaderboardIterationResult(
                    seed=seed,
                    elapsed_seconds=2.5,
                    terminated=True,
                    goal_reached=True,
                    progress_text="Hay=100000000/100000000",
                )

            with mock.patch("gamesimulator.runtime.execution.MIN_LEADERBOARD_TOTAL_SECONDS", 2.0, create=True), mock.patch(
                "gamesimulator.runtime.execution.MAX_LEADERBOARD_WORKERS", 1, create=True
            ), mock.patch(
                "gamesimulator.runtime.execution.LEADERBOARD_HEARTBEAT_INTERVAL_SECONDS", 0.005, create=True
            ), mock.patch(
                "gamesimulator.runtime.execution.LEADERBOARD_WAIT_TIMEOUT_SECONDS", 0.001, create=True
            ), mock.patch(
                "gamesimulator.runtime.execution.ProcessPoolExecutor", ThreadPoolExecutor
            ), mock.patch(
                "gamesimulator.runner.run_leaderboard_iteration", side_effect=fake_iteration
            ):
                result = run_file("lb_start", tmp_path, seed=1)

            self.assertTrue(result.terminated)
            self.assertTrue(any(line.startswith("leaderboard_run heartbeat") for line in result.logs))
            self.assertTrue(any("leaderboard_run run=1" in line for line in result.logs))
            self.assertTrue(any("leaderboard_run lb_probe.py pass average=" in line for line in result.logs))

    def test_repeated_run_file_reuses_cached_program_and_bindings(self) -> None:
        import gamesimulator.runner as runner_module

        runner_module._PROGRAM_CACHE.clear()
        runner_module._GLOBAL_BINDINGS_CACHE.clear()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "mini.py").write_text(
                "from __builtins__ import *\n"
                "quick_print('cached')\n",
                encoding="utf-8",
            )
            with mock.patch("gamesimulator.runner.build_global_bindings", wraps=runner_module.build_global_bindings) as build_mock, mock.patch(
                "gamesimulator.runner.tokenize", wraps=runner_module.tokenize
            ) as tokenize_mock, mock.patch(
                "gamesimulator.runner.parse", wraps=runner_module.parse
            ) as parse_mock:
                result1 = run_file("mini", tmp_path, seed=1)
                result2 = run_file("mini", tmp_path, seed=1)

            self.assertTrue(result1.terminated)
            self.assertTrue(result2.terminated)
            self.assertEqual(result1.logs, ["cached"])
            self.assertEqual(result2.logs, ["cached"])
            self.assertEqual(build_mock.call_count, 1)
            self.assertEqual(tokenize_mock.call_count, 1)
            self.assertEqual(parse_mock.call_count, 1)

    def test_runner_cli_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "mini.py").write_text(
                "from __builtins__ import *\nquick_print('ok')\n",
                encoding="utf-8",
            )
            exit_code = runner_main(["mini", "1", str(tmp_path)])
            self.assertEqual(exit_code, 0)

    def test_runner_cli_accepts_speedup_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_test_builtins(tmp_path)
            (tmp_path / "mini.py").write_text(
                "from __builtins__ import *\nquick_print('ok-speedup')\n",
                encoding="utf-8",
            )
            exit_code = runner_main(["mini", "1", "10000", str(tmp_path)])
            self.assertEqual(exit_code, 0)

    def test_run_file_uses_max_speed_factor_for_lb_defaults(self) -> None:
        bindings = build_global_bindings()
        has_unknown, stream = tokenize("\nmove(North)\n")
        self.assertFalse(has_unknown)
        program = parse(stream)
        sim = Simulation(seed=1)
        sim.farm = FarmState(
            bindings,
            unlock_levels=_default_unlock_levels(bindings),
            items=_default_items("lb_wood_single", bindings, require_save_root()),
        )
        execution = Execution(sim, program.syntax_tree, 91, global_bindings=bindings)
        run_execution_to_termination(execution)
        self.assertLess(sim.current_time.seconds, 0.1)


if __name__ == "__main__":
    unittest.main()
