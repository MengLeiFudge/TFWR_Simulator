from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/leaderboard-astra/github-dinosaur-sunflowers/lb_dinosaur_safe.py
# 私有候选：边界绕行、成对列捷径与后期填隙；尚无实机完整成绩。
# Copyright (c) 2026 enihsyou, MIT；原文及完整许可保存在本目录。

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
    l = s * s // 2  # 大于这个长度就强制走汉密顿路径

    dir = East
    snake = 0
    while True:
        x, y = get_pos_x(), get_pos_y()
        if get_entity_type() == Entities.Apple:
            snake += 1
            wx, wy = measure()  # ty: ignore

        # 不留缝隙地占满空间，强迫果子生成在前方，提速 10%
        if snake > l:
            if y == 0 and can_move(North) and x % 2 == 1:
                for _ in range(m - 1):  # 避开最北的一行
                    # 到苹果立即返回外层更新目标；移动失败则结束本条蛇。
                    if not move(North):
                        return
                    if get_entity_type() == Entities.Apple:
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
