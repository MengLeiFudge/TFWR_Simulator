from __builtins__ import *

# 8:31.992
def lb_carrots_single():
    count = 100000000
    set_world_size(SINGLE_FIELD_SIZE)
    support_entity = create_entity_grid(SINGLE_FIELD_SIZE)
    init_anchors(support_entity)

    cycle_count = [0]
    harvest_count = [0]
    reroll_count = [0]
    static_hit_count = [0]
    memory_hit_count = [0]
    memory_rewrite_count = [0]
    memory_far_reject_count = [0]
    anchor_block_count = [0]
    last_log_carrots = [0]
    last_log_time = [0]

    quick_print("lb_carrots_single", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    while num_items(Items.Carrot) < count:
        process_anchor(
            2, 1, support_entity, harvest_count, reroll_count, static_hit_count,
            memory_hit_count, memory_rewrite_count, memory_far_reject_count, anchor_block_count,
        )
        process_anchor(
            3, 1, support_entity, harvest_count, reroll_count, static_hit_count,
            memory_hit_count, memory_rewrite_count, memory_far_reject_count, anchor_block_count,
        )
        process_anchor(
            3, 2, support_entity, harvest_count, reroll_count, static_hit_count,
            memory_hit_count, memory_rewrite_count, memory_far_reject_count, anchor_block_count,
        )
        process_anchor(
            2, 2, support_entity, harvest_count, reroll_count, static_hit_count,
            memory_hit_count, memory_rewrite_count, memory_far_reject_count, anchor_block_count,
        )

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_progress(last_log_carrots, last_log_time, cycle_count, harvest_count, reroll_count)

    quick_print(
        "lb_carrots_single", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " reroll=", reroll_count[0],
        " static_hit=", static_hit_count[0],
        " memory_hit=", memory_hit_count[0],
        " memory_rewrite=", memory_rewrite_count[0],
        " memory_far_reject=", memory_far_reject_count[0],
        " anchor_block=", anchor_block_count[0],
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
                    roll_seed_reroll = [0]
                    roll_adaptive_companion(support_entity, roll_seed_reroll, [0], [0], [0], [0], [0])
            else:
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                support_entity[x][y] = Entities.Bush


def process_anchor(
        x, y, support_entity, harvest_count, reroll_count, static_hit_count,
        memory_hit_count, memory_rewrite_count, memory_far_reject_count, anchor_block_count):
    goto(x, y)
    if get_entity_type() == Entities.Carrot:
        if can_harvest():
            harvest()
            harvest_count[0] = harvest_count[0] + 1
            plant(Entities.Carrot)
            roll_adaptive_companion(
                support_entity, reroll_count, static_hit_count, memory_hit_count,
                memory_rewrite_count, memory_far_reject_count, anchor_block_count,
            )
            water_anchor()
        else:
            water_anchor()
    else:
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)
        roll_adaptive_companion(
            support_entity, reroll_count, static_hit_count, memory_hit_count,
            memory_rewrite_count, memory_far_reject_count, anchor_block_count,
        )
        water_anchor()


def roll_adaptive_companion(
        support_entity, reroll_count, static_hit_count, memory_hit_count,
        memory_rewrite_count, memory_far_reject_count, anchor_block_count):
    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            cx = companion_pos[0]
            cy = companion_pos[1]
            if is_anchor(cx, cy):
                anchor_block_count[0] = anchor_block_count[0] + 1
            else:
                known_entity = support_entity[cx][cy]
                if known_entity == companion_entity:
                    if companion_entity == Entities.Bush:
                        static_hit_count[0] = static_hit_count[0] + 1
                    else:
                        memory_hit_count[0] = memory_hit_count[0] + 1
                    return
                if companion_distance(cx, cy) <= 2:
                    if rewrite_adaptive_support(cx, cy, companion_entity, support_entity):
                        memory_rewrite_count[0] = memory_rewrite_count[0] + 1
                        return
                else:
                    memory_far_reject_count[0] = memory_far_reject_count[0] + 1
        harvest()
        plant(Entities.Carrot)
        reroll_count[0] = reroll_count[0] + 1


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


def maybe_log_progress(last_log_carrots, last_log_time, cycle_count, harvest_count, reroll_count):
    curr_carrots = num_items(Items.Carrot)
    if curr_carrots < last_log_carrots[0] + 10000000:
        return

    curr_time = get_time()
    quick_print(
        "lb_carrots_single", " progress carrots=", curr_carrots,
        " time=", curr_time,
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " reroll=", reroll_count[0],
        " dcarrots=", curr_carrots - last_log_carrots[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_carrots[0] = curr_carrots
    last_log_time[0] = curr_time


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
