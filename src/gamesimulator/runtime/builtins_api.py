from __future__ import annotations

from typing import Any

from .py_function import PyFunction
from .execute_exception import ExecuteException
from .py_values import PyBool, PyDict, PyList, PyNone, PyNumber, PyRange, PySet, PyString, PyTickNumber, PyTuple
from ..common.side_effects import SideEffect


def _stringify(value: Any) -> str:
    if isinstance(value, PyString):
        return value.text
    if isinstance(value, PyBool):
        return "True" if bool(value) else "False"
    if isinstance(value, PyNumber):
        if getattr(value, "display_as_int", False):
            return str(int(round(float(value.num))))
        return str(float(value.num))
    return repr(value)


def get_time(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_time takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_TIME
    return 0.0


def get_pos_x(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_pos_x takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_POS_X
    return 0.0


def get_pos_y(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_pos_y takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_POS_Y
    return 0.0


def get_world_size(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_world_size takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_WORLD_SIZE
    return 0.0


def move(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("move expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.MOVE
    state.current_side_effect_argument = parameters[0]
    return 0.0


def swap_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("swap expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.SWAP
    state.current_side_effect_argument = parameters[0]
    return 0.0


def can_move(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("can_move expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.CAN_MOVE
    state.current_side_effect_argument = parameters[0]
    return 0.0


def till(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("till takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.TILL
    return 0.0


def can_harvest(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("can_harvest takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.CAN_HARVEST
    return 0.0


def harvest(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("harvest takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.HARVEST
    return 0.0


def plant(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("plant expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.PLANT
    state.current_side_effect_argument = parameters[0]
    return 0.0


def get_ground_type(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_ground_type takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_GROUND_TYPE
    return 0.0


def get_entity_type(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_entity_type takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_ENTITY_TYPE
    return 0.0


def get_water(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_water takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_WATER
    return 0.0


def get_companion(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_companion takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.GET_COMPANION
    return 0.0


def measure_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) > 1:
        raise ValueError("measure expects 0 or 1 parameters")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.MEASURE
    state.current_side_effect_argument = parameters[0] if parameters else PyNone()
    return 0.0


def set_execution_speed(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("set_execution_speed expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.SET_EXECUTION_SPEED
    state.current_side_effect_argument = parameters[0]
    return 0.0


def change_hat(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("change_hat expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.CHANGE_HAT
    state.current_side_effect_argument = parameters[0]
    return 0.0


def clear_builtin(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("clear takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.CLEAR
    return 0.0


def unlock_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("unlock expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.UNLOCK
    state.current_side_effect_argument = parameters[0]
    return 0.0


def do_a_flip_builtin(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("do_a_flip takes no parameters")
    execution.states[drone_id].current_side_effect = SideEffect.DO_A_FLIP
    return 0.0


def use_item(parameters, sim, execution, drone_id) -> float:
    if len(parameters) not in (1, 2):
        raise ValueError("use_item expects 1 or 2 parameters")
    amount = 1 if len(parameters) == 1 else int(float(parameters[1].num))
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.USE_ITEM
    state.current_side_effect_argument = parameters[0]
    state.current_side_effect_argument2 = PyNumber(amount)
    return 0.0


def set_world_size(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("set_world_size expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.SET_WORLD_SIZE
    state.current_side_effect_argument = parameters[0]
    return 0.0


def simulate_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 6:
        raise ValueError("simulate expects 6 parameters")
    if execution.states[drone_id] is not execution.main_state:
        raise ExecuteException("simulate can only be called from the main execution")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.SIMULATE
    state.current_side_effect_argument = PyList(list(parameters))
    return 0.0


def num_items(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("num_items expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.NUM_ITEMS
    state.current_side_effect_argument = parameters[0]
    return 0.0


def num_unlocked(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("num_unlocked expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.NUM_UNLOCKED
    state.current_side_effect_argument = parameters[0]
    return 0.0


def num_drones_builtin(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("num_drones takes no parameters")
    state = execution.states[drone_id]
    state.return_value = PyNumber(len([drone for drone in sim.farm.drones if drone is not None]))
    return 1.0


def max_drones_builtin(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("max_drones takes no parameters")
    state = execution.states[drone_id]
    state.return_value = PyNumber(sim.farm.max_drones())
    return 1.0


def spawn_drone_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) < 1:
        raise ValueError("spawn_drone expects at least 1 parameter")
    if not isinstance(parameters[0], PyFunction):
        raise ValueError("spawn_drone first parameter must be function")
    state = execution.states[drone_id]
    if parameters[0].syntax_tree is None:
        raise ValueError("error_spawn_drone_builtin")
    state.current_side_effect = SideEffect.SPAWN_DRONE
    state.current_side_effect_argument = PyList(list(parameters))
    return 0.0


def wait_for_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("wait_for expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.AWAIT
    state.current_side_effect_argument = parameters[0]
    return 0.0


def has_finished_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("has_finished expects 1 parameter")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.HAS_FINISHED
    state.current_side_effect_argument = parameters[0]
    return 0.0


def len_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("len expects 1 parameter")
    target = parameters[0]
    if hasattr(target, "__len__"):
        execution.states[drone_id].return_value = PyNumber(len(target))
        return 1.0
    raise ValueError("len on unsupported type")


def abs_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("abs expects 1 parameter")
    execution.states[drone_id].return_value = PyNumber(abs(float(parameters[0].num)))
    return 1.0


def min_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 2:
        raise ValueError("min expects 2 parameters")
    left = parameters[0]
    right = parameters[1]
    execution.states[drone_id].return_value = left if float(left.num) <= float(right.num) else right
    return 1.0


def max_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 2:
        raise ValueError("max expects 2 parameters")
    left = parameters[0]
    right = parameters[1]
    execution.states[drone_id].return_value = left if float(left.num) >= float(right.num) else right
    return 1.0


def str_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 1:
        raise ValueError("str expects 1 parameter")
    execution.states[drone_id].return_value = PyString(_stringify(parameters[0]))
    return 1.0


def random_builtin(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("random expects no parameters")
    execution.states[drone_id].return_value = PyNumber(sim.random_random.random())
    return 1.0


def list_constructor(parameters, sim, execution, drone_id) -> float:
    if len(parameters) == 0:
        execution.states[drone_id].return_value = PyList([])
        return 1.0
    if len(parameters) == 1:
        execution.states[drone_id].return_value = PyList(list(parameters[0]))
        return 1.0
    raise ValueError("list expects 0 or 1 parameters")


def set_constructor(parameters, sim, execution, drone_id) -> float:
    if len(parameters) == 0:
        execution.states[drone_id].return_value = PySet(set())
        return 1.0
    if len(parameters) == 1:
        execution.states[drone_id].return_value = PySet(set(parameters[0]))
        return 1.0
    raise ValueError("set expects 0 or 1 parameters")


def dict_constructor(parameters, sim, execution, drone_id) -> float:
    if len(parameters) == 0:
        execution.states[drone_id].return_value = PyDict({})
        return 1.0
    raise ValueError("dict constructor with input not implemented yet")


def get_cost_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) not in (1, 2):
        raise ValueError("get_cost expects 1 or 2 parameters")
    thing = parameters[0]
    if thing in sim.farm.entity_cost:
        mapping = {
            key: __import__("gamesimulator.runtime.py_values", fromlist=["PyObjectBox"]).PyObjectBox(PyNumber(value))
            for key, value in sim.farm.get_entity_cost(thing).items()
        }
        execution.states[drone_id].return_value = PyDict(mapping)
        return 1.0
    execution.states[drone_id].return_value = PyNone()
    return 1.0


def get_tick_count(parameters, sim, execution, drone_id) -> float:
    if parameters:
        raise ValueError("get_tick_count takes no parameters")
    state = execution.states[drone_id]
    state.return_value = PyTickNumber(state.op_count - state.start_op_count)
    return 0.0


def quick_print(parameters, sim, execution, drone_id) -> float:
    if not parameters:
        raise ValueError("error_empty_print")
    execution.log(stringify_parts(parameters))
    execution.states[drone_id].return_value = PyNone()
    return 0.0


def print_builtin(parameters, sim, execution, drone_id) -> float:
    if not parameters:
        raise ValueError("error_empty_print")
    state = execution.states[drone_id]
    state.current_side_effect = SideEffect.PRINT
    state.current_side_effect_argument = PyString(stringify_parts(parameters))
    return 0.0


def stringify_parts(parameters) -> str:
    return " ".join(_stringify(param) for param in parameters)


def default_functions() -> dict[str, PyFunction]:
    return {
        "move": PyFunction("move", binding=move),
        "swap": PyFunction("swap", binding=swap_builtin),
        "can_move": PyFunction("can_move", binding=can_move),
        "harvest": PyFunction("harvest", binding=harvest),
        "can_harvest": PyFunction("can_harvest", binding=can_harvest),
        "plant": PyFunction("plant", binding=plant),
        "till": PyFunction("till", binding=till),
        "get_pos_x": PyFunction("get_pos_x", binding=get_pos_x),
        "get_pos_y": PyFunction("get_pos_y", binding=get_pos_y),
        "get_world_size": PyFunction("get_world_size", binding=get_world_size),
        "get_entity_type": PyFunction("get_entity_type", binding=get_entity_type),
        "get_ground_type": PyFunction("get_ground_type", binding=get_ground_type),
        "measure": PyFunction("measure", binding=measure_builtin),
        "get_time": PyFunction("get_time", binding=get_time, is_free=True),
        "get_tick_count": PyFunction("get_tick_count", binding=get_tick_count, is_free=True),
        "use_item": PyFunction("use_item", binding=use_item),
        "get_water": PyFunction("get_water", binding=get_water),
        "get_companion": PyFunction("get_companion", binding=get_companion),
        "change_hat": PyFunction("change_hat", binding=change_hat),
        "do_a_flip": PyFunction("do_a_flip", binding=do_a_flip_builtin),
        "clear": PyFunction("clear", binding=clear_builtin),
        "unlock": PyFunction("unlock", binding=unlock_builtin),
        "set_execution_speed": PyFunction("set_execution_speed", binding=set_execution_speed),
        "set_world_size": PyFunction("set_world_size", binding=set_world_size),
        "simulate": PyFunction("simulate", binding=simulate_builtin),
        "quick_print": PyFunction("quick_print", binding=quick_print, is_free=True),
        "print": PyFunction("print", binding=print_builtin),
        "len": PyFunction("len", binding=len_builtin),
        "num_items": PyFunction("num_items", binding=num_items),
        "get_cost": PyFunction("get_cost", binding=get_cost_builtin),
        "num_unlocked": PyFunction("num_unlocked", binding=num_unlocked),
        "min": PyFunction("min", binding=min_builtin),
        "max": PyFunction("max", binding=max_builtin),
        "abs": PyFunction("abs", binding=abs_builtin),
        "str": PyFunction("str", binding=str_builtin),
        "random": PyFunction("random", binding=random_builtin),
        "list": PyFunction("list", binding=list_constructor),
        "set": PyFunction("set", binding=set_constructor),
        "dict": PyFunction("dict", binding=dict_constructor),
        "spawn_drone": PyFunction("spawn_drone", binding=spawn_drone_builtin),
        "num_drones": PyFunction("num_drones", binding=num_drones_builtin),
        "max_drones": PyFunction("max_drones", binding=max_drones_builtin),
        "wait_for": PyFunction("wait_for", binding=wait_for_builtin),
        "has_finished": PyFunction("has_finished", binding=has_finished_builtin),
        "append": PyFunction("append", binding=append_builtin),
        "add": PyFunction("add", binding=add_builtin),
        "remove": PyFunction("remove", binding=remove_builtin),
        "pop": PyFunction("pop", binding=pop_builtin),
        "insert": PyFunction("insert", binding=insert_builtin),
        "range": PyFunction("range", binding=range_builtin),
    }


def range_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) == 1:
        execution.states[drone_id].return_value = PyRange(0.0, float(parameters[0].num), 1.0)
        return 0.0
    if len(parameters) == 2:
        execution.states[drone_id].return_value = PyRange(float(parameters[0].num), float(parameters[1].num), 1.0)
        return 0.0
    if len(parameters) == 3:
        execution.states[drone_id].return_value = PyRange(float(parameters[0].num), float(parameters[1].num), float(parameters[2].num))
        return 0.0
    raise ValueError("range expects 1 to 3 parameters")


def append_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 2:
        raise ValueError("append expects 2 parameters")
    parameters[0].append(parameters[1])
    execution.states[drone_id].return_value = PyNone()
    return 1.0


def add_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 2:
        raise ValueError("add expects 2 parameters")
    parameters[0].items.add(parameters[1])
    execution.states[drone_id].return_value = PyNone()
    return float(getattr(parameters[1], "size", lambda: 1)())


def remove_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 2:
        raise ValueError("remove expects 2 parameters")
    collection = parameters[0]
    target = parameters[1]
    if hasattr(collection, "items") and isinstance(collection.items, list):
        collection.items.remove(target)
        execution.states[drone_id].return_value = PyNone()
        return 1.0
    if hasattr(collection, "items") and isinstance(collection.items, set):
        collection.items.remove(target)
        execution.states[drone_id].return_value = PyNone()
        return float(getattr(target, "size", lambda: 1)())
    raise ValueError("remove on unsupported type")


def pop_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) < 1 or len(parameters) > 2:
        raise ValueError("pop expects 1 or 2 parameters")
    collection = parameters[0]
    if hasattr(collection, "items") and isinstance(collection.items, list):
        index = -1
        if len(parameters) == 2:
            index = int(float(parameters[1].num))
        value = collection.items.pop(index)
        execution.states[drone_id].return_value = value
        return 1.0
    if hasattr(collection, "items") and isinstance(collection.items, dict):
        key = parameters[1]
        value = collection.items.pop(key).obj
        execution.states[drone_id].return_value = value
        return float(getattr(key, "size", lambda: 1)())
    raise ValueError("pop on unsupported type")


def insert_builtin(parameters, sim, execution, drone_id) -> float:
    if len(parameters) != 3:
        raise ValueError("insert expects 3 parameters")
    collection = parameters[0]
    index = int(float(parameters[1].num))
    value = parameters[2]
    collection.items.insert(index, value)
    execution.states[drone_id].return_value = PyNone()
    return 1.0


def default_methods() -> dict[str, PyFunction]:
    return {
        "append": PyFunction("append", binding=append_builtin),
        "add": PyFunction("add", binding=add_builtin),
        "remove": PyFunction("remove", binding=remove_builtin),
        "pop": PyFunction("pop", binding=pop_builtin),
        "insert": PyFunction("insert", binding=insert_builtin),
    }
