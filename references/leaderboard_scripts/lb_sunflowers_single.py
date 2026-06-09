from __builtins__ import *

# 10:35.599
def lb_sunflowers_single():
    set_world_size(SINGLE_FIELD_SIZE)
    size = get_world_size()

    # 单机没有多机规模优势，这里主动放弃严格最大花瓣管理，换取更高重种刷新频率。
    init_field(size)
    current_power = num_items(Items.Power)
    quick_print("lb_sunflowers_single", " init power=", current_power, " time=", get_time())

    while current_power < SINGLE_POWER_GOAL:
        current_power = sweep_field(size, current_power)


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


def sweep_field(size, current_power):
    direction = East
    for row in range(size):
        for col in range(size):
            # 只沿相邻格蛇形前进，避免旧分桶路线反复 move_to 的管理成本。
            if can_harvest():
                harvest()
                current_power = num_items(Items.Power)
                if current_power >= SINGLE_POWER_GOAL:
                    quick_print("lb_sunflowers_single", " done power=", current_power, " time=", get_time())
                    return current_power
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
    return current_power


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
