from __builtins__ import *
# 淘汰候选归档：lb_ores | 原实验路径 .codex/leaderboard-sol/underground-official/ores/trench-layers-candidate/lb_ores.py

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
        local = True
        # 石英稳定性5；相邻波次最多降5层，避免未采矿因深差过大而塌掉。
        for depth in [37, 42, 47]:
            handles = []
            for owner in range(1, workers):
                handle = spawn_drone(ore_trench, owner, workers, size, depth, 20000, deadline)
                if handle == None:
                    local = False
                    break
                handles.append(handle)
            if not ore_trench(0, workers, size, depth, 20000, deadline):
                local = False
            for handle in handles:
                if not wait_for(handle):
                    local = False
            quick_print("ores_layer", cycle, depth, get_time(), num_items(Items.Quartz))
            if not local or num_items(Items.Quartz) >= 20000:
                break
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


def ore_trench(first, stride, size, depth, goal, deadline):
    # 每个x由唯一工人向North推进；相邻已降低的柱帮助清除覆盖层。
    # 只按公开高度和地面采掘，收益仅取实际dig库存，不把塌掉的矿计入产量。
    for x in range(first, size, stride):
        if not ore_move_to(x, 0, size):
            return False
        for y in range(size):
            while get_pos_z() > -depth:
                if num_items(Items.Quartz) >= goal:
                    return True
                if get_time() > deadline or get_hardness() >= 10000000 or not dig():
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
    lb_ores()
