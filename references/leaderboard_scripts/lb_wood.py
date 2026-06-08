from __builtins__ import *

# 7:36.580
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
        " reroll=", WOOD_REROLL,
    )


GOAL_WOOD = 10000000000
WOOD_STATIC_BUSH = 0
WOOD_GRASS_REQUEST = 0
WOOD_GRASS_REWRITE = 0
WOOD_REROLL = 0


def wood_worker():
    while num_items(Items.Wood) < GOAL_WOOD:
        use_wood_water()
        if (get_pos_x() + get_pos_y()) % 2 == 0:
            handle_tree_slot()
        else:
            if can_harvest():
                harvest()
            plant(Entities.Bush)
        if num_items(Items.Fertilizer) > 100:
            use_item(Items.Fertilizer)
        move(North)


def handle_tree_slot():
    global WOOD_STATIC_BUSH
    global WOOD_GRASS_REQUEST
    global WOOD_GRASS_REWRITE
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
