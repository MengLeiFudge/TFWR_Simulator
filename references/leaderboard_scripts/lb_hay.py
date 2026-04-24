from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2，32 个 7x8 分散双草伴生单元。


FIELD_SIZE = 32
GOAL_HAY = 2000000000
ACTIVE_PAIR_COUNT = 32
PAIR_BASE_XS = (1, 5, 9, 13, 17, 21, 25, 29)
PAIR_BASE_YS = (1, 9, 17, 25)
PAIR_SUPPORT_OFFSETS = (
    (0, -3), (-1, -2), (0, -2), (1, -2),
    (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1),
    (-3, 0), (-2, 0), (-1, 0), (1, 0), (2, 0), (3, 0),
    (-3, 1), (-2, 1), (-1, 1), (1, 1), (2, 1), (3, 1),
    (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
    (-1, 3), (0, 3), (1, 3),
    (0, 4),
)


def main1():
    set_world_size(FIELD_SIZE)
    # 初始化：整图 till 成 Soil，再按 (x+y)%2 铺 Grass/Bush。全部由 main 机一次性打底，
    # 然后再 spawn 30 个 drone 各接管一行；主机接管最后一行。
    init_checkerboard()
    # 回到 (0, 0)
    goto(0, 0)
    for _ in range(31):
        spawn_drone(row_thread)
        move(North)
    row_thread()


def goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def init_checkerboard():
    size = get_world_size()
    for y in range(size):
        if y % 2 == 0:
            end_x = size - 1
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if get_ground_type() != Grounds.Soil:
                till()
            if (x + y) % 2 == 0:
                if get_entity_type() != Entities.Grass:
                    plant(Entities.Grass)
            else:
                if get_entity_type() != Entities.Bush:
                    plant(Entities.Bush)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


# 每行线程：在自己所在行 y 沿 East 扫；碰到成熟 Grass 就 harvest+plant，否则跳过。
def row_thread():
    goal = 2000000000
    y = get_pos_y()
    while num_items(Items.Hay) < goal:
        x_start = get_pos_x()
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Grass:
                if can_harvest():
                    harvest()
                    plant(Entities.Grass)
            elif entity == Entities.Bush:
                # Bush 不需要重种；它只做 companion 目标。
                pass
            else:
                # 空格或其他：按棋盘回填
                x = get_pos_x()
                if (x + y) % 2 == 0:
                    plant(Entities.Grass)
                else:
                    plant(Entities.Bush)
            move(East)
    # 只由某台 drone 报告 done，避免 32 台同时 quick_print。主机的 y==31。
    if y == 31:
        quick_print("main1 done hay=", num_items(Items.Hay), " time=", get_time())


def main2():
    set_world_size(FIELD_SIZE)
    pair_count = 0
    for base_y in PAIR_BASE_YS:
        for base_x in PAIR_BASE_XS:
            if pair_count >= ACTIVE_PAIR_COUNT:
                return
            goto(base_x, base_y)
            pair_count = pair_count + 1
            if pair_count < ACTIVE_PAIR_COUNT:
                spawn_drone(companion_pair_thread)
            else:
                companion_pair_thread()


def companion_pair_thread():
    base_x = get_pos_x()
    base_y = get_pos_y()
    north_y = (base_y + 1) % FIELD_SIZE
    base_pos = (base_x, base_y)
    north_pos = (base_x, north_y)
    init_pair_support(base_x, base_y)
    run_pair_cycle(base_pos, north_pos)


def init_pair_support(base_x, base_y):
    # 分散单元间距为 x=4 / y=8；每个单元只初始化自身可能用到的伴生支撑区。
    for dx, dy in PAIR_SUPPORT_OFFSETS:
        x = (base_x + dx) % FIELD_SIZE
        y = (base_y + dy) % FIELD_SIZE
        goto(x, y)
        entity = get_entity_type()
        if entity != Entities.Bush:
            if entity != None:
                harvest()
            plant(Entities.Bush)

    goto(base_x, base_y)
    plant(Entities.Grass)
    move(North)
    plant(Entities.Grass)
    move(South)


def run_pair_cycle(base_pos, north_pos):
    harvest()
    water_pair_slot()
    roll_bush_companion(north_pos)
    move(North)

    harvest()
    water_pair_slot()
    roll_bush_companion(base_pos)
    move(South)

    while num_items(Items.Hay) < GOAL_HAY:
        harvest_ready_grass()
        if num_items(Items.Hay) >= GOAL_HAY:
            break
        roll_bush_companion(north_pos)
        move(North)

        harvest_ready_grass()
        if num_items(Items.Hay) >= GOAL_HAY:
            break
        roll_bush_companion(base_pos)
        move(South)

    if base_pos == (PAIR_BASE_XS[0], PAIR_BASE_YS[0]):
        quick_print("main2 done hay=", num_items(Items.Hay), " time=", get_time())


def harvest_ready_grass():
    if not can_harvest():
        water_pair_slot()
    harvest()


def water_pair_slot():
    # 32 线程会同时抢水；保留阈值，避免真实游戏日志被缺水警告刷屏。
    if num_items(Items.Water) > 128:
        use_item(Items.Water)


def roll_bush_companion(blocked_pos):
    while True:
        companion_entity, companion_pos = get_companion()
        if companion_entity == Entities.Bush and companion_pos != blocked_pos:
            break
        harvest()
        plant(Entities.Grass)


if __name__ == "__main__":
    main2()
