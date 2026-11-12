from __builtins__ import *
# 淘汰候选归档：lb_ores | 原实验路径 .codex/underground-efficiency-20261108/candidates/ores-targeted/lb_ores.py

def lb_ores():
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 7200
    empty = 0
    for cycle in range(512):
        if num_items(Items.Quartz) >= 20000:
            quick_print("ores_done", True, get_time(), num_items(Items.Quartz))
            return
        clear()
        before = num_items(Items.Quartz)
        if num_items(Items.Iron) >= 3:
            handles = []
            ok = True
            groups = min(8, max_drones(), size // 4)
            for owner in range(1, groups):
                handle = spawn_drone(ore_target_patch, owner, groups, size, 20000, deadline)
                if handle == None:
                    ok = False
                    break
                handles.append(handle)
            if not ore_target_patch(0, groups, size, 20000, deadline):
                ok = False
            for handle in handles:
                if not wait_for(handle):
                    ok = False
            quick_print("ores_targeted", cycle, ok, num_items(Items.Quartz) - before, get_time(), num_items(Items.Iron))
            if not ok:
                return
            if num_items(Items.Quartz) >= 20000:
                continue
        handles = []
        local = True
        for owner in range(1, workers):
            handle = spawn_drone(ore_trench, owner, workers, size, 20000, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not ore_trench(0, workers, size, 20000, deadline):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        gained = num_items(Items.Quartz) - before
        quick_print("ores_cycle", cycle, local, gained, get_time(), num_items(Items.Quartz))
        if not local:
            quick_print("ores_failed", "cycle", cycle)
            return
        if gained == 0:
            empty += 1
            if empty >= 8:
                quick_print("ores_failed", "eight_empty_cycles")
                return
        else:
            empty = 0
    quick_print("ores_failed", "cycle_limit", get_time(), num_items(Items.Quartz))


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



def ore_target_patch(owner, groups, size, goal, deadline):
    left = owner * size // groups
    right = (owner + 1) * size // groups
    ax = left + 1
    for ay in range(1, size - 1, 4):
        if num_items(Items.Quartz) >= goal or num_items(Items.Iron) < 3:
            return True
        anchors = [(ax, ay), (ax + 1, ay), (ax, ay + 1)]
        for x, y in anchors:
            if not ore_prepare(x, y, -31, size, deadline):
                return False
        samples = []
        for x, y in anchors:
            if not ore_move_to(x, y, size):
                return False
            distance = prospect_quartz()
            if distance == None:
                return True
            samples.append((x, y, get_pos_z(), distance))
        point = ore_locate(samples, size, left, right)
        if point == None:
            continue
        if not ore_move_to(point[0], point[1], size):
            return False
        found = False
        for step in range(48):
            if num_items(Items.Quartz) >= goal:
                return True
            if get_time() > deadline:
                return False
            ground = get_ground_type()
            if ground == Grounds.Quartz:
                if not dig():
                    return False
                found = True
            elif found or get_pos_z() < point[2]:
                break
            elif not dig():
                return False
    return True


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


def ore_locate(samples, size, left, right):
    # 第一读数规定球面，其他最近距离只规定球内无矿，并不保证也是同一矿块。
    # 在合法剩余候选中选总距离残差最小者；到达后仍靠实际Quartz验证，错误就回退。
    x0, y0, z0, d0 = samples[0]
    best = None
    best_score = 10000000
    for x in range(left, right):
        for y in range(size):
            square = d0 * d0 - (x - x0) ** 2 - (y - y0) ** 2
            if square < 0:
                continue
            dz = (square ** 0.5 + 0.5) // 1
            if abs(dz * dz - square) > 0.01:
                continue
            for z in [z0 - dz, z0 + dz]:
                if z > -32 or z < -47:
                    continue
                score = 0
                valid = True
                for sx, sy, sz, distance in samples:
                    residual = (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2 - distance * distance
                    if residual < -0.01 or (x == sx and y == sy and z > sz):
                        valid = False
                        break
                    score += residual
                if valid and score < best_score:
                    best = (x, y, z)
                    best_score = score
    return best


if __name__ == "__main__":
    lb_ores()
