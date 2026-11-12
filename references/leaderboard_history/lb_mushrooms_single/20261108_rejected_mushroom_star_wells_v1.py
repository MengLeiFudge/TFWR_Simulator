from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-star-wells-v1/lb_mushrooms_single.py

def lb_mushrooms_single():
    began = get_time()
    size = get_world_size()
    centers = []
    for y in range(size):
        for x in range(size):
            if (x + 2 * y) % 5 == 0:
                centers.append((x, y))
    for batch in range(128):
        if num_items(Items.Mushroom) >= 30000:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if get_time() - began > 7200 or not dig():
                quick_print("mushrooms_failed", "find", batch)
                return
        if get_ground_type() != Grounds.Mushroom:
            quick_print("mushrooms_failed", "find_limit", batch)
            return
        top = get_pos_z()
        if not dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch)
            return
        for x, y in centers:
            if num_items(Items.Mushroom) >= 30000:
                break
            if not work_star(x, y, size):
                quick_print("mushrooms_failed", "star", batch, x, y)
                return
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def work_star(x, y, size):
    if not move_to(x, y):
        return False
    neighbors = []
    if y + 1 < size:
        neighbors.append(0)
    if x + 1 < size:
        neighbors.append(1)
    if y > 0:
        neighbors.append(2)
    if x > 0:
        neighbors.append(3)
    for turn in range(128):
        if num_items(Items.Mushroom) >= 30000:
            return True
        center_height = get_pos_z()
        center_color = -1
        if get_ground_type() == Grounds.Mushroom:
            center_color = measure()
        colors = [-1, -1, -1, -1]
        heights = [0, 0, 0, 0]
        highest = -1000000
        source = -1
        direct = -1
        for i in neighbors:
            direction = DIRECTIONS[i]
            if get_ground_type(direction) == Grounds.Mushroom:
                colors[i] = measure(direction)
                heights[i] = get_pos_z(direction)
                if heights[i] > highest:
                    highest = heights[i]
                    source = i
                if center_color == colors[i] and heights[i] > center_height:
                    direct = i
        if source < 0:
            return True
        if direct >= 0:
            if not push_neighbor(direct):
                return False
            continue
        acted = False
        for i in neighbors:
            if colors[i] < 0:
                continue
            for j in neighbors:
                if j <= i or colors[i] != colors[j]:
                    continue
                first = i
                second = j
                if heights[first] > heights[second]:
                    first = j
                    second = i
                needed = min(heights[first] - 1, heights[second] - 2)
                if needed < highest - 3:
                    continue
                if center_height > needed:
                    while get_pos_z() > needed:
                        if get_hardness() >= 10000000 or not dig():
                            return False
                else:
                    if not push_neighbor(first) or not push_neighbor(second):
                        return False
                acted = True
                break
            if acted:
                break
        if acted:
            continue
        # 下一次dig前抬高过深的井；不足的Block不赠送，塌方损失按实计。
        for step in range(16):
            if get_pos_z() >= highest - 3 or num_items(Items.Block) < 1:
                break
            if not place(Grounds.Dirt):
                return False
        if not move(DIRECTIONS[source]):
            return False
        dug = dig()
        if not move(BACKS[source]) or not dug:
            return False
    return False


# 每台无人机负责一列；无人机不足时按列步长分担，整层完成后才返回。
def dig_layer(target):
    size = get_world_size()
    workers = min(size, max_drones())
    handles = []
    ok = True
    for x in range(workers - 1):
        if not move_to(x, 0):
            ok = False
            break
        handle = spawn_drone(dig_columns, x, workers, size, target)
        if handle == None:
            if not dig_columns(x, workers, size, target):
                ok = False
        else:
            handles.append(handle)
    if ok and not dig_columns(workers - 1, workers, size, target):
        ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


# 覆盖层起始高度一致，只需逐格挖到本次目标高度，无需识别地面类型。
def dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
        if not move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() != target:
                return False
            if not move(North):
                return False
    return True


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
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


def push_neighbor(i):
    if not move(DIRECTIONS[i]):
        return False
    pushed = push(BACKS[i])
    if not move(BACKS[i]):
        return False
    return pushed


DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


if __name__ == "__main__":
    lb_mushrooms_single()
