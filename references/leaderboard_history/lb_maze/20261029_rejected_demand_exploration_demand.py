# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-demand-exploration/demand.py
def solve_one(n, bx, by, grid, mapped, blank):
    p = mapped
    graph = []
    walls = []
    for row in grid:
        graph.append(list(row))
        walls.append([])
    relocations = 0
    cost = n * MULT
    while num_items(Items.Gold) < TARGET_GOLD:
        target = measure()
        goal = (target[1] - by) * n + target[0] - bx
        remaining = []
        for side in walls[p]:
            if graph[p][side] != -1:
                continue
            if can_move(DIRS[side]):
                q = grid[p][side]
                graph[p][side] = q
                graph[q][BACK[side]] = p
            else:
                remaining.append(side)
        walls[p] = remaining
        while p != goal:
            path = optimistic_path(p, goal, graph, blank)
            if path == None:
                quick_print("maze_demand_failed", "no_path", p, goal)
                return relocations
            for side in path:
                q = grid[p][side]
                if not can_move(DIRS[side]):
                    graph[p][side] = -1
                    graph[q][BACK[side]] = -1
                    walls[p].append(side)
                    walls[q].append(BACK[side])
                    break
                if not move(DIRS[side]):
                    quick_print("maze_demand_failed", "move", p, side)
                    return relocations
                p = q
            if num_items(Items.Gold) >= TARGET_GOLD:
                return relocations
        if num_items(Items.Gold) >= TARGET_GOLD:
            return relocations
        if relocations >= REUSE_LIMIT:
            harvest()
            return relocations + 1
        if not use_item(Items.Weird_Substance, cost):
            quick_print("maze_demand_failed", "reuse", relocations)
            return relocations
        relocations += 1
    return relocations


def optimistic_path(start, goal, graph, blank):
    # 未知边先按可通，只删实测墙；初始树的真实边从未关闭，始终保留可达路径。
    previous = list(blank)
    directions = list(blank)
    previous[start] = start
    queue = [start]
    head = 0
    while head < len(queue) and previous[goal] == -1:
        p = queue[head]
        head += 1
        for side in range(4):
            q = graph[p][side]
            if q != -1 and previous[q] == -1:
                previous[q] = p
                directions[q] = side
                queue.append(q)
    if previous[goal] == -1:
        return None
    backward = []
    p = goal
    while p != start:
        backward.append(directions[p])
        p = previous[p]
    path = []
    for i in range(len(backward) - 1, -1, -1):
        path.append(backward[i])
    return path
