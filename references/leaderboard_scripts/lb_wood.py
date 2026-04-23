from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main1，32x32 Tree/Bush 棋盘多机基线。


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
