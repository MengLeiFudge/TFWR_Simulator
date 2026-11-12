from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/mushroom-walk-v1/lb_mushrooms.py
# 本地研究：局部连续合并，收到高邻柱后留在该柱；未实机。

def lb_mushrooms():
    mushroom_walk(240000)


def mushroom_walk(goal):
    size = get_world_size()
    workers = max_drones()
    gx = 1
    gy = 1
    while gx * gy * 2 <= workers:
        if gx <= gy:
            gx *= 2
        else:
            gy *= 2
    for batch in range(128):
        if num_items(Items.Mushroom) >= goal:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for _ in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                return
        top = get_pos_z()
        handles = []
        for x in range(1, min(size, workers)):
            handles.append(spawn_drone(mushroom_cover, x, min(size, workers), top))
        if not mushroom_cover(0, min(size, workers), top):
            return
        for handle in handles:
            if not wait_for(handle):
                return
        handles = []
        for owner in range(1, gx * gy):
            block = ((owner % gx) * size // gx, (owner % gx + 1) * size // gx,
                     (owner // gx) * size // gy, (owner // gx + 1) * size // gy)
            handles.append(spawn_drone(mushroom_patch, block, top, goal))
        if not mushroom_patch((0, size // gx, 0, size // gy), top, goal):
            return
        for handle in handles:
            if not wait_for(handle):
                return
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
        if get_time() > 3600:
            return


def mushroom_cover(first, stride, top):
    size = get_world_size()
    for x in range(first, size, stride):
        mushroom_move_to(x, 0, size)
        for y in range(size):
            while get_pos_z() > top:
                if not dig():
                    return False
            move(North)
    return True


def mushroom_patch(block, top, goal):
    size = get_world_size()
    x0, x1, y0, y1 = block
    for layer in range(6):
        ceiling = top - layer
        floor = ceiling - 2
        seen = 0
        for y in range(y0, y1):
            for offset in range(x1 - x0):
                if num_items(Items.Mushroom) >= goal:
                    return True
                x = x0 + offset
                if (y - y0) % 2:
                    x = x1 - 1 - offset
                if not mushroom_move_to(x, y, size):
                    return False
                cx = x
                cy = y
                for _ in range(32):
                    z = get_pos_z()
                    if z <= floor:
                        break
                    color = -1
                    if get_ground_type() == Grounds.Mushroom:
                        color = measure()
                        seen += 1
                    hit = -1
                    source = False
                    if color >= 0:
                        for i in range(4):
                            dx, dy = OFFSETS[i]
                            nx = cx + dx
                            ny = cy + dy
                            if nx < x0 or nx >= x1 or ny < y0 or ny >= y1:
                                continue
                            nz = get_pos_z(DIRECTIONS[i])
                            if nz == z or nz <= floor:
                                continue
                            if get_ground_type(DIRECTIONS[i]) == Grounds.Mushroom and measure(DIRECTIONS[i]) == color:
                                hit = i
                                source = nz > z
                                break
                    if hit >= 0:
                        if source:
                            if not move(DIRECTIONS[hit]) or not push(BACKS[hit]):
                                return False
                            dx, dy = OFFSETS[hit]
                            cx += dx
                            cy += dy
                        elif not push(DIRECTIONS[hit]):
                            return False
                    elif z >= ceiling:
                        if not dig():
                            return False
                    else:
                        break
        if not seen:
            return True
    return True


def mushroom_move_to(tx, ty, size):
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
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


if __name__ == "__main__":
    lb_mushrooms()
