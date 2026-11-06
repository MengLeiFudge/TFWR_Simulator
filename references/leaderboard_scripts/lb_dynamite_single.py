from __builtins__ import *
# 完整轮时间：1437.266秒（构建26462009，6轮官方完整统计；请求351）。

def lb_dynamite_single():
    began = get_time()
    size = get_world_size()
    for cycle in range(512):
        if num_items(Items.Dynamite) >= 100000:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        clear()
        if not move_to(1, 1, size):
            return
        covers = 0
        while get_ground_type() != Grounds.Dynamite:
            if covers >= 256 or get_time() - began > 14400 or not dig():
                quick_print("dynamite_failed", "find_stratum", cycle)
                return
            covers += 1
        depth = get_pos_z()
        if not prepare_all(size, depth):
            quick_print("dynamite_failed", "prepare", cycle)
            return
        before = num_items(Items.Dynamite)
        result, guesses = dynamite_solve(size, depth)
        quick_print("dynamite_cycle", cycle, result, guesses, num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite))
        if result == "error":
            return
    quick_print("dynamite_failed", "cycle_limit", get_time(), num_items(Items.Dynamite))


def dynamite_solve(size, depth):
    # 数字由唯一协调机合并；推理停滞才猜，猜测不写成已证明SAFE事实。
    status, number = dig_target(1 + size, size, depth)
    if status != "number":
        return status, 0
    facts = {1 + size: number}
    status = "waiting"
    for guesses in range(33):
        if status == "waiting" or status == "incomplete":
            status, facts = worker(size, (0, size - 1, 0, size - 1), depth, facts, False)
        if status == "ended":
            return status, guesses
        if status == "done":
            # 所有未挖格均已证明为雷后，挖已揭开的Soot完成一次人工结算。
            for cell in facts:
                if facts[cell] >= 0 and move_to(cell % size, cell // size, size):
                    if get_ground_type() == Grounds.Soot and dig():
                        return "settled", guesses
            return "error", guesses
        if status == "mine":
            for _ in range(4):
                if get_entity_type() != Entities.Dynamite:
                    break
                do_a_flip()
            return "mine", guesses
        if status == "error" and get_pos_z() < depth - 1:
            quick_print("dynamite_board_changed", guesses, get_pos_z(), get_ground_type())
            return "board_changed", guesses
        if status == "error" or guesses == 32:
            return "error", guesses
        choice = dynamite_guess(facts, size)
        if choice == None:
            return "error", guesses
        status, number = dig_target(choice, size, depth)
        if status == "mine":
            for _ in range(4):
                if get_entity_type() != Entities.Dynamite:
                    break
                do_a_flip()
            return "mine", guesses + 1
        if status == "ended":
            return status, guesses + 1
        if status != "number":
            if get_pos_z() < depth - 1:
                quick_print("dynamite_board_changed", guesses + 1, get_pos_z(), get_ground_type())
                return "board_changed", guesses + 1
            return "error", guesses + 1
        facts[choice] = number
        status = "waiting"
    return "error", 32


def dynamite_guess(facts, size):
    # 取相邻公开约束中最大的剩余雷比例作风险启发式，不声称独立概率。
    best = None
    best_risk = 2
    for cell in range(size * size):
        if cell in facts:
            if facts[cell] == SAFE:
                return cell
            continue
        risk = -1
        for clue in adjacent_cells(size, cell):
            if clue not in facts or facts[clue] < 0:
                continue
            remaining = facts[clue]
            unknown = 0
            for other in adjacent_cells(size, clue):
                if other not in facts:
                    unknown += 1
                elif facts[other] == MINE:
                    remaining -= 1
            if unknown > 0:
                risk = max(risk, remaining / unknown)
        if risk < 0:
            risk = 0.5
        if risk < best_risk:
            best = cell
            best_risk = risk
    return best


def prepare_all(size, depth):
    handles = []
    ok = True
    for x in range(size):
        if num_drones() < max_drones():
            handle = spawn_drone(prepare_column, x, size, depth)
            if handle != None:
                handles.append(handle)
                continue
        if not prepare_column(x, size, depth):
            ok = False
            break
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def prepare_column(x, size, depth):
    if not move_to(x, 0, size):
        return False
    for row in range(size):
        while get_pos_z() > depth:
            if not dig():
                return False
        if get_pos_z() != depth or get_ground_type() != Grounds.Dynamite:
            return False
        if row < size - 1 and not move(North):
            return False
    return True


# 只交回窗口内已证明的事实；窗口外的辅助约束变量不导出。


# 交接只携带接收区域8×12内的数字/SAFE/MINE，不传全图棋盘。


def finish_region(board, status):
    facts = {}
    size = board["size"]
    left, right, bottom, top = board["info"]
    for y in range(bottom, top + 1):
        for x in range(left, right + 1):
            cell = x + y * size
            if board["cells"][cell] != UNKNOWN:
                facts[cell] = board["cells"][cell]
    return status, facts


# 数字的八邻域不环绕；栈末端优先四邻方向。
def adjacent_cells(size, cell):
    x = cell % size
    y = cell // size
    diagonal = []
    adjacent = []
    for ny in range(max(0, y - 1), min(size, y + 2)):
        for nx in range(max(0, x - 1), min(size, x + 2)):
            if nx == x and ny == y:
                continue
            other = nx + ny * size
            if nx == x or ny == y:
                adjacent.append(other)
            else:
                diagonal.append(other)
    return diagonal + adjacent


def build_board(size):
    cells = []
    for cell in range(size * size):
        cells.append(UNKNOWN)
    return {"size": size, "cells": cells, "owned": set(), "sampled": set(),
            "neighbors": {}, "tasks": {}, "tops": [None, None, None],
            "versions": {}, "checked": {}, "constraints": {}, "closed": set(),
            "ending": None}


# 三个独立LIFO，每格每类最多一个节点：[更早任务, 较新任务, 版本]。
def remove_task(board, key):
    tasks = board["tasks"]
    if key not in tasks:
        return
    older, newer, version = tasks.pop(key)
    if older != None:
        tasks[older][1] = newer
    if newer != None:
        tasks[newer][0] = older
    else:
        board["tops"][key % 3] = older


def push_task(board, kind, cell, version):
    tasks = board["tasks"]
    key = cell * 3 + kind
    if key in tasks:
        if board["tops"][kind] == key:
            tasks[key][2] = version
            return
        remove_task(board, key)
    older = board["tops"][kind]
    tasks[key] = [older, None, version]
    if older != None:
        tasks[older][1] = key
    board["tops"][kind] = key


# 只执行本区开挖任务，数字约束允许跨区；零扩展始终先于推理。
def next_kind(board):
    for kind in range(3):
        while board["tops"][kind] != None:
            key = board["tops"][kind]
            cell = key // 3
            valid = False
            if kind == CLUE_TASK:
                valid = cell not in board["closed"] and board["tasks"][key][2] == board["versions"][cell]
            else:
                valid = cell in board["owned"] and board["cells"][cell] == SAFE
            if valid:
                return kind
            remove_task(board, key)
    return None


def neighbors(board, cell):
    if cell not in board["neighbors"]:
        board["neighbors"][cell] = adjacent_cells(board["size"], cell)
    return board["neighbors"][cell]


def queue_clue(board, clue):
    if clue in board["closed"]:
        return
    version = 0
    if clue in board["versions"]:
        version = board["versions"][clue] + 1
    board["versions"][clue] = version
    push_task(board, CLUE_TASK, clue, version)


def queue_clues(board, cell):
    for clue in neighbors(board, cell):
        if board["cells"][clue] >= 0:
            queue_clue(board, clue)


# SAFE可从普通开挖提升到零扩展；不允许后来的普通任务降低已有优先级。
def queue_open(board, cell, kind):
    if cell not in board["owned"]:
        return
    if kind == ZERO_TASK:
        remove_task(board, cell * 3 + OPEN_TASK)
        push_task(board, ZERO_TASK, cell, 0)
    elif cell * 3 + ZERO_TASK not in board["tasks"]:
        push_task(board, OPEN_TASK, cell, 0)


def mark_cells(board, targets, value, priority):
    cells = board["cells"]
    for cell in targets:
        previous = cells[cell]
        if previous >= 0 and value == SAFE:
            continue
        if previous != value:
            if previous != UNKNOWN:
                quick_print("格子推断冲突：", cell % board["size"], cell // board["size"])
                return False
            cells[cell] = value
            if value == MINE:
                if cell in board["owned"]:
                    board["owned"].remove(cell)
            queue_clues(board, cell)
        if value == SAFE:
            queue_open(board, cell, priority)
    return True


# 本区及跨区读数统一走这里；只更新任务，不在读数期间运行infer。
def record_number(board, cell, number):
    previous = board["cells"][cell]
    if previous == number:
        return True
    if previous == MINE or previous >= 0:
        quick_print("现场数字与记录冲突：", cell % board["size"], cell // board["size"])
        return False
    board["cells"][cell] = number
    if cell in board["owned"]:
        board["owned"].remove(cell)
    remove_task(board, cell * 3 + ZERO_TASK)
    remove_task(board, cell * 3 + OPEN_TASK)
    queue_clue(board, cell)
    if previous == UNKNOWN:
        queue_clues(board, cell)
    around = neighbors(board, cell)
    if number == 0:
        if not mark_cells(board, around, SAFE, ZERO_TASK):
            return False
        board["closed"].add(cell)
        remove_task(board, cell * 3 + CLUE_TASK)
    return True


def constraint(board, clue):
    version = board["versions"][clue]
    if clue in board["constraints"]:
        cached = board["constraints"][clue]
        if cached[0] == version:
            return cached[1], cached[2]
    remaining = board["cells"][clue]
    unknown = set()
    for cell in neighbors(board, clue):
        if board["cells"][cell] == MINE:
            remaining -= 1
        elif board["cells"][cell] == UNKNOWN:
            unknown.add(cell)
    if remaining < 0 or remaining > len(unknown):
        quick_print("数字约束矛盾：", clue % board["size"], clue // board["size"])
        return None
    board["constraints"][clue] = (version, unknown, remaining)
    return unknown, remaining


# A包含于B时，B-A的实弹数等于两者剩余实弹数之差。
def infer_subset(board, first, second):
    a = constraint(board, first)
    b = constraint(board, second)
    if a == None or b == None:
        return None
    small, small_count = a
    large, large_count = b
    if len(small) > len(large):
        small, large = large, small
        small_count, large_count = large_count, small_count
    for cell in small:
        if cell not in large:
            return False
    difference = []
    for cell in large:
        if cell not in small:
            difference.append(cell)
    remaining = large_count - small_count
    if remaining < 0 or remaining > len(difference):
        return None
    if len(difference) == 0:
        return False
    if remaining == 0:
        if not mark_cells(board, difference, SAFE, OPEN_TASK):
            return None
        return True
    if remaining == len(difference):
        if not mark_cells(board, difference, MINE, OPEN_TASK):
            return None
        return True
    return False


# 只由最低优先级任务调用；每次判断一个数字及共享未知格的附近数字。
def infer(board, clue):
    if clue in board["closed"]:
        return True
    version = board["versions"][clue]
    if clue in board["checked"] and board["checked"][clue] == version:
        remove_task(board, clue * 3 + CLUE_TASK)
        return True
    row = constraint(board, clue)
    if row == None:
        return False
    unknown, remaining = row
    if remaining == 0 or remaining == len(unknown):
        value = MINE
        if remaining == 0:
            value = SAFE
        if not mark_cells(board, unknown, value, OPEN_TASK):
            return False
        board["closed"].add(clue)
        remove_task(board, clue * 3 + CLUE_TASK)
        return True
    peers = set()
    for cell in unknown:
        for other in neighbors(board, cell):
            if other != clue and board["cells"][other] >= 0 and other not in board["closed"]:
                peers.add(other)
    push_task(board, CLUE_TASK, clue, version)
    for other in peers:
        changed = infer_subset(board, clue, other)
        if changed == None:
            return False
        if changed:
            return True
    board["checked"][clue] = version
    remove_task(board, clue * 3 + CLUE_TASK)
    return True


# 每台使用相同求解器；初次到位后，移动和读取均由各自窗口限制。
def worker(size, area, depth, facts, await_start):
    if await_start:
        until = get_tick_count() + 100000
        while get_pos_z() == depth:
            if get_tick_count() >= until:
                return "error", {}
    x0, x1, y0, y1 = area
    board = build_board(size)
    travel = (max(0, x0 - 1), min(size - 1, x1 + 1), max(0, y0 - 1), min(size - 1, y1 + 1))
    board["travel"] = travel
    board["info"] = (max(0, x0 - 2), min(size - 1, x1 + 2), max(0, y0 - 2), min(size - 1, y1 + 2))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            board["owned"].add(x + y * size)
    for cell in facts:
        value = facts[cell]
        if value >= 0:
            if not record_number(board, cell, value):
                return "error", {}
        elif not mark_cells(board, [cell], value, OPEN_TASK):
            return "error", {}
    seed = 1 + size
    if get_pos_x() == 1 and get_pos_y() == 1 and inside(seed, size, board["info"]):
        status, first_number = read_ground(depth)
        if status != "number":
            return status, {}
        if not record_number(board, seed, first_number):
            return "error", {}
    # 每次启动仅部署一次；求解期间禁止用环绕捷径离开自己的活动区。
    if not move_to(max(travel[0], min(travel[1], get_pos_x())),
                   max(travel[2], min(travel[3], get_pos_y())), size):
        return "error", {}
    probes = []
    for y in range(travel[2], travel[3] + 1):
        if (y - travel[2]) % 2 == 0:
            for x in range(travel[0], travel[1] + 1):
                probes.append(x + y * size)
        else:
            for x in range(travel[1], travel[0] - 1, -1):
                probes.append(x + y * size)
    # 四向读取缺少最外斜角，临时从活动区角点沿y跨一步，再横向读取。
    for y in [travel[2] - 1, travel[3] + 1]:
        if y < board["info"][2] or y > board["info"][3]:
            continue
        for x in [travel[0], travel[1]]:
            probes.append(x + y * size)
    probe_at = 0
    scan_epoch = num_items(Items.Dynamite)
    while board["ending"] == None and len(board["owned"]) > 0:
        kind = next_kind(board)
        if kind != None:
            key = board["tops"][kind]
            cell = key // 3
            remove_task(board, key)
            if kind == CLUE_TASK:
                if not infer(board, cell):
                    board["ending"] = "error"
            else:
                if not open_cell(board, cell, depth) and board["ending"] == None:
                    board["ending"] = "error"
            continue
        if probe_at < len(probes):
            cell = probes[probe_at]
            if not probe_needed(board, cell):
                probe_at += 1
                continue
            if not visit_cell(board, cell, depth):
                board["ending"] = "error"
            # 若观测被零任务抢占，保留游标，之后补读这个点剩余的方向。
            continue
        epoch = num_items(Items.Dynamite)
        if epoch != scan_epoch:
            scan_epoch = epoch
            board["sampled"] = set()
            probe_at = 0
            continue
        result, unused = audit_constraints(board, epoch)
        if result == "changed" or result == "stale":
            continue
        if result == "error":
            board["ending"] = "error"
            continue
        if result == "incomplete":
            quick_print("区域", x0, y0, "局部核对达到预算，交回已知事实。")
        return finish_region(board, result)
    if board["ending"] != None:
        return finish_region(board, board["ending"])
    quick_print("区域", x0, y0, "已处理完。")
    return finish_region(board, "done")


# 窗口坐标为包含两端的(left, right, bottom, top)，不跨世界边界环绕。
def inside(cell, size, bounds):
    x = cell % size
    y = cell // size
    return bounds[0] <= x and x <= bounds[1] and bounds[2] <= y and y <= bounds[3]


# 判断脚下及四向是否仍有本轮信息未读，不能仅因脚下数字已知就跳过邻居。
def probe_needed(board, cell):
    size = board["size"]
    x = cell % size
    y = cell // size
    for dx, dy in [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx = x + dx
        ny = y + dy
        if nx < 0 or nx >= size or ny < 0 or ny >= size:
            continue
        other = nx + ny * size
        if not inside(other, size, board["info"]) or other in board["sampled"]:
            continue
        if board["cells"][other] == UNKNOWN or board["cells"][other] == SAFE:
            return True
    return False


# 仅枚举关联本区未决格的分量；其余边缘约束不消耗枚举预算。
# 外部未知格仍是约束变量，但不会因此扩大实际读取或移动范围。
def audit_constraints(board, epoch):
    rows = []
    links = {}
    for clue in board["versions"]:
        if clue in board["closed"]:
            continue
        row = constraint(board, clue)
        if row == None:
            return "error", None
        targets, count = row
        if len(targets) == 0:
            continue
        index = len(rows)
        rows.append((targets, count))
        for cell in targets:
            if cell not in links:
                links[cell] = []
            links[cell].append(index)
    pending = set(links)
    deadline = get_tick_count() + ENUM_TICKS
    while len(pending) > 0:
        first = None
        for cell in board["owned"]:
            if cell in pending:
                first = cell
                break
        if first == None:
            break
        todo = [first]
        pending.remove(first)
        order = []
        row_ids = set()
        while len(todo) > 0:
            cell = todo.pop()
            order.append(cell)
            for index in links[cell]:
                if index in row_ids:
                    continue
                row_ids.add(index)
                for other in rows[index][0]:
                    if other in pending:
                        pending.remove(other)
                        todo.append(other)
        if num_items(Items.Dynamite) != epoch:
            return "stale", None
        if len(order) > ENUM_CELLS or get_tick_count() >= deadline:
            return "incomplete", None
        left = {}
        need = {}
        for index in row_ids:
            left[index] = len(rows[index][0])
            need[index] = rows[index][1]
        values = []
        seen = []
        for cell in order:
            values.append(0)
            seen.append(0)
        search = {"order": order, "links": links, "left": left, "need": need,
                  "values": values, "seen": seen, "both": 0, "solutions": 0,
                  "nodes": 0, "stop": None, "deadline": deadline, "epoch": epoch}
        enumerate_layouts(search, 0)
        if search["stop"] == "stale":
            return "stale", None
        if search["stop"] == "incomplete":
            return "incomplete", None
        if search["solutions"] == 0:
            return "error", None
        changed = False
        for i in range(len(order)):
            if seen[i] == 1 or seen[i] == 2:
                value = SAFE
                if seen[i] == 2:
                    value = MINE
                if not mark_cells(board, [order[i]], value, OPEN_TASK):
                    return "error", None
                changed = True
        if changed:
            return "changed", None
    if num_items(Items.Dynamite) != epoch:
        return "stale", None
    return "waiting", None


# 深度优先枚举可满足布局，维护各数字的剩余格数和剩余雷数以即时剪枝。
def enumerate_layouts(search, at):
    if search["stop"] != None:
        return
    search["nodes"] += 1
    if search["nodes"] % 64 == 0:
        if num_items(Items.Dynamite) != search["epoch"]:
            search["stop"] = "stale"
            return
        if search["nodes"] >= ENUM_NODES or get_tick_count() >= search["deadline"]:
            search["stop"] = "incomplete"
            return
    if search["nodes"] % 512 == 0:
        quick_print("停滞约束核对：", len(search["order"]), "格，节点", search["nodes"])
    if at == len(search["order"]):
        search["solutions"] += 1
        for i in range(at):
            value = search["values"][i] + 1
            if search["seen"][i] == 0:
                search["seen"][i] = value
            elif search["seen"][i] != 3 and search["seen"][i] != value:
                search["seen"][i] = 3
                search["both"] += 1
        if search["both"] == at:
            search["stop"] = "ambiguous"
        return
    cell = search["order"][at]
    for value in [0, 1]:
        search["values"][at] = value
        valid = True
        for index in search["links"][cell]:
            search["left"][index] -= 1
            search["need"][index] -= value
            if search["need"][index] < 0 or search["need"][index] > search["left"][index]:
                valid = False
        if valid:
            enumerate_layouts(search, at + 1)
        for index in search["links"][cell]:
            search["left"][index] += 1
            search["need"][index] += value
        if search["stop"] != None:
            return


# 返回closed/number/ended/mine/error；只把实际数字交给求解器。
def read_ground(depth, direction=None):
    z = get_pos_z(direction)
    if z >= depth:
        return "closed", None
    if z != depth - 1 or get_ground_type(direction) != Grounds.Soot:
        return "error", None
    if get_entity_type(direction) == Entities.Dynamite:
        return "mine", None
    number = measure(direction)
    if number == None:
        return "ended", None
    if number < 0 or number > 8:
        return "error", None
    return "number", number


# 调用者必须持有该格的唯一开挖权；检查地层只负责防止跨层，不充当并发锁。
def dig_target(cell, size, depth):
    if not move_to(cell % size, cell // size, size):
        return "error", None
    z = get_pos_z()
    if z == depth:
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    elif z != depth - 1:
        return "error", None
    return read_ground(depth)


def read_cell(board, cell, direction, depth):
    if not inside(cell, board["size"], board["info"]):
        return True
    if board["cells"][cell] >= 0 or board["cells"][cell] == MINE or cell in board["sampled"]:
        return True
    status, number = read_ground(depth, direction)
    board["sampled"].add(cell)
    if status == "closed":
        return True
    if status != "number":
        board["ending"] = status
        return status == "ended"
    return record_number(board, cell, number)


# 读取脚下及四邻；一旦已有零扩展任务就立即让回开挖循环。
def observe(board, depth):
    size = board["size"]
    x = get_pos_x()
    y = get_pos_y()
    cell = x + y * size
    if not read_cell(board, cell, None, depth):
        return False
    for dx, dy, direction in [(0, 1, North), (1, 0, East), (0, -1, South), (-1, 0, West)]:
        if board["ending"] != None or next_kind(board) == ZERO_TASK:
            return True
        nx = x + dx
        ny = y + dy
        if nx >= 0 and nx < size and ny >= 0 and ny < size:
            if not read_cell(board, nx + ny * size, direction, depth):
                return False
    return True


def open_cell(board, cell, depth):
    if cell not in board["owned"]:
        return False
    if board["cells"][cell] != SAFE and board["cells"][cell] != UNKNOWN:
        return False
    if not move_local(board, cell):
        return False
    status, number = dig_target(cell, board["size"], depth)
    if status != "number":
        board["ending"] = status
        return status == "ended"
    if not record_number(board, cell, number):
        return False
    if next_kind(board) == ZERO_TASK:
        return True
    return observe(board, depth)


# 角点短暂外跨读完立即退回；普通观测点留在6×10活动区内。
def visit_cell(board, cell, depth):
    if not move_local(board, cell):
        return False
    ok = observe(board, depth)
    travel = board["travel"]
    x = get_pos_x()
    y = get_pos_y()
    if y < travel[2] or y > travel[3]:
        if not move_direct(x, max(travel[2], min(travel[3], y))):
            return False
    return ok


# 开挖/读取共用移动入口，只允许活动矩形和四个角点的单步外跨位置。
def move_local(board, cell):
    size = board["size"]
    travel = board["travel"]
    tx = cell % size
    ty = cell // size
    if not inside(cell, size, travel):
        if not inside(cell, size, board["info"]):
            return False
        if (tx != travel[0] and tx != travel[1]) or (ty != travel[2] - 1 and ty != travel[3] + 1):
            return False
    x = get_pos_x()
    y = get_pos_y()
    if x < travel[0] or x > travel[1]:
        return False
    if y < travel[2] or y > travel[3]:
        if not move_direct(x, max(travel[2], min(travel[3], y))):
            return False
    ay = max(travel[2], min(travel[3], ty))
    if not move_direct(tx, ay):
        return False
    if ay != ty:
        return move_direct(tx, ty)
    return True


# 矩形内部用直接路径，避免环绕捷径经过其他区域。
def move_direct(tx, ty):
    dx = tx - get_pos_x()
    dy = ty - get_pos_y()
    horizontal = East
    vertical = North
    if dx < 0:
        horizontal = West
    if dy < 0:
        vertical = South
    for _ in range(abs(dx)):
        if not move(horizontal):
            return False
    for _ in range(abs(dy)):
        if not move(vertical):
            return False
    return True


# 仅用于覆盖层准备、首次部署，以及已由move_local到位后的原地dig。
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


REGION_WIDTH = 4
REGION_HEIGHT = 8
UNKNOWN = -2
MINE = -1
SAFE = -3
ZERO_TASK = 0
OPEN_TASK = 1
CLUE_TASK = 2
ENUM_CELLS = 24
ENUM_NODES = 4096
ENUM_TICKS = 12000


if __name__ == "__main__":
    lb_dynamite_single()
