# 淘汰候选归档：lb_wood | 原实验路径 .codex/leaderboard-astra/github-wood/wood.py
W = 0.35


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


def is_tree_pos(p):
    x, y = p
    return (x + y) % 2 == 0


# 4 x 8 区域中第 0, 2 列种树
def work_drone_task():
    wants = {}

    def on_eachcell():
        t = (get_pos_x(), get_pos_y())

        # 满足当前位置的种植需求
        if t in wants:
            c = wants.pop(t)
            if get_entity_type() != c:
                harvest()
                # may failed at Carrot with no enough resource
                _ = plant(c) or plant(Entities.Bush)
            return

        # 在树的位置种树，其他位置不管
        if is_tree_pos(t):
            # 只在树的位置浇水
            if get_water() < W:
                # 访问间隔挺长的，不需要太多水
                use_item(Items.Water)
            while True:
                harvest()
                plant(Entities.Tree)
                c, p = get_companion()
                if is_tree_pos(p):
                    continue  #  和树的位置冲突
                if p in wants and wants[p] != c:
                    continue  # 和其他植物的请求种植的冲突
                wants[p] = c  # 标记格子接下来要种植的作物
                break
            return

    def first_round():
        till()
        on_eachcell()

    def range_round():
        on_eachcell()

    def while_round():
        on_eachcell()
        return num_items(Items.Wood) >= 10000000000

    traverse_rectangle(first_round, 4, 8)
    for _ in range(22):
        traverse_rectangle(range_round, 4, 8)
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


DIRECTIONS = [North, East, South, West]
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
