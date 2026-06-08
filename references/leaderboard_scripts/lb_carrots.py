from __builtins__ import *

# 4:41.545
def lb_carrots():
    set_world_size(FIELD_SIZE)
    tile_count = 0
    for base_y in TILE_BASE_YS:
        for base_x in TILE_BASE_XS:
            if tile_count >= ACTIVE_TILE_COUNT:
                return
            goto(base_x, base_y)
            tile_count = tile_count + 1
            if tile_count < ACTIVE_TILE_COUNT:
                spawn_drone(companion_carrot_tile_thread)
            else:
                companion_carrot_tile_thread()


FIELD_SIZE = 32
GOAL_CARROTS = 2000000000
ACTIVE_TILE_COUNT = 32
TILE_WIDTH = 4
TILE_HEIGHT = 8
TILE_BASE_XS = (0, 4, 8, 12, 16, 20, 24, 28)
TILE_BASE_YS = (0, 8, 16, 24)
TILE_ANCHOR_OFFSETS = (
    (0, 0), (0, 1), (0, 2),
    (0, 3), (0, 4), (0, 5),
    (0, 6), (0, 7),
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


def companion_carrot_tile_thread():
    base_x = get_pos_x()
    base_y = get_pos_y()

    harvest_count = 0
    reroll_count = 0
    last_log_carrots = 0

    init_tile_support(base_x, base_y)
    init_tile_anchors(base_x, base_y)

    while num_items(Items.Carrot) < GOAL_CARROTS:
        for dx, dy in TILE_ANCHOR_OFFSETS:
            goto((base_x + dx) % FIELD_SIZE, (base_y + dy) % FIELD_SIZE)
            harvest_count = harvest_tile_carrot(harvest_count)
            if num_items(Items.Carrot) >= GOAL_CARROTS:
                break
            reroll_count = roll_static_bush_companion(reroll_count)
            water_carrot_anchor()

        if base_x == TILE_BASE_XS[0] and base_y == TILE_BASE_YS[0]:
            curr_carrots = num_items(Items.Carrot)
            if curr_carrots >= last_log_carrots + 100000000:
                last_log_carrots = curr_carrots
                quick_print(
                    "lb_carrots progress carrots=", curr_carrots,
                    " time=", get_time(),
                    " harvest=", harvest_count,
                    " reroll=", reroll_count,
                )

    if base_x == TILE_BASE_XS[0] and base_y == TILE_BASE_YS[0]:
        quick_print("lb_carrots done carrots=", num_items(Items.Carrot), " time=", get_time())


def init_tile_support(base_x, base_y):
    for dy in range(TILE_HEIGHT):
        for dx in range(TILE_WIDTH):
            x = (base_x + dx) % FIELD_SIZE
            y = (base_y + dy) % FIELD_SIZE
            if is_carrot_anchor(x, y):
                continue
            goto(x, y)
            entity = get_entity_type()
            if entity != Entities.Bush:
                if entity != None:
                    harvest()
                plant(Entities.Bush)


def init_tile_anchors(base_x, base_y):
    for dx, dy in TILE_ANCHOR_OFFSETS:
        goto((base_x + dx) % FIELD_SIZE, (base_y + dy) % FIELD_SIZE)
        prepare_static_carrot_slot()
        roll_static_bush_companion(0)
        water_carrot_anchor()


def is_carrot_anchor(x, y):
    if x % TILE_WIDTH != 0:
        return False
    local_y = y % TILE_HEIGHT
    return local_y < 8


def prepare_static_carrot_slot():
    if get_ground_type() != Grounds.Soil:
        till()
    entity = get_entity_type()
    if entity != Entities.Carrot:
        if entity != None:
            harvest()
        plant(Entities.Carrot)
    water_carrot_anchor()


def harvest_tile_carrot(harvest_count):
    if can_harvest():
        harvest()
        harvest_count = harvest_count + 1
        plant(Entities.Carrot)
    else:
        water_carrot_anchor()
    return harvest_count


def roll_static_bush_companion(reroll_count):
    while num_items(Items.Carrot) < GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and not is_carrot_anchor(companion_pos[0], companion_pos[1]):
                return reroll_count
        harvest()
        plant(Entities.Carrot)
        reroll_count = reroll_count + 1
    return reroll_count


if __name__ == "__main__":
    lb_carrots()
