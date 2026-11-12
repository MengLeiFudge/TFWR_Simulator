# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-github-algorithms/enihsyou-cactus.py
s = get_world_size()
m = s - 1


def insertion_sort_vertical():
    while True:
        if get_pos_y() < m:
            if measure() > measure(North):  # ty: ignore
                swap(North)
        if get_pos_y() > 0:
            if measure() < measure(South):  # ty: ignore
                swap(South)
                # 多线程环境下不可再与北侧交换
                move(South)
                continue
        break


def insertion_sort_horizontal():
    while True:
        if get_pos_x() < m:
            if measure() > measure(East):  # ty: ignore
                swap(East)
        if get_pos_x() > 0:
            if measure() < measure(West):  # ty: ignore
                swap(West)
                # 多线程环境下不可再与东侧交换
                move(West)
                continue
        break


def move_to_and_swap_x(tx):
    cx = get_pos_x()
    dx_east = (tx - cx) % s
    dx_west = s - dx_east
    if dx_east < dx_west:
        for _ in range(dx_east):
            move(East)
    else:
        for _ in range(dx_west):
            # 已跨越边界，在移动到目标位置前的这阶段，遇到的都是未排序过的，利用移动到此位的机会做个交换
            if get_pos_x() > cx and measure() < measure(West):  # ty: ignore
                swap(West)
            move(West)


def move_to_and_swap_y(ty):
    cy = get_pos_y()
    dy_north = (ty - cy) % s
    dy_south = s - dy_north
    if dy_north < dy_south:
        for _ in range(dy_north):
            move(North)
    else:
        for _ in range(dy_south):
            if get_pos_y() > cy and measure() < measure(South):  # ty: ignore
                swap(South)
            move(South)


def straight_move_do(side_length, d, do):
    def fn():
        for _ in range(side_length):
            move(d)
        do()

    return fn


def horizontal_work():
    for _ in range(s):
        till()
        plant(Entities.Cactus)
        if get_pos_y() > 0 and measure() < measure(South):  # ty: ignore
            # 种完就立刻排序，节约移动时间
            swap(South)
        move(North)
    all_dispatched = False
    other_finished = False
    drones = []
    for y in range(s):
        all_dispatched = all_dispatched or num_drones() == s
        other_finished = other_finished or num_drones() < s
        move_to_and_swap_y(y)
        if all_dispatched and other_finished:
            drone = spawn_drone(insertion_sort_vertical)
            if drone:
                drones.append(drone)
                continue
        insertion_sort_vertical()
    for drone in drones:
        wait_for(drone)


def vertical_work():
    all_dispatched = False
    other_finished = False
    drones = []
    for x in range(s):
        all_dispatched = all_dispatched or num_drones() == s
        other_finished = other_finished or num_drones() < s
        move_to_and_swap_x(x)
        if all_dispatched and other_finished:
            drone = spawn_drone(insertion_sort_horizontal)
            if drone:
                drones.append(drone)
                continue
        insertion_sort_horizontal()

    for drone in drones:
        wait_for(drone)


def sender(dir, main, work):
    def fn():
        if main:
            move(dir)
        drones = []
        for _ in range(1, s // 2):
            drones.append(spawn_drone(work))
            move(dir)
        work()
        for drone in drones:
            wait_for(drone)

    return fn


sorter1 = sender(West, False, horizontal_work)
sorter2 = sender(East, True, horizontal_work)
forked = spawn_drone(sorter1)
sorter2()
wait_for(forked)

sorter1 = sender(North, False, vertical_work)
sorter2 = sender(South, True, vertical_work)
forked = spawn_drone(sorter1)
sorter2()
wait_for(forked)

harvest()
