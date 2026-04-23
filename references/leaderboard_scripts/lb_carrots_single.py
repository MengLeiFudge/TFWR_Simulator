from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2；main1 保留做高冲突 claim 对照。


def create_entity_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        ret.append(row)
    return ret


def create_number_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(0)
        ret.append(row)
    return ret


def goto(tx, ty):
    size = get_world_size()
    half_size = size // 2
    x = get_pos_x()
    y = get_pos_y()

    dx = (tx - x) % size
    if dx <= half_size:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)

    dy = (ty - y) % size
    if dy <= half_size:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def is_main1_carrot_slot(x, y):
    return (x + y) % 2 == 0


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


def release_main1_claim(
        x,
        y,
        support_entity,
        support_count,
        companion_entity,
        companion_x,
        companion_y):
    ct = companion_entity[x][y]
    if ct == None:
        return

    cx = companion_x[x][y]
    cy = companion_y[x][y]
    if not is_main1_carrot_slot(cx, cy):
        support_count[cx][cy] = support_count[cx][cy] - 1
        if support_count[cx][cy] <= 0:
            support_count[cx][cy] = 0
            support_entity[cx][cy] = None

    companion_entity[x][y] = None
    companion_x[x][y] = 0
    companion_y[x][y] = 0


def roll_main1_carrot_companion(
        support_entity,
        support_count,
        reroll_count):
    while True:
        ct, (cx, cy) = get_companion()

        if is_main1_carrot_slot(cx, cy):
            if ct != Entities.Carrot:
                reroll_count[0] = reroll_count[0] + 1
                harvest()
                plant(Entities.Carrot)
                maybe_water_main1_slot()
                continue
            return ct, cx, cy

        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            reroll_count[0] = reroll_count[0] + 1
            harvest()
            plant(Entities.Carrot)
            maybe_water_main1_slot()
            continue

        return ct, cx, cy


def process_main1_support_slot(
        x,
        y,
        support_entity,
        support_count,
        support_replant_count,
        support_keep_count):
    if support_count[x][y] <= 0:
        return

    ct = support_entity[x][y]
    entity = get_entity_type()
    if entity == ct:
        support_keep_count[0] = support_keep_count[0] + 1
        return

    if entity != None:
        support_replant_count[0] = support_replant_count[0] + 1
        harvest()

    plant(ct)


def maybe_log_main1(
        last_log_carrots,
        last_log_time,
        cycle_count,
        harvest_count,
        unready_count,
        reroll_count,
        support_replant_count,
        support_keep_count):
    curr_carrots = num_items(Items.Carrot)
    if curr_carrots < last_log_carrots[0] + 10000000:
        return

    curr_time = get_time()
    quick_print(
        "main1", " progress carrots=", curr_carrots,
        " time=", curr_time,
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " reroll=", reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
        " dcarrots=", curr_carrots - last_log_carrots[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_carrots[0] = curr_carrots
    last_log_time[0] = curr_time


def main1(count=100000000):
    set_world_size(5)
    init_main1_soil()

    support_entity = create_entity_grid(5)
    support_count = create_number_grid(5)
    companion_entity = create_entity_grid(5)
    companion_x = create_number_grid(5)
    companion_y = create_number_grid(5)

    cycle_count = [0]
    harvest_count = [0]
    unready_count = [0]
    reroll_count = [0]
    support_replant_count = [0]
    support_keep_count = [0]
    last_log_carrots = [0]
    last_log_time = [0]

    quick_print("main1", " init_time=", get_time(), " carrots=", num_items(Items.Carrot))

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
                if is_main1_carrot_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Carrot:
                        if not can_harvest():
                            unready_count[0] = unready_count[0] + 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue

                        release_main1_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            companion_entity,
                            companion_x,
                            companion_y,
                        )
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                    elif entity != None:
                        harvest()

                    plant(Entities.Carrot)
                    maybe_water_main1_slot()
                    ct, cx, cy = roll_main1_carrot_companion(
                        support_entity,
                        support_count,
                        reroll_count,
                    )
                    companion_entity[x][y] = ct
                    companion_x[x][y] = cx
                    companion_y[x][y] = cy
                    if not is_main1_carrot_slot(cx, cy):
                        support_entity[cx][cy] = ct
                        support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main1_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                        support_replant_count,
                        support_keep_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_main1(
            last_log_carrots,
            last_log_time,
            cycle_count,
            harvest_count,
            unready_count,
            reroll_count,
            support_replant_count,
            support_keep_count,
        )

    quick_print(
        "main1", " done carrots=", num_items(Items.Carrot),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " reroll=", reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
    )


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


if __name__ == "__main__":
    main2()
