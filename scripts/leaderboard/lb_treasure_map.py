from __builtins__ import *
# 完整轮时间：本版尚无实机成绩；原版目标本地对照见同名策略文档。


def lb_treasure_map():
    clear()
    treasure_move(3, 3)
    shifts = {"E": 1, "W": -1, "N": 10, "S": -10, "D": 100}
    for cycle in range(64):
        if num_items(Items.Gold) >= 115000:
            quick_print("treasure_map_done", get_time(), num_items(Items.Gold))
            return
        for _ in range(256):
            if get_ground_type() == Grounds.Basalt:
                break
            if not dig():
                quick_print("treasure_map_failed", "basalt", cycle)
                return
        target = measure()
        if target == None or not treasure_tunnel(target[0], target[1]):  # ty: ignore[not-subscriptable] Basalt测量返回坐标元组。
            quick_print("treasure_map_failed", "tunnel", cycle)
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Treasure_Map:
                break
            if not dig():
                return
        path = measure()
        if path == None:
            return
        start = get_pos_y() * 10 + get_pos_x()
        point = start
        cells = {start}
        for step in path:  # ty: ignore[not-iterable] Treasure_Map测量返回方向字符串。
            point += shifts[step]  # ty: ignore[invalid-argument-type] 方向字符串逐字符解析。
            cells.add(point)
        goal = point
        if not dig():
            return
        point = start + 100
        while point != goal:
            if point + 100 not in cells:
                point = treasure_exit(cells, point)
                if point == None:
                    return
            if not dig():
                return
            point += 100
        if get_entity_type() != Entities.Underground_Treasure or not harvest():
            quick_print("treasure_map_failed", "reward", cycle)
            return
        quick_print("treasure_map_cycle", cycle, get_time(), num_items(Items.Gold))


def treasure_exit(cells, start):
    # 只在公开路径的同一层搜索；下挖仍要求上下两个格子都在路径上。
    queue = [start]
    previous = {start: start}
    head = 0
    found = None
    while head < len(queue) and found == None:
        point = queue[head]
        head += 1
        for offset in [1, -1, 10, -10]:
            neighbor = point + offset
            if neighbor in cells and neighbor not in previous:
                previous[neighbor] = point
                if neighbor + 100 in cells:
                    found = neighbor
                    break
                queue.append(neighbor)
    if found == None:
        quick_print("treasure_map_failed", "exit", start)
        return None
    directions = {1: East, -1: West, 10: North, -10: South}
    route = []
    point = found
    while point != start:
        parent = previous[point]
        route.append(directions[point - parent])
        point = parent
    for i in range(len(route) - 1, -1, -1):
        if not move(route[i]):
            return None
    return found


def treasure_tunnel(tx, ty):
    # Basalt横移时只清除中间柱，借坍塌降低下一柱；末柱交给找图循环。
    dx = tx - get_pos_x()
    dy = ty - get_pos_y()
    horizontal = East
    if dx < 0:
        dx = -dx
        horizontal = West
    vertical = North
    if dy < 0:
        dy = -dy
        vertical = South
    left = dx + dy
    for direction, count in [(horizontal, dx), (vertical, dy)]:
        for _ in range(count):
            if not move(direction):
                return False
            left -= 1
            if left and not dig():
                return False
    return True


def treasure_move(tx, ty):
    size = get_world_size()
    for target, current, positive, negative in [(tx, get_pos_x(), East, West), (ty, get_pos_y(), North, South)]:
        count = (target - current) % size
        direction = positive
        if count > size // 2:
            direction = negative
            count = size - count
        for _ in range(count):
            move(direction)


if __name__ == "__main__":
    lb_treasure_map()
