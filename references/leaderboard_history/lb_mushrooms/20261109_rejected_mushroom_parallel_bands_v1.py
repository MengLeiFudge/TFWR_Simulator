from __builtins__ import *
# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261109/mushroom-parallel-bands-v1/lb_mushrooms.py

def lb_mushrooms():
    blocks = make_blocks()
    for batch in range(128):
        if num_items(Items.Mushroom) >= 240000:
            return
        clear()
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Mushroom:
            return
        top = get_pos_z()
        if not dig_layer(top):
            return
        quick_print("mushrooms_prepared", batch, get_time(), top)
        for band in range(3):
            handles = []
            for index in range(1, len(blocks)):
                handles.append(spawn_drone(work_patch, blocks[index], top - (band + 1) * 3))
            results = [work_patch(blocks[0], top - (band + 1) * 3)]
            for handle in handles:
                if handle == None:
                    return
                results.append(wait_for(handle))
            left = 0
            for ok, remaining in results:
                if not ok:
                    quick_print("mushrooms_failed", "band", batch, band)
                    return
                left += remaining
            quick_print("mushrooms_band", batch, band, get_time(), num_items(Items.Mushroom), left)
            if left == 0 or num_items(Items.Mushroom) >= 240000:
                break
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))


def work_patch(block, floor):
    global X0
    global Y0
    global WIDTH
    global SIZE
    X0, x1, Y0, y1 = block
    WIDTH = x1 - X0
    SIZE = get_world_size()
    height = y1 - Y0
    area = WIDTH * height
    near = []
    heights = []
    colors = []
    tops = {}
    active = set()
    for cell in range(area):
        x = cell % WIDTH
        y = cell // WIDTH
        neighbors = [-1, -1, -1, -1]
        if y + 1 < height:
            neighbors[0] = cell + WIDTH
        if x + 1 < WIDTH:
            neighbors[1] = cell + 1
        if y > 0:
            neighbors[2] = cell - WIDTH
        if x > 0:
            neighbors[3] = cell - 1
        near.append(neighbors)
        heights.append(0)
        colors.append(-1)
    for y in range(height):
        for offset in range(WIDTH):
            x = offset
            if y % 2 != 0:
                x = WIDTH - 1 - offset
            cell = x + y * WIDTH
            if not move_cell(cell):
                return False, 0
            read_cell(cell, heights, colors, tops, active)
    ok = work_field(WIDTH, near, heights, colors, tops, active, floor)
    remaining = 0
    for color in colors:
        if color >= 0:
            remaining += 1
    return ok, remaining


