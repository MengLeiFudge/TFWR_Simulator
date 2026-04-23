from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main1，5x5 满图并记录 petal。


def create_number_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(0)
        ret.append(row)
    return ret


def maybe_water_main1_slot():
    if get_water() < 0.75 and num_items(Items.Water) >= 3:
        use_item(Items.Water, 3)
    elif get_water() < 0.25 and num_items(Items.Water) >= 1:
        use_item(Items.Water)


def init_main1_field(petals):
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
            if get_entity_type() != Entities.Sunflower:
                plant(Entities.Sunflower)
            maybe_water_main1_slot()
            petals[x][y] = measure()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def get_main1_max_petals(petals):
    max_petals = 0
    for x in range(5):
        for y in range(5):
            if petals[x][y] > max_petals:
                max_petals = petals[x][y]
    return max_petals


def maybe_log_main1(
        last_log_power,
        last_log_time,
        sweep_count,
        harvest_count,
        max_petals):
    curr_power = num_items(Items.Power)
    if curr_power < last_log_power[0] + 1000:
        return

    curr_time = get_time()
    quick_print(
        "main1", " progress power=", curr_power,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " max_petals=", max_petals,
        " dpower=", curr_power - last_log_power[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_power[0] = curr_power
    last_log_time[0] = curr_time


def main1(count=10000):
    set_world_size(5)

    petals = create_number_grid(5)
    init_main1_field(petals)

    sweep_count = [0]
    harvest_count = [0]
    last_log_power = [0]
    last_log_time = [0]

    quick_print("main1", " init_time=", get_time(), " power=", num_items(Items.Power))

    while num_items(Items.Power) < count:
        max_petals = get_main1_max_petals(petals)

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
                if entity != Entities.Sunflower:
                    if entity != None:
                        harvest()
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Sunflower)
                    maybe_water_main1_slot()
                    petals[x][y] = measure()
                elif can_harvest():
                    if petals[x][y] >= max_petals:
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                        plant(Entities.Sunflower)
                        maybe_water_main1_slot()
                        petals[x][y] = measure()
                else:
                    maybe_water_main1_slot()

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        sweep_count[0] = sweep_count[0] + 1
        maybe_log_main1(
            last_log_power,
            last_log_time,
            sweep_count,
            harvest_count,
            max_petals,
        )

    quick_print(
        "main1", " done power=", num_items(Items.Power),
        " time=", get_time(),
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
    )


if __name__ == "__main__":
    main1()
