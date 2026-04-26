from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main3，32x32 多机 Bush support 双胡萝卜单元。


FIELD_SIZE = 32
GOAL_CARROTS = 2000000000
COMPANION_BASE_XS = (0, 8, 16, 24)
COMPANION_BASE_YS = (0, 8, 16, 24)
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
    set_world_size(32)
    init_all_carrots()
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


def init_all_carrots():
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
            if get_entity_type() != Entities.Carrot:
                plant(Entities.Carrot)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


def row_thread():
    goal = 2000000000
    y = get_pos_y()
    while num_items(Items.Carrot) < goal:
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Carrot:
                if can_harvest():
                    harvest()
                    plant(Entities.Carrot)
            else:
                if entity != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Carrot)
            move(East)
    if y == 31:
        quick_print("main1 done carrots=", num_items(Items.Carrot), " time=", get_time())


def main2():
    set_world_size(FIELD_SIZE)
    unit_count = 0
    for base_y in COMPANION_BASE_YS:
        for base_x in COMPANION_BASE_XS:
            goto(base_x, base_y)
            unit_count = unit_count + 1
            if unit_count < 16:
                spawn_drone(companion_carrot_thread)
            else:
                companion_carrot_thread()


def companion_carrot_thread():
    base_x = get_pos_x()
    base_y = get_pos_y()
    harvest_count = 0
    reroll_count = 0
    last_log_carrots = 0
    prepare_carrot_anchor()
    reroll_count = roll_bush_companion_for_anchor(base_x, base_y, reroll_count)
    water_carrot_anchor()

    while num_items(Items.Carrot) < GOAL_CARROTS:
        if can_harvest():
            harvest()
            harvest_count = harvest_count + 1
            plant(Entities.Carrot)
            reroll_count = roll_bush_companion_for_anchor(base_x, base_y, reroll_count)
            water_carrot_anchor()
        else:
            water_carrot_anchor()

        if base_x == 0 and base_y == 0 and num_items(Items.Carrot) >= last_log_carrots + 50000000:
            last_log_carrots = num_items(Items.Carrot)
            quick_print(
                "main2 progress carrots=", last_log_carrots,
                " time=", get_time(),
                " harvest=", harvest_count,
                " reroll=", reroll_count,
            )

    if base_x == 0 and base_y == 0:
        quick_print("main2 done carrots=", num_items(Items.Carrot), " time=", get_time())


def prepare_carrot_anchor():
    if get_ground_type() != Grounds.Soil:
        till()
    if get_entity_type() != Entities.Carrot:
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)


def water_carrot_anchor():
    # 32 台无人机会同时抢水；低库存调用只会刷警告，实际收益很小。
    if num_items(Items.Water) > 512:
        use_item(Items.Water, 3)
    elif num_items(Items.Water) > 256:
        use_item(Items.Water, 2)
    elif num_items(Items.Water) > 128:
        use_item(Items.Water)


def roll_bush_companion_for_anchor(base_x, base_y, reroll_count):
    while num_items(Items.Carrot) < GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and is_local_support_pos(base_x, base_y, companion_pos):
                origin_x = get_pos_x()
                origin_y = get_pos_y()
                goto(companion_pos[0], companion_pos[1])
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                goto(origin_x, origin_y)
                return reroll_count
        harvest()
        plant(Entities.Carrot)
        reroll_count = reroll_count + 1
    return reroll_count


def is_local_support_pos(base_x, base_y, pos):
    support_x = pos[0]
    support_y = pos[1]
    if support_x == base_x and support_y == base_y:
        return False
    return wrapped_distance(base_x, support_x) <= 3 and wrapped_distance(base_y, support_y) <= 3


def wrapped_distance(a, b):
    delta = (a - b) % FIELD_SIZE
    if delta > FIELD_SIZE // 2:
        return FIELD_SIZE - delta
    return delta


def main3():
    set_world_size(FIELD_SIZE)
    pair_count = 0
    for base_y in PAIR_BASE_YS:
        for base_x in PAIR_BASE_XS:
            if pair_count >= ACTIVE_PAIR_COUNT:
                return
            goto(base_x, base_y)
            pair_count = pair_count + 1
            if pair_count < ACTIVE_PAIR_COUNT:
                spawn_drone(companion_carrot_pair_thread)
            else:
                companion_carrot_pair_thread()


def companion_carrot_pair_thread():
    base_x = get_pos_x()
    base_y = get_pos_y()
    north_y = (base_y + 1) % FIELD_SIZE
    base_pos = (base_x, base_y)
    north_pos = (base_x, north_y)

    harvest_count = 0
    reroll_count = 0
    last_log_carrots = 0

    init_pair_support(base_x, base_y)
    goto(base_pos[0], base_pos[1])
    reroll_count = roll_static_bush_companion(north_pos, reroll_count)
    water_carrot_anchor()
    goto(north_pos[0], north_pos[1])
    reroll_count = roll_static_bush_companion(base_pos, reroll_count)
    water_carrot_anchor()
    goto(base_pos[0], base_pos[1])

    while num_items(Items.Carrot) < GOAL_CARROTS:
        harvest_count = harvest_pair_carrot(harvest_count)
        if num_items(Items.Carrot) >= GOAL_CARROTS:
            break
        reroll_count = roll_static_bush_companion(north_pos, reroll_count)
        water_carrot_anchor()
        move(North)

        harvest_count = harvest_pair_carrot(harvest_count)
        if num_items(Items.Carrot) >= GOAL_CARROTS:
            break
        reroll_count = roll_static_bush_companion(base_pos, reroll_count)
        water_carrot_anchor()
        move(South)

        if base_pos == (PAIR_BASE_XS[0], PAIR_BASE_YS[0]):
            curr_carrots = num_items(Items.Carrot)
            if curr_carrots >= last_log_carrots + 100000000:
                last_log_carrots = curr_carrots
                quick_print(
                    "main3 progress carrots=", curr_carrots,
                    " time=", get_time(),
                    " harvest=", harvest_count,
                    " reroll=", reroll_count,
                )

    if base_pos == (PAIR_BASE_XS[0], PAIR_BASE_YS[0]):
        quick_print("main3 done carrots=", num_items(Items.Carrot), " time=", get_time())


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
    prepare_static_carrot_slot()
    move(North)
    prepare_static_carrot_slot()
    move(South)


def prepare_static_carrot_slot():
    if get_ground_type() != Grounds.Soil:
        till()
    entity = get_entity_type()
    if entity != Entities.Carrot:
        if entity != None:
            harvest()
        plant(Entities.Carrot)
    water_carrot_anchor()


def harvest_pair_carrot(harvest_count):
    if can_harvest():
        harvest()
        harvest_count = harvest_count + 1
        plant(Entities.Carrot)
    else:
        water_carrot_anchor()
    return harvest_count


def roll_static_bush_companion(blocked_pos, reroll_count):
    while num_items(Items.Carrot) < GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and companion_pos != blocked_pos:
                return reroll_count
        harvest()
        plant(Entities.Carrot)
        reroll_count = reroll_count + 1
    return reroll_count


if __name__ == "__main__":
    main3()
