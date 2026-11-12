# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/github-strategy-search/enihsyou/maze.py
s = get_world_size()

INF_METRIC = 999999
DIRECTIONS = [North, East, South, West]
OPPOSITES = {
    North: South,
    South: North,
    East: West,
    West: East,
}
RELATIVE = {
    North: (0, 1),
    South: (0, -1),
    East: (1, 0),
    West: (-1, 0),
}

MULTIPLIER = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
# 迷宫大小
MSIZE = 8
# 需要的 Weird_Substance 数量
COSTS = MSIZE * MULTIPLIER
# 能获得的 Gold 数量
GOLDS = MSIZE * COSTS


def wrapper2(fn, arg0, arg1):
    def wrapped():
        return fn(arg0, arg1)

    return wrapped


def scan_maze(maze, direction):
    if direction == None:
        backwards = None
    else:
        backwards = OPPOSITES[direction]
    if direction != None:
        move(direction)

    walls = set()
    searchable = []
    for dir in DIRECTIONS:
        if dir != backwards:
            if can_move(dir):
                searchable.append(dir)
            else:
                walls.add(dir)

    maze[get_pos_x(), get_pos_y()] = walls
    for dir in searchable:
        scan_maze(maze, dir)

    if backwards != None:
        move(backwards)

    return maze


def plot_flow_field(maze, dist_to_base, path_to_base, base):
    # use two stacks to simulate a queue, because pop() is faster than pop(0)
    in_stack = []
    out_stack = [(base, dist_to_base[base])]

    while in_stack or out_stack:
        if not out_stack:
            out_stack = in_stack[::-1]
            in_stack = []
        old_pos, dist = out_stack.pop()
        for dir in DIRECTIONS:
            if dir in maze[old_pos]:
                continue  # hit walls
            new_pos = virtual_move(old_pos, dir)
            # take out distance remembered
            if new_pos in dist_to_base:
                dist_old = dist_to_base[new_pos]
            else:
                dist_old = INF_METRIC
            # compare to current optimal distance
            dist_new = dist + 1
            # update if better
            if dist_new < dist_old:
                dist_to_base[new_pos] = dist_new
                path_to_base[new_pos] = OPPOSITES[dir]
                in_stack.append((new_pos, dist_new))


def find_path(path_to_base, start):
    movements = []
    pos = start
    dir = path_to_base[pos]
    while dir:
        movements.append(dir)
        pos = virtual_move(pos, dir)
        dir = path_to_base[pos]
    return movements


def virtual_move(pos, direction):
    px, py = pos
    dx, dy = RELATIVE[direction]
    return px + dx, py + dy


def update_maze(maze, dist_to_base, path_to_base):
    old_pos = (get_pos_x(), get_pos_y())
    changed = False
    for dir in list(maze[old_pos]):
        if can_move(dir):
            new_pos = virtual_move(old_pos, dir)
            maze[old_pos].remove(dir)
            maze[new_pos].remove(OPPOSITES[dir])
            changed = True
            plot_flow_field(maze, dist_to_base, path_to_base, new_pos)
    if changed:
        plot_flow_field(maze, dist_to_base, path_to_base, old_pos)


def wait_ticks(ticks):
    for _ in range(ticks):
        pass


def drone_work():
    # 等待其他无人机到位
    while not can_harvest():
        continue
    harvest()
    while num_items(Items.Hay) != BEGIN_HAY:
        continue

    # 生成迷宫
    plant(Entities.Bush)
    use_item(Items.Weird_Substance, COSTS)

    # 了解迷宫
    maze = scan_maze({}, None)

    forked = spawn_drone(wrapper2(maze_solver, maze, (2, 2)))
    maze_solver(maze, (-2, -2))
    wait_for(forked)
    harvest()


def maze_solver(maze, offset):
    base = (get_pos_x() + offset[0], get_pos_y() + offset[1])
    dist_to_base = {base: 0}
    path_to_base = {base: None}
    plot_flow_field(maze, dist_to_base, path_to_base, base)

    for i in range(600):
        gold = measure()
        if get_entity_type() == Entities.Treasure:
            use_item(Items.Weird_Substance, COSTS)
            if measure() == gold:
                return
            continue
        if get_entity_type() != Entities.Hedge:
            return

        back_to_base = find_path(path_to_base, (get_pos_x(), get_pos_y()))
        base_to_gold = find_path(path_to_base, gold)

        while back_to_base and base_to_gold and back_to_base[-1] == base_to_gold[-1]:
            back_to_base.pop()
            base_to_gold.pop()

        if i % 8:
            for step in back_to_base:
                move(step)
            if measure() != gold:
                continue
            for step in base_to_gold[::-1]:
                move(OPPOSITES[step])
        else:
            for step in back_to_base:
                move(step)
                update_maze(maze, dist_to_base, path_to_base)
            if measure() != gold:
                continue
            for step in base_to_gold[::-1]:
                move(OPPOSITES[step])
                update_maze(maze, dist_to_base, path_to_base)


def spawn_drones_16(work):
    def move_do(side_length, d, do):
        def fn():
            for _ in range(side_length):
                move(d)
            do()

        return fn

    def spawn_drone_task1():
        forked2 = spawn_drone(move_do(16, East, work))
        forked1 = spawn_drone(move_do(8, East, work))
        forked3 = spawn_drone(move_do(8, West, work))
        work()
        wait_for(forked1)
        wait_for(forked2)
        wait_for(forked3)

    forked1 = spawn_drone(move_do(16, North, spawn_drone_task1))
    forked2 = spawn_drone(move_do(8, North, spawn_drone_task1))
    forked3 = spawn_drone(move_do(8, South, spawn_drone_task1))
    spawn_drone_task1()
    wait_for(forked1)
    wait_for(forked2)
    wait_for(forked3)


START_HAY = num_items(Items.Hay)
BEGIN_HAY = START_HAY + 512 * 16
clear()
for _ in range(4):
    move(East)
    move(North)
spawn_drones_16(drone_work)
