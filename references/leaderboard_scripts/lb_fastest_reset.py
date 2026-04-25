from __builtins__ import *


def main():
    quick_print("reset_stage", "start", "time=", get_time())
    step1()
    quick_print("reset_stage", "step1", "time=", get_time(), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood), "carrot=", num_items(Items.Carrot))
    step2()
    quick_print("reset_stage", "step2", "time=", get_time(), "power=", num_items(Items.Power), "size=", get_world_size())
    step3()
    quick_print("reset_stage", "step3", "time=", get_time(), "weird=", num_items(Items.Weird_Substance), "gold=", num_items(Items.Gold))
    step4()
    quick_print("reset_stage", "step4", "time=", get_time(), "size=", get_world_size(), "cactus=", num_items(Items.Cactus))
    step5()
    quick_print("reset_stage", "done", "time=", get_time(), "bone=", num_items(Items.Bone), "gold=", num_items(Items.Gold))


# 最开始的状态，点一些前期的东西直至解锁胡萝卜
def step1():
    # 速度1 20草
    while num_items(Items.Hay) < 20:
        harvest()
    unlock(Unlocks.Speed)

    # 扩张1 30草 1x1->1*3
    while num_items(Items.Hay) < 30:
        while not can_harvest():
            pass
        harvest()
    unlock(Unlocks.Expand)

    # 种植 50草
    while num_items(Items.Hay) < 50:
        while not can_harvest():
            pass
        harvest()
    unlock(Unlocks.Plant)

    # 扩张2 20木 1x3->3*3
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    while num_items(Items.Wood) < 20:
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
    unlock(Unlocks.Expand)

    # 胡萝卜 50木
    while num_items(Items.Wood) < 50:
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(East)
    unlock(Unlocks.Carrots)


# 草、灌木、（树）、胡萝卜、（向日葵） 混种，速度升满，直至有1000能量
def step2():
    can_plant_tree = False
    can_use_water = False
    can_use_fertilizer = False
    can_plant_sunflower = False
    while num_items(Items.Power) < 1000:
        for _ in range(get_world_size()):
            if get_ground_type() == Grounds.Grassland:
                till()
            if can_use_water:
                water_needed = (min(0.75, num_items(Items.Water) / 100) - get_water()) // 0.25
                if water_needed > 0:
                    use_item(Items.Water, water_needed)
            if not can_harvest() and get_entity_type() != None:
                if can_use_fertilizer and get_entity_type() == Entities.Tree:
                    while not can_harvest():
                        if not use_item(Items.Fertilizer):
                            break
                    if not can_harvest():
                        move(North)
                        continue
                else:
                    move(North)
                    continue
            harvest()
            if can_plant_sunflower:
                if num_unlocked(Unlocks.Speed) < 5:
                    if num_items(Items.Power) < 100 and plant(Entities.Sunflower):
                        move(North)
                        continue
                else:
                    if can_plant_sunflower and plant(Entities.Sunflower):
                        move(North)
                        continue
            rand = random()
            if can_plant_tree:
                if rand < 0.25 and plant(Entities.Grass):
                    move(North)
                    continue
                if rand < 0.5 and plant(Entities.Bush):
                    move(North)
                    continue
                if rand < 0.75 and plant(Entities.Tree) and ((get_pos_x() + get_pos_y()) % 2 == 0):
                    move(North)
                    continue
                if plant(Entities.Carrot):
                    move(North)
                    continue
            else:
                if rand < 0.33 and plant(Entities.Grass):
                    move(North)
                    continue
                if rand < 0.66 and plant(Entities.Bush):
                    move(North)
                    continue
                if plant(Entities.Carrot):
                    move(North)
                    continue
            # 种最缺的
            hay = num_items(Items.Hay)
            wood = num_items(Items.Wood)
            carrot = num_items(Items.Carrot)
            if hay < wood and hay < carrot:
                if plant(Entities.Grass):
                    move(North)
                    continue
            elif wood < hay and wood < carrot:
                if can_plant_tree and ((get_pos_x() + get_pos_y()) % 2 == 0):
                    if plant(Entities.Tree):
                        move(North)
                        continue
                else:
                    if plant(Entities.Bush):
                        move(North)
                        continue
            else:
                if plant(Entities.Carrot):
                    move(North)
                    continue
            plant(Entities.Grass)
            move(North)
        move(East)
        unlock(Unlocks.Grass)
        unlock(Unlocks.Speed)
        unlock(Unlocks.Expand)
        unlock(Unlocks.Carrots)
        if unlock(Unlocks.Trees):
            can_plant_tree = True
        if unlock(Unlocks.Watering):
            can_use_water = True
        if unlock(Unlocks.Fertilizer):
            can_use_fertilizer = True
        if unlock(Unlocks.Sunflowers):
            can_plant_sunflower = True


