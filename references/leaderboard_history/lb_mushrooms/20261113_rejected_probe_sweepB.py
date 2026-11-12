from __builtins__ import *

# 探针 B：平整层蛇形巡访，能推就推，否则挖本格。
# 目的：测「每次有效配对的动作与解释器开销」，作为重写基准。

DIRECTIONS = [North, East, South, West]


def probe(area, deadline):
    began = get_time()
    clear()
    for step in range(256):
        if get_ground_type() == Grounds.Mushroom:
            break
        dig()
    if get_ground_type() != Grounds.Mushroom:
        quick_print("probe_failed", "no_stratum")
        return
    top = get_pos_z()
    height = 0
    for step in range(7):
        if get_ground_type() != Grounds.Mushroom:
            break
        dig()
        height += 1
    quick_print("probe_stratum", height, top, get_time())
    level(top, area)
    quick_print("probe_leveled", get_time())
    sweep(top, area, deadline, began)


def level(top, area):
    for j in range(area):
        for i in range(area):
            x = i
            if j % 2 != 0:
                x = area - 1 - i
            if not move_to(x, j):
                return False
            while get_pos_z() > top:
                if not dig():
                    return False
    return True


def sweep(top, area, deadline, began):
    merges = 0
    pushes = 0
    digs = 0
    passes = 0
    while get_time() < deadline:
        pass_start = get_time()
        pass_merges = 0
        for j in range(area):
            for i in range(area):
                x = i
                if j % 2 != 0:
                    x = area - 1 - i
                if not move_to(x, j):
                    quick_print("probe_failed", "move", x, j)
                    return
                if get_ground_type() != Grounds.Mushroom:
                    continue
                z = get_pos_z()
                t = measure()
                hit = 0
                if get_ground_type(North) == Grounds.Mushroom and get_pos_z(North) < z and measure(North) == t:
                    hit = 1
                elif get_ground_type(East) == Grounds.Mushroom and get_pos_z(East) < z and measure(East) == t:
                    hit = 2
                elif get_ground_type(South) == Grounds.Mushroom and get_pos_z(South) < z and measure(South) == t:
                    hit = 3
                elif get_ground_type(West) == Grounds.Mushroom and get_pos_z(West) < z and measure(West) == t:
                    hit = 4
                if hit > 0:
                    if push(DIRECTIONS[hit - 1]):
                        passes = passes
                        pushes += 1
                        pass_merges += 1
                        merges += 1
                else:
                    if get_hardness() >= 10000000:
                        continue
                    if dig():
                        digs += 1
        passes += 1
        quick_print("probe_pass", passes, merges, pushes, digs,
                    num_items(Items.Mushroom), get_time() - pass_start, get_time())
        if get_pos_z() < top - 9:
            break
    quick_print("probe_done", passes, merges, pushes, digs,
                num_items(Items.Mushroom), get_time() - began)


def move_to(tx, ty):
    size = get_world_size()
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
    for step in range(dx):
        if not move(horizontal):
            return False
    for step in range(dy):
        if not move(vertical):
            return False
    return True


if __name__ == "__main__":
    probe(8, 40)
