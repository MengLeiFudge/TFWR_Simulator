from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261109/mushroom-checkerboard-supply-v1/lb_mushrooms.py

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
        if (x + y) % 2 == 0:
            ok = source_column()
        else:
            ok = receive_column()
        if not ok or not move(North):
            return False
    return True


def source_column():
    for turn in range(256):
        if get_ground_type() != Grounds.Mushroom:
            return True
        color = measure()
        z = get_pos_z()
        left_z = get_pos_z(West)
        right_z = get_pos_z(East)
        left_m = get_ground_type(West) == Grounds.Mushroom
        right_m = get_ground_type(East) == Grounds.Mushroom
        if left_m and z > left_z and measure(West) == color:
            push(West)
        elif right_m and z > right_z and measure(East) == color:
            push(East)
        elif not left_m and z >= left_z + 2:
            push(West)
        elif not right_m and z >= right_z + 2:
            push(East)
        elif z > max(left_z, right_z) + 2:
            if not dig():
                return False
        else:
            hover(1)
    return False


def receive_column():
    for turn in range(256):
        left_m = get_ground_type(West) == Grounds.Mushroom
        right_m = get_ground_type(East) == Grounds.Mushroom
        own_m = get_ground_type() == Grounds.Mushroom
        if not left_m and not right_m and not own_m:
            return True
        z = get_pos_z()
        left_z = get_pos_z(West)
        right_z = get_pos_z(East)
        if own_m:
            color = measure()
            if left_m and left_z > z and measure(West) == color or right_m and right_z > z and measure(East) == color:
                hover(1)
            elif not dig():
                return False
        elif left_m and left_z >= z + 2 or right_m and right_z >= z + 2:
            hover(1)
        elif not dig():
            return False
    return False


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
