from __builtins__ import *


# Cactus single 版本结论
# main1: 8x8 世界（单机 Expand 上限 5），全场种成 variant=9 让所有 cactus 变同簇，
#        一次 harvest 就能 `cactus_cluster` 到整盘 64 格，yield = 64^2 = 4096，
#        每轮目标 131072 / 4096 = 32 轮即达标。
#        `is_sorted_cactus` 要求 N/E 邻居 >= self、S/W 邻居 <= self，全 9 自动满足。
#        代码结构借自 lb_cactus.main2 的单线程版，去掉 spawn_drone、删掉 do_a_flip（UI 动作）。


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


# 蛇形扫图种 cactus，每格 reroll 到 variant=9；扫完全图后集体 harvest 一次。
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
