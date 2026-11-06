from __builtins__ import *
# 完整轮时间：5561.376秒（构建26462009，2轮官方完整统计；请求367）。

def lb_dynamite():
    size = get_world_size()
    adjacent = []
    for cell in range(size * size):
        adjacent.append(dynamite_neighbors(cell, size))
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 10000000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        clear()
        covers = 0
        while get_ground_type() != Grounds.Dynamite:
            if covers >= 256 or get_time() - began > 24000 or not dig():
                quick_print("dynamite_failed", "find_stratum", cycle)
                return
            covers += 1
        depth = get_pos_z()
        # 开局先逐列准备到同一顶面；此时还没有扫雷盘，不会挖到未知雷。
        ready = dynamite_prepare(size, depth)
        if not ready or not dynamite_move_to(1, 1, size) or not dig():
            quick_print("dynamite_failed", "prepare", cycle)
            return
        before = num_items(Items.Dynamite)
        status, guesses = dynamite_solve(size, depth, adjacent)
        quick_print("dynamite_cycle", cycle, status, guesses, num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite))
        if status == "error":
            return
    quick_print("dynamite_failed", "cycle_limit", get_time(), num_items(Items.Dynamite))


def dynamite_prepare(size, depth):
    handles = []
    ok = True
    for x in range(size):
        if num_drones() < max_drones():
            handle = spawn_drone(dynamite_prepare_column, x, size, depth)
            if handle != None:
                handles.append(handle)
                continue
        if not dynamite_prepare_column(x, size, depth):
            ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def dynamite_prepare_column(x, size, depth):
    if not dynamite_move_to(x, 0, size):
        return False
    for _ in range(size):
        while get_pos_z() > depth:
            if not dig():
                return False
        if get_pos_z() != depth or get_ground_type() != Grounds.Dynamite:
            return False
        if not move(North):
            return False
    return True


