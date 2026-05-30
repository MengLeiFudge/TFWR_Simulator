from __builtins__ import *

# 7:52.654
def lb_pumpkins_single():
    count = 10000000
    size = 6
    set_world_size(size)
    init_soil(size)

    wave_count = [0]
    harvest_count = [0]
    last_log_pumpkin = [0]
    last_log_time = [0]

    quick_print("lb_pumpkins_single", " init_time=", get_time(), " pumpkin=", num_items(Items.Pumpkin))

    while num_items(Items.Pumpkin) < count:
        pending = prepare_wave(size)
        wait_wave(pending)
        harvest_wave(size, harvest_count)
        wave_count[0] = wave_count[0] + 1
        maybe_log_progress(
            last_log_pumpkin,
            last_log_time,
            wave_count,
            harvest_count,
        )

    quick_print(
        "lb_pumpkins_single", " done pumpkin=", num_items(Items.Pumpkin),
        " time=", get_time(),
        " waves=", wave_count[0],
        " harvest=", harvest_count[0],
    )


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


def maybe_water_slot():
    if get_water() < 0.425 and num_items(Items.Water) >= 3:
        use_item(Items.Water, 3)


def init_soil(size):
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


def prepare_wave(size):
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
                maybe_water_slot()
                append(pending, (x, y))
            elif entity == Entities.Dead_Pumpkin or entity == None:
                plant(Entities.Pumpkin)
                maybe_water_slot()
                append(pending, (x, y))
            elif entity == Entities.Pumpkin:
                if can_harvest():
                    pass
                else:
                    maybe_water_slot()
                    append(pending, (x, y))
            else:
                harvest()
                plant(Entities.Pumpkin)
                maybe_water_slot()
                append(pending, (x, y))

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)

    return pending


def wait_wave(pending):
    while len(pending) > 0:
        next_pending = []
        for pos in pending:
            goto(pos[0], pos[1])
            entity = get_entity_type()
            if entity == Entities.Pumpkin:
                if can_harvest():
                    continue
                if len(pending) <= 6 and num_items(Items.Fertilizer) > 0:
                    use_item(Items.Fertilizer)
                    entity = get_entity_type()
                    if entity == Entities.Pumpkin and can_harvest():
                        continue
                maybe_water_slot()
                append(next_pending, pos)
                continue

            if entity == Entities.Grass:
                harvest()
            elif entity != None and entity != Entities.Dead_Pumpkin:
                harvest()

            plant(Entities.Pumpkin)
            maybe_water_slot()
            append(next_pending, pos)

        pending = next_pending


def harvest_wave(size, harvest_count):
    # 6x6 已合并后任意一格收割都会结算整块；不再浪费一整轮 6x6 扫描。
    goto(0, 0)
    if get_entity_type() == Entities.Pumpkin and can_harvest():
        harvest()
        harvest_count[0] = harvest_count[0] + 1


def maybe_log_progress(
        last_log_pumpkin,
        last_log_time,
        wave_count,
        harvest_count):
    curr_pumpkin = num_items(Items.Pumpkin)
    if curr_pumpkin < last_log_pumpkin[0] + 500000:
        return

    curr_time = get_time()
    quick_print(
        "lb_pumpkins_single", " progress pumpkin=", curr_pumpkin,
        " time=", curr_time,
        " waves=", wave_count[0],
        " harvest=", harvest_count[0],
        " dpumpkin=", curr_pumpkin - last_log_pumpkin[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_pumpkin[0] = curr_pumpkin
    last_log_time[0] = curr_time


if __name__ == "__main__":
    lb_pumpkins_single()
