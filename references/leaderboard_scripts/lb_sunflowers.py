from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main4，32x32 每行一机，高吞吐收割；有水才补水。


POWER_GOAL = 100000
FIELD_SIZE = 32


def main4():
    set_world_size(FIELD_SIZE)
    for _ in range(FIELD_SIZE - 1):
        spawn_drone(main4_row_worker)
        move(North)
    main4_row_worker()


def main4_row_worker():
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
    main4()
