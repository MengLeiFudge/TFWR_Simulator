from __builtins__ import *
# 全科技功能初版；来源 lb_carrots.py，本地对照见docs/functional-validation.md。
import production
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0f9dcb9479abcf8219819eaa38c0bd6f785196b3。

def carrot(target=-1):
    if not production.active(Items.Carrot, target):
        return
    set_world_size(32)
    clear()
    child = spawn_drone(straight_move_do(BLOCK_H, North, spawn_drone_task1(North, target)))
    spawn_drone_task1(South, target)()
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


def work_drone_task(target):
    wants = {}
    x_lower, y_lower = get_pos_x(), get_pos_y()
    x_upper, y_upper = x_lower + 4, y_lower + 8

    def on_eachcell():
        if not production.active(Items.Carrot, target):
            return
        t = (get_pos_x(), get_pos_y())

        # 满足当前位置的种植需求
        if t in wants:
            c = wants.pop(t)
            if get_entity_type() != c:
                harvest()
                if not plant(c):
                    return True
            return

        if get_water() < W and num_items(Items.Water) > 32:
            use_item(Items.Water, 4)
        while production.active(Items.Carrot, target):
            harvest()
            if not plant(Entities.Carrot):
                return True
            c, p = get_companion()
            x, y = p
            if x_lower <= x < x_upper and y_lower <= y < y_upper:
                if p in wants and wants[p] != c:
                    continue  # 和其他植物的请求种植的冲突
                wants[p] = c  # 标记格子接下来要种植的作物
                break
        return

    def first_round():
        till()
        on_eachcell()

    def while_round():
        if on_eachcell():
            quick_print("胡萝卜种植失败，本区域停止，等待补料后重新派工。")
            return True
        return not production.active(Items.Carrot, target)

    traverse_rectangle(first_round, 4, 8)
    while traverse_rectangle_if(while_round, 4, 8):
        continue


def straight_move_do(side_length, d, do):
    def fn():
        for _ in range(side_length):
            move(d)
        do()

    return fn


def spawn_drone_task1(face, target):
    def fn():
        child = spawn_drone(straight_move_do(BLOCK_H, face, spawn_drone_task2(target)))
        spawn_drone_task2(target)()
        wait_for(child)

    return fn


def spawn_drone_task2(target):
    def fn():
        child = spawn_drone(straight_move_do(BLOCK_W, East, spawn_drone_task3(East, target)))
        spawn_drone_task3(West, target)()
        wait_for(child)

    return fn


def spawn_drone_task3(face, target):
    def fn():
        children = []
        for _ in range(3):
            children.append(spawn_drone(work_drone_task, target))
            for _ in range(BLOCK_W):
                move(face)
        work_drone_task(target)
        for child in children:
            wait_for(child)

    return fn


if __name__ == "__main__":
    carrot()
