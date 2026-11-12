from __builtins__ import *
# 淘汰候选归档：lb_dynamite_single | 原实验路径 .codex/nonreset-100-20261108/dynamite-interior-v1/lb_dynamite_single.py


def lb_dynamite_single():
    size = get_world_size()
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    started = get_time()
    for cycle in range(CYCLE_LIMIT):
        if num_items(Items.Dynamite) >= 100000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        if get_time() - started > 14400:
            quick_print("dynamite_failed", "time_limit")
            return
        began = get_time()
        before = num_items(Items.Dynamite)
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find_stratum", cycle)
            return
        depth = get_pos_z()
        prepared = get_time()
        status, number = open_ground(depth)
        if status != "number":
            quick_print("dynamite_failed", "first_cell", status)
            return
        known = []
        for cell in range(size * size):
            known.append(UNKNOWN)
        known[(size // 2) * (size + 1)] = number
        groups = min(max_drones(), size)
        rounds = 0
        for phase in range(PHASE_LIMIT):
            results = dispatch(0, groups, groups, known, near, size, depth)
            changed = False
            status = "running"
            for state, updates in results:
                if len(updates) > 0:
                    changed = True
                if state == "error":
                    status = state
                elif state == "mine" and status != "error":
                    status = state
                elif state == "ended" and status == "running":
                    status = state
                for cell in updates:
                    value = updates[cell]
                    old = known[cell]
                    if old == value or (old >= 0 and value == SAFE) or (old == DONE and value >= 0):
                        continue
                    if old == UNKNOWN or (old == SAFE and value >= 0) or (old >= 0 and value == DONE):
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
    quick_print("dynamite_failed", "cycle_limit")


UNKNOWN = -2
MINE = -1
SAFE = -3
# 已开格且所有邻格均已证明，退出本盘约束队列。
DONE = 9
CYCLE_LIMIT = 512
DIG_LIMIT = 256
PHASE_LIMIT = 256


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


# 单机负责全盘；只维护变化数字，推理停滞后正常结算一次。
def work(group, groups, known, near, size, depth):
    columns = min(8, groups)
    rows = groups // columns
    left = (group % columns) * size // columns
    right = (group % columns + 1) * size // columns
    bottom = (group // columns) * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    for y in range(bottom, top):
        if (y - bottom) % 2 == 0:
            for x in range(left, right):
                owned.append(x + y * size)
        else:
            for x in range(right - 1, left - 1, -1):
                owned.append(x + y * size)
    clues = set()
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            cell = x + y * size
            if known[cell] >= 0 and known[cell] != DONE:
                clues.add(cell)
    owned_set = set(owned)
    updates = {}
    for step in range(PHASE_LIMIT):
        if not propagate(known, clues, near, updates):
            return "error", updates
        targets = []
        for cell in owned:
            if known[cell] == SAFE:
                targets.append(cell)
        if len(targets) == 0:
            return "running", updates
        while len(targets) > 0:
            cell = targets.pop()
            if known[cell] != SAFE:
                continue
            boundary = False
            for other in near[cell]:
                if known[other] == UNKNOWN or known[other] == MINE:
                    boundary = True
                    break
            if not boundary:
                known[cell] = DONE
                updates[cell] = DONE
                continue
            if not move_to(cell % size, cell // size, size):
                return "error", updates
            status, number = open_ground(depth)
            if status != "number":
                return status, updates
            known[cell] = number
            updates[cell] = number
            if number == 0:
                known[cell] = DONE
                updates[cell] = DONE
                for other in near[cell]:
                    if known[other] == UNKNOWN:
                        known[other] = SAFE
                        updates[other] = SAFE
                        if other in owned_set:
                            targets.append(other)
            else:
                clues.add(cell)
    return "error", updates


# 一个新事实只唤醒相邻数字，已完成约束不再扫描。
def propagate(known, active, near, updates):
    pending = []
    queued = set()
    for clue in active:
        pending.append(clue)
        queued.add(clue)
    while len(pending) > 0:
        clue = pending.pop()
        queued.remove(clue)
        if clue not in active:
            continue
        remaining = known[clue]
        unknown = []
        for cell in near[clue]:
            value = known[cell]
            if value == MINE:
                remaining -= 1
            elif value == UNKNOWN:
                unknown.append(cell)
        if remaining < 0 or remaining > len(unknown):
            return False
        if remaining != 0 and remaining != len(unknown):
            continue
        active.remove(clue)
        known[clue] = DONE
        updates[clue] = DONE
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
    return True


def find_stratum():
    for _ in range(DIG_LIMIT):
        if get_ground_type() == Grounds.Dynamite:
            return True
        if get_hardness() >= 10000000 or not dig():
            return False
    return get_ground_type() == Grounds.Dynamite


# 深度或数字表消失表示已结束；煤灰只读数，不因复读再次dig。
def read_ground(depth):
    z = get_pos_z()
    if z >= depth:
        return "closed", None
    if z < depth - 1:
        return "ended", None
    if get_ground_type() != Grounds.Soot:
        return "error", None
    if get_entity_type() == Entities.Dynamite:
        return "mine", None
    number = measure()
    if number == None:
        return "ended", None
    if number not in range(9):
        return "error", None
    return "number", number


def open_ground(depth):
    for _ in range(DIG_LIMIT):
        if get_pos_z() <= depth:
            break
        if get_hardness() >= 10000000 or not dig():
            return "error", None
    z = get_pos_z()
    if z > depth:
        return "error", None
    if z == depth:
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    return read_ground(depth)


def settle(size, depth):
    if not move_to(size // 2, size // 2, size):
        return "error"
    status, number = read_ground(depth)
    if status == "ended":
        return status
    if status != "number" or not dig():
        return "error"
    status, number = read_ground(depth)
    if status != "ended":
        return "error"
    return status


# 雷数八邻域不环绕，常规移动允许经过农场边界。
def neighbors(cell, size):
    x = cell % size
    y = cell // size
    result = []
    if y > 0:
        if x > 0:
            result.append(cell - size - 1)
        result.append(cell - size)
        if x + 1 < size:
            result.append(cell - size + 1)
    if x > 0:
        result.append(cell - 1)
    if x + 1 < size:
        result.append(cell + 1)
    if y + 1 < size:
        if x > 0:
            result.append(cell + size - 1)
        result.append(cell + size)
        if x + 1 < size:
            result.append(cell + size + 1)
    return result


def move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


if __name__ == "__main__":
    lb_dynamite_single()
