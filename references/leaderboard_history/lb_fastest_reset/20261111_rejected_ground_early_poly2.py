from __builtins__ import *
# 淘汰候选归档：lb_fastest_reset | 原实验路径 .codex/reset-route-20261111/candidates/ground-early-poly2.py
# 恐龙路径Copyright (c) 2026 enihsyou，MIT许可见enihsyou_LICENSE.txt。


def lb_fastest_reset():
    step1()
    for technology in [Unlocks.Speed, Unlocks.Trees, Unlocks.Expand,
                       Unlocks.Grass, Unlocks.Trees, Unlocks.Carrots,
                       Unlocks.Speed, Unlocks.Expand, Unlocks.Watering,
                       Unlocks.Grass, Unlocks.Trees, Unlocks.Grass,
                       Unlocks.Carrots, Unlocks.Fertilizer, Unlocks.Sunflowers]:
        if not buy(technology):
            return
    if not solar_reserve():
        return
    for technology in [Unlocks.Speed, Unlocks.Speed, Unlocks.Pumpkins,
                       Unlocks.Pumpkins, Unlocks.Polyculture]:
        if not buy(technology):
            return
    quick_print("directed", "polyculture", get_time(), num_items(Items.Power),
                num_items(Items.Fertilizer), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot))
    if not first_megafarm() or not eight_drones():
        return
    if staged_supply() and finish_gold():
        finish_bones()


def affordable(cost):
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True


def missing(cost, item):
    if item in cost:
        return max(0, cost[item] - num_items(item))
    return 0


def tick_cell(cost):
    if get_time() > 7000:
        return False
    entity = get_entity_type()
    if entity != None and can_harvest():
        harvest()
        entity = None
    if entity != None and entity != Entities.Grass:
        return True
    wood = missing(cost, Items.Wood)
    hay = missing(cost, Items.Hay)
    carrot = missing(cost, Items.Carrot)
    desired = Entities.Grass
    if wood > 0:
        if num_unlocked(Unlocks.Trees) > 0:
            if (get_pos_x() + get_pos_y()) % 2 == 0:
                desired = Entities.Tree
        elif hay == 0:
            desired = Entities.Bush
    if desired == Entities.Grass and hay == 0 and carrot > 0:
        if affordable(get_cost(Entities.Carrot)):
            desired = Entities.Carrot
        elif num_items(Items.Wood) < get_cost(Entities.Carrot)[Items.Wood]:
            if num_unlocked(Unlocks.Trees) > 0:
                if (get_pos_x() + get_pos_y()) % 2 == 0:
                    desired = Entities.Tree
            else:
                desired = Entities.Bush
    if desired == Entities.Grass:
        if get_ground_type() != Grounds.Grassland:
            till()
    else:
        if desired == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        if not plant(desired):
            quick_print("directed_failed", "plant", desired, get_time())
            return False
    return True


def basic(cost):
    if num_unlocked(Unlocks.Polyculture) > 0:
        return boost_stock(cost)
    passes = 0
    while not affordable(cost):
        if get_time() > 7000 or passes >= 1500:
            quick_print("directed_failed", "basic_limit", get_time(), cost)
            return False
        size = get_world_size()
        for x in range(size):
            for y in range(size):
                if not tick_cell(cost):
                    return False
                if affordable(cost):
                    return True
                move(North)
            move(East)
        passes += 1
        if passes % 40 == 0:
            quick_print("directed_progress", get_time(), cost, num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot))
    return True


def origin():
    size = get_world_size()
    for _ in range((size - get_pos_x()) % size):
        move(East)
    for _ in range((size - get_pos_y()) % size):
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
        if not pumpkin_strip(0, 1, size):
            return False
        before = num_items(Items.Pumpkin)
        harvest()
        quick_print("directed_pumpkin", get_time(), num_items(Items.Pumpkin) - before)
    return True


def buy(technology):
    cost = get_cost(technology)
    if Items.Pumpkin in cost:
        if not pumpkin_stock(cost[Items.Pumpkin]):
            return False
    if Items.Cactus in cost:
        if not cactus_stock(cost[Items.Cactus]):
            return False
    basic_cost = {}
    for item in cost:
        if item != Items.Pumpkin and item != Items.Cactus:
            basic_cost[item] = cost[item]
    if not basic(basic_cost):
        return False
    if not unlock(technology):
        quick_print("directed_failed", "unlock", technology, get_time())
        return False
    quick_print("directed_upgrade", technology, num_unlocked(technology), get_time(), num_items(Items.Power))
    return True


def solar_reserve():
    size = get_world_size()
    if not basic({Items.Carrot: size * size}):
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
            buckets[measure()].append((x, y))
            move(North)
        move(East)
    for petals in range(15, 6, -1):
        for x, y in buckets[petals]:
            for _ in range((x - get_pos_x()) % size):
                move(East)
            for _ in range((y - get_pos_y()) % size):
                move(North)
            while not can_harvest():
                if get_time() > 7000:
                    return False
                if get_water() < 0.5 and num_items(Items.Water) > 0:
                    use_item(Items.Water)
            harvest()
    quick_print("directed_solar", get_time(), num_items(Items.Power))
    return True


