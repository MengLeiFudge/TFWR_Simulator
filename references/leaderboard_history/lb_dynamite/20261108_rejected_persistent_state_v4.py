from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/dynamite-persistent-state-v4/lb_dynamite.py

def lb_dynamite():
    size = get_world_size()
    groups = min(max_drones(), size)
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    plans = []
    columns = min(8, groups)
    rows = groups // columns
    for owner in range(groups):
        left = owner % columns * size // columns
        right = (owner % columns + 1) * size // columns
        bottom = owner // columns * size // rows
        top = (owner // columns + 1) * size // rows
        owned = []
        for y in range(bottom, top):
            for x in range(left, right):
                owned.append(x + y * size)
        peers = []
        for gy in range(max(0, owner // columns - 1), min(rows, owner // columns + 2)):
            for gx in range(max(0, owner % columns - 1), min(columns, owner % columns + 2)):
                peers.append(gx + gy * columns)
        plans.append((owned, set(owned), peers, left, right, bottom, top))
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 10000000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            return
        depth = get_pos_z()
        status, first = open_ground(depth)
        if status != "number":
            return
        base = [UNKNOWN] * (size * size)
        start = (size // 2) * (size + 1)
        base[start] = first
        states = [None] * groups
        before = num_items(Items.Dynamite)
        phases = 0
        for _ in range(256):
            results = dispatch(0, groups, base, states, plans, near, size, depth, start, first)
            changed = False
            status = "running"
            for owner, state, payload, progress in results:
                states[owner] = payload
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


def dispatch(lo, hi, base, states, plans, near, size, depth, start, first):
    if hi - lo == 1:
        return [work(lo, base, states, plans, near, size, depth, start, first)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, base, states, plans, near, size, depth, start, first)
    results = dispatch(lo, mid, base, states, plans, near, size, depth, start, first)
    if handle == None:
        right = dispatch(mid, hi, base, states, plans, near, size, depth, start, first)
    else:
        right = wait_for(handle)
    for result in right:
        results.append(result)
    return results


def work(owner, base, states, plans, near, size, depth, start, first):
    owned, owned_set, peers, left, right, bottom, top = plans[owner]
    previous = states[owner]
    if previous == None:
        known = list(base)
        constraints = {}
        numbers = {}
    else:
        known = previous[1]
        constraints = previous[2]
        numbers = previous[3]
    pending = []
    targets = []
    out = []
    for cell in owned:
        if known[cell] == SAFE:
            targets.append(cell)
    for peer in peers:
        other = states[peer]
        if other == None:
            continue
        for cell, value in other[0] + other[4]:
            if value == UNKNOWN:
                continue
            if value < 0:
                fact(cell, value, known, near, constraints, pending, targets, out, owned_set)
            elif cell not in numbers:
                if known[cell] == MINE:
                    return pack(owner, "error", owned, known, constraints, numbers, out, previous)
                fact(cell, SAFE, known, near, constraints, pending, targets, out, owned_set)
                numbers[cell] = value
                x = cell % size
                y = cell // size
                if x >= left - 2 and x < right + 2 and y >= bottom - 2 and y < top + 2:
                    number(cell, value, known, near, constraints, pending, targets, out, owned_set)
                else:
                    known[cell] = value
    if previous == None and start % size >= left - 2 and start % size < right + 2 and start // size >= bottom - 2 and start // size < top + 2:
        numbers[start] = first
        number(start, first, known, near, constraints, pending, targets, out, owned_set)
    cursor = get_pos_x() + get_pos_y() * size
    for _ in range(512):
        while len(pending) > 0:
            clue = pending.pop()
            if clue not in constraints:
                continue
            remaining, unknown = constraints[clue]
            if remaining < 0 or remaining > len(unknown):
                return pack(owner, "error", owned, known, constraints, numbers, out, previous)
            if remaining != 0 and remaining != len(unknown):
                continue
            constraints.pop(clue)
            known[clue] = DONE
            value = SAFE
            if remaining > 0:
                value = MINE
            for cell in unknown:
                fact(cell, value, known, near, constraints, pending, targets, out, owned_set)
        if len(targets) == 0:
            return pack(owner, "running", owned, known, constraints, numbers, out, previous)
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
            return pack(owner, "error", owned, known, constraints, numbers, out, previous)
        status, value = open_ground(depth)
        if status != "number":
            return pack(owner, status, owned, known, constraints, numbers, out, previous)
        numbers[cell] = value
        number(cell, value, known, near, constraints, pending, targets, out, owned_set)
    return pack(owner, "error", owned, known, constraints, numbers, out, previous)


def pack(owner, status, owned, known, constraints, numbers, out, previous):
    public = []
    for cell in owned:
        value = known[cell]
        if cell in numbers:
            value = numbers[cell]
        public.append((cell, value))
    payload = [public, known, constraints, numbers, out]
    return owner, status, payload, len(out) > 0 or previous == None or public != previous[0]


def fact(cell, value, known, near, constraints, pending, targets, out, owned):
    if known[cell] != UNKNOWN:
        return
    known[cell] = value
    if cell not in owned:
        out.append((cell, value))
    elif value == SAFE:
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


def number(cell, value, known, near, constraints, pending, targets, out, owned):
    known[cell] = value
    if value == 0:
        known[cell] = DONE
        for other in near[cell]:
            fact(other, SAFE, known, near, constraints, pending, targets, out, owned)
        return
    remaining = value
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
