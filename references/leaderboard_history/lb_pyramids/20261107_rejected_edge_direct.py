from __builtins__ import *
# 淘汰候选归档：lb_pyramids | 原实验路径 .codex/leaderboard-sol/underground-official/pyramids/edge-direct-candidate/lb_pyramids.py


def lb_pyramids():
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Power) >= 150100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        if get_time() - began > 14400:
            quick_print("pyramids_failed", "deadline", cycle)
            return
        clear()
        start = get_time()
        point = pyramid_find(get_time() + 600)
        if point == None:
            continue
        if point == False or not pyramid_move_to(point[0], point[1]):
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Limestone:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Limestone:
            return
        found = get_time()
        bounds = pyramid_edge_bounds(point[0], point[1], get_pos_z())
        if bounds == None:
            quick_print("pyramids_failed", "bounds", cycle)
            return
        located = get_time()
        x0, x1, y0, y1, floor = bounds
        if pyramid_dispatch(pyramid_clean_column, bounds) == None:
            return
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        height = (x1 - x0 + 2) // 2
        if not pyramid_move_to(cx, cy):
            return
        if get_pos_z() == floor + height and not dig():
            return
        cleaned = get_time()
        repaired = True
        for layer in range(1, height):
            if pyramid_dispatch(pyramid_direct_layer, bounds, layer) == None:
                repaired = False
                break
        if not repaired:
            quick_print("pyramid_skip_materials", cycle, num_items(Items.Block), get_time())
            continue
        if not pyramid_move_to(cx, cy) or get_pos_z() != floor + height - 1:
            return
        if not place(Grounds.Sand) or get_entity_type() != Entities.Sunflower or not harvest():
            return
        quick_print("pyramid_direct_cycle", cycle, x1 - x0 + 1, found - start,
                    located - found, cleaned - located, get_time() - cleaned,
                    get_time(), num_items(Items.Power))
    quick_print("pyramids_failed", "cycle_limit", get_time())


def pyramid_edge_bounds(x, y, floor):
    # 先找到西边，再沿西边走到南端；沿南边量出边长，正方形决定另一端。
    west = pyramid_boundary((x, y), floor, (-1, 0))
    if west == None:
        return None
    corner = pyramid_boundary(west, floor, (0, -1))
    if corner == None:
        return None
    east = pyramid_boundary(corner, floor, (1, 0))
    if east == None:
        return None
    x0, y0 = corner
    x1 = east[0]
    length = x1 - x0 + 1
    if length < 5 or length % 2 != 1 or y0 + length > get_world_size():
        return None
    return x0, x1, y0, y0 + length - 1, floor


def pyramid_direct_layer(x, bounds, layer):
    # 本层足印固定；完整上一层已就绪，只核对实际高度并补当前缺块。
    x0, x1, y0, y1, floor = bounds
    target = floor + layer
    for y in range(y0 + layer - 1, y1 - layer + 2):
        if not pyramid_move_to(x, y):
            return None
        z = get_pos_z()
        if z < target:
            if z != target - 1 or not place(Grounds.Sand) or get_pos_z() != target:
                return None
    return 0


def pyramid_find(deadline):
    # 专用盘第一块地层深16格。中央抽样覆盖所有边长超过半场的大塔，空样本重生。
    size = get_world_size()
    x = size // 2
    y = x
    if not pyramid_move_to(x, y):
        return False
    for _ in range(17):
        ground = get_ground_type()
        if ground == Grounds.Sand or ground == Grounds.Limestone:
            break
        if get_pos_z() <= -16:
            return None
        if get_time() > deadline or not dig():
            return False
    if get_ground_type() == Grounds.Limestone:
        return x, y
    if get_ground_type() != Grounds.Sand:
        return None
    # 完好塔面相邻高度差至多1；遇缺口或足印外格便回到上一沙柱读基座。
    # 多数样本在外圈只挖1块沙，避免在塔心钻深孔诱发大面积塌方。
    for tx in range(x - 1, -1, -1):
        limit = get_pos_z() - 1
        if not move(West):
            return False
        while get_pos_z() > limit:
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                break
            if not dig():
                return False
        ground = get_ground_type()
        if ground == Grounds.Limestone:
            return tx, y
        if ground != Grounds.Sand:
            if not move(East):
                return False
            return tx + 1, y
    return 0, y


def pyramid_floor_at(x, y, floor):
    # 遇到沙柱已能证明在足印内，找边界无需把整条轴钻穿到基座。
    if not pyramid_move_to(x, y):
        return False
    while get_pos_z() > floor:
        if get_ground_type() == Grounds.Sand:
            return True
        if not dig():
            return False
    return get_pos_z() == floor and get_ground_type() == Grounds.Limestone


def pyramid_boundary(point, floor, delta):
    # 从已知塔内格沿单轴探查，首个不属于塔的格子只是终止点。
    size = get_world_size()
    x, y = point
    dx, dy = delta
    for _ in range(size):
        nx = x + dx
        ny = y + dy
        if nx < 0 or nx >= size or ny < 0 or ny >= size:
            return x, y
        if not pyramid_floor_at(nx, ny, floor):
            return x, y
        x = nx
        y = ny
    return None


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
