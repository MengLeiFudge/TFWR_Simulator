from __builtins__ import *
# 淘汰候选归档：lb_rice_single | 原实验路径 .codex/underground-efficiency-20261108/candidates/rice-ring/lb_rice_single.py
# 本地候选：两层粘土按柱循环采收；完整目标时间待验证。

def lb_rice_single():
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    for batch in range(128):
        if num_items(Items.Rice) >= 100000:
            quick_print("rice_done", True, batch, get_time(), num_items(Items.Rice))
            return
        clear()
        handles = []
        local = True
        for column in range(1, workers):
            handle = spawn_drone(rice_columns, column, workers, size, 100000, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not rice_columns(0, workers, size, 100000, deadline):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        quick_print("rice_batch", batch, local, get_time(), num_items(Items.Rice))
        if not local:
            return
    quick_print("rice_failed", "batch_limit", get_time(), num_items(Items.Rice))


def rice_columns(first, stride, size, goal, deadline):
    for x in range(first, size, stride):
        if not rice_move_to(x, 0, size):
            return False
        for lap in range(1024):
            active = False
            for y in range(size):
                if num_items(Items.Rice) >= goal:
                    return True
                if get_time() > deadline:
                    return False
                growing = get_entity_type() == Entities.Rice
                if growing and can_harvest():
                    if not harvest():
                        return False
                    growing = False
                if growing:
                    active = True
                else:
                    ground = get_ground_type()
                    digs = 0
                    while ground != Grounds.Clay and ground != Grounds.Rock and digs < 128:
                        if not dig():
                            return False
                        ground = get_ground_type()
                        digs += 1
                    if ground == Grounds.Clay:
                        if not plant(Entities.Rice):
                            return False
                        active = True
                    elif ground != Grounds.Rock:
                        return False
                if not move(North):
                    return False
            if not active:
                break
        if active:
            return False
    return True


def rice_move_to(tx, ty, size):
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
    lb_rice_single()
