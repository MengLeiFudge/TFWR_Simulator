from __builtins__ import *

# 9:33.732
def lb_carrots():
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


FIELD_SIZE = 32
GOAL_CARROTS = 2000000000
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

def water_carrot_anchor():
    # 32 台无人机会同时抢水；低库存调用只会刷警告，实际收益很小。
    if num_items(Items.Water) > 512:
        use_item(Items.Water, 3)
    elif num_items(Items.Water) > 256:
        use_item(Items.Water, 2)
    elif num_items(Items.Water) > 128:
        use_item(Items.Water)

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
                    "lb_carrots progress carrots=", curr_carrots,
                    " time=", get_time(),
                    " harvest=", harvest_count,
                    " reroll=", reroll_count,
                )

    if base_pos == (PAIR_BASE_XS[0], PAIR_BASE_YS[0]):
        quick_print("lb_carrots done carrots=", num_items(Items.Carrot), " time=", get_time())


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
    lb_carrots()
