from __builtins__ import *
# 淘汰候选归档：lb_carrots | 原实验路径 .codex/leaderboard-astra/carrots-direct-companion/lb_carrots.py
# 私有跨区直接满足伴生代表；完整时间未取得。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0f9dcb9479abcf8219819eaa38c0bd6f785196b3。

def lb_carrots():
    set_world_size(32)
    clear()
    child = spawn_drone(straight_move_do(BLOCK_H, North, spawn_drone_task1(North)))
    spawn_drone_task1(South)()
    wait_for(child)

W = 0.15
BLOCK_W, BLOCK_H = 4, 8


def traverse_rectangle(fn, w, h):
    fn()
    move(North)
    for i in range(w, 0, -2):
        for j in range(h, 1, -1):
            fn()
            if j != 2:
                move(North)
        move(East)
        for j in range(h, 1, -1):
            fn()
            if j != 2:
                move(South)
        if i != 2:
            move(East)
    move(South)
    for _ in range(1, w):
        fn()
        move(West)


def traverse_rectangle_if(fn, w, h):
    if fn():
        return False
    move(North)
    for i in range(w, 0, -2):
        for j in range(h, 1, -1):
            if fn():
                return False
            if j != 2:
                move(North)
        move(East)
        for j in range(h, 1, -1):
            if fn():
                return False
            if j != 2:
                move(South)
        if i != 2:
            move(East)
    move(South)
    for _ in range(1, w):
        if fn():
            return False
        move(West)

    return True


def work_drone_task():
    def on_eachcell():
        here = (get_pos_x(), get_pos_y())
        if get_water() < W and num_items(Items.Water) > 32:
            use_item(Items.Water)
        harvest()
        plant(Entities.Carrot)
        companion = get_companion()
        # 其他机可能在本格满足自己的请求；缺失请求直接留待下次巡田。
        if companion == None:
            return
        kind, pos = companion
        direct_goto(pos)
        if get_entity_type() != kind:
            harvest()
            plant(kind)
        direct_goto(here)

    def first_round():
        till()
        on_eachcell()

    def while_round():
        on_eachcell()
        return num_items(Items.Carrot) >= 2000000000

    traverse_rectangle(first_round, 4, 8)
    while traverse_rectangle_if(while_round, 4, 8):
        continue


def direct_goto(pos):
    x, y = pos
    dx = (x - get_pos_x()) % 32
    if dx <= 16:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(32 - dx):
            move(West)
    dy = (y - get_pos_y()) % 32
    if dy <= 16:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(32 - dy):
            move(South)


def straight_move_do(side_length, d, do):
    def fn():
        for _ in range(side_length):
            move(d)
        do()

    return fn


def spawn_drone_task1(face):
    def fn():
        child = spawn_drone(straight_move_do(BLOCK_H, face, spawn_drone_task2()))
        spawn_drone_task2()()
        wait_for(child)

    return fn


def spawn_drone_task2():
    def fn():
        child = spawn_drone(straight_move_do(BLOCK_W, East, spawn_drone_task3(East)))
        spawn_drone_task3(West)()
        wait_for(child)

    return fn


def spawn_drone_task3(face):
    def fn():
        children = []
        for _ in range(3):
            children.append(spawn_drone(work_drone_task))
            for _ in range(BLOCK_W):
                move(face)
        work_drone_task()
        for child in children:
            wait_for(child)

    return fn


if __name__ == "__main__":
    lb_carrots()
