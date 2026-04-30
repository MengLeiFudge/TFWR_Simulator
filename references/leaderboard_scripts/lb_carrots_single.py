from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main4；main3 保留做纯滚动基线。


SINGLE_GOAL_CARROTS = 100000000
SINGLE_FIELD_SIZE = 5






def init_main1_soil():
    size = 5
    for y in range(size):
        if y % 2 == 0:
            end_x = size - 1
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def maybe_water_main1_slot():
    if get_water() < 1 and num_items(Items.Water) >= 4:
        use_item(Items.Water, 4)
    elif get_water() < 0.5 and num_items(Items.Water) >= 2:
        use_item(Items.Water, 2)


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







def maybe_log_main2(
        last_log_carrots,
        last_log_time,
        cycle_count,
        harvest_count,
        replant_count,
        unready_count):
    curr_carrots = num_items(Items.Carrot)
    if curr_carrots < last_log_carrots[0] + 10000000:
        return

    curr_time = get_time()
    quick_print(
        "main2", " progress carrots=", curr_carrots,
        " time=", curr_time,
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " replant=", replant_count[0],
        " unready=", unready_count[0],
        " dcarrots=", curr_carrots - last_log_carrots[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_carrots[0] = curr_carrots
    last_log_time[0] = curr_time


def main2(count=100000000):
    set_world_size(5)
    init_main1_soil()

    cycle_count = [0]
    harvest_count = [0]
    replant_count = [0]
    unready_count = [0]
    last_log_carrots = [0]
    last_log_time = [0]

    quick_print("main2", " init_time=", get_time(), " carrots=", num_items(Items.Carrot))

    while num_items(Items.Carrot) < count:
        for y in range(5):
            if y % 2 == 0:
                start_x = 0
                end_x = 4
                step = 1
                move_dir = East
            else:
                start_x = 4
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                entity = get_entity_type()
                if entity == Entities.Carrot:
                    if can_harvest():
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                        plant(Entities.Carrot)
                        replant_count[0] = replant_count[0] + 1
                        get_companion()
                        maybe_water_main1_slot()
                    else:
                        unready_count[0] = unready_count[0] + 1
                        maybe_water_main1_slot()
                else:
                    if entity != None:
                        harvest()
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                    replant_count[0] = replant_count[0] + 1
                    get_companion()
                    maybe_water_main1_slot()

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_main2(
            last_log_carrots,
            last_log_time,
            cycle_count,
            harvest_count,
            replant_count,
            unready_count,
        )

    quick_print(
        "main2", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " replant=", replant_count[0],
        " unready=", unready_count[0],
    )


def main3_worker(exit_condition):
    for _ in range(get_world_size()):
        if get_ground_type() != Grounds.Soil:
            till()
        move(North)

    while not exit_condition():
        while get_water() < min(num_items(Items.Water) / 100, 0.75):
            use_item(Items.Water)
        if can_harvest():
            harvest()
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Carrot)
        move(North)


def main3(count=100000000):
    set_world_size(5)
    quick_print("main3", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    def exit_condition():
        return num_items(Items.Carrot) >= count

    main3_worker(exit_condition)
    quick_print("main3", " done carrots=", num_items(Items.Carrot), " time=", get_time())


def main4(count=100000000):
    set_world_size(SINGLE_FIELD_SIZE)
    known_entity = init_main4_anchors()

    cycle_count = [0]
    harvest_count = [0]
    reroll_count = [0]
    last_log_carrots = [0]
    last_log_time = [0]

    quick_print("main4", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    while num_items(Items.Carrot) < count:
        process_main4_anchor(1, 1, harvest_count, reroll_count, known_entity)
        process_main4_anchor(3, 1, harvest_count, reroll_count, known_entity)
        process_main4_anchor(1, 3, harvest_count, reroll_count, known_entity)
        process_main4_anchor(3, 3, harvest_count, reroll_count, known_entity)

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_main4(last_log_carrots, last_log_time, cycle_count, harvest_count, reroll_count)

    quick_print(
        "main4", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " reroll=", reroll_count[0],
    )


def init_main4_anchors():
    known_entity = make_main4_known_entities()
    for y in range(SINGLE_FIELD_SIZE):
        for x in range(SINGLE_FIELD_SIZE):
            goto(x, y)
            if is_main4_anchor(x, y):
                if get_ground_type() != Grounds.Soil:
                    till()
                if get_entity_type() != Entities.Carrot:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Carrot)
                    roll_seed_reroll = [0]
                    set_main4_known_entity(known_entity, x, y, Entities.Carrot)
                    roll_main4_bush_companion(roll_seed_reroll, known_entity)
                else:
                    set_main4_known_entity(known_entity, x, y, Entities.Carrot)
            else:
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                set_main4_known_entity(known_entity, x, y, Entities.Bush)
    return known_entity


def make_main4_known_entities():
    known_entity = []
    for _ in range(SINGLE_FIELD_SIZE):
        row = []
        for _ in range(SINGLE_FIELD_SIZE):
            row.append(None)
        known_entity.append(row)
    return known_entity


def set_main4_known_entity(known_entity, x, y, entity):
    known_entity[y][x] = entity


def get_main4_known_entity(known_entity, x, y):
    return known_entity[y][x]


def process_main4_anchor(x, y, harvest_count, reroll_count, known_entity):
    goto(x, y)
    if get_entity_type() == Entities.Carrot:
        if can_harvest():
            harvest()
            harvest_count[0] = harvest_count[0] + 1
            plant(Entities.Carrot)
            set_main4_known_entity(known_entity, x, y, Entities.Carrot)
            roll_main4_bush_companion(reroll_count, known_entity)
            water_main4_anchor()
        else:
            water_main4_anchor()
    else:
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)
        set_main4_known_entity(known_entity, x, y, Entities.Carrot)
        roll_main4_bush_companion(reroll_count, known_entity)
        water_main4_anchor()


def roll_main4_bush_companion(reroll_count, known_entity):
    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            companion_pos = companion[1]
            if companion_entity == Entities.Bush and not is_main4_anchor(companion_pos[0], companion_pos[1]):
                if get_main4_known_entity(known_entity, companion_pos[0], companion_pos[1]) == Entities.Bush:
                    return
                origin_x = get_pos_x()
                origin_y = get_pos_y()
                goto(companion_pos[0], companion_pos[1])
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                set_main4_known_entity(known_entity, companion_pos[0], companion_pos[1], Entities.Bush)
                goto(origin_x, origin_y)
                return
        harvest()
        plant(Entities.Carrot)
        set_main4_known_entity(known_entity, get_pos_x(), get_pos_y(), Entities.Carrot)
        reroll_count[0] = reroll_count[0] + 1


def water_main4_anchor():
    if num_items(Items.Water) > 2:
        use_item(Items.Water, 3)
    elif num_items(Items.Water) > 1:
        use_item(Items.Water, 2)
    elif num_items(Items.Water) > 0:
        use_item(Items.Water)


def maybe_log_main4(last_log_carrots, last_log_time, cycle_count, harvest_count, reroll_count):
    curr_carrots = num_items(Items.Carrot)
    if curr_carrots < last_log_carrots[0] + 10000000:
        return

    curr_time = get_time()
    quick_print(
        "main4", " progress carrots=", curr_carrots,
        " time=", curr_time,
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " reroll=", reroll_count[0],
        " dcarrots=", curr_carrots - last_log_carrots[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_carrots[0] = curr_carrots
    last_log_time[0] = curr_time


def is_main4_anchor(x, y):
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
    main4()
