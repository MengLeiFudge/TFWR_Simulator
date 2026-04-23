from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main1，32x32 Grass/Bush 棋盘多机基线。


def main1():
    set_world_size(32)
    # 初始化：整图 till 成 Soil，再按 (x+y)%2 铺 Grass/Bush。全部由 main 机一次性打底，
    # 然后再 spawn 30 个 drone 各接管一行；主机接管最后一行。
    init_checkerboard()
    # 回到 (0, 0)
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
                if get_entity_type() != Entities.Grass:
                    plant(Entities.Grass)
            else:
                if get_entity_type() != Entities.Bush:
                    plant(Entities.Bush)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


# 每行线程：在自己所在行 y 沿 East 扫；碰到成熟 Grass 就 harvest+plant，否则跳过。
def row_thread():
    goal = 2000000000
    y = get_pos_y()
    while num_items(Items.Hay) < goal:
        x_start = get_pos_x()
        for _ in range(32):
            entity = get_entity_type()
            if entity == Entities.Grass:
                if can_harvest():
                    harvest()
                    plant(Entities.Grass)
            elif entity == Entities.Bush:
                # Bush 不需要重种；它只做 companion 目标。
                pass
            else:
                # 空格或其他：按棋盘回填
                x = get_pos_x()
                if (x + y) % 2 == 0:
                    plant(Entities.Grass)
                else:
                    plant(Entities.Bush)
            move(East)
    # 只由某台 drone 报告 done，避免 32 台同时 quick_print。主机的 y==31。
    if y == 31:
        quick_print("main1 done hay=", num_items(Items.Hay), " time=", get_time())


if __name__ == "__main__":
    main1()
