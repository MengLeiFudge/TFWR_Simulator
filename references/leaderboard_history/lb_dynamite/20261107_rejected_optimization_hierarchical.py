from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/dynamite-leaderboard-optimization/hierarchical.py
from lb_dynamite import neighbors, move_to, find_stratum, open_ground, settle, infer_subset, choose_guess

UNKNOWN = -2
MINE = -1
SAFE = -3


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
        began = get_time()
        before = num_items(Items.Dynamite)
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            return
        depth = get_pos_z()
        prepared = get_time()
        status, number = open_ground(depth)
        if status != "number":
            return
        known = []
        for cell in range(size * size):
            known.append(UNKNOWN)
        known[(size // 2) * (size + 1)] = number
        groups = min(max_drones(), size)
        status, updates = dispatch(0, groups, groups, known, near, size, depth)
        if status == "running":
            status = settle(size, depth)
        quick_print("dynamite_cycle", cycle, status,
                    num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite),
                    "prepare", prepared - began, "solve", get_time() - prepared)
        if status != "ended":
            return


# 相邻子组先在本层合并到停滞，再将新事实交给父组。
def dispatch(lo, hi, groups, known, near, size, depth):
    if hi - lo == 1:
        return work(lo, groups, known, near, size, depth)
    mid = (lo + hi) // 2
    combined = {}
    for phase in range(32):
        handle = spawn_drone(dispatch, mid, hi, groups, known, near, size, depth)
        left = dispatch(lo, mid, groups, known, near, size, depth)
        if handle == None:
            right = dispatch(mid, hi, groups, known, near, size, depth)
        else:
            right = wait_for(handle)
        status = "running"
        changed = False
        for state, updates in [left, right]:
            if state == "error" or state == "mine":
                status = state
            elif state == "ended" and status == "running":
                status = state
            if len(updates) > 0:
                changed = True
            for cell in updates:
                value = updates[cell]
                old = known[cell]
                if old == value:
                    combined[cell] = value
                elif old >= 0 and value == SAFE:
                    continue
                elif old == UNKNOWN or (old == SAFE and value >= 0):
                    known[cell] = value
                    combined[cell] = value
                else:
                    return "error", combined
        if status != "running" or not changed:
            return status, combined
    return "running", combined


# 相邻区域只交换可证明状态；实际开格只由所属区域执行。
def work(group, groups, known, near, size, depth):
    columns = min(8, groups)
    rows = groups // columns
    left = (group % columns) * size // columns
    right = (group % columns + 1) * size // columns
    bottom = (group // columns) * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    for y in range(bottom, top):
        for x in range(left, right):
            owned.append(x + y * size)
    clues = set()
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            cell = x + y * size
            if known[cell] >= 0:
                clues.add(cell)
    owned_set = set(owned)
    updates = {}
    for step in range(256):
        constraints = propagate(known, clues, near, updates)
        if constraints == None:
            return "error", updates
        targets = []
        for cell in owned:
            if known[cell] == SAFE:
                targets.append(cell)
        if len(targets) == 0:
            return "running", updates
        while len(targets) > 0:
            cell = targets.pop()
            if not move_to(cell % size, cell // size, size):
                return "error", updates
            status, number = open_ground(depth)
            if status != "number":
                return status, updates
            known[cell] = number
            updates[cell] = number
            if number == 0:
                for other in near[cell]:
                    if known[other] == UNKNOWN:
                        known[other] = SAFE
                        updates[other] = SAFE
                        if other in owned_set:
                            targets.append(other)
            else:
                clues.add(cell)
    return "error", updates


# 一次传播只处理本区及两格边界的数字，变化通过公开事实交给父机。
def propagate(known, active, near, updates):
    pending = []
    queued = set()
    constraints = {}
    for clue in active:
        pending.append(clue)
        queued.add(clue)
    while len(pending) > 0:
        clue = pending.pop()
        queued.remove(clue)
        if clue not in active:
            continue
        remaining = known[clue]
        unknown = set()
        for cell in near[clue]:
            value = known[cell]
            if value == MINE:
                remaining -= 1
            elif value == UNKNOWN:
                unknown.add(cell)
        if remaining < 0 or remaining > len(unknown):
            return None
        if remaining != 0 and remaining != len(unknown):
            constraints[clue] = (unknown, remaining)
            continue
        active.remove(clue)
        if clue in constraints:
            constraints.pop(clue)
        value = MINE
        if remaining == 0:
            value = SAFE
        for cell in unknown:
            known[cell] = value
            updates[cell] = value
            for other in near[cell]:
                if other in active and other not in queued:
                    pending.append(other)
                    queued.add(other)
    return constraints


if __name__ == "__main__":
    lb_dynamite()
