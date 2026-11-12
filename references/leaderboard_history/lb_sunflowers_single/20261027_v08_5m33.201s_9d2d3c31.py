from __builtins__ import *
# 历史提交归档：lb_sunflowers_single | 初次提交 2026-10-27 (9d2d3c31) | 优化：迁入七项实机上榜策略并记录完整统计
# 完整轮时间：5:33.201（2026-10-26，官方完整22轮，request 83）。

def lb_sunflowers_single():
    quick_print("sunflower_reserve", "start", "time=", get_time(), "power=", num_items(Items.Power))
    set_world_size(FIELD_SIZE)
    positions, buckets = prepare_field(FIELD_SIZE)
    quick_print("sunflower_reserve", "initialized", "time=", get_time(), "power=", num_items(Items.Power))
    support = []
    batch = 0
    while num_items(Items.Power) < POWER_GOAL and batch < MAX_BATCHES:
        support = reserve_lowest(buckets, support)
        if len(support) != SUPPORT_COUNT:
            quick_print("sunflower_reserve", "support_limit", "batch=", batch, "time=", get_time())
            return
        if not harvest_batch(buckets, FIELD_SIZE):
            return
        batch = batch + 1
        quick_print("sunflower_reserve", "harvested", "batch=", batch, "time=", get_time(), "power=", num_items(Items.Power))
        if num_items(Items.Power) >= POWER_GOAL:
            break
        buckets = plant_batch(positions, support, FIELD_SIZE)
    quick_print("sunflower_reserve", "done", "batches=", batch, "time=", get_time(), "power=", num_items(Items.Power), "goal=", num_items(Items.Power) >= POWER_GOAL)


FIELD_SIZE = 8
POWER_GOAL = 10000
SUPPORT_COUNT = 9
SUPPORT_PETALS = 7
MAX_BATCHES = 80
MAX_MATURITY_SECONDS = 12


def prepare_field(size):
    # 首次清草翻地并种满全场，固定蛇形坐标也用于后续补种。
    positions = []
    buckets = []
    for petals in range(9):
        buckets.append([])
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
            plant(Entities.Sunflower)
            water_if_available(size)
            pos = (x, y)
            positions.append(pos)
            buckets[measure() - SUPPORT_PETALS].append(pos)
    return positions, buckets


def reserve_lowest(buckets, previous):
    # 全场只保留最低九株；同瓣先保留旧支撑，再从新株补足。
    support = []
    for petals in range(9):
        bucket = buckets[petals]
        for old in previous:
            if old[1] == petals:
                bucket.remove(old[0])
                support.append(old)
                if len(support) == SUPPORT_COUNT:
                    return support
        while len(bucket) > 0 and len(support) < SUPPORT_COUNT:
            support.append((bucket.pop(), petals))
        if len(support) == SUPPORT_COUNT:
            return support
    return support


def plant_batch(positions, support, size):
    # 保留株不重种或重测；其余55株仍按全图蛇形过滤后的顺序补齐。
    buckets = []
    for petals in range(9):
        buckets.append([])
    retained = set()
    for old in support:
        retained.add(old[0])
        buckets[old[1]].append(old[0])
    for pos in positions:
        if pos in retained:
            continue
        goto_wrap(pos[0], pos[1], size)
        plant(Entities.Sunflower)
        water_if_available(size)
        buckets[measure() - SUPPORT_PETALS].append(pos)
    return buckets


def harvest_batch(buckets, size):
    # 九株支撑已从桶移出；其余降序收完后全场恰好剩九株。
    for petals in range(8, -1, -1):
        bucket = buckets[petals]
        while len(bucket) > 0:
            pos = bucket.pop(nearest_index(bucket, size))
            goto_wrap(pos[0], pos[1], size)
            deadline = get_time() + MAX_MATURITY_SECONDS
            while not can_harvest():
                water_if_available(size)
                if get_time() >= deadline:
                    quick_print("sunflower_reserve", "maturity_limit", "x=", pos[0], "y=", pos[1], "time=", get_time())
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
    # 水量低于阈值且库存超过地图边长时补水。
    if get_water() < 0.425 and num_items(Items.Water) > size:
        use_item(Items.Water)


if __name__ == "__main__":
    lb_sunflowers_single()
