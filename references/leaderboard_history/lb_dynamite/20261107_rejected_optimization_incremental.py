from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/dynamite-leaderboard-optimization/incremental.py
from lb_dynamite import neighbors, move_to, find_stratum, open_ground, settle

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
        rounds = 0
        for phase in range(128):
            results = dispatch(0, groups, groups, known, near, size, depth)
            changed = False
            status = "running"
            for result in results:
                state, updates = result
                if len(updates) > 0:
                    changed = True
                if state == "error" or state == "mine":
                    status = state
                elif state == "ended" and status == "running":
                    status = state
                for cell in updates:
                    value = updates[cell]
                    old = known[cell]
                    if old == value or (old >= 0 and value == SAFE):
                        continue
                    if old == UNKNOWN or (old == SAFE and value >= 0):
                        known[cell] = value
                    else:
                        quick_print("dynamite_conflict", cell, old, value)
                        return
            rounds += 1
            if status != "running" or not changed:
                break
        if status == "running":
            status = settle(size, depth)
        quick_print("dynamite_cycle", cycle, status, "phases", rounds,
                    num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite),
                    "prepare", prepared - began, "solve", get_time() - prepared)
        if status != "ended":
            return


def dispatch(lo, hi, groups, known, near, size, depth):
    if hi - lo == 1:
        return [work(lo, groups, known, near, size, depth)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, groups, known, near, size, depth)
    results = dispatch(lo, mid, groups, known, near, size, depth)
    if handle == None:
        right = dispatch(mid, hi, groups, known, near, size, depth)
    else:
        right = wait_for(handle)
    for result in right:
        results.append(result)
    return results


# 每次状态变化只唤醒邻近约束，安全任务队列直接驱动实际开挖。
def work(group, groups, known, near, size, depth):
    columns = min(8, groups)
    rows = groups // columns
    left = (group % columns) * size // columns
    right = (group % columns + 1) * size // columns
    bottom = (group // columns) * size // rows
    top = (group // columns + 1) * size // rows
    owned = set()
    targets = []
    active = set()
    pending = []
    queued = set()
    updates = {}
    for y in range(bottom, top):
        for x in range(left, right):
            cell = x + y * size
            owned.add(cell)
            if known[cell] == SAFE:
                targets.append(cell)
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            cell = x + y * size
            if known[cell] >= 0:
                active.add(cell)
                pending.append(cell)
                queued.add(cell)

    def mark(cell, value):
        known[cell] = value
        updates[cell] = value
        if value == SAFE and cell in owned:
            targets.append(cell)
        for clue in near[cell]:
            if clue in active and clue not in queued:
                pending.append(clue)
                queued.add(clue)

    for step in range(4096):
        while len(pending) > 0:
            clue = pending.pop()
            queued.remove(clue)
            if clue not in active:
                continue
            remaining = known[clue]
            cells = []
            for cell in near[clue]:
                value = known[cell]
                if value == MINE:
                    remaining -= 1
                elif value == UNKNOWN:
                    cells.append(cell)
            if remaining < 0 or remaining > len(cells):
                return "error", updates
            if remaining == 0 or remaining == len(cells):
                active.remove(clue)
                value = MINE
                if remaining == 0:
                    value = SAFE
                for cell in cells:
                    mark(cell, value)
        if len(targets) == 0:
            return "running", updates
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
                    mark(other, SAFE)
        else:
            active.add(cell)
            pending.append(cell)
            queued.add(cell)
    return "error", updates


if __name__ == "__main__":
    lb_dynamite()