# 无人机数目升级刷到最大（5级）
def step3():
    # 刷奇异物质到1200，解锁迷宫
    while num_items(Items.Weird_Substance) < 2000:
        for _ in range(get_world_size()):
            if (get_pos_x() + get_pos_y()) % 2 == 0:
                # 种树并用一次奇异物质
                if can_harvest():
                    harvest()
                    plant(Entities.Tree)
                    use_item(Items.Fertilizer)
                elif get_entity_type() == None:
                    plant(Entities.Tree)
                    use_item(Items.Fertilizer)
                move(North)
            else:
                # 种最缺的
                if not can_harvest():
                    plant(Entities.Grass)
                    move(North)
                    continue
                harvest()
                hay = num_items(Items.Hay)
                wood = num_items(Items.Wood)
                carrot = num_items(Items.Carrot)
                if hay < wood and hay < carrot:
                    plant(Entities.Grass)
                elif wood < hay and wood < carrot:
                    plant(Entities.Bush)
                else:
                    plant(Entities.Carrot)
        move(East)
        unlock(Unlocks.Grass)
        unlock(Unlocks.Trees)
        unlock(Unlocks.Carrots)
        unlock(Unlocks.Watering)
        unlock(Unlocks.Fertilizer)
    unlock(Unlocks.Mazes)
    # 刷奇异物质-刷金币-解锁更多无人机（能量不够要刷能量）
    # 下面这个不对，会因为没有奇异物质而死循环
    # idx = 0
    # directions = [North, East, South, West]
    # while num_items(Items.Gold) < 2000:
    #     if get_entity_type() == Entities.Treasure:
    #         harvest()
    #     elif get_entity_type() == Entities.Hedge:
    #         idx = (idx - 1) % 4
    #         while not can_move(directions[idx]):
    #             idx = (idx + 1) % 4
    #         move(directions[idx])
    #     else:
    #         harvest()
    #         plant(Entities.Bush)
    #         use_item(Items.Weird_Substance, get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1))
    # unlock(Unlocks.Megafarm)


# 扩张升到最大（9级）
def step4():
    farm_basic_for_cost(get_cost(Unlocks.Pumpkins))
    unlock(Unlocks.Pumpkins)

    # Expand 7 需要 64k 南瓜，短窗口验证显示会吞掉 reset 节奏。
    # 先在 Expand 6 切到恐龙/金币阶段，避免为了更大棋盘过度刷南瓜。
    while num_unlocked(Unlocks.Expand) < 6:
        cost = get_cost(Unlocks.Expand)
        if cost == None or cost == {}:
            break
        farm_for_cost(cost)
        if not unlock(Unlocks.Expand):
            break
        quick_print("reset_stage", "expand", num_unlocked(Unlocks.Expand), "time=", get_time(), "pumpkin=", num_items(Items.Pumpkin))

    farm_pumpkins_until(5000)
    unlock(Unlocks.Cactus)
    farm_cactus_until(2000)
    unlock(Unlocks.Dinosaurs)


# 解锁排行榜
def step5():
    upgrade_mazes_for_gold()
    farm_gold_until(2000)
    unlock(Unlocks.Megafarm)
    quick_print("reset_stage", "megafarm", num_unlocked(Unlocks.Megafarm), "time=", get_time(), "gold=", num_items(Items.Gold))

    farm_gold_until(1000000)
    upgrade_dinosaurs_for_bones()
    farm_bones_until(2000000)
    unlock(Unlocks.Leaderboard)


def cost_amount(cost, item):
    if cost == None:
        return 0
    if item in cost:
        return cost[item]
    return 0


