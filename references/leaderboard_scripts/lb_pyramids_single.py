from __builtins__ import *
# 完整轮时间：未取得（识别基座后彩块重建，尚无官方完整统计）。

def lb_pyramids_single():
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Power) >= 30100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        clear()
        point = pyramid_find(get_time() + 600)
        if point == None:
            quick_print("pyramids_failed", "find", cycle)
            return
        if not pyramid_move_to(point[0], point[1]):
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Limestone:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Limestone:
            quick_print("pyramids_failed", "foundation", cycle)
            return
        floor = get_pos_z()
        bounds = pyramid_bounds(point[0], point[1], floor)
        if bounds == None:
            quick_print("pyramids_failed", "bounds", cycle)
            return
        x0, x1, y0, y1, floor = bounds
        if not pyramid_dispatch(pyramid_clear_column, bounds):
            quick_print("pyramids_failed", "clear", cycle)
            return
        if not pyramid_materials(bounds):
            quick_print("pyramid_materials_missing", cycle, num_items(Items.Block))
            continue
        if not pyramid_dispatch(pyramid_build_column, bounds):
            quick_print("pyramids_failed", "build", cycle)
            return
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        if not pyramid_move_to(cx, cy) or get_entity_type() != Entities.Sunflower:
            quick_print("pyramids_failed", "sunflower", cycle, cx, cy)
            return
        while not can_harvest():
            if get_time() - began > 14400:
                return
            do_a_flip()
        if not harvest():
            return
        quick_print("pyramid_cycle", cycle, x1 - x0 + 1, floor, get_time(), num_items(Items.Power))
        if get_time() - began > 14400:
            quick_print("pyramids_failed", "deadline", cycle)
            return
    quick_print("pyramids_failed", "cycle_limit", get_time(), num_items(Items.Power))


def pyramid_find(deadline):
    # 最小底边5格，每4格采样必交到底面；每轮只推进同一深度，保护基座。
    size = get_world_size()
    for layer in range(128):
        handles = []
        found = None
        for x in range(0, size, 4):
            if num_drones() < max_drones():
                handle = spawn_drone(pyramid_probe_column, x, -layer)
                if handle != None:
                    handles.append(handle)
                    continue
            point = pyramid_probe_column(x, -layer)
            if point != None:
                found = point
        for handle in handles:
            point = wait_for(handle)
            if point != None:
                found = point
        if found != None:
            return found
        if get_time() > deadline:
            return None
    return None


def pyramid_probe_column(x, target):
    size = get_world_size()
    for y in range(0, size, 4):
        if not pyramid_move_to(x, y):
            return None
        while get_pos_z() > target:
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                return x, y
            if not dig():
                return None
        ground = get_ground_type()
        if ground == Grounds.Sand or ground == Grounds.Limestone:
            return x, y
    return None


def pyramid_floor_at(x, y, floor):
    if not pyramid_move_to(x, y):
        return False
    while get_pos_z() > floor:
        if not dig():
            return False
    return get_pos_z() == floor and get_ground_type() == Grounds.Limestone


def pyramid_bounds(x, y, floor):
    # 沿穿过已知基座的两条轴找矩形边界，随后逐格清理再次核实基座。
    size = get_world_size()
    x0 = x
    x1 = x
    y0 = y
    y1 = y
    for tx in range(x - 1, -1, -1):
        if not pyramid_floor_at(tx, y, floor):
            break
        x0 = tx
    for tx in range(x + 1, size):
        if not pyramid_floor_at(tx, y, floor):
            break
        x1 = tx
    for ty in range(y - 1, -1, -1):
        if not pyramid_floor_at(x, ty, floor):
            break
        y0 = ty
    for ty in range(y + 1, size):
        if not pyramid_floor_at(x, ty, floor):
            break
        y1 = ty
    length = x1 - x0 + 1
    if length < 5 or length % 2 != 1 or y1 - y0 + 1 != length:
        return None
    return x0, x1, y0, y1, floor


def pyramid_dispatch(job, bounds):
    x0, x1, y0, y1, floor = bounds
    handles = []
    ok = True
    for x in range(x0, x1 + 1):
        if num_drones() < max_drones():
            handle = spawn_drone(job, x, bounds)
            if handle != None:
                handles.append(handle)
                continue
        if not job(x, bounds):
            ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def pyramid_clear_column(x, bounds):
    x0, x1, y0, y1, floor = bounds
    for y in range(y0, y1 + 1):
        if not pyramid_floor_at(x, y, floor):
            return False
    return True


def pyramid_materials(bounds):
    # 完整彩块体积逐层求和；只挖基座以外且不低于基座的柱，避免损伤石灰岩。
    x0, x1, y0, y1, floor = bounds
    length = x1 - x0 + 1
    needed = 0
    for side in range(length, 0, -2):
        needed += side * side
    size = get_world_size()
    for x in range(size):
        for y in range(size):
            if num_items(Items.Block) >= needed:
                return True
            if x0 <= x and x <= x1 and y0 <= y and y <= y1:
                continue
            if not pyramid_move_to(x, y):
                return False
            while get_pos_z() > floor:
                if num_items(Items.Block) >= needed:
                    return True
                if not dig():
                    return False
    return num_items(Items.Block) >= needed


def pyramid_build_column(x, bounds):
    x0, x1, y0, y1, floor = bounds
    for y in range(y0, y1 + 1):
        if not pyramid_move_to(x, y):
            return False
        height = 1 + min(x - x0, x1 - x, y - y0, y1 - y)
        for _ in range(height):
            if not place(Grounds.Block_Red):
                return False
    return True


def pyramid_move_to(tx, ty):
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
    lb_pyramids_single()
