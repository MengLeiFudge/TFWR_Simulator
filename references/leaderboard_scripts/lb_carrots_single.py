from __builtins__ import *
# 完整轮时间：4:11.449（2026-11-03，build26385848，官方完整29轮，request252）。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 6564437d28f4ce02a160373ce1efbd1af283f29f。

def lb_carrots_single():
    global s
    global m
    global n
    global wants
    set_world_size(8)
    clear()
    s = get_world_size()
    m = s - 1
    n = s - 2
    wants = {}
    traverse_rectangle(first_round)
    while traverse_rectangle(while_round):
        continue


def traverse_rectangle(fn):
    # traverse_rectangle 针对 8 x 8 的性能优化版
    if fn():
        return False
    move(North)
    for i in range(0, s, 2):
        for j in range(m):
            if fn():
                return False
            if j != n:
                move(North)
        move(East)
        for j in range(m):
            if fn():
                return False
            if j != n:
                move(South)
        if i != n:
            move(East)
    move(South)
    for _ in range(m):
        if fn():
            return False
        move(West)

    return True


def on_eachcell():
    t = (get_pos_x(), get_pos_y())

    if get_water() < 0.01:
        # 访问间隔挺长的，不需要太多水
        use_item(Items.Water)

    if t in wants:
        # 满足当前位置的种植需求
        c = wants.pop(t)
        if get_entity_type() != c:
            harvest()
            plant(c)
        return

    while True:
        harvest()
        plant(Entities.Carrot)
        c, p = get_companion()
        if p in wants and wants[p] != c:
            continue  # 和其他植物的请求种植的冲突
        wants[p] = c  # 标记格子接下来要种植的作物
        break


def first_round():
    till()
    on_eachcell()


def while_round():
    on_eachcell()
    return num_items(Items.Carrot) >= 100000000


if __name__ == "__main__":
    lb_carrots_single()
