from __builtins__ import *
# 淘汰候选归档：lb_sunflowers_single | 原实验路径 .codex/leaderboard-sol/sunflowers-single/size6/lb_sunflowers_single.py
# 本地候选；完整实测成绩未验证。


def lb_sunflowers_single():
    set_world_size(FIELD_SIZE)
    positions = prepare_field(FIELD_SIZE)
    if len(positions) == 0:
        return
    quick_print("sunflower_stage", "support_ready", "size=", FIELD_SIZE, "time=", get_time(), "power=", num_items(Items.Power))
    batch = 0
    while num_items(Items.Power) < POWER_GOAL and batch < MAX_BATCHES:
        buckets = plant_batch(positions, FIELD_SIZE)
        quick_print("sunflower_stage", "planted", "batch=", batch, "time=", get_time(), "power=", num_items(Items.Power))
        if not harvest_batch(buckets, FIELD_SIZE):
            return
        batch = batch + 1
        quick_print("sunflower_stage", "harvested", "batch=", batch, "time=", get_time(), "power=", num_items(Items.Power))
    quick_print("sunflower_stage", "done", "batches=", batch, "time=", get_time(), "power=", num_items(Items.Power), "goal=", num_items(Items.Power) >= POWER_GOAL)


# 单机榜可用8x8；本轮只比较6x6和8x8，左下3x3为永久最低花瓣支撑。
FIELD_SIZE = 6
POWER_GOAL = 10000
SUPPORT_SIDE = 3
SUPPORT_PETALS = 7
# 候选执行上限；到界只输出未达标结果，不把部分进度当作成绩。
MAX_BATCHES = 80
MAX_SUPPORT_ATTEMPTS = 256
MAX_MATURITY_SECONDS = 12


def prepare_field(size):
    # 准备土壤与九株7瓣支撑，返回其余格子的固定蛇形种植顺序。
    positions = []
    for y in range(size):
        if y % 2 == 0:
            columns = range(size)
        else:
            columns = range(size - 1, -1, -1)
        for x in columns:
            goto_wrap(x, y, size)
            if get_ground_type() != Grounds.Soil:
                till()
            if get_entity_type() != None:
                harvest()
            if x < SUPPORT_SIDE and y < SUPPORT_SIDE:
                petals = 0
                for attempt in range(MAX_SUPPORT_ATTEMPTS):
                    plant(Entities.Sunflower)
                    petals = measure()
                    if petals == SUPPORT_PETALS:
                        break
                    harvest()
                if petals != SUPPORT_PETALS:
                    quick_print("sunflower_stage", "support_limit", "x=", x, "y=", y, "time=", get_time())
                    return []
                water_if_available(size)
            else:
                positions.append((x, y))
    return positions


def plant_batch(positions, size):
    # 整批种完并记录九个花瓣桶；收割期间不向这些空位重种。
    buckets = []
    for petals in range(9):
        buckets.append([])
    for pos in positions:
        goto_wrap(pos[0], pos[1], size)
        plant(Entities.Sunflower)
        water_if_available(size)
        buckets[measure() - SUPPORT_PETALS].append(pos)
    return buckets


def harvest_batch(buckets, size):
    # 降序收完全部生产位；同瓣按环绕最近邻选择，并限制单株成熟等待。
    for petals in range(8, -1, -1):
        bucket = buckets[petals]
        while len(bucket) > 0:
            pos = bucket.pop(nearest_index(bucket, size))
            goto_wrap(pos[0], pos[1], size)
            deadline = get_time() + MAX_MATURITY_SECONDS
            while not can_harvest():
                water_if_available(size)
                if get_time() >= deadline:
                    quick_print("sunflower_stage", "maturity_limit", "x=", pos[0], "y=", pos[1], "time=", get_time())
                    return False
            harvest()
            if num_items(Items.Power) >= POWER_GOAL:
                return True
    return True


def nearest_index(bucket, size):
    # 只在当前花瓣桶选择最近格子，不搜索路径排列。
    x = get_pos_x()
    y = get_pos_y()
    best = 0
    distance = size * 2
    for index in range(len(bucket)):
        pos = bucket[index]
        dx = abs(pos[0] - x)
        dy = abs(pos[1] - y)
        steps = min(dx, size - dx) + min(dy, size - dy)
        if steps < distance:
            distance = steps
            best = index
    return best


def goto_wrap(tx, ty, size):
    # 沿两个坐标轴的较短环绕方向移动；先横后纵。
    dx = (tx - get_pos_x()) % size
    if dx > size // 2:
        for step in range(size - dx):
            move(West)
    else:
        for step in range(dx):
            move(East)
    dy = (ty - get_pos_y()) % size
    if dy > size // 2:
        for step in range(size - dy):
            move(South)
    else:
        for step in range(dy):
            move(North)


def water_if_available(size):
    # 沿用当前盲收的水量阈值与库存保护，初始化成本也计入候选。
    if get_water() < 0.425 and num_items(Items.Water) > size:
        use_item(Items.Water)


if __name__ == "__main__":
    lb_sunflowers_single()
