from __builtins__ import *


SINGLE_POWER_GOAL = 10000
SINGLE_FIELD_SIZE = 6


def move_to(pos):
    x, y = pos
    size = get_world_size()
    dx = x - get_pos_x()
    if abs(dx) > size // 2:
        if dx > 0:
            for _ in range(size - dx):
                move(West)
        else:
            for _ in range(size + dx):
                move(East)
    else:
        if dx < 0:
            for _ in range(-dx):
                move(West)
        elif dx > 0:
            for _ in range(dx):
                move(East)
    dy = y - get_pos_y()
    if abs(dy) > size // 2:
        if dy > 0:
            for _ in range(size - dy):
                move(South)
        else:
            for _ in range(size + dy):
                move(North)
    else:
        if dy < 0:
            for _ in range(-dy):
                move(South)
        elif dy > 0:
            for _ in range(dy):
                move(North)


def main():
    set_world_size(SINGLE_FIELD_SIZE)
    size = get_world_size()
    while True:
        power = []
        for _ in range(16):
            power.append([])
        for i in range(size):
            for j in range(size):
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Sunflower)
                power[measure()].append((i, j))
                if get_water() < num_items(Items.Water) / 100:
                    use_item(Items.Water)
                move(North)
            move(East)
        t = size * size
        for sunflowers in range(15, 6, -1):
            for pos in power[sunflowers]:
                move_to(pos)
                while not can_harvest():
                    if get_water() < num_items(Items.Water) / 100:
                        use_item(Items.Water)
                harvest()
                if num_items(Items.Power) >= SINGLE_POWER_GOAL:
                    return
                t -= 1
                if t < 10:
                    break


def main2():
    set_world_size(SINGLE_FIELD_SIZE)
    size = get_world_size()
    harvest_count = 0
    sweep_count = 0
    last_log_power = 0

    # 单机没有多机规模优势，这里主动放弃严格最大花瓣管理，换取更高重种刷新频率。
    init_main2_field(size)
    quick_print("main2", " init power=", num_items(Items.Power), " time=", get_time())

    while num_items(Items.Power) < SINGLE_POWER_GOAL:
        harvest_count = sweep_main2_field(size, harvest_count)
        sweep_count = sweep_count + 1
        current_power = num_items(Items.Power)
        if current_power >= last_log_power + 1000:
            quick_print(
                "main2", " progress power=", current_power,
                " sweeps=", sweep_count,
                " harvest=", harvest_count,
                " time=", get_time(),
            )
            last_log_power = current_power


def init_main2_field(size):
    direction = East
    for row in range(size):
        for col in range(size):
            prepare_main2_sunflower()
            if col < size - 1:
                move(direction)
        if row < size - 1:
            move(North)
            direction = opposite_horizontal(direction)
    move(North)


def sweep_main2_field(size, harvest_count):
    direction = East
    for row in range(size):
        for col in range(size):
            # 只沿相邻格蛇形前进，避免旧分桶路线反复 move_to 的管理成本。
            if can_harvest():
                harvest()
                harvest_count = harvest_count + 1
                if num_items(Items.Power) >= SINGLE_POWER_GOAL:
                    quick_print("main2", " done power=", num_items(Items.Power), " time=", get_time(), " harvest=", harvest_count)
                    return harvest_count
                plant(Entities.Sunflower)
                water_main2_if_available()
            else:
                water_main2_if_available()
            if col < size - 1:
                move(direction)
        if row < size - 1:
            move(North)
            direction = opposite_horizontal(direction)
    move(North)
    return harvest_count


def prepare_main2_sunflower():
    if get_ground_type() != Grounds.Soil:
        till()
    entity = get_entity_type()
    if entity != Entities.Sunflower:
        if entity != None:
            harvest()
        plant(Entities.Sunflower)
    water_main2_if_available()


def opposite_horizontal(direction):
    if direction == East:
        return West
    return East


def water_main2_if_available():
    if get_water() < 0.425 and num_items(Items.Water) > SINGLE_FIELD_SIZE:
        use_item(Items.Water)


main2()
