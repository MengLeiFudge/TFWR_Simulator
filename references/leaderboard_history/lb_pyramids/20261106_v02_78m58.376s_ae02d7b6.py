from __builtins__ import *
# 历史提交归档：lb_pyramids | 初次提交 2026-11-06 (ae02d7b6) | 优化：金字塔多机保留沙体并按层修补
# 完整轮时间：4738.376秒（构建26462009，2轮官方完整统计；请求370）。


def lb_pyramids():
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Power) >= 150100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        clear()
        point = pyramid_find(get_time() + 600)
        if point == None or not pyramid_move_to(point[0], point[1]):
            quick_print("pyramids_failed", "find", cycle)
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Limestone:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Limestone:
            quick_print("pyramids_failed", "foundation", cycle)
            return
        bounds = pyramid_bounds(point[0], point[1], get_pos_z())
        if bounds == None:
            quick_print("pyramids_failed", "bounds", cycle)
            return
        x0, x1, y0, y1, floor = bounds
        if pyramid_dispatch(pyramid_clean_column, bounds) == None:
            quick_print("pyramids_failed", "clean", cycle)
            return
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        height = (x1 - x0 + 2) // 2
        if not pyramid_move_to(cx, cy):
            return
        # 只保留中心最后一块未放，禁止其他工人未结束时自动完成并清场。
        if get_pos_z() == floor + height:
            if get_ground_type() != Grounds.Sand or not dig():
                return
        if get_pos_z() >= floor + height or get_pos_z() < floor:
            quick_print("pyramids_failed", "center_height", cycle)
            return
        counts = pyramid_dispatch(pyramid_missing_column, bounds)
        if counts == None:
            quick_print("pyramids_failed", "count", cycle)
            return
        needed = 0
        for count in counts:
            needed += count
        if not pyramid_materials(bounds, needed):
            quick_print("pyramid_materials_missing", cycle, needed, num_items(Items.Block))
            continue
        quick_print("pyramid_sand_prepare", cycle, x1 - x0 + 1, needed, get_time())
        for layer in range(1, height):
            if pyramid_dispatch(pyramid_sand_column, bounds, layer) == None:
                quick_print("pyramids_failed", "repair", cycle, layer)
                return
        if not pyramid_move_to(cx, cy) or get_pos_z() != floor + height - 1:
            quick_print("pyramids_failed", "cap_height", cycle)
            return
        if not place(Grounds.Sand) or get_entity_type() != Entities.Sunflower:
            quick_print("pyramids_failed", "sunflower", cycle)
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


def pyramid_dispatch(job, bounds, layer=0):
    x0, x1, y0, y1, floor = bounds
    handles = []
    results = []
    inset = max(0, layer - 1)
    for x in range(x0 + inset, x1 - inset + 1):
        if num_drones() < max_drones():
            handle = spawn_drone(job, x, bounds, layer)
            if handle != None:
                handles.append(handle)
                continue
        results.append(job(x, bounds, layer))
    for handle in handles:
        results.append(wait_for(handle))
    for result in results:
        if result == None:
            return None
    return results


def pyramid_clean_column(x, bounds, _layer):
    x0, x1, y0, y1, floor = bounds
    for y in range(y0, y1 + 1):
        if not pyramid_move_to(x, y):
            return None
        while get_pos_z() > floor:
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                break
            if not dig():
                return None
        ground = get_ground_type()
        if get_pos_z() < floor or (ground != Grounds.Sand and ground != Grounds.Limestone):
            return None
    return 0


def pyramid_missing_column(x, bounds, _layer):
    # 只在所有清理和中心预留结束后读数，避免并发塌方使缓存失效。
    x0, x1, y0, y1, floor = bounds
    needed = 0
    for y in range(y0, y1 + 1):
        if not pyramid_move_to(x, y):
            return None
        height = 1 + min(x - x0, x1 - x, y - y0, y1 - y)
        z = get_pos_z()
        if z < floor or z > floor + height:
            return None
        needed += floor + height - z
    return needed


def pyramid_sand_column(x, bounds, layer):
    # 上一完整沙层完成后才推进；本层放置只依赖上一层的八邻支撑。
    x0, x1, y0, y1, floor = bounds
    inset = layer - 1
    for y in range(y0 + inset, y1 - inset + 1):
        if not pyramid_move_to(x, y):
            return None
        z = get_pos_z()
        if z < floor + layer:
            if z != floor + layer - 1 or not place(Grounds.Sand):
                return None
            if get_pos_z() != z + 1:
                return None
    return 0


def pyramid_materials(bounds, needed):
    # 只补实际缺块；基座以外的矿柱也不挖到石灰岩以下。
    x0, x1, y0, y1, floor = bounds
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
    lb_pyramids()
