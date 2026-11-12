from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/dynamite-central-cached-v1/lb_dynamite.py


def lb_dynamite():
    size = get_world_size()
    groups = min(max_drones(), size)
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 10000000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        began = get_time()
        before = num_items(Items.Dynamite)
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find", cycle)
            return
        depth = get_pos_z()
        status, number = open_ground(depth)
        if status != "number":
            quick_print("dynamite_failed", "first", status)
            return
        known = [UNKNOWN] * (size * size)
        unseen = set(range(size * size))
        mines = set()
        constraints = {}
        pending = []
        targets = []
        start = size // 2 * (size + 1)
        known[start] = SAFE
        unseen.remove(start)
        store_number(start, number, known, near, constraints, pending, targets, unseen, mines)
        prepared = get_time()
        rounds = 0
        for phase in range(1024):
            while len(pending) > 0:
                clue = pending.pop()
                if clue not in constraints:
                    continue
                remaining, unknown = constraints[clue]
                if remaining != 0 and remaining != len(unknown):
                    continue
                constraints.pop(clue)
                known[clue] = DONE
                value = SAFE
                if remaining > 0:
                    value = MINE
                for cell in unknown:
                    set_fact(cell, value, known, near, constraints, pending, targets, unseen, mines)
            if len(targets) == 0:
                break
            columns = []
            for index in range(groups):
                columns.append([])
            for cell in targets:
                if known[cell] == SAFE:
                    columns[cell % size % groups].append(cell)
            targets = []
            jobs = []
            for cells in columns:
                if len(cells) > 0:
                    jobs.append(cells)
            if len(jobs) == 0:
                break
            results = dispatch(0, len(jobs), jobs, size, depth)
            rounds += 1
            for state, numbers in results:
                if state == "error" or state == "mine":
                    quick_print("dynamite_failed", "open", state)
                    return
                if state == "ended":
                    status = "ended"
                for cell, number in numbers:
                    store_number(cell, number, known, near, constraints, pending, targets, unseen, mines)
            if status == "ended":
                break
        if status != "ended":
            status, number = read_ground(depth)
            if status == "number" and dig():
                status, number = read_ground(depth)
        quick_print("dynamite_cycle", cycle, status, "phases", rounds,
                    num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite),
                    "prepare", prepared - began, "solve", get_time() - prepared)
        if status != "ended":
            return


# 一批只打开已证明安全的格子；每格只有一个任务，全部结束后再推进约束。
def dispatch(lo, hi, jobs, size, depth):
    if hi - lo == 1:
        numbers = []
        for cell in jobs[lo]:
            if not move_to(cell % size, cell // size, size):
                return [("error", numbers)]
            state, number = open_ground(depth)
            if state != "number":
                return [(state, numbers)]
            numbers.append((cell, number))
        return [("running", numbers)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, jobs, size, depth)
    results = dispatch(lo, mid, jobs, size, depth)
    if handle == None:
        other = dispatch(mid, hi, jobs, size, depth)
    else:
        other = wait_for(handle)
    for result in other:
        results.append(result)
    return results


def set_fact(cell, value, known, near, constraints, pending, targets, unseen, mines):
    if known[cell] != UNKNOWN:
        return
    known[cell] = value
    unseen.remove(cell)
    if value == MINE:
        mines.add(cell)
    else:
        targets.append(cell)
    # 每个新事实只删除相邻约束里的这一格，不重新扫描全部旧数字。
    for clue in near[cell]:
        if clue not in constraints:
            continue
        state = constraints[clue]
        if cell not in state[1]:
            continue
        state[1].remove(cell)
        if value == MINE:
            state[0] -= 1
        if state[0] == 0 or state[0] == len(state[1]):
            pending.append(clue)


def store_number(cell, number, known, near, constraints, pending, targets, unseen, mines):
    known[cell] = number
    if number == 0:
        known[cell] = DONE
        for other in near[cell]:
            set_fact(other, SAFE, known, near, constraints, pending, targets, unseen, mines)
        return
    remaining = number
    unknown = set()
    for other in near[cell]:
        if known[other] == MINE:
            remaining -= 1
        elif known[other] == UNKNOWN:
            unknown.add(other)
    if len(unknown) == 0:
        known[cell] = DONE
        return
    constraints[cell] = [remaining, unknown]
    if remaining == 0 or remaining == len(unknown):
        pending.append(cell)


UNKNOWN = -2
MINE = -1
SAFE = -3
DONE = 9
DIG_LIMIT = 256


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
    lb_dynamite()
