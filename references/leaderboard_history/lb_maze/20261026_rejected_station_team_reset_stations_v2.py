from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-station-team/lb_reset_stations_v2.py
# 私有Expand7全链路16×16候选：完整Reset时间未验证。
def lb_reset_directed():
    step1()
    quick_print("directed", "step1", get_time(), num_items(Items.Hay), num_items(Items.Wood))
    plan = [Unlocks.Speed, Unlocks.Expand, Unlocks.Trees, Unlocks.Speed,
            Unlocks.Grass, Unlocks.Trees, Unlocks.Grass, Unlocks.Carrots,
            Unlocks.Expand, Unlocks.Watering, Unlocks.Fertilizer, Unlocks.Sunflowers]
    for technology in plan:
        if not buy(technology):
            return
    if not solar_reserve():
        return
    for technology in [Unlocks.Trees, Unlocks.Grass, Unlocks.Carrots,
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
        ready = 0
        rounds = 0
        while ready < size * size:
            if get_time() > 7000 or rounds >= 300:
                return False
            ready = 0
            for x in range(size):
                for y in range(size):
                    kind = get_entity_type()
                    if kind != Entities.Pumpkin and kind != Entities.Dead_Pumpkin:
                        if kind != None:
                            harvest()
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if get_entity_type() != Entities.Pumpkin:
                        if not affordable(get_cost(Entities.Pumpkin)):
                            quick_print("directed_failed", "pumpkin_material", get_time())
                            return False
                        if not plant(Entities.Pumpkin):
                            return False
                    if can_harvest():
                        ready += 1
                    move(North)
                move(East)
            rounds += 1
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
    for technology in [Unlocks.Speed, Unlocks.Speed]:
        if not buy(technology):
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
    rounds = 0
    expected = 0
    for x in range(start, size, stride):
        expected += size
    while rounds < 300 and get_time() < 7000:
        ready = 0
        for x in range(start, size, stride):
            go(x, 0)
            for y in range(size):
                kind = get_entity_type()
                if kind != None and kind != Entities.Grass and kind != Entities.Pumpkin and kind != Entities.Dead_Pumpkin:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if get_entity_type() != Entities.Pumpkin:
                    if not affordable(get_cost(Entities.Pumpkin)) or not plant(Entities.Pumpkin):
                        return False
                if can_harvest():
                    ready += 1
                elif get_water() < 0.5 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
                move(North)
        if ready == expected:
            return True
        rounds += 1
    return False


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
    target_gold = get_cost(Unlocks.Megafarm)[Items.Gold]
    count = (max(0, target_gold - num_items(Items.Gold)) + size * size - 1) // (size * size)
    if count > 299:
        return False
    if not boost_stock({Items.Weird_Substance: size * (count + 1)}, True):
        return False
    clear()
    if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, size):
        return False
    graph = build_maze_graph(size)
    for _ in range(count + 2):
        if get_time() > 7000:
            return False
        target = measure()
        if target == None or not goto_treasure_with_graph(target[0], target[1], size, graph):
            return False
        if not use_item(Items.Weird_Substance, size):
            return False
        if num_items(Items.Gold) >= target_gold:
            clear()
            if not unlock(Unlocks.Megafarm):
                return False
            quick_print("directed_megafarm", get_time(), max_drones(), num_items(Items.Power), num_items(Items.Fertilizer), num_items(Items.Weird_Substance))
            return True
    return False


def eight_drones():
    if not buy(Unlocks.Fertilizer):
        return False
    if not buy(Unlocks.Pumpkins) or not buy(Unlocks.Expand):
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
    return next_megafarm()


