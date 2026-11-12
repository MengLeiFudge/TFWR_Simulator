# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-parallel-stations/explore.fragment.py
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
