from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-single-owner/root-overflow/lb_maze.py

# 私有合规候选：完整轮时间尚未取得。
def lb_maze():
    run_deadline = get_time() + 180
    clear()
    set_world_size(32)
    size = get_world_size()
    size_max = size - 1
    size_half = size_max // 2
    size_31 = size_max // 3
    size_32 = size_max - size_31
    maze_substance = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    maze_map = []
    explore_visited = set()

    local_dirs = [North, East, South, West]
    dir_to_pos = {North: (0, 1), East: (1, 0), South: (0, -1), West: (-1, 0)}
    back_dir = {North: South, East: West, South: North, West: East, None: None}

    def current_pos():
        return get_pos_x(), get_pos_y()

    def pos_move(pos, direction):
        x, y = pos
        dx, dy = dir_to_pos[direction]
        return x + dx, y + dy

    def relative_dir(pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        if x1 == x2:
            if y2 > y1:
                return North
            if y2 < y1:
                return South
        if y1 == y2:
            if x2 > x1:
                return East
            if x2 < x1:
                return West
        return None

    def move_to(pos):
        x, y = pos
        dx = x - get_pos_x()
        if abs(dx) > size // 2:
            if dx > 0:
                for _ in range(size - dx):
                    move(West)
            else:
                for _ in range(size + dx):
                    move(East)
        elif dx < 0:
            for _ in range(-dx):
                move(West)
        elif dx > 0:
            for _ in range(dx):
                move(East)

        dy = y - get_pos_y()
        if abs(dy) > size // 2:
            if dy > 0:
                for _ in range(size - dy):
                    move(South)
            else:
                for _ in range(size + dy):
                    move(North)
        elif dy < 0:
            for _ in range(-dy):
                move(South)
        elif dy > 0:
            for _ in range(dy):
                move(North)

    def wait_spawn(task, label):
        drone = spawn_drone(task)
        tries = 0
        while not drone and tries < 200:
            tries += 1
            drone = spawn_drone(task)
        if not drone:
            quick_print("maze_multi spawn_failed", label)
        return drone

    def check_new_path(paths):
        pos = current_pos()
        for direction in local_dirs:
            if can_move(direction):
                moved_pos = pos_move(pos, direction)
                edge = (pos, moved_pos)
                if edge not in paths:
                    paths.add(edge)

    def explore_maze(start_pos, sub_drone_pos):
        def _explore_maze(curr_dir):
            pos = current_pos()
            explore_visited.add(pos)
            x, y = pos
            back = back_dir[curr_dir]
            paths = []
            sub_drones = []
            while get_ground_type() == Grounds.Grassland:
                first_dir = None
                other_dirs = []
                for direction in local_dirs:
                    moved_pos = pos_move(pos, direction)
                    if can_move(direction):
                        paths.append((pos, moved_pos))
                    if direction == back:
                        continue
                    if can_move(direction) and moved_pos not in explore_visited:
                        if first_dir == None:
                            first_dir = direction
                        else:
                            other_dirs.append(direction)
                if first_dir == None:
                    break

                for branch_dir in other_dirs:
                    def make_branch_task(direction, branch_x, branch_y):
                        def branch_task():
                            if branch_x == size_31 or branch_x == size_32 or branch_y == size_31 or branch_y == size_32:
                                till()
                            move(direction)
                            return _explore_maze(direction)
                        return branch_task

                    drone = wait_spawn(make_branch_task(branch_dir, x, y), "explore_branch")
                    if drone:
                        sub_drones.append(drone)

                if x == size_31 or x == size_32 or y == size_31 or y == size_32:
                    till()
                move(first_dir)
                back = back_dir[first_dir]
                pos = current_pos()
                x, y = pos
                explore_visited.add(pos)

            active_drones = []
            for drone in sub_drones:
                if has_finished(drone):
                    data, sub_sub_drones = wait_for(drone)
                    for path in data:
                        paths.append(path)
                    for sub_drone in sub_sub_drones:
                        active_drones.append(sub_drone)
                else:
                    active_drones.append(drone)
            return paths, active_drones

        def sub_task(pos):
            def _sub_task():
                move_to(pos)
                wait_start = get_time()
                while get_entity_type() == Entities.Grass:
                    if get_time() - wait_start > 1000:
                        quick_print("maze_multi wait_maze_timeout", pos)
                        return [], []
                return _explore_maze(None)
            return _sub_task

        def root_task():
            return _explore_maze(None)

        sub_drones = set()
        for pos in sub_drone_pos:
            drone = wait_spawn(sub_task(pos), "explore_seed")
            if drone:
                sub_drones.add(drone)

        move_to(start_pos)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, maze_substance)
        drone = wait_spawn(root_task, "explore_root")
        if drone:
            sub_drones.add(drone)

        for _ in range(size):
            maze_map.append([])
            for _ in range(size):
                maze_map[-1].append(set())

        last_progress_time = get_time()
        while sub_drones:
            to_add = set()
            to_remove = set()
            for drone in sub_drones:
                if has_finished(drone):
                    paths, sub_sub_drones = wait_for(drone)
                    for path in paths:
                        (x, y), neighbor = path
                        if 0 <= x < size and 0 <= y < size:
                            maze_map[x][y].add(neighbor)
                    to_remove.add(drone)
                    for sub_drone in sub_sub_drones:
                        to_add.add(sub_drone)
            if to_remove or to_add:
                last_progress_time = get_time()
            for drone in to_remove:
                sub_drones.remove(drone)
            for drone in to_add:
                sub_drones.add(drone)
            if get_time() - last_progress_time > 1000:
                quick_print("maze_multi explore_stall active=", len(sub_drones))
                break
        quick_print("maze_multi explore_done time=", get_time())

    def k_center_on_tree(root, k=32):
        return 14

    def solve_maze_in_area(center, area, radius, owned_set):
        path = {center: []}
        reverse_path = {center: []}
        nodes = [center]
        for node in nodes:
            x, y = node
            for neighbor in maze_map[x][y]:
                if neighbor in area and neighbor not in path:
                    path[neighbor] = []
                    for direction in path[node]:
                        path[neighbor].append(direction)
                    path[neighbor].append(relative_dir(node, neighbor))
                    reverse_path[neighbor] = [relative_dir(neighbor, node)]
                    for direction in reverse_path[node]:
                        reverse_path[neighbor].append(direction)
                    nodes.append(neighbor)

        hits = 0
        while get_time() < run_deadline:
            treasure = measure()
            while treasure not in owned_set:
                if treasure == None or num_items(Items.Gold) >= target_gold_count:
                    quick_print("maze_owner done", center, hits, get_time())
                    return True
                if get_time() >= run_deadline:
                    quick_print("maze_owner failed", "wait_deadline", center)
                    return False
                # 支付正常换帽的200tick再查询，降低闲机空转；不改实体或负责权。
                change_hat(Hats.Straw_Hat)
                treasure = measure()
            # 负责集合互斥；只有本机可以修改这个宝藏，路线期间它不会被别人推进。
            for direction in path[treasure]:
                if not move(direction):
                    quick_print("maze_owner failed", "outbound", center, treasure)
                    return False
            if measure() != treasure or get_entity_type() != Entities.Treasure:
                quick_print("maze_owner failed", "ownership", center, treasure)
                return False
            # 300次标准重定位后，唯一负责机只执行一次最终收割并返回。
            if num_items(Items.Gold) == target_gold_count - 32768:
                if not harvest():
                    quick_print("maze_owner failed", "final_harvest", center)
                    return False
                quick_print("maze_owner final", center, hits, get_time())
                return True
            if not use_item(Items.Weird_Substance, maze_substance):
                quick_print("maze_owner failed", "reuse", center, num_items(Items.Gold))
                return False
            hits += 1
            for direction in reverse_path[treasure]:
                if not move(direction):
                    quick_print("maze_owner failed", "return", center)
                    return False
        quick_print("maze_owner failed", "deadline", center)
        return False

    def complete_map(center):
        # 探图器配额不足时可能漏分支；把已知边双向补齐，再实际探测未知格的边界。
        for x in range(size):
            for y in range(size):
                for nx, ny in list(maze_map[x][y]):
                    maze_map[nx][ny].add((x, y))
        checked = set()
        repaired = 0
        while get_time() < run_deadline:
            pos = current_pos()
            parent = {pos: None}
            incoming = {}
            nodes = [pos]
            for node in nodes:
                x, y = node
                for neighbor in maze_map[x][y]:
                    if neighbor not in parent:
                        parent[neighbor] = node
                        incoming[neighbor] = relative_dir(node, neighbor)
                        nodes.append(neighbor)
            if len(nodes) == size * size:
                route = []
                node = center
                while parent[node] != None:
                    route.append(incoming[node])
                    node = parent[node]
                for i in range(len(route) - 1, -1, -1):
                    if not move(route[i]):
                        quick_print("maze_owner failed", "repair_return")
                        return False
                quick_print("maze_owner map_complete", len(nodes), repaired, get_time())
                return True
            frontier = None
            for node in nodes:
                for direction in local_dirs:
                    neighbor = pos_move(node, direction)
                    nx, ny = neighbor
                    if 0 <= nx < size and 0 <= ny < size and neighbor not in parent and (node, neighbor) not in checked:
                        frontier = (node, neighbor, direction)
                        break
                if frontier != None:
                    break
            if frontier == None:
                quick_print("maze_owner failed", "repair_frontier", len(nodes))
                return False
            target, neighbor, direction = frontier
            route = []
            node = target
            while parent[node] != None:
                route.append(incoming[node])
                node = parent[node]
            for i in range(len(route) - 1, -1, -1):
                if not move(route[i]):
                    quick_print("maze_owner failed", "repair_route")
                    return False
            checked.add((target, neighbor))
            if can_move(direction):
                if not move(direction):
                    quick_print("maze_owner failed", "repair_cross")
                    return False
                x, y = target
                nx, ny = neighbor
                maze_map[x][y].add(neighbor)
                maze_map[nx][ny].add(target)
                repaired += 1
        quick_print("maze_owner failed", "repair_deadline")
        return False

    def maze_chunking(root, radius):
        node_parent = {root: None}
        nodes = [root]
        for node in nodes:
            x, y = node
            for neighbor in maze_map[x][y]:
                if neighbor not in node_parent:
                    nodes.append(neighbor)
                    node_parent[neighbor] = node

        def task(center, area, owned_set):
            def _task():
                path_to_center = []
                node = center
                while node_parent[node]:
                    path_to_center.append(relative_dir(node_parent[node], node))
                    node = node_parent[node]
                for i in range(len(path_to_center) - 1, -1, -1):
                    move(path_to_center[i])
                return solve_maze_in_area(center, area, radius, owned_set)
            return _task

        covered = set()
        solver_drones = []
        root_owned = set()
        for i in range(len(nodes) - 1, -1, -1):
            node = nodes[i]
            if node in covered:
                continue
            for _ in range(radius):
                if node_parent[node] == None:
                    break
                node = node_parent[node]
            center = node
            node_set = set()
            node_set.add(node)
            owned_set = set()
            node_dist = {node: 0}
            node_queue = [node]
            for current in node_queue:
                if current not in covered:
                    owned_set.add(current)
                covered.add(current)
                node_set.add(current)
                x, y = current
                if node_dist[current] < radius:
                    for neighbor in maze_map[x][y]:
                        if neighbor not in node_dist:
                            node_dist[neighbor] = node_dist[current] + 1
                            node_queue.append(neighbor)
            if not owned_set:
                continue
            drone = spawn_drone(task(center, node_set, owned_set))
            if drone:
                solver_drones.append(drone)
            else:
                for position in owned_set:
                    root_owned.add(position)

        quick_print("maze_multi nodes=", len(nodes))
        quick_print("maze_owner assigned", len(covered), len(solver_drones), len(root_owned))
        solve_start_time = get_time()
        # 分区必须全部分配后才处理主机任务；容量不足不能阻塞剩余区域的负责权分配。
        if root_owned:
            if not solve_maze_in_area(root, set(nodes), radius, root_owned):
                quick_print("maze_owner failed", "root_worker")
        last_gold = num_items(Items.Gold)
        last_progress_time = get_time()
        while solver_drones and num_items(Items.Gold) < target_gold_count:
            active = []
            for drone in solver_drones:
                if has_finished(drone):
                    if not wait_for(drone):
                        quick_print("maze_owner failed", "worker")
                else:
                    active.append(drone)
            solver_drones = active
            current_gold = num_items(Items.Gold)
            if current_gold != last_gold:
                last_gold = current_gold
                last_progress_time = get_time()
                quick_print("maze_multi gold=", current_gold, "time=", get_time())
            if get_time() - last_progress_time > 1000:
                quick_print("maze_multi solve_stall gold=", current_gold, "active=", len(solver_drones))
                break
            change_hat(Hats.Straw_Hat)
        for drone in solver_drones:
            if not wait_for(drone):
                quick_print("maze_owner failed", "final_worker")
        quick_print("maze_multi solve_done gold=", num_items(Items.Gold), "time=", get_time(), "solve_time=", get_time() - solve_start_time)

    center = (size_half, size_half)
    explore_maze(center, [
        (0, size_max), (size_half, size_max), (size_max, size_max),
        (0, size_half), (size_max, size_half),
        (0, 0), (size_half, 0), (size_max, 0),
    ])
    if not complete_map(center):
        return
    radius = k_center_on_tree(center)
    maze_chunking(center, radius)


target_gold_count = 9863168


if __name__ == "__main__":
    lb_maze()