def solar_plant_strip(worker, workers, size, deadline):
    buckets = {}
    for petals in range(7, 16):
        buckets[petals] = []
    first = worker * size // workers
    last = (worker + 1) * size // workers
    for y in range(first, last):
        for x in range(size):
            if get_time() > deadline:
                return None
            go(x, y)
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Sunflower):
                return None
            buckets[measure()].append((x, y))
    return buckets


def solar_harvest_rank(points, deadline):
    for x, y in points:
        if get_time() > deadline:
            return False
        go(x, y)
        while not can_harvest():
            if get_time() > deadline:
                return False
            if get_water() < 0.5 and num_items(Items.Water) > 0:
                use_item(Items.Water)
        if not harvest():
            return False
    return True


def parallel_solar_reserve(size):
    started = get_time()
    deadline = min(7000, started + 180)
    workers = min(size, max_drones())
    handles = []
    passed = True
    batches = []
    for worker in range(1, workers):
        handle = spawn_drone(solar_plant_strip, worker, workers, size, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        own = solar_plant_strip(0, workers, size, deadline)
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
    for petals in range(15, 6, -1):
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

def nursery_stock(item, target, weird=False):
    if max_drones() > 1:
        return parallel_nursery_stock(item, target, weird)
    if num_items(item) >= target:
        return True
    crop = Entities.Tree
    support = Entities.Grass
    if item == Items.Hay:
        crop = Entities.Grass
        support = Entities.Bush
    elif item == Items.Carrot:
        crop = Entities.Carrot
        support = Entities.Bush
        gain = 2 ** (num_unlocked(Unlocks.Carrots) - 1) * (5 * 2 ** num_unlocked(Unlocks.Polyculture))
        count = (target - num_items(item) + gain - 1) // gain
        seed = get_cost(Entities.Carrot)
        reserve = count * 6 + 64
        if not nursery_stock(Items.Hay, reserve * seed[Items.Hay]):
            return False
        if not nursery_stock(Items.Wood, reserve * seed[Items.Wood]):
            return False
    size = get_world_size()
    anchors = []
    anchor_set = set()
    for y in range(0, min(size, 6), 2):
        for x in range(0, min(size, 6), 2):
            anchors.append((x, y))
            anchor_set.add((x, y))
    clear()
    if support == Entities.Bush:
        for x in range(size):
            for y in range(size):
                if (x, y) not in anchor_set:
                    if not plant(Entities.Bush):
                        return False
                move(North)
            move(East)
    accepted = []
    for _ in anchors:
        accepted.append(False)
    beginning = get_time()
    initial = num_items(item)
    produced = 0
    rejected = 0
    unready = 0
    for visit in range(20000):
        if get_time() > 7000 or get_time() > beginning + 700:
            quick_print("directed_failed", "nursery_limit", item, get_time())
            return False
        index = visit % len(anchors)
        x, y = anchors[index]
        go(x, y)
        if accepted[index]:
            if can_harvest():
                harvest()
                accepted[index] = False
                produced += 1
                if num_items(item) >= target:
                    quick_print("directed_nursery", item, beginning, get_time(), produced, rejected, unready, num_items(item) - initial)
                    return True
            else:
                unready += 1
                if get_water() < 0.5 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
                continue
        if crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        matched = False
        for attempt in range(128):
            if not affordable(get_cost(crop)) or not plant(crop):
                quick_print("directed_failed", "nursery_material", item, get_time())
                return False
            companion = get_companion()
            if companion == None:
                return False
            kind, position = companion
            if kind == support and position not in anchor_set:
                matched = True
                break
            harvest()
            rejected += 1
        if not matched:
            quick_print("directed_failed", "nursery_reroll", item, get_time())
            return False
        if weird:
            if num_items(Items.Fertilizer) < 1 or not use_item(Items.Fertilizer):
                quick_print("directed_failed", "nursery_fertilizer", get_time())
                return False
        if get_water() < 0.5 and num_items(Items.Water) >= 2:
            use_item(Items.Water, 2)
        accepted[index] = True
    quick_print("directed_failed", "nursery_visits", item, get_time())
    return False


def nursery_support_strip(worker, workers, size, support, deadline):
    first = worker * size // workers
    last = (worker + 1) * size // workers
    for y in range(first, last):
        for x in range(size):
            if get_time() > deadline:
                return False
            if x % 2 != 0 or y % 2 != 0:
                go(x, y)
                if not plant(support):
                    return False
    return True


def nursery_produce_strip(worker, workers, size, crop, support, item, target, weird, deadline):
    anchors = []
    for y in range(0, size, 2):
        if (y // 2) % workers == worker:
            for x in range(0, size, 2):
                anchors.append((x, y))
    accepted = []
    for _ in anchors:
        accepted.append(False)
    if len(anchors) == 0:
        return (True, 0, 0, 0)
    produced = 0
    rejected = 0
    unready = 0
    for visit in range(20000):
        if num_items(item) >= target:
            return (True, produced, rejected, unready)
        if get_time() > deadline:
            return (False, produced, rejected, unready)
        index = visit % len(anchors)
        x, y = anchors[index]
        go(x, y)
        if accepted[index]:
            if can_harvest():
                if weird and not use_item(Items.Weird_Substance, 1):
                    return (False, produced, rejected, unready)
                if not harvest():
                    return (False, produced, rejected, unready)
                accepted[index] = False
                produced += 1
                if num_items(item) >= target:
                    return (True, produced, rejected, unready)
            else:
                unready += 1
                if get_water() < 0.5 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
                continue
        if crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        matched = False
        for attempt in range(128):
            if num_items(item) >= target:
                return (True, produced, rejected, unready)
            if get_time() > deadline or not affordable(get_cost(crop)) or not plant(crop):
                return (False, produced, rejected, unready)
            companion = get_companion()
            if companion == None:
                return (False, produced, rejected, unready)
            kind, position = companion
            px, py = position
            if kind == support and (px % 2 != 0 or py % 2 != 0):
                matched = True
                break
            harvest()
            rejected += 1
        if not matched:
            return (False, produced, rejected, unready)
        if get_water() < 0.5 and num_items(Items.Water) >= 2:
            use_item(Items.Water, 2)
        accepted[index] = True
    return (False, produced, rejected, unready)


def parallel_nursery_stock(item, target, weird=False):
    if num_items(item) >= target:
        return True
    beginning = get_time()
    initial = num_items(item)
    size = get_world_size()
    workers = min(max_drones(), size // 2)
    crop = Entities.Tree
    support = Entities.Grass
    if item == Items.Hay:
        crop = Entities.Grass
        support = Entities.Bush
    elif item == Items.Carrot:
        crop = Entities.Carrot
        support = Entities.Bush
        gain = 2 ** (num_unlocked(Unlocks.Carrots) - 1) * (5 * 2 ** num_unlocked(Unlocks.Polyculture))
        count = (target - num_items(item) + gain - 1) // gain
        seed = get_cost(Entities.Carrot)
        reserve = count * 6 + 4 * ((size // 2) ** 2)
        if not nursery_stock(Items.Hay, reserve * seed[Items.Hay]):
            return False
        if not nursery_stock(Items.Wood, reserve * seed[Items.Wood]):
            return False
    deadline = min(7000, get_time() + 700)
    clear()
    if support == Entities.Bush:
        handles = []
        passed = True
        for worker in range(1, workers):
            handle = spawn_drone(nursery_support_strip, worker, workers, size, support, deadline)
            if handle == None:
                passed = False
                break
            handles.append(handle)
        if passed:
            passed = nursery_support_strip(0, workers, size, support, deadline)
        for handle in handles:
            if not wait_for(handle):
                passed = False
        if not passed:
            quick_print("directed_failed", "nursery_support_workers", get_time())
            return False
    handles = []
    passed = True
    results = []
    for worker in range(1, workers):
        handle = spawn_drone(nursery_produce_strip, worker, workers, size, crop, support, item, target, weird, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        results.append(nursery_produce_strip(0, workers, size, crop, support, item, target, weird, deadline))
    for handle in handles:
        results.append(wait_for(handle))
    produced = 0
    rejected = 0
    unready = 0
    for result in results:
        if result == None:
            passed = False
        else:
            if not result[0]:
                passed = False
            produced += result[1]
            rejected += result[2]
            unready += result[3]
    if num_items(item) < target:
        quick_print("directed_failed", "nursery_production_workers", item, get_time(), num_items(item), target)
        return False
    quick_print("directed_parallel_nursery", item, beginning, get_time(), workers, produced, rejected, unready, num_items(item) - initial)
    return True


def boost_stock(cost, weird=False):
    if weird:
        return nursery_stock(Items.Weird_Substance, cost[Items.Weird_Substance], True)
    for cycle in range(5):
        if affordable(cost):
            return True
        for item in [Items.Carrot, Items.Hay, Items.Wood]:
            if item in cost and not nursery_stock(item, cost[item]):
                return False
    return affordable(cost)


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


def first_megafarm():
    while num_unlocked(Unlocks.Speed) < 5:
        if not buy(Unlocks.Speed):
            return False
    if not solar_reserve():
        return False
    if not boost_stock({Items.Weird_Substance: 1400}, True):
        return False
    if not unlock(Unlocks.Mazes):
        return False
    clear()
    if not plant(Entities.Bush):
        return False
    size = get_world_size()
    if not use_item(Items.Weird_Substance, size):
        return False
    graph = build_maze_graph(size)
    for _ in range(60):
        if get_time() > 7000:
            return False
        target = measure()
        if target == None or not goto_treasure_with_graph(target[0], target[1], size, graph):
            return False
        if not use_item(Items.Weird_Substance, size):
            return False
        if num_items(Items.Gold) >= 2000:
            clear()
            if not unlock(Unlocks.Megafarm):
                return False
            quick_print("directed_megafarm", get_time(), max_drones(), num_items(Items.Power), num_items(Items.Fertilizer), num_items(Items.Weird_Substance))
            return True
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
        if move_direct_toward_treasure(tx, ty, size, graph):
            continue
        if not move_with_graph_path(target, size, graph):
            return False
    return True

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

def pumpkin_strip(start, stride, size):
    # 各列只有一个写者；健康成熟格在整田收割前不会再枯死。
    pending = []
    for x in range(start, size, stride):
        for y in range(size):
            pending.append((x, y))
    watering = max_drones() > 1
    deadline = min(7000, get_time() + 120)
    while pending and get_time() < deadline:
        remaining = []
        for x, y in pending:
            if get_time() >= deadline:
                quick_print("directed_failed", "pumpkin_pending_deadline", get_time(), start, len(pending))
                return False
            go(x, y)
            kind = get_entity_type()
            if kind != None and kind != Entities.Pumpkin and kind != Entities.Dead_Pumpkin:
                # 单机原流程收草；多机原流程直接翻地，保留各自准备费用。
                if kind != Entities.Grass or not watering:
                    harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if get_entity_type() != Entities.Pumpkin:
                if not affordable(get_cost(Entities.Pumpkin)) or not plant(Entities.Pumpkin):
                    return False
            if not can_harvest():
                if watering and get_water() < 0.5 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
                remaining.append((x, y))
        pending = remaining
    return not pending


def parallel_pumpkin_stock(target):
    size = get_world_size()
    workers = min(size, max_drones())
    while num_items(Items.Pumpkin) < target:
        if get_time() > 7000:
            return False
        price = get_cost(Entities.Pumpkin)[Items.Carrot]
        if not boost_stock({Items.Carrot: price * size * size * 2}):
            return False
        handles = []
        success = True
        for worker in range(1, workers):
            handle = spawn_drone(pumpkin_strip, worker, workers, size)
            if handle == None:
                success = False
                break
            handles.append(handle)
        if success:
            success = pumpkin_strip(0, workers, size)
        for handle in handles:
            if not wait_for(handle):
                success = False
        if not success:
            quick_print("directed_failed", "pumpkin_workers", get_time())
            return False
        origin()
        before = num_items(Items.Pumpkin)
        if not harvest():
            return False
        expected = size * size * min(6, size) * 2 ** (num_unlocked(Unlocks.Pumpkins) - 1)
        if num_items(Items.Pumpkin) - before != expected:
            quick_print("directed_failed", "pumpkin_group", get_time(), expected, num_items(Items.Pumpkin) - before)
            return False
        quick_print("directed_parallel_pumpkin", get_time(), workers, num_items(Items.Pumpkin) - before, num_items(Items.Power))
    return True


def next_megafarm():
    size = get_world_size()
    factor = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    unit = size * factor
    gain = size * size * factor
    target_gold = get_cost(Unlocks.Megafarm)[Items.Gold]
    count = (max(0, target_gold - num_items(Items.Gold)) + gain - 1) // gain
    if count > 299:
        return False
    if not boost_stock({Items.Weird_Substance: unit * (count + 1)}, True):
        return False
    clear()
    if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, unit):
        return False
    graph = build_maze_graph(size)
    if not maze_team(graph, size, min(max_drones(), 8), target_gold, unit, min(7000, get_time() + 800)):
        quick_print("directed_failed", "early_station_gold", get_time(), num_items(Items.Gold))
        return False
    clear()
    if not unlock(Unlocks.Megafarm):
        return False
    quick_print("directed_megafarm", get_time(), max_drones(), num_items(Items.Power), num_items(Items.Fertilizer), num_items(Items.Weird_Substance))
    return True


def eight_drones():
    if not buy(Unlocks.Fertilizer):
        return False
    if num_unlocked(Unlocks.Pumpkins) < 2:
        if not buy(Unlocks.Pumpkins):
            return False
    if not buy(Unlocks.Expand):
        return False
    if not solar_reserve():
        return False
    if not next_megafarm():
        return False
    if not buy(Unlocks.Carrots):
        return False
    if not buy(Unlocks.Pumpkins) or not buy(Unlocks.Expand):
        return False
    if not solar_reserve():
        return False
    # 先用一田C1实付Maze2，再筹32000 Gold；不提前读取下一宝藏。
    if not buy(Unlocks.Cactus) or not buy(Unlocks.Mazes):
        return False
    quick_print("early_maze2", get_time(), num_items(Items.Cactus), num_items(Items.Power))
    if not buy(Unlocks.Dinosaurs):
        return False
    clear()
    origin()
    change_hat(Hats.Dinosaur_Hat)
    run_dinosaur_chase_loop(get_world_size())
    change_hat(Hats.Straw_Hat)
    if not unlock(Unlocks.Polyculture):
        quick_print("directed_failed", "early_polyculture2", get_time(), num_items(Items.Bone))
        return False
    quick_print("reset_early_polyculture2", get_time(), num_items(Items.Bone))
    return next_megafarm()


def cactus_worker_supply(start, stride, phase, deadline):
    size = get_world_size()
    for line in range(start, size, stride):
        if get_time() > deadline:
            return False
        if phase == 0:
            go(line, 0)
            for y in range(size):
                if get_ground_type() != Grounds.Soil:
                    till()
                if not affordable(get_cost(Entities.Cactus)) or not plant(Entities.Cactus):
                    return False
                # 铺田时先消除相邻逆序，复用已支付的访问。
                if y > 0 and measure(South) > measure():
                    if not swap(South):
                        return False
                if not move(North):
                    return False
            # 最后一株播种后至少一秒；排序与自然成熟重叠，不做空巡回。
            mature_at = get_time() + 1
            if not sort_cactus_line(North, South, deadline):
                return False
            while get_time() < mature_at:
                if get_time() > deadline:
                    return False
        else:
            go(0, line)
            if not sort_cactus_line(East, West, deadline):
                return False
    return True


def cactus_stock(target):
    size = get_world_size()
    workers = min(size, max_drones())
    while num_items(Items.Cactus) < target:
        if not ensure_power(300):
            return False
        price = get_cost(Entities.Cactus)[Items.Pumpkin]
        if not pumpkin_stock(price * size * size):
            return False
        clear()
        for phase in range(2):
            deadline = get_time() + 120
            handles = []
            passed = True
            for worker in range(1, workers):
                handle = spawn_drone(cactus_worker_supply, worker, workers, phase, deadline)
                if handle == None:
                    passed = False
                    break
                handles.append(handle)
            if passed:
                passed = cactus_worker_supply(0, workers, phase, deadline)
            for handle in handles:
                if not wait_for(handle):
                    passed = False
            if not passed:
                quick_print("directed_failed", "cactus_workers", get_time(), phase)
                return False
        origin()
        expected = size * size * size * size * 2 ** (num_unlocked(Unlocks.Cactus) - 1)
        before = num_items(Items.Cactus)
        if not can_harvest() or not harvest() or num_items(Items.Cactus) - before != expected:
            quick_print("directed_failed", "cactus_gain", get_time(), expected, num_items(Items.Cactus) - before)
            return False
        quick_print("directed_cactus", get_time(), num_items(Items.Cactus), num_items(Items.Power))
    return True


def ensure_power(target):
    attempts = 0
    while num_items(Items.Power) < target:
        if attempts >= 5 or get_time() > 7000 or not solar_reserve():
            return False
        attempts += 1
    return True


def staged_supply():
    # 提高每单位肥料的Weird兑现；费用全部走满当前伴生的生产。
    for technology in [Unlocks.Trees, Unlocks.Trees, Unlocks.Watering,
                       Unlocks.Watering, Unlocks.Watering, Unlocks.Watering]:
        if not buy(technology):
            return False
    # 供料前真实补电，支付播种、成熟和收获，以覆盖P4与扩田生产。
    if not solar_reserve():
        return False
    # 用实际16000 Carrot购买P4，再支付Expand7与Cactus科技的整田供料。
    if not buy(Unlocks.Pumpkins):
        return False
    # Expand7的64000 Pumpkin走原真实供料，不借后期库存。
    if not buy(Unlocks.Expand):
        return False
    quick_print("directed_expand16", get_time(), get_world_size(), num_items(Items.Power), num_items(Items.Pumpkin))
    if not ensure_power(1200):
        return False
    while num_unlocked(Unlocks.Cactus) < 2:
        if not buy(Unlocks.Cactus):
            return False
    # M2→4=504000；D0→4=518000；保留30000苹果与告警储备。
    if not cactus_stock(1052000):
        return False
    while num_unlocked(Unlocks.Mazes) < 4:
        if not buy(Unlocks.Mazes):
            return False
    while num_unlocked(Unlocks.Dinosaurs) < 4:
        if not buy(Unlocks.Dinosaurs):
            return False
    quick_print("directed_supply", get_time(), num_items(Items.Cactus), num_items(Items.Power), num_items(Items.Fertilizer))
    return True


# 驻点服务：仅由预分配owner兑现；所有worker实际回程并观察新开墙。
def maze_team(graph, size, workers, target_gold, unit, deadline):
    directions = [North, East, South, West]
    reverse = {North: South, East: West, South: North, West: East}
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]

    def distances(center):
        dist = []
        parent = []
        incoming = []
        for _ in range(size * size):
            dist.append(size * size)
            parent.append(-1)
            incoming.append(None)
        dist[center] = 0
        parent[center] = center
        queue = [center]
        for current in queue:
            for edge in graph[current]:
                if parent[edge[0]] == -1:
                    parent[edge[0]] = current
                    incoming[edge[0]] = edge[1]
                    dist[edge[0]] = dist[current] + 1
                    queue.append(edge[0])
        return dist, parent, incoming

    centers = [0]
    tables = []
    closest = []
    for _ in range(size * size):
        closest.append(size * size)
    for worker in range(workers):
        table = distances(centers[worker])
        tables.append(table)
        for node in range(size * size):
            closest[node] = min(closest[node], table[0][node])
        if worker + 1 < workers:
            farthest = 0
            for node in range(size * size):
                if closest[node] > closest[farthest]:
                    farthest = node
            centers.append(farthest)
    owners = []
    for node in range(size * size):
        owner = 0
        for worker in range(1, workers):
            if tables[worker][0][node] < tables[owner][0][node]:
                owner = worker
        owners.append(owner)

    def serve(worker):
        center = centers[worker]
        dist, parent, incoming = tables[worker]
        route = []
        node = center
        while node != 0:
            route.append(tables[0][2][node])
            node = tables[0][1][node]
        for i in range(len(route) - 1, -1, -1):
            if not move(route[i]):
                return False
        hits = 0
        outbound = 0
        discoveries = 0
        while num_items(Items.Gold) < target_gold:
            if get_time() >= deadline:
                return False
            treasure = measure()
            if treasure == None:
                return False
            target = treasure[0] + treasure[1] * size
            if owners[target] != worker:
                # 原开边永久保留；闭合往返后仍在center。每次实际付400t移动和约0.066秒响应间隔。
                idle_direction = graph[center][0][1]
                if not move(idle_direction) or not move(reverse[idle_direction]):
                    return False
                continue
            route = []
            node = target
            while node != center:
                route.append(incoming[node])
                node = parent[node]
            walked = []
            for i in range(len(route) - 1, -1, -1):
                if measure() != treasure or num_items(Items.Gold) >= target_gold:
                    break
                if not move(route[i]):
                    return False
                walked.append(route[i])
                outbound += 1
            if len(walked) == len(route) and num_items(Items.Gold) < target_gold and measure() == treasure:
                if not use_item(Items.Weird_Substance, unit):
                    return False
                hits += 1
            if num_items(Items.Gold) >= target_gold:
                quick_print("station_worker", worker, hits, outbound, discoveries, get_time())
                return True
            # 返回路径仍使用本次出发的不可变方向列；新边只修改下一次出发的父指针。
            new_edges = []
            for i in range(len(walked) - 1, -2, -1):
                x = get_pos_x()
                y = get_pos_y()
                current = x + y * size
                for j in range(4):
                    nx = x + dx[j]
                    ny = y + dy[j]
                    if 0 <= nx < size and 0 <= ny < size and can_move(directions[j]):
                        neighbor = nx + ny * size
                        known = False
                        for edge in graph[current]:
                            if edge[0] == neighbor:
                                known = True
                                break
                        if not known:
                            add_maze_edge(graph, current, neighbor, directions[j])
                            add_maze_edge(graph, neighbor, current, reverse[directions[j]])
                            new_edges.append(current)
                            new_edges.append(neighbor)
                            discoveries += 1
                if i >= 0 and not move(reverse[walked[i]]):
                    return False
            for current in new_edges:
                for edge in graph[current]:
                    neighbor = edge[0]
                    if dist[neighbor] > dist[current] + 1:
                        dist[neighbor] = dist[current] + 1
                        parent[neighbor] = current
                        incoming[neighbor] = edge[1]
                        new_edges.append(neighbor)
        quick_print("station_worker", worker, hits, outbound, discoveries, get_time())
        return True

    handles = []
    passed = True
    for worker in range(1, workers):
        handle = spawn_drone(serve, worker)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        passed = serve(0)
    for handle in handles:
        if not wait_for(handle):
            passed = False
    return passed and num_items(Items.Gold) >= target_gold


def finish_gold():
    if not ensure_power(2000):
        return False
    return small_maze_gold(1000000)


def finish_bones():
    if not ensure_power(600):
        return False
    clear()
    for cycle in range(15):
        if num_items(Items.Bone) >= 2000000:
            if not unlock(Unlocks.Leaderboard):
                return False
            quick_print("directed_done", get_time(), num_items(Items.Bone), num_items(Items.Gold))
            return True
        if get_time() > 7000 or num_items(Items.Cactus) < get_world_size() * get_world_size() * get_cost(Entities.Apple)[Items.Cactus]:
            return False
        origin()
        before = num_items(Items.Bone)
        change_hat(Hats.Dinosaur_Hat)
        run_dinosaur_chase_loop(get_world_size())
        change_hat(Hats.Straw_Hat)
        if num_items(Items.Bone) <= before:
            quick_print("directed_failed", "bone_no_gain", get_time(), cycle)
            return False
        quick_print("directed_bone", get_time(), num_items(Items.Bone) - before, num_items(Items.Cactus), num_items(Items.Power))
        clear()
    return False


def sort_cactus_line(forward, backward, deadline):
    size = get_world_size()
    bound_low = 0
    bound_high = size - 1
    while True:
        if get_time() >= deadline:
            return False
        swap_pos_last = -1
        if not move_cactus_line_to(forward, backward, bound_low, deadline):
            return False
        i = bound_low
        while i < bound_high - 1:
            if get_time() >= deadline:
                return False
            if not move(forward):
                return False
            i = i + 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if a > b:
                if not swap(backward):
                    return False
                swap_pos_last = max(swap_pos_last, i)
                a, b = b, a
            if b > c:
                if not swap(forward):
                    return False
                swap_pos_last = max(swap_pos_last, i + 1)
                b, c = c, b
                if a > b:
                    if not swap(backward):
                        return False
        if swap_pos_last == -1:
            break
        bound_high = swap_pos_last - 2
        if bound_low >= bound_high:
            break
        swap_pos_first = size
        if not move_cactus_line_to(forward, backward, bound_high, deadline):
            return False
        i = bound_high
        while i > bound_low + 1:
            if get_time() >= deadline:
                return False
            if not move(backward):
                return False
            i = i - 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if b > c:
                if not swap(forward):
                    return False
                swap_pos_first = min(swap_pos_first, i)
                b, c = c, b
            if a > b:
                if not swap(backward):
                    return False
                swap_pos_first = min(swap_pos_first, i - 1)
                a, b = b, a
                if b > c:
                    if not swap(forward):
                        return False
        if swap_pos_first == size:
            break
        bound_low = swap_pos_first + 2
        if bound_low >= bound_high:
            break
    if bound_low + 1 == bound_high:
        if not move_cactus_line_to(forward, backward, bound_low, deadline):
            return False
        if get_time() >= deadline:
            return False
        if measure() > measure(forward):
            if not swap(forward):
                return False
    return get_time() < deadline

def move_cactus_line_to(forward, backward, target, deadline):
    size = get_world_size()
    if forward == North:
        current = get_pos_y()
    else:
        current = get_pos_x()
    delta = (target - current) % size
    if delta <= size // 2:
        for _ in range(delta):
            if get_time() >= deadline:
                return False
            if not move(forward):
                return False
    else:
        for _ in range(size - delta):
            if get_time() >= deadline:
                return False
            if not move(backward):
                return False
    return get_time() < deadline

def run_dinosaur_chase_loop(size):
    # https://www.reddit.com/r/TheFarmerWasReplaced/comments/1o90hxs/my_sna_i_mean_dinosaur_algorithm/
    s = get_world_size()
    m = s - 1
    l = s * s // 2  # 苹果观测次数阈值；直段可能经过苹果，因此不等于精确尾长。

    dir = East
    snake = 0
    while True:
        x, y = get_pos_x(), get_pos_y()
        if get_entity_type() == Entities.Apple:
            snake += 1
            wx, wy = measure()  # ty: ignore

        # 后期优先填满成对列间的空隙，缩小苹果可生成的区域。
        if snake > l:
            if y == 0 and can_move(North) and x % 2 == 1:
                for _ in range(m - 1):  # 避开最北的一行
                    # 碰尾只结束这段直走，下一轮仍按当前位置选路。
                    if not move(North):
                        break
                continue

        # 访问中心区域的果子
        if x != 0 and x != m:  # 不在左右两侧
            if (x == wx or x + 1 == wx) and x % 2 == 1:
                if can_move(North) and wy > y and wy != m:  # 向北可以到达苹果
                    for _ in range(wy - y):
                        move(North)
                    continue
            if (x == wx or x - 1 == wx) and x % 2 == 0:
                if can_move(South) and y > wy and wy != 0:  # 向南可以前往苹果
                    for _ in range(y - wy):
                        move(South)
                    continue

        # 围着操场逆时针转圈
        if dir == East:
            if y != 0 and can_move(South):
                while move(South) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == m:
                dir = North  # 在边界转向, 下面直接 move 节约一个循环
            if not (move(dir) or move(North)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == West:
            if y == m and can_move(dir) and x > wx + 1:
                for _ in range(x - wx - 1 - 1):  # 考虑到奇偶性，多减 1
                    move(dir)  # 快速移过最北边, 因为那是回程的线
            if y != m and can_move(North):
                while move(North) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == 0:
                dir = South  # 在边界转向
            if not (move(dir) or move(South)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == South:
            if x != 0 and can_move(West):
                move(West)  # 回归边线
                continue
            if x == 0 and y != 0:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not (can_move(dir) or can_move(East)):
                    break  # 碰到尾巴
            dir = East  # 在边界转向
            continue
        if dir == North:
            if x != m and can_move(East):
                move(East)  # 回归边线
                continue
            if x == m and y != m:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not can_move(dir) and not can_move(West):
                    break  # 碰到尾巴
            dir = West  # 在边界转向
            continue

def small_maze_gold(target):
    # 使用迷宫榜已经验证的独立小宫与增量路由；所有子机回收后再清场。
    WORLD = get_world_size()
    TARGET_GOLD = target
    DRONES = min(max_drones(), 8)
    REUSE_LIMIT = 300
    DIRS = [North, East, South, West]
    BACK = [2, 3, 0, 1]
    MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    n = WORLD // 3
    deadline = min(7000, get_time() + 800)
    # 金币/Weird比为宫边长；另付创建、到位登记和并行超收的完整储备。
    required = (max(0, target - num_items(Items.Gold)) + n - 1) // n + 8 * n * MULT * DRONES + 2 * DRONES
    if not boost_stock({Items.Weird_Substance: required}, True):
        return False
    clear()
    start_stock = num_items(Items.Weird_Substance)
    jobs = []
    for index in range(DRONES):
        jobs.append((n, n // 2 + n * (index % 3), n // 2 + n * (index // 3)))


    def go_empty(tx, ty):
        # 仅用于所有迷宫生成前。利用32x32农场环绕，分别走较短的横、纵位移。
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
        # 仅在本宫已经harvest消失后调用；路线留在原方块内部，不环绕穿过邻宫。
        while get_pos_x() < cx:
            move(East)
        while get_pos_x() > cx:
            move(West)
        while get_pos_y() < cy:
            move(North)
        while get_pos_y() > cy:
            move(South)

    def geometry(n):
        # 本地格号 p=y*n+x；grid[p][方向]是几何邻居，-1表示本宫边界。
        # 几何表。
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
        # links记录实测通路；graph供DFS选择未访问的邻居，建图后不再返回。
        # walls记录当时仍有墙的方向；以后可能从两端之一发现该墙已经消失。
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

        # order是父节点先于子节点的顺序；trail记录真正走过的DFS回退方向。
        order = []
        trail = []
        p = home
        visited = 0
        while True:
            if get_time() > deadline:
                return None
            if not seen[p]:
                # 正常取消条件：其它机可能已凑够黄金，没必要继续建这张图。
                if num_items(Items.Gold) >= TARGET_GOLD:
                    return None
                seen[p] = True
                visited += 1
                order.append(p)
                for d in range(4):
                    q = grid[p][d]
                    # 边界不能跨；已从另一端记下的通路不用重复探测。
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
                # 连通树、尚有未访问节点：必然还有可以回退的祖先。
                d = trail.pop()
                move(DIRS[d])
                p = grid[p][d]

        # 初始根parent=-1；up_hop是往父节点走的指令，down_hop是相反指令。
        tree = (parent, up_hop, down_hop, order)
        return (p, links, walls, tree)

    def build_all_routes(tree, blank):
        # rows[目标][0][起点] = 最短距离。
        # rows[目标][1][起点] = (下一格, 游戏方向对象)。注意第一维是“目标”。
        parent, up_hop, down_hop, order = tree
        rows = []
        for goal in range(len(blank)):
            dist = list(blank)
            hop = list(up_hop)
            dist[goal] = 0
            hop[goal] = None
            rows.append([dist, hop])
        # 每加入一个叶节点，只算它与已加入节点的无序点对，并填写双向首步。
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
        # 已知图刚新增一条无向单位边a--b。
        # 新最短路只能是：旧路、经a->b、经b->a。无需重新跑BFS。
        da, ha = rows[a]
        db, hb = rows[b]
        left = []
        right = []

        # 必须先冻结两侧距离与首步，再开始修改rows。
        # left: D(u,a)+1 < D(u,b)；right: D(v,b)+1 < D(v,a)。
        # 只有左右两组之间的点对可能变短；快照里仅一侧加1，代表新边长度。
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

        # 把较小集合放外层；x+y仍然只包含一次新边长度，互换不改变计算。
        if len(left) > len(right):
            left, right = right, left
        for u, x, hop_u, row_u in left:
            dist_u, toward_u = row_u
            for v, y, hop_v, row_v in right:
                candidate = x + y
                # 这是算法条件：只更新严格更短的路线，等长时保留原首步。
                if candidate < dist_u[v]:
                    dist_u[v] = candidate
                    # row_u的目标是u，因此起点v应采用hop_v，而不是hop_u。
                    toward_u[v] = hop_v
                    dist_v, toward_v = row_v
                    dist_v[u] = candidate
                    toward_v[u] = hop_u

    def scan_departure(p, links, walls, grid, routes):
        # 固定原SENSOR_MODE=1：只在上一箱位置、下一次出发前检查原来的墙。
        # 发现一条边便完整更新路由表。
        remaining = []
        for side in walls[p]:
            # 同一条墙可能早已从另一端发现，必须去重。
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
            # 一机一宫；measure一定返回本宫当前宝箱坐标。
            t = measure()
            goal = (t[1] - by) * n + t[0] - bx  # ty: ignore[not-subscriptable]  本机始终处于独占迷宫，measure返回坐标。
            if p != goal:
                # 第一次搬箱前还没有开新墙，不重复扫描刚建图时测过的墙。
                if relocations > 0 and len(walls[p]) > 0:
                    scan_departure(p, links, walls, grid, routes)
                dist, hop = routes[goal]
                # 沿已确认的路线移动；不查实体、不重复核对坐标、不检查move返回值。
                for _ in range(dist[p]):
                    p, direction = hop[p]
                    move(direction)

            # 正常终止条件：行走期间其它宫可能已达到目标，不再多收/多搬一箱。
            if num_items(Items.Gold) >= TARGET_GOLD:
                return relocations
            if relocations >= REUSE_LIMIT:
                # 300次成功搬迁之后，走到最后一个箱子并harvest，本宫才会消失。
                harvest()
                return relocations + 1
            use_item(Items.Weird_Substance, cost)
            relocations += 1
        return relocations

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

        # 正常初始化：中心若尚无自动生长的草，就主动种一株作为登记载体。
        if get_entity_type() == None:
            plant(Entities.Grass)
        # 32台各用两次WS：感染再恢复。全场合计消耗64，构成到位计数。
        for _ in range(2):
            use_item(Items.Weird_Substance, 1)
        while num_items(Items.Weird_Substance) > start_stock - 2 * DRONES:
            if get_time() > deadline:
                return (n, 0, 0)
            change_hat(Hats.Straw_Hat)

        while num_items(Items.Gold) < TARGET_GOLD and get_time() <= deadline:
            go_home(cx, cy)
            # 普通场地清理：有草才收，没有植物就直接种灌木。
            if get_entity_type() != None:
                harvest()
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, n * MULT)
            mapped = explore(n, grid, home)
            generations += 1
            if mapped == None:
                # explore只有一种None含义：其它机已经达到黄金目标，正常取消。
                break
            boxes += solve_one(n, bx, by, grid, mapped, blank)
            # 完整收掉本宫后才进入下一代；下次go_home仍然回同一个固定中心。
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


if __name__ == "__main__":
    lb_fastest_reset()
