from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-direct-queue-v1/lb_mushrooms_single.py


def lb_mushrooms_single():
    size = get_world_size()
    adjacent = []
    for y in range(size):
        for x in range(size):
            adjacent.append([((y + 1) % size * size + x, North),
                             (y * size + (x + 1) % size, East),
                             ((y - 1) % size * size + x, South),
                             (y * size + (x - 1) % size, West)])
    route = []
    for y in range(size):
        for offset in range(size):
            x = offset
            if y % 2:
                x = size - 1 - offset
            route.append(x + y * size)
    for batch in range(128):
        if num_items(Items.Mushroom) >= 30000:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                quick_print("mushrooms_failed", "find")
                return
        if get_ground_type() != Grounds.Mushroom:
            return
        top = get_pos_z()
        heights = []
        colors = []
        for cell in range(size * size):
            heights.append(top)
            colors.append(-1)
        for cell in route:
            if not move_to(cell % size, cell // size, size):
                return
            for step in range(256):
                if get_pos_z() <= top:
                    break
                if not dig():
                    return
            heights[cell] = get_pos_z()
            if get_ground_type() == Grounds.Mushroom:
                colors[cell] = measure()
        prepared = get_time()
        pairs = 0
        digs = 0
        for layer in range(6):
            ceiling = top - layer
            floor = ceiling - 2
            for cell in route:
                if num_items(Items.Mushroom) >= 30000:
                    break
                pending = [cell]
                dug = False
                for step in range(size * size * 16):
                    if len(pending) == 0:
                        if dug or heights[cell] < ceiling or colors[cell] < 0:
                            break
                        if not move_to(cell % size, cell // size, size) or not dig():
                            quick_print("mushrooms_failed", "dig", batch, layer, cell)
                            return
                        digs += 1
                        heights[cell] = get_pos_z()
                        colors[cell] = -1
                        if get_ground_type() == Grounds.Mushroom:
                            colors[cell] = measure()
                        dug = True
                        pending.append(cell)
                    current = pending.pop()
                    z = heights[current]
                    color = colors[current]
                    if color < 0:
                        continue
                    source = -1
                    target = -1
                    direction = None
                    for other, candidate in adjacent[current]:
                        if colors[other] == color and z > heights[other] and heights[other] >= floor:
                            source = current
                            target = other
                            direction = candidate
                            break
                    if source < 0 and z >= floor:
                        for other, candidate in adjacent[current]:
                            if colors[other] == color and heights[other] > z:
                                source = other
                                target = current
                                direction = BACK[candidate]
                                break
                    if source < 0:
                        continue
                    if not move_to(source % size, source // size, size):
                        return
                    if get_pos_z() != heights[source] or get_ground_type() != Grounds.Mushroom or measure() != colors[source]:
                        quick_print("mushrooms_failed", "cache_source", batch, layer, source)
                        return
                    if get_pos_z(direction) != heights[target] or get_ground_type(direction) != Grounds.Mushroom or measure(direction) != colors[target]:
                        quick_print("mushrooms_failed", "cache_target", batch, layer, target)
                        return
                    if not push(direction):
                        return
                    pairs += 1
                    heights[source] = get_pos_z()
                    colors[source] = -1
                    if get_ground_type() == Grounds.Mushroom:
                        colors[source] = measure()
                    heights[target] = get_pos_z(direction)
                    colors[target] = -1
                    if get_ground_type(direction) == Grounds.Mushroom:
                        colors[target] = measure(direction)
                    pending.append(target)
                    pending.append(source)
            if num_items(Items.Mushroom) >= 30000:
                break
        quick_print("mushrooms_batch", batch, pairs, digs, get_time(), num_items(Items.Mushroom), "work", get_time() - prepared)


def move_to(tx, ty, size):
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


BACK = {North: South, East: West, South: North, West: East}

if __name__ == "__main__":
    lb_mushrooms_single()
