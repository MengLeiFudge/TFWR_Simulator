from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261109/mushroom-fixed-columns-v1/lb_mushrooms.py

def lb_mushrooms():
    size = get_world_size()
    for batch in range(128):
        if num_items(Items.Mushroom) >= 240000:
            return
        clear()
        handles = []
        for x in range(1, size):
            handle = spawn_drone(prepare_column, x, size)
            if handle != None:
                handles.append(handle)
        top = prepare_column(0, size)
        for handle in handles:
            result = wait_for(handle)
            if top == None:
                top = result
        if top == None:
            quick_print("mushrooms_failed", "prepare", batch)
            return
        quick_print("mushrooms_prepared", batch, get_time(), top)
        handles = []
        for x in range(1, size):
            handle = spawn_drone(work_column, x, size, top)
            if handle != None:
                handles.append(handle)
        ok = work_column(0, size, top)
        for handle in handles:
            if not wait_for(handle):
                ok = False
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom), ok)
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def prepare_column(x, size):
    if not move_to_column(x, size):
        return None
    for step in range(256):
        if get_ground_type() == Grounds.Mushroom:
            return get_pos_z()
        if not dig():
            return None
    return None


def work_column(x, size, top):
    if not move_to_column(x, size):
        return False
    for y in range(size):
        if num_items(Items.Mushroom) >= 240000:
            return True
        for step in range(256):
            if get_pos_z() <= top or get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                return False
        for step in range(32):
            if get_ground_type() != Grounds.Mushroom:
                break
            color = measure()
            direction = None
            if can_push(East) and get_ground_type(East) == Grounds.Mushroom and measure(East) == color:
                direction = East
            elif can_push(West) and get_ground_type(West) == Grounds.Mushroom and measure(West) == color:
                direction = West
            if direction != None:
                push(direction)
            elif not dig():
                return False
        if not move(North):
            return False
    return True


def move_to_column(x, size):
    delta = (x - get_pos_x()) % size
    direction = East
    if delta > size // 2:
        delta = size - delta
        direction = West
    for step in range(delta):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_mushrooms()
