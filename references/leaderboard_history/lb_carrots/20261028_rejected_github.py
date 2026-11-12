# 淘汰候选归档：lb_carrots | 原实验路径 .codex/leaderboard-astra/github-carrots/carrots.py
W = 0.15


def traverse_rectangle(fn, w, h):
    fn()
    move(North)
    for i in range(w, 0, -2):
        for j in range(h, 1, -1):
            fn()
            if j != 2:
                move(North)
        move(East)
        for j in range(h, 1, -1):
            fn()
            if j != 2:
                move(South)
        if i != 2:
            move(East)
    move(South)
    for _ in range(1, w):
        fn()
        move(West)


def traverse_rectangle_if(fn, w, h):
    if fn():
        return False
    move(North)
    for i in range(w, 0, -2):
        for j in range(h, 1, -1):
            if fn():
                return False
            if j != 2:
                move(North)
        move(East)
        for j in range(h, 1, -1):
            if fn():
                return False
            if j != 2:
                move(South)
        if i != 2:
            move(East)
    move(South)
    for _ in range(1, w):
        if fn():
            return False
        move(West)

    return True  # loop continues


def work_drone_task():
    wants = {}
    x_lower, y_lower = get_pos_x(), get_pos_y()
    x_upper, y_upper = x_lower + 4, y_lower + 8

    def on_eachcell():
        t = (get_pos_x(), get_pos_y())

        # 满足当前位置的种植需求
        if t in wants:
            c = wants.pop(t)
            if get_entity_type() != c:
                harvest()
                plant(c)
            return

        if get_water() < W:
            use_item(Items.Water)
        while True:
            harvest()
            plant(Entities.Carrot)
            c, p = get_companion()
            x, y = p
            if x_lower <= x < x_upper and y_lower <= y < y_upper:
                if p in wants and wants[p] != c:
                    continue  # 和其他植物的请求种植的冲突
                wants[p] = c  # 标记格子接下来要种植的作物
                break
        return

    def first_round():
        till()
        on_eachcell()

    def while_round():
        on_eachcell()
        return num_items(Items.Carrot) >= 2000000000

    traverse_rectangle(first_round, 4, 8)
    while traverse_rectangle_if(while_round, 4, 8):
        continue


def move_to(pos):
    cx, cy = get_pos_x(), get_pos_y()
    tx, ty = pos
    s = 32

    dx_east = (tx - cx) % s
    dx_west = s - dx_east
    if dx_east < dx_west:
        for _ in range(dx_east):
            move(East)
    else:
        for _ in range(dx_west):
            move(West)

    dy_north = (ty - cy) % s
    dy_south = s - dy_north
    if dy_north < dy_south:
        for _ in range(dy_north):
            move(North)
    else:
        for _ in range(dy_south):
            move(South)


def straight_move_do(side_length, d, do):
    def fn():
        for _ in range(side_length):
            move(d)
        do()

    return fn


BLOCK_W, BLOCK_H = 4, 8


def spawn_drone_task1(face):
    def fn():
        spawn_drone(straight_move_do(BLOCK_H, face, spawn_drone_task2()))
        spawn_drone_task2()()

    return fn


def spawn_drone_task2():
    def fn():
        spawn_drone(straight_move_do(BLOCK_W, East, spawn_drone_task3(East)))
        spawn_drone_task3(West)()

    return fn


def spawn_drone_task3(face):
    def fn():
        for _ in range(3):
            spawn_drone(work_drone_task)
            for _ in range(BLOCK_W):
                move(face)
        work_drone_task()

    return fn


spawn_drone(straight_move_do(BLOCK_H, North, spawn_drone_task1(North)))
spawn_drone_task1(South)()
