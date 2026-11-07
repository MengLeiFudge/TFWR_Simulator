from __builtins__ import *
# 来源lb_treasure_map.py；保留去环路径，普通地形使用Jump和浅层钻头定位。


def gold_treasure_map():
    jump(Unlocks.Treasure_Map)
    first = True
    size = get_world_size()
    offsets = {'N': size, 'E': 1, 'S': -size, 'W': -1, 'D': size * size}
    directions = {'N': North, 'E': East, 'S': South, 'W': West}
    cycle = -1
    empty = 0
    while True:
        deadline = get_time() + 7200
        cycle += 1
        if not first:
            clear()
        first = False
        if not treasure_map_find(Grounds.Basalt, -128, -64, deadline):
            empty += 1
            quick_print('treasure_map_skip', cycle, get_pos_z())
            if empty >= 8:
                quick_print('treasure_map_failed', 'eight_empty_cycles', cycle)
                return
            continue
        map_z = get_pos_z() - 1
        location = measure()
        if location == None or not treasure_map_move_to(location[0], location[1]):
            quick_print('treasure_map_failed', 'map_location', cycle)
            return
        if not treasure_map_find(Grounds.Treasure_Map, map_z - 1, map_z + 16, deadline):
            quick_print('treasure_map_failed', 'find_map', cycle)
            return
        path = measure()
        if path == None:
            quick_print('treasure_map_failed', 'path', cycle)
            return
        began = get_time()
        start = get_pos_x() + size * get_pos_y()
        point = start
        exits = {}
        for step in path:
            exits[point] = step
            point += offsets[step]
        goal = point
        point = start
        planned = get_time()
        steps = 0
        while point != goal:
            if get_time() > deadline:
                quick_print('treasure_map_failed', 'deadline', cycle)
                return
            step = exits[point]
            if step == 'D':
                ok = dig()
            else:
                ok = move(directions[step])
            if not ok:
                quick_print('treasure_map_failed', 'action', cycle, step)
                return
            point += offsets[step]
            steps += 1
        if get_entity_type() != Entities.Underground_Treasure or not harvest():
            quick_print('treasure_map_failed', 'treasure', cycle, get_pos_x(), get_pos_y(), get_pos_z())
            return
        empty = 0
        quick_print('treasure_map_cycle', cycle, len(path), steps, began, planned, get_time(), num_items(Items.Gold))


def treasure_map_find(kind, limit, drill_to, deadline):
    drilling = get_pos_z() > drill_to and num_items(Items.Dynamite) > 0
    if drilling:
        change_hat(Hats.Explosive_Drill)
    else:
        change_hat(Hats.Mining_Hat)
    for _ in range(256):
        if get_ground_type() == kind:
            change_hat(Hats.Mining_Hat)
            return True
        if get_pos_z() <= limit or get_time() > deadline or get_hardness() >= 10000000:
            change_hat(Hats.Mining_Hat)
            return False
        if drilling and (get_pos_z() <= drill_to or num_items(Items.Dynamite) < 1):
            change_hat(Hats.Mining_Hat)
            drilling = False
        if not dig():
            change_hat(Hats.Mining_Hat)
            return False
    change_hat(Hats.Mining_Hat)
    return False


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
    gold_treasure_map()
