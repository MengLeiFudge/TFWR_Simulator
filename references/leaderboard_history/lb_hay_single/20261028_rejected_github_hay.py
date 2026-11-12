from __builtins__ import *
# 淘汰候选归档：lb_hay_single | 原实验路径 .codex/leaderboard-astra/github-hay/lb_hay_single.py
# 私有单机干草候选，尚无本版完整实机成绩。
# Copyright (c) 2026 enihsyou，MIT许可见enihsyou_LICENSE.txt。

def lb_hay_single():
    # 周围三格种上草丛

    set_world_size(5)
    clear()
    for dir in (
        North,
        North,
        North,
        North,
        # at (0, 4)
        East,
        # at (1, 4)
        South,
        South,
        South,
        # at (1, 1)
        East,
        # at (2, 1)
        North,
        North,
        North,
        North,
        # at (2, 0)
        East,
        North,
        # at (3, 1)
        East,
        North,
        North,
        # at (4, 3)
        West,
        North,
        East,
        # at (4, 4)
        North,
        # at (4, 0)
    ):
        move(dir)
        plant(Entities.Bush)
    move(East)
    # at (0, 0)

    W = 0.68  # 替代 can_harvest() 等待时间的最小值
    A, B = (0, 0), (1, 0)

    # 理想状态下需要 1220 次完整加成的 harvest

    # 第一个循环，补水
    while get_water() < W:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)
    harvest()  # move 消耗的时间基本抵消了成长时间，无需 can_harvest()
    c, pos = get_companion()
    while c != Entities.Bush or pos == B:
        harvest()
        c, pos = get_companion()
    move(East)

    while get_water() < W:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)
    harvest()
    c, pos = get_companion()
    while c != Entities.Bush or pos == A:
        harvest()
        c, pos = get_companion()
    move(West)

    # 第二个循环，省略数量判断
    for _ in range(604):
        if get_water() < W:
            if num_items(Items.Water) > 0:
                use_item(Items.Water)
        harvest()  # move 消耗的时间基本抵消了成长时间，无需 can_harvest()
        c, pos = get_companion()
        while c != Entities.Bush or pos == B:
            harvest()
            c, pos = get_companion()
        move(East)

        if get_water() < W:
            if num_items(Items.Water) > 0:
                use_item(Items.Water)
        harvest()
        c, pos = get_companion()
        while c != Entities.Bush or pos == A:
            harvest()
            c, pos = get_companion()
        move(West)

    # 第三个循环，省略补水，直到收集足够的干草
    while True:
        harvest()  # move 消耗的时间基本抵消了成长时间，无需 can_harvest()
        if num_items(Items.Hay) >= 100000000:
            break
        c, pos = get_companion()
        while c != Entities.Bush or pos == B:
            harvest()
            c, pos = get_companion()
        move(East)

        harvest()
        if num_items(Items.Hay) >= 100000000:
            break
        c, pos = get_companion()
        while c != Entities.Bush or pos == A:
            harvest()
            c, pos = get_companion()
        move(West)

if __name__ == "__main__":
    lb_hay_single()
