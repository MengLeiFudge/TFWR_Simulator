from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2，32 个分散非相邻双树伴生单元。


FIELD_SIZE = 32
GOAL_WOOD = 10000000000
ACTIVE_PAIR_COUNT = 32
PAIR_BASE_XS = (1, 5, 9, 13, 17, 21, 25, 29)
PAIR_BASE_YS = (1, 9, 17, 25)
PAIR_SUPPORT_OFFSETS = (
    (0, -3), (-1, -2), (0, -2), (1, -2),
    (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1),
    (-3, 0), (-2, 0), (-1, 0), (1, 0), (2, 0), (3, 0),
    (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1),
    (-3, 2), (-2, 2), (-1, 2), (1, 2), (2, 2), (3, 2),
    (-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3),
    (-1, 4), (0, 4), (1, 4),
    (0, 5),
)


def main1():
    set_world_size(FIELD_SIZE)
    init_checkerboard()
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
                if get_entity_type() != Entities.Tree:
                    plant(Entities.Tree)
            else:
                if get_entity_type() != Entities.Bush:
                    plant(Entities.Bush)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


def row_thread():
    goal = 10000000000
    y = get_pos_y()
    while num_items(Items.Wood) < goal:
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Tree:
                if can_harvest():
                    harvest()
                    plant(Entities.Tree)
            elif entity == Entities.Bush:
                pass
            else:
                x = get_pos_x()
                if (x + y) % 2 == 0:
                    plant(Entities.Tree)
                else:
                    plant(Entities.Bush)
            move(East)
    if y == 31:
        quick_print("main1 done wood=", num_items(Items.Wood), " time=", get_time())


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
    north_y = (base_y + 2) % FIELD_SIZE
    base_pos = (base_x, base_y)
    north_pos = (base_x, north_y)
    init_pair_support(base_x, base_y)
    run_pair_cycle(base_pos, north_pos)


def init_pair_support(base_x, base_y):
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
    prepare_tree_slot()
    move(North)
    move(North)
    prepare_tree_slot()
    move(South)
    move(South)


def run_pair_cycle(base_pos, north_pos):
    roll_bush_companion(north_pos)
    move(North)
    move(North)

    roll_bush_companion(base_pos)
    move(South)
    move(South)

    while num_items(Items.Wood) < GOAL_WOOD:
        harvest_ready_tree()
        if num_items(Items.Wood) >= GOAL_WOOD:
            break
        roll_bush_companion(north_pos)
        move(North)
        move(North)

        harvest_ready_tree()
        if num_items(Items.Wood) >= GOAL_WOOD:
            break
        roll_bush_companion(base_pos)
        move(South)
        move(South)

    if base_pos == (PAIR_BASE_XS[0], PAIR_BASE_YS[0]):
        quick_print("main2 done wood=", num_items(Items.Wood), " time=", get_time())


def prepare_tree_slot():
    entity = get_entity_type()
    if entity != Entities.Tree:
        if entity != None:
            harvest()
        plant(Entities.Tree)
    water_tree_slot()


def harvest_ready_tree():
    if not can_harvest():
        water_tree_slot()
    while not can_harvest():
        if num_items(Items.Fertilizer) > 64:
            use_item(Items.Fertilizer)
        else:
            do_a_flip()
    harvest()


def water_tree_slot():
    if num_items(Items.Water) > 128:
        use_item(Items.Water, 4)
    elif num_items(Items.Water) > 64:
        use_item(Items.Water, 2)
    elif num_items(Items.Water) > 32:
        use_item(Items.Water)


def roll_bush_companion(blocked_pos):
    while True:
        companion_entity, companion_pos = get_companion()
        if companion_entity == Entities.Bush and companion_pos != blocked_pos:
            break
        harvest()
        plant(Entities.Tree)
        water_tree_slot()


if __name__ == "__main__":
    main2()
