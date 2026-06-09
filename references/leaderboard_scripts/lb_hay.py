from __builtins__ import *

# 2:48.124
def lb_hay():
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
        quick_print("lb_hay done hay=", num_items(Items.Hay), " time=", get_time())


def harvest_ready_grass():
    if not can_harvest():
        water_pair_slot()
    harvest()


def water_pair_slot():
    # 32 线程会同时抢水；只在仍有库存时补水，避免无水时反复调用。
    water = num_items(Items.Water)
    if water > 2:
        use_item(Items.Water, 3)
    elif water > 1:
        use_item(Items.Water, 2)
    elif water > 0:
        use_item(Items.Water)


def roll_bush_companion(blocked_pos):
    while True:
        companion_entity, companion_pos = get_companion()
        if companion_entity == Entities.Bush and companion_pos != blocked_pos:
            break
        harvest()
        plant(Entities.Grass)


if __name__ == "__main__":
    lb_hay()
