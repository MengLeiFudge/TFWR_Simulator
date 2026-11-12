from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261109/mushroom-local-templates-v1/lb_mushrooms_single.py

def lb_mushrooms_single():
    size = get_world_size()
    area = size * size
    near = []
    for cell in range(area):
        x = cell % size
        y = cell // size
        near.append([x + ((y + 1) % size) * size, (x + 1) % size + y * size,
                     x + ((y - 1) % size) * size, (x - 1) % size + y * size])
    for batch in range(128):
        if num_items(Items.Mushroom) >= 30000:
            return
        clear()
        found = False
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                found = True
                break
            if not dig():
                break
        if not found:
            quick_print("mushrooms_failed", "find", batch)
            return
        top = get_pos_z()
        heights = []
        colors = []
        tops = {}
        active = set()
        for cell in range(area):
            heights.append(0)
            colors.append(-1)
        for y in range(size):
            for offset in range(size):
                x = offset
                if y % 2 != 0:
                    x = size - 1 - offset
                if not move_to(x, y, size):
                    return
                for step in range(256):
                    if get_pos_z() <= top:
                        break
                    if not dig():
                        return
                read_cell(x + y * size, heights, colors, tops, active)
        quick_print("mushrooms_prepared", batch, get_time(), top)
        if not work_field(size, near, heights, colors, tops, active):
            quick_print("mushrooms_failed", "field", batch)
            return
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def work_field(size, near, heights, colors, tops, active):
    queue = []
    queued = set()
    highest = 1000000
    for turn in range(2048):
        if num_items(Items.Mushroom) >= 30000 or len(active) == 0:
            return True
        new_highest = max(active)
        if highest != new_highest:
            highest = new_highest
            for cell in range(size * size):
                enqueue(cell, queue, queued)
        center = -1
        plan = None
        while len(queue) > 0:
            center = queue.pop()
            queued.remove(center)
            plan = plan_for(center, highest - 3, near, heights, colors)
            if plan != None:
                break
        if plan == None:
            source = -1
            for cell in tops[highest]:
                source = cell
                break
            if source < 0 or not move_to(source % size, source // size, size) or not dig():
                return False
            read_cell(source, heights, colors, tops, active)
            dirty(source, near, queue, queued)
            continue
        kind, first, second, needed = plan
        if kind == 0:
            if not move_to(center % size, center // size, size):
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
            if colors[source] == color and heights[source] > z:
                return 1, source, -1, z
    for first in neighbors:
        t = colors[first]
        if t < 0 or t == color or heights[first] <= z:
            continue
        for second in neighbors:
            if second != first and colors[second] == t and floor < heights[second] and heights[second] <= z:
                return 3, first, second, z
    best = None
    best_digs = 1000000
    for i in range(4):
        first = neighbors[i]
        t = colors[first]
        if t < 0:
            continue
        for j in range(i + 1, 4):
            second = neighbors[j]
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
            if colors[first] != color or heights[first] != z:
                continue
            for second in neighbors:
                if second != first and colors[second] != color and heights[second] <= z - 2:
                    return 4, first, second, z
    return best


def push_to(source, center, size, near, heights, colors, tops, active):
    if not move_to(source % size, source // size, size):
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
        enqueue(other, queue, queued)


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


DIRECTIONS = [North, East, South, West]


if __name__ == "__main__":
    lb_mushrooms_single()
