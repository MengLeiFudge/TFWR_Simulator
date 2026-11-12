# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/github-dinosaur-sunflowers/sunflowers.py
s = get_world_size()
m = s - 1
d = max_drones()
MAX_P = 15
MIN_P = 7
AVERAGE_BUCKET_SIZE = 32 // (MAX_P - MIN_P) + 1

COST_OF_SUNFLOWER = get_cost(Entities.Sunflower)[Items.Carrot]  # ty: ignore
COST_OF_CARROT_EVERY_ROUND = s * s * COST_OF_SUNFLOWER
YIELD_OF_HAY_EVERY_ROUND = d * 512

BLOCK_W, BLOCK_H = 4, 8


def move_to(pos):
    cx, cy = get_pos_x(), get_pos_y()
    tx, ty = pos

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


def drone_work(carrots_on_finish, hay_on_start):

    def fn():
        line = [[], [], [], [], [], [], [], [], []]

        def do_plant():
            if get_ground_type() != Grounds.Soil:
                till()
            pos = (get_pos_x(), get_pos_y())
            plant(Entities.Sunflower)
            v = measure()
            # 控制各无人机处理数量不要差别太大
            while len(line[v - MIN_P]) > AVERAGE_BUCKET_SIZE:
                harvest()
                plant(Entities.Sunflower)
                v = measure()
            line[v - MIN_P].append(pos)

        traverse_rectangle(do_plant, BLOCK_W, BLOCK_H)

        wait_others_plant = True
        wait_others_harvest = False

        for p in range(MAX_P - MIN_P, -1, -1):
            hay_on_finish = hay_on_start + YIELD_OF_HAY_EVERY_ROUND * (8 - p)
            for pos in line[p]:
                move_to(pos)
                if wait_others_plant:
                    # 等待全部种植完成
                    while num_items(Items.Carrot) > carrots_on_finish:
                        continue
                    wait_others_plant = False
                if wait_others_harvest:
                    # 等待全部采收完成
                    while num_items(Items.Hay) < hay_on_finish:
                        if num_items(Items.Power) >= 100000:
                            return
                    wait_others_harvest = False
                if measure() == None:
                    continue
                while not can_harvest():
                    if use_item(Items.Fertilizer):
                        continue
                    w = min(
                        4 - 4 * get_water() // 1,
                        num_items(Items.Water),
                    )
                    if w:
                        use_item(Items.Water, w)
                harvest()
            if p == 0:
                # 最后一轮了，不用通知其他人
                return

            if not line[p]:
                # 本列没有这个花瓣数的向日葵了，随便清理一株以种草
                harvest()

            plant(Entities.Grass)
            while not can_harvest():
                if get_water() < 0.75:
                    num_items(Items.Water)
            harvest()
            wait_others_harvest = True

    return fn


def spawn_drones_32(work):
    w, h = 4, 8

    def wrapper(fn, arg0):
        def wrapped():
            fn(arg0)

        return wrapped

    def move_do(side_length, d, do):
        def fn():
            for _ in range(side_length):
                move(d)
            do()

        return fn

    def spawn_drone_task1(face):
        forked = spawn_drone(move_do(h, face, spawn_drone_task2))
        spawn_drone_task2()
        wait_for(forked)

    def spawn_drone_task2():
        forked = spawn_drone(move_do(w, East, wrapper(spawn_drone_task3, East)))
        spawn_drone_task3(West)
        wait_for(forked)

    def spawn_drone_task3(face):
        for _ in range(3):
            spawn_drone(work)
            for _ in range(w):
                move(face)
        work()

    forked = spawn_drone(move_do(h, North, wrapper(spawn_drone_task1, North)))
    spawn_drone_task1(South)
    wait_for(forked)


while num_items(Items.Power) < 100000:
    carrots_on_finish = num_items(Items.Carrot) - COST_OF_CARROT_EVERY_ROUND
    hay_on_start = num_items(Items.Hay)
    work = drone_work(carrots_on_finish, hay_on_start)
    spawn_drones_32(work)
