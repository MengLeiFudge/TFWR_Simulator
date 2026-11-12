from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/dynamite-multi-cached-v2/lb_dynamite.py


def lb_dynamite():
    size = get_world_size()
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    started = get_time()
    for cycle in range(CYCLE_LIMIT):
        if num_items(Items.Dynamite) >= 10000000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        if get_time() - started > 24000:
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
                # 主机叶子也会修改known；以本批新事实判断进展。
                if len(updates) > 0:
                    changed = True
                if state == "error" or state == "mine":
                    status = state
                elif state == "ended" and status == "running":
                    status = state
                for cell, value in updates:
                    if known[cell] != DONE and (value >= 0 or known[cell] < 0):
                        known[cell] = value
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
# 已实际开挖且所有邻格均已证明；不再需要原数字，也不能重复挖掘。
DONE = 9
# 延续有限盘数和开挖保护；局部与全局批次均设置有限上限。
CYCLE_LIMIT = 512
DIG_LIMIT = 256
PHASE_LIMIT = 256


# 二叉派遣同时展开各层；容量不足时本机完成未派出的子树。
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


# 各区独立推理并连续开安全格；相邻区域只交换公开数字与确定证明。
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
    owned_set = set(owned)
    constraints = {}
    pending = []
    targets = []
    updates = {}
    for cell in owned:
        if known[cell] == SAFE:
            targets.append(cell)
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            cell = x + y * size
            if known[cell] >= 0 and known[cell] != DONE:
                cache_number(cell, known[cell], known, near, constraints, pending, targets, updates, owned_set)
    cursor = get_pos_x() + get_pos_y() * size
    for _ in range(256):
        while len(pending) > 0:
            clue = pending.pop()
            if clue not in constraints:
                continue
            remaining, unknown = constraints[clue]
            if remaining != 0 and remaining != len(unknown):
                continue
            constraints.pop(clue)
            known[clue] = DONE
            updates[clue] = DONE
            value = SAFE
            if remaining > 0:
                value = MINE
            for cell in unknown:
                cache_fact(cell, value, known, near, constraints, pending, targets, updates, owned_set)
        if len(targets) == 0:
            if len(constraints) <= 12 and cache_refine(known, near, constraints, pending, targets, updates, owned_set):
                continue
            return "running", publish(owned, updates)
        cell = -1
        for other in near[cursor]:
            if known[other] == SAFE and other in owned_set:
                cell = other
                break
        if cell < 0:
            cell = targets.pop()
        if known[cell] != SAFE:
            continue
        cursor = cell
        if not move_to(cell % size, cell // size, size):
            return "error", publish(owned, updates)
        status, number = open_ground(depth)
        if status != "number":
            return status, publish(owned, updates)
        cache_number(cell, number, known, near, constraints, pending, targets, updates, owned_set)
    return "error", publish(owned, updates)


def publish(owned, updates):
    result = []
    owned_set = set(owned)
    for cell in updates:
        value = updates[cell]
        if cell in owned_set or value == SAFE or value == MINE:
            result.append((cell, value))
    return result


def cache_fact(cell, value, known, near, constraints, pending, targets, updates, owned):
    if known[cell] != UNKNOWN:
        return
    known[cell] = value
    updates[cell] = value
    if value == SAFE and cell in owned:
        targets.append(cell)
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


def cache_number(cell, number, known, near, constraints, pending, targets, updates, owned):
    if known[cell] != number:
        known[cell] = number
        updates[cell] = number
    if number == 0:
        known[cell] = DONE
        updates[cell] = DONE
        for other in near[cell]:
            cache_fact(other, SAFE, known, near, constraints, pending, targets, updates, owned)
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
        updates[cell] = DONE
        return
    constraints[cell] = [remaining, unknown]
    if remaining == 0 or remaining == len(unknown):
        pending.append(cell)


def cache_refine(known, near, constraints, pending, targets, updates, owned):
    for ca in constraints:
        ra, a = constraints[ca]
        for cb in constraints:
            rb, b = constraints[cb]
            count = len(b) - len(a)
            if count <= 0 or (rb != ra and rb - ra != count):
                continue
            subset = True
            for cell in a:
                if cell not in b:
                    subset = False
                    break
            if not subset:
                continue
            difference = []
            for cell in b:
                if cell not in a:
                    difference.append(cell)
            value = SAFE
            if rb != ra:
                value = MINE
            for cell in difference:
                cache_fact(cell, value, known, near, constraints, pending, targets, updates, owned)
            return True
    return False


# 局部状态变化唤醒相邻数字；解完的约束永久退出本盘推理。
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


# 只准备首挖入口，其余柱的覆盖层按实际安全任务清理。
def find_stratum():
    for _ in range(DIG_LIMIT):
        if get_ground_type() == Grounds.Dynamite:
            return True
        if get_hardness() >= 10000000 or not dig():
            return False
    return get_ground_type() == Grounds.Dynamite


# 以真实地面、深度和数字表区分当前盘与已结束盘。
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


# 每个区域独占本区的开挖权，绝不在煤灰上为补读数字而再次dig。
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


# 所有工人已回收；在首挖入口的有效煤灰上只结算一次。
def settle(size, depth):
    status, number = read_ground(depth)
    if status == "ended":
        return status
    if status != "number" or not dig():
        return "error"
    status, number = read_ground(depth)
    if status != "ended":
        return "error"
    return status


# 雷数八邻域不环绕，移动允许走农场边界的环绕最短路。
def neighbors(cell, size):
    x = cell % size
    y = cell // size
    result = []
    for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,-1),(-1,1)]:
        nx = x + dx
        ny = y + dy
        if nx >= 0 and nx < size and ny >= 0 and ny < size:
            result.append(nx + ny * size)
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
