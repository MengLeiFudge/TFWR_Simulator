from __builtins__ import *

# 6:40.073
def lb_wood():
    while True:
        if not spawn_drone(wood_worker):
            wood_worker()
            break
        move(East)
    quick_print("lb_wood done wood=", num_items(Items.Wood), " time=", get_time())
    quick_print(
        "wood_dynamic_stats static_bush=", WOOD_STATIC_BUSH,
        " grass_request=", WOOD_GRASS_REQUEST,
        " grass_rewrite=", WOOD_GRASS_REWRITE,
        " carrot_request=", WOOD_CARROT_REQUEST,
        " carrot_rewrite=", WOOD_CARROT_REWRITE,
        " carrot_skip=", WOOD_CARROT_SKIP,
        " force_unready_bush=", WOOD_CARROT_FORCE_UNREADY_BUSH,
        " bush_ground_fix=", WOOD_BUSH_GROUND_FIX,
        " reroll=", WOOD_REROLL,
    )


GOAL_WOOD = 10000000000
WOOD_GOAL_CHECK_INTERVAL = 8
WOOD_STATIC_BUSH = 0
WOOD_GRASS_REQUEST = 0
WOOD_GRASS_REWRITE = 0
WOOD_CARROT_REQUEST = 0
WOOD_CARROT_REWRITE = 0
WOOD_CARROT_SKIP = 0
WOOD_CARROT_FORCE_UNREADY_BUSH = 0
WOOD_BUSH_GROUND_FIX = 0
WOOD_REROLL = 0


def wood_worker():
    goal_check_countdown = 0
    while True:
        if goal_check_countdown <= 0:
            if num_items(Items.Wood) >= GOAL_WOOD:
                return
            goal_check_countdown = WOOD_GOAL_CHECK_INTERVAL
        goal_check_countdown -= 1
        use_wood_water()
        if (get_pos_x() + get_pos_y()) % 2 == 0:
            handle_tree_slot()
        else:
            handle_bush_slot()
        if num_items(Items.Fertilizer) > 100:
            use_item(Items.Fertilizer)
        move(North)


def handle_tree_slot():
    global WOOD_STATIC_BUSH
    global WOOD_GRASS_REQUEST
    global WOOD_GRASS_REWRITE
    global WOOD_CARROT_REQUEST
    global WOOD_CARROT_REWRITE
    global WOOD_CARROT_SKIP
    global WOOD_REROLL
    if can_harvest():
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if is_bush_slot(companion_pos):
                if companion_entity == Entities.Bush:
                    WOOD_STATIC_BUSH += 1
                    harvest()
                    plant(Entities.Tree)
                    return
                if companion_entity == Entities.Grass:
                    WOOD_GRASS_REQUEST += 1
                    if rewrite_grass_support(companion_pos):
                        WOOD_GRASS_REWRITE += 1
                        harvest()
                        plant(Entities.Tree)
                        return
                if companion_entity == Entities.Carrot:
                    WOOD_CARROT_REQUEST += 1
                    if rewrite_carrot_support(companion_pos):
                        WOOD_CARROT_REWRITE += 1
                        harvest()
                        plant(Entities.Tree)
                        return
                    WOOD_CARROT_SKIP += 1
        WOOD_REROLL += 1
        harvest()
    plant(Entities.Tree)


def is_bush_slot(pos):
    return (pos[0] + pos[1]) % 2 == 1


def rewrite_grass_support(pos):
    tx = pos[0]
    ty = pos[1]
    ox = get_pos_x()
    oy = get_pos_y()
    move_to(tx, ty)
    entity = get_entity_type()
    if entity != Entities.Grass:
        if entity != None:
            harvest()
        plant(Entities.Grass)
    move_to(ox, oy)
    return True


def rewrite_carrot_support(pos):
    global WOOD_CARROT_FORCE_UNREADY_BUSH
    tx = pos[0]
    ty = pos[1]
    ox = get_pos_x()
    oy = get_pos_y()
    move_to(tx, ty)
    entity = get_entity_type()
    if entity != Entities.Carrot:
        if entity != None:
            already_harvested = False
            if not can_harvest():
                if entity == Entities.Bush:
                    WOOD_CARROT_FORCE_UNREADY_BUSH += 1
                    harvest()
                    already_harvested = True
                else:
                    move_to(ox, oy)
                    return False
            if not already_harvested:
                harvest()
        if get_ground_type() != Grounds.Soil:
            till()
        if get_ground_type() != Grounds.Soil:
            move_to(ox, oy)
            return False
        if not can_pay_carrot_cost():
            move_to(ox, oy)
            return False
        if not plant(Entities.Carrot):
            move_to(ox, oy)
            return False
    move_to(ox, oy)
    return True


def handle_bush_slot():
    entity = get_entity_type()
    if entity != None:
        if not can_harvest():
            return
        harvest()
    restore_bush_ground()
    plant(Entities.Bush)


def can_pay_carrot_cost():
    cost = get_cost(Entities.Carrot)
    if cost == None:
        return True
    items = [
        Items.Hay,
        Items.Wood,
        Items.Carrot,
        Items.Pumpkin,
        Items.Power,
        Items.Cactus,
        Items.Gold,
        Items.Bone,
        Items.Weird_Substance,
    ]
    for item in items:
        if item in cost and num_items(item) < cost[item]:
            return False
    return True


def restore_bush_ground():
    global WOOD_BUSH_GROUND_FIX
    if get_ground_type() != Grounds.Grassland:
        WOOD_BUSH_GROUND_FIX += 1
        till()


def move_to(tx, ty):
    size = get_world_size()
    half_size = size // 2
    x = get_pos_x()
    dx = (tx - x) % size
    if dx <= half_size:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    y = get_pos_y()
    dy = (ty - y) % size
    if dy <= half_size:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def use_wood_water():
    while get_water() < min(num_items(Items.Water) / 100, 0.75):
        use_item(Items.Water)


if __name__ == "__main__":
    lb_wood()
