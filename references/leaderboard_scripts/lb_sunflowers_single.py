from __builtins__ import *

# 10:35.599
def lb_sunflowers_single():
    set_world_size(SINGLE_FIELD_SIZE)
    size = get_world_size()
    harvest_count = 0
    sweep_count = 0
    last_log_power = 0

    # 单机没有多机规模优势，这里主动放弃严格最大花瓣管理，换取更高重种刷新频率。
    init_field(size)
    quick_print("lb_sunflowers_single", " init power=", num_items(Items.Power), " time=", get_time())

    while num_items(Items.Power) < SINGLE_POWER_GOAL:
        harvest_count = sweep_field(size, harvest_count)
        sweep_count = sweep_count + 1
        current_power = num_items(Items.Power)
        if current_power >= last_log_power + 1000:
            quick_print(
                "lb_sunflowers_single", " progress power=", current_power,
                " sweeps=", sweep_count,
                " harvest=", harvest_count,
                " time=", get_time(),
            )
            last_log_power = current_power


def init_field(size):
    direction = East
    for row in range(size):
        for col in range(size):
            prepare_sunflower()
            if col < size - 1:
                move(direction)
        if row < size - 1:
            move(North)
            direction = opposite_horizontal(direction)
    move(North)


SINGLE_POWER_GOAL = 10000
SINGLE_FIELD_SIZE = 6


def sweep_field(size, harvest_count):
    direction = East
    for row in range(size):
        for col in range(size):
            # 只沿相邻格蛇形前进，避免旧分桶路线反复 move_to 的管理成本。
            if can_harvest():
                harvest()
                harvest_count = harvest_count + 1
                if num_items(Items.Power) >= SINGLE_POWER_GOAL:
                    quick_print("lb_sunflowers_single", " done power=", num_items(Items.Power), " time=", get_time(), " harvest=", harvest_count)
                    return harvest_count
                plant(Entities.Sunflower)
                water_if_available()
            else:
                water_if_available()
            if col < size - 1:
                move(direction)
        if row < size - 1:
            move(North)
            direction = opposite_horizontal(direction)
    move(North)
    return harvest_count


def prepare_sunflower():
    if get_ground_type() != Grounds.Soil:
        till()
    entity = get_entity_type()
    if entity != Entities.Sunflower:
        if entity != None:
            harvest()
        plant(Entities.Sunflower)
    water_if_available()


def opposite_horizontal(direction):
    if direction == East:
        return West
    return East


def water_if_available():
    if get_water() < 0.425 and num_items(Items.Water) > SINGLE_FIELD_SIZE:
        use_item(Items.Water)


if __name__ == "__main__":
    lb_sunflowers_single()
