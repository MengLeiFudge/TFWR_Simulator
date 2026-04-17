from __future__ import annotations

from enum import Enum


class SideEffect(Enum):
    """Python-safe port of Core.SideEffect."""

    NONE = "None"
    HARVEST = "Harvest"
    CAN_HARVEST = "CanHarvest"
    SWAP = "Swap"
    PLANT = "Plant"
    MOVE = "Move"
    CAN_MOVE = "CanMove"
    TILL = "Till"
    GET_POS_X = "GetPosX"
    GET_POS_Y = "GetPosY"
    GET_WORLD_SIZE = "GetWorldSize"
    GET_ENTITY_TYPE = "GetEntityType"
    GET_GROUND_TYPE = "GetGroundType"
    USE_ITEM = "UseItem"
    GET_WATER = "GetWater"
    CHANGE_HAT = "ChangeHat"
    NUM_ITEMS = "NumItems"
    GET_COST = "GetCost"
    CLEAR = "Clear"
    GET_COMPANION = "GetCompanion"
    UNLOCK = "Unlock"
    NUM_UNLOCKED = "NumUnlocked"
    MEASURE = "Measure"
    SET_EXECUTION_SPEED = "SetExecutionSpeed"
    SET_WORLD_SIZE = "SetWorldSize"
    GET_TIME = "GetTime"
    SPAWN_DRONE = "SpawnDrone"
    GET_DRONE_ID = "GetDroneId"
    NUM_DRONES = "NumDrones"
    MAX_DRONES = "MaxDrones"
    AWAIT = "Await"
    HAS_FINISHED = "HasFinished"
    TERMINATED = "Terminated"
    ERROR = "Error"
    DO_A_FLIP = "DoAFlip"
    PET_THE_PIGGY = "PetThePiggy"
    PRINT = "Print"
    SIMULATE = "Simulate"
    RUN_LEADERBOARD = "RunLeaderboard"

    @classmethod
    def ordered_names(cls) -> list[str]:
        return [member.value for member in cls]
