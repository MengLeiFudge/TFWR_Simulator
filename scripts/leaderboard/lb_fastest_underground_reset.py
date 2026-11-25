from __builtins__ import *
# 完整轮时间：本地游戏随机12轮均值 36:31.994（SD 79.501s，95% CI ±50.513s，12/12达标；seed1..6均 35:10.521，实机待验证）。

ur_m_OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
ur_m_DIRECTIONS = [North, East, South, West]
ur_m_BACKS = [South, West, North, East]

UR_D_UNKNOWN = -2
UR_D_MINE = -1
UR_D_SAFE = -3
UR_D_DONE = 9
UR_D_DIG_LIMIT = 768
UR_D_PHASE_LIMIT = 256
ur_d_WORK_LAYOUTS = {}


def lb_fastest_underground_reset():
    # 高效地上前缀：直达 4 机 + 8×8 + Polyculture 1 + Speed 5 + Fertilizer 2
    prefix_route = [
        (Unlocks.Expand, 1),
        (Unlocks.Plant, 1),
        (Unlocks.Speed, 1),
        (Unlocks.Speed, 2),
        (Unlocks.Expand, 2),
        (Unlocks.Carrots, 1),
        (Unlocks.Trees, 1),
        (Unlocks.Watering, 1),
        (Unlocks.Speed, 3),
        (Unlocks.Grass, 2),
        (Unlocks.Trees, 2),
        (Unlocks.Grass, 3),
        (Unlocks.Trees, 3),
        (Unlocks.Expand, 3),
        (Unlocks.Carrots, 2),
        (Unlocks.Carrots, 3),
        (Unlocks.Watering, 2),
        (Unlocks.Speed, 4),
        (Unlocks.Watering, 3),
        (Unlocks.Fertilizer, 1),
        (Unlocks.Expand, 4),
        (Unlocks.Sunflowers, 1),
        (Unlocks.Watering, 4),
        (Unlocks.Grass, 4),
        (Unlocks.Speed, 5),
        (Unlocks.Mazes, 1),
        (Unlocks.Megafarm, 1),
        (Unlocks.Pumpkins, 1),
        (Unlocks.Expand, 5),
        (Unlocks.Pumpkins, 2),
        (Unlocks.Megafarm, 2),
        (Unlocks.Polyculture, 1),
        (Unlocks.Carrots, 4),
        (Unlocks.Fertilizer, 2),
    ]
    for index in range(len(prefix_route)):
        tech, level = prefix_route[index]
        if num_unlocked(tech) != level - 1:
            quick_print("wrong_level", index, tech, num_unlocked(tech))
            return
        cost = get_cost(tech)
        if not ur_prefix_pay(cost, index) or not unlock(tech):
            quick_print("unpaid", index, tech, level, get_time(), cost)
            return
        quick_print("paid", index, tech, num_unlocked(tech), get_time(), num_items(Items.Power))
        if tech == Unlocks.Sunflowers and not ensure_power(100):
            return
    quick_print("underground_reset_prefix", get_time(), max_drones(), get_world_size(), num_items(Items.Power))

    # 地下科技链：按实际支付并按资源依赖倒序筹资（Quartz -> Iron -> Coal），一次筹齐 7600 金。
    stages = [
        (Unlocks.Mining, 2), (Unlocks.Coal, 1), (Unlocks.Rice, 1),
        (Unlocks.Mining, 3), (Unlocks.Rice, 3), (Unlocks.Coal, 2),
        (Unlocks.Iron, 1), (Unlocks.Mining, 4), (Unlocks.Bamboo, 1),
        (Unlocks.Mining, 5), (Unlocks.Prospecting, 1), (Unlocks.Iron, 2),
        (Unlocks.Mining, 6), (Unlocks.Rice, 4), (Unlocks.Coal, 3),
        (Unlocks.Iron, 4), (Unlocks.Quartz, 2), (Unlocks.Ore_Boost, 1), (Unlocks.Quartz, 3), (Unlocks.Bamboo, 3),
        (Unlocks.Mining, 7), (Unlocks.Mushrooms, 3), (Unlocks.Mining, 8),
        (Unlocks.Bamboo, 4), (Unlocks.Dynamite, 4), (Unlocks.Pumpkins, 3),
        (Unlocks.Expand, 6), (Unlocks.Underground_Leaderboard, 1),
    ]
    item_order = [
        Items.Quartz, Items.Iron, Items.Coal, Items.Block,
        Items.Mushroom, Items.Dynamite, Items.Bamboo, Items.Rice,
        Items.Gold, Items.Pumpkin, Items.Carrot, Items.Wood, Items.Hay,
    ]
    for tech, level in stages:
        while num_unlocked(tech) < level:
            if get_time() > 6900:
                quick_print("underground_reset_failed", "deadline", tech)
                return
            cost = get_cost(tech)
            ready = False
            for funding in range(8):
                ordered = []
                for key in item_order:
                    if key in cost:
                        ordered.append(key)
                for key in cost:
                    if key not in ordered:
                        ordered.append(key)
                for item in ordered:
                    if num_items(Items.Power) < 100:
                        power_goal = 900
                        if tech == Unlocks.Underground_Leaderboard:
                            power_goal = 500
                        if not ur_power_stock(power_goal):
                            quick_print("underground_reset_failed", "power", tech)
                            return
                    target_amt = cost[item]
                    # Mushrooms 2 时一次筹齐 7600 金（覆盖 Mushrooms 2/3 与 Dynamite 1）
                    if item == Items.Gold and tech == Unlocks.Mushrooms and num_unlocked(Unlocks.Mushrooms) == 1:
                        target_amt = max(target_amt, 7600)
                    if not ur_need(item, target_amt):
                        quick_print("underground_reset_failed", "resource", tech, item, target_amt)
                        return
                ready = True
                for item in cost:
                    if num_items(item) < cost[item]:
                        ready = False
                if ready:
                    break
            if not ready or not unlock(tech):
                quick_print("underground_reset_failed", "unlock", tech)
                return
            quick_print("underground_reset_upgrade", tech, num_unlocked(tech), get_time(), num_items(Items.Power))
    quick_print("underground_reset_done", num_unlocked(Unlocks.Underground_Leaderboard) > 0, get_time())


def ur_prefix_pay(cost, i):
    if affordable(cost):
        return True
    if i < 5:
        return starter(cost, i)
    if Items.Gold in cost and num_items(Items.Gold) < cost[Items.Gold]:
        size = get_world_size()
        n = size
        if max_drones() > 1:
            n = size // 2
        if not ensure_power(80 * max_drones()):
            return False
        if not small_maze_gold(cost[Items.Gold], n):
            return False
    if Items.Pumpkin in cost and not pumpkin_stock(cost[Items.Pumpkin]):
        return False
    if affordable(cost):
        return True
    basic_cost = {}
    for item in cost:
        if item in [Items.Wood, Items.Hay, Items.Carrot, Items.Weird_Substance]:
            basic_cost[item] = cost[item]
    if num_unlocked(Unlocks.Polyculture) > 0:
        return stock_anchors(basic_cost)
    return mixed_stock(basic_cost, i)


def ur_power_stock(goal):
    if num_items(Items.Power) >= goal:
        return True
    clear()
    size = get_world_size()
    for _ in range(8):
        if num_items(Items.Power) >= goal:
            return True
        if not basic({Items.Carrot: size * size}):
            return False
        if not parallel_solar_reserve(size, goal):
            return False
    return num_items(Items.Power) >= goal


def ur_need(item, goal):
    if num_items(item) >= goal:
        return True
    quick_print("underground_reset_collect", item, goal, get_time())
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot or item == Items.Pumpkin:
        clear()
        if item == Items.Pumpkin:
            return pumpkin_stock(goal)
        return basic({item: goal})
    if item == Items.Quartz:
        return ur_q_stock(goal)
    if item == Items.Iron and num_unlocked(Unlocks.Prospecting) > 0:
        return ur_i_stock(goal)
    if item == Items.Coal:
        return ur_c_hour_coal(goal)
    if item == Items.Block or item == Items.Iron:
        return ur_c_ur_mine_parallel(item, goal)
    if item == Items.Rice:
        ur_rice_stock(goal)
    elif item == Items.Bamboo:
        size = get_world_size()
        factor = 2 ** (num_unlocked(Unlocks.Bamboo) - 1)
        rows_per = 1
        if goal >= 10000:
            rows_per = size // min(4, max_drones())
            if rows_per < 1:
                rows_per = 1
        stems = min(4, max_drones()) * rows_per * (size - 1)
        reserve = (stems + 8) * factor
        if not ur_need(Items.Rice, reserve):
            return False
        ur_bamboo_stock(goal)
    elif item == Items.Gold:
        if not ur_power_stock(240):
            return False
        clear()
        return small_maze_gold(goal, 4)
    elif item == Items.Mushroom:
        if num_unlocked(Unlocks.Mining) >= 8 and num_unlocked(Unlocks.Dynamite) == 0:
            goal = max(goal, 580)
        ur_mushroom_stock(goal)
    elif item == Items.Dynamite:
        ur_dynamite_stock(goal)
    else:
        return False
    return num_items(item) >= goal