def farm_for_cost(cost):
    farm_basic_for_cost(cost)
    weird_need = cost_amount(cost, Items.Weird_Substance)
    if weird_need > 0:
        farm_weird_substance_until(weird_need)
    pumpkin_need = cost_amount(cost, Items.Pumpkin)
    if pumpkin_need > 0:
        farm_pumpkins_until(pumpkin_need)
    cactus_need = cost_amount(cost, Items.Cactus)
    if cactus_need > 0:
        farm_cactus_until(cactus_need)
    gold_need = cost_amount(cost, Items.Gold)
    if gold_need > 0:
        farm_gold_until(gold_need)
    bone_need = cost_amount(cost, Items.Bone)
    if bone_need > 0:
        farm_bones_until(bone_need)


def farm_scaled_cost_for_current_inventory(cost, multiplier):
    if cost == None:
        return
    hay_need = cost_amount(cost, Items.Hay) * multiplier
    if num_items(Items.Hay) < hay_need:
        farm_hay_until(hay_need)
    wood_need = cost_amount(cost, Items.Wood) * multiplier
    if num_items(Items.Wood) < wood_need:
        farm_wood_until(wood_need)
    carrot_need = cost_amount(cost, Items.Carrot) * multiplier
    if num_items(Items.Carrot) < carrot_need:
        farm_carrots_until(carrot_need)
    pumpkin_need = cost_amount(cost, Items.Pumpkin) * multiplier
    if num_items(Items.Pumpkin) < pumpkin_need:
        farm_pumpkins_until(pumpkin_need)
    cactus_need = cost_amount(cost, Items.Cactus) * multiplier
    if num_items(Items.Cactus) < cactus_need:
        farm_cactus_until(cactus_need)
    gold_need = cost_amount(cost, Items.Gold) * multiplier
    if num_items(Items.Gold) < gold_need:
        farm_gold_until(gold_need)


def farm_basic_for_cost(cost):
    if cost == None:
        return
    farm_hay_until(cost_amount(cost, Items.Hay))
    farm_wood_until(cost_amount(cost, Items.Wood))
    farm_carrots_until(cost_amount(cost, Items.Carrot))


def upgrade_mazes_for_gold():
    while num_unlocked(Unlocks.Mazes) < 2:
        cost = get_cost(Unlocks.Mazes)
        if cost == None or cost == {}:
            return
        if cost_amount(cost, Items.Gold) > 0 or cost_amount(cost, Items.Bone) > 0:
            return
        farm_for_cost(cost)
        if not unlock(Unlocks.Mazes):
            return
        quick_print("reset_stage", "mazes", num_unlocked(Unlocks.Mazes), "time=", get_time(), "weird=", num_items(Items.Weird_Substance))


def upgrade_dinosaurs_for_bones():
    while num_unlocked(Unlocks.Dinosaurs) < 3:
        cost = get_cost(Unlocks.Dinosaurs)
        if cost == None or cost == {}:
            return
        if cost_amount(cost, Items.Gold) > 0 or cost_amount(cost, Items.Bone) > 0:
            return
        farm_for_cost(cost)
        if not unlock(Unlocks.Dinosaurs):
            return
        quick_print("reset_stage", "dinosaurs", num_unlocked(Unlocks.Dinosaurs), "time=", get_time(), "cactus=", num_items(Items.Cactus))


def farm_hay_until(target):
    while num_items(Items.Hay) < target:
        if can_harvest():
            harvest()
        if get_entity_type() == None:
            plant(Entities.Grass)
        move(North)


def farm_wood_until(target):
    while num_items(Items.Wood) < target:
        if can_harvest():
            harvest()
        if get_entity_type() == None:
            plant(Entities.Bush)
        move(North)


def farm_carrots_until(target):
    while num_items(Items.Carrot) < target:
        size = get_world_size()
        farm_hay_until(num_items(Items.Hay) + size * size)
        farm_wood_until(num_items(Items.Wood) + size * size)
        for _ in range(size):
            for _ in range(size):
                if can_harvest():
                    harvest()
                if get_entity_type() == None:
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    plant(Entities.Carrot)
                move(North)
            move(East)


