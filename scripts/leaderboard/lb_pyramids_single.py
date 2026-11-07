from __builtins__ import *
# 完整轮时间：1162.559秒（构建26462009，7轮官方完整统计；请求438）。


def lb_pyramids_single():
    set_world_size(5)
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Power) >= 30100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        clear()
        # 金字塔最小边长5；在5×5专用盘中足印固定，角柱最多只有一块沙。
        for _ in range(17):
            if get_ground_type() == Grounds.Limestone:
                break
            if get_pos_z() <= -16 or not dig():
                quick_print("pyramids_failed", "foundation", cycle)
                return
        if get_ground_type() != Grounds.Limestone:
            quick_print("pyramids_failed", "foundation_limit", cycle)
            return
        floor = get_pos_z()
        found = get_time()
        holes = []
        needed = 1
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
                        quick_print("pyramids_failed", "clean", cycle, x, y)
                        return
                z = get_pos_z()
                top = floor + 1 + min(x, 4 - x, y, 4 - y)
                if z < floor or z > top:
                    quick_print("pyramids_failed", "height", cycle, x, y, z, top)
                    return
                # 非中心柱最高2层；全场不挖穿基座，稳定性2保证其已露沙顶不再塌落。
                # 中心高度3另行重读并留顶块，不使用这次可能被后续挖掘改变的读数。
                if (x != 2 or y != 2) and z < top:
                    holes.append((x, y, z, top))
                    needed += top - z
        if not pyramid_move_to(2, 2):
            return
        if get_pos_z() == floor + 3:
            if not dig():
                return
        z = get_pos_z()
        if z < floor or z > floor + 2:
            quick_print("pyramids_failed", "center", cycle, z)
            return
        if z < floor + 2:
            holes.append((2, 2, z, floor + 2))
            needed += floor + 2 - z
        if num_items(Items.Block) < needed:
            # 重生保留已采Block；不为补料挖穿本塔基座。
            quick_print("pyramid_materials_retry", cycle, needed, num_items(Items.Block))
            continue
        prepared = get_time()
        for layer in range(1, 3):
            target = floor + layer
            for x, y, z, top in holes:
                if z >= target or top < target:
                    continue
                if not pyramid_move_to(x, y):
                    return
                if get_pos_z() != target - 1 or not place(Grounds.Sand) or get_pos_z() != target:
                    quick_print("pyramids_failed", "repair", cycle, x, y, layer)
                    return
        if not pyramid_move_to(2, 2) or get_pos_z() != floor + 2:
            return
        if not place(Grounds.Sand) or get_entity_type() != Entities.Sunflower or not harvest():
            quick_print("pyramids_failed", "sunflower", cycle)
            return
        quick_print("pyramid_cycle", cycle, 5, needed, found, prepared, get_time(), num_items(Items.Power))
        if get_time() - began > 14400:
            quick_print("pyramids_failed", "deadline", cycle)
            return
    quick_print("pyramids_failed", "cycle_limit", get_time(), num_items(Items.Power))


def pyramid_move_to(tx, ty):
    # 固定5格世界；沿环绕最短距离转移，所有施工都由同一无人机完成。
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
