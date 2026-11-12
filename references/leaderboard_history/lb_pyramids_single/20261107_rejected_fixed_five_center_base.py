from __builtins__ import *
# 淘汰候选归档：lb_pyramids_single | 原实验路径 .codex/leaderboard-sol/underground-official/pyramids_single/fixed-five-center-base-candidate/lb_pyramids_single.py


def lb_pyramids_single():
    set_world_size(5)
    deadline = get_time() + 14400
    for cycle in range(512):
        if num_items(Items.Power) >= 30100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        if get_time() > deadline:
            quick_print("pyramids_failed", "deadline", cycle)
            return
        clear()
        began = get_time()
        if not pyramid_move_to(2, 2):
            return
        for _ in range(17):
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                break
            if get_pos_z() <= -16 or not dig():
                return
        ground = get_ground_type()
        if ground == Grounds.Sand:
            # 首次挖掘只有中心柱，遇到的Sand仍是原塔3层高顶面；基座由固定几何直接推得。
            floor = get_pos_z() - 3
            if not dig():
                return
        elif ground == Grounds.Limestone:
            floor = get_pos_z()
        else:
            return
        remaining = []
        base_filled = 0
        for x in range(5):
            for offset in range(5):
                y = offset
                if x % 2 != 0:
                    y = 4 - offset
                if not pyramid_move_to(x, y):
                    return
                for _ in range(17):
                    ground = get_ground_type()
                    if ground == Grounds.Sand or ground == Grounds.Limestone:
                        break
                    if get_pos_z() <= floor or not dig():
                        return
                z = get_pos_z()
                top = floor + 1 + min(x, 4 - x, y, 4 - y)
                if z < floor or z > top:
                    return
                if z == floor:
                    if not place(Grounds.Sand) or get_pos_z() != z + 1:
                        return
                    z += 1
                    base_filled += 1
                # 非中心柱最多2层，后续不挖穿基座，已读Sand高度不会继续塌落。
                if (x != 2 or y != 2) and z < top:
                    remaining.append((x, y, z, top))
        # 中心最高3层，必须在清理全部结束后重读，不挖掉本来完整的顶块。
        if not pyramid_move_to(2, 2):
            return
        z = get_pos_z()
        if z < floor + 1 or z > floor + 3:
            return
        if z < floor + 3:
            remaining.append((2, 2, z, floor + 3))
        cleaned = get_time()
        tasks = remaining
        # 中心顶块从入口阶段始终预留；先补第二层，最后补中心，才允许自动完成。
        for i in range(len(tasks)):
            x, y, z, top = tasks[i]
            if not pyramid_move_to(x, y) or get_pos_z() != z:
                return
            while z < top:
                if get_time() > deadline or not place(Grounds.Sand):
                    return
                z += 1
                if i + 1 != len(tasks) or z < top:
                    if get_pos_z() != z:
                        quick_print("pyramids_failed", "support", cycle, x, y, z)
                        return
        if not pyramid_move_to(2, 2) or get_entity_type() != Entities.Sunflower or not harvest():
            quick_print("pyramids_failed", "sunflower", cycle)
            return
        quick_print("pyramid_base_cycle", cycle, base_filled, len(tasks), cleaned - began,
                    get_time() - cleaned, get_time(), num_items(Items.Power))
    quick_print("pyramids_failed", "cycle_limit", get_time())


def pyramid_move_to(tx, ty):
    dx = (tx - get_pos_x()) % 5
    direction = East
    if dx > 2:
        direction = West
        dx = 5 - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % 5
    direction = North
    if dy > 2:
        direction = South
        dy = 5 - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_pyramids_single()
