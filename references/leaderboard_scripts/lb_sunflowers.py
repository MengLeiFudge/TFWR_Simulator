from __builtins__ import *

# 3:57.101
def lb_sunflowers():
    set_world_size(FIELD_SIZE)
    for _ in range(FIELD_SIZE - 1):
        spawn_drone(row_worker)
        move(North)
    row_worker()


POWER_GOAL = 100000
FIELD_SIZE = 32


def row_worker():
    for _ in range(FIELD_SIZE):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Sunflower)
        water_if_available()
        move(East)

    while num_items(Items.Power) < POWER_GOAL:
        if can_harvest():
            harvest()
            if num_items(Items.Power) >= POWER_GOAL:
                return
            plant(Entities.Sunflower)
            water_if_available()
        move(East)


def water_if_available():
    if get_water() < 0.425 and num_items(Items.Water) > FIELD_SIZE:
        use_item(Items.Water)


if __name__ == "__main__":
    lb_sunflowers()