def farm_pumpkins_until(target):
    while num_items(Items.Pumpkin) < target:
        plant_pumpkin_field()
        wait_pumpkin_field()
        harvest_field()
        quick_print("reset_stage", "pumpkins", "time=", get_time(), "pumpkin=", num_items(Items.Pumpkin), "target=", target, "size=", get_world_size())


def plant_pumpkin_field():
    size = get_world_size()
    farm_carrots_until(size * size * 3)
    for _ in range(size):
        for _ in range(size):
            entity = get_entity_type()
            if entity != Entities.Pumpkin:
                if entity != None:
                    harvest()
                if get_ground_type() == Grounds.Grassland:
                    till()
                plant(Entities.Pumpkin)
            move(North)
        move(East)


def wait_pumpkin_field():
    size = get_world_size()
    while True:
        ready = 0
        for _ in range(size):
            for _ in range(size):
                entity = get_entity_type()
                if entity == Entities.Dead_Pumpkin:
                    harvest()
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    if num_items(Items.Carrot) > 0:
                        plant(Entities.Pumpkin)
                elif entity == None:
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    if num_items(Items.Carrot) > 0:
                        plant(Entities.Pumpkin)
                elif can_harvest():
                    ready = ready + 1
                move(North)
            move(East)
        if ready >= size * size:
            return


def harvest_field():
    size = get_world_size()
    for _ in range(size):
        for _ in range(size):
            if can_harvest():
                harvest()
            move(North)
        move(East)


def farm_cactus_until(target):
    while num_items(Items.Cactus) < target:
        size = get_world_size()
        if size >= 8 and target - num_items(Items.Cactus) > size * size * 4:
            farm_sorted_cactus_field()
            continue
        if num_items(Items.Pumpkin) < size * size * 2:
            farm_pumpkins_until(size * size * 2)
        for _ in range(size):
            for _ in range(size):
                if can_harvest():
                    harvest()
                if get_entity_type() == None:
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    plant(Entities.Cactus)
                move(North)
            move(East)
        quick_print("reset_stage", "cactus", "time=", get_time(), "cactus=", num_items(Items.Cactus), "target=", target)


def farm_sorted_cactus_field():
    size = get_world_size()
    if num_items(Items.Pumpkin) < size * size * 2:
        farm_pumpkins_until(size * size * 2)
    for _ in range(size):
        for _ in range(size):
            if get_entity_type() != None:
                harvest()
            if get_ground_type() == Grounds.Grassland:
                till()
            plant(Entities.Cactus)
            move(North)
        move(East)
    wait_cactus_field()
    for x in range(size):
        goto_wrap(x, 0)
        sort_cactus_line(North, South)
    for y in range(size):
        goto_wrap(0, y)
        sort_cactus_line(East, West)
    goto_wrap(0, 0)
    harvest()
    quick_print("reset_stage", "cactus_sorted", "time=", get_time(), "cactus=", num_items(Items.Cactus), "size=", size)


def wait_cactus_field():
    size = get_world_size()
    while True:
        ready = 0
        for _ in range(size):
            for _ in range(size):
                if can_harvest():
                    ready = ready + 1
                move(North)
            move(East)
        if ready >= size * size:
            return


def sort_cactus_line(forward, backward):
    size = get_world_size()
    bound_low = 0
    bound_high = size - 1
    while True:
        swap_pos_last = -1
        move_cactus_line_to(forward, backward, bound_low)
        i = bound_low
        while i < bound_high - 1:
            move(forward)
            i = i + 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if a > b:
                swap(backward)
                swap_pos_last = max(swap_pos_last, i)
                a, b = b, a
            if b > c:
                swap(forward)
                swap_pos_last = max(swap_pos_last, i + 1)
                b, c = c, b
                if a > b:
                    swap(backward)
        if swap_pos_last == -1:
            break
        bound_high = swap_pos_last - 2
        if bound_low >= bound_high:
            break
        swap_pos_first = size
        move_cactus_line_to(forward, backward, bound_high)
        i = bound_high
        while i > bound_low + 1:
            move(backward)
            i = i - 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if b > c:
                swap(forward)
                swap_pos_first = min(swap_pos_first, i)
                b, c = c, b
            if a > b:
                swap(backward)
                swap_pos_first = min(swap_pos_first, i - 1)
                a, b = b, a
                if b > c:
                    swap(forward)
        if swap_pos_first == size:
            break
        bound_low = swap_pos_first + 2
        if bound_low >= bound_high:
            break
    if bound_low + 1 == bound_high:
        move_cactus_line_to(forward, backward, bound_low)
        if measure() > measure(forward):
            swap(forward)


