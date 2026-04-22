from __builtins__ import *


# Hay multi 版本结论
# main1: 32x32 棋盘（(x+y)%2==0 为 Grass，其余 Bush），32 个 drone 每机 1 行。
#        Grass 单次基础 yield = 2^(Grass-1) = 512；companion match 时乘 5<<Polyculture = 160 倍。
#        棋盘排布下，Grass 在 L1<=3 邻居里 Bush 占 16/24 个位置，期望 companion Bush 匹配率 ~2/9，
#        每次 harvest 期望 hay ≈ 18.4k。1024 格并行 => 足够覆盖 2B 目标做首版验证。
#        不做 reroll：hay_single main10 靠 reroll 榨干吞吐，但多机搜索空间复杂，首版先吃 baseline。


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


# 每行线程：在自己所在行 y，沿 East 扫；碰到 Grass 成熟就 harvest+plant，
# 否则跳过。为了省 tick，不做 reroll、不浇水：棋盘本来就让 bush 填 L1=3 邻居，
# 自然 match 率已到 2/9，再 reroll 几乎吃不到额外收益。
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
