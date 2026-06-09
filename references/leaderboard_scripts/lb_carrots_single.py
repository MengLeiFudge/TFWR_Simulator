from __builtins__ import *

# 8:31.992
def lb_carrots_single():
    count = 100000000
    set_world_size(SINGLE_FIELD_SIZE)
    support_entity = create_entity_grid(SINGLE_FIELD_SIZE)
    init_anchors(support_entity)

    quick_print("lb_carrots_single", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    while num_items(Items.Carrot) < count:
        process_anchor(2, 1, support_entity)
        process_anchor(3, 1, support_entity)
        process_anchor(3, 2, support_entity)
        process_anchor(2, 2, support_entity)

    quick_print(
        "lb_carrots_single", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
    )


SINGLE_GOAL_CARROTS = 100000000
SINGLE_FIELD_SIZE = 5


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

def init_anchors(support_entity):
    for y in range(SINGLE_FIELD_SIZE):
        for x in range(SINGLE_FIELD_SIZE):
            goto(x, y)
            if is_anchor(x, y):
                support_entity[x][y] = None
                if get_ground_type() != Grounds.Soil:
                    till()
                if get_entity_type() != Entities.Carrot:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Carrot)
                    roll_adaptive_companion(support_entity)
            else:
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                support_entity[x][y] = Entities.Bush


def process_anchor(x, y, support_entity):
    goto(x, y)
    if get_entity_type() == Entities.Carrot:
        if can_harvest():
            harvest()
            plant(Entities.Carrot)
            roll_adaptive_companion(support_entity)
            water_anchor()
        else:
            water_anchor()
    else:
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)
        roll_adaptive_companion(support_entity)
        water_anchor()


def roll_adaptive_companion(support_entity):
    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            cx = companion_pos[0]
            cy = companion_pos[1]
            if not is_anchor(cx, cy):
                known_entity = support_entity[cx][cy]
                if known_entity == companion_entity:
                    return
                if companion_distance(cx, cy) <= 2:
                    if rewrite_adaptive_support(cx, cy, companion_entity, support_entity):
                        return
        harvest()
        plant(Entities.Carrot)


def rewrite_adaptive_support(tx, ty, companion_entity, support_entity):
    ox = get_pos_x()
    oy = get_pos_y()
    goto(tx, ty)
    entity = get_entity_type()
    if entity != companion_entity:
        if entity != None:
            harvest()
        if companion_entity == Entities.Carrot:
            if get_ground_type() != Grounds.Soil:
                till()
            if get_ground_type() != Grounds.Soil or not can_pay_carrot_cost():
                goto(ox, oy)
                return False
        elif companion_entity != Entities.Grass:
            if get_ground_type() != Grounds.Grassland:
                till()
        if not plant(companion_entity):
            goto(ox, oy)
            return False
    support_entity[tx][ty] = companion_entity
    goto(ox, oy)
    return True


def companion_distance(tx, ty):
    size = get_world_size()
    x = get_pos_x()
    y = get_pos_y()
    dx = abs(tx - x)
    dy = abs(ty - y)
    return min(dx, size - dx) + min(dy, size - dy)


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


def water_anchor():
    if num_items(Items.Water) > 2:
        use_item(Items.Water, 3)
    elif num_items(Items.Water) > 1:
        use_item(Items.Water, 2)
    elif num_items(Items.Water) > 0:
        use_item(Items.Water)


def is_anchor(x, y):
    if x == 2 and y == 1:
        return True
    if x == 3 and y == 1:
        return True
    if x == 3 and y == 2:
        return True
    if x == 2 and y == 2:
        return True
    return False


def create_entity_grid(size):
    rows = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        rows.append(row)
    return rows

if __name__ == "__main__":
    lb_carrots_single()