def move_cell(cell):
    return move_to(X0 + cell % WIDTH, Y0 + cell // WIDTH, SIZE)


def work_field(size, near, heights, colors, tops, active, floor):
    queue = []
    queued = set()
    highest = 1000000
    for turn in range(2048):
        if num_items(Items.Mushroom) >= 240000 or len(active) == 0:
            return True
        new_highest = max(active)
        if highest != new_highest:
            highest = new_highest
            if highest <= floor:
                return True
            for cell in range(len(near)):
                enqueue(cell, queue, queued)
        center = -1
        plan = None
        while len(queue) > 0:
            center = queue.pop()
            queued.remove(center)
            plan = plan_for(center, floor, near, heights, colors)
            if plan != None:
                break
        if plan == None:
            source = -1
            for cell in tops[highest]:
                source = cell
                break
            if source < 0 or not move_cell(source) or not dig():
                return False
            read_cell(source, heights, colors, tops, active)
            dirty(source, near, queue, queued)
            continue
        kind, first, second, needed = plan
        if kind == 0:
            if not move_cell(center):
                return False
            while get_pos_z() > needed:
                if not dig():
                    return False
                read_cell(center, heights, colors, tops, active)
            dirty(center, near, queue, queued)
            continue
        if kind == 4:
            if not push_to(center, second, size, near, heights, colors, tops, active):
                return False
        if not push_to(first, center, size, near, heights, colors, tops, active):
            return False
        dirty(first, near, queue, queued)
        dirty(center, near, queue, queued)
        if kind == 2:
            if not push_to(second, center, size, near, heights, colors, tops, active):
                return False
            dirty(second, near, queue, queued)
            dirty(center, near, queue, queued)
        elif kind == 3 or kind == 4:
            if not push_to(center, second, size, near, heights, colors, tops, active):
                return False
            dirty(second, near, queue, queued)
            dirty(center, near, queue, queued)
    return False


def plan_for(center, floor, near, heights, colors):
    z = heights[center]
    color = colors[center]
    neighbors = near[center]
    if color >= 0 and z > floor:
        for source in neighbors:
            if source < 0:
                continue
            if colors[source] == color and heights[source] > z:
                return 1, source, -1, z
    for first in neighbors:
        if first < 0:
            continue
        t = colors[first]
        if t < 0 or t == color or heights[first] <= z:
            continue
        for second in neighbors:
            if second < 0:
                continue
            if second != first and colors[second] == t and floor < heights[second] and heights[second] <= z:
                return 3, first, second, z
    best = None
    best_digs = 1000000
    for i in range(4):
        first = neighbors[i]
        if first < 0:
            continue
        t = colors[first]
        if t < 0:
            continue
        for j in range(i + 1, 4):
            second = neighbors[j]
            if second < 0:
                continue
            if colors[second] != t:
                continue
            a = first
            b = second
            if heights[a] > heights[b]:
                a = second
                b = first
            needed = min(heights[a] - 1, heights[b] - 2)
            if needed < floor:
                continue
            if z > needed:
                digs = z - needed
                if digs < best_digs:
                    best = 0, a, b, needed
                    best_digs = digs
            elif color != t:
                return 2, a, b, z
    if color >= 0 and z - 2 >= floor:
        for first in neighbors:
            if first < 0 or colors[first] != color or heights[first] != z:
                continue
            for second in neighbors:
                if second < 0:
                    continue
                if second != first and colors[second] != color and heights[second] <= z - 2:
                    return 4, first, second, z
    return best


def push_to(source, center, size, near, heights, colors, tops, active):
    if not move_cell(source):
        return False
    direction = None
    for i in range(4):
        if near[source][i] == center:
            direction = DIRECTIONS[i]
            break
    if direction == None or not push(direction):
        return False
    read_cell(source, heights, colors, tops, active)
    read_cell(center, heights, colors, tops, active, direction)
    return True


def read_cell(cell, heights, colors, tops, active, direction=None):
    old = colors[cell]
    if old >= 0:
        z = heights[cell]
        tops[z].remove(cell)
        if len(tops[z]) == 0:
            active.remove(z)
    z = get_pos_z(direction)
    color = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        color = measure(direction)
    heights[cell] = z
    colors[cell] = color
    if color >= 0:
        if z not in tops:
            tops[z] = set()
        tops[z].add(cell)
        active.add(z)


def enqueue(cell, queue, queued):
    if cell not in queued:
        queued.add(cell)
        queue.append(cell)


def dirty(cell, near, queue, queued):
    enqueue(cell, queue, queued)
    for other in near[cell]:
        if other >= 0:
            enqueue(other, queue, queued)


def move_to(tx, ty, size=None):
    if size == None:
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


def make_blocks():
    size = get_world_size()
    limit = max(1, size // 4)
    capacity = max_drones()
    gx = 1
    gy = 1
    best = 1
    for ty in range(1, limit + 1):
        tx = min(limit, capacity // ty)
        if tx * ty > best:
            best = tx * ty
            gx = tx
            gy = ty
    blocks = []
    for k in range(best):
        bx = k % gx
        by = k // gx
        blocks.append((bx * size // gx, (bx + 1) * size // gx,
                       by * size // gy, (by + 1) * size // gy))
    return blocks


DIRECTIONS = [North, East, South, West]

if __name__ == "__main__":
    lb_mushrooms()
