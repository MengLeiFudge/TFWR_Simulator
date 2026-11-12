from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/underground-leaderboards-20261111/candidates/mushrooms_pairs.py


def mushrooms_pairs():
    for batch in range(128):
        if num_items(Items.Mushroom) >= 240000:
            quick_print("pairs_done", get_time(), num_items(Items.Mushroom))
            return
        clear()
        for probe in range(128):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Mushroom:
            return
        top = get_pos_z()
        handles = []
        for worker in range(1, 32):
            handle = spawn_drone(prepare, worker, top)
            if handle == None:
                return
            handles.append(handle)
        prepare(0, top)
        for handle in handles:
            wait_for(handle)
        handles = []
        for worker in range(1, 32):
            handle = spawn_drone(pairs, worker)
            if handle == None:
                return
            handles.append(handle)
        pairs(0)
        for handle in handles:
            wait_for(handle)
        quick_print("pairs_cycle", batch, get_time(), num_items(Items.Mushroom))


def prepare(worker, top):
    x = worker % 16 * 2
    first = worker // 16 * 16
    for row in range(first, first + 16):
        go(x, row)
        while get_pos_z() > top:
            if not dig():
                return False
        move(East)
        while get_pos_z() > top:
            if not dig():
                return False
    return True


def pairs(worker):
    x = worker % 16 * 2
    first = worker // 16 * 16
    for row in range(first, first + 16):
        go(x, row)
        direction = East
        for action in range(32):
            if num_items(Items.Mushroom) >= 240000:
                return True
            if get_ground_type() != Grounds.Mushroom or get_ground_type(direction) != Grounds.Mushroom:
                break
            own = get_pos_z()
            other = get_pos_z(direction)
            if own < other:
                move(direction)
                if direction == East:
                    direction = West
                else:
                    direction = East
            elif own > other and measure() == measure(direction):
                if not push(direction):
                    break
            elif not dig():
                return False
    return True


def go(tx, ty):
    dx = (tx - get_pos_x()) % 32
    dy = (ty - get_pos_y()) % 32
    horizontal = East
    vertical = North
    if dx > 16:
        dx = 32 - dx
        horizontal = West
    if dy > 16:
        dy = 32 - dy
        vertical = South
    for step in range(dx):
        move(horizontal)
    for step in range(dy):
        move(vertical)


mushrooms_pairs()
