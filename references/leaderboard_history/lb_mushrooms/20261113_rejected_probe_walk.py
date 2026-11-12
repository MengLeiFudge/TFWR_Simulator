from __builtins__ import *

# 探针 W：无地图的局部贪心。站在格上先找同色更深邻格推送；
# 否则向最浅的蘑菇邻格移动（沿坑边界上坡走）；长时间无配对才挖本格。
# 目的：测「沿坑边界巡走」的每对动作数与挖/配比例。

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
    walk(top, area, deadline, began)


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


def walk(top, area, deadline, began):
    merges = 0
    moves = 0
    pushes = 0
    digs = 0
    idle = 0
    floor = top - 9
    report = get_time()
    while get_time() < deadline:
        z = get_pos_z()
        t = -1
        if get_ground_type() == Grounds.Mushroom:
            t = measure()
        hit = 0
        if t >= 0:
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
                pushes += 1
                merges += 1
                idle = 0
                continue
        best = -1
        bz = -100000
        for k in range(4):
            direction = DIRECTIONS[k]
            if get_ground_type(direction) != Grounds.Mushroom:
                continue
            dz = get_pos_z(direction)
            if dz > bz:
                bz = dz
                best = k
        if best >= 0:
            if bz > floor:
                move(DIRECTIONS[best])
                moves += 1
            else:
                best = -1
        if best < 0:
            # 四邻都不是可工作的蘑菇：本格若还有蘑菇就挖掉，否则停在这里等下一处。
            if t >= 0 and z > floor:
                if dig():
                    digs += 1
            else:
                idle += 20
        idle += 1
        if idle > 30:
            idle = 0
            if t >= 0 and get_pos_z() > floor:
                if dig():
                    digs += 1
        if get_time() - report > 5:
            report = get_time()
            quick_print("probe_walk", merges, pushes, digs, moves,
                        num_items(Items.Mushroom), get_time() - began, get_pos_z())
    quick_print("probe_done", merges, pushes, digs, moves,
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
    probe(12, 40)
