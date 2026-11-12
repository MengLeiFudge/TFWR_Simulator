from __builtins__ import *
# 历史提交归档：lb_carrots | 初次提交 2026-10-27 (9d2d3c31) | 优化：迁入七项实机上榜策略并记录完整统计
# 完整轮时间：4:36.794（2026-10-26，官方完整27轮，request 86）。

def lb_carrots():
    set_world_size(FIELD_SIZE)
    workers = []
    support_ready = True
    tile_count = 0
    for base_y in TILE_BASE_YS:
        for base_x in TILE_BASE_XS:
            goto(base_x, base_y)
            tile_count = tile_count + 1
            if tile_count < ACTIVE_TILE_COUNT:
                worker = spawn_drone(initialize_tile_support_worker)
                if worker == None:
                    quick_print("carrots_init stopped: support dispatch failed", tile_count)
                    support_ready = False
                    break
                workers.append(worker)
            else:
                support_ready = initialize_tile_support_worker()
        if not support_ready:
            break
    for worker in workers:
        if not wait_for(worker):
            support_ready = False
    if not support_ready:
        quick_print("carrots_init stopped: support preparation failed")
        return

    # 收齐全部支撑结果后才种生产锚点；生产期间不再改写支撑。
    workers = []
    tile_count = 0
    for base_y in TILE_BASE_YS:
        for base_x in TILE_BASE_XS:
            goto(base_x, base_y)
            tile_count = tile_count + 1
            if tile_count < ACTIVE_TILE_COUNT:
                worker = spawn_drone(companion_carrot_tile_thread)
                if worker == None:
                    quick_print("carrots_init stopped: production dispatch failed", tile_count)
                    clear()
                    return
                workers.append(worker)
            else:
                companion_carrot_tile_thread()
    for worker in workers:
        wait_for(worker)


def initialize_tile_support_worker():
    return init_tile_support(get_pos_x(), get_pos_y())


FIELD_SIZE = 32
GOAL_CARROTS = 2000000000
ACTIVE_TILE_COUNT = 32
TILE_WIDTH = 4
TILE_HEIGHT = 8
TILE_BASE_XS = (0, 4, 8, 12, 16, 20, 24, 28)
TILE_BASE_YS = (0, 8, 16, 24)
TILE_ANCHOR_OFFSETS = (
    (0, 0), (0, 1), (0, 2),
    (0, 3), (0, 4), (1, 4),
    (1, 5), (1, 6),
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
    water = num_items(Items.Water)
    if water > 384:
        use_item(Items.Water, 3)
    elif water > 192:
        use_item(Items.Water, 2)
    elif water > 64:
        use_item(Items.Water)


def companion_carrot_tile_thread():
    base_x = get_pos_x()
    base_y = get_pos_y()

    init_tile_anchors(base_x, base_y)

    while num_items(Items.Carrot) < GOAL_CARROTS:
        for dx, dy in TILE_ANCHOR_OFFSETS:
            goto((base_x + dx) % FIELD_SIZE, (base_y + dy) % FIELD_SIZE)
            harvest_tile_carrot()
            if num_items(Items.Carrot) >= GOAL_CARROTS:
                break
            roll_static_bush_companion()
            water_carrot_anchor()

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
                if not plant(Entities.Bush):
                    quick_print("carrots_init stopped: support plant failed", x, y)
                    return False
    return True


def init_tile_anchors(base_x, base_y):
    for dx, dy in TILE_ANCHOR_OFFSETS:
        goto((base_x + dx) % FIELD_SIZE, (base_y + dy) % FIELD_SIZE)
        prepare_static_carrot_slot()
        roll_static_bush_companion()
        water_carrot_anchor()


def is_carrot_anchor(x, y):
    local_x = x % TILE_WIDTH
    local_y = y % TILE_HEIGHT
    for anchor_x, anchor_y in TILE_ANCHOR_OFFSETS:
        if local_x == anchor_x and local_y == anchor_y:
            return True
    return False


def prepare_static_carrot_slot():
    if get_ground_type() != Grounds.Soil:
        till()
    entity = get_entity_type()
    if entity != Entities.Carrot:
        if entity != None:
            harvest()
        plant(Entities.Carrot)
    water_carrot_anchor()


def harvest_tile_carrot():
    if can_harvest():
        harvest()
        plant(Entities.Carrot)
    else:
        water_carrot_anchor()


def roll_static_bush_companion():
    while num_items(Items.Carrot) < GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and not is_carrot_anchor(companion_pos[0], companion_pos[1]):
                return
        harvest()
        plant(Entities.Carrot)


if __name__ == "__main__":
    lb_carrots()
