from __builtins__ import *
import farm_support


def gold_treasure_map():
    # 持续寻找普通地下藏宝图，沿合法路线收取宝藏。
    farm_support.run(Items.Gold, collect)


def collect(goal):
    # 复用排行榜的逐层去环路线；普通地形不假定固定地图深度。
    if not farm_support.require(Unlocks.Treasure_Map) or not farm_support.require(Unlocks.Mining):
        return False
    if not farm_support.require(Unlocks.Underground_Senses):
        return False
    empty = 0
    while num_items(Items.Gold) < goal:
        clear()
        found = False
        for _ in range(256):
            if get_ground_type() == Grounds.Basalt:
                found = True
                break
            if get_hardness() >= 10000000 or not dig():
                break
        if not found:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有找到可达的藏宝图，停止。")
                return False
            continue
        location = measure()
        if location == None or not farm_support.move_to(location[0], location[1]):  # ty: ignore[not-subscriptable]  玄武岩measure返回地图坐标。
            return False
        for _ in range(32):
            if get_ground_type() == Grounds.Treasure_Map:
                break
            if get_hardness() >= 10000000 or not dig():
                return False
        if get_ground_type() != Grounds.Treasure_Map:
            return False
        path = measure()
        if path == None or not follow(path):
            quick_print("藏宝图路线执行失败，停止。")
            return False
        empty = 0
    return True


def follow(path):
    # 同层同坐标只保留原路线最后出口；层号用size²区分，去环不跨层捷径。
    size = get_world_size()
    offsets = {"N": size, "E": 1, "S": -size, "W": -1, "D": size * size}
    directions = {"N": North, "E": East, "S": South, "W": West}
    point = get_pos_x() + size * get_pos_y()
    start = point
    exits = {}
    for step in path:
        if step not in offsets:
            return False
        exits[point] = step
        point += offsets[step]
    goal = point
    point = start
    for _ in range(len(path) + 1):
        if point == goal:
            return get_entity_type() == Entities.Underground_Treasure and harvest()
        if point not in exits:
            return False
        step = exits[point]
        if step == "D":
            if not dig():
                return False
        elif not move(directions[step]):
            return False
        point += offsets[step]
    return False


if __name__ == "__main__":
    gold_treasure_map()
