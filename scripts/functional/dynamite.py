from __builtins__ import *
import production


# 多机榜区域求解器；邻接表每次调用只建一次，每盘结算后检查库存目标。
def dynamite(target=-1, round_limit=0):
    if not production.active(Items.Dynamite, target):
        return
    started = get_time()
    size = get_world_size()
    if size < 4:
        quick_print("炸药采集需要至少4×4的农场。")
        return
    if num_drones() != 1:
        quick_print("请在其他无人机结束后启动。")
        return
    near = make_near(size)

    initial = num_items(Items.Dynamite)
    change_hat(Hats.Mining_Hat)
    production.jump_once(Unlocks.Dynamite)
    cycle = 0
    first = True
    while (round_limit == 0 or cycle < round_limit) and production.active(Items.Dynamite, target):
        began = get_time()
        before = num_items(Items.Dynamite)
        if not first:
            clear()
        first = False
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("dynamite_failed", "find_stratum", cycle)
            return
        depth = get_pos_z()
        if get_ground_type() == Grounds.Soot:
            depth += 1
        prepared = get_time()
        status, number = open_ground(depth)
        rounds = 0
        if status == "number":
            status, rounds = solve(size, depth, near, number)
        if status == "mine":
            status = settle(size, depth)
            rounds += 1
        if status == "running":
            status = settle(size, depth)
        cycle += 1
        total = num_items(Items.Dynamite) - initial
        quick_print("dynamite_cycle", cycle, status, "phases", rounds,
                    num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite),
                    "prepare", prepared - began, "solve", get_time() - prepared,
                    "rate", total / (get_time() - started))
        if status != "ended":
            return


def make_near(size):
    # 同一批工人并行建立邻接表和固定区域；缓存只含几何，不含任何盘面事实。
    workers = min(size, max_drones())
    handles = []
    for group in range(1, workers):
        handle = spawn_drone(plan_strip, group, workers, size)
        result = None
        if handle == None:
            result = plan_strip(group, workers, size)
        handles.append((handle, result))
    near, first = plan_strip(0, workers, size)
    layouts = [first]
    for handle, result in handles:
        if handle != None:
            result = wait_for(handle)
        near = near + result[0]
        layouts.append(result[1])
    WORK_LAYOUTS[(size, workers)] = layouts
    return near


