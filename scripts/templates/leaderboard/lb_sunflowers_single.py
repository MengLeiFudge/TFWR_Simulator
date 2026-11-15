from __builtins__ import *
# 完整轮时间：本生成版本尚无完整实机成绩。


def lb_sunflowers_single():
    clear()
    buckets = {}
    ready = {}
    for value in range(7, 16):
        buckets[value] = []
    count = 0
    for cycle in range(128):
        for x in range(8):
            for y in range(8):
                if get_entity_type() != Entities.Sunflower:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    value, mature_at = sunflower_seed(x * 8 + y >= 46)
                    position = get_pos_y() * 16 + get_pos_x()
                    buckets[value].append(position)
                    ready[position] = mature_at
                    count += 1
                if cycle == 0 and count >= 10 and num_items(Items.Power) == 0:
                    if sunflower_boot(buckets, ready):
                        count -= 1
                if y < 7:
                    if x % 2:
                        move(South)
                    else:
                        move(North)
            move(East)
        level = 15
        while level >= 7 and count >= 10:
            positions = buckets[level]
            if not positions:
                level -= 1
                continue
            index = sunflower_pick(positions, ready, level >= 11)
            position = positions[index]
            positions[index] = positions[-1]
            positions.pop()
            sunflower_move(position)
            if not can_harvest():
                sunflower_water(1)
                while not can_harvest():
                    pass
            harvest()
            count -= 1
            if num_items(Items.Power) >= 10005:
                clear()
                return
            if level >= 12:
                remaining = level
                while remaining >= 12 and not buckets[remaining]:
                    remaining -= 1
                if remaining >= 12:
                    # 新苗必须低于场上最高瓣，重抽的苗本身是最高瓣，保持奖励状态。
                    plant(Entities.Sunflower)
                    value = measure()
                    while value >= remaining:  # ty: ignore[unsupported-operator] # Sunflower的measure返回瓣数。
                        harvest()
                        plant(Entities.Sunflower)
                        value = measure()
                    threshold = 0.5
                    if value == remaining - 1:
                        threshold = 0.85
                    water = sunflower_water(threshold)
                    ready[position] = get_time() + 8.4 / (1 + 4 * water)
                    buckets[value].append(position)  # ty: ignore[invalid-argument-type]
                    count += 1
        quick_print("sunflower_cycle", cycle, get_time(), num_items(Items.Power))


def sunflower_boot(buckets, ready):
    level = 15
    while level > 7 and not buckets[level]:
        level -= 1
    if not buckets[level]:
        return False
    positions = buckets[level]
    index = sunflower_pick(positions, ready, True)
    position = positions[index]
    if ready[position] > get_time():
        return False
    origin = get_pos_y() * 16 + get_pos_x()
    if SUN_DISTANCE[position - origin + 119] > 3:
        return False
    sunflower_move(position)
    if can_harvest():
        harvest()
        positions[index] = positions[-1]
        positions.pop()
        sunflower_move(origin)
        return True
    sunflower_move(origin)
    return False


def sunflower_seed(late):
    plant(Entities.Sunflower)
    value = measure()
    while late and value == 15:
        harvest()
        plant(Entities.Sunflower)
        value = measure()
    water = sunflower_water(0.5)
    return value, get_time() + 8.4 / (1 + 4 * water)


def sunflower_water(threshold):
    water = get_water()
    if water < threshold:
        amount = (1 - water) * 4 // 1
        if water + amount * 0.25 < 1:
            amount += 1
        amount = min(amount, num_items(Items.Water) // 1)
        if amount > 0 and use_item(Items.Water, amount):  # ty: ignore[invalid-argument-type] # 向上取整后的游戏Number。
            water = min(1, water + amount * 0.25)
    return water


def sunflower_pick(positions, ready, prefer_mature):
    current = get_pos_y() * 16 + get_pos_x() - 119
    now = get_time()
    nearest = 0
    nearest_cost = 99
    mature = None
    mature_cost = 99
    for i in range(len(positions)):
        position = positions[i]
        cost = SUN_DISTANCE[position - current]
        if not prefer_mature and cost <= 1:
            return i
        if cost < mature_cost and prefer_mature:
            if ready[position] <= now:
                if cost <= 1:
                    return i
                mature = i
                mature_cost = cost
        if cost < nearest_cost:
            nearest = i
            nearest_cost = cost
    if mature != None:
        return mature
    return nearest


def sunflower_move(position):
    current = get_pos_y() * 16 + get_pos_x()
    for direction in SUN_PATHS[position - current + 119]:
        move(direction)


def sunflower_tables():
    # 母版可直接执行；固定生成器只替换下面标记处的初始化，避免游戏内重建。
    distances = []
    paths = []
    for delta in range(-119, 120):
        dx = (delta + 7) % 16 - 7
        dy = (delta - dx) // 16
        route = []
        if abs(dx) >= 8 or abs(dy) >= 8:
            distances.append(99)
            paths.append(route)
            continue
        for count, positive, negative in [(dx % 8, East, West), (dy % 8, North, South)]:
            direction = positive
            if count > 4:
                count = 8 - count
                direction = negative
            for _ in range(count):
                route.append(direction)
        distances.append(len(route))
        paths.append(route)
    return distances, paths


#@wrap_paths 8 16
SUN_DISTANCE, SUN_PATHS = sunflower_tables()


if __name__ == "__main__":
    lb_sunflowers_single()
