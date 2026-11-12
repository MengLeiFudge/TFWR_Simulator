from __builtins__ import *
# 历史提交归档：lb_ores | 初次提交 2026-11-06 (effd70d1) | 文档：补齐其余十个地下榜的正式实机基线
# 完整轮时间：867.389秒（构建26462009，9轮官方完整统计；请求346）。

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
        handles = []
        local = True
        for owner in range(1, workers):
            handle = spawn_drone(ore_wells, owner, workers, size, 20000, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not ore_wells(0, workers, size, 20000, deadline):
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


def ore_wells(first, stride, size, goal, deadline):
    # 每个x只有一个挖掘者；在各4×8区域错开采样x，两口井均不跨所属列。
    for x in range(first, size, stride):
        y0 = ((x % 4) * 8 + (x // 4) % 4) % size
        for offset in [0, 4]:
            y = (y0 + offset) % size
            if num_items(Items.Quartz) >= goal:
                return True
            if not ore_move_to(x, y, size):
                return False
            # 官方首石英区块32..47，长8/9的针都穿过39；实际库存只计真实dig。
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
    lb_ores()
