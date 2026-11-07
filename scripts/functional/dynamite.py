from __builtins__ import *
import farm_support

# 约束传播、子集推理与按列开安全格来自Save0/Dynamite.py。
UNKNOWN = -2
MINE = -1
SAFE = -3
DIG_LIMIT = 2048
GUESS_LIMIT = 32
BATCH_LIMIT = 2048
SUBSET_LIMIT = 4096


def dynamite():
    # 正常结算每盘后继续下挖；不要求Jump或固定科技等级。
    farm_support.run(Items.Dynamite, collect)


def collect(goal):
    # 普通扫雷需要正方形地图，使用公开数字推理并允许正常猜测风险。
    if not farm_support.require(Unlocks.Dynamite) or not farm_support.require(Unlocks.Mining):
        return False
    if not farm_support.require(Unlocks.Underground_Senses):
        return False
    width, size = farm_support.dimensions()
    if width != size or size < 2:
        quick_print("炸药采集需要至少2×2的正方形农场。")
        return False
    clear()
    adjacent = []
    for cell in range(size * size):
        adjacent.append(neighbors(cell, size))
    empty = 0
    while num_items(Items.Dynamite) < goal:
        before = num_items(Items.Dynamite)
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("找不到下一可达炸药层，停止。")
            return False
        depth = get_pos_z()
        if get_ground_type() == Grounds.Soot:
            depth += 1
        status, number = open_ground(depth)
        if status == "number":
            status, guesses = solve(size, depth, adjacent, number)
        if status == "settle" or status == "mine":
            status = settle(size, depth)
        if status != "ended":
            quick_print("炸药地层或求解异常，已回收子机：", status)
            return False
        if num_items(Items.Dynamite) > before:
            empty = 0
        else:
            empty += 1
            if empty >= 8:
                quick_print("连续八盘没有炸药收益，停止。")
                return False
    return True


def find_stratum():
    # 入口由主机独占，避免无人机不足时按槽位轮转的挖掘协议悬空等待。
    for _ in range(DIG_LIMIT):
        ground = get_ground_type()
        if ground == Grounds.Dynamite:
            return True
        if ground == Grounds.Soot and measure() != None:
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
    # 实际结算可返回None，外部Measure类型桩未声明此终态。
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

def solve(size, depth, adjacent, first_number):
    known = []
    for _ in range(size * size):
        known.append(UNKNOWN)
    active = set()
    facts = {(size // 2) * (size + 1): first_number}
    guesses = 0
    for batch in range(BATCH_LIMIT):
        for cell in facts:
            previous = known[cell]
            if previous == MINE or (previous >= 0 and previous != facts[cell]):
                quick_print("扫雷数字冲突：", cell)
                return "error", guesses
            known[cell] = facts[cell]
            active.add(cell)
        # 每次子集推理至少确定一个未知格，故此循环不会反复处理相同状态。
        while True:
            constraints = propagate(known, active, adjacent)
            if constraints == None:
                return "error", guesses
            safe = False
            for cell in range(len(known)):
                if known[cell] == SAFE:
                    safe = True
                    break
            if safe:
                break
            result = infer_subset(known, constraints, adjacent)
            if result == "error":
                return "error", guesses
            if result != "changed":
                break
        if safe:
            # 零扩展可沿已知零格的安全邻域逐批读全，无须巡查整盘未知格。
            status, facts = run_columns(size, depth, known)
            if status != "running":
                return status, guesses
            continue
        choice = choose_guess(known, constraints)
        if choice == None or guesses >= GUESS_LIMIT:
            return "settle", guesses
        if not move_to(choice % size, choice // size, size):
            return "error", guesses
        status, number = open_ground(depth)
        guesses += 1
        if status != "number":
            return status, guesses
        facts = {choice: number}
    return "settle", guesses

def propagate(known, active, adjacent):
    pending = []
    queued = set()
    constraints = {}
    for clue in active:
        pending.append(clue)
        queued.add(clue)
    while len(pending) > 0:
        clue = pending.pop()
        queued.remove(clue)
        if clue not in active:
            continue
        remaining = known[clue]
        unknown = set()
        for cell in adjacent[clue]:
            if known[cell] == MINE:
                remaining -= 1
            elif known[cell] == UNKNOWN:
                unknown.add(cell)
        if remaining < 0 or remaining > len(unknown):
            quick_print("扫雷约束冲突：", clue)
            return None
        if remaining != 0 and remaining != len(unknown):
            constraints[clue] = (unknown, remaining)
            continue
        active.remove(clue)
        if clue in constraints:
            constraints.pop(clue)
        value = MINE
        if remaining == 0:
            value = SAFE
        for cell in unknown:
            known[cell] = value
            for other in adjacent[cell]:
                if other in active and other not in queued:
                    pending.append(other)
                    queued.add(other)
    return constraints

def infer_subset(known, constraints, adjacent):
    checked = 0
    for first in constraints:
        peers = set()
        for cell in constraints[first][0]:
            for second in adjacent[cell]:
                if second > first and second in constraints:
                    peers.add(second)
        for second in peers:
            checked += 1
            if checked > SUBSET_LIMIT:
                return "unchanged"
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
                if cell not in small:
                    difference.append(cell)
            remaining = b - a
            if remaining < 0 or remaining > len(difference):
                quick_print("扫雷子集约束冲突：", first, second)
                return "error"
            if len(difference) > 0 and (remaining == 0 or remaining == len(difference)):
                value = MINE
                if remaining == 0:
                    value = SAFE
                for cell in difference:
                    known[cell] = value
                return "changed"
    return "unchanged"

def choose_guess(known, constraints):
    risks = {}
    for clue in constraints:
        cells, count = constraints[clue]
        risk = count / len(cells)
        for cell in cells:
            if cell not in risks or risk > risks[cell]:
                risks[cell] = risk
    best = None
    least = 2
    for cell in range(len(known)):
        if known[cell] != UNKNOWN:
            continue
        risk = 0.5
        if cell in risks:
            risk = risks[cell]
        if risk < least:
            best = cell
            least = risk
    return best

def run_columns(size, depth, known):
    handles = []
    results = []
    for x in range(size):
        targets = []
        for y in range(size):
            cell = x + y * size
            if known[cell] == SAFE:
                targets.append(cell)
        if len(targets) == 0:
            continue
        if farm_support.capacity() > 1 and num_drones() < farm_support.capacity():
            handle = spawn_drone(work_column, targets, size, depth)
            if handle != None:
                handles.append(handle)
                continue
        results.append(work_column(targets, size, depth))
    for handle in handles:
        results.append(wait_for(handle))
    status = "running"
    facts = {}
    for result in results:
        if result == None:
            status = "error"
            continue
        if result[0] == "error":
            status = "error"
        elif result[0] == "mine" and status != "error":
            status = "mine"
        elif result[0] == "ended" and status == "running":
            status = "ended"
        for cell in result[1]:
            if cell in facts and facts[cell] != result[1][cell]:
                quick_print("扫雷观测冲突：", cell)
                status = "error"
            facts[cell] = result[1][cell]
    return status, facts

def work_column(targets, size, depth):
    facts = {}
    for cell in targets:
        if not move_to(cell % size, cell // size, size):
            return "error", facts
        status, number = open_ground(depth)
        if status == "number":
            facts[cell] = number
        else:
            return status, facts
    return "running", facts

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
