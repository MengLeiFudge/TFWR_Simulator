# 淘汰候选归档：lb_wood | 原实验路径 .codex/leaderboard-astra/github-wood/wood_single.py
# set_world_size(8)
s = get_world_size()

W = 0.16


def traverse_rectangle_if(fn, w, h):
    # traverse_rectangle 针对 8 x 8 的性能优化版
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

    return True  # loop continues


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


def is_tree_pos(p):
    x, y = p
    return (x + y) % 2 == 0


def work_drone_task():
    wants = {}  # 记录种植需求

    def on_eachcell():
        t = (get_pos_x(), get_pos_y())

        # 满足当前位置的种植需求
        if t in wants:
            c = wants.pop(t)
            if get_entity_type() != c:
                harvest()
                # may failed at Carrot with no enough resource
                _ = plant(c) or plant(Entities.Bush)
            return

        # 在树的位置种树，其他位置不管
        if is_tree_pos(t):
            # 只在树的位置浇水
            if get_water() < W:
                # 访问间隔挺长的，不需要太多水
                use_item(Items.Water)
            while True:
                harvest()
                plant(Entities.Tree)
                c, p = get_companion()
                if is_tree_pos(p):
                    continue  #  和树的位置冲突
                if p in wants and wants[p] != c:
                    continue  # 和其他植物的请求种植的冲突
                wants[p] = c  # 标记格子接下来要种植的作物
                break
            return

    def first_round():
        till()
        on_eachcell()

    def range_round():
        on_eachcell()

    def while_round():
        on_eachcell()
        return num_items(Items.Wood) >= 500000000

    traverse_rectangle(first_round, s, s)
    for _ in range(34):  # 需要约 37 轮能够收集到足够的木头
        traverse_rectangle(range_round, s, s)
    while traverse_rectangle_if(while_round, s, s):
        continue


work_drone_task()
