# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-branch-team/team.py
def branch_map(p, previous, back, grid, allow_fork):
    records = []
    handles = []
    def visit(p, previous, back):
        row = [-1, -1, -1, -1]
        closed = []
        children = []
        for d in range(4):
            q = grid[p][d]
            if q == -1:
                continue
            if q == previous or can_move(DIRS[d]):
                row[d] = q
                if q != previous:
                    children.append((q, d))
            else:
                closed.append(d)
        records.append((p, previous, back, row, closed))
        # 尚未搬迁的初始迷宫是树；去掉父边后，各子枝不相交。
        for q, d in children:
            forked = False
            if allow_fork and not handles and len(children) > 1:
                handle = spawn_drone(enter_branch, q, p, d, grid)
                if handle != None:
                    handles.append(handle)
                    forked = True
            if not forked:
                move(DIRS[d])
                visit(q, p, BACK[d])
                move(DIRS[BACK[d]])
    visit(p, previous, back)
    for handle in handles:
        for record in wait_for(handle):
            records.append(record)
    return records


def enter_branch(p, previous, direction, grid):
    move(DIRS[direction])
    return branch_map(p, previous, BACK[direction], grid, False)


def explore(n, grid, home):
    started = get_time()
    records = branch_map(home, -1, -1, grid, True)
    links = []
    walls = []
    parent = []
    up_hop = []
    down_hop = []
    for _ in range(n * n):
        links.append(None)
        walls.append(None)
        parent.append(-1)
        up_hop.append(None)
        down_hop.append(None)
    order = []
    for p, previous, back, row, closed in records:
        if links[p] != None:
            quick_print("maze_branch_failed", "duplicate", p)
            return None
        links[p] = row
        walls[p] = closed
        parent[p] = previous
        if previous != -1:
            up_hop[p] = (previous, DIRS[back])
            down_hop[p] = (p, DIRS[BACK[back]])
        order.append(p)
    if len(order) != n * n:
        quick_print("maze_branch_failed", "coverage", len(order))
        return None
    quick_print("branch_map", get_pos_x(), get_pos_y(), len(order), get_time() - started)
    return home, links, walls, (parent, up_hop, down_hop, order)


def choose_stations(routes):
    # 用树直径的四分点，不枚举中心组合；所有格的归属在开墙前固定。
    a = 0
    for p in range(len(routes)):
        if routes[0][0][p] > routes[0][0][a]:
            a = p
    b = a
    for p in range(len(routes)):
        if routes[a][0][p] > routes[a][0][b]:
            b = p
    length = routes[a][0][b]
    path = [b]
    p = b
    for _ in range(length):
        p, direction = routes[a][1][p]
        path.append(p)
    stations = [path[length // 4], path[(3 * length) // 4]]
    owners = []
    for p in range(len(routes)):
        owner = 0
        if routes[stations[1]][0][p] < routes[stations[0]][0][p]:
            owner = 1
        owners.append(owner)
    return stations, owners


def solve_one(n, bx, by, grid, mapped, blank):
    p, links, walls, tree = mapped
    started = get_time()
    routes = build_all_routes(tree, blank)
    stations, owners = choose_stations(routes)
    quick_print("branch_plan", bx, by, stations, get_time() - started)
    def partner():
        return serve(n, bx, by, grid, p, links, walls, routes, 1, stations, owners)
    handle = spawn_drone(partner)
    if handle == None:
        return None
    left, local_ok = serve(n, bx, by, grid, p, links, walls, routes, 0, stations, owners)
    right, other_ok = wait_for(handle)
    if not local_ok or not other_ok:
        return None
    return left + right
