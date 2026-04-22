from __builtins__ import *


# Carrots multi 版本结论
# main1: 32x32 满田胡萝卜，32 个 drone 每机 1 行，直接 harvest+replant 循环。
#        lb_carrots_single main2 验证过“胡萝卜不值得 reroll companion”的结论，
#        多机更没必要卷 companion——单机 25 格时 reroll 冲突就已经压过收益。
#        Carrot 基础 yield = 2^(Carrots-2) = 2^8 = 256；随机 companion 命中时再乘 160。
#        本版只吃自然命中：靠全田 1024 株 carrot 的 bulk 吞吐覆盖 2B 目标做首版。


def main1():
    set_world_size(32)
    init_all_carrots()
    goto(0, 0)
    for _ in range(31):
        spawn_drone(row_thread)
        move(North)
    row_thread()


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


def init_all_carrots():
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
            if get_ground_type() != Grounds.Soil:
                till()
            if get_entity_type() != Entities.Carrot:
                plant(Entities.Carrot)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


def row_thread():
    goal = 2000000000
    y = get_pos_y()
    while num_items(Items.Carrot) < goal:
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Carrot:
                if can_harvest():
                    harvest()
                    plant(Entities.Carrot)
            else:
                if entity != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Carrot)
            move(East)
    if y == 31:
        quick_print("main1 done carrots=", num_items(Items.Carrot), " time=", get_time())


if __name__ == "__main__":
    main1()
