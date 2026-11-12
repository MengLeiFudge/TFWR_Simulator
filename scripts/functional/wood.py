from __builtins__ import *
# 全科技功能初版；来源 lb_wood.py，本地对照见docs/script-rate-validation.md。
import production
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。

def wood(target=-1):
    global carrot_hay
    global carrot_wood
    if not production.active(Items.Wood, target):
        return
    set_world_size(32)
    clear()
    cost = get_cost(Entities.Carrot)
    carrot_hay = cost[Items.Hay]
    carrot_wood = cost[Items.Wood]
    child = spawn_drone(straight_move_do(BLOCK_H, North, spawn_drone_task1(North, target)))
    spawn_drone_task1(South, target)()
    wait_for(child)

W = 0.35
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


def is_tree_pos(p):
    x, y = p
    return (x + y) % 2 == 0


def work_drone_task(target):
    wants = {}

    def on_eachcell():
        if not production.active(Items.Wood, target):
            return
        t = (get_pos_x(), get_pos_y())

        # 满足当前位置的种植需求
        if t in wants:
            c = wants.pop(t)
            if get_entity_type() != c:
                harvest()
                # 启动期缺Carrot材料时保持原来的Bush退路。
                if c == Entities.Carrot and (num_items(Items.Hay) < carrot_hay or num_items(Items.Wood) < carrot_wood):
                    plant(Entities.Bush)
                else:
                    plant(c)
            return

        # 在树的位置种树，其他位置不管
        if is_tree_pos(t):
            # 只在树的位置浇水
            if get_water() < W and num_items(Items.Water) > 32:
                # 一次补满水位，库存检查仍为并发调用保留余量。
                use_item(Items.Water, 4)
            while production.active(Items.Wood, target):
                harvest()
                plant(Entities.Tree)
                c, p = get_companion()
                if is_tree_pos(p):
                    continue  #  和树的位置冲突
                if p in wants and wants[p] != c:
                    continue  # 和其他植物的请求种植的冲突
                wants[p] = c  # 跨区请求不会交给邻机；其低倍率收获按实际收益计入。
                break
            return

    def first_round():
        till()
        on_eachcell()

    def range_round():
        on_eachcell()

    def while_round():
        on_eachcell()
        return not production.active(Items.Wood, target)

    traverse_rectangle(first_round, 4, 8)
    for _ in range(22):
        if not production.active(Items.Wood, target):
            break
        traverse_rectangle(range_round, 4, 8)
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
    wood()
