from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-routed-sliding-v1/lb_mushrooms_single.py


def lb_mushrooms_single():
    global heights
    global colors
    global adjacent
    size = get_world_size()
    count = size * size
    adjacent = []
    offsets = []
    for distance in range(size + 1):
        for dy in range(size):
            for dx in range(size):
                if min(dx, size - dx) + min(dy, size - dy) == distance:
                    offsets.append((dx, dy))
    for cell in range(count):
        x, y = cell % size, cell // size
        adjacent.append([((y + 1) % size * size + x, North),
                         (y * size + (x + 1) % size, East),
                         ((y - 1) % size * size + x, South),
                         (y * size + (x - 1) % size, West)])
    began = get_time()
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
            return
        top = get_pos_z()
        if not dig_layer(top) or not move_to(0, 0) or not dig():
            return
        heights = [0] * count
        colors = [-1] * count
        cursor = 0
        for y in range(size):
            for offset in range(size):
                x = offset
                if y % 2:
                    x = size - 1 - offset
                if not move_to(x, y):
                    return
                cursor = x + y * size
                read_column(cursor)
        previous = None
        dry = 0
        pairs = 0
        pushes = 0
        for step in range(8192):
            if step % 16 == 0 and num_items(Items.Mushroom) >= 30000:
                break
            plan = None
            start = -1
            backup = None
            x, y = cursor % size, cursor // size
            for dx, dy in offsets:
                cell = (x + dx) % size + ((y + dy) % size) * size
                if colors[cell] < 0:
                    continue
                plan = find_route(cell)
                if plan != None:
                    start = cell
                    break
                if backup == None:
                    for other, direction in adjacent[cell]:
                        if heights[other] < heights[cell] and previous != (other, cell):
                            backup = (cell, other, direction)
                            break
            matched = plan != None
            if not matched:
                if backup == None or dry >= count * 4:
                    break
                start, other, direction = backup
                plan = [(other, direction)]
            if start != cursor and not move_to(start % size, start // size):
                return
            cursor = start
            for index in range(len(plan)):
                other, direction = plan[index]
                if not push(direction):
                    quick_print("mushrooms_failed", "planned_push", batch, cursor, other)
                    return
                previous = (cursor, other)
                pushes += 1
                read_column(cursor)
                read_column(other, direction)
                if index + 1 < len(plan):
                    if not move(direction):
                        return
                    cursor = other
            if matched:
                pairs += 1
                dry = 0
            else:
                dry += 1
        quick_print("mushrooms_routed_batch", batch, pairs, pushes, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


# 最多三推；仅使用路径开始前可见的柱顶，不猜被遮挡的颜色。
def find_route(source):
    color = colors[source]
    frontier = [(source, heights[source] - 1, [])]
    seen = {source: heights[source]}
    for depth in range(3):
        following = []
        for cell, ceiling, path in frontier:
            for other, direction in adjacent[cell]:
                height = heights[other]
                if height > ceiling or other in seen and seen[other] >= height:
                    continue
                route = path + [(other, direction)]
                if colors[other] == color:
                    return route
                seen[other] = height
                if depth < 2:
                    following.append((other, height, route))
        frontier = following
        if len(frontier) == 0:
            break
    return None


# push不触发塌方；只回读实际被推动的两柱，覆盖层与启动dig后才建缓存。
def read_column(cell, direction=None):
    heights[cell] = get_pos_z(direction)
    colors[cell] = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        colors[cell] = measure(direction)


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


if __name__ == "__main__":
    lb_mushrooms_single()