def dynamite_solve(size, depth, adjacent):
    known = []
    for _ in range(size * size):
        known.append(-2)
    active = set()
    jobs = []
    for _ in range(size):
        jobs.append([])
    guesses = 0
    for phase in range(2048):
        status, facts = dynamite_phase(jobs, size, depth, known)
        if status != "running":
            return status, guesses
        for cell in facts:
            if known[cell] == -1:
                quick_print("dynamite_failed", "contradiction", cell)
                return "error", guesses
            known[cell] = facts[cell]
            active.add(cell)
        constraints = []
        for _ in range(16):
            changed = False
            closed = []
            constraints = []
            for clue in active:
                remaining = known[clue]
                unknown = set()
                for other in adjacent[clue]:
                    if known[other] == -1:
                        remaining -= 1
                    elif known[other] == -2:
                        unknown.add(other)
                if remaining < 0 or remaining > len(unknown):
                    quick_print("dynamite_failed", "constraint", clue)
                    return "error", guesses
                if remaining == 0 or remaining == len(unknown):
                    value = -1
                    if remaining == 0:
                        value = -3
                    for other in unknown:
                        known[other] = value
                        changed = True
                    closed.append(clue)
                else:
                    constraints.append((unknown, remaining))
            for clue in closed:
                active.remove(clue)
            if not changed:
                break
        # 达到传播上限时重新读盘，再由完整快照建立约束。
        if changed:
            continue
        safe = []
        for cell in range(size * size):
            if known[cell] == -3:
                safe.append(cell)
        if len(safe) == 0 and dynamite_subset(known, constraints):
            for cell in range(size * size):
                if known[cell] == -3:
                    safe.append(cell)
        jobs = []
        for _ in range(size):
            jobs.append([])
        for cell in safe:
            jobs[cell % size].append(cell)
        if len(safe) > 0:
            continue
        # 没有确定安全格时先重新观察一次，接收零扩展公开揭开的数字。
        if phase == 0 or len(facts) > 0:
            continue
        choice = dynamite_guess(known, constraints)
        if choice == None or guesses >= 32:
            for cell in range(size * size):
                if known[cell] >= 0 and dynamite_move_to(cell % size, cell // size, size):
                    if get_ground_type() == Grounds.Soot:
                        dig()
                        return "settled", guesses
            return "error", guesses
        if not dynamite_move_to(choice % size, choice // size, size):
            return "error", guesses
        if get_pos_z() == depth and get_ground_type() == Grounds.Dynamite:
            dig()
            guesses += 1
        # 踩雷可能在dig返回前就完成爆炸；下一观察批次按真实地层识别终态。
    return "error", guesses


def dynamite_phase(jobs, size, depth, known):
    # known在派发到wait完成之间只读，每列只执行自己的确定安全格。
    handles = []
    results = []
    for x in range(size):
        if num_drones() < max_drones():
            handle = spawn_drone(dynamite_column, x, jobs[x], size, depth, known)
            if handle != None:
                handles.append(handle)
                continue
        results.append(dynamite_column(x, jobs[x], size, depth, known))
    for handle in handles:
        results.append(wait_for(handle))
    status = "running"
    facts = {}
    for result in results:
        if result[0] == "error":
            status = "error"
        elif result[0] == "ended" and status != "error":
            status = "ended"
        for cell in result[1]:
            if cell in facts and facts[cell] != result[1][cell]:
                quick_print("dynamite_failed", "observation_conflict", cell)
                status = "error"
            facts[cell] = result[1][cell]
    return status, facts


def dynamite_column(x, cells, size, depth, known):
    facts = {}
    for cell in cells:
        if not dynamite_move_to(x, cell // size, size):
            return "error", facts
        if get_pos_z() == depth and get_ground_type() == Grounds.Dynamite:
            if not dig():
                return "error", facts
    # 已知Soot也可用于检查数字表是否结算；不能只看未知格而漏掉终态。
    z = get_pos_z()
    if z < depth - 1:
        return "ended", facts
    if z == depth - 1 and get_ground_type() == Grounds.Soot:
        if measure() == None:
            return "ended", facts
    # 每格由本列观察一次；零扩展在其他工人稍后出现时由下一批补读。
    for y in range(size):
        cell = x + y * size
        if known[cell] != -2 and known[cell] != -3:
            continue
        if not dynamite_move_to(x, y, size):
            return "error", facts
        z = get_pos_z()
        if z < depth - 1:
            return "ended", facts
        if z == depth - 1 and get_ground_type() == Grounds.Soot:
            number = measure()
            if number == None:
                return "ended", facts
            facts[cell] = number
    return "running", facts


def dynamite_subset(known, constraints):
    # 只比较有限对约束；找不到证明就交给显式猜测，不把启发式当安全结论。
    checked = 0
    for first in range(len(constraints)):
        for second in range(first + 1, len(constraints)):
            checked += 1
            if checked > 4096:
                return False
            small, a = constraints[first]
            large, b = constraints[second]
            if len(small) > len(large):
                small, large = large, small
                a, b = b, a
            subset = True
            for cell in small:
                if cell not in large:
                    subset = False
                    break
            if not subset:
                continue
            difference = []
            for cell in large:
                if cell not in small and known[cell] == -2:
                    difference.append(cell)
            remaining = b - a
            if len(difference) > 0 and (remaining == 0 or remaining == len(difference)):
                value = -1
                if remaining == 0:
                    value = -3
                for cell in difference:
                    known[cell] = value
                return True
    return False


def dynamite_guess(known, constraints):
    risks = {}
    for cells, count in constraints:
        risk = count / len(cells)
        for cell in cells:
            if known[cell] == -2 and (cell not in risks or risk > risks[cell]):
                risks[cell] = risk
    best = None
    least = 2
    for cell in range(len(known)):
        if known[cell] != -2:
            continue
        risk = 0.5
        if cell in risks:
            risk = risks[cell]
        if risk < least:
            best = cell
            least = risk
    return best


def dynamite_neighbors(cell, size):
    x = cell % size
    y = cell // size
    result = []
    for ny in range(max(0, y - 1), min(size, y + 2)):
        for nx in range(max(0, x - 1), min(size, x + 2)):
            if nx != x or ny != y:
                result.append(nx + ny * size)
    return result


def dynamite_move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_dynamite()
