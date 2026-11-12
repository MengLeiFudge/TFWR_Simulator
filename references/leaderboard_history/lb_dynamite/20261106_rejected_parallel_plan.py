from __builtins__ import *
# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/leaderboard-sol/underground-strategies/dynamite/parallel-plan/lb_dynamite.py

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
    jobs = []
    for _ in range(size):
        jobs.append([])
    guesses = 0
    for phase in range(2048):
        ended, facts, marks, constraints = dynamite_phase(jobs, size, depth, known)
        if ended:
            return "ended", guesses
        changed = False
        for cell in facts:
            if known[cell] == -1:
                quick_print("dynamite_failed", "contradiction", cell)
                return "error", guesses
            if known[cell] != facts[cell]:
                changed = True
            known[cell] = facts[cell]
        for cell in marks:
            if known[cell] >= 0:
                if marks[cell] == -1:
                    quick_print("dynamite_failed", "proved_mine_open", cell)
                    return "error", guesses
                continue
            if known[cell] == -2:
                known[cell] = marks[cell]
                changed = True
            elif known[cell] != marks[cell]:
                quick_print("dynamite_failed", "proof_conflict", cell)
                return "error", guesses
        jobs = []
        for _ in range(size):
            jobs.append([])
        safe = 0
        for cell in range(size * size):
            if known[cell] == -3:
                jobs[cell % size].append(cell)
                safe += 1
        if safe > 0 or changed:
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
    return "error", guesses


def dynamite_phase(jobs, size, depth, known):
    # 冻结的known按值复制；工人只执行确定安全格，证明在全部wait后才合并。
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
    ended = False
    facts = {}
    marks = {}
    constraints = []
    for result in results:
        ended = ended or result[0]
        for cell in result[1]:
            facts[cell] = result[1][cell]
        for cell in result[2]:
            marks[cell] = result[2][cell]
        constraints = constraints + result[3]
    return ended, facts, marks, constraints


def dynamite_column(x, cells, size, depth, known):
    facts = {}
    for cell in cells:
        if not dynamite_move_to(x, cell // size, size):
            return True, facts, {}, []
        if get_pos_z() == depth and get_ground_type() == Grounds.Dynamite:
            if not dig():
                return True, facts, {}, []
    if not dynamite_move_to(x, 0, size):
        return True, facts, {}, []
    for y in range(size):
        for dx, dy, direction in [(0, 0, None), (0, 1, North), (1, 0, East), (0, -1, South), (-1, 0, West)]:
            nx = x + dx
            ny = y + dy
            if nx < 0 or nx >= size or ny < 0 or ny >= size:
                continue
            cell = nx + ny * size
            if known[cell] != -2 and known[cell] != -3:
                continue
            z = get_pos_z(direction)
            if z < depth - 1:
                return True, facts, {}, []
            if z == depth - 1 and get_ground_type(direction) == Grounds.Soot:
                number = measure(direction)
                if number == None:
                    return True, facts, {}, []
                facts[cell] = number
        if not move(North):
            return True, facts, {}, []
    marks, constraints = dynamite_plan(known, facts, x, size)
    return False, facts, marks, constraints


def dynamite_plan(known, facts, x, size):
    # 每次证明只使用同一份快照及本批真实数字，不在证明过程中改写约束基数。
    view = known[:]
    for cell in facts:
        view[cell] = facts[cell]
    marks = {}
    rows = []
    constraints = []
    for y in range(size):
        for cx in range(x, min(x + 2, size)):
            clue = cx + y * size
            if view[clue] < 0:
                continue
            remaining = view[clue]
            unknown = set()
            for other in dynamite_neighbors(clue, size):
                if view[other] == -1:
                    remaining -= 1
                elif view[other] == -2:
                    unknown.add(other)
            if remaining < 0 or remaining > len(unknown):
                continue
            if remaining == 0 or remaining == len(unknown):
                value = -1
                if remaining == 0:
                    value = -3
                for cell in unknown:
                    marks[cell] = value
            else:
                rows.append((unknown, remaining, y))
                constraints.append((unknown, remaining))
    # 两列窗口内只比较纵向相距至多两格的数字，覆盖实际可共享未知格的约束。
    for first in range(len(rows)):
        for second in range(first + 1, len(rows)):
            if rows[second][2] - rows[first][2] > 2:
                break
            small, a, unused = rows[first]
            large, b, unused = rows[second]
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
                if cell not in small:
                    difference.append(cell)
            remaining = b - a
            if len(difference) > 0 and (remaining == 0 or remaining == len(difference)):
                value = -1
                if remaining == 0:
                    value = -3
                for cell in difference:
                    marks[cell] = value
    return marks, constraints


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
