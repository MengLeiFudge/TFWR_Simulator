from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/dynamite-leaderboard-optimization/autonomous.py
from lb_dynamite import neighbors, move_to, find_stratum, open_ground, settle
from regional_zero import propagate

UNKNOWN = -2
MINE = -1
SAFE = -3
BOARD_SECONDS = 18


def lb_dynamite(goal=10000000):
    size = get_world_size()
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    started = get_time()
    for cycle in range(512):
        if num_items(Items.Dynamite) >= goal:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        if get_time() - started > 24000:
            return
        before = num_items(Items.Dynamite)
        began = get_time()
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            return
        depth = get_pos_z()
        status, number = open_ground(depth)
        if status != "number":
            return
        known = []
        for cell in range(size * size):
            known.append(UNKNOWN)
        known[(size // 2) * (size + 1)] = number
        prepared = get_time()
        results = dispatch(0, min(max_drones(), size), known, near, size, depth, get_time() + BOARD_SECONDS)
        for result in results:
            if not result:
                quick_print("dynamite_failed", "worker")
                return
        status = settle(size, depth)
        quick_print("dynamite_cycle", cycle, status, num_items(Items.Dynamite) - before,
                    get_time(), num_items(Items.Dynamite), "prepare", prepared - began,
                    "solve", get_time() - prepared)
        if status != "ended":
            return


# 工人一次派出后自主读取周边公开数字，全部退出后主机才结算。
def dispatch(lo, hi, known, near, size, depth, deadline):
    if hi - lo == 1:
        return [work(lo, known, near, size, depth, deadline)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, known, near, size, depth, deadline)
    results = dispatch(lo, mid, known, near, size, depth, deadline)
    if handle == None:
        other = dispatch(mid, hi, known, near, size, depth, deadline)
    else:
        other = wait_for(handle)
    for result in other:
        results.append(result)
    return results


# 区域边界只读；挖掘仅在本区，避免并发改写同一列。
def work(group, known, near, size, depth, deadline):
    columns = 8
    rows = min(max_drones(), size) // columns
    left = group % columns * size // columns
    right = (group % columns + 1) * size // columns
    bottom = group // columns * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    border = []
    for y in range(max(0, bottom - 1), min(size, top + 1)):
        for x in range(max(0, left - 1), min(size, right + 1)):
            cell = x + y * size
            if x >= left and x < right and y >= bottom and y < top:
                owned.append(cell)
            else:
                border.append(cell)
    owned_set = set(owned)
    active = set()
    for cell in range(len(known)):
        if known[cell] >= 0:
            active.add(cell)
    updates = {}
    scans = 0
    while get_time() < deadline:
        constraints = propagate(known, active, near, updates)
        if constraints == None:
            return False
        targets = []
        remaining = False
        for cell in owned:
            if known[cell] == SAFE:
                targets.append(cell)
            elif known[cell] == UNKNOWN:
                remaining = True
        while len(targets) > 0:
            cell = targets.pop()
            if not move_to(cell % size, cell // size, size):
                return False
            status, number = open_ground(depth)
            if status == "ended":
                return True
            if status != "number":
                return False
            known[cell] = number
            if number == 0:
                for other in near[cell]:
                    if known[other] == UNKNOWN:
                        known[other] = SAFE
                        if other in owned_set:
                            targets.append(other)
            else:
                active.add(cell)
        if not remaining:
            return True
        # 边界读取只接受当前盘真实Soot，覆盖层与未开雷格不产生事实。
        for cell in border:
            if known[cell] >= 0:
                continue
            if not move_to(cell % size, cell // size, size):
                return False
            z = get_pos_z()
            if z < depth - 1:
                return True
            if z != depth - 1 or get_ground_type() != Grounds.Soot:
                continue
            number = measure()
            if number == None:
                return True
            known[cell] = number
            active.add(cell)
        scans += 1
    return True


if __name__ == "__main__":
    lb_dynamite()
