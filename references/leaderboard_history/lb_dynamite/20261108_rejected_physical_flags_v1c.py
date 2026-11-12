from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/dynamite-physical-flags-v1c/lb_dynamite.py


def lb_dynamite():
    size = get_world_size()
    groups = min(max_drones(), size)
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 10000000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        started = get_time()
        before = num_items(Items.Dynamite)
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find", cycle)
            return
        depth = get_pos_z()
        if not prepare(0, groups, groups, size, depth):
            quick_print("dynamite_failed", "prepare", cycle)
            return
        if not move_to(size // 2, size // 2, size):
            return
        status, number = open_ground(depth)
        if status != "number":
            quick_print("dynamite_failed", "first", status)
            return
        prepared = get_time()
        if not deploy(0, groups, groups, size, depth, prepared + 12):
            quick_print("dynamite_failed", "worker", cycle)
            return
        status = settle(size, depth)
        quick_print("dynamite_cycle", cycle, status, num_items(Items.Dynamite) - before,
                    get_time(), num_items(Items.Dynamite), "prepare", prepared - started,
                    "solve", get_time() - prepared)
        if status != "ended":
            return


UNKNOWN = -2
MINE = -1
SAFE = -3
DIG_LIMIT = 256


# 开盘前统一清掉覆盖层，避免数字零扩展与仍在准备的工人争挖矿层。
def prepare(lo, hi, groups, size, depth):
    if hi - lo > 1:
        mid = (lo + hi) // 2
        handle = spawn_drone(prepare, mid, hi, groups, size, depth)
        ok = prepare(lo, mid, groups, size, depth)
        other = False
        if handle == None:
            other = prepare(mid, hi, groups, size, depth)
        else:
            other = wait_for(handle)
        return ok and other
    for y in range(lo, size, groups):
        for offset in range(size):
            x = offset
            if y % 2:
                x = size - 1 - offset
            if not move_to(x, y, size):
                return False
            for step in range(DIG_LIMIT):
                if get_pos_z() <= depth:
                    break
                if get_hardness() >= 10000000 or not dig():
                    return False
            if get_pos_z() != depth or get_ground_type() != Grounds.Dynamite:
                return False
    return True


# 每盘仅派出一次求解工人；所有后代退出后主机才结算。
def deploy(lo, hi, groups, size, depth, deadline):
    if hi - lo == 1:
        return work(lo, groups, size, depth, deadline)
    mid = (lo + hi) // 2
    handle = spawn_drone(deploy, mid, hi, groups, size, depth, deadline)
    ok = deploy(lo, mid, groups, size, depth, deadline)
    other = False
    if handle == None:
        other = deploy(mid, hi, groups, size, depth, deadline)
    else:
        other = wait_for(handle)
    return ok and other


# 只在本区挖格或放石块雷标，边界信息从公开地面读取。
def work(group, groups, size, depth, deadline):
    columns = min(8, groups)
    rows = groups // columns
    left = group % columns * size // columns
    right = (group % columns + 1) * size // columns
    bottom = group // columns * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    owned_set = set()
    route = []
    known = {}
    near = {}
    active = set()
    flagged = set()
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            known[x + y * size] = UNKNOWN
    for y in range(bottom, top):
        for offset in range(right - left):
            x = left + offset
            if (y - bottom) % 2:
                x = right - 1 - offset
            cell = x + y * size
            owned.append(cell)
            owned_set.add(cell)
    for y in range(max(0, bottom - 1), min(size, top + 1)):
        for offset in range(min(size, right + 1) - max(0, left - 1)):
            x = max(0, left - 1) + offset
            if y % 2:
                x = min(size, right + 1) - 1 - offset
            cell = x + y * size
            route.append(cell)
            near[cell] = neighbors(cell, size)

    def observe(cell, direction=None):
        if cell not in known or known[cell] >= 0 or known[cell] == MINE:
            return True
        z = get_pos_z(direction)
        if z < depth - 1:
            return False
        ground = get_ground_type(direction)
        if z == depth + 1 and ground == Grounds.Rock:
            known[cell] = MINE
        elif z == depth - 1 and ground == Grounds.Soot:
            number = measure(direction)
            if number == None:
                return False
            known[cell] = number
            if cell in near:
                active.add(cell)
        return True

    for sweep in range(64):
        if get_time() >= deadline:
            return True
        for index in range(len(route)):
            cell = route[index]
            if sweep % 2:
                cell = route[len(route) - 1 - index]
            if get_time() >= deadline:
                return True
            if not move_to(cell % size, cell // size, size):
                return False
            if not observe(cell):
                return True
            x = cell % size
            y = cell // size
            for other, direction in [(cell - 1, West), (cell + 1, East), (cell - size, South), (cell + size, North)]:
                if (direction == West and x == 0) or (direction == East and x + 1 == size) or (direction == South and y == 0) or (direction == North and y + 1 == size):
                    continue
                if not observe(other, direction):
                    return True
        for phase in range(128):
            changed = True
            while changed:
                changed = False
                retired = []
                for clue in active:
                    remaining = known[clue]
                    unknown = []
                    for cell in near[clue]:
                        value = known[cell]
                        if value == MINE:
                            remaining -= 1
                        elif value == UNKNOWN:
                            unknown.append(cell)
                    if remaining < 0 or remaining > len(unknown):
                        quick_print("dynamite_conflict", group, clue, remaining, len(unknown))
                        return False
                    if remaining != 0 and remaining != len(unknown):
                        continue
                    retired.append(clue)
                    value = MINE
                    if remaining == 0:
                        value = SAFE
                    for cell in unknown:
                        known[cell] = value
                        changed = True
                for clue in retired:
                    active.remove(clue)
            progressed = False
            for cell in owned:
                if get_time() >= deadline:
                    return True
                value = known[cell]
                if value != SAFE and (value != MINE or cell in flagged):
                    continue
                if not move_to(cell % size, cell // size, size):
                    return False
                if value == MINE:
                    if get_pos_z() != depth:
                        quick_print("dynamite_bad_flag", group, cell, get_pos_z())
                        return False
                    if not place(Grounds.Rock):
                        return False
                    flagged.add(cell)
                else:
                    status, number = open_ground(depth)
                    if status == "ended":
                        return True
                    if status != "number":
                        quick_print("dynamite_bad_open", group, cell, status)
                        return False
                    known[cell] = number
                    active.add(cell)
                progressed = True
            if not progressed:
                break
    return True


# 首孔只挖到矿层，不触发其他未知格。
def find_stratum():
    for step in range(DIG_LIMIT):
        if get_ground_type() == Grounds.Dynamite:
            return True
        if get_hardness() >= 10000000 or not dig():
            return False
    return False


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
    return "number", number


def open_ground(depth):
    z = get_pos_z()
    if z == depth:
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    return read_ground(depth)


# 工人已全部退出，才在有效煤灰上正常结算一次。
def settle(size, depth):
    if not move_to(size // 2, size // 2, size):
        return "error"
    status, number = read_ground(depth)
    if status == "ended":
        return status
    if status != "number" or not dig():
        return "error"
    return read_ground(depth)[0]


def neighbors(cell, size):
    result = []
    x = cell % size
    y = cell // size
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if (dx != 0 or dy != 0) and 0 <= x + dx < size and 0 <= y + dy < size:
                result.append(cell + dx + dy * size)
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
    for step in range(dx):
        if not move(horizontal):
            return False
    for step in range(dy):
        if not move(vertical):
            return False
    return True


if __name__ == "__main__":
    lb_dynamite()