def move_cactus_line_to(forward, backward, target):
    size = get_world_size()
    if forward == North:
        current = get_pos_y()
    else:
        current = get_pos_x()
    delta = (target - current) % size
    if delta <= size // 2:
        for _ in range(delta):
            move(forward)
    else:
        for _ in range(size - delta):
            move(backward)


def farm_weird_substance_until(target):
    if num_items(Items.Weird_Substance) < target:
        size = get_world_size()
        if num_items(Items.Wood) < size * size:
            farm_wood_until(size * size)
        clear()
    while num_items(Items.Weird_Substance) < target:
        size = get_world_size()
        for x in range(size):
            for y in range(size):
                if (x + y) % 2 == 0:
                    if can_harvest():
                        harvest()
                    plant(Entities.Tree)
                    if get_entity_type() == Entities.Tree and num_items(Items.Fertilizer) > 0:
                        use_item(Items.Fertilizer)
                elif can_harvest():
                    harvest()
                move(North)
            move(East)
        quick_print("reset_stage", "weird", "time=", get_time(), "weird=", num_items(Items.Weird_Substance), "target=", target, "wood=", num_items(Items.Wood), "fert=", num_items(Items.Fertilizer))


def farm_gold_until(target):
    while num_items(Items.Gold) < target:
        farm_gold_single_cycle(target)
        quick_print("reset_stage", "gold", "time=", get_time(), "gold=", num_items(Items.Gold), "target=", target, "weird=", num_items(Items.Weird_Substance))


def farm_gold_single_cycle(target):
    maze_size = get_world_size()
    set_world_size(maze_size)
    substance = maze_size * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
    gold_needed = target - num_items(Items.Gold)
    total_paid_move_count = (gold_needed + maze_size * maze_size - 1) // (maze_size * maze_size)
    if total_paid_move_count < 0:
        total_paid_move_count = 0
    batch_paid_move_count = total_paid_move_count
    if batch_paid_move_count > 600:
        batch_paid_move_count = 600
    cycle_count = (batch_paid_move_count + 299) // 300
    if cycle_count < 1:
        cycle_count = 1
    farm_weird_substance_until(substance * (batch_paid_move_count + cycle_count))
    remaining_paid_move_count = batch_paid_move_count
    while remaining_paid_move_count >= 0 and num_items(Items.Gold) < target:
        paid_move_count = remaining_paid_move_count
        if paid_move_count > 300:
            paid_move_count = 300
        clear()
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, substance)
        maze_graph = build_maze_graph(maze_size)
        for _ in range(paid_move_count):
            if num_items(Items.Gold) >= target:
                return
            if not use_treasure_once(substance, maze_graph):
                return
        remaining_paid_move_count = remaining_paid_move_count - paid_move_count
        if remaining_paid_move_count <= 0:
            return
        if paid_move_count < 300:
            return


def farm_gold_multi_until(target):
    if num_drones() < 4:
        farm_gold_single_cycle(target)
        return
    if num_drones() >= 16:
        maze_size = 4
    else:
        maze_size = 2
    set_world_size(maze_size)
    substance = maze_size * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
    farm_weird_substance_until(num_items(Items.Weird_Substance) + substance * 12000)
    clear()
    worker_count = 1
    for x in range(maze_size):
        for y in range(maze_size):
            if x != 0 or y != 0:
                if worker_count < num_drones():
                    spawn_drone(gold_worker_at, x, y, target, substance)
                    worker_count = worker_count + 1
    gold_worker_at(0, 0, target, substance)


