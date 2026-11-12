# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/github-sunflowers-single/sunflowers_single.py
# set_world_size(8)
s = get_world_size()
m = s - 1

# twealable parameters
W = 0.72


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
        # 只给最后一列浇水，因为前面的已经长好了
        while get_water() < W:
            use_item(Items.Water)


def plant_a_sunflower():
    # plant 会在已有植物上 return False
    if plant(Entities.Sunflower):
        v = measure()
        sunflower_dict[v].append((get_pos_x(), get_pos_y()))
        if v <= 10:  # ty: ignore
            # 采集其他的时间足够它生长了
            return
        while get_water() < W:
            use_item(Items.Water)


sunflower_dict = {}  # 记录不同花瓣数的向日葵位置
for petals in range(7, 16):
    sunflower_dict[petals] = []

MAX_PETALS = 15
MIN_PETALS = 7
MIN_PETALS_S1 = 6  # MIN_PETALS -1
FULL_GROUND = s * s  # 田块总数
OCTUPLE_BASE = 10
OCTUPLE_BASE_S1 = 9  # OCTUPLE_BASE - 1


def nearest_expect_current(positions):
    # 找到离当前位置最近的点
    min_pos = None
    min_dis = 9999
    x, y = get_pos_x(), get_pos_y()
    for pos in positions:
        mx, my = pos
        dis = abs(mx - x) + abs(my - y)
        if dis == 0:
            continue
        if dis < min_dis:
            min_dis = dis
            min_pos = pos
    return min_pos


# 平均每轮收集至少 430 能量
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
                    while not can_harvest():
                        use_item(Items.Fertilizer)
                    harvest()
                    break  # while loop
                else:
                    # 尝试采集，否则检查下一个
                    move_to(nearest)
                    if can_harvest() or use_item(Items.Fertilizer):
                        harvest()
                        tocheck.remove(nearest)
                        break  # while loop
                    else:
                        unripes.append(nearest)
        sunflower_count -= max(0, this_petal_harvest)
    # 场面上应该剩余 9 株向日葵，开始种植新的
    traverse_topdown_no_if(plant_a_sunflower)


# 最后几轮收集添加数量判断提前结束
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
                    while not can_harvest():
                        use_item(Items.Fertilizer)
                    harvest()
                    break
                else:
                    move_to(nearest)
                    if can_harvest() or use_item(Items.Fertilizer):
                        harvest()
                        tocheck.remove(nearest)
                        break
                    else:
                        unripes.append(nearest)
            if num_items(Items.Power) > 10000:
                return
        sunflower_count -= max(0, this_petal_harvest)
    traverse_topdown_no_if(plant_a_sunflower)


traverse_topdown_no_if(plant_a_sunflower_first)
for _ in range(23):
    trip_round()
while num_items(Items.Power) < 10000:
    last_trip_round()
