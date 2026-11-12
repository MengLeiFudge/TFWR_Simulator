from __builtins__ import *
# 淘汰候选归档：lb_fastest_underground_reset | 原实验路径 .codex/reset-optimization-20261110/candidates/underground-expand6.py

def lb_fastest_underground_reset():
    # 每次升级都读取当前成本；低科技阶段使用单机，资源阶段结束后才clear。
    stages = [
        (Unlocks.Speed, 1), (Unlocks.Expand, 1), (Unlocks.Plant, 1),
        (Unlocks.Carrots, 1), (Unlocks.Expand, 2), (Unlocks.Expand, 3),
        (Unlocks.Speed, 2), (Unlocks.Mining, 1), (Unlocks.Mining, 2),
        (Unlocks.Coal, 1), (Unlocks.Rice, 1), (Unlocks.Mining, 3),
        (Unlocks.Rice, 3), (Unlocks.Coal, 2), (Unlocks.Iron, 1), (Unlocks.Mining, 4),
        (Unlocks.Speed, 3), (Unlocks.Expand, 4),
        (Unlocks.Grass, 2), (Unlocks.Trees, 2),
        (Unlocks.Carrots, 2), (Unlocks.Speed, 5), (Unlocks.Sunflowers, 1), (Unlocks.Bamboo, 3),
        (Unlocks.Mining, 5), (Unlocks.Iron, 2), (Unlocks.Rice, 5),
        (Unlocks.Coal, 3), (Unlocks.Prospecting, 1),
        (Unlocks.Mining, 6),
        (Unlocks.Treasure_Map, 1), (Unlocks.Quartz, 1),
        (Unlocks.Mining, 7), (Unlocks.Pumpkins, 1), (Unlocks.Mushrooms, 2),
        (Unlocks.Mining, 8),
        (Unlocks.Dynamite, 3), (Unlocks.Expand, 5), (Unlocks.Expand, 6), (Unlocks.Underground_Leaderboard, 1)]
    for tech, level in stages:
        while num_unlocked(tech) < level:
            if get_time() > 72000:
                quick_print("underground_reset_failed", "deadline", tech)
                return
            cost = get_cost(tech)
            ready = False
            for funding in range(8):
                for item in cost:
                    if num_unlocked(Unlocks.Sunflowers) > 0 and num_items(Items.Power) < 100:
                        if not ur_power_stock(1000):
                            quick_print("underground_reset_failed", "power")
                            return
                    if not ur_need(item, cost[item]):
                        quick_print("underground_reset_failed", "resource", tech, item, cost[item])
                        return
                ready = True
                for item in cost:
                    if num_items(item) < cost[item]:
                        ready = False
                if ready:
                    break
            if not ready:
                quick_print("underground_reset_failed", "funding", tech)
                return
            if not unlock(tech):
                quick_print("underground_reset_failed", "unlock", tech)
                return
            quick_print("underground_reset_upgrade", tech, num_unlocked(tech), get_time())
    quick_print("underground_reset_done", num_unlocked(Unlocks.Underground_Leaderboard) > 0, get_time())


def ur_need(item, goal):
    if num_items(item) >= goal:
        return True
    quick_print("underground_reset_collect", item, goal, get_time())
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot or item == Items.Pumpkin:
        return ur_farm(item, goal)
    if item == Items.Quartz:
        return ur_q_stock(goal)
    if item == Items.Iron and num_unlocked(Unlocks.Prospecting) > 0:
        return ur_i_stock(goal)
    if item == Items.Block or item == Items.Coal or item == Items.Iron:
        return ur_mine(item, goal)
    if item == Items.Rice:
        ur_rice_stock(goal)
    elif item == Items.Bamboo:
        factor = 2 ** (num_unlocked(Unlocks.Bamboo) - 1)
        stems = (goal - num_items(item)) // (81 * factor) + 2
        reserve = (2 * stems + get_world_size() * get_world_size()) * factor
        if not ur_need(Items.Rice, reserve):
            return False
        ur_bamboo_stock(goal)
    elif item == Items.Gold:
        ur_treasure_stock(goal)
    elif item == Items.Mushroom:
        ur_mushroom_stock(goal)
    elif item == Items.Dynamite:
        ur_dynamite_stock(goal)
    else:
        return False
    return num_items(item) >= goal


