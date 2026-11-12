# 淘汰候选归档：lb_carrots | 原实验路径 .codex/leaderboard-astra/github-carrots/carrots_single.py
# set_world_size(8)

s = get_world_size()
m = s - 1
n = s - 2

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

    return True  # loop continues


wants = {}  # 记录种植需求


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


traverse_rectangle(first_round)
while traverse_rectangle(while_round):
    continue
