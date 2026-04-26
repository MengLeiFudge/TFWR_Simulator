from __builtins__ import *


# 单无人机迷宫候选：一次 DFS 全探图 + 每次单源 BFS 寻宝。
# 目标是替代旧 A* 的 open_set 扫描、path 深拷贝和渐进置信探图成本。

clear()
size = get_world_size()
for _ in range(size // 2):
    move(North)
    move(East)

plant(Entities.Bush)
substance = size * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
use_item(Items.Weird_Substance, substance)

directions = [North, East, South, West]
backs = {North: South, East: West, South: North, West: East, None: None}
dx = {North: 0, East: 1, South: 0, West: -1}
dy = {North: 1, East: 0, South: -1, West: 0}
explore_steps = 0
bfs_count = 0
bfs_nodes = 0


def maze_index(x, y):
    return x + y * size


def in_maze(x, y):
    return x >= 0 and y >= 0 and x < size and y < size


def add_edge(graph, source, target, direction):
    for edge in graph[source]:
        if edge[0] == target:
            return
    graph[source].append([target, direction])


def refresh_current_edges(graph):
    x = get_pos_x()
    y = get_pos_y()
    source = maze_index(x, y)
    for direction in directions:
        nx = x + dx[direction]
        ny = y + dy[direction]
        if not in_maze(nx, ny):
            continue
        if can_move(direction):
            target = maze_index(nx, ny)
            add_edge(graph, source, target, direction)
            add_edge(graph, target, source, backs[direction])


def explore_maze(graph, visited, entered_from):
    global explore_steps
    x = get_pos_x()
    y = get_pos_y()
    current = maze_index(x, y)
    if visited[current]:
        return

    visited[current] = True
    open_dirs = []
    for direction in directions:
        nx = x + dx[direction]
        ny = y + dy[direction]
        if not in_maze(nx, ny):
            continue
        if can_move(direction):
            target = maze_index(nx, ny)
            add_edge(graph, current, target, direction)
            add_edge(graph, target, current, backs[direction])
            open_dirs.append(direction)

    back = backs[entered_from]
    for direction in open_dirs:
        if direction == back:
            continue
        nx = get_pos_x() + dx[direction]
        ny = get_pos_y() + dy[direction]
        if not in_maze(nx, ny):
            continue
        target = maze_index(nx, ny)
        if visited[target]:
            continue
        move(direction)
        explore_steps = explore_steps + 1
        explore_maze(graph, visited, direction)
        move(backs[direction])
        explore_steps = explore_steps + 1


def move_with_bfs(tx, ty, graph):
    global bfs_count
    global bfs_nodes
    global bfs_stamp
    start = maze_index(get_pos_x(), get_pos_y())
    target = maze_index(tx, ty)
    if start == target:
        return True

    bfs_stamp = bfs_stamp + 1
    bfs_queue[0] = start
    bfs_seen[start] = bfs_stamp
    bfs_previous[start] = start
    head = 0
    tail = 1
    bfs_count = bfs_count + 1
    while head < tail:
        current = bfs_queue[head]
        head = head + 1
        bfs_nodes = bfs_nodes + 1
        for edge in graph[current]:
            neighbor = edge[0]
            if bfs_seen[neighbor] == bfs_stamp:
                continue
            bfs_seen[neighbor] = bfs_stamp
            bfs_previous[neighbor] = current
            bfs_previous_direction[neighbor] = edge[1]
            if neighbor == target:
                head = tail
                break
            bfs_queue[tail] = neighbor
            tail = tail + 1

    if bfs_seen[target] != bfs_stamp:
        return False

    path_length = 0
    current = target
    while current != start:
        bfs_path[path_length] = bfs_previous_direction[current]
        path_length = path_length + 1
        current = bfs_previous[current]

    while path_length > 0:
        path_length = path_length - 1
        direction = bfs_path[path_length]
        if not can_move(direction):
            refresh_current_edges(graph)
            return False
        move(direction)
        refresh_current_edges(graph)
    return True


def goto_treasure(graph):
    target = measure()
    if target == None:
        return False
    tx = target[0]
    ty = target[1]
    while get_pos_x() != tx or get_pos_y() != ty:
        if not move_with_bfs(tx, ty, graph):
            return False
    return True


graph = []
visited = []
for _ in range(size * size):
    graph.append([])
    visited.append(False)

bfs_stamp = 0
bfs_seen = []
bfs_previous = []
bfs_previous_direction = []
bfs_queue = []
bfs_path = []
for _ in range(size * size):
    bfs_seen.append(0)
    bfs_previous.append(-1)
    bfs_previous_direction.append(None)
    bfs_queue.append(0)
    bfs_path.append(None)

start_time = get_time()
explore_maze(graph, visited, None)
explore_done_time = get_time()
quick_print("maze_single_dfs", "explore_time=", explore_done_time - start_time, "steps=", explore_steps)

while True:
    if goto_treasure(graph):
        use_item(Items.Weird_Substance, substance)
        if get_entity_type() == Entities.Treasure:
            harvest()
            break
    else:
        refresh_current_edges(graph)
        for _ in range(size):
            if get_entity_type() == Entities.Treasure:
                harvest()
                break
            move(North)
            refresh_current_edges(graph)
        if get_entity_type() == Entities.Treasure:
            break
        move(East)
        refresh_current_edges(graph)

quick_print("maze_single_dfs", "total_time=", get_time() - start_time, "bfs=", bfs_count, "nodes=", bfs_nodes)