def ur_c_ur_mine_parallel(item, goal, deadline=None):
    if deadline == None:
        deadline = min(6900, get_time() + 1800)
    layers = 256
    if item == Items.Coal and num_unlocked(Unlocks.Rice) > 0:
        layers = 16
    elif item == Items.Iron:
        layers = 64
    workers = min(get_world_size(), max_drones())
    for cycle in range(128):
        if num_items(item) >= goal:
            return True
        if get_time() > deadline:
            return False
        clear()
        handles = []
        passed = True
        for worker in range(1, workers):
            handle = spawn_drone(ur_c_ur_mine_parallel_worker, worker, workers, layers, item, goal, deadline)
            if handle == None:
                passed = False
                break
            handles.append(handle)
        if passed:
            passed = ur_c_ur_mine_parallel_worker(0, workers, layers, item, goal, deadline)
        for handle in handles:
            if not wait_for(handle):
                passed = False
        if not passed:
            return False
        if num_items(item) >= goal:
            return True
    return num_items(item) >= goal


def ur_c_ur_mine_parallel_worker(first, stride, layers, item, goal, deadline):
    size = get_world_size()
    for layer in range(layers):
        if get_time() > deadline:
            return False
        for x in range(first, size, stride):
            if not ur_c_ur_d_move_to(x, 0, size):
                return False
            for y in range(size):
                if num_items(item) >= goal:
                    return True
                if get_time() > deadline:
                    return False
                if get_pos_z() >= -layer and get_hardness() < 10000000:
                    if not dig():
                        return False
                if y + 1 < size:
                    if not move(North):
                        return False
    return True


def ur_i_stock(goal):
    # 主机用 prospect_iron 定位铁矿脉，命中后派 4 机并行掘目标柱及相邻三柱。
    deadline = min(6900, get_time() + 1800)
    size = get_world_size()
    workers = min(4, max_drones())
    for cycle in range(128):
        if num_items(Items.Iron) >= goal:
            return True
        if get_time() > deadline:
            return False
        if num_items(Items.Coal) < 24 and not ur_need(Items.Coal, 64):
            return False
        clear()
        dry = 0
        drilling = 0
        for action in range(384):
            if num_items(Items.Iron) >= goal:
                return True
            if get_time() > deadline:
                return False
            if get_ground_type() == Grounds.Iron:
                ix, iy, iz = get_pos_x(), get_pos_y(), get_pos_z()
                cols = [(ix, iy)]
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < size and 0 <= ny < size and len(cols) < workers:
                        cols.append((nx, ny))
                handles = []
                ok = True
                for k in range(1, len(cols)):
                    h = spawn_drone(ur_i_dig_col, cols[k][0], cols[k][1], iz, size, goal, deadline)
                    if h == None:
                        ok = False
                        break
                    handles.append(h)
                if ok:
                    ok = ur_i_dig_col(cols[0][0], cols[0][1], iz, size, goal, deadline)
                for h in handles:
                    if not wait_for(h):
                        ok = False
                if not ok:
                    return False
                dry = 0
                drilling = 0
                continue
            direction = None
            for nearby in [North, East, South, West]:
                if get_ground_type(nearby) == Grounds.Iron:
                    direction = nearby
                    break
            if direction == None and drilling <= 0:
                if num_items(Items.Coal) < 1:
                    break
                direction = prospect_iron()
                if direction == None:
                    drilling = 16
            if direction != None:
                if not move(direction):
                    return False
                drilling = 0
                continue
            if get_pos_z() < -80 or get_hardness() >= 10000000:
                break
            drilling -= 1
            previous = num_items(Items.Iron)
            if not dig():
                return False
            if num_items(Items.Iron) > previous:
                dry = 0
            else:
                dry += 1
                if dry >= 56:
                    break
    return num_items(Items.Iron) >= goal


def ur_i_dig_col(tx, ty, tz, size, goal, deadline):
    if not ur_d_move_to(tx, ty, size):
        return False
    found = False
    for _ in range(96):
        if num_items(Items.Iron) >= goal:
            return True
        if get_time() > deadline:
            return False
        if get_ground_type() == Grounds.Iron:
            if not dig():
                return False
            found = True
            continue
        if found:
            break
        if get_pos_z() < tz - 3 or get_hardness() >= 10000000:
            break
        if not dig():
            return False
    return True


def ur_q_stock(goal):
    # 浅表三角定位 + 4 机并行掘邻柱（借坍塌降覆土并同时揭露矿团）。
    deadline = min(6900, get_time() + 1800)
    size = get_world_size()
    anchors = [(0, 0), (1, 0), (0, 1)]
    for cycle in range(128):
        if num_items(Items.Quartz) >= goal:
            return True
        if get_time() > deadline:
            return False
        if num_items(Items.Iron) < 16 and not ur_need(Items.Iron, 48):
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
                continue
            tx, ty, tz = target
            # 最多 4 机并行下挖目标柱及其相邻柱，利用邻柱坍塌并同步开采整团石英。
            cols = [(tx, ty)]
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < size and 0 <= ny < size and len(cols) < max_drones():
                    cols.append((nx, ny))
            handles = []
            ok = True
            for idx in range(1, len(cols)):
                h = spawn_drone(ur_q_dig_col, cols[idx][0], cols[idx][1], tz, size, goal, deadline)
                if h == None:
                    ok = False
                    break
                handles.append(h)
            if ok:
                ok = ur_q_dig_col(cols[0][0], cols[0][1], tz, size, goal, deadline)
            for h in handles:
                if not wait_for(h):
                    ok = False
            if not ok:
                return False
            if num_items(Items.Quartz) >= goal:
                return True
    return num_items(Items.Quartz) >= goal


def ur_q_dig_col(tx, ty, tz, size, goal, deadline):
    if not ur_d_move_to(tx, ty, size):
        return False
    found = False
    for _ in range(192):
        if num_items(Items.Quartz) >= goal:
            return True
        if get_time() > deadline:
            return False
        if get_ground_type() == Grounds.Quartz:
            if not dig():
                return False
            found = True
            continue
        if found:
            break
        if get_pos_z() < tz - 2 or get_hardness() >= 10000000:
            break
        if not dig():
            return False
    return True


def ur_q_prepare(x, y, target, deadline, size):
    if not ur_d_move_to(x, y, size):
        return False
    for _ in range(192):
        if get_pos_z() <= target:
            return True
        if get_time() > deadline or get_hardness() >= 10000000 or not dig():
            return False
    return False


def ur_rice_stock(goal):
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = min(6900, get_time() + 1800)
    for batch in range(128):
        if num_items(Items.Rice) >= goal:
            quick_print("rice_done", True, batch, get_time(), num_items(Items.Rice))
            return
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
        if not local:
            return


def ur_r_rice_columns(first, stride, size, goal, deadline):
    for layer in range(2):
        planted = []
        for x in range(first, size, stride):
            if not ur_d_move_to(x, 0, size):
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
                    if get_water() < 0.6 and num_items(Items.Water) >= 2 * max_drones():
                        use_item(Items.Water)
                    planted.append((x, y))
                if not move(North):
                    return False
        # 轮询收割已成熟格，不用 do_a_flip 整秒空等。
        while planted and get_time() < deadline:
            retry = []
            for x, y in planted:
                if num_items(Items.Rice) >= goal:
                    return True
                if not ur_d_move_to(x, y, size):
                    return False
                if get_entity_type() != Entities.Rice:
                    continue
                if can_harvest():
                    if not harvest():
                        return False
                else:
                    if get_water() < 0.5 and num_items(Items.Water) >= 2 * max_drones():
                        use_item(Items.Water)
                    retry.append((x, y))
            planted = retry
    return True


def ur_mushroom_stock(goal):
    # 连续下探查层（不设 8 连空退出），利用 112 层循环硬度重置。
    deadline = min(6900, get_time() + 1800)
    need_clear = True
    for batch in range(256):
        if num_items(Items.Mushroom) >= goal:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        if get_time() > deadline:
            return
        if need_clear:
            clear()
            need_clear = False
        if not ur_m_move_to(0, 0):
            need_clear = True
            continue
        covers = 0
        while get_ground_type() != Grounds.Mushroom and covers < 112:
            if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                break
            covers += 1
        if get_ground_type() != Grounds.Mushroom:
            need_clear = True
            continue
        top = get_pos_z()
        height = 0
        for sample in range(7):
            if get_ground_type() != Grounds.Mushroom:
                break
            if not dig():
                need_clear = True
                break
            height += 1
        if height < 1 or height > 6:
            need_clear = True
            continue
        if not ur_m_dig_layer(top):
            need_clear = True
            continue
        blocks = ur_m_make_blocks()
        result = ur_m_run_patch(blocks, top, max(1, height - 1), goal)
        if result == None:
            need_clear = True
            continue
        quick_print("mushrooms_batch", batch, top, height, result[0], get_time(), num_items(Items.Mushroom))
        # 挖完当前蘑菇层后直接从该层底部继续下探，免 clear 重来。
        if not ur_m_move_to(0, 0):
            need_clear = True
            continue
        while get_ground_type() == Grounds.Mushroom and get_pos_z() > top - 8:
            if not dig():
                need_clear = True
                break


