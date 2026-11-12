# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-station-team/station.fragment.py
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
    if not ensure_power(1200):
        return False
    size = get_world_size()
    multiplier = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    unit = size * multiplier
    gain = size * size * multiplier
    while num_items(Items.Gold) < 1000000:
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