def plan_strip(group, groups, size):
    near = []
    count = size * size
    for cell in range(group * count // groups, (group + 1) * count // groups):
        near.append(neighbors(cell, size))
    return near, work_layout(group, groups, size)


def work_layout(group, groups, size):
    # owned保留原蛇形顺序，clue_cells只限定可读约束范围，不扩大开挖权。
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
    clue_cells = []
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            clue_cells.append(x + y * size)
    return owned, set(owned), clue_cells


# 主机建立后由后代继承只读副本；尺寸或工人数不同的求解调用独立构造。
WORK_LAYOUTS = {}
UNKNOWN = -3
MINE = -1
SAFE = -2
DONE = 9
DIG_LIMIT = 2048
PHASE_LIMIT = 256


def solve(size, depth, near, number, deadline=0, settle_partial=True):
    known = []
    for cell in range(size * size):
        known.append(UNKNOWN)
    known[(size // 2) * (size + 1)] = number
    groups = min(max_drones(), size)
    rounds = 0
    for phase in range(PHASE_LIMIT):
        if deadline > 0 and get_time() >= deadline:
            return "timeout", rounds
        results = dispatch(0, groups, groups, known, near, size, depth, deadline)
        changed = False
        status = "running"
        for state, updates in results:
            if len(updates) > 0:
                changed = True
            if state == "error" or state == "mine" or state == "timeout":
                status = state
            elif state == "ended" and status == "running":
                status = state
            # 状态值按 UNKNOWN、SAFE、MINE、数字、DONE 递增，只保留本盘更强的事实。
            for cell in updates:
                known[cell] = max(known[cell], updates[cell])
        rounds += 1
        if status != "running" or not changed:
            break
    if status == "running" and settle_partial:
        status = settle(size, depth)
    return status, rounds


# 各层同时派工，容量不足时本机完成未派出的区域。
def dispatch(lo, hi, groups, known, near, size, depth, deadline=0):
    if hi - lo == 1:
        return [work(lo, groups, known, near, size, depth, deadline)]
    mid = (lo + hi) // 2
    handle = spawn_drone(dispatch, mid, hi, groups, known, near, size, depth, deadline)
    results = dispatch(lo, mid, groups, known, near, size, depth, deadline)
    if handle == None:
        right = dispatch(mid, hi, groups, known, near, size, depth, deadline)
    else:
        right = wait_for(handle)
    for result in right:
        results.append(result)
    return results


# 各区独立推理并连续开安全格；相邻区域只交换公开数字与确定证明。
def work(group, groups, known, near, size, depth, deadline=0):
    key = (size, groups)
    if key in WORK_LAYOUTS:
        owned, owned_set, clue_cells = WORK_LAYOUTS[key][group]
    else:
        owned, owned_set, clue_cells = work_layout(group, groups, size)
    clues = set()
    for cell in clue_cells:
        if known[cell] >= 0 and known[cell] != DONE:
            clues.add(cell)
    updates = {}
    for step in range(PHASE_LIMIT):
        if deadline > 0 and get_time() >= deadline:
            return "timeout", updates
        if not propagate(known, clues, near, updates):
            return "error", updates
        targets = []
        for cell in owned:
            if known[cell] == SAFE:
                targets.append(cell)
        if len(targets) == 0:
            found = propagate_differences(known, clues, near, updates)
            if found < 0:
                return "error", updates
            if found > 0:
                continue
            return "running", updates
        while len(targets) > 0:
            cell = targets.pop()
            if not move_to(cell % size, cell // size, size):
                return "error", updates
            status, number = open_ground(depth, deadline)
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


# 事实改变只唤醒相邻数字，已解决约束退出本盘队列。
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

# 仅在基本规则停滞时比较相邻公开数字；所有差集事实来自同一盘。
def propagate_differences(known, active, near, updates):
    constraints = {}
    for clue in active:
        remaining = known[clue]
        cells = set()
        for cell in near[clue]:
            if known[cell] == MINE:
                remaining -= 1
            elif known[cell] == UNKNOWN:
                cells.add(cell)
        constraints[clue] = (remaining, cells)
    facts = {}
    for clue in constraints:
        mines_a, cells_a = constraints[clue]
        for other in near[clue]:
            if other <= clue or other not in constraints:
                continue
            mines_b, cells_b = constraints[other]
            only_a = []
            only_b = []
            for cell in cells_a:
                if cell not in cells_b:
                    only_a.append(cell)
            for cell in cells_b:
                if cell not in cells_a:
                    only_b.append(cell)
            difference = mines_a - mines_b
            value_a = UNKNOWN
            value_b = UNKNOWN
            if difference == len(only_a):
                value_a = MINE
                value_b = SAFE
            elif -difference == len(only_b):
                value_a = SAFE
                value_b = MINE
            else:
                continue
            for cell in only_a:
                if cell in facts and facts[cell] != value_a:
                    return -1
                facts[cell] = value_a
            for cell in only_b:
                if cell in facts and facts[cell] != value_b:
                    return -1
                facts[cell] = value_b
    for cell in facts:
        known[cell] = facts[cell]
        updates[cell] = facts[cell]
    return len(facts)


# 找层工人按深度轮流下刀，全部结束后才解盘；上一盘有效煤灰不重复挖。
def find_stratum():
    if get_ground_type() == Grounds.Dynamite:
        return True
    if get_ground_type() == Grounds.Soot:
        if measure() != None:
            return True
        if not dig():
            return False
    count = max_drones()
    limit_z = get_pos_z() - DIG_LIMIT
    handles = []
    for slot in range(1, count):
        handles.append(spawn_drone(dig_to_stratum, slot, count, limit_z))
    dig_to_stratum(0, count, limit_z)
    for handle in handles:
        wait_for(handle)
    return get_ground_type() == Grounds.Dynamite


def dig_to_stratum(slot, count, limit_z):
    while True:
        z = get_pos_z()
        ground = get_ground_type()
        if ground == Grounds.Dynamite or ground == Grounds.Soot:
            return
        if z <= limit_z or get_hardness() >= 10000000:
            return
        if (-z) % count == slot:
            if not dig():
                return


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


# 只有实际要开格时才清理覆盖层，绝不在煤灰上为了读数再次dig。
def open_ground(depth, deadline=0):
    for _ in range(DIG_LIMIT):
        if deadline > 0 and get_time() + get_hardness() / (1.5 ** num_unlocked(Unlocks.Mining)) >= deadline:
            return "timeout", None
        if get_pos_z() <= depth:
            break
        if get_hardness() >= 10000000 or not dig():
            return "error", None
    z = get_pos_z()
    if z > depth:
        return "error", None
    if z == depth:
        if deadline > 0 and get_time() + get_hardness() / (1.5 ** num_unlocked(Unlocks.Mining)) >= deadline:
            return "timeout", None
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    return read_ground(depth)


# 所有句柄已回收；正常结算当前盘一次，再进入下一层。
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
    dynamite()
