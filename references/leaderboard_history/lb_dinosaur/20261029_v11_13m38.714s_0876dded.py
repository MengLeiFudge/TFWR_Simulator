from __builtins__ import *
# 历史提交归档：lb_dinosaur | 初次提交 2026-10-29 (0876dded) | 优化：采用恐龙边界绕行与后期填隙策略
# 完整轮时间：13:38.714（官方完整9轮，request159）；本地三seed819.568663秒，短时2轮811.857秒。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0a257bbd27f0520464f5efe3baefe74c7d4f7168。

def lb_dinosaur():
    clear()
    change_hat(Hats.Dinosaur_Hat)
    cycle_loop()
    change_hat(Hats.Brown_Hat)

def cycle_loop():
    # 参照这个地址来实现
    # https://www.reddit.com/r/TheFarmerWasReplaced/comments/1o90hxs/my_sna_i_mean_dinosaur_algorithm/
    s = get_world_size()
    m = s - 1
    l = s * s // 2  # 苹果观测次数阈值；直段可能经过苹果，因此不等于精确尾长。

    dir = East
    snake = 0
    while True:
        x, y = get_pos_x(), get_pos_y()
        if get_entity_type() == Entities.Apple:
            snake += 1
            wx, wy = measure()  # ty: ignore

        # 后期优先填满成对列间的空隙，缩小苹果可生成的区域。
        if snake > l:
            if y == 0 and can_move(North) and x % 2 == 1:
                for _ in range(m - 1):  # 避开最北的一行
                    # 碰尾只结束这段直走，下一轮仍按当前位置选路。
                    if not move(North):
                        break
                continue

        # 访问中心区域的果子
        if x != 0 and x != m:  # 不在左右两侧
            if (x == wx or x + 1 == wx) and x % 2 == 1:
                if can_move(North) and wy > y and wy != m:  # 向北可以到达苹果
                    for _ in range(wy - y):
                        move(North)
                    continue
            if (x == wx or x - 1 == wx) and x % 2 == 0:
                if can_move(South) and y > wy and wy != 0:  # 向南可以前往苹果
                    for _ in range(y - wy):
                        move(South)
                    continue

        # 围着操场逆时针转圈
        if dir == East:
            if y != 0 and can_move(South):
                while move(South) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == m:
                dir = North  # 在边界转向, 下面直接 move 节约一个循环
            if not (move(dir) or move(North)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == West:
            if y == m and can_move(dir) and x > wx + 1:
                for _ in range(x - wx - 1 - 1):  # 考虑到奇偶性，多减 1
                    move(dir)  # 快速移过最北边, 因为那是回程的线
            if y != m and can_move(North):
                while move(North) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == 0:
                dir = South  # 在边界转向
            if not (move(dir) or move(South)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == South:
            if x != 0 and can_move(West):
                move(West)  # 回归边线
                continue
            if x == 0 and y != 0:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not (can_move(dir) or can_move(East)):
                    break  # 碰到尾巴
            dir = East  # 在边界转向
            continue
        if dir == North:
            if x != m and can_move(East):
                move(East)  # 回归边线
                continue
            if x == m and y != m:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not can_move(dir) and not can_move(West):
                    break  # 碰到尾巴
            dir = West  # 在边界转向
            continue


if __name__ == "__main__":
    lb_dinosaur()
