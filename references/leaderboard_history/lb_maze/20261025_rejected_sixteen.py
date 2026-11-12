from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-sixteen/lb_maze.py
# 45游戏秒方向组件；完整本地/短测/官方三值均未取得。
def lb_maze():
    clear()
    deadline = get_time() + 45
    handles = []
    for index in range(15):
        ox = (index % 4) * 8
        oy = (index // 4) * 8
        if not farm_goto(ox + 4, oy + 4):
            break
        def task():
            return controller(index, deadline)
        handle = spawn_drone(task)
        if handle == None:
            break
        handles.append(handle)
    if len(handles) == 15 and farm_goto(28, 28):
        local = controller(15, deadline)
    else:
        local = [False, False, 0, 0, 0]
    results = [local]
    for handle in handles:
        result = wait_for(handle)
        if result != None:
            results.append(result)
    quick_print("sixteen_done", get_time(), num_items(Items.Gold), results)


DIRS = [North, East, South, West]
VEC = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def home_for(index, code):
    x = ((code // 32) % 2) * 4 + ((code // 8) % 2) * 2 + ((code // 2) % 2)
    y = ((code // 16) % 2) * 4 + ((code // 4) % 2) * 2 + (code % 2)
    return ((index % 4) * 8 + (x + 2) % 8, (index // 4) * 8 + (y + 2 + 3 * (x // 4)) % 8)


def controller(index, deadline):
    def second():
        return initial_worker(index, 32, 32, deadline)
    handle = spawn_drone(second)
    if handle == None:
        return [False, False, 0, 1, 0]
    while not can_harvest() and get_time() < deadline:
        pass
    ready = harvest()
    while num_items(Items.Hay) < 16384 and get_time() < deadline:
        pass
    ok = ready and num_items(Items.Hay) >= 16384 and get_time() < deadline
    if ok:
        ok = plant(Entities.Bush)
    if ok:
        ok = use_item(Items.Weird_Substance, 256)
    if ok:
        graph = {}
        start = (get_pos_x(), get_pos_y())
        ok = explore(index, start, graph, deadline)
        if ok:
            local = solve(index, 0, 32, graph, start, deadline)
        else:
            local = [False, False, 0, 1, 0]
    else:
        local = [False, False, 0, 1, 0]
    other = wait_for(handle)
    merge_result(local, other)
    if local[1] and local[2] != 300:
        local[0] = False
    if local[0] and local[1]:
        # 只有本控制者收尾；所有后代和第二初始worker均已结束。
        before = num_items(Items.Gold)
        if get_entity_type() != Entities.Treasure or not harvest():
            local[0] = False
        elif num_items(Items.Gold) - before != 2048:
            local[0] = False
    quick_print("sixteen_maze", index, get_time(), local)
    return local


def initial_worker(index, code, width, deadline):
    home = home_for(index, code)
    if not farm_goto(home[0], home[1]):
        return [False, False, 0, 1, 0]
    while not can_harvest() and get_time() < deadline:
        pass
    if not harvest():
        return [False, False, 0, 1, 0]
    while get_entity_type() == Entities.Grass and get_time() < deadline:
        pass
    if get_time() >= deadline:
        return [True, False, 0, 1, 0]
    graph = {}
    if not explore(index, home, graph, deadline):
        return [False, False, 0, 1, 0]
    return solve(index, code, width, graph, home, deadline)


def merge_result(result, other):
    if other == None:
        result[0] = False
        result[1] = False
        return
    result[0] = result[0] and other[0]
    result[1] = result[1] and other[1]
    result[2] += other[2]
    result[3] += other[3]
    result[4] += other[4]


def offset(pos, direction):
    step = VEC[direction]
    return pos[0] + step[0], pos[1] + step[1]


def explore(index, pos, graph, deadline):
    graph[pos] = []
    ox = (index % 4) * 8
    oy = (index // 4) * 8
    for direction in range(4):
        neighbor = offset(pos, direction)
        if ox <= neighbor[0] < ox + 8 and oy <= neighbor[1] < oy + 8 and can_move(DIRS[direction]):
            graph[pos].append(direction)
            if neighbor not in graph:
                if get_time() >= deadline or not move(DIRS[direction]):
                    return False
                if not explore(index, neighbor, graph, deadline):
                    return False
                if not move(DIRS[(direction + 2) % 4]):
                    return False
    return True


def routes_from(graph, home):
    paths = {home: []}
    nodes = [home]
    for pos in nodes:
        for direction in graph[pos]:
            neighbor = offset(pos, direction)
            if neighbor not in paths:
                path = paths[pos][:]
                path.append(direction)
                paths[neighbor] = path
                nodes.append(neighbor)
    return paths


def scan(index, graph, pos):
    ox = (index % 4) * 8
    oy = (index // 4) * 8
    changed = 0
    for direction in range(4):
        neighbor = offset(pos, direction)
        if ox <= neighbor[0] < ox + 8 and oy <= neighbor[1] < oy + 8 and direction not in graph[pos]:
            if can_move(DIRS[direction]):
                graph[pos].append(direction)
                reverse = (direction + 2) % 4
                if reverse not in graph[neighbor]:
                    graph[neighbor].append(reverse)
                changed += 1
    return changed


def solve(index, code, width, graph, start, deadline):
    home = home_for(index, code)
    positioning = routes_from(graph, start)
    if home not in positioning or len(positioning) != 64:
        return [False, False, 0, 1, 0]
    for direction in positioning[home]:
        if get_time() >= deadline or not move(DIRS[direction]):
            return [False, False, 0, 1, 0]
    paths = routes_from(graph, home)
    handles = []
    result = [True, False, 0, 1, 0]
    while get_time() < deadline:
        treasure = measure()
        if treasure == None or treasure not in paths:
            result[0] = False
            break
        # 其他迷宫完成后释放的真实无人机槽，允许尚忙迷宫在本地补派。
        if width > 1 and num_drones() < 32:
            half = width // 2
            child_code = code + half
            def child():
                return solve(index, child_code, half, graph, home, deadline)
            handle = spawn_drone(child)
            if handle != None:
                width = half
                handles.append(handle)
        walked = []
        pos = home
        for direction in paths[treasure]:
            if get_time() >= deadline or measure() != treasure:
                break
            if not move(DIRS[direction]):
                result[0] = False
                break
            walked.append(direction)
            pos = offset(pos, direction)
        if not result[0]:
            break
        if pos == treasure and get_time() < deadline and measure() == treasure:
            paid = use_item(Items.Weird_Substance, 256)
            if paid:
                result[2] += 1
            elif measure() == treasure:
                result[1] = True
                break
        changed = 0
        for j in range(len(walked) - 1, -1, -1):
            changed += scan(index, graph, pos)
            direction = (walked[j] + 2) % 4
            if not move(DIRS[direction]):
                result[0] = False
                break
            pos = offset(pos, direction)
        if not result[0]:
            break
        changed += scan(index, graph, home)
        result[4] += changed
        if changed:
            paths = routes_from(graph, home)
    for handle in handles:
        merge_result(result, wait_for(handle))
    return result


def farm_goto(tx, ty):
    dx = (tx - get_pos_x()) % 32
    direction = East
    if dx > 16:
        dx = 32 - dx
        direction = West
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % 32
    direction = North
    if dy > 16:
        dy = 32 - dy
        direction = South
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_maze()
