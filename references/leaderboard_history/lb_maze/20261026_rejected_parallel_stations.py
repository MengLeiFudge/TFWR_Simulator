from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-parallel-stations/lb_maze.py
# 私有Maze多机并行初图与最近驻点；完整时间待验证。
def lb_maze():
    clear()
    size = get_world_size()
    unit = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, unit):
        return
    deadline = get_time() + 160
    graph = parallel_maze_graph(size, deadline)
    if graph == None:
        return
    target_gold = num_items(Items.Gold) + 300 * size * unit
    if not maze_team(graph, size, min(32, max_drones()), target_gold, unit, deadline):
        quick_print("station_failed", "service", get_time(), num_items(Items.Gold))
        return
    target = measure()
    if target == None or not goto_treasure_with_graph(target[0], target[1], size, graph) or not harvest():
        quick_print("station_failed", "final_harvest", get_time())
        return
    quick_print("station_done", get_time(), num_items(Items.Gold))

# 初图无环且本阶段不兑现宝藏；每个叉口分支只有一个递归写者。
def explore_tree(entry, size, deadline):
    directions = [North, East, South, West]
    reverse = {North: South, East: West, South: North, West: East}
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]
    edges = []
    handles = []
    frames = []
    nodes = 0
    success = True
    back = None
    if entry != None:
        if not move(entry):
            return False, edges, nodes
        back = reverse[entry]
    entering = True
    while entering or frames:
        if get_time() >= deadline:
            success = False
            break
        if entering:
            x = get_pos_x()
            y = get_pos_y()
            node = x + y * size
            nodes += 1
            exits = []
            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < size and 0 <= ny < size and can_move(directions[i]):
                    edges.append((node, nx + ny * size, directions[i]))
                    if directions[i] != back:
                        exits.append(directions[i])
            pending = []
            if exits:
                pending.append(exits[0])
            for i in range(1, len(exits)):
                handle = spawn_drone(explore_tree, exits[i], size, deadline)
                if handle == None:
                    pending.append(exits[i])
                else:
                    handles.append(handle)
            frames.append([back, pending, 0])
            entering = False
        frame = frames[-1]
        if frame[2] < len(frame[1]):
            direction = frame[1][frame[2]]
            frame[2] += 1
            if not move(direction):
                success = False
                break
            back = reverse[direction]
            entering = True
        else:
            back = frame[0]
            frames.pop()
            if back != None and not move(back):
                success = False
                break
    for handle in handles:
        result = wait_for(handle)
        if result == None or not result[0]:
            success = False
        if result != None:
            for edge in result[1]:
                edges.append(edge)
            nodes += result[2]
    return success, edges, nodes


def parallel_maze_graph(size, deadline):
    result = explore_tree(None, size, deadline)
    if not result[0] or result[2] != size * size or len(result[1]) != 2 * (size * size - 1):
        quick_print("station_failed", "initial_tree", get_time(), result[2], len(result[1]))
        return None
    graph = []
    for _ in range(size * size):
        graph.append([])
    for edge in result[1]:
        graph[edge[0]].append([edge[1], edge[2]])
    quick_print("station_graph", get_time(), result[2], len(result[1]))
    return graph


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

    # 标签只会减小；懒删除桶以O(实际松弛次数)维护最远未覆盖节点。
    closest = []
    owners = []
    buckets = []
    for _ in range(size * size + 1):
        buckets.append([])
    for _ in range(size * size):
        closest.append(size * size)
        owners.append(-1)
    centers = []
    peak = size * size
    center = 0
    for worker in range(workers):
        if worker > 0:
            found = False
            while peak >= 0 and not found:
                while buckets[peak]:
                    candidate = buckets[peak].pop()
                    if closest[candidate] == peak:
                        center = candidate
                        found = True
                        break
                if not found:
                    peak -= 1
            if not found:
                return False
        centers.append(center)
        closest[center] = 0
        owners[center] = worker
        queue = [center]
        for current in queue:
            for edge in graph[current]:
                neighbor = edge[0]
                if closest[neighbor] > closest[current] + 1:
                    closest[neighbor] = closest[current] + 1
                    owners[neighbor] = worker
                    buckets[closest[neighbor]].append(neighbor)
                    queue.append(neighbor)
    quick_print("station_planned", get_time(), len(centers), peak)

    def serve(worker):
        center = centers[worker]
        dist, parent, incoming = distances(center)
        node = 0
        while node != center:
            if not move(reverse[incoming[node]]):
                return False
            node = parent[node]
        quick_print("station_positioned", worker, get_time(), center)
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

if __name__ == "__main__":
    lb_maze()
