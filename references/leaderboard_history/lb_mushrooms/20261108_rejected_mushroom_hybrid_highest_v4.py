from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/mushroom-hybrid-highest-v4/lb_mushrooms.py
# 本地研究：一次整面准备，缓存柱顶，只向已知同色终点搬运；未实机。

def lb_mushrooms():
    mushroom_saturate(240000)


def mushroom_saturate(goal):
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
            handles.append(spawn_drone(saturate_patch, block, goal))
        if not saturate_patch((0, size // gx, 0, size // gy), goal):
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
            target = top - (x + y) % 2
            while get_pos_z() > target:
                if not dig():
                    return False
            move(North)
    return True


def saturate_patch(block, goal):
    global mushroom_live
    global mushroom_columns
    global mushroom_bottom
    mushroom_live = {}
    mushroom_columns = 0
    mushroom_bottom = None
    size = get_world_size()
    x0, x1, y0, y1 = block
    owned = []
    adjacent = {}
    cache = {}
    for y in range(y0, y1):
        for offset in range(x1 - x0):
            x = x0 + offset
            if (y - y0) % 2:
                x = x1 - 1 - offset
            cell = x + y * size
            owned.append(cell)
            around = []
            for i in range(4):
                dx, dy = OFFSETS[i]
                nx = x + dx
                ny = y + dy
                if x0 == 0 and x1 == size and y0 == 0 and y1 == size:
                    nx = nx % size
                    ny = ny % size
                if nx >= x0 and nx < x1 and ny >= y0 and ny < y1:
                    around.append((nx + ny * size, DIRECTIONS[i], BACKS[i]))
            adjacent[cell] = around
            if not mushroom_move_to(x, y, size):
                return False
            mushroom_read(cache, cell)
    pending = list(owned)
    queued = set(owned)
    forced = 0
    highest = -100000
    for z in mushroom_live:
        highest = max(highest, z)
    pairs = 0
    for step in range(len(owned) * 128):
        if step % 16 == 0 and num_items(Items.Mushroom) >= goal:
            return True
        if mushroom_columns == 0:
            break
        old_highest = highest
        while highest not in mushroom_live or len(mushroom_live[highest]) == 0:
            highest -= 1
        if mushroom_bottom != None and highest <= mushroom_bottom + 1:
            break
        floor = highest - 2
        if highest != old_highest:
            pending = list(owned)
            queued = set(owned)
        if len(pending) > 0:
            cell = pending.pop()
            queued.remove(cell)
            plan = mushroom_plan(cell, cache, adjacent, floor)
            if plan == None:
                continue
            if not mushroom_move_to(cell % size, cell // size, size):
                return False
            touched = set()
            cursor = cell
            for _ in range(32):
                if plan == None:
                    break
                result = mushroom_apply(cursor, plan, cache)
                if result == None:
                    return False
                affected, cursor = result
                for changed in affected:
                    touched.add(changed)
                pairs += 1
                plan = mushroom_plan(cursor, cache, adjacent, floor)
            for changed in touched:
                mushroom_touch(changed, cache, adjacent, pending, queued)
            continue
        source = get_pos_x() + get_pos_y() * size
        if cache[source][0] != highest or cache[source][1] < 0:
            nearby = -1
            for other, direction, reverse in adjacent[source]:
                if cache[other][0] == highest and cache[other][1] >= 0:
                    nearby = other
                    break
            if nearby >= 0:
                source = nearby
            else:
                for candidate in mushroom_live[highest]:
                    source = candidate
                    break
        if not mushroom_move_to(source % size, source // size, size) or not dig():
            return False
        mushroom_read(cache, source)
        mushroom_touch(source, cache, adjacent, pending, queued)
        forced += 1
    quick_print("mushrooms_patch", block, pairs, forced, get_time())
    return True


def mushroom_plan(cell, cache, adjacent, floor):
    z, color = cache[cell]
    if color < 0:
        return None
    for other, direction, back in adjacent[cell]:
        height, kind = cache[other]
        if kind == color and height != z and min(height, z) >= floor:
            if height < z:
                return 1, other, -1, direction, None, None
            return 4, other, cell, direction, back, None
    for middle, first, first_back in adjacent[cell]:
        height, kind = cache[middle]
        if height >= z:
            continue
        for end, second, second_back in adjacent[middle]:
            if end != cell and cache[end][0] <= height and cache[end][0] >= floor and cache[end][1] == color:
                return 2, middle, end, first, second, None
    for neighbor, incoming, incoming_back in adjacent[cell]:
        if cache[neighbor] != (z, color):
            continue
        for receiver, outgoing, outgoing_back in adjacent[cell]:
            if receiver != neighbor and floor <= cache[receiver][0] <= z - 2:
                return 3, neighbor, receiver, incoming, outgoing, incoming_back
    return None


def mushroom_apply(cell, plan, cache):
    kind, a, b, first, second, reverse = plan
    if kind == 1:
        if not push(first):
            return None
        mushroom_read(cache, cell)
        mushroom_read(cache, a, first)
        return [cell, a], cell
    if kind == 4:
        if not move(first) or not push(second):
            return None
        mushroom_read(cache, a)
        mushroom_read(cache, cell, second)
        return [cell, a], a
    if kind == 2:
        if not push(first):
            return None
        mushroom_read(cache, cell)
        mushroom_read(cache, a, first)
        if not move(first) or not push(second):
            return None
        mushroom_read(cache, a)
        mushroom_read(cache, b, second)
        return [cell, a, b], a
    z, color = cache[cell]
    if not push(second):
        return None
    mushroom_read(cache, cell)
    mushroom_read(cache, b, second)
    if not move(first) or not push(reverse):
        return None
    mushroom_read(cache, a)
    mushroom_read(cache, cell, reverse)
    if cache[cell] != (z, color):
        return [cell, a, b], a
    if not move(reverse) or not push(second):
        return None
    mushroom_read(cache, cell)
    mushroom_read(cache, b, second)
    return [cell, a, b], cell


def mushroom_touch(cell, cache, adjacent, pending, queued):
    if cache[cell][1] >= 0 and cell not in queued:
        pending.append(cell)
        queued.add(cell)
    color = cache[cell][1]
    for other, direction, back in adjacent[cell]:
        if cache[other][1] >= 0 and other not in queued:
            pending.append(other)
            queued.add(other)
        if color >= 0:
            for end, second, second_back in adjacent[other]:
                if cache[end][1] == color and end not in queued:
                    pending.append(end)
                    queued.add(end)


def mushroom_read(cache, cell, direction=None):
    global mushroom_columns
    global mushroom_bottom
    if cell in cache:
        old_z, old_color = cache[cell]
        if old_color >= 0:
            mushroom_live[old_z].remove(cell)
            mushroom_columns -= 1
    color = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        color = measure(direction)
    z = get_pos_z(direction)
    cache[cell] = (z, color)
    if color >= 0:
        if z not in mushroom_live:
            mushroom_live[z] = set()
        mushroom_live[z].add(cell)
        mushroom_columns += 1
    else:
        mushroom_bottom = z


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
