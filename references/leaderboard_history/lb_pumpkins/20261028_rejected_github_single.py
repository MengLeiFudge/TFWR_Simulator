# 淘汰候选归档：lb_pumpkins | 原实验路径 .codex/leaderboard-astra/github-pumpkins/pumpkins_single.py
set_world_size(6)

s = get_world_size()
m = s - 1


def traverse_topdown(fn):
    # 宽度为 2 的逆时针圈不断向东
    for i in range(0, s, 2):
        for j in range(m):
            if fn():
                return True
            move(North)
        if fn():
            return True
        move(East)
        for j in range(m):
            if fn():
                return True
            move(South)
        if fn():
            return True
        move(East)
    return False


def traverse_topdown_no_if(fn):
    for i in range(0, s, 2):
        for j in range(m):
            fn()
            move(North)
        fn()
        move(East)
        for j in range(m):
            fn()
            move(South)
        fn()
        move(East)


def move_to(pos):
    cx, cy = get_pos_x(), get_pos_y()
    tx, ty = pos

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


def plant_pumpkin_first():
    till()
    plant_pumpkin()


def plant_pumpkin():
    plant(Entities.Pumpkin)
    if get_water() < 0.65:
        use_item(Items.Water)


def is_fully_grown(mvalue):
    # 四个角落拥有同一个 id 说明南瓜已完全合并
    x, y = mvalue
    v = measure()  # 一定不是 None
    return (
        (y == 0 and v == measure(South))
        or (y == m and v == measure(North))
        or (x == 0 and v == measure(West))
        or (x == m and v == measure(East))
    )


def replant_dead_pumpkins():
    while unripes:
        mvalue = unripes.pop(0)
        move_to(mvalue)
        if plant(Entities.Pumpkin):  # dead pumpkin
            unripes.append(mvalue)
            continue
        if can_harvest():
            if unripes and is_fully_grown(mvalue):  # fully grown up and merged
                return True  # 只在还有其他为检查的植物时做这个提前判断
            continue
        if use_item(Items.Fertilizer):
            if can_harvest():
                if unripes and is_fully_grown(mvalue):
                    return True
                continue
        unripes.append(mvalue)  # still growing
        continue


def check_pumpkin():
    if plant(Entities.Pumpkin):  # dead pumpkin
        unripes.append((get_pos_x(), get_pos_y()))
        return
    if not can_harvest():  # still growing
        unripes.append((get_pos_x(), get_pos_y()))
        return


def harvest_a_pumpkin():
    traverse_topdown_no_if(plant_pumpkin)
    traverse_topdown_no_if(check_pumpkin) # 基本不可能一遍就种成功吧
    replant_dead_pumpkins()
    harvest()


def harvest_a_pumpkin_first():
    traverse_topdown_no_if(plant_pumpkin_first)
    traverse_topdown_no_if(check_pumpkin)
    replant_dead_pumpkins()
    harvest()


unripes = []
harvest_a_pumpkin_first()
for _ in range(89):  # 需要 92 轮才能达到目标
    unripes = []
    harvest_a_pumpkin()
while num_items(Items.Pumpkin) < 10000000:
    unripes = []
    harvest_a_pumpkin()
