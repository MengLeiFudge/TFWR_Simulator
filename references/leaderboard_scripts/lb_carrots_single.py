from __builtins__ import *

# 9:46.899
def lb_carrots_single():
    count = 100000000
    set_world_size(SINGLE_FIELD_SIZE)
    init_anchors()

    cycle_count = [0]
    harvest_count = [0]
    reroll_count = [0]
    last_log_carrots = [0]
    last_log_time = [0]

    quick_print("lb_carrots_single", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    while num_items(Items.Carrot) < count:
        process_anchor(1, 1, harvest_count, reroll_count)
        process_anchor(3, 1, harvest_count, reroll_count)
        process_anchor(1, 3, harvest_count, reroll_count)
        process_anchor(3, 3, harvest_count, reroll_count)

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_progress(last_log_carrots, last_log_time, cycle_count, harvest_count, reroll_count)

    quick_print(
        "lb_carrots_single", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " reroll=", reroll_count[0],
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

def init_anchors():
    for y in range(SINGLE_FIELD_SIZE):
        for x in range(SINGLE_FIELD_SIZE):
            goto(x, y)
            if is_anchor(x, y):
                if get_ground_type() != Grounds.Soil:
                    till()
                if get_entity_type() != Entities.Carrot:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Carrot)
                    roll_seed_reroll = [0]
                    roll_bush_companion(roll_seed_reroll)
            else:
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)


def process_anchor(x, y, harvest_count, reroll_count):
    goto(x, y)
    if get_entity_type() == Entities.Carrot:
        if can_harvest():
            harvest()
            harvest_count[0] = harvest_count[0] + 1
            plant(Entities.Carrot)
            roll_bush_companion(reroll_count)
            water_anchor()
        else:
            water_anchor()
    else:
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)
        roll_bush_companion(reroll_count)
        water_anchor()


def roll_bush_companion(reroll_count):
    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and not is_anchor(companion_pos[0], companion_pos[1]):
                return
        harvest()
        plant(Entities.Carrot)
        reroll_count[0] = reroll_count[0] + 1


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
    if x == 1 and y == 1:
        return True
    if x == 3 and y == 1:
        return True
    if x == 1 and y == 3:
        return True
    if x == 3 and y == 3:
        return True
    return False

if __name__ == "__main__":
    lb_carrots_single()