def ur_farm(item, goal):
    kind = Entities.Grass
    if item == Items.Wood:
        kind = Entities.Bush
    elif item == Items.Carrot:
        kind = Entities.Carrot
    elif item == Items.Pumpkin:
        kind = Entities.Pumpkin
    if item == Items.Carrot or item == Items.Pumpkin:
        factor = 1
        if item == Items.Carrot:
            factor = 2 ** (num_unlocked(Unlocks.Carrots) - 1)
        seeds = 2 * ((goal - num_items(item)) // factor + 1) + 2 * get_world_size() * get_world_size()
        cost = get_cost(kind)
        for seed_item in cost:
            if not ur_need(seed_item, cost[seed_item] * seeds):
                return False
    clear()
    size = get_world_size()
    width = size
    if num_unlocked(Unlocks.Expand) == 1:
        width = 1
    deadline = get_time() + 7200
    for lap in range(20000):
        if num_items(item) >= goal:
            return True
        if get_time() > deadline:
            return False
        for x in range(width):
            for y in range(size):
                if num_items(item) >= goal:
                    return True
                if can_harvest():
                    harvest()
                if item != Items.Hay and get_entity_type() != kind:
                    if item == Items.Carrot or item == Items.Pumpkin:
                        if get_ground_type() != Grounds.Soil:
                            till()
                    if not plant(kind):
                        return False
                move(North)
            if width > 1:
                move(East)
        if lap % 32 == 0:
            quick_print("underground_reset_farm", item, lap, get_time(), num_items(item))
        do_a_flip()
    return False


def ur_mine(item, goal, deadline=None):
    # 普通Reset按实际地层采集；Rice开启后的煤只采首段再重生。
    empty = 0
    if deadline == None:
        deadline = get_time() + 18000
    layers = 1024
    if item == Items.Coal and num_unlocked(Unlocks.Rice) > 0:
        layers = 16
    for cycle in range(128):
        clear()
        size = get_world_size()
        before = num_items(item)
        for layer in range(layers):
            active = 0
            for x in range(size):
                for y in range(size):
                    if num_items(item) >= goal:
                        return True
                    if get_time() > deadline:
                        return False
                    if get_pos_z() >= -layer and get_hardness() < 10000000:
                        if not dig():
                            return False
                        active += 1
                    move(North)
                move(East)
            if layer % 16 == 0:
                quick_print("underground_reset_mine", item, cycle, layer, get_time(), num_items(item))
            if active == 0:
                break
        if num_items(item) == before:
            empty += 1
            if empty >= 8:
                return False
        else:
            empty = 0
    return False


def ur_i_stock(goal):
    deadline = get_time() + 18000
    size = get_world_size()
    empty = 0
    for cycle in range(64):
        if num_items(Items.Iron) >= goal:
            return True
        if get_time() > deadline:
            return False
        # 解锁和每次勘探均支付真实Coal，筹资完成后才开始新片。
        if num_items(Items.Coal) < 16 and not ur_need(Items.Coal, 32):
            return False
        clear()
        before = num_items(Items.Iron)
        for layer in [32, 64, 96, 128]:
            if not ur_q_prepare(0, 0, -layer, deadline, size):
                break
            if num_items(Items.Iron) >= goal:
                return True
            if num_items(Items.Coal) < 2 * size + 1:
                break
            for _ in range(2 * size + 1):
                direction = prospect_iron()
                if direction == None:
                    break
                if not move(direction):
                    return False
            # None也可能表示范围无矿；它不是已找到矿的证明。
            found = False
            for _ in range(64):
                if num_items(Items.Iron) >= goal:
                    return True
                if get_time() > deadline:
                    return False
                ground = get_ground_type()
                if ground == Grounds.Iron:
                    if not dig():
                        return False
                    found = True
                    continue
                if found or get_hardness() >= 10000000:
                    break
                if not dig():
                    return False
            quick_print("iron_prospect_column", cycle, layer, num_items(Items.Iron) - before, get_time())
            if num_items(Items.Iron) > before:
                break
        if num_items(Items.Iron) > before:
            empty = 0
        else:
            empty += 1
            if empty >= 2:
                quick_print("iron_prospect_fallback", get_time(), num_items(Items.Iron), goal)
                return ur_mine(Items.Iron, goal, deadline)
    return num_items(Items.Iron) >= goal


def ur_q_stock(goal):
    deadline = get_time() + 18000
    size = get_world_size()
    empty = 0
    anchors = [(0, 0), (1, 0), (0, 1)]
    for cycle in range(64):
        if num_items(Items.Quartz) >= goal:
            return True
        if get_time() > deadline:
            return False
        # 勘探按真实库存支付Iron，筹资发生在新片开始前，避免清场使定位失效。
        if num_items(Items.Iron) < 16 and not ur_need(Items.Iron, 32):
            return False
        clear()
        before = num_items(Items.Quartz)
        for layer in range(0, 129, 16):
            if not ur_q_prepare(0, 0, -layer, deadline, size):
                break
            if num_items(Items.Quartz) >= goal:
                return True
            if num_items(Items.Iron) < 4:
                break
            if prospect_quartz() == None:
                continue
            ready = True
            for point in anchors:
                if not ur_q_prepare(point[0], point[1], -layer, deadline, size):
                    ready = False
                    break
            if not ready:
                break
            # 先完成全部开挖，再在不改地形时重读三点，不能缓存塌方前的距离。
            samples = []
            for point in anchors:
                if not ur_d_move_to(point[0], point[1], size):
                    return False
                distance = prospect_quartz()
                if distance == None:
                    break
                samples.append((get_pos_x(), get_pos_y(), get_pos_z(), distance))
            if len(samples) != 3:
                continue
            target = ur_q_locate(samples, size)
            if target == None:
                quick_print("quartz_prospect_ambiguous", cycle, layer, get_time())
                continue
            if not ur_d_move_to(target[0], target[1], size):
                return False
            found = False
            for _ in range(192):
                if num_items(Items.Quartz) >= goal:
                    return True
                if get_time() > deadline:
                    return False
                ground = get_ground_type()
                if ground == Grounds.Quartz:
                    if not dig():
                        return False
                    found = True
                    continue
                if found or get_pos_z() < target[2] or get_hardness() >= 10000000:
                    break
                if not dig():
                    return False
            quick_print("quartz_prospect_column", cycle, layer, target, num_items(Items.Quartz) - before, get_time())
            if num_items(Items.Quartz) > before:
                break
        if num_items(Items.Quartz) > before:
            empty = 0
        else:
            empty += 1
            if empty >= 2:
                quick_print("quartz_prospect_fallback", get_time(), num_items(Items.Quartz), goal)
                return ur_mine(Items.Quartz, goal, deadline)
    return num_items(Items.Quartz) >= goal


def ur_q_prepare(x, y, target, deadline, size):
    if not ur_d_move_to(x, y, size):
        return False
    for _ in range(192):
        if get_pos_z() <= target:
            return True
        if get_time() > deadline or get_hardness() >= 10000000 or not dig():
            return False
    return False


def ur_q_locate(samples, size):
    # 只枚举公开距离允许的整数坐标；三点的最近矿可能变化，失配就放弃定位。
    x0, y0, z0, d0 = samples[0]
    best = None
    for x in range(size):
        for y in range(size):
            square = d0 * d0 - (x - x0) ** 2 - (y - y0) ** 2
            if square < 0:
                continue
            dz = (square ** 0.5 + 0.5) // 1
            for z in [z0 - dz, z0 + dz]:
                if z > 0 or z < -256:
                    continue
                valid = True
                for sx, sy, sz, distance in samples:
                    residual = (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2 - distance * distance
                    if abs(residual) > 0.01:
                        valid = False
                        break
                    if x == sx and y == sy and z > sz:
                        valid = False
                        break
                if valid and (best == None or z < best[2]):
                    best = (x, y, z)
    return best


def ur_rice_stock(goal):
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    for batch in range(128):
        if num_items(Items.Rice) >= goal:
            quick_print("rice_done", True, batch, get_time(), num_items(Items.Rice))
            return
        # 上一批所有句柄已回收，clear不会取消仍在工作的子机。
        clear()
        handles = []
        local = True
        for column in range(1, workers):
            handle = spawn_drone(ur_r_rice_columns, column, workers, size, goal, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not ur_r_rice_columns(0, workers, size, goal, deadline):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        quick_print("rice_batch", batch, local, get_time(), num_items(Items.Rice))
        if not local:
            quick_print("rice_failed", "batch", batch)
            return
    quick_print("rice_failed", "batch_limit", get_time(), num_items(Items.Rice))


def ur_r_rice_columns(first, stride, size, goal, deadline):
    # 每个柱独占；两层粘土用尽就返回，由主机在全体结束后重生下一片。
    for layer in range(2):
        planted = []
        for x in range(first, size, stride):
            if not ur_r_rice_move_to(x, 0, size):
                return False
            for y in range(size):
                if num_items(Items.Rice) >= goal:
                    return True
                ground = get_ground_type()
                digs = 0
                while ground != Grounds.Clay and ground != Grounds.Rock and digs < 128:
                    if get_time() > deadline or not dig():
                        return False
                    ground = get_ground_type()
                    digs += 1
                if ground == Grounds.Clay:
                    if not plant(Entities.Rice):
                        return False
                    planted.append((x, y))
                if not move(North):
                    return False
        for x, y in planted:
            if num_items(Items.Rice) >= goal:
                return True
            if not ur_r_rice_move_to(x, y, size):
                return False
            while get_entity_type() == Entities.Rice and not can_harvest():
                if get_time() > deadline:
                    return False
                # 一秒等待避免忙轮询；不继续下挖，保留相邻尚未成熟的稻米。
                do_a_flip()
            if get_entity_type() == Entities.Rice and not harvest():
                return False
    return True


def ur_r_rice_move_to(tx, ty, size):
    # 常规帽子可跨高度移动；每次到柱后重新读取地层，不缓存塌方前深度。
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


def ur_bamboo_stock(goal):
    # 每列唯一写者；子机只通过全局库存判断结束，不共享私有作用域。
    clear()
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    handles = []
    for column in range(1, workers):
        handle = spawn_drone(ur_b_bamboo_columns, column, workers, size, goal, deadline)
        if handle == None:
            quick_print("bamboo_failed", "spawn", column)
            break
        handles.append(handle)
    local = ur_b_bamboo_columns(0, workers, size, goal, deadline)
    for handle in handles:
        if not wait_for(handle):
            local = False
    quick_print("bamboo_done", local, get_time(), num_items(Items.Bamboo))


def ur_b_bamboo_columns(first, stride, size, goal, deadline):
    # 偶数行种竹，奇数行留通道；低飞切花的出入不会碰到另一株竹子。
    phases = {}
    for x in range(first, size, stride):
        for y in range(0, size - 1, 2):
            phases[(x, y)] = 0
    hover(18)
    rounds = 0
    while num_items(Items.Bamboo) < goal:
        if get_time() > deadline:
            quick_print("bamboo_failed", "deadline", first, get_time())
            return False
        for x in range(first, size, stride):
            for y in range(0, size - 1, 2):
                if num_items(Items.Bamboo) >= goal:
                    return True
                if not ur_b_bamboo_move_to(x, y + 1, size) or not move(South):
                    return False
                if get_entity_type() != Entities.Bamboo:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if not plant(Entities.Bamboo):
                        return False
                    phases[(x, y)] = 0
                    hover(18)
                elif can_harvest():
                    phase = phases[(x, y)]
                    if phase < 2:
                        height = measure()
                        if not move(North):
                            return False
                        hover(height)
                        if not move(South):
                            return False
                        if measure() <= height:
                            quick_print("bamboo_failed", "flower_not_cut", x, y, phase)
                            return False
                        phases[(x, y)] = phase + 1
                        hover(18)
                    else:
                        if not harvest() or not plant(Entities.Bamboo):
                            return False
                        phases[(x, y)] = 0
                        hover(18)
                if not move(North):
                    return False
        rounds += 1
        if first == 0 and rounds % 8 == 0:
            quick_print("bamboo_round", rounds, get_time(), num_items(Items.Bamboo))
    return True


def ur_b_bamboo_move_to(tx, ty, size):
    # 定位期间高飞，切花仅在专属空通道与目标竹子之间往返。
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


def ur_treasure_stock(goal):
    clear()
    deadline = get_time() + 7200
    for cycle in range(256):
        if num_items(Items.Gold) >= goal:
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
        if location == None or not ur_t_treasure_map_move_to(location[0], location[1]):
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


def ur_t_treasure_map_move_to(tx, ty):
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


def ur_mushroom_stock(goal):
    began = get_time()
    empty = 0
    for batch in range(128):
        if num_items(Items.Mushroom) >= goal:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        # 只有上一批句柄全部回收后才重生，禁止clear取消仍在采集的子机。
        clear()
        covers = 0
        while get_ground_type() != Grounds.Mushroom and covers < 256:
            if get_time() - began > 18000 or not dig():
                quick_print("mushrooms_failed", "search_action", batch)
                return
            covers += 1
        if get_ground_type() != Grounds.Mushroom:
            empty += 1
            quick_print("mushrooms_search_miss", batch, empty, get_time())
            if empty >= 8:
                quick_print("mushrooms_failed", "eight_search_misses")
                return
            continue
        empty = 0
        top = get_pos_z()
        if not ur_m_dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch, top)
            return
        quick_print("mushrooms_prepared", batch, covers, top, get_time())
        if not ur_m_move_to(0, 0):
            return
        ceiling = get_pos_z()
        blocks = ur_m_make_blocks()
        layers = 0
        while get_ground_type() == Grounds.Mushroom and num_items(Items.Mushroom) < goal:
            result = ur_m_run_layer(blocks, ceiling)
            if result == None:
                quick_print("mushrooms_failed", "layer", batch, layers, ceiling)
                return
            if not ur_m_move_to(0, 0) or get_pos_z() != ceiling or not dig():
                quick_print("mushrooms_failed", "sample", batch, layers)
                return
            pairs, digs = result
            ceiling -= 1
            layers += 1
            quick_print("mushrooms_layer", batch, layers, pairs, digs + 1, get_time(), num_items(Items.Mushroom))
        quick_print("mushrooms_batch", batch, layers, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


# 每台无人机负责一列；无人机不足时按列步长分担，整层完成后才返回。
def ur_m_dig_layer(target):
    size = get_world_size()
    workers = min(size, max_drones())
    handles = []
    ok = True
    for x in range(workers - 1):
        if not ur_m_move_to(x, 0):
            ok = False
            break
        handle = spawn_drone(ur_m_dig_columns, x, workers, size, target)
        if handle == None:
            if not ur_m_dig_columns(x, workers, size, target):
                ok = False
        else:
            handles.append(handle)
    if ok and not ur_m_dig_columns(workers - 1, workers, size, target):
        ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


# 覆盖层起始高度一致，只需逐格挖到本次目标高度，无需识别地面类型。
def ur_m_dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
        if not ur_m_move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() != target:
                return False
            if not move(North):
                return False
    return True


# 主机只创建少量矩形边界，逐格坐标和邻格交给各子机就地计算。
def ur_m_make_blocks():
    size = get_world_size()
    limit = max(1, size // 4)
    capacity = max_drones()
    gx = 1
    gy = 1
    best = 1
    for ty in range(1, limit + 1):
        tx = min(limit, capacity // ty)
        if tx * ty > best:
            best = tx * ty
            gx = tx
            gy = ty
    blocks = []
    for k in range(best):
        bx = k % gx
        by = k // gx
        blocks.append((bx * size // gx, (bx + 1) * size // gx,
                       by * size // gy, (by + 1) * size // gy))
    return blocks


# 各分区共用本层高度上限；先收回全部子机，再推进采样点和下一层。
def ur_m_run_layer(blocks, ceiling):
    handles = []
    results = []
    for k in range(1, len(blocks)):
        handle = spawn_drone(ur_m_work_layer, blocks[k], ceiling)
        if handle == None:
            results.append(ur_m_work_layer(blocks[k], ceiling))
        else:
            handles.append(handle)
    results.append(ur_m_work_layer(blocks[0], ceiling))
    for handle in handles:
        results.append(wait_for(handle))
    pairs = 0
    digs = 0
    for result in results:
        if result == None:
            return None
        pairs += result[0]
        digs += result[1]
    return pairs, digs


# 单遍蛇形处理：最高处先尝试直接推送，无法配对才挖，再接收邻格配对。
# 蘑菇稳定性为3；两格高度带也把内部地块承受的落差限制在一格。
def ur_m_work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    floor = ceiling - 2
    pairs = 0
    digs = 0
    for y in range(y0, y1):
        for offset in range(x1 - x0):
            x = x0 + offset
            if (y - y0) % 2 != 0:
                x = x1 - 1 - offset
            if x == 0 and y == 0:
                continue
            if not ur_m_move_to(x, y):
                return None
            neighbors = []
            if y + 1 < y1:
                neighbors.append(0)
            if x + 1 < x1:
                neighbors.append(1)
            if y > y0 and (x != 0 or y != 1):
                neighbors.append(2)
            if x > x0 and (x != 1 or y != 0):
                neighbors.append(3)
            z = get_pos_z()
            if z < floor or z > ceiling:
                return None
            if z == ceiling:
                count = ur_m_push_match(neighbors, floor)
                if count == None:
                    return None
                pairs += count
                if count == 0:
                    if get_hardness() >= 10000000 or not dig():
                        return None
                    if get_pos_z() != z - 1:
                        return None
                    digs += 1
            count = ur_m_feed_column(neighbors, floor)
            if count == None:
                return None
            pairs += count
    return pairs, digs


# 直接从脚下推送省去前往邻格再返回的两次移动。
def ur_m_push_match(neighbors, floor):
    if get_ground_type() != Grounds.Mushroom:
        return 0
    t = measure()
    z = get_pos_z()
    for i in neighbors:
        direction = ur_m_DIRECTIONS[i]
        if get_ground_type(direction) == Grounds.Mushroom:
            target = get_pos_z(direction)
            if floor < target and target < z and measure(direction) == t:
                if not push(direction):
                    return None
                return 1
    return 0


# 从邻格推向当前格并返回，移动或推送失败交给主机停止本轮。
def ur_m_push_neighbor(i):
    if not move(ur_m_DIRECTIONS[i]):
        return False
    pushed = push(ur_m_BACKS[i])
    if not move(ur_m_BACKS[i]):
        return False
    return pushed


# 直接匹配会使目标下降一格；双邻配对保持目标高度，但不能提前同型消除。
def ur_m_feed_column(neighbors, floor):
    matched = 0
    while True:
        z = get_pos_z()
        if z < floor:
            return None
        if get_ground_type() != Grounds.Mushroom:
            return matched
        t = measure()
        types = [-1, -1, -1, -1]
        heights = [0, 0, 0, 0]
        hit = -1
        for i in neighbors:
            direction = ur_m_DIRECTIONS[i]
            if get_ground_type(direction) == Grounds.Mushroom:
                types[i] = measure(direction)
                heights[i] = get_pos_z(direction)
                if z > floor and types[i] == t and heights[i] > z:
                    hit = i
                    break
        if hit >= 0:
            if not ur_m_push_neighbor(hit):
                return None
            matched += 1
            continue
        pair_a = -1
        pair_b = -1
        for i in neighbors:
            if types[i] < 0 or types[i] == t or heights[i] < z + 2:
                continue
            for j in neighbors:
                if j > i and types[j] == types[i] and heights[j] >= z + 2:
                    pair_a = i
                    pair_b = j
                    break
            if pair_a >= 0:
                break
        if pair_a < 0:
            return matched
        if not ur_m_push_neighbor(pair_a):
            return None
        if not ur_m_push_neighbor(pair_b):
            return None
        matched += 1


# 利用边界环绕走较短路径，坐标只读一次。
def ur_m_move_to(tx, ty):
    size = get_world_size()
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


ur_m_DIRECTIONS = [North, East, South, West]
ur_m_BACKS = [South, West, North, East]

def ur_dynamite_stock(goal):
    began = get_time()
    empty = 0
    size = get_world_size()
    near = []
    for cell in range(size * size):
        near.append(ur_d_neighbors(cell, size))
    for cycle in range(512):
        if num_items(Items.Dynamite) >= goal:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        clear()
        if not ur_d_move_to(size // 2, size // 2, size):
            return
        covers = 0
        while get_ground_type() != Grounds.Dynamite and covers < 256:
            if get_time() - began > 72000 or not dig():
                quick_print("dynamite_failed", "search_action", cycle)
                return
            covers += 1
        if get_ground_type() != Grounds.Dynamite:
            empty += 1
            if empty >= 8:
                quick_print("dynamite_failed", "eight_search_misses")
                return
            continue
        empty = 0
        depth = get_pos_z()
        before = num_items(Items.Dynamite)
        status, number = ur_d_open_ground(depth)
        phases = 0
        if status == "number":
            status, phases = ur_d_solve(size, depth, near, number)
        if status == "mine":
            status = ur_d_settle(size, depth)
        quick_print("dynamite_cycle", cycle, status, phases, num_items(Items.Dynamite) - before,
                    get_time(), num_items(Items.Dynamite))
        if status != "ended":
            return
    quick_print("dynamite_failed", "cycle_limit", get_time(), num_items(Items.Dynamite))


UR_D_UNKNOWN = -2
UR_D_MINE = -1
UR_D_SAFE = -3
UR_D_DONE = 9
UR_D_DIG_LIMIT = 256
UR_D_PHASE_LIMIT = 256


def ur_d_solve(size, depth, near, number):
    known = []
    for cell in range(size * size):
        known.append(UR_D_UNKNOWN)
    known[(size // 2) * (size + 1)] = number
    groups = min(max_drones(), size)
    rounds = 0
    for phase in range(UR_D_PHASE_LIMIT):
        results = ur_d_dispatch(0, groups, groups, known, near, size, depth)
        changed = False
        status = "running"
        for state, updates in results:
            # 主机叶子也会修改known；以本批新事实判断进展。
            if len(updates) > 0:
                changed = True
            if state == "error":
                status = state
            elif state == "mine" and status != "error":
                status = state
            elif state == "ended" and status == "running":
                status = state
            for cell in updates:
                value = updates[cell]
                old = known[cell]
                if old == value or (old >= 0 and value == UR_D_SAFE) or (old == UR_D_DONE and value >= 0):
                    continue
                if old == UR_D_UNKNOWN or (old == UR_D_SAFE and value >= 0) or (old >= 0 and value == UR_D_DONE):
                    known[cell] = value
                else:
                    quick_print("dynamite_conflict", cell, old, value)
                    return "error", rounds
        rounds += 1
        if status != "running" or not changed:
            break
    if status == "running":
        status = ur_d_settle(size, depth)
    return status, rounds


def ur_d_dispatch(lo, hi, groups, known, near, size, depth):
    if hi - lo == 1:
        return [ur_d_work(lo, groups, known, near, size, depth)]
    mid = (lo + hi) // 2
    handle = spawn_drone(ur_d_dispatch, mid, hi, groups, known, near, size, depth)
    results = ur_d_dispatch(lo, mid, groups, known, near, size, depth)
    if handle == None:
        right = ur_d_dispatch(mid, hi, groups, known, near, size, depth)
    else:
        right = wait_for(handle)
    for result in right:
        results.append(result)
    return results


def ur_d_work(group, groups, known, near, size, depth):
    columns = min(8, groups)
    rows = groups // columns
    left = (group % columns) * size // columns
    right = (group % columns + 1) * size // columns
    bottom = (group // columns) * size // rows
    top = (group // columns + 1) * size // rows
    owned = []
    for y in range(bottom, top):
        if (y - bottom) % 2 == 0:
            for x in range(left, right):
                owned.append(x + y * size)
        else:
            for x in range(right - 1, left - 1, -1):
                owned.append(x + y * size)
    clues = set()
    # 两格边界允许本区利用相邻数字约束，不取得邻区的开挖权。
    for y in range(max(0, bottom - 2), min(size, top + 2)):
        for x in range(max(0, left - 2), min(size, right + 2)):
            cell = x + y * size
            if known[cell] >= 0 and known[cell] != UR_D_DONE:
                clues.add(cell)
    owned_set = set(owned)
    updates = {}
    for step in range(UR_D_PHASE_LIMIT):
        if not ur_d_propagate(known, clues, near, updates):
            return "error", updates
        targets = []
        for cell in owned:
            if known[cell] == UR_D_SAFE:
                targets.append(cell)
        if len(targets) == 0:
            return "running", updates
        while len(targets) > 0:
            cell = targets.pop()
            if not ur_d_move_to(cell % size, cell // size, size):
                return "error", updates
            status, number = ur_d_open_ground(depth)
            if status != "number":
                return status, updates
            known[cell] = number
            updates[cell] = number
            if number == 0:
                known[cell] = UR_D_DONE
                updates[cell] = UR_D_DONE
                for other in near[cell]:
                    if known[other] == UR_D_UNKNOWN:
                        known[other] = UR_D_SAFE
                        updates[other] = UR_D_SAFE
                        if other in owned_set:
                            targets.append(other)
            else:
                clues.add(cell)
    return "error", updates


def ur_d_propagate(known, active, near, updates):
    pending = []
    queued = set()
    for clue in active:
        pending.append(clue)
        queued.add(clue)
    while len(pending) > 0:
        clue = pending.pop()
        queued.remove(clue)
        if clue not in active:
            continue
        remaining = known[clue]
        unknown = []
        for cell in near[clue]:
            value = known[cell]
            if value == UR_D_MINE:
                remaining -= 1
            elif value == UR_D_UNKNOWN:
                unknown.append(cell)
        if remaining < 0 or remaining > len(unknown):
            return False
        if remaining != 0 and remaining != len(unknown):
            continue
        active.remove(clue)
        known[clue] = UR_D_DONE
        updates[clue] = UR_D_DONE
        value = UR_D_MINE
        if remaining == 0:
            value = UR_D_SAFE
        for cell in unknown:
            known[cell] = value
            updates[cell] = value
            for other in near[cell]:
                if other in active and other not in queued:
                    pending.append(other)
                    queued.add(other)
    return True


def ur_d_read_ground(depth):
    z = get_pos_z()
    if z >= depth:
        return "closed", None
    if z < depth - 1:
        return "ended", None
    if get_ground_type() != Grounds.Soot:
        return "error", None
    if get_entity_type() == Entities.Dynamite:
        return "mine", None
    number = measure()
    # 实际结算可返回None，外部Measure类型桩未声明此终态。
    if number == None:
        return "ended", None
    if number not in range(9):
        return "error", None
    return "number", number


def ur_d_open_ground(depth):
    for _ in range(UR_D_DIG_LIMIT):
        if get_pos_z() <= depth:
            break
        if get_hardness() >= 10000000 or not dig():
            return "error", None
    z = get_pos_z()
    if z > depth:
        return "error", None
    if z == depth:
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    return ur_d_read_ground(depth)


def ur_d_settle(size, depth):
    if not ur_d_move_to(size // 2, size // 2, size):
        return "error"
    status, number = ur_d_read_ground(depth)
    if status == "ended":
        return status
    if status != "number" or not dig():
        return "error"
    status, number = ur_d_read_ground(depth)
    if status != "ended":
        return "error"
    return status


def ur_d_neighbors(cell, size):
    x = cell % size
    y = cell // size
    result = []
    if y > 0:
        if x > 0:
            result.append(cell - size - 1)
        result.append(cell - size)
        if x + 1 < size:
            result.append(cell - size + 1)
    if x > 0:
        result.append(cell - 1)
    if x + 1 < size:
        result.append(cell + 1)
    if y + 1 < size:
        if x > 0:
            result.append(cell + size - 1)
        result.append(cell + size)
        if x + 1 < size:
            result.append(cell + size + 1)
    return result


def ur_d_move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True



def ur_power_stock(goal):
    size = get_world_size()
    deadline = get_time() + 3600
    for batch in range(64):
        if num_items(Items.Power) >= goal:
            return True
        cost = get_cost(Entities.Sunflower)
        for item in cost:
            if not ur_need(item, cost[item] * size * size):
                return False
        clear()
        flowers = []
        for petals in range(16):
            flowers.append([])
        for x in range(size):
            for y in range(size):
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Sunflower):
                    return False
                flowers[measure()].append((x, y))
                move(North)
            move(East)
        remaining = size * size
        for petals in range(15, 6, -1):
            for x, y in flowers[petals]:
                if remaining < 10:
                    break
                if num_items(Items.Power) >= goal:
                    return True
                if not ur_r_rice_move_to(x, y, size):
                    return False
                while not can_harvest():
                    if get_time() > deadline:
                        return False
                    do_a_flip()
                if not harvest():
                    return False
                remaining -= 1
        quick_print("underground_reset_power", batch, get_time(), num_items(Items.Power))
    return False

if __name__ == "__main__":
    lb_fastest_underground_reset()