def gold_worker_at(x, y, target, substance):
    for _ in range(x):
        move(East)
    for _ in range(y):
        move(North)
    while num_items(Items.Gold) < target:
        if get_entity_type() != Entities.Treasure:
            plant(Entities.Bush)
        use_item(Items.Weird_Substance, substance)
        for _ in range(25):
            if num_items(Items.Gold) >= target:
                return
            use_item(Items.Weird_Substance, substance)
            if get_entity_type() == Entities.Treasure:
                harvest()


def use_treasure_once(substance, maze_graph=None):
    size = get_world_size()
    pos = measure()
    if pos != None:
        if maze_graph != None and goto_treasure_with_graph(pos[0], pos[1], size, maze_graph):
            return use_item(Items.Weird_Substance, substance)
        if maze_graph == None and goto_treasure_in_maze(pos[0], pos[1], size):
            return use_item(Items.Weird_Substance, substance)
    for _ in range(size):
        for _ in range(size):
            if get_entity_type() == Entities.Treasure:
                return use_item(Items.Weird_Substance, substance)
            move(North)
        move(East)
    return False


def build_maze_graph(size):
    directions = [North, East, South, West]
    backs = [South, West, North, East]
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]
    graph = []
    for _ in range(size * size):
        graph.append([])
    visited = []
    backtrack = []
    while True:
        current = get_pos_x() + get_pos_y() * size
        if current not in visited:
            visited.append(current)
        moved = False
        for idx in range(4):
            nx = get_pos_x() + dx[idx]
            ny = get_pos_y() + dy[idx]
            if nx < 0 or ny < 0 or nx >= size or ny >= size:
                continue
            neighbor = nx + ny * size
            if can_move(directions[idx]):
                add_maze_edge(graph, current, neighbor, directions[idx])
                add_maze_edge(graph, neighbor, current, backs[idx])
                if neighbor not in visited:
                    move(directions[idx])
                    backtrack.append(backs[idx])
                    moved = True
                    break
        if moved:
            continue
        if len(backtrack) <= 0:
            return graph
        move(backtrack.pop())


def add_maze_edge(graph, source, target, direction):
    for edge in graph[source]:
        if edge[0] == target:
            return
    graph[source].append([target, direction])


def goto_treasure_with_graph(tx, ty, size, graph):
    target = tx + ty * size
    while get_pos_x() + get_pos_y() * size != target:
        refresh_maze_edges(graph, size)
        if move_direct_toward_treasure(tx, ty, size, graph):
            continue
        if not move_with_graph_path(target, size, graph):
            return False
    return True


def refresh_maze_edges(graph, size):
    directions = [North, East, South, West]
    backs = [South, West, North, East]
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]
    current = get_pos_x() + get_pos_y() * size
    for idx in range(4):
        nx = get_pos_x() + dx[idx]
        ny = get_pos_y() + dy[idx]
        if nx < 0 or ny < 0 or nx >= size or ny >= size:
            continue
        if can_move(directions[idx]):
            neighbor = nx + ny * size
            add_maze_edge(graph, current, neighbor, directions[idx])
            add_maze_edge(graph, neighbor, current, backs[idx])


def move_direct_toward_treasure(tx, ty, size, graph):
    current = get_pos_x() + get_pos_y() * size
    if tx > get_pos_x() and can_move(East):
        neighbor = get_pos_x() + 1 + get_pos_y() * size
        add_maze_edge(graph, current, neighbor, East)
        add_maze_edge(graph, neighbor, current, West)
        move(East)
        return True
    if tx < get_pos_x() and can_move(West):
        neighbor = get_pos_x() - 1 + get_pos_y() * size
        add_maze_edge(graph, current, neighbor, West)
        add_maze_edge(graph, neighbor, current, East)
        move(West)
        return True
    if ty > get_pos_y() and can_move(North):
        neighbor = get_pos_x() + (get_pos_y() + 1) * size
        add_maze_edge(graph, current, neighbor, North)
        add_maze_edge(graph, neighbor, current, South)
        move(North)
        return True
    if ty < get_pos_y() and can_move(South):
        neighbor = get_pos_x() + (get_pos_y() - 1) * size
        add_maze_edge(graph, current, neighbor, South)
        add_maze_edge(graph, neighbor, current, North)
        move(South)
        return True
    return False


