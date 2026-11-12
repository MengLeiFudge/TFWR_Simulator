from __builtins__ import *
# 历史提交归档：lb_treasure_map | 初次提交 2026-11-06 (8b327985) | 文档：补齐其余十个地下榜的正式实机基线
# 完整轮时间：277.200秒（构建26462009，26轮官方完整统计；请求354）。

def lb_treasure_map():
    clear()
    deadline = get_time() + 7200
    for cycle in range(256):
        if num_items(Items.Gold) >= 115000:
            quick_print("treasure_map_done", True, get_time(), num_items(Items.Gold))
            return
        found = False
        for _ in range(256):
            if get_ground_type() == Grounds.Basalt:
                found = True
                break
            if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                quick_print("treasure_map_failed", "find_basalt", cycle)
                return
        if not found:
            quick_print("treasure_map_failed", "basalt_limit", cycle)
            return
        location = measure()
        if location == None or not treasure_map_move_to(location[0], location[1]):
            quick_print("treasure_map_failed", "map_location", cycle)
            return
        found = False
        for _ in range(32):
            if get_ground_type() == Grounds.Treasure_Map:
                found = True
                break
            if get_time() > deadline or not dig():
                return
        if not found:
            quick_print("treasure_map_failed", "find_map", cycle)
            return
        # 地图只读一次；包括回头路在内的每个字符都由同一无人机执行。
        path = measure()
        if path == None:
            quick_print("treasure_map_failed", "path", cycle)
            return
        began = get_time()
        for step in path:
            if get_time() > deadline:
                quick_print("treasure_map_failed", "deadline", cycle)
                return
            if step == "D":
                ok = dig()
            elif step == "N":
                ok = move(North)
            elif step == "E":
                ok = move(East)
            elif step == "S":
                ok = move(South)
            elif step == "W":
                ok = move(West)
            else:
                quick_print("treasure_map_failed", "unknown_step", step)
                return
            if not ok:
                quick_print("treasure_map_failed", "action", cycle, step)
                return
        if get_entity_type() != Entities.Underground_Treasure or not harvest():
            quick_print("treasure_map_failed", "treasure", cycle, get_pos_x(), get_pos_y(), get_pos_z())
            return
        quick_print("treasure_map_cycle", cycle, len(path), began, get_time(), num_items(Items.Gold))
    quick_print("treasure_map_failed", "cycle_limit", get_time(), num_items(Items.Gold))


def treasure_map_move_to(tx, ty):
    # 只用于读图前定位；路线执行期间不调用此方法、不简化路径。
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
