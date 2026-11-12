from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/mushroom-conveyor-v1/lb_mushrooms.py
# 本地研究：双行输送，把上排颜色运到下排同色柱；未实机。

def lb_mushrooms():
    mushroom_conveyor(240000)


def mushroom_conveyor(goal):
    size = get_world_size()
    columns = 1
    if max_drones() > 1:
        columns = 2
    blocks = []
    for y in range(0, size, 2):
        for i in range(columns):
            blocks.append((i * size // columns, (i + 1) * size // columns, y))
    for batch in range(128):
        if num_items(Items.Mushroom) >= goal:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for _ in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                quick_print("mushrooms_failed", "find")
                return
        if get_ground_type() != Grounds.Mushroom:
            return
        top = get_pos_z()
        quick_print("mushrooms_top", batch, top, get_time())
        for layer in range(7):
            handles = []
            results = []
            for index in range(len(blocks)):
                if max_drones() > 1 and index < len(blocks) - 1:
                    handle = spawn_drone(conveyor_pair, blocks[index], top - layer, layer % 2, goal)
                    if handle == None:
                        results.append(conveyor_pair(blocks[index], top - layer, layer % 2, goal))
                    else:
                        handles.append(handle)
                else:
                    results.append(conveyor_pair(blocks[index], top - layer, layer % 2, goal))
            for handle in handles:
                results.append(wait_for(handle))
            pairs = 0
            mushrooms = 0
            for result in results:
                if result == None:
                    quick_print("mushrooms_failed", "pair", batch, layer)
                    return
                pairs += result[0]
                mushrooms += result[1]
            quick_print("mushrooms_layer", batch, layer, pairs, mushrooms, get_time(), num_items(Items.Mushroom))
            if num_items(Items.Mushroom) >= goal or mushrooms == 0:
                break
        if get_time() > 3600:
            return
    quick_print("mushrooms_failed", "batch_limit")


def conveyor_pair(block, ceiling, parity, goal):
    x0, x1, y = block
    size = get_world_size()
    high_y = y + parity
    low_y = y + 1 - parity
    down = North
    up = South
    if parity:
        down = South
        up = North
    floor = ceiling - 1
    colors = []
    heights = []
    pairs = 0
    mushrooms = 0
    for row in [high_y, low_y]:
        target = ceiling
        if row == low_y:
            target = floor
        for x in range(x0, x1):
            if not conveyor_move_to(x, row, size):
                return None
            for _ in range(128):
                if get_pos_z() <= target:
                    break
                if not dig():
                    return None
            if row == low_y:
                heights.append(get_pos_z())
                colors.append(measure() if get_ground_type() == Grounds.Mushroom else -1)
    for x in range(x0, x1):
        if num_items(Items.Mushroom) >= goal:
            return pairs, mushrooms
        if not conveyor_move_to(x, high_y, size):
            return None
        if get_pos_z() != ceiling or get_ground_type() != Grounds.Mushroom:
            continue
        mushrooms += 1
        color = measure()
        start = x - x0
        end = -1
        best = 10000
        for candidate in range(x1 - x0):
            if colors[candidate] != color or heights[candidate] < floor - 1:
                continue
            cost = abs(candidate - start)
            first = min(candidate, start)
            last = max(candidate, start)
            for k in range(first, last + 1):
                if k != candidate:
                    cost += 2 * (floor - heights[k])
            if cost < best:
                best = cost
                end = candidate
        if end < 0:
            continue
        direction = East
        step = 1
        if end < start:
            direction = West
            step = -1
        repaired = False
        for k in range(start, end, step):
            if heights[k] < floor:
                if not conveyor_move_to(x0 + k, low_y, size):
                    return None
                while get_pos_z() < floor:
                    if not place(Grounds.Dirt):
                        return None
                if get_pos_z() != floor:
                    return None
                heights[k] = floor
                colors[k] = -1
                repaired = True
        if repaired and not conveyor_move_to(x, high_y, size):
            return None
        if not push(down):
            return None
        if start == end:
            heights[end] = get_pos_z(down)
            colors[end] = measure(down) if get_ground_type(down) == Grounds.Mushroom else -1
        else:
            if not move(down):
                return None
            for k in range(start, end, step):
                if not push(direction):
                    return None
                if k + step != end and not move(direction):
                    return None
            heights[end] = get_pos_z(direction)
            colors[end] = measure(direction) if get_ground_type(direction) == Grounds.Mushroom else -1
        pairs += 1
    return pairs, mushrooms


def conveyor_move_to(tx, ty, size):
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


if __name__ == "__main__":
    lb_mushrooms()