def ur_dynamite_stock(goal):
    # 连续深探扫雷（利用 GetMineRatio(z) 随深度爬升 + 112 层硬度重置）+ 差集推理 + 零下行风险猜格。
    global ur_d_WORK_LAYOUTS
    ur_d_WORK_LAYOUTS = {}

    def ur_d_make_near(size):
        workers = min(size, max_drones())
        handles = []
        for group in range(1, workers):
            handle = spawn_drone(ur_d_plan_strip, group, workers, size)
            result = None
            if handle == None:
                result = ur_d_plan_strip(group, workers, size)
            handles.append((handle, result))
        near, first = ur_d_plan_strip(0, workers, size)
        layouts = [first]
        for handle, result in handles:
            if handle != None:
                result = wait_for(handle)
            near = near + result[0]
            layouts.append(result[1])
        ur_d_WORK_LAYOUTS[(size, workers)] = layouts
        return near

    def ur_d_plan_strip(group, groups, size):
        near = []
        count = size * size
        for cell in range(group * count // groups, (group + 1) * count // groups):
            near.append(ur_d_neighbors(cell, size))
        return near, ur_d_work_layout(group, groups, size)

    def ur_d_work_layout(group, groups, size):
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
        clue_cells = []
        for y in range(max(0, bottom - 2), min(size, top + 2)):
            for x in range(max(0, left - 2), min(size, right + 2)):
                clue_cells.append(x + y * size)
        return owned, set(owned), clue_cells

    deadline = min(6900, get_time() + 3600)
    size = get_world_size()
    near = ur_d_make_near(size)
    need_clear = True
    for cycle in range(512):
        if num_items(Items.Dynamite) >= goal:
            quick_print("dynamite_done", True, get_time(), num_items(Items.Dynamite))
            return
        if get_time() > deadline:
            return
        if need_clear:
            clear()
            need_clear = False
        if not ur_d_move_to(size // 2, size // 2, size):
            need_clear = True
            continue
        covers = 0
        cover_limit = 224
        if get_pos_z() <= -250:
            cover_limit = 420
        while get_ground_type() != Grounds.Dynamite and covers < cover_limit:
            if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                break
            covers += 1
        if get_ground_type() != Grounds.Dynamite:
            need_clear = True
            continue
        depth = get_pos_z()
        before = num_items(Items.Dynamite)
        status, number = ur_d_open_ground(depth)
        phases = 0
        exploded = False
        if status == "number":
            status, phases, exploded = ur_d_solve(size, depth, near, number)
        if status == "mine":
            exploded = True
            status = ur_d_settle(size, depth)
        gained = num_items(Items.Dynamite) - before
        quick_print("dynamite_cycle", cycle, depth, status, exploded, phases, gained,
                    get_time(), num_items(Items.Dynamite))
        if status != "ended" or exploded or gained < 1000:
            need_clear = True


def ur_d_solve(size, depth, near, number):
    known = []
    for cell in range(size * size):
        known.append(UR_D_UNKNOWN)
    known[(size // 2) * (size + 1)] = number
    groups = min(max_drones(), size)
    rounds = 0
    exploded = False
    for phase in range(UR_D_PHASE_LIMIT):
        results = ur_d_dispatch(0, groups, groups, known, near, size, depth)
        changed = False
        status = "running"
        for state, updates in results:
            if len(updates) > 0:
                changed = True
            # 结算终态优先于并发竞态触发的 error
            if state == "ended":
                status = "ended"
            elif state == "mine" and status != "ended":
                status = "mine"
            elif state == "error" and status == "running":
                status = "error"
            for cell in updates:
                value = updates[cell]
                old = known[cell]
                if old == value or (old >= 0 and value == UR_D_SAFE) or (old == UR_D_DONE and value >= 0):
                    continue
                if old == UR_D_UNKNOWN or (old == UR_D_SAFE and value >= 0) or (old >= 0 and value == UR_D_DONE):
                    known[cell] = value
                else:
                    return "error", rounds, True
        rounds += 1
        if status != "running":
            break
        if not changed:
            # 差集推理无法继续时，挑选风险最低未知格主动破局（零额外下行风险）。
            guess = ur_d_pick_guess(known, near, size)
            if guess < 0:
                break
            if not ur_d_move_to(guess % size, guess // size, size):
                return "error", rounds, True
            g_status, g_num = ur_d_open_ground(depth)
            if g_status == "ended":
                status = "ended"
                break
            if g_status == "mine":
                status = "mine"
                exploded = True
                break
            if g_status != "number":
                return "error", rounds, True
            known[guess] = g_num
            if g_num == 0:
                known[guess] = UR_D_DONE
                for other in near[guess]:
                    if known[other] == UR_D_UNKNOWN:
                        known[other] = UR_D_SAFE
    if status == "running":
        exploded = True
        status = ur_d_settle(size, depth)
    elif status == "mine":
        exploded = True
    return status, rounds, exploded


def ur_d_pick_guess(known, near, size):
    # 估算每个未知格的风险：无相邻线索的内部未知格按基础雷率 0.15；前沿格按最大局部剩余雷比例。
    best = -1
    best_risk = 2.0
    for cell in range(size * size):
        if known[cell] != UR_D_UNKNOWN:
            continue
        risk = 0.0
        has_clue = False
        for nb in near[cell]:
            v = known[nb]
            if v >= 0 and v != UR_D_DONE:
                has_clue = True
                rem = v
                unk = 0
                for c2 in near[nb]:
                    v2 = known[c2]
                    if v2 == UR_D_MINE:
                        rem -= 1
                    elif v2 == UR_D_UNKNOWN:
                        unk += 1
                if unk > 0:
                    r = rem / unk
                    if r > risk:
                        risk = r
        if not has_clue:
            risk = 0.15
        if risk < best_risk:
            best_risk = risk
            best = cell
    return best


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
    owned, owned_set, clue_cells = ur_d_WORK_LAYOUTS[(size, groups)][group]
    clues = set()
    for cell in clue_cells:
        if known[cell] >= 0 and known[cell] != UR_D_DONE:
            clues.add(cell)
    updates = {}
    for step in range(UR_D_PHASE_LIMIT):
        if not ur_d_propagate(known, clues, near, updates):
            return "error", updates
        targets = []
        for cell in owned:
            if known[cell] == UR_D_SAFE:
                targets.append(cell)
        if len(targets) == 0:
            found = ur_d_propagate_diff(known, clues, near, updates)
            if found < 0:
                return "error", updates
            if found > 0:
                continue
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


def ur_d_propagate_diff(known, active, near, updates):
    constraints = {}
    for clue in active:
        remaining = known[clue]
        cells = set()
        for cell in near[clue]:
            v = known[cell]
            if v == UR_D_MINE:
                remaining -= 1
            elif v == UR_D_UNKNOWN:
                cells.add(cell)
        if remaining < 0 or remaining > len(cells):
            return -1
        if len(cells) > 0:
            constraints[clue] = (remaining, cells)
    changed = 0
    clue_list = list(constraints)
    for i in range(len(clue_list)):
        c1 = clue_list[i]
        r1, s1 = constraints[c1]
        for j in range(i + 1, len(clue_list)):
            c2 = clue_list[j]
            r2, s2 = constraints[c2]
            if len(s1) == len(s2):
                continue
            if len(s1) < len(s2):
                small_r, small_s, big_r, big_s = r1, s1, r2, s2
            else:
                small_r, small_s, big_r, big_s = r2, s2, r1, s1
            subset = True
            for x in small_s:
                if x not in big_s:
                    subset = False
                    break
            if not subset:
                continue
            diff = []
            for x in big_s:
                if x not in small_s:
                    diff.append(x)
            dr = big_r - small_r
            if dr < 0 or dr > len(diff):
                return -1
            if dr == 0 or dr == len(diff):
                val = UR_D_SAFE
                if dr == len(diff):
                    val = UR_D_MINE
                for x in diff:
                    if known[x] == UR_D_UNKNOWN:
                        known[x] = val
                        updates[x] = val
                        changed += 1
    return changed


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
            return ur_d_read_ground(depth)
    z = get_pos_z()
    if z > depth:
        return "error", None
    if z == depth:
        if get_ground_type() != Grounds.Dynamite:
            return ur_d_read_ground(depth)
        if not dig():
            return ur_d_read_ground(depth)
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


def starter(cost, i):
    while not affordable(cost) and get_time() < 300:
        if i < 2:
            if can_harvest():
                harvest()
        else:
            y = get_pos_y()
            if y == 0:
                until = get_time() + 1.5
                while get_time() < until and not affordable(cost):
                    if can_harvest():
                        harvest()
            elif not tend(Entities.Bush, False, False):
                return False
            if not affordable(cost):
                move(North)
    return affordable(cost)


def tend(crop, water, infect):
    kind = get_entity_type()
    if kind != None and can_harvest():
        if kind == Entities.Tree and infect:
            if num_items(Items.Fertilizer) > 0:
                use_item(Items.Fertilizer)
            elif num_items(Items.Weird_Substance) > 0:
                use_item(Items.Weird_Substance)
        if not harvest():
            return False
        kind = None
    if kind == None or kind == Entities.Grass:
        if crop == Entities.Carrot:
            cc = get_cost(Entities.Carrot)
            w_cnt = max_drones()
            if num_items(Items.Hay) < cc[Items.Hay] * w_cnt or num_items(Items.Wood) < cc[Items.Wood] * w_cnt:
                crop = Entities.Grass
        if crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        if crop == Entities.Grass:
            if get_ground_type() != Grounds.Grassland:
                till()
        elif not plant(crop):
            if crop != Entities.Carrot:
                return False
            if get_ground_type() == Grounds.Soil:
                till()
    if water and get_water() < 0.45 and num_items(Items.Water) >= max_drones():
        use_item(Items.Water)
    return True


def mixed_stock(cost, stage):
    if affordable(cost):
        return True
    workers = max_drones()
    deadline = min(6800, get_time() + 550)
    handles = []
    for w in range(1, workers):
        job = spawn_drone(mixed_worker, w, workers, cost, stage, deadline)
        if job == None:
            break
        handles.append(job)
    ok = len(handles) == workers - 1 and mixed_worker(0, workers, cost, stage, deadline)
    for job in handles:
        if not wait_for(job):
            ok = False
    return ok and affordable(cost)


def mixed_worker(w, workers, cost, stage, deadline):
    size = get_world_size()
    if workers==1 and size in (4,6) and stage in range(14,22):
        return orchard_lane(cost,stage,deadline)
    if size == 3:
        return nursery(cost, stage, deadline)
    tree = Entities.Tree
    wet = num_unlocked(Unlocks.Watering) > 0
    infect_at = 0
    if num_unlocked(Unlocks.Fertilizer) > 0:
        if stage >= 19 and stage < 27:
            infect_at = 1384
        if size == 8 and workers == 2:
            infect_at = 2064
        if Items.Weird_Substance in cost:
            infect_at = max(infect_at, cost[Items.Weird_Substance])
    start = w * size // workers
    end = (w + 1) * size // workers
    go(start, 0)
    while get_time() < deadline:
        for x in range(start, end):
            for y in range(size):
                if affordable(cost):
                    return True
                crop = Entities.Grass
                if (x + y) % 2 == 1:
                    crop = tree
                elif x % 3 != 0 or (Items.Carrot in cost and num_items(Items.Hay) >= 35):
                    crop = Entities.Carrot
                if not tend(crop, wet and crop != Entities.Grass, num_items(Items.Weird_Substance) < infect_at):
                    return False
                move(North)
            if x + 1 == end:
                go(start, 0)
            else:
                move(East)
    return affordable(cost)


def nursery(cost, stage, deadline):
    # 3×3 环面用九步闭环。(0,0) 专产草，另外八格在同一圈供木和胡萝卜，库存足时让成熟支撑留在田里。
    points = [
        (0, 0, North), (0, 1, North), (0, 2, East),
        (1, 2, North), (1, 0, North), (1, 1, East),
        (2, 1, North), (2, 2, North), (2, 0, East),
    ]
    go(0, 0)
    wood = Entities.Bush
    if num_unlocked(Unlocks.Trees) > 0:
        wood = Entities.Tree
    wet = num_unlocked(Unlocks.Watering) > 0
    carrots = num_unlocked(Unlocks.Carrots) > 0
    while get_time() < deadline:
        for x, y, direction in points:
            if affordable(cost):
                return True
            if x == 0 and y == 0:
                if not tend(Entities.Grass, False, False):
                    return False
                if wet and get_water() < 0.84 and num_items(Items.Water) > 0 and (stage != 11 or num_items(Items.Water) > 3):
                    use_item(Items.Water, min(3, num_items(Items.Water)))  # ty: ignore[invalid-argument-type]  水箱库存按整箱增减。
                span = 0
                if carrots and num_items(Items.Hay) < 20:
                    span = 2
                # 浇水1到树3要兼付大额草、木，两次回访间保留树和胡萝卜。
                if stage >= 7 and stage <= 12:
                    span = 3
                    if Items.Hay in cost:
                        span = 6
                    if stage == 11:
                        span = 1.5
                end = get_time() + span
                while get_time() < end and not affordable(cost):
                    if can_harvest():
                        harvest()
            else:
                crop = wood
                if carrots and wood == Entities.Bush:
                    if x == 1 or (x == 0 and y == 1):
                        crop = Entities.Carrot
                elif carrots:
                    if y == (x + 1) % 3:
                        crop = Entities.Tree
                    elif (x == 0 and y == 2) or (x == 2 and y == 2):
                        crop = Entities.Bush
                    else:
                        crop = Entities.Carrot
                if crop == Entities.Bush and wood == Entities.Tree and get_entity_type() == Entities.Bush:
                    move(direction)
                    continue
                if crop == Entities.Carrot and stage >= 7 and num_items(Items.Carrot) >= 78 and get_entity_type() == crop:
                    move(direction)
                    continue
                if not tend(crop, wet and (stage == 11 or num_items(Items.Water) > 2) and crop == wood, False):
                    return False
            move(direction)
    return affordable(cost)


def basic(cost):
    if affordable(cost):
        return True
    if num_unlocked(Unlocks.Polyculture) > 0:
        return stock_anchors(cost)
    return mixed_stock(cost, 99)


def stock_anchors(cost, companions=True):
    # 原料订单复用现成田；所有工人回收后才允许调用方切换机制。
    if affordable(cost):
        return True
    for item in cost:
        if item not in [Items.Hay, Items.Wood, Items.Carrot, Items.Weird_Substance]:
            quick_print("persistent_failed", "unsupported", item)
            return False
    began = get_time()
    deadline = min(7000, began + 700)
    size = get_world_size()
    workers = 1
    limit = min(size, max_drones())
    while workers * 2 <= limit:
        workers *= 2
    handles = []
    passed = True
    for worker in range(1, workers):
        handle = spawn_drone(stock_worker, worker, workers, cost, deadline, companions)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed and not stock_worker(0, workers, cost, deadline, companions):
        passed = False
    for handle in handles:
        if not wait_for(handle):
            passed = False
    quick_print("persistent_stock", passed, began, get_time(), cost,
                num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot),
                num_items(Items.Weird_Substance))
    return passed and affordable(cost)


def affordable(cost):
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True


def missing(cost, item):
    if item in cost:
        return max(0, cost[item] - num_items(item))
    return 0


def origin():
    size = get_world_size()
    for _ in range((size - get_pos_x()) % size):
        move(East)
    for _ in range((size - get_pos_y()) % size):
        move(North)


def go(x, y):
    size = get_world_size()
    dx = (x - get_pos_x()) % size
    dy = (y - get_pos_y()) % size
    if dx > size // 2:
        for _ in range(size - dx):
            move(West)
    else:
        for _ in range(dx):
            move(East)
    if dy > size // 2:
        for _ in range(size - dy):
            move(South)
    else:
        for _ in range(dy):
            move(North)


def pumpkin_stock(target):
    if num_items(Items.Pumpkin) < target:
        size = get_world_size()
        gain = size * size * min(6, size) * 2 ** (num_unlocked(Unlocks.Pumpkins) - 1)
        fields = (target - num_items(Items.Pumpkin) + gain - 1) // gain
        seeds = (fields * size * size * 3 + 1) // 2
        price = get_cost(Entities.Pumpkin)[Items.Carrot]
        if not basic({Items.Carrot: seeds * price}):
            return False
    if max_drones() > 1:
        return parallel_pumpkin_stock(target)
    size = get_world_size()
    while num_items(Items.Pumpkin) < target:
        if get_time() > 7000:
            return False
        # 预备一田和额外一田重补料，每株仍逐次核价。
        cost = get_cost(Entities.Pumpkin)
        if not basic({Items.Carrot: cost[Items.Carrot] * size * size * 2}):
            return False
        origin()
        if not pumpkin_strip(0, 1, size, -1):
            return False
        before = num_items(Items.Pumpkin)
        harvest()
        quick_print("directed_pumpkin", get_time(), num_items(Items.Pumpkin) - before)
    return True


def pumpkin_strip(worker, workers, size, start_stock):
    # 相邻矩形只归一台机，坏苗复查不横穿其他区。所有区域汇合后仍一次收整田。
    columns = 1
    while columns * columns < workers:
        columns *= 2
    rows = workers // columns
    x0, x1 = (worker % columns) * size // columns, (worker % columns + 1) * size // columns
    y0, y1 = (worker // columns) * size // rows, (worker // columns + 1) * size // rows
    pending = []
    for y in range(y0, y1):
        xs = range(x0, x1)
        if (y - y0) % 2:
            xs = range(x1 - 1, x0 - 1, -1)
        for x in xs:
            pending.append((x, y))
    first = True
    deadline = get_time() + 120
    while pending and get_time() < deadline:
        retry = []
        for x, y in pending:
            if start_stock >= 0 and num_items(Items.Pumpkin) > start_stock:
                return True
            go(x, y)
            crop = get_entity_type()
            if crop != Entities.Pumpkin:
                if crop != None and crop != Entities.Grass and crop != Entities.Dead_Pumpkin:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Pumpkin):
                    return False
                if get_water() < 0.45:
                    if num_items(Items.Water) >= 2 * workers:
                        use_item(Items.Water, 2)
                    elif num_items(Items.Water) >= workers:
                        use_item(Items.Water)
                if not first and len(pending) <= 3 and num_items(Items.Fertilizer) > 1:
                    use_item(Items.Fertilizer)
            if not can_harvest():
                retry.append((x, y))
        pending = retry
        first = False
    return not pending


def parallel_pumpkin_stock(target):
    # 同一块田的连续批次由同一组工人种到交货，主机在田角检查大南瓜是否已经连到对角。
    size = get_world_size()
    workers = min(size, max_drones())
    price = get_cost(Entities.Pumpkin)[Items.Carrot]
    gain = size * size * min(size, 6) * 2 ** (num_unlocked(Unlocks.Pumpkins) - 1)
    fee = size * size * price * 3 // 2

    def harvest_full_pumpkin(before, expected):
        weird = num_items(Items.Weird_Substance)
        if not harvest():
            return False
        return num_items(Items.Pumpkin) - before + num_items(Items.Weird_Substance) - weird == expected

    def pumpkin_batch_worker(w, count):
        for batch in range(count):
            initial = num_items(Items.Pumpkin)
            if not pumpkin_strip(w, workers, size, initial):
                return False
            if batch + 1 == count:
                # 最后一批由主机在所有分区退出后收割，给下一项生产交付空田。
                return True
            deadline = get_time() + 30
            if w == 0:
                go(0, size - 1)
                while get_time() < deadline:
                    key = measure(North)
                    if key != None and measure(West) == key and can_harvest():
                        if not harvest_full_pumpkin(initial, gain):
                            return False
                        break
            while num_items(Items.Pumpkin) == initial and get_time() < deadline:
                pass
            if num_items(Items.Pumpkin) == initial:
                quick_print('pumpkin_timeout', w, get_time())
                return False
        return True

    while num_items(Items.Pumpkin) < target:
        if not basic({Items.Carrot: fee}):
            return False
        count = min((target - num_items(Items.Pumpkin) + gain - 1) // gain, num_items(Items.Carrot) // fee)
        jobs = []
        for w in range(1, workers):
            h = spawn_drone(pumpkin_batch_worker, w, count)
            if h == None:
                break
            jobs.append(h)
        ok = len(jobs) == workers - 1 and pumpkin_batch_worker(0, count)
        for h in jobs:
            if not wait_for(h):
                ok = False
        if not ok:
            return False
        if not harvest_full_pumpkin(num_items(Items.Pumpkin), gain):
            return False
    return True


def solar_reserve():
    size = get_world_size()
    if max_drones() == 1 and size == 6:
        if not orchard_lane({Items.Carrot: size * size}, 21, get_time() + 60):
            return False
    elif not basic({Items.Carrot: size * size}):
        return False
    if max_drones() > 1:
        return parallel_solar_reserve(size)
    origin()
    buckets = {}
    for petals in range(7, 16):
        buckets[petals] = []
    for x in range(size):
        for y in range(size):
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Sunflower):
                return False
            buckets[measure()].append((x, y))  # ty: ignore[invalid-argument-type]  播种成功后的向日葵返回整数瓣数。
            move(North)
        move(East)
    remaining = size * size
    rolls = 0
    for petals in range(15, 6, -1):
        for x, y in buckets[petals]:
            go(x, y)
            while not can_harvest():
                if get_time() > 7000:
                    return False
                if get_water() < 0.5 and num_items(Items.Water) >= max_drones():
                    use_item(Items.Water)
            harvest()
            remaining -= 1
            # 仅用现有种子少量滚动补低瓣；不抬高未收花的最大瓣数。
            if remaining >= 10 and petals > 7 and rolls < size:
                for _ in range(16):
                    if num_items(Items.Carrot) < 1 or not plant(Entities.Sunflower):
                        break
                    next_petals = measure()
                    if next_petals < petals:  # ty: ignore[unsupported-operator]  已种向日葵，measure只返回整数花瓣数。
                        buckets[next_petals].append((x, y))  # ty: ignore[invalid-argument-type]
                        remaining += 1
                        rolls += 1
                        break
                    harvest()
    clear()
    quick_print("directed_solar", get_time(), num_items(Items.Power))
    return True


def solar_plant_strip(worker, workers, size, deadline, width):
    buckets = {}
    for petals in range(7, 16):
        buckets[petals] = []
    first = worker * size // workers
    last = (worker + 1) * size // workers
    for y in range(first, last):
        for x in range(width):
            if get_time() > deadline:
                return None
            go(x, y)
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if x == 0 and y == first and workers >= 4:
                continue
            if not plant(Entities.Sunflower):
                return None
            buckets[measure()].append((x, y))  # ty: ignore[invalid-argument-type]  播种成功后的向日葵返回整数瓣数。
    return buckets


def solar_harvest_rank(points, deadline):
    for x, y in points:
        if get_time() > deadline:
            return False
        go(x, y)
        while not can_harvest():
            if get_time() > deadline:
                return False
            if get_water() < 0.5 and num_items(Items.Water) >= max_drones():
                use_item(Items.Water)
        if not harvest():
            return False
    return True


def parallel_solar_reserve(size, target=0):
    started = get_time()
    deadline = min(7000, started + 180)
    workers = min(size, max_drones())
    handles = []
    passed = True
    batches = []
    width = size
    if target > 0 and workers == size:
        width = min(size, max(2, (target-num_items(Items.Power)+184+8*size-1)//(8*size)+1))
    for worker in range(1, workers):
        handle = spawn_drone(solar_plant_strip, worker, workers, size, deadline, width)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        own = solar_plant_strip(0, workers, size, deadline, width)
        if own == None:
            passed = False
        else:
            batches.append(own)
    for handle in handles:
        result = wait_for(handle)
        if result == None:
            passed = False
        else:
            batches.append(result)
    if not passed or len(batches) != workers:
        quick_print("directed_failed", "solar_plant_workers", get_time())
        return False
    if workers >= 4:
        fee = get_cost(Entities.Carrot)[Items.Wood]
        if num_items(Items.Wood) >= 9*workers*fee and num_items(Items.Hay) >= 9*workers*fee:
            lowest = 7
            if target > 0:
                count = 0
                for rank in range(15, 6, -1):
                    for buckets in batches:
                        count += len(buckets[rank])
                    if num_items(Items.Power) + 8 * count >= target + 75:
                        lowest = rank
                        break
            if not solar_wave(0,workers,batches,num_items(Items.Wood),fee,workers,lowest,deadline):
                return False
            quick_print('solar_wave',get_time()-started,num_items(Items.Power))
            return True
    for petals in range(15, 6, -1):
        # 同花瓣工人全部回收后检查库存，末段够用即停止；target=0收完整田。
        if target > 0 and num_items(Items.Power) >= target:
            break
        handles = []
        passed = True
        for worker in range(1, workers):
            if len(batches[worker][petals]) > 0:
                handle = spawn_drone(solar_harvest_rank, batches[worker][petals], deadline)
                if handle == None:
                    passed = False
                    break
                handles.append(handle)
        if passed:
            passed = solar_harvest_rank(batches[0][petals], deadline)
        for handle in handles:
            if not wait_for(handle):
                passed = False
        if not passed:
            quick_print("directed_failed", "solar_rank_workers", petals, get_time())
            return False
    quick_print("directed_parallel_solar", get_time(), workers, get_time() - started, num_items(Items.Power))
    return True


def ensure_power(target):
    attempts = 0
    while num_items(Items.Power) < target:
        if attempts >= 5 or get_time() > 7000 or not solar_reserve():
            return False
        attempts += 1
    return True


def small_maze_gold(target, n=None):
    # 中期用半幅小迷宫，末段16机用四列布局；工人全回收后才清场。
    WORLD = get_world_size()
    TARGET_GOLD = target
    DRONES = min(max_drones(), 16)
    REUSE_LIMIT = 300
    DIRS = [North, East, South, West]
    BACK = [2, 3, 0, 1]
    MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    if n == None:
        n = WORLD // 4
    if n <= 0:
        quick_print("directed_failed", "maze_size_invalid", get_time(), n)
        return False
    cols = WORLD // n
    if DRONES > cols * cols:
        quick_print("directed_failed", "maze_capacity", get_time(), DRONES, cols)
        return False
    deadline = min(7000, get_time() + 800)
    # 金币/Weird比为宫边长；另付创建、到位登记和并行超收的完整储备。
    required = (max(0, target - num_items(Items.Gold)) + n - 1) // n + 8 * n * MULT * DRONES + 2 * DRONES
    if num_items(Items.Weird_Substance) < required:
        if not basic({Items.Weird_Substance: required}):
            return False
    clear()
    start_stock = num_items(Items.Weird_Substance)
    jobs = []
    for index in range(DRONES):
        jobs.append((n, n // 2 + n * (index % cols), n // 2 + n * (index // cols)))

    if n == 5 and WORLD == 16 and DRONES == 8:
        # 前七个中心留给独立迷宫，第八台在右上角供电，也参加全员到位检查。
        jobs[-1] = (0, 7, 10)

    def go_empty(tx, ty):
        # 仅在迷宫生成前使用农场环绕，分别走较短的横、纵位移。
        dx = (tx - get_pos_x()) % WORLD
        if dx <= WORLD // 2:
            for _ in range(dx):
                move(East)
        else:
            for _ in range(WORLD - dx):
                move(West)
        dy = (ty - get_pos_y()) % WORLD
        if dy <= WORLD // 2:
            for _ in range(dy):
                move(North)
        else:
            for _ in range(WORLD - dy):
                move(South)

    def go_home(cx, cy):
        # 本宫harvest消失后回到中心；路径不穿越邻宫。
        while get_pos_x() < cx:
            move(East)
        while get_pos_x() > cx:
            move(West)
        while get_pos_y() < cy:
            move(North)
        while get_pos_y() > cy:
            move(South)

    def geometry(n):
        # 本地格号p=y*n+x；grid[p][方向]是几何邻居，-1表示本宫边界。
        grid = []
        for y in range(n):
            for x in range(n):
                p = y * n + x
                row = [-1, -1, -1, -1]
                if y < n - 1:
                    row[0] = p + n
                if x < n - 1:
                    row[1] = p + 1
                if y > 0:
                    row[2] = p - n
                if x > 0:
                    row[3] = p - 1
                grid.append(row)
        return grid

    def explore(n, grid, home):
        # links是实测通路，walls是以后可能打开的墙；DFS给出初始树。
        count = n * n
        links = []
        graph = []
        walls = []
        seen = []
        parent = []
        up_hop = []
        down_hop = []
        for _ in range(count):
            links.append([-1, -1, -1, -1])
            graph.append([])
            walls.append([])
            seen.append(False)
            parent.append(-1)
            up_hop.append(None)
            down_hop.append(None)
        order = []
        trail = []
        p = home
        visited = 0
        while True:
            if get_time() > deadline:
                return None
            if not seen[p]:
                if num_items(Items.Gold) >= TARGET_GOLD:
                    return None
                seen[p] = True
                visited += 1
                order.append(p)
                for d in range(4):
                    q = grid[p][d]
                    if q == -1 or links[p][d] != -1:
                        continue
                    if can_move(DIRS[d]):
                        back = BACK[d]
                        links[p][d] = q
                        links[q][back] = p
                        graph[p].append((q, d))
                        graph[q].append((p, back))
                    else:
                        walls[p].append(d)
                if visited == count:
                    break
            choice = -1
            next_p = -1
            for q, d in graph[p]:
                if not seen[q]:
                    choice = d
                    next_p = q
                    break
            if choice != -1:
                move(DIRS[choice])
                parent[next_p] = p
                up_hop[next_p] = (p, DIRS[BACK[choice]])
                down_hop[next_p] = (next_p, DIRS[choice])
                trail.append(BACK[choice])
                p = next_p
            else:
                d = trail.pop()
                move(DIRS[d])
                p = grid[p][d]
        tree = (parent, up_hop, down_hop, order)
        return (p, links, walls, tree)

    def build_all_routes(tree, blank):
        # rows[目标]保存各起点的距离与首步；每个无序点对只计算一次。
        parent, up_hop, down_hop, order = tree
        rows = []
        for goal in range(len(blank)):
            dist = list(blank)
            hop = list(up_hop)
            dist[goal] = 0
            hop[goal] = None
            rows.append([dist, hop])
        visited = []
        for v in order:
            p = parent[v]
            if p != -1:
                dist_v, toward_v = rows[v]
                parent_hop = rows[p][1]
                up = up_hop[v]
                down = down_hop[v]
                for u in visited:
                    dist_u, toward_u = rows[u]
                    distance = dist_u[p] + 1
                    dist_u[v] = distance
                    toward_u[v] = up
                    dist_v[u] = distance
                    if u == p:
                        toward_v[u] = down
                    else:
                        toward_v[u] = parent_hop[u]
            visited.append(v)
        return rows

    def add_route_edge(rows, a, b, hop_ab, hop_ba):
        # 先冻结新边两端的旧距离，再只更新可能经该边缩短的点对。
        da, ha = rows[a]
        db, hb = rows[b]
        left = []
        right = []
        for u in range(len(rows)):
            x = da[u]
            y = db[u]
            if x + 1 < y:
                next_hop = ha[u]
                if u == a:
                    next_hop = hop_ab
                left.append((u, x + 1, next_hop, rows[u]))
            elif y + 1 < x:
                next_hop = hb[u]
                if u == b:
                    next_hop = hop_ba
                right.append((u, y, next_hop, rows[u]))
        if len(left) > len(right):
            left, right = right, left
        for u, x, hop_u, row_u in left:
            dist_u, toward_u = row_u
            for v, y, hop_v, row_v in right:
                candidate = x + y
                if candidate < dist_u[v]:
                    dist_u[v] = candidate
                    toward_u[v] = hop_v
                    dist_v, toward_v = row_v
                    dist_v[u] = candidate
                    toward_v[u] = hop_u

    def scan_departure(p, links, walls, grid, routes):
        # 从上一宝箱位置检查旧墙，发现新边后更新下一次导航。
        remaining = []
        for side in walls[p]:
            if links[p][side] != -1:
                continue
            if can_move(DIRS[side]):
                q = grid[p][side]
                back = BACK[side]
                links[p][side] = q
                links[q][back] = p
                add_route_edge(routes, p, q, (q, DIRS[side]), (p, DIRS[back]))
            else:
                remaining.append(side)
        walls[p] = remaining

    def solve_one(n, bx, by, grid, mapped, blank):
        p, links, walls, tree = mapped
        cost = n * MULT
        routes = build_all_routes(tree, blank)
        relocations = 0
        while num_items(Items.Gold) < TARGET_GOLD:
            if get_time() > deadline:
                return 0
            t = measure()
            goal = (t[1] - by) * n + t[0] - bx  # ty: ignore[not-subscriptable]  本机始终处于独占迷宫，measure返回坐标。
            if p != goal:
                if relocations > 0 and len(walls[p]) > 0:
                    scan_departure(p, links, walls, grid, routes)
                dist, hop = routes[goal]
                for _ in range(dist[p]):
                    p, direction = hop[p]
                    move(direction)
            if num_items(Items.Gold) >= TARGET_GOLD:
                return relocations
            if relocations >= REUSE_LIMIT:
                # 300次成功迁移后只正常收取一次末箱，再重建本宫。
                harvest()
                return relocations + 1
            use_item(Items.Weird_Substance, cost)
            relocations += 1
        return relocations

    def margin_sunflowers():
        # 常驻九株低瓣花，另外十六株按瓣收割。收到最后一株时，田里仍有十株。
        for y in range(10, 13):
            for x in range(7, 10):
                go(x, y)
                if get_ground_type() != Grounds.Soil:
                    till()
                for attempt in range(65):
                    if num_items(Items.Gold) >= TARGET_GOLD or num_items(Items.Carrot) < 1:
                        return
                    if not plant(Entities.Sunflower):
                        return
                    if measure() <= 9:  # ty: ignore[unsupported-operator]  刚种好的向日葵返回整数瓣数。
                        break
                    harvest()
        coords = []
        for y in range(10, 14):
            xs = range(10,14)
            if y % 2:
                xs = range(13,9,-1)
            for x in xs:
                coords.append((x, y))
        began = get_time()
        while num_items(Items.Gold) < TARGET_GOLD and get_time() < deadline:
            buckets = []
            for _ in range(16):
                buckets.append([])
            for x,y in coords:
                if num_items(Items.Gold) >= TARGET_GOLD or num_items(Items.Carrot) < 5:
                    return
                go(x,y)
                if get_ground_type() != Grounds.Soil:
                    till()
                for attempt in range(16):
                    if not plant(Entities.Sunflower):
                        return
                    rank = measure()
                    if rank >= 9:  # ty: ignore[unsupported-operator]  已种向日葵的花瓣数。
                        buckets[rank].append((x, y))  # ty: ignore[invalid-argument-type]
                        break
                    harvest()
                if get_water() < 0.55 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
            for rank in range(15,8,-1):
                for x,y in buckets[rank]:
                    if num_items(Items.Gold) >= TARGET_GOLD:
                        quick_print('margin_power',get_time()-began,num_items(Items.Power))
                        return
                    go(x,y)
                    while not can_harvest() and get_time()<deadline:
                        pass
                    if get_time()>=deadline or not harvest():
                        return

    def worker(job, start_stock):
        n, cx, cy = job
        generations = 0
        boxes = 0
        go_empty(cx, cy)
        grid = geometry(n)
        blank = []
        for _ in range(n * n):
            blank.append(-1)
        half = n // 2
        home = half * n + half
        bx = cx - half
        by = cy - half
        if get_entity_type() == None:
            plant(Entities.Grass)
        # 每台感染再恢复草，合计2*DRONES次消耗构成全部到位的屏障。
        for _ in range(2):
            use_item(Items.Weird_Substance, 1)
        while num_items(Items.Weird_Substance) > start_stock - 2 * DRONES:
            if get_time() > deadline:
                return (n, 0, 0)
            if num_unlocked(Unlocks.Dinosaurs) > 0:
                change_hat(Hats.Straw_Hat)
            else:
                can_harvest()
        if n == 0:
            margin_sunflowers()
            return (0, 0, 0)
        while num_items(Items.Gold) < TARGET_GOLD and get_time() <= deadline:
            go_home(cx, cy)
            if get_entity_type() != None:
                harvest()
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, n * MULT)
            mapped = explore(n, grid, home)
            generations += 1
            if mapped == None:
                # 达标或超时都结束本机，父机最终按实际Gold判断成功。
                break
            boxes += solve_one(n, bx, by, grid, mapped, blank)
        return (n, generations, boxes)

    handles = []
    passed = True
    for job in jobs[1:]:
        handle = spawn_drone(worker, job, start_stock)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        worker(jobs[0], start_stock)
    for handle in handles:
        wait_for(handle)
    clear()
    quick_print("reset_small_maze_gold", get_time(), num_items(Items.Gold))
    return num_items(Items.Gold) >= target


def stock_worker(worker, workers, cost, deadline, companions=True):
    size = get_world_size()
    columns = 1
    while columns * columns < workers:
        columns *= 2
    rows = workers // columns
    x0 = (worker % columns) * size // columns
    x1 = (worker % columns + 1) * size // columns
    y0 = (worker // columns) * size // rows
    y1 = (worker // columns + 1) * size // rows
    bounds = (x0, x1, y0, y1)
    anchors = []
    # 本区树位蛇形排列并往返巡视，避免每轮从末端绕回起点。
    for y in range(y0, y1):
        xs = range(x0, x1)
        if (y // 2) % 2 != 0:
            xs = range(x1 - 1, x0 - 1, -1)
        for x in xs:
            if x % 2 == 0 and y % 2 == 0:
                anchors.append((x, y))
    if len(anchors) == 0:
        return True
    prepared = None
    if companions and workers >= 4 and Items.Weird_Substance not in cost:
        prepared = set()
    index = 0
    step = 1
    for visit in range(20000):
        if affordable(cost):
            return True
        if get_time() > deadline:
            quick_print("persistent_failed", "deadline", worker, cost)
            return False
        x, y = anchors[index]
        go(x, y)
        if not stock_cell(cost, bounds, deadline, companions, prepared):
            return False
        if len(anchors) > 1:
            if index + step < 0 or index + step >= len(anchors):
                step = -step
            index += step
    return affordable(cost)


def stock_crop(cost):
    hay, wood = stock_seed_budget(cost, 4 * max_drones() + 4)
    if num_items(Items.Hay) < hay:
        return Entities.Grass
    if num_items(Items.Wood) < wood:
        return Entities.Tree
    if missing(cost, Items.Carrot) > 0:
        return Entities.Carrot
    return Entities.Tree


def stock_cell(cost, bounds, deadline, companions, prepared):
    point = (get_pos_x(), get_pos_y())
    entity = get_entity_type()
    if entity in [Entities.Grass, Entities.Bush, Entities.Tree, Entities.Carrot]:
        if not can_harvest():
            if get_water() < 0.5 and num_items(Items.Water) >= 2 * max_drones():
                use_item(Items.Water, 2)
            return True
        companion = None
        if companions and (prepared == None or point not in prepared):
            companion = get_companion()
        if companion != None:
            kind, position = companion
            if stock_companion_inside(position, bounds):
                hay, wood = stock_seed_budget(cost, 2 * max_drones() + 2)
                if kind != Entities.Carrot or (prepared == None and num_items(Items.Hay) >= hay and num_items(Items.Wood) >= wood):
                    if not stock_support(kind, position):
                        return False
        if entity == Entities.Tree and missing(cost, Items.Weird_Substance) > 0:
            if num_items(Items.Weird_Substance) > 0:
                if not use_item(Items.Weird_Substance, 1):
                    return False
            elif num_items(Items.Fertilizer) > 0:
                if not use_item(Items.Fertilizer):
                    return False
            else:
                return True
        if not harvest():
            return False
    elif entity != None:
        if not harvest():
            return False
    if affordable(cost):
        return True
    crop = stock_crop(cost)
    if crop == Entities.Grass and get_ground_type() != Grounds.Grassland:
        till()
    elif crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
        till()
    tries = 128
    if prepared != None:
        tries = 10
    for attempt in range(tries):
        if get_time() > deadline:
            return False
        if not affordable(get_cost(crop)):
            # 胡萝卜成本随等级上涨，草见底时本格重抽无意义：结束本格，回外层按缺草/木重选作物。
            return True
        if not plant(crop):
            quick_print("persistent_failed", "plant", crop, get_time())
            return False
        if not companions:
            return True
        companion = get_companion()
        if companion != None and stock_companion_inside(companion[1], bounds):
            if prepared != None:
                if get_water() < 0.6 and num_items(Items.Water) >= 2 * max_drones():
                    use_item(Items.Water, 2)
                prepared.add(point)
                kind, position = companion
                stock_support(kind, position, False)
            return True
        if not harvest():
            return False
    if prepared != None:
        return True
    quick_print("persistent_failed", "companion", get_time())
    return False


def stock_companion_inside(position, bounds):
    # 偶行偶列留给主作物。其余格子可以跨分区种伴生植物。
    x, y = position
    x0, x1, y0, y1 = bounds
    return x % 2 != 0 or y % 2 != 0


def stock_seed_budget(cost, margin):
    # 并发种子留工作余量，支撑播种不能花掉订单要求保留的Hay/Wood。
    seed = get_cost(Entities.Carrot)
    hay = seed[Items.Hay] * margin
    wood = seed[Items.Wood] * margin
    if Items.Hay in cost:
        hay += cost[Items.Hay]
    if Items.Wood in cost:
        wood += cost[Items.Wood]
    return hay, wood


def stock_support(kind, position, return_home=True):
    x, y = get_pos_x(), get_pos_y()
    px, py = position
    go(px, py)
    if get_entity_type() != kind:
        if get_entity_type() != None:
            harvest()
        if kind == Entities.Grass and get_ground_type() != Grounds.Grassland:
            till()
        elif kind == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        if affordable(get_cost(kind)):
            plant(kind)
    if return_home:
        go(x, y)
    return True


def solar_wave(first, count, batches, start_wood, fee, rows, lowest, deadline):
    jobs = []
    while count > 1:
        split = count//2
        h = spawn_drone(solar_wave, first+split, count-split, batches, start_wood, fee, rows, lowest, deadline)
        if h==None:
            return False
        jobs.append(h)
        count=split
    marker_y = first * get_world_size() // rows
    ok=True
    for rank in range(15, lowest-1,-1):
        ready = start_wood - (16-rank)*rows*fee
        for x, y in batches[first][rank]:
            go(x, y)
            while not can_harvest() and get_time() < deadline:
                if get_water() < 0.5:
                    if num_items(Items.Water) >= 2 * rows:
                        use_item(Items.Water, 2)
                    elif num_items(Items.Water) >= rows:
                        use_item(Items.Water)
            if not can_harvest() or not harvest():
                ok=False
                break
        # 最后一株收割后就地种胡萝卜。首波空桶的工人先到自己留下的空位。
        if rank == 15 and len(batches[first][rank]) == 0:
            go(0, marker_y)
        if get_entity_type()!=None and get_entity_type()!=Entities.Grass:
            harvest()
        if get_ground_type()!=Grounds.Soil:
            till()
        if not plant(Entities.Carrot):
            ok=False
        while num_items(Items.Wood)>ready and get_time() < deadline:
            for _ in range(16):
                pass
        if get_time() >= deadline or not ok:
            ok=False
            break
    for h in jobs:
        if not wait_for(h):
            ok=False
    return ok


def orchard_lane(cost, stage, deadline):
    size = get_world_size()
    go(0, 0)
    wet = num_unlocked(Unlocks.Watering) > 0
    fee = get_cost(Entities.Carrot)[Items.Hay]
    while get_time() < deadline:
        for y in range(2):
            xs = range(size)
            step = East
            if y == 1:
                xs = range(size-1,-1,-1)
                step = West
            for x in xs:
                if affordable(cost):
                    return True
                crop = Entities.Carrot
                if x == 0 and y == 0:
                    crop = Entities.Grass
                elif (x+y)%2 == 1:
                    if stage<=17 or x%3 != 1:
                        crop = Entities.Tree
                if not tend(crop, False, stage>=19 and num_items(Items.Weird_Substance)<1384):
                    return False
                if wet and get_water()<0.54 and num_items(Items.Water)>1:
                    use_item(Items.Water, 2)
                if crop == Entities.Grass:
                    end = get_time() + 3
                    while num_items(Items.Hay) < fee*size*2 and get_time()<end:
                        if can_harvest():
                            harvest()
                if y==0 and x==size-1:
                    move(North)
                elif y==1 and x==0:
                    move(South)
                else:
                    move(step)
    return affordable(cost)


def ur_c_ur_d_move_to(tx, ty, size):
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


def ur_c_hour_coal(goal):
    size = get_world_size()
    workers = min(max_drones(), size)
    deadline = get_time() + 1200
    for cycle in range(64):
        if num_items(Items.Coal) >= goal:
            return True
        if get_time() > deadline:
            return False
        clear()
        handles = []
        for worker in range(1, workers):
            handle = spawn_drone(ur_c_hour_coal_worker, worker, workers, goal, deadline)
            if handle != None:
                handles.append(handle)
        ur_c_hour_coal_worker(0, workers, goal, deadline)
        for handle in handles:
            wait_for(handle)
    return num_items(Items.Coal) >= goal


def ur_c_hour_coal_worker(worker, workers, goal, deadline):
    size = get_world_size()
    left = worker * size // workers
    right = (worker + 1) * size // workers
    cursor = 0
    ur_c_ur_d_move_to(left, 0, size)
    for action in range(size * size * 32):
        if num_items(Items.Coal) >= goal:
            return True
        if get_time() > deadline:
            return False
        if get_ground_type() == Grounds.Coal:
            if not dig():
                return False
            continue
        x = get_pos_x()
        y = get_pos_y()
        selected = None
        for direction, nx, ny in [(North, x, y + 1), (East, x + 1, y),
                                  (South, x, y - 1), (West, x - 1, y)]:
            if left <= nx < right and 0 <= ny < size and get_ground_type(direction) == Grounds.Coal:
                selected = direction
                break
        if selected != None:
            move(selected)
            continue
        if get_pos_z() > -16:
            if not dig():
                return False
            continue
        found = False
        while cursor < (right - left) * size:
            tx = left + cursor // size
            ty = cursor % size
            cursor += 1
            ur_c_ur_d_move_to(tx, ty, size)
            if get_pos_z() > -16 or get_ground_type() == Grounds.Coal:
                found = True
                break
        if not found:
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


def ur_bamboo_stock(goal):
    clear()
    size = get_world_size()
    workers = min(4, max_drones())
    rows_per = 1
    if goal >= 10000:
        rows_per = size // workers
        if rows_per < 1:
            rows_per = 1
    deadline = min(6900, get_time() + 900)
    handles = []
    for w in range(1, workers):
        h = spawn_drone(ur_b_worker, w, workers, rows_per, size, goal, deadline)
        if h != None:
            handles.append(h)
    ok = ur_b_worker(0, workers, rows_per, size, goal, deadline)
    for h in handles:
        if not wait_for(h):
            ok = False
    quick_print("bamboo_done", ok, get_time(), num_items(Items.Bamboo), num_items(Items.Rice))


def ur_b_wait(target, deadline):
    while get_time() + 1.0 < target and get_time() < deadline:
        do_a_flip()
    while get_time() < target and get_time() < deadline:
        for _ in range(16):
            pass


def ur_b_water(target):
    lv = get_water()
    if lv < target:
        need = ((target - lv) * 4) // 1
        if need < 1:
            need = 1
        avail = (num_items(Items.Water) // max_drones()) - 1
        if need > avail:
            need = avail
        if need > 0 and use_item(Items.Water, need):
            lv = get_water()
    return lv


def ur_b_worker(w, workers, rows_per, size, goal, deadline):
    rows = []
    for r in range(rows_per):
        ry = w * rows_per + r
        if ry < size:
            rows.append(ry)
    if not rows:
        return True
    flowers = {}
    lowest = 1.0
    max_g1 = 4
    for y in rows:
        ur_d_move_to(0, y, size)
        for x in range(1, size):
            move(East)
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Bamboo):
                return False
            f1 = measure()
            flowers[(x, y)] = f1
            if f1 > max_g1:
                max_g1 = f1
            lv = ur_b_water(0.85)
            if lv < lowest:
                lowest = lv
        move(East)
    began = get_time()
    growth = max_g1
    for cycle in range(128):
        if num_items(Items.Bamboo) >= goal:
            return True
        if get_time() > deadline:
            return False
        # 第 1 次切花
        ur_b_wait(began + growth / (1 + 4 * lowest) + 0.08, deadline)
        max_g2 = 4
        for y in rows:
            hover(18)
            ur_d_move_to(0, y, size)
            for x in range(1, size):
                f1 = flowers[(x, y)]
                hover(f1)
                move(East)
                f2 = measure()
                if f2 != None:
                    flowers[(x, y)] = f2
                    if f2 - f1 > max_g2:
                        max_g2 = f2 - f1
            hover(18)
            move(East)
        began = get_time()
        # 第 2 次切花
        ur_b_wait(began + max_g2 / (1 + 4 * lowest) + 0.08, deadline)
        max_g3 = 4
        for y in rows:
            hover(18)
            ur_d_move_to(0, y, size)
            for x in range(1, size):
                f2 = flowers[(x, y)]
                hover(f2)
                move(East)
                f3 = measure()
                if f3 != None:
                    flowers[(x, y)] = f3
                    if f3 - f2 > max_g3:
                        max_g3 = f3 - f2
            hover(18)
            move(East)
        began = get_time()
        # 第 3 次花熟后 hover(1) 齐根切收保桩，零米耗进入下一轮
        ur_b_wait(began + max_g3 / (1 + 4 * lowest) + 0.08, deadline)
        new_lowest = 1.0
        max_g1 = 4
        for y in rows:
            hover(18)
            ur_d_move_to(0, y, size)
            hover(1)
            for x in range(1, size):
                move(East)
                if num_items(Items.Bamboo) >= goal:
                    return True
                f1 = measure()
                if f1 != None:
                    flowers[(x, y)] = f1
                    if f1 - 1 > max_g1:
                        max_g1 = f1 - 1
                lv = ur_b_water(0.85)
                if lv < new_lowest:
                    new_lowest = lv
            hover(18)
            move(East)
        began = get_time()
        lowest = new_lowest * 0.97
        growth = max_g1
    return num_items(Items.Bamboo) >= goal


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


def ur_m_dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
        if not ur_m_move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() > target:
                return False
            if not move(North):
                return False
    return True


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


def ur_m_run_patch(blocks, ceiling, levels, goal):
    # 每区只派工一次，全部工人结束后才返回或允许换田。
    handles = []
    results = []
    for k in range(1, len(blocks)):
        handle = spawn_drone(ur_m_work_patch, blocks[k], ceiling, levels, goal)
        if handle == None:
            results.append(ur_m_work_patch(blocks[k], ceiling, levels, goal))
        else:
            handles.append(handle)
    results.append(ur_m_work_patch(blocks[0], ceiling, levels, goal))
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


def ur_m_work_patch(block, ceiling, levels, goal):
    # 层末检查真实库存，已开始的配对先兑现；各区自行连续推进。
    pairs = 0
    digs = 0
    for layer in range(levels):
        if num_items(Items.Mushroom) >= goal:
            break
        result = ur_m_work_layer(block, ceiling - layer)
        if result == None:
            return None
        pairs += result[0]
        digs += result[1]
        if result[2] == 0:
            break
    return pairs, digs


def ur_m_work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    cache = {}
    floor = ceiling - 2
    pairs = 0
    digs = 0
    mushrooms = 0
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
            if z < floor:
                continue
            mushroom = get_ground_type() == Grounds.Mushroom
            if mushroom:
                mushrooms += 1
            if z >= ceiling and mushroom:
                count = ur_m_carry_match(cache, x, y, neighbors, floor)
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
            ur_m_read_column(cache, x, y)
            for i in neighbors:
                dx, dy = ur_m_OFFSETS[i]
                ur_m_read_column(cache, x + dx, y + dy, ur_m_DIRECTIONS[i])
    return pairs, digs, mushrooms


def ur_m_push_match(neighbors, floor):
    if get_ground_type() != Grounds.Mushroom:
        return 0
    t = measure()
    z = get_pos_z()
    for i in neighbors:
        direction = ur_m_DIRECTIONS[i]
        if get_ground_type(direction) == Grounds.Mushroom:
            goal = get_pos_z(direction)
            if floor < goal and goal < z and measure(direction) == t:
                if not push(direction):
                    return None
                return 1
    return 0


def ur_m_push_neighbor(i):
    if not move(ur_m_DIRECTIONS[i]):
        return False
    pushed = push(ur_m_BACKS[i])
    if not move(ur_m_BACKS[i]):
        return False
    return pushed


def ur_m_feed_column(neighbors, floor):
    matched = 0
    while True:
        z = get_pos_z()
        if z < floor:
            return matched
        mushroom = get_ground_type() == Grounds.Mushroom
        t = -1
        if mushroom:
            t = measure()
        types = [-1, -1, -1, -1]
        heights = [0, 0, 0, 0]
        hit = -1
        for i in neighbors:
            direction = ur_m_DIRECTIONS[i]
            if get_ground_type(direction) == Grounds.Mushroom:
                types[i] = measure(direction)
                heights[i] = get_pos_z(direction)
                if mushroom and z > floor and types[i] == t and heights[i] > z:
                    hit = i
                    break
        if hit >= 0:
            if not ur_m_push_neighbor(hit):
                return None
            matched += 1
            continue
        goal = z
        if not mushroom:
            goal = floor
        pair_a = -1
        pair_b = -1
        for i in neighbors:
            if types[i] < 0 or types[i] == t or heights[i] < goal + 2:
                continue
            for j in neighbors:
                if j > i and types[j] == types[i] and heights[j] >= goal + 2:
                    pair_a = i
                    pair_b = j
                    break
            if pair_a >= 0:
                break
        if pair_a < 0:
            return matched
        if not mushroom:
            while get_pos_z() > floor:
                if get_ground_type() == Grounds.Mushroom:
                    return matched
                if get_hardness() >= 10000000 or not dig():
                    return None
            if get_pos_z() != floor:
                return None
            if get_ground_type() == Grounds.Mushroom:
                return matched
        if not ur_m_push_neighbor(pair_a):
            return None
        if not ur_m_push_neighbor(pair_b):
            return None
        matched += 1


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


# 缓存仅保存本分区公开柱顶，搬运后更新全部受影响的柱。


def ur_m_read_column(cache, x, y, direction=None):
    if direction == None:
        z = get_pos_z()
        ground = get_ground_type()
        t = -1
        if ground == Grounds.Mushroom:
            t = measure()
    else:
        z = get_pos_z(direction)
        ground = get_ground_type(direction)
        t = -1
        if ground == Grounds.Mushroom:
            t = measure(direction)
    cache[(x, y)] = (z, t)


def ur_m_carry_match(cache, x, y, neighbors, floor):
    # 实测相邻低台搬运同色块；缺建材时保留其他可支付路径。
    direct = ur_m_push_match(neighbors, floor)
    if direct != 0:
        return direct
    ur_m_read_column(cache, x, y)
    z, t = cache[(x, y)]
    if t < 0 or z - 1 <= floor:
        return 0
    for i in neighbors:
        dx, dy = ur_m_OFFSETS[i]
        ur_m_read_column(cache, x + dx, y + dy, ur_m_DIRECTIONS[i])
    for i in neighbors:
        dx, dy = ur_m_OFFSETS[i]
        mx = x + dx
        my = y + dy
        height = cache[(mx, my)][0]
        if height != z - 1 and height != z - 2:
            continue
        for j in range(4):
            ex, ey = ur_m_OFFSETS[j]
            end = (mx + ex, my + ey)
            if end not in cache:
                continue
            goal, color = cache[end]
            if goal != z - 1 or color != t:
                continue
            if height == z - 2:
                if num_items(Items.Block) < 1:
                    continue
                if not move(ur_m_DIRECTIONS[i]) or get_pos_z() != height:
                    return None
                if not place(Grounds.Dirt) or get_pos_z() != z - 1:
                    return None
                if not move(ur_m_BACKS[i]):
                    return None
            if not push(ur_m_DIRECTIONS[i]):
                return None
            ur_m_read_column(cache, x, y)
            if not move(ur_m_DIRECTIONS[i]) or not push(ur_m_DIRECTIONS[j]):
                return None
            ur_m_read_column(cache, mx, my)
            ur_m_read_column(cache, end[0], end[1], ur_m_DIRECTIONS[j])
            if not move(ur_m_BACKS[i]):
                return None
            return 1
    return ur_m_fixture_match(neighbors, floor)


def ur_m_fixture_match(neighbors, floor):
    # 相邻同高同色A/B借低两格的C完成B→C、A→B、B→C。
    if get_ground_type() != Grounds.Mushroom:
        return 0
    z = get_pos_z()
    if z - 2 < floor:
        return 0
    t = measure()
    for i in neighbors:
        source = ur_m_DIRECTIONS[i]
        if get_pos_z(source) != z or get_ground_type(source) != Grounds.Mushroom or measure(source) != t:
            continue
        for j in neighbors:
            if i == j or get_pos_z(ur_m_DIRECTIONS[j]) != z - 2:
                continue
            if not push(ur_m_DIRECTIONS[j]):
                return None
            if not move(source) or not push(ur_m_BACKS[i]):
                return None
            if not move(ur_m_BACKS[i]) or not push(ur_m_DIRECTIONS[j]):
                return None
            return 1
    return 0


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


if __name__ == "__main__":
    lb_fastest_underground_reset()
