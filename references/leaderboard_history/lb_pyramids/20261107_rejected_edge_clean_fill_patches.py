from __builtins__ import *
# 淘汰候选归档：lb_pyramids | 原实验路径 .codex/leaderboard-sol/underground-official/pyramids/edge-clean-fill-patches-candidate/lb_pyramids.py


def lb_pyramids():
    began = get_time()
    for cycle in range(512):
        if num_items(Items.Power) >= 150100:
            quick_print("pyramids_done", True, get_time(), num_items(Items.Power))
            return
        if get_time() - began > 14400:
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
        bounds = pyramid_edge_bounds(point[0], point[1], get_pos_z())
        if bounds == None:
            return
        x0, x1, y0, y1, floor = bounds
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        height = (x1 - x0 + 2) // 2
        if not pyramid_move_to(cx, cy):
            return
        top = floor + height
        for _ in range(17):
            if get_pos_z() < top:
                break
            if not dig():
                return
        if get_pos_z() >= top:
            return
        located = get_time()
        attempts = pyramid_dispatch(pyramid_clean_fill, bounds)
        if attempts == None:
            quick_print("pyramids_failed", "clean_fill", cycle)
            return
        wasted = 0
        for count in attempts:
            wasted += count
        cleaned = get_time()
        jobs = pyramid_dispatch(pyramid_missing_column, bounds)
        if jobs == None:
            return
        needed = 0
        for column in jobs:
            for x, y, z, target in column:
                needed += target - z
        counted = get_time()
        if not pyramid_materials(bounds, needed):
            continue
        if not pyramid_repair(jobs, bounds, height):
            quick_print("pyramids_failed", "repair", cycle)
            return
        if not pyramid_move_to(cx, cy) or get_pos_z() != floor + height - 1:
            return
        if not place(Grounds.Sand) or get_entity_type() != Entities.Sunflower or not harvest():
            quick_print("pyramids_failed", "sunflower", cycle)
            return
        quick_print("pyramid_fill_cycle", cycle, x1 - x0 + 1, needed, wasted,
                    located - start, cleaned - located, counted - cleaned,
                    get_time() - counted, get_time(), num_items(Items.Power))
    quick_print("pyramids_failed", "cycle_limit", get_time())


def pyramid_edge_bounds(x, y, floor):
    # 先确认西边，仅沿该条基边向南北找到端点；正方形边长确定东边。
    west = pyramid_boundary((x, y), floor, (-1, 0))
    if west == None:
        return None
    handles = []
    edges = []
    for delta in [(0, -1), (0, 1)]:
        if num_drones() < max_drones():
            handle = spawn_drone(pyramid_boundary, west, floor, delta)
            if handle != None:
                handles.append(handle)
                continue
        edges.append(pyramid_boundary(west, floor, delta))
    for handle in handles:
        edges.append(wait_for(handle))
    if edges[0] == None or edges[1] == None:
        return None
    x0 = west[0]
    y0 = min(edges[0][1], edges[1][1])
    y1 = max(edges[0][1], edges[1][1])
    length = y1 - y0 + 1
    if length < 5 or length % 2 != 1 or x0 + length > get_world_size():
        return None
    return x0, x0 + length - 1, y0, y1, floor


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


def pyramid_repair(columns, bounds, height):
    # 剩余缺口分为至多3×3的邻近施工块，避免整根长列或大区域集中到少数工人。
    # 修补期间只有place消耗Block。准确计算每层耗材，库存到达阈值才进入下一层。
    # 这段期间禁止挖掘、补料或其他Block消费；顶块由全部工人返回后的主机放置。
    floor = bounds[4]
    counts = []
    for _ in range(height):
        counts.append(0)
    length = bounds[1] - bounds[0] + 1
    groups = (length + 2) // 3
    patches = []
    for _ in range(groups * groups):
        patches.append([])
    for holes in columns:
        for x, y, z, top in holes:
            if z < min(top, floor + height - 1):
                owner = (x - bounds[0]) // 3 + groups * ((y - bounds[2]) // 3)
                patches[owner].append((x, y, z, top))
            for layer in range(z - floor + 1, min(top - floor, height - 1) + 1):
                counts[layer] += 1
    active = []
    for patch in patches:
        if len(patch) > 0:
            active.append(patch)
    remaining = num_items(Items.Block)
    thresholds = []
    for layer in range(1, height):
        remaining -= counts[layer]
        thresholds.append(remaining)
    if len(active) == 0:
        return True
    jobs = []
    for _ in range(min(len(active), max_drones())):
        jobs.append([])
    for i in range(len(active)):
        for hole in active[i]:
            jobs[i % len(jobs)].append(hole)
    deadline = get_time() + 120
    handles = []
    for i in range(1, len(jobs)):
        handle = spawn_drone(pyramid_patch_layers, jobs[i], floor, thresholds, deadline)
        if handle == None:
            # 未启动的列并入主机，仍保证每个计划放块恰好有一个执行者。
            for hole in jobs[i]:
                jobs[0].append(hole)
        else:
            handles.append(handle)
    ok = pyramid_patch_layers(jobs[0], floor, thresholds, deadline)
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def pyramid_patch_layers(holes, floor, thresholds, deadline):
    # 每台机逐层完成自己的列。等待全局本层耗材用完，八邻底层才都已就绪。
    # 失败可能使其他机等待未发生的消费，统一deadline保证所有等待有界。
    for index in range(len(thresholds)):
        target = floor + index + 1
        for x, y, z, top in holes:
            if z >= target or top < target:
                continue
            if get_time() > deadline or not pyramid_move_to(x, y):
                return False
            if get_pos_z() != target - 1 or not place(Grounds.Sand):
                return False
            if get_pos_z() != target:
                return False
        while num_items(Items.Block) > thresholds[index]:
            if get_time() > deadline:
                return False
            # 所在格没有竹子；保持普通悬浮高度，仅用200t动作等待其他列。
            if not hover(1):
                return False
    return True


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


def pyramid_missing_column(x, bounds, _layer):
    # 在清理与预留顶块全部结束后取快照，避免并发塌方使缺口高度失效。
    x0, x1, y0, y1, floor = bounds
    holes = []
    for y in range(y0, y1 + 1):
        if not pyramid_move_to(x, y):
            return None
        target = floor + 1 + min(x - x0, x1 - x, y - y0, y1 - y)
        z = get_pos_z()
        if z < floor or z > target:
            return None
        if z < target:
            holes.append((x, y, z, target))
    return holes


def pyramid_clean_fill(x, bounds, _layer):
    # 本列独占，清掉Dirt后立即尝试补到公式高度；中心始终少一块作为完成屏障。
    x0, x1, y0, y1, floor = bounds
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    wasted = 0
    for y in range(y0, y1 + 1):
        if not pyramid_move_to(x, y):
            return None
        while get_pos_z() > floor:
            ground = get_ground_type()
            if ground == Grounds.Sand or ground == Grounds.Limestone:
                break
            if not dig():
                return None
        if get_pos_z() < floor:
            return None
        target = floor + 1 + min(x - x0, x1 - x, y - y0, y1 - y)
        if x == cx and y == cy:
            target -= 1
        z = get_pos_z()
        while z < target and num_items(Items.Block) > 0:
            if not place(Grounds.Sand):
                return None
            after = get_pos_z()
            if after != z + 1:
                # 无支撑或并发塌方都可能使高度未升一格；停止尝试，交给清理后的实读修补。
                wasted += 1
                break
            z = after
    return wasted


if __name__ == "__main__":
    lb_pyramids()
