from __builtins__ import *
# 完整轮时间：4:56.061（官方完整复验25轮，request210）；环绕距离查表选点。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 209990a4977f011e0f8e7861530cf3045c6a3a2f。

def lb_sunflowers_single():
    global s
    global m
    global FULL_GROUND
    global sunflower_dict
    set_world_size(8)
    clear()
    s = get_world_size()
    m = s - 1
    FULL_GROUND = s * s
    sunflower_dict = {}
    for petals in range(7, 16):
        sunflower_dict[petals] = []
    traverse_topdown_no_if(plant_a_sunflower_first)
    for _ in range(23):
        trip_round()
    while num_items(Items.Power) < 10000:
        last_trip_round()

# 固定8格世界，差值-7..7均可直接索引；负下标对应反向距离。
WRAP_DISTANCE = [0, 1, 2, 3, 4, 3, 2, 1]

W = 0.72
MAX_PETALS = 15
MIN_PETALS = 7
MIN_PETALS_S1 = 6
OCTUPLE_BASE = 10
OCTUPLE_BASE_S1 = 9


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


def plant_a_sunflower_first():
    till()
    plant(Entities.Sunflower)
    x = get_pos_x()
    sunflower_dict[measure()].append((x, get_pos_y()))
    if x >= m:
        # 首轮只浇最后一列；前面的植株利用后续动作时间生长。
        while get_water() < W and num_items(Items.Water) > 0:
            use_item(Items.Water)


def plant_a_sunflower():
    # plant 会在已有植物上 return False
    if plant(Entities.Sunflower):
        v = measure()
        sunflower_dict[v].append((get_pos_x(), get_pos_y()))
        if v <= 10:  # ty: ignore
            # 较低花瓣利用先收高花瓣的时间生长，收割前仍检查成熟。
            return
        while get_water() < W and num_items(Items.Water) > 0:
            use_item(Items.Water)


def nearest_expect_current(positions):
    # 按实际环绕距离选点；保留当前点最后处理的成熟协议。
    min_pos = None
    min_dis = 9999
    x, y = get_pos_x(), get_pos_y()
    for pos in positions:
        mx, my = pos
        dis = WRAP_DISTANCE[mx - x] + WRAP_DISTANCE[my - y]
        if dis == 0:
            continue
        if dis < min_dis:
            min_dis = dis
            min_pos = pos
    return min_pos


def trip_round():
    sunflower_count = FULL_GROUND  # 肯定种满了，直接赋值
    for petal in range(MAX_PETALS, MIN_PETALS_S1, -1):
        # 为了维持场上至少 10 株，最多采集这么多
        max_can_harvest = sunflower_count - OCTUPLE_BASE_S1
        tocheck, unripes = sunflower_dict[petal], []
        this_petal_harvest = min(max_can_harvest, len(tocheck))
        for _ in range(this_petal_harvest):
            while True:
                if not tocheck:
                    tocheck, unripes = unripes, []
                # assert tocheck is not empty
                nearest = nearest_expect_current(tocheck)
                if nearest == None:
                    # 说明当前位置就是最后一个点
                    while not mature():
                        continue
                    harvest()
                    tocheck.pop()
                    break  # while loop
                else:
                    # 尝试采集，否则检查下一个
                    move_to(nearest)
                    if mature():
                        harvest()
                        tocheck.remove(nearest)
                        break  # while loop
                    else:
                        tocheck.remove(nearest)
                        unripes.append(nearest)
        sunflower_dict[petal] = tocheck + unripes
        sunflower_count -= max(0, this_petal_harvest)
    # 场面上应该剩余 9 株向日葵，开始种植新的
    traverse_topdown_no_if(plant_a_sunflower)


def last_trip_round():
    sunflower_count = FULL_GROUND
    for petal in range(MAX_PETALS, MIN_PETALS_S1, -1):
        max_can_harvest = sunflower_count - OCTUPLE_BASE_S1
        tocheck, unripes = sunflower_dict[petal], []
        this_petal_harvest = min(max_can_harvest, len(tocheck))
        for _ in range(this_petal_harvest):
            while True:
                if not tocheck:
                    tocheck, unripes = unripes, []
                nearest = nearest_expect_current(tocheck)
                if nearest == None:
                    while not mature():
                        continue
                    harvest()
                    tocheck.pop()
                    break
                else:
                    move_to(nearest)
                    if mature():
                        harvest()
                        tocheck.remove(nearest)
                        break
                    else:
                        tocheck.remove(nearest)
                        unripes.append(nearest)
            if num_items(Items.Power) > 10000:
                return
        sunflower_dict[petal] = tocheck + unripes
        sunflower_count -= max(0, this_petal_harvest)
    traverse_topdown_no_if(plant_a_sunflower)


def mature():
    if can_harvest():
        return True
    if num_items(Items.Fertilizer) > 0:
        use_item(Items.Fertilizer)
        return can_harvest()
    return False


if __name__ == "__main__":
    lb_sunflowers_single()
