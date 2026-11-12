from __builtins__ import *
# 完整轮时间：2507.696秒（2026-11-12，实机完整3轮）；C#原目标3seed均值2479.106秒。
# 恐龙路径Copyright (c) [2026] [lywlucas]，MIT许可见lywlucas_LICENSE.txt。
# 小迷宫沿用lb_maze的zzlg-git方案；来源与许可边界见同名策略文档。


def lb_fastest_reset():
    step1()
    # 扩4格后实付Speed3，供能后再付Speed4/5及伴生。
    for technology in [Unlocks.Speed, Unlocks.Trees, Unlocks.Expand, Unlocks.Speed,
                       Unlocks.Grass, Unlocks.Trees, Unlocks.Carrots,
                       Unlocks.Expand, Unlocks.Watering,
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


def parallel_solar_reserve(size, target=0):
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

def boost_stock(cost):
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
        handle = spawn_drone(stock_worker, worker, workers, cost, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed and not stock_worker(0, workers, cost, deadline):
        passed = False
    for handle in handles:
        if not wait_for(handle):
            passed = False
    quick_print("persistent_stock", passed, began, get_time(), cost,
                num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot),
                num_items(Items.Weird_Substance))
    return passed and affordable(cost)


def stock_worker(worker, workers, cost, deadline):
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
        if not stock_cell(cost, bounds, deadline):
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


def stock_cell(cost, bounds, deadline):
    entity = get_entity_type()
    if entity in [Entities.Grass, Entities.Bush, Entities.Tree, Entities.Carrot]:
        if not can_harvest():
            if get_water() < 0.5 and num_items(Items.Water) >= 2:
                use_item(Items.Water, 2)
            return True
        companion = get_companion()
        if companion != None:
            kind, position = companion
            if stock_companion_inside(position, bounds):
                hay, wood = stock_seed_budget(cost, 2 * max_drones() + 2)
                if kind != Entities.Carrot or (num_items(Items.Hay) >= hay and num_items(Items.Wood) >= wood):
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
    for attempt in range(128):
        if get_time() > deadline:
            return False
        if not affordable(get_cost(crop)) or not plant(crop):
            quick_print("persistent_failed", "plant", crop, get_time())
            return False
        companion = get_companion()
        if companion != None and stock_companion_inside(companion[1], bounds):
            return True
        if not harvest():
            return False
    quick_print("persistent_failed", "companion", get_time())
    return False


def stock_companion_inside(position, bounds):
    # 支撑位不能占用本机主种植位，也不能进入其他工人的矩形。
    x, y = position
    x0, x1, y0, y1 = bounds
    return x >= x0 and x < x1 and y >= y0 and y < y1 and (x % 2 != 0 or y % 2 != 0)


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


def stock_support(kind, position):
    x, y = get_pos_x(), get_pos_y()
    px, py = position
    go(px, py)
    if get_entity_type() != kind:
        if get_entity_type() != None and not harvest():
            return False
        if kind == Entities.Grass and get_ground_type() != Grounds.Grassland:
            till()
        elif kind == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        if not affordable(get_cost(kind)) or not plant(kind):
            return False
    go(x, y)
    return True


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
    if not boost_stock({Items.Weird_Substance: 1400}):
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
    target_gold = get_cost(Unlocks.Megafarm)[Items.Gold]
    if not small_maze_gold(target_gold, get_world_size() // 2):
        quick_print("directed_failed", "early_small_gold", get_time(), num_items(Items.Gold))
        return False
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
    # 提前筹最终8座5格M4小迷宫的Weird，联产木头支付胡萝卜5/6与供水6。
    required = (max(0, 1000000 - num_items(Items.Gold)) + 4) // 5 + 8 * 5 * 8 * 8 + 16
    if not boost_stock({Items.Weird_Substance: required}):
        return False
    for technology in [Unlocks.Carrots, Unlocks.Carrots, Unlocks.Watering]:
        if not buy(technology):
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





def finish_gold():
    # Weird已提前支付；补足末段迷宫与四条蛇所需能量，避免再收整田。
    if num_items(Items.Power) < 1600:
        if not basic({Items.Carrot: get_world_size() * get_world_size()}):
            return False
        if not parallel_solar_reserve(get_world_size(), 1600):
            return False
    return small_maze_gold(1000000)





def finish_bones():
    # 迷宫工人均已回收，预留400 Power，串行完成完整恐龙周期。
    if not ensure_power(400):
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
        maximum = get_world_size() * get_world_size() - 1
        factor = 2 ** (num_unlocked(Unlocks.Dinosaurs) - 1)
        length = maximum
        remaining = 2000000 - num_items(Items.Bone)
        while (length - 1) * (length - 1) * factor >= remaining:
            length -= 1
        cactus_floor = -1
        if length < maximum:
            cactus_floor = num_items(Items.Cactus) - (length + 1) * get_cost(Entities.Apple)[Items.Cactus]
        before = num_items(Items.Bone)
        change_hat(Hats.Dinosaur_Hat)
        run_dinosaur_chase_loop(get_world_size(), cactus_floor)
        change_hat(Hats.Straw_Hat)
        expected = length * length * factor
        if num_items(Items.Bone) - before < expected:
            quick_print("directed_failed", "bone_incomplete_cycle", get_time(), cycle)
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

def run_dinosaur_chase_loop(size, cactus_floor):
    global farm_size
    global cycle_deadline
    global main_area
    farm_size = size
    cycle_deadline = min(7000, get_time() + 1200)
    A = size ** 2
    turn_point = A // 2
    main_area = ((1, size - 1), size - 1, West, North)
    main_move = {}
    for xi in range(size):
        for yi in range(size):
            i = cycle_index(xi, yi)
            if i < size:
                main_move[i] = South
            elif i == size:
                main_move[i] = East
            else:
                i = i % A
                main_move[i] = region_step(main_area, (xi, yi))
    cnt = 1
    next_x, next_y = measure()  # ty: ignore[not-iterable]  此处位于Apple上，measure返回下一苹果坐标。
    next_id = cycle_index(next_x, next_y)
    while get_time() < cycle_deadline:
        x, y = (get_pos_x(), get_pos_y())
        id = cycle_index(x, y)
        if id == next_id:
            cnt += 1
            next_x, next_y = measure()  # ty: ignore[not-iterable]  此处位于Apple上，measure返回下一苹果坐标。
            next_id = cycle_index(next_x, next_y)
        if cnt >= turn_point:
            quick_print('dinosaur_finish', cnt, get_time())
            fill_main_cycle(id, main_move, next_id, cactus_floor)
            break
        ccnt = cnt - size + cnt // size
        if id < ccnt:
            if id < next_id <= ccnt:
                l = next_id - id
                for _ in range(l):
                    move(main_move[id])
                    id += 1
                continue
            else:
                l = ccnt - id
                for _ in range(l):
                    move(main_move[id])
                    id += 1
                continue
        elif x == 0:
            move(main_move[id])
            continue
        else:
            next_target, new_cnt = collect_in_region((next_x, next_y), main_area, cnt)
            next_x, next_y = next_target
            next_id = cycle_index(next_x, next_y)
            cnt = new_cnt
    return


REVERSE = {East: West, West: East, North: South, South: North}
farm_size = 32
cycle_deadline = 0
# 主区域由每轮入口按田尺寸建立，区域查询只复用它。
main_area = None


# 主回路编号只用本轮固定田尺寸，避免每次坐标换算重新读取世界。
def cycle_index(x, y):
    n = farm_size
    if x == 0:
        return n - y
    elif y % 2 == 0:
        return n + (n - 1) * y + x
    else:
        return n + (n - 1) * y + n - x


# 判断目标是否在当前矩形，以及是否位于该矩形蛇形路线的前方。
def in_region(location, area, upper=False, can_equal=True):
    size = farm_size
    (x_n, y_n), width, dir, up = area
    x, y = location
    if area == main_area:
        if upper == False:
            return x != 0
        else:
            a, b = (get_pos_x(), get_pos_y())
            return size < cycle_index(a, b) <= cycle_index(x, y)
    if upper == True:
        a, b = (get_pos_x(), get_pos_y())
        flg = False
        if in_region((a, b), area) == False:
            return False
        if up == East:
            if a > x:
                return False
            elif a == x:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif up == West:
            if a < x:
                return False
            elif a == x:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif up == North:
            if b > y:
                return False
            elif b == y:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif b < y:
            return False
        elif b == y:
            if can_equal == False:
                return False
            else:
                flg = True
        if flg != False:
            d = region_step(area, (a, b))
            if a > x:
                if d != West:
                    return False
            elif a < x:
                if d != East:
                    return False
            elif b > y:
                if d != South:
                    return False
            elif b < y:
                if d != North:
                    return False
    if dir == East:
        if x <= x_n - width or x > x_n:
            return False
    elif dir == West:
        if x < x_n or x >= x_n + width:
            return False
    elif dir == North:
        if y > y_n or y <= y_n - width:
            return False
    elif y < y_n or y >= y_n + width:
        return False
    if up == North:
        if y > y_n:
            return False
    elif up == West:
        if x < x_n:
            return False
    elif up == South:
        if y < y_n:
            return False
    elif x > x_n:
        return False
    return True


# 返回区域蛇形方向；给出模拟坐标时只计算，不移动。
def region_step(area, simulating=None):
    (x_n, y_n), width, dir, up = area
    if simulating == None:
        x, y = (get_pos_x(), get_pos_y())
        if in_region((x, y), area) == False:
            return None
    else:
        x, y = simulating
    if dir == East or dir == West:
        up_dist = abs(y - y_n)
        hor_dist = abs(x - x_n)
    else:
        up_dist = abs(x - x_n)
        hor_dist = abs(y - y_n)
    new_dir = dir
    if up_dist % 2 == 0:
        if hor_dist == 0 and up_dist != 0:
            new_dir = up
        else:
            pass
    elif hor_dist == width - 1:
        new_dir = up
    else:
        new_dir = REVERSE[dir]
    if simulating == None:
        move(new_dir)
    return new_dir


# 在当前安全矩形内沿剪枝路线到目标，返回最后转折点；受阻或超时交回上层。
def reach_in_region(target, area):
    a, b = target
    (x_n, y_n), width, dir, up = area
    break_point = None
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return None
    if in_region(target, area, True, True) == False:
        reach_in_region((x_n, y_n), area)
        region_step(area)
        return None
    while get_time() < cycle_deadline:
        x, y = (get_pos_x(), get_pos_y())
        if x == a and y == b:
            if break_point == None:
                break_point = (a, b)
            return break_point
        if dir == East or dir == West:
            if x == a:
                break_point = (x, y)
                for _ in range(abs(y - b)):
                    if not move(up):
                        return None
                continue
            temp = region_step(area, (x, y))
            if temp == East:
                if x > a:
                    if not move(up):
                        return None
                else:
                    for _ in range(a - x):
                        if not move(East):
                            return None
            elif temp == West:
                if x < a:
                    if not move(up):
                        return None
                else:
                    for _ in range(x - a):
                        if not move(West):
                            return None
            else:
                if not move(temp):
                    return None
        else:
            if y == b:
                break_point = (x, y)
                for _ in range(abs(x - a)):
                    if not move(up):
                        return None
                continue
            temp = region_step(area, (x, y))
            if temp == North:
                if y > b:
                    if not move(up):
                        return None
                else:
                    for _ in range(b - y):
                        if not move(North):
                            return None
            elif temp == South:
                if y < b:
                    if not move(up):
                        return None
                else:
                    for _ in range(y - b):
                        if not move(South):
                            return None
            else:
                if not move(temp):
                    return None
    return None


# 按区域出口恢复父区域路线，避免任意短路破坏身体形状。
def leave_region(area):
    (x_n, y_n), width, dir, up = area
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return True
    if up == North or up == South:
        if y != y_n:
            move(up)
        for _ in range(abs(x - x_n) + 1):
            move(dir)
    else:
        if x != x_n:
            move(up)
        for _ in range(abs(y - y_n) + 1):
            move(dir)


# 追当前苹果后按可达性进入内区或外区，退出时恢复父区域。
def collect_in_region(target, area, cnt):
    if get_time() >= cycle_deadline:
        return (target, cnt)
    (x_n, y_n), width, dir, up = area
    a, b = target
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return (target, cnt)
    if a == 0:
        reach_in_region((x_n, y_n), area)
        region_step(area)
        return (target, cnt)
    last_break = reach_in_region(target, area)
    if last_break == None:
        return (target, cnt)
    cnt += 1
    x, y = (get_pos_x(), get_pos_y())
    if x != a or y != b:
        return (target, cnt)
    newt = measure()
    if in_region(newt, area, True) == True:
        newt, cnt = collect_in_region(newt, area, cnt)
    else:
        # 目标需要跨区时才计算转折带；外侧区域仅在内侧不可达时构造。
        x_b, y_b = last_break
        x_g, y_g = (x, y)
        x_f, y_f = (x, y)
        if up == North or up == South:
            warn = abs(y - y_n)
            n_width = abs(y - y_b)
            if dir == East:
                x_f = x_n - width + 1
                x_g = x_n
            else:
                x_f = x_n + width - 1
                x_g = x_n
        else:
            warn = abs(x - x_n)
            n_width = abs(x - x_b)
            if dir == North:
                y_f = y_n - width + 1
                y_g = y_n
            else:
                y_f = y_n + width - 1
                y_g = y_n
        if warn != 0:
            area_ins = ((x_g, y_g), n_width - 1, up, dir)
            if in_region(newt, area_ins, True, False) == True:
                move(dir)
                newt, cnt = collect_in_region(newt, area_ins, cnt)
                newt, cnt = collect_in_region(newt, area, cnt)
            else:
                area_out = ((x_f, y_f), n_width - 1, up, REVERSE[dir])
                if in_region(newt, area_out, True, False) == True:
                    move(REVERSE[dir])
                    newt, cnt = collect_in_region(newt, area_out, cnt)
                    newt, cnt = collect_in_region(newt, area, cnt)
    if width < farm_size - 1:
        leave_region(area)
    elif cnt <= y * 2 + 1:
        leave_region(area)
    else:
        reach_in_region((x_n, y_n), area)
        region_step(area)
    return (newt, cnt)


# 未满蛇且只有本机消耗Cactus时，可由扣除首个Apple的实耗核算身体增长。
# 沿主回路整段到果，只在Apple处核对；满蛇保留原快速循环。
def fill_main_cycle(start, moves, apple_index, cactus_floor):
    count = len(moves)
    start = start % count
    if cactus_floor >= 0:
        apple_index = apple_index % count
        if num_items(Items.Cactus) <= cactus_floor:
            return
        if get_entity_type() == Entities.Apple:
            if not move(moves[start]):
                return
            start = (start + 1) % count
        while num_items(Items.Cactus) > cactus_floor:
            if start > apple_index:
                for i in range(start, count):
                    if not move(moves[i]):
                        return
                start = 0
            for i in range(start, apple_index):
                if not move(moves[i]):
                    return
            x, y = measure()  # ty: ignore[not-iterable]  此时沿已知回路到达唯一Apple。
            following = cycle_index(x, y) % count
            if not move(moves[apple_index]):
                return
            start = (apple_index + 1) % count
            apple_index = following
        return
    while True:
        for i in range(start, count):
            if not move(moves[i]):
                return
        start = 0

def small_maze_gold(target, n=None):
    # 中期2/4机用半幅小迷宫，末段8机用三列布局；工人全回收后才清场。
    WORLD = get_world_size()
    TARGET_GOLD = target
    DRONES = min(max_drones(), 8)
    REUSE_LIMIT = 300
    DIRS = [North, East, South, West]
    BACK = [2, 3, 0, 1]
    MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    cols = 3
    if n == None:
        n = WORLD // 3
    else:
        cols = WORLD // n
    deadline = min(7000, get_time() + 800)
    # 金币/Weird比为宫边长；另付创建、到位登记和并行超收的完整储备。
    required = (max(0, target - num_items(Items.Gold)) + n - 1) // n + 8 * n * MULT * DRONES + 2 * DRONES
    if not boost_stock({Items.Weird_Substance: required}):
        return False
    clear()
    start_stock = num_items(Items.Weird_Substance)
    jobs = []
    for index in range(DRONES):
        jobs.append((n, n // 2 + n * (index % cols), n // 2 + n * (index // cols)))

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


if __name__ == "__main__":
    lb_fastest_reset()