def cactus_worker_supply(start, stride, phase, deadline):
    size = get_world_size()
    for line in range(start, size, stride):
        if get_time() > deadline:
            return False
        if phase == 0:
            go(line, 0)
            for _ in range(size):
                if get_ground_type() != Grounds.Soil:
                    till()
                if not affordable(get_cost(Entities.Cactus)) or not plant(Entities.Cactus):
                    return False
                if not move(North):
                    return False
            # 每轮真实闭合巡回；四轮已超过已核对的一秒成熟上界。
            mature = False
            for _ in range(4):
                ready = 0
                for _ in range(size):
                    if can_harvest():
                        ready += 1
                    if not move(North):
                        return False
                if ready == size:
                    mature = True
                    break
            if not mature or not sort_cactus_line(North, South, deadline):
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
    # Expand7的64000 Pumpkin走原真实供料，不借后期库存。
    if not buy(Unlocks.Expand):
        return False
    quick_print("directed_expand16", get_time(), get_world_size(), num_items(Items.Power), num_items(Items.Pumpkin))
    if not ensure_power(1200):
        return False
    if not buy(Unlocks.Cactus) or not buy(Unlocks.Cactus):
        return False
    # M1→4=516000；D0→4=518000；13轮满尾苹果29744及最终告警储备。
    if not cactus_stock(1064000):
        return False
    for technology in [Unlocks.Mazes, Unlocks.Mazes, Unlocks.Mazes,
                       Unlocks.Dinosaurs, Unlocks.Dinosaurs, Unlocks.Dinosaurs, Unlocks.Dinosaurs]:
        if not buy(technology):
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
    size = get_world_size()
    multiplier = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    unit = size * multiplier
    gain = size * size * multiplier
    while num_items(Items.Gold) < 1000000:
        if not ensure_power(2000):
            return False
        count = min(299, (1000000 - num_items(Items.Gold) + gain - 1) // gain)
        target_gold = num_items(Items.Gold) + count * gain
        if not boost_stock({Items.Weird_Substance: unit * (count + 1)}, True):
            return False
        clear()
        if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, unit):
            return False
        graph = build_maze_graph(size)
        if not maze_team(graph, size, min(max_drones(), 8), target_gold, unit, min(7000, get_time() + 800)):
            quick_print("directed_failed", "station_gold", get_time(), num_items(Items.Gold))
            return False
        clear()
        quick_print("directed_gold", get_time(), num_items(Items.Gold), num_items(Items.Power), num_items(Items.Fertilizer))
    return True





def finish_bones():
    if not ensure_power(2200):
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

def build_dinosaur_path(size):
    # 构造安全兜底路径：前期追苹果失败或尾巴变长后，沿这条路径继续吃满。
    path = []
    for _ in range(size):
        path.append([])
        for _ in range(size):
            path[-1].append(None)

    for x in range(size - 1):
        path[x][0] = East
    path[-1][0] = North

    line = size - 1
    for _ in range(size // 2):
        for y in range(1, size - 1):
            path[line][y] = North
        path[line][-1] = West
        line = line - 1
        for y in range(2, size):
            path[line][y] = South
        path[line][1] = West
        line = line - 1
    path[0][1] = South
    return path

def run_dinosaur_chase_loop(size):
    # 复用恐龙榜策略：先按 measure() 追苹果，尽早触发 3% 移动降本，再切回安全路径。
    path = build_dinosaur_path(size)
    state = [get_pos_x(), get_pos_y(), 0, 0, 1, 0]
    measured = measure()
    if measured:
        state[2] = measured[0]
        state[3] = measured[1]

    def update_and_move(direction):
        if direction == None:
            return False
        if not can_move(direction):
            return False
        move(direction)
        state[5] = state[5] + 1
        measured_pos = measure()
        if measured_pos:
            state[2] = measured_pos[0]
            state[3] = measured_pos[1]
            state[4] = state[4] + 1
        state[0] = get_pos_x()
        state[1] = get_pos_y()
        return True

    while state[4] < size * size / 3:
        state[5] = 0
        while state[5] < state[4]:
            if not update_and_move(path[state[0]][state[1]]):
                return
        while state[0] < state[2]:
            if not update_and_move(East):
                return
        while state[1] == 0:
            if state[0] % 2 == 0:
                if not update_and_move(East):
                    return
            else:
                if not update_and_move(North):
                    return
        while state[0] >= state[2]:
            target_x = state[2]
            target_y = state[3]
            if target_y == 0:
                break
            while state[1] < target_y:
                if can_move(North):
                    if not update_and_move(North):
                        return
                else:
                    if not update_and_move(West):
                        return
                    if state[0] == 0:
                        break
            if state[0] == 0:
                break
            while state[1] > target_y:
                if can_move(South):
                    if not update_and_move(South):
                        return
                else:
                    if not update_and_move(West):
                        return
                    if state[0] == 0:
                        break
            if state[0] == 0:
                break
            while state[0] > target_x:
                if not update_and_move(West):
                    return
                if state[0] == 0:
                    break
            if state[0] == 0:
                break
        while state[0] > 0:
            if not update_and_move(West):
                return
        while state[1] > 0:
            if not update_and_move(South):
                return

    while True:
        direction = path[state[0]][state[1]]
        if direction == None or not can_move(direction):
            return
        move(direction)
        state[0] = get_pos_x()
        state[1] = get_pos_y()

if __name__ == "__main__":
    lb_reset_directed()
