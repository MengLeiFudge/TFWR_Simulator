from __builtins__ import *
# 淘汰候选归档：lb_cactus_single | 原实验路径 .codex/nonreset-100-20261108/cactus-frontier-bound-v1/lb_cactus_single.py
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。

def lb_cactus_single():
    global s
    global m
    global board
    set_world_size(8)
    clear()
    s = get_world_size()
    m = s - 1
    board = {}
    frontier = {(0, 0)}
    wrap = [0, 1, 2, 3, 4, 3, 2, 1]
    last = get_time()
    for _ in range(s * s):
        cx = get_pos_x()
        cy = get_pos_y()
        best = None
        score = 10000
        for x, y in frontier:
            bound = 0
            if x > 0:
                bound = board[(x - 1, y)]
            if y > 0:
                bound = max(bound, board[(x, y - 1)])
            distance = wrap[x - cx] + wrap[y - cy]
            candidate = distance + 20 * bound
            if candidate < score:
                score = candidate
                best = (x, y)
        x, y = best
        frontier.remove(best)
        move_to(x, y)
        till()
        plant(Entities.Cactus)
        last = get_time()
        perform_insertion_sort()
        if x + 1 < s and (x + 1, y) not in board and (y == 0 or (x + 1, y - 1) in board):
            frontier.add((x + 1, y))
        if y + 1 < s and (x, y + 1) not in board and (x == 0 or (x - 1, y + 1) in board):
            frontier.add((x, y + 1))
    while get_time() - last < 1:
        do_a_flip()
    harvest()
    quick_print("cactus_done", get_time(), num_items(Items.Cactus))


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


def perform_insertion_sort():
    while True:
        v = measure()
        x, y = get_pos_x(), get_pos_y()

        if x > 0:
            vw = measure(West)
            if v < vw:
                vs = measure(South)
                if y > 0 and vw < vs:
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
            if v < vs:
                if x > 0 and vs < vw:
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


if __name__ == "__main__":
    lb_cactus_single()
