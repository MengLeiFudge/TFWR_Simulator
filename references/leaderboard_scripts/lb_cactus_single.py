from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main1，8x8 全图 reroll 到 variant=9 后统一 harvest。


def main1():
    set_world_size(8)
    goal = 131072
    while num_items(Items.Cactus) < goal:
        goto(0, 0)
        plant_row_wave()
        goto(0, 0)
        harvest()
    quick_print("main1 done cactus=", num_items(Items.Cactus), " time=", get_time())


def goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


# 蛇形扫图种 cactus，每格 reroll 到 variant=9；扫完全图后统一 harvest 一次。
def plant_row_wave():
    size = get_world_size()
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
            if get_ground_type() == Grounds.Grassland:
                till()
            plant(Entities.Cactus)
            while measure() != 9:
                harvest()
                plant(Entities.Cactus)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


if __name__ == "__main__":
    main1()
