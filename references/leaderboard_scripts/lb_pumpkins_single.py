from __builtins__ import *


# Pumpkins single 版本结论
# main1: 旧版 6x6 简单双循环，保留做对照。
# main2: 6x6 满田波次策略。南瓜不走 companion，而是按 mega pumpkin 连通块收菜，
#        所以主目标是尽量维持整块南瓜田一起长成、一起结算。
#
# 当前建议：
# 1. 默认从 main2 继续优化。
# 2. 死南瓜立即补种，优先保住整田连通。
# 3. 单榜优化重点是整波成熟后的收割顺序，不是像树/胡萝卜那样靠 companion 刷新。


def main1():
    set_world_size(6)
    N = 6
    while num_items(Items.Pumpkin) < 10000000:
        for i in range(N):
            for j in range(N):
                if i == 0 and j == 0:
                    ca = measure()
                elif i == N - 1 and j == N - 1:
                    if measure() == ca:
                        harvest()
                entity_type = get_entity_type()
                if entity_type == Entities.Grass:
                    harvest()
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    plant(Entities.Pumpkin)
                elif entity_type == Entities.Dead_Pumpkin or entity_type == None:
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    plant(Entities.Pumpkin)
                move(East)
            move(North)


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


def maybe_water_main2_slot():
    if get_water() < 0.75 and num_items(Items.Water) >= 3:
        use_item(Items.Water, 3)
    elif get_water() < 0.25 and num_items(Items.Water) >= 1:
        use_item(Items.Water)


def init_main2_soil(size):
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


def prepare_main2_wave(size):
    pending = []
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
            entity = get_entity_type()
            if entity == Entities.Grass:
                harvest()
                plant(Entities.Pumpkin)
                maybe_water_main2_slot()
                append(pending, (x, y))
            elif entity == Entities.Dead_Pumpkin or entity == None:
                plant(Entities.Pumpkin)
                maybe_water_main2_slot()
                append(pending, (x, y))
            elif entity == Entities.Pumpkin:
                if can_harvest():
                    pass
                else:
                    maybe_water_main2_slot()
                    append(pending, (x, y))
            else:
                harvest()
                plant(Entities.Pumpkin)
                maybe_water_main2_slot()
                append(pending, (x, y))

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)

    return pending


def wait_main2_wave(pending):
    while len(pending) > 0:
        next_pending = []
        for pos in pending:
            goto(pos[0], pos[1])
            entity = get_entity_type()
            if entity == Entities.Pumpkin:
                if can_harvest():
                    continue
                maybe_water_main2_slot()
                append(next_pending, pos)
                continue

            if entity == Entities.Grass:
                harvest()
            elif entity != None and entity != Entities.Dead_Pumpkin:
                harvest()

            plant(Entities.Pumpkin)
            maybe_water_main2_slot()
            append(next_pending, pos)

        pending = next_pending


def harvest_main2_wave(size, harvest_count):
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
            if get_entity_type() == Entities.Pumpkin and can_harvest():
                harvest()
                harvest_count[0] = harvest_count[0] + 1

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def maybe_log_main2(
        last_log_pumpkin,
        last_log_time,
        wave_count,
        harvest_count):
    curr_pumpkin = num_items(Items.Pumpkin)
    if curr_pumpkin < last_log_pumpkin[0] + 500000:
        return

    curr_time = get_time()
    quick_print(
        "main2", " progress pumpkin=", curr_pumpkin,
        " time=", curr_time,
        " waves=", wave_count[0],
        " harvest=", harvest_count[0],
        " dpumpkin=", curr_pumpkin - last_log_pumpkin[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_pumpkin[0] = curr_pumpkin
    last_log_time[0] = curr_time


def main2(count=10000000):
    size = 6
    set_world_size(size)
    init_main2_soil(size)

    wave_count = [0]
    harvest_count = [0]
    last_log_pumpkin = [0]
    last_log_time = [0]

    quick_print("main2", " init_time=", get_time(), " pumpkin=", num_items(Items.Pumpkin))

    while num_items(Items.Pumpkin) < count:
        pending = prepare_main2_wave(size)
        wait_main2_wave(pending)
        harvest_main2_wave(size, harvest_count)
        wave_count[0] = wave_count[0] + 1
        maybe_log_main2(
            last_log_pumpkin,
            last_log_time,
            wave_count,
            harvest_count,
        )

    quick_print(
        "main2", " done pumpkin=", num_items(Items.Pumpkin),
        " time=", get_time(),
        " waves=", wave_count[0],
        " harvest=", harvest_count[0],
    )


if __name__ == "__main__":
    main2()