def move_with_graph_path(target, size, graph):
    start = get_pos_x() + get_pos_y() * size
    previous = []
    previous_direction = []
    for _ in range(size * size):
        previous.append(-1)
        previous_direction.append(None)
    queue = [start]
    previous[start] = start
    head = 0
    while head < len(queue):
        current = queue[head]
        head = head + 1
        for edge in graph[current]:
            neighbor = edge[0]
            if previous[neighbor] != -1:
                continue
            previous[neighbor] = current
            previous_direction[neighbor] = edge[1]
            if neighbor == target:
                head = len(queue)
                break
            queue.append(neighbor)
    if previous[target] == -1:
        return False
    path = []
    current = target
    while current != start:
        path.append(previous_direction[current])
        current = previous[current]
    while len(path) > 0:
        move(path.pop())
    return True


def goto_treasure_in_maze(tx, ty, size):
    directions = [North, East, South, West]
    backs = [South, West, North, East]
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]
    visited = []
    backtrack = []
    while True:
        if get_pos_x() == tx and get_pos_y() == ty:
            return True
        current = get_pos_x() + get_pos_y() * size
        if current not in visited:
            visited.append(current)
        moved = False
        for idx in range(4):
            nx = get_pos_x() + dx[idx]
            ny = get_pos_y() + dy[idx]
            if nx < 0 or ny < 0 or nx >= size or ny >= size:
                continue
            encoded = nx + ny * size
            if encoded not in visited and can_move(directions[idx]):
                move(directions[idx])
                backtrack.append(backs[idx])
                moved = True
                break
        if moved:
            continue
        if len(backtrack) <= 0:
            return False
        move(backtrack.pop())


def harvest_treasure_once(maze_graph=None):
    size = get_world_size()
    pos = measure()
    if pos != None:
        if maze_graph != None and goto_treasure_with_graph(pos[0], pos[1], size, maze_graph) and get_entity_type() == Entities.Treasure:
            harvest()
            return
        if maze_graph == None and goto_treasure_in_maze(pos[0], pos[1], size) and get_entity_type() == Entities.Treasure:
            harvest()
            return
    for _ in range(size):
        for _ in range(size):
            if get_entity_type() == Entities.Treasure:
                harvest()
                return
            move(North)
        move(East)


def farm_bones_until(target):
    set_world_size(get_world_size())
    while num_items(Items.Bone) < target:
        goto_wrap(0, 0)
        farm_dinosaur_apple_cost()
        change_hat(Hats.Dinosaur_Hat)
        run_dinosaur_loop(get_world_size(), get_world_size() * get_world_size() - 2)
        change_hat(Hats.Straw_Hat)
        quick_print("reset_stage", "bones", "time=", get_time(), "bone=", num_items(Items.Bone), "target=", target)


def farm_dinosaur_apple_cost():
    level = num_unlocked(Unlocks.Dinosaurs)
    if level < 1:
        level = 1
    multiplier = 2 ** (level - 1)
    farm_scaled_cost_for_current_inventory(get_cost(Entities.Apple), multiplier)


def goto_wrap(tx, ty):
    size = get_world_size()
    half = size // 2
    dx = (tx - get_pos_x()) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - get_pos_y()) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def run_dinosaur_loop(size, target_tail):
    eaten = 0
    while eaten < target_tail:
        eaten = eaten + dinosaur_move(East, size - 1, target_tail, eaten)
        for y in range(1, size):
            eaten = eaten + dinosaur_move(North, 1, target_tail, eaten)
            if y % 2 == 1:
                eaten = eaten + dinosaur_move(West, size - 2, target_tail, eaten)
            else:
                eaten = eaten + dinosaur_move(East, size - 2, target_tail, eaten)
        eaten = eaten + dinosaur_move(West, 1, target_tail, eaten)
        eaten = eaten + dinosaur_move(South, size - 1, target_tail, eaten)


def dinosaur_move(direction, count, target_tail, already_eaten):
    eaten = 0
    for _ in range(count):
        if already_eaten + eaten >= target_tail:
            return eaten
        ate_this = get_entity_type() == Entities.Apple
        if not can_move(direction):
            return eaten
        move(direction)
        if ate_this:
            eaten = eaten + 1
    return eaten


if __name__ == "__main__":
    main()
