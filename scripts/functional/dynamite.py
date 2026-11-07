from __builtins__ import *
import production


# 持续向下采集：主机合并全图公开数字，子机按列开安全格；每盘独立重建缓存。
UNKNOWN = -2
MINE = -1
SAFE = -3
# 沿用地下策略的有限搜层、猜测与批次预算；耗尽搜层预算时报错，求解预算耗尽则结算。
DIG_LIMIT = 2048
GUESS_LIMIT = 32
BATCH_LIMIT = 2048
SUBSET_LIMIT = 4096


# 默认连续运行；有限盘数用于本地模型比较，不改变每盘策略。
def dynamite(round_limit=0):
    started = get_time()
    size = get_world_size()
    if size < 4:
        quick_print("炸药采集需要至少 4×4 的农场。")
        return
    if num_unlocked(Unlocks.Dynamite) < 1 or num_unlocked(Unlocks.Jump) < 1:
        quick_print("请先解锁炸药和 Jump。")
        return
    if num_drones() != 1:
        quick_print("请在其他无人机结束后启动。")
        return
    adjacent = []
    for cell in range(size * size):
        adjacent.append(neighbors(cell, size))

    initial = num_items(Items.Dynamite)
    change_hat(Hats.Mining_Hat)
    # jump每次执行只能用一次；后续沿当前地层下挖，不clear回地表。
    production.jump_once(Unlocks.Dynamite)
    cycle = 0
    while (round_limit == 0 or cycle < round_limit) and production.active(Items.Dynamite):
        began = get_time()
        before = num_items(Items.Dynamite)
        if not move_to(size // 2, size // 2, size) or not find_stratum():
            quick_print("炸药采集停止：无法到达下一炸药层。", "深度", get_pos_z())
            return
        depth = get_pos_z()
        # 找层工人可能已开入口；煤灰上的数字属于上一格的炸药层。
        if get_ground_type() == Grounds.Soot:
            depth += 1
        prepared = get_time()
        status, number = open_ground(depth)
        guesses = 0
        if status == "number":
            status, guesses = solve(size, depth, adjacent, number)
        # 猜中雷或主动结束时，全部工人已回收；只结算仍有数字表的当前盘。
        if status == "settle" or status == "mine":
            status = settle(size, depth)
        cycle += 1
        now = get_time()
        gained = num_items(Items.Dynamite) - before
        total = num_items(Items.Dynamite) - initial
        quick_print("炸药第", cycle, "盘：", status, "深度", depth,
                    "获得", gained, "准备秒", prepared - began,
                    "求解秒", now - prepared, "猜测", guesses,
                    "累计", total, "累计秒", now - started, "每秒", total / (now - started))
        if status != "ended":
            quick_print("炸药采集停止：地层、动作或数字异常，全部子机已回收。")
            return


# 多机在同一入口下挖；回收全部工人后才开始解盘。
def find_stratum():
    if get_ground_type() == Grounds.Dynamite:
        return True
    if get_ground_type() == Grounds.Soot:
        if measure() != None:
            return True
        # 上一盘全部挖完时仍留下煤灰，由主机先清掉再派找层工人。
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


# 深度唯一决定下刀工人；其余工人不改地形，检查与下刀之间不会被抢挖。
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


# 数字只在同一盘内有效；低于Soot底面或数字表消失均表示该盘已结束。
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


# 只准备实际要开的柱；零扩展可自动清掉其他柱的覆盖层。
# 调用者持有该列唯一开挖权；猜测只在所有子机回收后由主机执行。
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


# 首挖点必已揭开；只挖仍有有效数字的Soot一次，兑现当前盘收益后继续下层。
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


# 主机统一推理，避免相邻分区反复交接；实际数字、确定雷和安全格分别缓存。
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


# 每次状态改变只唤醒相邻数字；队列收敛后所有剩余约束来自同一最新快照。
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


# 只有共享未知格的数字才可能有非空子集关系；省掉全图无关约束两两比较。
# 一旦确定新格便返回，调用者先传播新状态，不能继续使用旧约束猜测。
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


# 风险启发式只选择猜测位置，不作为安全证明；与多机榜保持相同风险口径。
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


# 每个工人只接收本列安全格，不复制全图棋盘；容量不足时主机顺序处理剩余列。
# 所有wait完成后才合并事实、猜测、结算或寻找下一层。
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
        if num_drones() < max_drones():
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


# 按y顺序把开挖与读数合为一趟；已知数字和已确定雷均不回访。
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


# 雷数八邻域不环绕；移动路径可以利用农场边界环绕。
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


# 两轴均走环绕最短路，每次移动保留失败检查。
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
