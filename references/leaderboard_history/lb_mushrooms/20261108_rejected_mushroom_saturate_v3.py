from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/mushroom-saturate-v3/lb_mushrooms.py
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
                if nx >= x0 and nx < x1 and ny >= y0 and ny < y1:
                    around.append((nx + ny * size, DIRECTIONS[i], BACKS[i]))
            adjacent[cell] = around
            if not mushroom_move_to(x, y, size):
                return False
            mushroom_read(cache, cell)
    pending = list(owned)
    queued = set(owned)
    forced = 0
    dry = 0
    pairs = 0
    previous = None
    for step in range(len(owned) * 128):
        if step % 16 == 0 and num_items(Items.Mushroom) >= goal:
            return True
        if len(pending) > 0:
            cell = pending.pop()
            queued.remove(cell)
            plan = mushroom_plan(cell, cache, adjacent)
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
                plan = mushroom_plan(cursor, cache, adjacent)
            for changed in touched:
                mushroom_touch(changed, cache, adjacent, pending, queued)
            dry = 0
            continue
        if forced >= 8:
            break
        source = -1
        target = -1
        direction = None
        highest = -10000
        landing = -10000
        for cell in owned:
            z, color = cache[cell]
            if color < 0:
                continue
            for other, move_dir, reverse in adjacent[cell]:
                nz = cache[other][0]
                if nz >= z or previous == (other, cell):
                    continue
                if z > highest or (z == highest and nz > landing):
                    source = cell
                    target = other
                    direction = move_dir
                    highest = z
                    landing = nz
        if source < 0:
            break
        if not mushroom_move_to(source % size, source // size, size) or not push(direction):
            return False
        mushroom_read(cache, source)
        mushroom_read(cache, target, direction)
        mushroom_touch(source, cache, adjacent, pending, queued)
        mushroom_touch(target, cache, adjacent, pending, queued)
        previous = (source, target)
        dry += 1
        forced += 1
    quick_print("mushrooms_patch", block, pairs, forced, get_time())
    return True


def mushroom_plan(cell, cache, adjacent):
    z, color = cache[cell]
    if color < 0:
        return None
    for other, direction, back in adjacent[cell]:
        height, kind = cache[other]
        if kind == color and height != z:
            if height < z:
                return 1, other, -1, direction, None, None
            return 4, other, cell, direction, back, None
    for middle, first, first_back in adjacent[cell]:
        height, kind = cache[middle]
        if height >= z:
            continue
        for end, second, second_back in adjacent[middle]:
            if end != cell and cache[end][0] <= height and cache[end][1] == color:
                return 2, middle, end, first, second, None
    for neighbor, incoming, incoming_back in adjacent[cell]:
        if cache[neighbor] != (z, color):
            continue
        for receiver, outgoing, outgoing_back in adjacent[cell]:
            if receiver != neighbor and cache[receiver][0] <= z - 2:
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
    color = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        color = measure(direction)
    cache[cell] = (get_pos_z(direction), color)


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
