from __builtins__ import *
# 淘汰候选归档：lb_ores_single | 原实验路径 .codex/leaderboard-sol/underground-official/ores_single/prospect-funded-candidate/lb_ores_single.py


def lb_ores_single():
    size = get_world_size()
    deadline = get_time() + 7200
    for cycle in range(128):
        if num_items(Items.Quartz) >= 4000:
            quick_print("ores_done", True, get_time(), num_items(Items.Quartz))
            return
        if num_items(Items.Iron) < 24 and not ore_fund(96, size, deadline):
            quick_print("ores_failed", "fund", cycle, get_time())
            return
        clear()
        before = num_items(Items.Quartz)
        # 在首层石英上方建立三个相邻锚点；全部准备结束后才读取距离。
        for x, y in [(0, 0), (1, 0), (0, 1)]:
            if not ore_prepare(x, y, -31, size, deadline):
                return
        fallback = False
        for attempt in range(8):
            if num_items(Items.Quartz) >= 4000:
                break
            if num_items(Items.Iron) < 3:
                fallback = True
                break
            samples = []
            for x, y in [(0, 0), (1, 0), (0, 1)]:
                if not ore_move_to(x, y, size):
                    return
                distance = prospect_quartz()
                if distance == None:
                    break
                samples.append((x, y, get_pos_z(), distance))
            if len(samples) != 3:
                break
            point = ore_locate(samples, size)
            if point == None:
                fallback = True
                break
            if not ore_move_to(point[0], point[1], size):
                return
            found = False
            for _ in range(48):
                if num_items(Items.Quartz) >= 4000:
                    break
                if get_time() > deadline:
                    return
                ground = get_ground_type()
                if ground == Grounds.Quartz:
                    if not dig():
                        return
                    found = True
                    continue
                if found or get_pos_z() < point[2]:
                    break
                if not dig():
                    return
            if not found:
                fallback = True
                break
        if fallback and not ore_trench(0, 1, size, 4000, deadline):
            return
        quick_print("ores_cycle", cycle, fallback, num_items(Items.Quartz) - before,
                    get_time(), num_items(Items.Quartz), num_items(Items.Iron))
    quick_print("ores_failed", "cycle_limit", get_time())


def ore_fund(goal, size, deadline):
    # 煤支付铁的方向勘探，铁支付石英距离；筹资只发生在新地图开始之前。
    for cycle in range(64):
        if num_items(Items.Iron) >= goal:
            return True
        if get_time() > deadline:
            return False
        clear()
        if not ore_prepare(0, 0, -16, size, deadline):
            return False
        if num_items(Items.Coal) < 2 * size + 1:
            continue
        for _ in range(2 * size + 1):
            direction = prospect_iron()
            if direction == None:
                break
            if not move(direction):
                return False
        found = False
        for _ in range(33):
            if num_items(Items.Iron) >= goal:
                return True
            if get_time() > deadline:
                return False
            if get_ground_type() == Grounds.Iron:
                if not dig():
                    return False
                found = True
            elif found or get_pos_z() <= -32:
                break
            elif not dig():
                return False
        quick_print("ores_fund", cycle, num_items(Items.Coal), num_items(Items.Iron), get_time())
    return False


def ore_prepare(x, y, depth, size, deadline):
    # 实际挖至锚点；之后取样会重读塌方改变的高度，不缓存开挖前的距离。
    if not ore_move_to(x, y, size):
        return False
    for _ in range(48):
        if get_pos_z() <= depth:
            return True
        if get_time() > deadline or not dig():
            return False
    return False


def ore_locate(samples, size):
    # 只枚举公开距离允许的整数坐标；三点的最近矿可能变化，失配就放弃定位。
    x0, y0, z0, d0 = samples[0]
    best = None
    for x in range(size):
        for y in range(size):
            square = d0 * d0 - (x - x0) ** 2 - (y - y0) ** 2
            if square < 0:
                continue
            dz = (square ** 0.5 + 0.5) // 1
            for z in [z0 - dz, z0 + dz]:
                if z > -32 or z < -47:
                    continue
                valid = True
                for sx, sy, sz, distance in samples:
                    residual = (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2 - distance * distance
                    if abs(residual) > 0.01:
                        valid = False
                        break
                    if x == sx and y == sy and z > sz:
                        valid = False
                        break
                if valid and (best == None or z < best[2]):
                    best = (x, y, z)
    return best


def ore_trench(first, stride, size, goal, deadline):
    # 每个x由唯一工人向North推进；相邻已降低的柱帮助清除覆盖层。
    # 只按公开高度和地面采掘，收益仅取实际dig库存，不把塌掉的矿计入产量。
    for x in range(first, size, stride):
        if not ore_move_to(x, 0, size):
            return False
        for y in range(size):
            while get_pos_z() > -39:
                if num_items(Items.Quartz) >= goal:
                    return True
                if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                    return False
            while get_ground_type() == Grounds.Quartz:
                if num_items(Items.Quartz) >= goal:
                    return True
                if get_time() > deadline or not dig():
                    return False
            if y + 1 < size and not move(North):
                return False
    return True


def ore_move_to(tx, ty, size):
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
    lb_ores_single()
