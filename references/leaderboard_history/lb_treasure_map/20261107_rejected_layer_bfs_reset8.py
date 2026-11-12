from __builtins__ import *
# 淘汰候选归档：lb_treasure_map | 原实验路径 .codex/leaderboard-sol/underground-official/treasure_map/layer-bfs-reset8-candidate/lb_treasure_map.py


def lb_treasure_map():
    clear()
    size = get_world_size()
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
        route = treasure_map_shortest_path(path, size)
        if route == None:
            quick_print("treasure_map_failed", "disconnected", cycle)
            return
        planned = get_time()
        steps = len(route)
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
        if get_entity_type() != Entities.Underground_Treasure or not harvest():
            quick_print("treasure_map_failed", "treasure", cycle, get_pos_x(), get_pos_y(), get_pos_z())
            return
        quick_print("treasure_map_cycle", cycle, len(path), steps, began, planned, get_time(), num_items(Items.Gold))
    quick_print("treasure_map_failed", "cycle_limit", get_time(), num_items(Items.Gold))


def treasure_map_shortest_path(path, size):
    # 各行、各层留一格空隙，整数相邻值不会把地图两边误接起来。
    stride = size + 1
    layer = stride * stride
    offsets = {"N": stride, "E": 1, "S": -stride, "W": -1, "D": layer}
    point = get_pos_x() + stride * get_pos_y()
    start = point
    cells = set()
    descents = []
    for step in path:
        cells.add(point)
        if step == "D":
            descents.append(point)
        point += offsets[step]
    route = []
    for target in descents:
        if start != target:
            parents = {start: None}
            queue = [start]
            head = 0
            while head < len(queue) and target not in parents:
                point = queue[head]
                head += 1
                for step in "NESW":
                    neighbor = point + offsets[step]
                    if neighbor in cells and neighbor not in parents:
                        parents[neighbor] = (point, step)
                        queue.append(neighbor)
            if target not in parents:
                return None
            reverse = []
            point = target
            while point != start:
                point, step = parents[point]
                reverse.append(step)
            for i in range(len(reverse) - 1, -1, -1):
                route.append(reverse[i])
        # 只在原串规定的下降口下降，不把同层捷径扩大为任意竖直挖掘。
        route.append("D")
        start = target + layer
    return route


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
