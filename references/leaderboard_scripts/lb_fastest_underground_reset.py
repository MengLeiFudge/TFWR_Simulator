from __builtins__ import *
# 完整轮时间：未取得（低科技资源链首版，尚无官方完整统计）。

def lb_fastest_underground_reset():
    # 每次升级都读取当前成本；低科技阶段使用单机，资源阶段结束后才clear。
    stages = [
        (Unlocks.Speed, 1), (Unlocks.Expand, 1), (Unlocks.Plant, 1),
        (Unlocks.Carrots, 1), (Unlocks.Expand, 2), (Unlocks.Expand, 3),
        (Unlocks.Speed, 2), (Unlocks.Mining, 1), (Unlocks.Mining, 2),
        (Unlocks.Coal, 1), (Unlocks.Rice, 1), (Unlocks.Mining, 3),
        (Unlocks.Rice, 3), (Unlocks.Iron, 1), (Unlocks.Mining, 4),
        (Unlocks.Speed, 3), (Unlocks.Expand, 4), (Unlocks.Bamboo, 3),
        (Unlocks.Mining, 5), (Unlocks.Treasure_Map, 1), (Unlocks.Quartz, 1),
        (Unlocks.Mining, 6), (Unlocks.Pumpkins, 1), (Unlocks.Mushrooms, 2),
        (Unlocks.Dynamite, 3), (Unlocks.Underground_Leaderboard, 1)]
    for tech, level in stages:
        while num_unlocked(tech) < level:
            if get_time() > 72000:
                quick_print("underground_reset_failed", "deadline", tech)
                return
            cost = get_cost(tech)
            ready = False
            for funding in range(8):
                for item in cost:
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
    if item == Items.Block or item == Items.Coal or item == Items.Iron or item == Items.Quartz:
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


def ur_mine(item, goal):
    # 普通Reset地层不能套用资源榜固定深度；逐层读实况，遇基岩后重生。
    empty = 0
    deadline = get_time() + 18000
    for cycle in range(128):
        clear()
        size = get_world_size()
        before = num_items(item)
        for layer in range(1024):
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
    for cycle in range(512):
        if num_items(Items.Dynamite) >= goal:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        clear()
        if not ur_d_move_to(1, 1, size):
            return
        covers = 0
        while get_ground_type() != Grounds.Dynamite and covers < 256:
            if get_time() - began > 72000 or not dig():
                quick_print("dynamite_failed", "search_action", cycle)
                return
            covers += 1
        if get_ground_type() != Grounds.Dynamite:
            empty += 1
            quick_print("dynamite_search_miss", cycle, empty, get_time())
            if empty >= 8:
                quick_print("dynamite_failed", "eight_search_misses")
                return
            continue
        empty = 0
        depth = get_pos_z()
        if not ur_d_prepare_all(size, depth):
            quick_print("dynamite_failed", "prepare", cycle)
            return
        before = num_items(Items.Dynamite)
        result, guesses = ur_d_dynamite_solve(size, depth)
        quick_print("dynamite_cycle", cycle, result, guesses, num_items(Items.Dynamite) - before, get_time(), num_items(Items.Dynamite))
        if result == "error":
            return
    quick_print("dynamite_failed", "cycle_limit", get_time(), num_items(Items.Dynamite))


