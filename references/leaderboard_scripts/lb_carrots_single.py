from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2；main1 保留做高冲突 claim 对照。






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


if __name__ == "__main__":
    main3()
