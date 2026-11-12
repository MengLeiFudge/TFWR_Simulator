# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/github-strategy-search/enihsyou/cactus_single.py
set_world_size(8)
s = get_world_size()
m = s - 1


def move_to(tx, ty):
    cx, cy = get_pos_x(), get_pos_y()

    dx_east = (tx - cx) % s
    dx_west = s - dx_east
    if dx_east < dx_west:
        for _ in range(dx_east):
            move(East)
    else:
        for _ in range(dx_west):
            move(West)

    dy_north = (ty - cy) % s
    dy_south = s - dy_north
    if dy_north < dy_south:
        for _ in range(dy_north):
            move(North)
    else:
        for _ in range(dy_south):
            move(South)


# 记录每个位置的测量值
board = {}


def perform_insertion_sort():
    while True:
        v = measure()
        x, y = get_pos_x(), get_pos_y()

        if x > 0:
            vw = measure(West)
            if v < vw:  # ty: ignore
                vs = measure(South)
                if y > 0 and vw < vs:  # ty: ignore
                    board[(x, y - 1)] = v
                    board[(x, y)] = vs
                    swap(South)
                    # 判断移动到下一个位置后，是否还需要继续交换
                    if (
                        board[(x - 1, y - 1)] > v  # 还能和左边交换
                    ) or (
                        y > 1 and board[(x, y - 2)] > v  # 还能和下面交换
                    ):
                        move(South)
                    else:
                        break
                else:
                    board[(x - 1, y)] = v
                    board[(x, y)] = vw
                    swap(West)
                    if (
                        y > 0 and board[(x - 1, y - 1)] > v  # 还能和下面交换
                    ) or (
                        x > 1 and board[(x - 2, y)] > v  # 还能和左边交换
                    ):
                        move(West)
                    else:
                        break
                continue

        if y > 0:
            vs = measure(South)
            if v < vs:  # ty: ignore
                if x > 0 and vs < vw:  # ty: ignore
                    board[(x - 1, y)] = v
                    board[(x, y)] = vw
                    swap(West)
                    if (
                        board[(x - 1, y - 1)] > v  # 还能和下面交换
                    ) or (
                        x > 1 and board[(x - 2, y)] > v  # 还能和左边交换
                    ):
                        move(West)
                    else:
                        break
                else:
                    board[(x, y - 1)] = v
                    board[(x, y)] = vs
                    swap(South)
                    if (
                        x > 0 and board[(x - 1, y - 1)] > v  # 还能和左边交换
                    ) or (
                        y > 1 and board[(x, y - 2)] > v  # 还能和下面交换
                    ):
                        move(South)
                    else:
                        break
                continue

        board[(x, y)] = v
        break


# 走一个 x + y = i 形状的对角线，左下角是排好序的
POSITIONS = [
    {(0, 0)},
    #
    {(0, 1), (1, 0)},
    #
    {(0, 2), (1, 1), (2, 0)},
    #
    {(0, 3), (1, 2), (2, 1), (3, 0)},
    #
    {(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)},
    #
    {(0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)},
    #
    {(0, 6), (1, 5), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)},
    #
    {(0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)},
    #
    {(1, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1)},
    #
    {(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2)},
    #
    {(3, 7), (4, 6), (5, 5), (6, 4), (7, 3)},
    #
    {(4, 7), (5, 6), (6, 5), (7, 4)},
    #
    {(5, 7), (6, 6), (7, 5)},
    #
    # {(6, 7), (7, 6)},
    #
    # {(7, 7)},
]
#


last_plant_time = 0
max_dis = s + s
for diag_pos in POSITIONS:
    while diag_pos:
        x, y = get_pos_x(), get_pos_y()

        # 去往离当前最近的对角线上的点
        min_pos = None
        min_dis = max_dis
        for pos in diag_pos:
            mx, my = pos
            dis = abs(mx - x) + abs(my - y)
            if dis < min_dis:
                min_dis = dis
                min_pos = pos

        x, y = min_pos
        diag_pos.remove(min_pos)
        move_to(x, y)
        till()
        plant(Entities.Cactus)
        last_plant_time = get_time()
        perform_insertion_sort()

# 最后几株先种再排序
move_to(m, m - 1)
use_item(Items.Fertilizer)
harvest()  # harvest weird substance

till()
plant(Entities.Cactus)
use_item(Items.Fertilizer)
move(West)
move(North)  # at (m - 1, m)
till()
plant(Entities.Cactus)
use_item(Items.Fertilizer)
move(East)  # at (m, m)
till()
plant(Entities.Cactus)
use_item(Items.Fertilizer)
use_item(Items.Weird_Substance)
move(South)  # at (m, m - 1)
perform_insertion_sort()
move_to(m - 1, m)
perform_insertion_sort()
move_to(m, m)
perform_insertion_sort()
# 最后几株生长时间大于排序时间就有几率失败
while get_time() - last_plant_time < 0.97:
    continue
harvest()
