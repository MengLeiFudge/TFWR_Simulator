from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/mushroom-slide-v1/lb_mushrooms.py
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
    width = x1 - x0
    area = width * (y1 - y0)
    rotor = [0] * area
    cx = x0
    cy = y0
    mushroom_move_to(cx, cy, size)
    if not dig():
        return False
    previous = -1
    dry = 0
    pairs = 0
    pushes = 0
    for step in range(area * 128):
        if step % 16 == 0 and num_items(Items.Mushroom) >= goal:
            return True
        z = get_pos_z()
        color = -1
        if get_ground_type() == Grounds.Mushroom:
            color = measure()
        here = (cy - y0) * width + cx - x0
        rotor[here] = (rotor[here] + 1) % 4
        hit = -1
        incoming = False
        matched = False
        highest = -10000
        backup = -1
        walk = -1
        for offset in range(4):
            i = (rotor[here] + offset) % 4
            dx, dy = OFFSETS[i]
            nx = cx + dx
            ny = cy + dy
            if nx < x0 or nx >= x1 or ny < y0 or ny >= y1:
                continue
            walk = i
            nz = get_pos_z(DIRECTIONS[i])
            nc = -1
            if get_ground_type(DIRECTIONS[i]) == Grounds.Mushroom:
                nc = measure(DIRECTIONS[i])
            if nc >= 0 and nc == color and nz != z:
                hit = i
                incoming = nz > z
                matched = True
                break
            neighbor = (ny - y0) * width + nx - x0
            if neighbor == previous:
                continue
            if nz > z and nc >= 0 and nz > highest:
                highest = nz
                hit = i
                incoming = True
            if nz < z and color >= 0:
                backup = i
        if hit < 0 and backup >= 0:
            hit = backup
            incoming = False
        if hit >= 0:
            if incoming:
                if not move(DIRECTIONS[hit]) or not push(BACKS[hit]):
                    return False
                previous = here
                dx, dy = OFFSETS[hit]
                cx += dx
                cy += dy
            else:
                if not push(DIRECTIONS[hit]):
                    return False
                dx, dy = OFFSETS[hit]
                previous = (cy + dy - y0) * width + cx + dx - x0
            pushes += 1
            if matched:
                pairs += 1
                dry = 0
            else:
                dry += 1
        elif walk >= 0:
            if not move(DIRECTIONS[walk]):
                return False
            previous = -1
            dx, dy = OFFSETS[walk]
            cx += dx
            cy += dy
            dry += 1
        else:
            return False
        if dry > area * 4:
            break
    quick_print("mushroom_slide", block, pairs, pushes, get_time())
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
