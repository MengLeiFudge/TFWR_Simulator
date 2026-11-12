from __builtins__ import *
# 淘汰候选归档：lb_treasure_map | 原实验路径 .codex/over50-screen-20261109/lb_treasure_map_stack.py


def lb_treasure_map():
    clear()
    size = get_world_size()
    offsets = {"N": size, "E": 1, "S": -size, "W": -1, "D": size * size}
    directions = {"N": North, "E": East, "S": South, "W": West}
    deadline = get_time() + 7200
    for cycle in range(256):
        if num_items(Items.Gold) >= 115000:
            quick_print("treasure_map_done", True, get_time(), num_items(Items.Gold))
            return
        clear()
        for _ in range(256):
            if get_ground_type() == Grounds.Basalt:
                break
            if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                quick_print("treasure_map_failed", "find_basalt", cycle)
                return
        if get_ground_type() != Grounds.Basalt:
            quick_print("treasure_map_failed", "basalt_limit", cycle)
            return
        location = measure()
        if location == None or not treasure_map_move_to(location[0], location[1]):
            quick_print("treasure_map_failed", "map_location", cycle)
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Treasure_Map:
                break
            if get_time() > deadline or not dig():
                quick_print("treasure_map_failed", "find_map", cycle)
                return
        if get_ground_type() != Grounds.Treasure_Map:
            quick_print("treasure_map_failed", "map_limit", cycle)
            return
        path = measure()
        if path == None:
            quick_print("treasure_map_failed", "path", cycle)
            return
        began = get_time()
        start = get_pos_x() + size * get_pos_y()
        point = start
        vertices = [start]
        positions = {start: 0}
        route = []
        # 公开路径的在线消环；深度单调，下降不会被跨层消除。
        for step in path:
            point += offsets[step]
            if point in positions:
                keep = positions[point]
                while len(route) > keep:
                    route.pop()
                    positions.pop(vertices.pop())
            else:
                route.append(step)
                positions[point] = len(route)
                vertices.append(point)
        goal = point
        point = start
        planned = get_time()
        steps = 0
        # 每次跟随最后出口，原串中的最后出现索引严格增加，故不会产生新环。
        for step in route:
            if get_time() > deadline:
                quick_print("treasure_map_failed", "deadline", cycle)
                return
            if step == "D":
                ok = dig()
            else:
                ok = move(directions[step])
            if not ok:
                quick_print("treasure_map_failed", "action", cycle, step)
                return
            point += offsets[step]
            steps += 1
        if get_entity_type() != Entities.Underground_Treasure or not harvest():
            quick_print("treasure_map_failed", "treasure", cycle, get_pos_x(), get_pos_y(), get_pos_z())
            return
        quick_print("treasure_map_cycle", cycle, len(path), steps, began, planned, get_time(), num_items(Items.Gold))
    quick_print("treasure_map_failed", "cycle_limit", get_time(), num_items(Items.Gold))


def treasure_map_move_to(tx, ty):
    # 仅用于读图前定位；已激活地图内只能沿公开路径的有效坐标移动。
    size = get_world_size()
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_treasure_map()
