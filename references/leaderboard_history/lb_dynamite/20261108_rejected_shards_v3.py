from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/dynamite-shards-v3/lb_dynamite.py

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
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find", cycle)
            return
        depth = get_pos_z()
        status, number = open_ground(depth)
        if status != "number":
            return
        known = [UNKNOWN] * (size * size)
        known[(size // 2) * (size + 1)] = number
        states = [None] * groups
        before = num_items(Items.Dynamite)
        phases = 0
        for _ in range(256):
            results = dispatch(0, groups, groups, known, states, near, size, depth)
            changed = False
            status = "running"
            for owner, state, published, progress in results:
                states[owner] = published
                if progress:
                    changed = True
                if state == "error" or state == "mine":
                    status = state
                elif state == "ended" and status == "running":
                    status = state
            phases += 1
            if not changed or status != "running":
                break
        if status == "running":
            status, number = read_ground(depth)
            if status == "number" and dig():
                status, number = read_ground(depth)
        quick_print("dynamite_cycle", cycle, status, phases, get_time(), num_items(Items.Dynamite) - before,
                    num_items(Items.Dynamite))
        if status != "ended":
            return
    quick_print("dynamite_failed", "cycle_limit")


def dispatch(lo, hi, groups, known, states, near, size, depth):
    if hi - lo == 1:
        return [work(lo, groups, known, states, near, size, depth)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, groups, known, states, near, size, depth)
    results = dispatch(lo, mid, groups, known, states, near, size, depth)
    if handle == None:
        right = dispatch(mid, hi, groups, known, states, near, size, depth)
    else:
        right = wait_for(handle)
    for result in right:
        results.append(result)
    return results


def work(group, groups, known, states, near, size, depth):
    state, result = region_work(group, groups, known, states, near, size, depth)
    return group, state, result, states[group] == None or result != states[group]


def region_work(group, groups, known, states, near, size, depth):
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
    width = size // columns
    height = size // rows
    for y in range(max(0, bottom - 3), min(size, top + 3)):
        for x in range(max(0, left - 3), min(size, right + 3)):
            owner = x // width + y // height * columns
            if states[owner] == None:
                continue
            lx = x % width
            ly = y % height
            if ly % 2:
                lx = width - 1 - lx
            known[x + y * size] = states[owner][ly * width + lx]
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
            value = SAFE
            if remaining > 0:
                value = MINE
            for cell in unknown:
                cache_fact(cell, value, known, near, constraints, pending, targets, updates, owned_set)
        if len(targets) == 0:
            if len(constraints) <= 12 and cache_refine(known, near, constraints, pending, targets, updates, owned_set):
                continue
            return "running", publish(owned, known, updates)
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
            return "error", publish(owned, known, updates)
        status, number = open_ground(depth)
        if status != "number":
            return status, publish(owned, known, updates)
        cache_number(cell, number, known, near, constraints, pending, targets, updates, owned_set)
    return "error", publish(owned, known, updates)



def publish(owned, known, updates):
    result = []
    for cell in owned:
        value = known[cell]
        if cell in updates:
            value = updates[cell]
        result.append(value)
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
    known[cell] = number
    updates[cell] = number
    if number == 0:
        known[cell] = DONE
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
