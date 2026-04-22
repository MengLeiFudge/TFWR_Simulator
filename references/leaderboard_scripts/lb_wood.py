from __builtins__ import *


# Wood multi 版本结论
# main1: 32x32 棋盘（(x+y)%2==0 为 Tree，其余 Bush），32 个 drone 每机 1 行。
#        Tree 基础 yield = 5 * 2^(Trees-1) = 5 * 512 = 2560；companion match 乘 160。
#        和 hay 不同，Tree 的 companion pool 是 {Grass, Bush, Carrot}（不是 Tree 自己）。
#        棋盘排布下，Bush 在 L1<=3 邻居里占 16/24；Bush companion 命中率 1/3 * 2/3 = 2/9。
#        期望 harvest ≈ 2560 * (1 + 160 * 2/9) ≈ 93k wood。1024 格 / 2B 池子能覆盖目标。


def main1():
    set_world_size(32)
    init_checkerboard()
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


def init_checkerboard():
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
            if (x + y) % 2 == 0:
                if get_entity_type() != Entities.Tree:
                    plant(Entities.Tree)
            else:
                if get_entity_type() != Entities.Bush:
                    plant(Entities.Bush)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


def row_thread():
    goal = 10000000000
    y = get_pos_y()
    while num_items(Items.Wood) < goal:
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Tree:
                if can_harvest():
                    harvest()
                    plant(Entities.Tree)
            elif entity == Entities.Bush:
                pass
            else:
                x = get_pos_x()
                if (x + y) % 2 == 0:
                    plant(Entities.Tree)
                else:
                    plant(Entities.Bush)
            move(East)
    if y == 31:
        quick_print("main1 done wood=", num_items(Items.Wood), " time=", get_time())


if __name__ == "__main__":
    main1()
