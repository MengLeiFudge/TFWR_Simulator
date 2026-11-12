from __builtins__ import *
# 淘汰候选归档：lb_treasure_map | 原实验路径 .codex/leaderboard-sol/underground-official/treasure_map/last-rank-reset8-candidate/lb_treasure_map.py


def lb_treasure_map():
    clear()
    size = get_world_size()
    stride = size + 1
    offsets = {"N": stride, "E": 1, "S": -stride, "W": -1, "D": stride * stride}
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
        start = get_pos_x() + stride * get_pos_y()
        point = start
        exits = {}
        # 每行与每层留空隙，邻格查询不会误把地图边缘接到下一行。
        for i in range(len(path)):
            exits[point] = i
            point += offsets[path[i]]
        goal = point
        point = start
        planned = get_time()
        steps = 0
        # 每次跟随最后出口，原串中的最后出现索引严格增加，故不会产生新环。
        while point != goal:
            if get_time() > deadline:
                quick_print("treasure_map_failed", "deadline", cycle)
                return
            rank = exits[point]
            step = path[rank]
            if step == "D":
                ok = dig()
            else:
                # 只选择同层公开通路中更靠后的格子，原串索引严格递增。
                for direction in "NESW":
                    neighbor = point + offsets[direction]
                    if neighbor in exits and exits[neighbor] > rank:
                        rank = exits[neighbor]
                        step = direction
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