def ur_d_dynamite_solve(size, depth):
    # 数字由唯一协调机合并；推理停滞才猜，猜测不写成已证明SAFE事实。
    status, number = ur_d_dig_target(1 + size, size, depth)
    if status != "number":
        return status, 0
    facts = {1 + size: number}
    status = "waiting"
    for guesses in range(33):
        if status == "waiting" or status == "incomplete":
            status, facts = ur_d_worker(size, (0, size - 1, 0, size - 1), depth, facts, False)
        if status == "ended":
            return status, guesses
        if status == "done":
            # 所有未挖格均已证明为雷后，挖已揭开的Soot完成一次人工结算。
            for cell in facts:
                if facts[cell] >= 0 and ur_d_move_to(cell % size, cell // size, size):
                    if get_ground_type() == Grounds.Soot and dig():
                        return "settled", guesses
            return "error", guesses
        if status == "mine":
            for _ in range(4):
                if get_entity_type() != Entities.Dynamite:
                    break
                do_a_flip()
            return "mine", guesses
        if status == "error" and get_pos_z() < depth - 1:
            quick_print("dynamite_board_changed", guesses, get_pos_z(), get_ground_type())
            return "board_changed", guesses
        if status == "error" or guesses == 32:
            return "error", guesses
        choice = ur_d_dynamite_guess(facts, size)
        if choice == None:
            return "error", guesses
        status, number = ur_d_dig_target(choice, size, depth)
        if status == "mine":
            for _ in range(4):
                if get_entity_type() != Entities.Dynamite:
                    break
                do_a_flip()
            return "mine", guesses + 1
        if status == "ended":
            return status, guesses + 1
        if status != "number":
            if get_pos_z() < depth - 1:
                quick_print("dynamite_board_changed", guesses + 1, get_pos_z(), get_ground_type())
                return "board_changed", guesses + 1
            return "error", guesses + 1
        facts[choice] = number
        status = "waiting"
    return "error", 32


def ur_d_dynamite_guess(facts, size):
    # 取相邻公开约束中最大的剩余雷比例作风险启发式，不声称独立概率。
    best = None
    best_risk = 2
    for cell in range(size * size):
        if cell in facts:
            if facts[cell] == ur_d_SAFE:
                return cell
            continue
        risk = -1
        for clue in ur_d_adjacent_cells(size, cell):
            if clue not in facts or facts[clue] < 0:
                continue
            remaining = facts[clue]
            unknown = 0
            for other in ur_d_adjacent_cells(size, clue):
                if other not in facts:
                    unknown += 1
                elif facts[other] == ur_d_MINE:
                    remaining -= 1
            if unknown > 0:
                risk = max(risk, remaining / unknown)
        if risk < 0:
            risk = 0.5
        if risk < best_risk:
            best = cell
            best_risk = risk
    return best


def ur_d_prepare_all(size, depth):
    handles = []
    ok = True
    for x in range(size):
        if num_drones() < max_drones():
            handle = spawn_drone(ur_d_prepare_column, x, size, depth)
            if handle != None:
                handles.append(handle)
                continue
        if not ur_d_prepare_column(x, size, depth):
            ok = False
            break
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def ur_d_prepare_column(x, size, depth):
    if not ur_d_move_to(x, 0, size):
        return False
    for row in range(size):
        while get_pos_z() > depth:
            if not dig():
                return False
        if get_pos_z() != depth or get_ground_type() != Grounds.Dynamite:
            return False
        if row < size - 1 and not move(North):
            return False
    return True


# 只交回窗口内已证明的事实；窗口外的辅助约束变量不导出。


# 交接只携带接收区域8×12内的数字/SAFE/MINE，不传全图棋盘。


def ur_d_finish_region(board, status):
    facts = {}
    size = board["size"]
    left, right, bottom, top = board["info"]
    for y in range(bottom, top + 1):
        for x in range(left, right + 1):
            cell = x + y * size
            if board["cells"][cell] != ur_d_UNKNOWN:
                facts[cell] = board["cells"][cell]
    return status, facts


# 数字的八邻域不环绕；栈末端优先四邻方向。
def ur_d_adjacent_cells(size, cell):
    x = cell % size
    y = cell // size
    diagonal = []
    adjacent = []
    for ny in range(max(0, y - 1), min(size, y + 2)):
        for nx in range(max(0, x - 1), min(size, x + 2)):
            if nx == x and ny == y:
                continue
            other = nx + ny * size
            if nx == x or ny == y:
                adjacent.append(other)
            else:
                diagonal.append(other)
    return diagonal + adjacent


def ur_d_build_board(size):
    cells = []
    for cell in range(size * size):
        cells.append(ur_d_UNKNOWN)
    return {"size": size, "cells": cells, "owned": set(), "sampled": set(),
            "neighbors": {}, "tasks": {}, "tops": [None, None, None],
            "versions": {}, "checked": {}, "constraints": {}, "closed": set(),
            "ending": None}


# 三个独立LIFO，每格每类最多一个节点：[更早任务, 较新任务, 版本]。
def ur_d_remove_task(board, key):
    tasks = board["tasks"]
    if key not in tasks:
        return
    older, newer, version = tasks.pop(key)
    if older != None:
        tasks[older][1] = newer
    if newer != None:
        tasks[newer][0] = older
    else:
        board["tops"][key % 3] = older


def ur_d_push_task(board, kind, cell, version):
    tasks = board["tasks"]
    key = cell * 3 + kind
    if key in tasks:
        if board["tops"][kind] == key:
            tasks[key][2] = version
            return
        ur_d_remove_task(board, key)
    older = board["tops"][kind]
    tasks[key] = [older, None, version]
    if older != None:
        tasks[older][1] = key
    board["tops"][kind] = key


# 只执行本区开挖任务，数字约束允许跨区；零扩展始终先于推理。
def ur_d_next_kind(board):
    for kind in range(3):
        while board["tops"][kind] != None:
            key = board["tops"][kind]
            cell = key // 3
            valid = False
            if kind == ur_d_CLUE_TASK:
                valid = cell not in board["closed"] and board["tasks"][key][2] == board["versions"][cell]
            else:
                valid = cell in board["owned"] and board["cells"][cell] == ur_d_SAFE
            if valid:
                return kind
            ur_d_remove_task(board, key)
    return None


def ur_d_neighbors(board, cell):
    if cell not in board["neighbors"]:
        board["neighbors"][cell] = ur_d_adjacent_cells(board["size"], cell)
    return board["neighbors"][cell]


def ur_d_queue_clue(board, clue):
    if clue in board["closed"]:
        return
    version = 0
    if clue in board["versions"]:
        version = board["versions"][clue] + 1
    board["versions"][clue] = version
    ur_d_push_task(board, ur_d_CLUE_TASK, clue, version)


def ur_d_queue_clues(board, cell):
    for clue in ur_d_neighbors(board, cell):
        if board["cells"][clue] >= 0:
            ur_d_queue_clue(board, clue)


# SAFE可从普通开挖提升到零扩展；不允许后来的普通任务降低已有优先级。
def ur_d_queue_open(board, cell, kind):
    if cell not in board["owned"]:
        return
    if kind == ur_d_ZERO_TASK:
        ur_d_remove_task(board, cell * 3 + ur_d_OPEN_TASK)
        ur_d_push_task(board, ur_d_ZERO_TASK, cell, 0)
    elif cell * 3 + ur_d_ZERO_TASK not in board["tasks"]:
        ur_d_push_task(board, ur_d_OPEN_TASK, cell, 0)


def ur_d_mark_cells(board, targets, value, priority):
    cells = board["cells"]
    for cell in targets:
        previous = cells[cell]
        if previous >= 0 and value == ur_d_SAFE:
            continue
        if previous != value:
            if previous != ur_d_UNKNOWN:
                quick_print("格子推断冲突：", cell % board["size"], cell // board["size"])
                return False
            cells[cell] = value
            if value == ur_d_MINE:
                if cell in board["owned"]:
                    board["owned"].remove(cell)
            ur_d_queue_clues(board, cell)
        if value == ur_d_SAFE:
            ur_d_queue_open(board, cell, priority)
    return True


# 本区及跨区读数统一走这里；只更新任务，不在读数期间运行infer。
def ur_d_record_number(board, cell, number):
    previous = board["cells"][cell]
    if previous == number:
        return True
    if previous == ur_d_MINE or previous >= 0:
        quick_print("现场数字与记录冲突：", cell % board["size"], cell // board["size"])
        return False
    board["cells"][cell] = number
    if cell in board["owned"]:
        board["owned"].remove(cell)
    ur_d_remove_task(board, cell * 3 + ur_d_ZERO_TASK)
    ur_d_remove_task(board, cell * 3 + ur_d_OPEN_TASK)
    ur_d_queue_clue(board, cell)
    if previous == ur_d_UNKNOWN:
        ur_d_queue_clues(board, cell)
    around = ur_d_neighbors(board, cell)
    if number == 0:
        if not ur_d_mark_cells(board, around, ur_d_SAFE, ur_d_ZERO_TASK):
            return False
        board["closed"].add(cell)
        ur_d_remove_task(board, cell * 3 + ur_d_CLUE_TASK)
    return True


def ur_d_constraint(board, clue):
    version = board["versions"][clue]
    if clue in board["constraints"]:
        cached = board["constraints"][clue]
        if cached[0] == version:
            return cached[1], cached[2]
    remaining = board["cells"][clue]
    unknown = set()
    for cell in ur_d_neighbors(board, clue):
        if board["cells"][cell] == ur_d_MINE:
            remaining -= 1
        elif board["cells"][cell] == ur_d_UNKNOWN:
            unknown.add(cell)
    if remaining < 0 or remaining > len(unknown):
        quick_print("数字约束矛盾：", clue % board["size"], clue // board["size"])
        return None
    board["constraints"][clue] = (version, unknown, remaining)
    return unknown, remaining


# A包含于B时，B-A的实弹数等于两者剩余实弹数之差。
def ur_d_infer_subset(board, first, second):
    a = ur_d_constraint(board, first)
    b = ur_d_constraint(board, second)
    if a == None or b == None:
        return None
    small, small_count = a
    large, large_count = b
    if len(small) > len(large):
        small, large = large, small
        small_count, large_count = large_count, small_count
    for cell in small:
        if cell not in large:
            return False
    difference = []
    for cell in large:
        if cell not in small:
            difference.append(cell)
    remaining = large_count - small_count
    if remaining < 0 or remaining > len(difference):
        return None
    if len(difference) == 0:
        return False
    if remaining == 0:
        if not ur_d_mark_cells(board, difference, ur_d_SAFE, ur_d_OPEN_TASK):
            return None
        return True
    if remaining == len(difference):
        if not ur_d_mark_cells(board, difference, ur_d_MINE, ur_d_OPEN_TASK):
            return None
        return True
    return False


# 只由最低优先级任务调用；每次判断一个数字及共享未知格的附近数字。
def ur_d_infer(board, clue):
    if clue in board["closed"]:
        return True
    version = board["versions"][clue]
    if clue in board["checked"] and board["checked"][clue] == version:
        ur_d_remove_task(board, clue * 3 + ur_d_CLUE_TASK)
        return True
    row = ur_d_constraint(board, clue)
    if row == None:
        return False
    unknown, remaining = row
    if remaining == 0 or remaining == len(unknown):
        value = ur_d_MINE
        if remaining == 0:
            value = ur_d_SAFE
        if not ur_d_mark_cells(board, unknown, value, ur_d_OPEN_TASK):
            return False
        board["closed"].add(clue)
        ur_d_remove_task(board, clue * 3 + ur_d_CLUE_TASK)
        return True
    peers = set()
    for cell in unknown:
        for other in ur_d_neighbors(board, cell):
            if other != clue and board["cells"][other] >= 0 and other not in board["closed"]:
                peers.add(other)
    ur_d_push_task(board, ur_d_CLUE_TASK, clue, version)
    for other in peers:
        changed = ur_d_infer_subset(board, clue, other)
        if changed == None:
            return False
        if changed:
            return True
    board["checked"][clue] = version
    ur_d_remove_task(board, clue * 3 + ur_d_CLUE_TASK)
    return True


# 每台使用相同求解器；初次到位后，移动和读取均由各自窗口限制。
def ur_d_worker(size, area, depth, facts, await_start):
    if await_start:
        until = get_tick_count() + 100000
        while get_pos_z() == depth:
            if get_tick_count() >= until:
                return "error", {}
    x0, x1, y0, y1 = area
    board = ur_d_build_board(size)
    travel = (max(0, x0 - 1), min(size - 1, x1 + 1), max(0, y0 - 1), min(size - 1, y1 + 1))
    board["travel"] = travel
    board["info"] = (max(0, x0 - 2), min(size - 1, x1 + 2), max(0, y0 - 2), min(size - 1, y1 + 2))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            board["owned"].add(x + y * size)
    for cell in facts:
        value = facts[cell]
        if value >= 0:
            if not ur_d_record_number(board, cell, value):
                return "error", {}
        elif not ur_d_mark_cells(board, [cell], value, ur_d_OPEN_TASK):
            return "error", {}
    seed = 1 + size
    if get_pos_x() == 1 and get_pos_y() == 1 and ur_d_inside(seed, size, board["info"]):
        status, first_number = ur_d_read_ground(depth)
        if status != "number":
            return status, {}
        if not ur_d_record_number(board, seed, first_number):
            return "error", {}
    # 每次启动仅部署一次；求解期间禁止用环绕捷径离开自己的活动区。
    if not ur_d_move_to(max(travel[0], min(travel[1], get_pos_x())),
                   max(travel[2], min(travel[3], get_pos_y())), size):
        return "error", {}
    probes = []
    for y in range(travel[2], travel[3] + 1):
        if (y - travel[2]) % 2 == 0:
            for x in range(travel[0], travel[1] + 1):
                probes.append(x + y * size)
        else:
            for x in range(travel[1], travel[0] - 1, -1):
                probes.append(x + y * size)
    # 四向读取缺少最外斜角，临时从活动区角点沿y跨一步，再横向读取。
    for y in [travel[2] - 1, travel[3] + 1]:
        if y < board["info"][2] or y > board["info"][3]:
            continue
        for x in [travel[0], travel[1]]:
            probes.append(x + y * size)
    probe_at = 0
    scan_epoch = num_items(Items.Dynamite)
    while board["ending"] == None and len(board["owned"]) > 0:
        kind = ur_d_next_kind(board)
        if kind != None:
            key = board["tops"][kind]
            cell = key // 3
            ur_d_remove_task(board, key)
            if kind == ur_d_CLUE_TASK:
                if not ur_d_infer(board, cell):
                    board["ending"] = "error"
            else:
                if not ur_d_open_cell(board, cell, depth) and board["ending"] == None:
                    board["ending"] = "error"
            continue
        if probe_at < len(probes):
            cell = probes[probe_at]
            if not ur_d_probe_needed(board, cell):
                probe_at += 1
                continue
            if not ur_d_visit_cell(board, cell, depth):
                board["ending"] = "error"
            # 若观测被零任务抢占，保留游标，之后补读这个点剩余的方向。
            continue
        epoch = num_items(Items.Dynamite)
        if epoch != scan_epoch:
            scan_epoch = epoch
            board["sampled"] = set()
            probe_at = 0
            continue
        result, unused = ur_d_audit_constraints(board, epoch)
        if result == "changed" or result == "stale":
            continue
        if result == "error":
            board["ending"] = "error"
            continue
        if result == "incomplete":
            quick_print("区域", x0, y0, "局部核对达到预算，交回已知事实。")
        return ur_d_finish_region(board, result)
    if board["ending"] != None:
        return ur_d_finish_region(board, board["ending"])
    quick_print("区域", x0, y0, "已处理完。")
    return ur_d_finish_region(board, "done")


# 窗口坐标为包含两端的(left, right, bottom, top)，不跨世界边界环绕。
def ur_d_inside(cell, size, bounds):
    x = cell % size
    y = cell // size
    return bounds[0] <= x and x <= bounds[1] and bounds[2] <= y and y <= bounds[3]


# 判断脚下及四向是否仍有本轮信息未读，不能仅因脚下数字已知就跳过邻居。
def ur_d_probe_needed(board, cell):
    size = board["size"]
    x = cell % size
    y = cell // size
    for dx, dy in [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx = x + dx
        ny = y + dy
        if nx < 0 or nx >= size or ny < 0 or ny >= size:
            continue
        other = nx + ny * size
        if not ur_d_inside(other, size, board["info"]) or other in board["sampled"]:
            continue
        if board["cells"][other] == ur_d_UNKNOWN or board["cells"][other] == ur_d_SAFE:
            return True
    return False


# 仅枚举关联本区未决格的分量；其余边缘约束不消耗枚举预算。
# 外部未知格仍是约束变量，但不会因此扩大实际读取或移动范围。
def ur_d_audit_constraints(board, epoch):
    rows = []
    links = {}
    for clue in board["versions"]:
        if clue in board["closed"]:
            continue
        row = ur_d_constraint(board, clue)
        if row == None:
            return "error", None
        targets, count = row
        if len(targets) == 0:
            continue
        index = len(rows)
        rows.append((targets, count))
        for cell in targets:
            if cell not in links:
                links[cell] = []
            links[cell].append(index)
    pending = set(links)
    deadline = get_tick_count() + ur_d_ENUM_TICKS
    while len(pending) > 0:
        first = None
        for cell in board["owned"]:
            if cell in pending:
                first = cell
                break
        if first == None:
            break
        todo = [first]
        pending.remove(first)
        order = []
        row_ids = set()
        while len(todo) > 0:
            cell = todo.pop()
            order.append(cell)
            for index in links[cell]:
                if index in row_ids:
                    continue
                row_ids.add(index)
                for other in rows[index][0]:
                    if other in pending:
                        pending.remove(other)
                        todo.append(other)
        if num_items(Items.Dynamite) != epoch:
            return "stale", None
        if len(order) > ur_d_ENUM_CELLS or get_tick_count() >= deadline:
            return "incomplete", None
        left = {}
        need = {}
        for index in row_ids:
            left[index] = len(rows[index][0])
            need[index] = rows[index][1]
        values = []
        seen = []
        for cell in order:
            values.append(0)
            seen.append(0)
        search = {"order": order, "links": links, "left": left, "need": need,
                  "values": values, "seen": seen, "both": 0, "solutions": 0,
                  "nodes": 0, "stop": None, "deadline": deadline, "epoch": epoch}
        ur_d_enumerate_layouts(search, 0)
        if search["stop"] == "stale":
            return "stale", None
        if search["stop"] == "incomplete":
            return "incomplete", None
        if search["solutions"] == 0:
            return "error", None
        changed = False
        for i in range(len(order)):
            if seen[i] == 1 or seen[i] == 2:
                value = ur_d_SAFE
                if seen[i] == 2:
                    value = ur_d_MINE
                if not ur_d_mark_cells(board, [order[i]], value, ur_d_OPEN_TASK):
                    return "error", None
                changed = True
        if changed:
            return "changed", None
    if num_items(Items.Dynamite) != epoch:
        return "stale", None
    return "waiting", None


# 深度优先枚举可满足布局，维护各数字的剩余格数和剩余雷数以即时剪枝。
def ur_d_enumerate_layouts(search, at):
    if search["stop"] != None:
        return
    search["nodes"] += 1
    if search["nodes"] % 64 == 0:
        if num_items(Items.Dynamite) != search["epoch"]:
            search["stop"] = "stale"
            return
        if search["nodes"] >= ur_d_ENUM_NODES or get_tick_count() >= search["deadline"]:
            search["stop"] = "incomplete"
            return
    if search["nodes"] % 512 == 0:
        quick_print("停滞约束核对：", len(search["order"]), "格，节点", search["nodes"])
    if at == len(search["order"]):
        search["solutions"] += 1
        for i in range(at):
            value = search["values"][i] + 1
            if search["seen"][i] == 0:
                search["seen"][i] = value
            elif search["seen"][i] != 3 and search["seen"][i] != value:
                search["seen"][i] = 3
                search["both"] += 1
        if search["both"] == at:
            search["stop"] = "ambiguous"
        return
    cell = search["order"][at]
    for value in [0, 1]:
        search["values"][at] = value
        valid = True
        for index in search["links"][cell]:
            search["left"][index] -= 1
            search["need"][index] -= value
            if search["need"][index] < 0 or search["need"][index] > search["left"][index]:
                valid = False
        if valid:
            ur_d_enumerate_layouts(search, at + 1)
        for index in search["links"][cell]:
            search["left"][index] += 1
            search["need"][index] += value
        if search["stop"] != None:
            return


# 返回closed/number/ended/mine/error；只把实际数字交给求解器。
def ur_d_read_ground(depth, direction=None):
    z = get_pos_z(direction)
    if z >= depth:
        return "closed", None
    if z != depth - 1 or get_ground_type(direction) != Grounds.Soot:
        return "error", None
    if get_entity_type(direction) == Entities.Dynamite:
        return "mine", None
    number = measure(direction)
    if number == None:
        return "ended", None
    if number < 0 or number > 8:
        return "error", None
    return "number", number


# 调用者必须持有该格的唯一开挖权；检查地层只负责防止跨层，不充当并发锁。
def ur_d_dig_target(cell, size, depth):
    if not ur_d_move_to(cell % size, cell // size, size):
        return "error", None
    z = get_pos_z()
    if z == depth:
        if get_ground_type() != Grounds.Dynamite or not dig():
            return "error", None
    elif z != depth - 1:
        return "error", None
    return ur_d_read_ground(depth)


def ur_d_read_cell(board, cell, direction, depth):
    if not ur_d_inside(cell, board["size"], board["info"]):
        return True
    if board["cells"][cell] >= 0 or board["cells"][cell] == ur_d_MINE or cell in board["sampled"]:
        return True
    status, number = ur_d_read_ground(depth, direction)
    board["sampled"].add(cell)
    if status == "closed":
        return True
    if status != "number":
        board["ending"] = status
        return status == "ended"
    return ur_d_record_number(board, cell, number)


# 读取脚下及四邻；一旦已有零扩展任务就立即让回开挖循环。
def ur_d_observe(board, depth):
    size = board["size"]
    x = get_pos_x()
    y = get_pos_y()
    cell = x + y * size
    if not ur_d_read_cell(board, cell, None, depth):
        return False
    for dx, dy, direction in [(0, 1, North), (1, 0, East), (0, -1, South), (-1, 0, West)]:
        if board["ending"] != None or ur_d_next_kind(board) == ur_d_ZERO_TASK:
            return True
        nx = x + dx
        ny = y + dy
        if nx >= 0 and nx < size and ny >= 0 and ny < size:
            if not ur_d_read_cell(board, nx + ny * size, direction, depth):
                return False
    return True


def ur_d_open_cell(board, cell, depth):
    if cell not in board["owned"]:
        return False
    if board["cells"][cell] != ur_d_SAFE and board["cells"][cell] != ur_d_UNKNOWN:
        return False
    if not ur_d_move_local(board, cell):
        return False
    status, number = ur_d_dig_target(cell, board["size"], depth)
    if status != "number":
        board["ending"] = status
        return status == "ended"
    if not ur_d_record_number(board, cell, number):
        return False
    if ur_d_next_kind(board) == ur_d_ZERO_TASK:
        return True
    return ur_d_observe(board, depth)


# 角点短暂外跨读完立即退回；普通观测点留在6×10活动区内。
def ur_d_visit_cell(board, cell, depth):
    if not ur_d_move_local(board, cell):
        return False
    ok = ur_d_observe(board, depth)
    travel = board["travel"]
    x = get_pos_x()
    y = get_pos_y()
    if y < travel[2] or y > travel[3]:
        if not ur_d_move_direct(x, max(travel[2], min(travel[3], y))):
            return False
    return ok


# 开挖/读取共用移动入口，只允许活动矩形和四个角点的单步外跨位置。
def ur_d_move_local(board, cell):
    size = board["size"]
    travel = board["travel"]
    tx = cell % size
    ty = cell // size
    if not ur_d_inside(cell, size, travel):
        if not ur_d_inside(cell, size, board["info"]):
            return False
        if (tx != travel[0] and tx != travel[1]) or (ty != travel[2] - 1 and ty != travel[3] + 1):
            return False
    x = get_pos_x()
    y = get_pos_y()
    if x < travel[0] or x > travel[1]:
        return False
    if y < travel[2] or y > travel[3]:
        if not ur_d_move_direct(x, max(travel[2], min(travel[3], y))):
            return False
    ay = max(travel[2], min(travel[3], ty))
    if not ur_d_move_direct(tx, ay):
        return False
    if ay != ty:
        return ur_d_move_direct(tx, ty)
    return True


# 矩形内部用直接路径，避免环绕捷径经过其他区域。
def ur_d_move_direct(tx, ty):
    dx = tx - get_pos_x()
    dy = ty - get_pos_y()
    horizontal = East
    vertical = North
    if dx < 0:
        horizontal = West
    if dy < 0:
        vertical = South
    for _ in range(abs(dx)):
        if not move(horizontal):
            return False
    for _ in range(abs(dy)):
        if not move(vertical):
            return False
    return True


# 仅用于覆盖层准备、首次部署，以及已由move_local到位后的原地dig。
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


ur_d_REGION_WIDTH = 4
ur_d_REGION_HEIGHT = 8
ur_d_UNKNOWN = -2
ur_d_MINE = -1
ur_d_SAFE = -3
ur_d_ZERO_TASK = 0
ur_d_OPEN_TASK = 1
ur_d_CLUE_TASK = 2
ur_d_ENUM_CELLS = 24
ur_d_ENUM_NODES = 4096
ur_d_ENUM_TICKS = 12000


if __name__ == "__main__":
    lb_fastest_underground_reset()
