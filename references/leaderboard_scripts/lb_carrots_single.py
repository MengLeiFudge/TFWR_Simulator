from __builtins__ import *
# 完整轮时间：6:43.330（2026-10-26，官方完整18轮，request 82）。

def lb_carrots_single():
    quick_print("carrot_eight", "start", "time=", get_time())
    set_world_size(FIELD_SIZE)
    if not prepare_field():
        return
    quick_print("carrot_eight", "ready", "time=", get_time(), "carrots=", num_items(Items.Carrot))
    goto(ANCHORS[0][0], ANCHORS[0][1])
    index = 0
    for visit in range(MAX_VISITS):
        water_once()
        if can_harvest():
            harvest()
            if num_items(Items.Carrot) >= GOAL_CARROTS:
                quick_print("carrot_eight", "done", "visits=", visit + 1, "time=", get_time(), "carrots=", num_items(Items.Carrot))
                return
            if not plant_valid_carrot():
                return
        move(ANCHOR_DIRECTIONS[index])
        index = (index + 1) % len(ANCHORS)
    quick_print("carrot_eight", "visit_limit", "time=", get_time(), "carrots=", num_items(Items.Carrot))


FIELD_SIZE = 8
GOAL_CARROTS = 100000000
MAX_REROLLS = 128
MAX_VISITS = 20000
ANCHORS = ((2, 2), (3, 2), (3, 3), (3, 4), (3, 5), (2, 5), (2, 4), (2, 3))
ANCHOR_DIRECTIONS = (East, North, North, North, West, South, South, South)


def prepare_field():
    # 先完成所有固定Bush支撑，再种锚点；生产期间不改写支撑。
    for y in range(FIELD_SIZE):
        if y % 2 == 0:
            columns = range(FIELD_SIZE)
        else:
            columns = range(FIELD_SIZE - 1, -1, -1)
        for x in columns:
            if is_anchor(x, y):
                continue
            goto(x, y)
            entity = get_entity_type()
            if entity != Entities.Bush:
                if entity != None:
                    harvest()
                if not plant(Entities.Bush):
                    quick_print("carrot_eight", "support_failed", "x=", x, "y=", y, "time=", get_time())
                    return False
    quick_print("carrot_eight", "support_ready", "time=", get_time())
    for pos in ANCHORS:
        goto(pos[0], pos[1])
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        if not plant_valid_carrot():
            return False
        water_once()
    return True


def plant_valid_carrot():
    if not plant(Entities.Carrot):
        quick_print("carrot_eight", "plant_failed", "time=", get_time())
        return False
    for attempt in range(MAX_REROLLS):
        companion = get_companion()
        if companion != None:
            entity = companion[0]
            pos = companion[1]
            if entity == Entities.Bush and not is_anchor(pos[0], pos[1]):
                return True
        harvest()
        if not plant(Entities.Carrot):
            quick_print("carrot_eight", "plant_failed", "time=", get_time())
            return False
    quick_print("carrot_eight", "reroll_limit", "time=", get_time())
    return False


def water_once():
    # 每次访问最多一次补水，不在重抽循环中额外补水。
    if get_water() < 0.9:
        water = num_items(Items.Water)
        if water > 0:
            use_item(Items.Water, min(4, water))


def is_anchor(x, y):
    return (x == 2 or x == 3) and y >= 2 and y <= 5


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


if __name__ == "__main__":
    lb_carrots_single()
