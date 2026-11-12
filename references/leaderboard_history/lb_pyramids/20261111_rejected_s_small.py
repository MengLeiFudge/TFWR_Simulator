from __builtins__ import *
# 淘汰候选归档：lb_pyramids | 原实验路径 .codex/underground-leaderboards-20261111/candidates/pyramids_small.py


def pyramids_small():
    set_world_size(5)
    for cycle in range(4096):
        if num_items(Items.Power) >= 150100:
            quick_print("small_done", get_time(), num_items(Items.Power))
            return
        if get_time() > 14400:
            return
        clear()
        for _ in range(17):
            if get_ground_type() == Grounds.Limestone:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Limestone:
            return
        floor = get_pos_z()
        result = small_dispatch(0, 25, floor, False)
        for ok in result:
            if not ok:
                quick_print("small_failed", "clean", cycle)
                return
        small_move(2, 2)
        if get_pos_z() == floor + 3:
            if not dig():
                return
        small_move(0, 0)
        if not place(Grounds.Sand):
            return
        handle = spawn_drone(small_dispatch, 0, 25, floor, True)
        if handle == None:
            return
        small_move(2, 2)
        result = wait_for(handle)
        for ok in result:
            if not ok:
                quick_print("small_failed", "patch", cycle)
                return
        if get_pos_z() != floor + 2 or not place(Grounds.Sand):
            return
        if get_entity_type() != Entities.Sunflower or not harvest():
            quick_print("small_failed", "harvest", cycle)
            return
        quick_print("small_cycle", cycle, get_time(), num_items(Items.Power))


def small_dispatch(lo, hi, floor, patch):
    if hi - lo == 1:
        return [small_work(lo, floor, patch)]
    middle = (lo + hi) // 2
    handle = spawn_drone(small_dispatch, middle, hi, floor, patch)
    result = small_dispatch(lo, middle, floor, patch)
    if handle == None:
        other = small_dispatch(middle, hi, floor, patch)
    else:
        other = wait_for(handle)
    for ok in other:
        result.append(ok)
    return result


def small_work(index, floor, patch):
    x = index // 5
    y = index % 5
    small_move(x, y)
    if not patch:
        for _ in range(17):
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                break
            if get_pos_z() <= floor or not dig():
                return False
        if index != 0 and get_pos_z() == floor:
            return place(Grounds.Sand)
        return True
    target = floor + 1 + min(x, 4 - x, y, 4 - y)
    if index == 12:
        target -= 1
    if get_pos_z() < target:
        if not place(Grounds.Sand):
            return False
    return get_pos_z() == target


def small_move(x, y):
    dx = (x - get_pos_x()) % 5
    direction = East
    if dx > 2:
        dx = 5 - dx
        direction = West
    for _ in range(dx):
        move(direction)
    dy = (y - get_pos_y()) % 5
    direction = North
    if dy > 2:
        dy = 5 - dy
        direction = South
    for _ in range(dy):
        move(direction)


if __name__ == "__main__":
    pyramids_small()
