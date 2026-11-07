from __builtins__ import *
# 全科技功能初版；来源 lb_pyramids.py，普通地形有界找层。


def power_pyramids():
    # Jump每次执行仅一次；后续重生用爆破钻清除远离塔体的浅覆盖层。
    jump(Unlocks.Pyramid)
    first = True
    began = get_time()
    cycle = -1
    while True:
        cycle += 1
        if first:
            first = False
        else:
            clear()
        cycle_began = get_time()
        point = pyramid_find(get_time() + 600)
        if point == None:
            quick_print('pyramid_skip', cycle, get_time())
            continue
        if point == False or not pyramid_move_to(point[0], point[1]):
            quick_print('pyramids_failed', 'find', cycle)
            return
        for _ in range(32):
            if get_ground_type() == Grounds.Limestone:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Limestone:
            quick_print('pyramids_failed', 'foundation', cycle)
            return
        if cycle < 3:
            quick_print('pyramid_stage', cycle, 'find_floor', get_time() - cycle_began)
        stage = get_time()
        bounds = pyramid_bounds(point[0], point[1], get_pos_z())
        if bounds == None:
            quick_print('pyramids_failed', 'bounds', cycle)
            return
        if cycle < 3:
            quick_print('pyramid_stage', cycle, 'bounds', get_time() - stage)
        stage = get_time()
        x0, x1, y0, y1, floor = bounds
        if pyramid_dispatch(pyramid_clean_column, bounds) == None:
            quick_print('pyramids_failed', 'clean', cycle)
            return
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        height = (x1 - x0 + 2) // 2
        if not pyramid_move_to(cx, cy):
            return
        if get_pos_z() == floor + height:
            if get_ground_type() != Grounds.Sand or not dig():
                return
        if get_pos_z() >= floor + height or get_pos_z() < floor:
            quick_print('pyramids_failed', 'center_height', cycle)
            return
        if cycle < 3:
            quick_print('pyramid_stage', cycle, 'clean', get_time() - stage)
        stage = get_time()
        counts = pyramid_dispatch(pyramid_missing_column, bounds)
        if counts == None:
            quick_print('pyramids_failed', 'count', cycle)
            return
        needed = 0
        for holes in counts:
            for x, y, z, target in holes:
                needed += target - z
        if not pyramid_materials(bounds, needed):
            quick_print('pyramid_materials_missing', cycle, needed, num_items(Items.Block))
            continue
        if cycle < 3:
            quick_print('pyramid_stage', cycle, 'count_materials', get_time() - stage)
        quick_print('pyramid_sand_prepare', cycle, x1 - x0 + 1, needed, get_time())
        if not pyramid_repair(counts, bounds, height):
            quick_print('pyramids_failed', 'repair', cycle)
            return
        if not pyramid_move_to(cx, cy) or get_pos_z() != floor + height - 1:
            quick_print('pyramids_failed', 'cap_height', cycle)
            return
        if not place(Grounds.Sand) or get_entity_type() != Entities.Sunflower:
            quick_print('pyramids_failed', 'sunflower', cycle)
            return
        while not can_harvest():
            if get_time() - began > 14400:
                return
            do_a_flip()
        if not harvest():
            return
        quick_print('pyramid_cycle', cycle, x1 - x0 + 1, floor, get_time(), num_items(Items.Power))


def pyramid_find(deadline):
    # 普通田金字塔最早位于第4区块；仅在深度48以上爆破，接近塔区换采矿帽。
    size = get_world_size()
    x = size // 2
    y = x
    if not pyramid_move_to(x, y):
        return False
    drilling = num_items(Items.Dynamite) > 0 and get_pos_z() > -48
    if drilling:
        change_hat(Hats.Explosive_Drill)
    else:
        change_hat(Hats.Mining_Hat)
    for _ in range(129):
        if drilling and (get_pos_z() <= -48 or num_items(Items.Dynamite) < 1):
            change_hat(Hats.Mining_Hat)
            drilling = False
        ground = get_ground_type()
        if ground == Grounds.Sand or ground == Grounds.Limestone:
            change_hat(Hats.Mining_Hat)
            break
        if get_pos_z() <= -128:
            change_hat(Hats.Mining_Hat)
            return None
        if get_time() > deadline or get_hardness() >= 10000000 or not dig():
            change_hat(Hats.Mining_Hat)
            return False
    change_hat(Hats.Mining_Hat)
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


def pyramid_bounds(x, y, floor):
    # 四条射线都只挖到已知基座高度，互不钻穿沙柱；全部返回后才清理塔盖。
    handles = []
    edges = []
    for delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if num_drones() < max_drones():
            handle = spawn_drone(pyramid_boundary, (x, y), floor, delta)
            if handle != None:
                handles.append(handle)
                continue
        edges.append(pyramid_boundary((x, y), floor, delta))
    for handle in handles:
        edges.append(wait_for(handle))
    x0 = x
    x1 = x
    y0 = y
    y1 = y
    for edge in edges:
        if edge == None:
            return None
        x0 = min(x0, edge[0])
        x1 = max(x1, edge[0])
        y0 = min(y0, edge[1])
        y1 = max(y1, edge[1])
    length = x1 - x0 + 1
    if length < 5 or length % 2 != 1 or y1 - y0 + 1 != length:
        return None
    return x0, x1, y0, y1, floor


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


def pyramid_repair(columns, bounds, height):
    # 修补期间只有place消耗Block。准确计算每层耗材，库存到达阈值才进入下一层。
    # 这段期间禁止挖掘、补料或其他Block消费；顶块由全部工人返回后的主机放置。
    floor = bounds[4]
    counts = []
    for _ in range(height):
        counts.append(0)
    active = []
    for holes in columns:
        if len(holes) > 0:
            active.append(holes)
        for x, y, z, top in holes:
            for layer in range(z - floor + 1, min(top - floor, height - 1) + 1):
                counts[layer] += 1
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


if __name__ == "__main__":
    power_pyramids()
