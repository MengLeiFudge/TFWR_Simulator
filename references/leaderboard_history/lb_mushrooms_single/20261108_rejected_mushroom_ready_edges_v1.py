from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-ready-edges-v1/lb_mushrooms_single.py

def lb_mushrooms_single():
    global heights
    global colors
    global buckets
    global remaining
    global ready
    global edges
    global incident
    global adjacent
    global wrap_distance
    size = get_world_size()
    count = size * size
    edges = []
    incident = []
    adjacent = []
    for cell in range(count):
        incident.append([])
        x = cell % size
        y = cell // size
        adjacent.append([((y + 1) % size * size + x, North),
                         (y * size + (x + 1) % size, East),
                         ((y - 1) % size * size + x, South),
                         (y * size + (x - 1) % size, West)])
    for cell in range(count):
        for other, direction in adjacent[cell][:2]:
            back = South
            if direction == East:
                back = West
            edge = len(edges)
            edges.append((cell, other, direction, back))
            incident[cell].append(edge)
            incident[other].append(edge)
    wrap_distance = []
    for step in range(size):
        wrap_distance.append(min(step, size - step))
    route = []
    for y in range(size):
        for offset in range(size):
            x = offset
            if y % 2:
                x = size - 1 - offset
            route.append(x + y * size)
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
        highest = get_pos_z()
        heights = []
        colors = []
        for cell in range(count):
            heights.append(highest)
            colors.append(-1)
        buckets = {}
        remaining = 0
        ready = set()
        where = 0
        for cell in route:
            if not move_to(cell % size, cell // size, size):
                return
            for step in range(256):
                if get_pos_z() <= highest:
                    break
                if not dig():
                    return
            read_cell(cell)
            where = cell
        for edge in range(len(edges)):
            refresh_edge(edge)
        pairs = 0
        digs = 0
        for step in range(4096):
            if remaining == 0 or num_items(Items.Mushroom) >= 30000:
                break
            while highest not in buckets or len(buckets[highest]) == 0:
                highest -= 1
            match = choose_edge(where, size, highest - 2)
            if match != None:
                source, target, direction, edge = match
                if source != where and not move_to(source % size, source // size, size):
                    return
                where = source
                if get_pos_z() != heights[source] or get_ground_type() != Grounds.Mushroom or measure() != colors[source]:
                    quick_print("mushrooms_failed", "cache_source", batch, source)
                    return
                if get_pos_z(direction) != heights[target] or get_ground_type(direction) != Grounds.Mushroom or measure(direction) != colors[target]:
                    quick_print("mushrooms_failed", "cache_target", batch, target)
                    return
                if not push(direction):
                    return
                pairs += 1
                read_cell(source)
                read_cell(target, direction)
                for changed in incident[source]:
                    refresh_edge(changed)
                for changed in incident[target]:
                    if changed != edge:
                        refresh_edge(changed)
                continue
            source = -1
            if colors[where] >= 0 and heights[where] == highest:
                source = where
            else:
                for other, direction in adjacent[where]:
                    if colors[other] >= 0 and heights[other] == highest:
                        source = other
                        break
            if source < 0:
                for other in buckets[highest]:
                    source = other
                    break
            if source != where and not move_to(source % size, source // size, size):
                return
            where = source
            if get_pos_z() != heights[source] or get_ground_type() != Grounds.Mushroom or measure() != colors[source]:
                quick_print("mushrooms_failed", "cache_dig", batch, source)
                return
            if not dig():
                return
            digs += 1
            read_cell(source)
            for edge in incident[source]:
                refresh_edge(edge)
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom), "pairs", pairs, "digs", digs)
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def read_cell(cell, direction=None):
    global remaining
    if colors[cell] >= 0:
        buckets[heights[cell]].remove(cell)
        remaining -= 1
    heights[cell] = get_pos_z(direction)
    colors[cell] = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        colors[cell] = measure(direction)
        if heights[cell] not in buckets:
            buckets[heights[cell]] = set()
        buckets[heights[cell]].add(cell)
        remaining += 1


def refresh_edge(edge):
    a, b, direction, back = edges[edge]
    if colors[a] >= 0 and colors[a] == colors[b] and heights[a] != heights[b]:
        ready.add(edge)
    elif edge in ready:
        ready.remove(edge)


def choose_edge(where, size, floor):
    best = None
    best_distance = size + size
    x = where % size
    y = where // size
    for edge in ready:
        a, b, direction, back = edges[edge]
        if heights[a] < heights[b]:
            a, b = b, a
            direction = back
        if heights[b] < floor:
            continue
        if a == where:
            return a, b, direction, edge
        distance = wrap_distance[a % size - x] + wrap_distance[a // size - y]
        if distance < best_distance:
            best_distance = distance
            best = (a, b, direction, edge)
    return best


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


if __name__ == "__main__":
    lb_mushrooms_single()
