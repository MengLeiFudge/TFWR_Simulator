from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/dynamite-leaderboard-optimization/autonomous_scan.py
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


# 每个工人沿自己区域巡回；边界数字通过方向查询读取，不绕行邻区。
def work(group, known, near, size, depth, deadline):
    columns = 8
    rows = min(max_drones(), size) // columns
    left = group % columns * size // columns
    right = (group % columns + 1) * size // columns
    bottom = group // columns * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    for y in range(bottom, top):
        if (y - bottom) % 2 == 0:
            for x in range(left, right):
                owned.append(x + y * size)
        else:
            for x in range(right - 1, left - 1, -1):
                owned.append(x + y * size)
    active = set()
    pending = []
    queued = set()
    for cell in range(len(known)):
        if known[cell] >= 0:
            active.add(cell)
            pending.append(cell)
            queued.add(cell)

    def notify(cell):
        for clue in near[cell]:
            if clue in active and clue not in queued:
                pending.append(clue)
                queued.add(clue)

    def record(cell, number):
        known[cell] = number
        active.add(cell)
        if cell not in queued:
            pending.append(cell)
            queued.add(cell)
        notify(cell)

    index = 0
    step = 1
    while get_time() < deadline:
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
                return False
            if remaining == 0 or remaining == len(cells):
                active.remove(clue)
                value = MINE
                if remaining == 0:
                    value = SAFE
                for cell in cells:
                    known[cell] = value
                    notify(cell)
        cell = owned[index]
        if not move_to(cell % size, cell // size, size):
            return False
        if known[cell] == SAFE:
            status, number = open_ground(depth)
            if status == "ended":
                return True
            if status != "number":
                return False
            record(cell, number)
        x = cell % size
        y = cell // size
        for other, direction in [(cell - 1, West), (cell + 1, East), (cell - size, South), (cell + size, North)]:
            if (direction == West and x == 0) or (direction == East and x + 1 == size) or (direction == South and y == 0) or (direction == North and y + 1 == size):
                continue
            if known[other] >= 0 or known[other] == MINE:
                continue
            z = get_pos_z(direction)
            if z < depth - 1:
                return True
            if z != depth - 1 or get_ground_type(direction) != Grounds.Soot:
                continue
            number = measure(direction)
            if number == None:
                return True
            record(other, number)
        index += step
        if index == len(owned):
            step = -1
            index -= 1
        elif index < 0:
            step = 1
            index = 0
    return True


if __name__ == "__main__":
    lb_dynamite()
