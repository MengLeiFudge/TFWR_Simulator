from __builtins__ import *
# 淘汰候选归档：lb_dynamite_single | 原实验路径 .codex/over50-screen-20261109/lb_dynamite_single_boundary.py

def lb_dynamite_single():
    size = get_world_size()
    near = []
    for cell in range(size * size):
        near.append(neighbors(cell, size))
    routes = []
    for cell in range(size * size):
        route = []
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,-1),(-1,1),(0,2),(2,0),(0,-2),(-2,0)]:
            route.append((cell % size + dx) % size + ((cell // size + dy) % size) * size)
        routes.append(route)
    started = get_time()
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 100000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        if get_time() - started > 14400:
            quick_print("dynamite_failed", "time_limit")
            return
        clear()
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find", cycle)
            return
        depth = get_pos_z()
        status, number = open_ground(depth)
        if status != "number":
            quick_print("dynamite_failed", "first", status)
            return
        before = num_items(Items.Dynamite)
        status = solve_cached((size // 2) * (size + 1), number, near, routes, size, depth)
        if status == "running":
            # 当前格已正常打开；直接在本格煤灰结算一次，无需绕回首挖入口。
            status, number = read_ground(depth)
            if status == "number" and dig():
                status, number = read_ground(depth)
        quick_print("dynamite_cycle", cycle, status, num_items(Items.Dynamite) - before,
                    get_time(), num_items(Items.Dynamite))
        if status != "ended":
            return
    quick_print("dynamite_failed", "cycle_limit")


def solve_cached(start, number, near, routes, size, depth):
    known = []
    for _ in range(size * size):
        known.append(UNKNOWN)
    unseen = set(range(size * size))
    mines = set()
    constraints = {}
    pending = []
    targets = []
    known[start] = SAFE
    unseen.remove(start)
    store_number(start, number, known, near, constraints, pending, targets, unseen, mines)
    cursor = start
    for _ in range(16384):
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
            if refine_cached(known, near, constraints, pending, targets, unseen, mines, size):
                continue
            return "running"
        cell = -1
        # 只有全盘雷已被证明时，才允许省去不相邻任何雷的安全格。
        complete_map = len(mines) == (size * size * 135 + 500) // 1000
        if complete_map:
            for other in routes[cursor]:
                if known[other] == SAFE:
                    for neighbor in near[other]:
                        if known[neighbor] == MINE:
                            cell = other
                            break
                    if cell >= 0:
                        break
            while cell < 0 and len(targets) > 0:
                other = targets.pop()
                if known[other] == SAFE:
                    for neighbor in near[other]:
                        if known[neighbor] == MINE:
                            cell = other
                            break
            if cell < 0:
                return "running"
        else:
            for other in routes[cursor]:
                if known[other] == SAFE:
                    cell = other
                    break
            if cell < 0:
                cell = targets.pop()
            if known[cell] != SAFE:
                continue
        cursor = cell
        if not move_to(cell % size, cell // size, size):
            return "error"
        status, number = open_ground(depth)
        if status != "number":
            return status
        store_number(cell, number, known, near, constraints, pending, targets, unseen, mines)
    return "error"


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


def refine_cached(known, near, constraints, pending, targets, unseen, mines, size):
    # 资源榜原生雷率固定为0.135；8×8按原版四舍五入生成9颗雷。
    remaining = (size * size * 135 + 500) // 1000 - len(mines)
    if len(unseen) > 0 and (remaining == 0 or remaining == len(unseen)):
        value = SAFE
        if remaining > 0:
            value = MINE
        for cell in list(unseen):
            set_fact(cell, value, known, near, constraints, pending, targets, unseen, mines)
        return True
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
                set_fact(cell, value, known, near, constraints, pending, targets, unseen, mines)
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
    lb_dynamite_single()
