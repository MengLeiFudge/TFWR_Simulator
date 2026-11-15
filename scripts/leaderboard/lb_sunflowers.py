from __builtins__ import *
# 完整轮时间：本版尚无完整实机成绩；本地完整目标对照见同名单榜文档。


def lb_sunflowers():
    clear()
    sunflower_launch(0, 32, get_time())


def sunflower_launch(lo, hi, began):
    while hi - lo > 1:
        mid = (lo + hi) // 2
        spawn_drone(sunflower_launch, mid, hi, began)
        hi = mid
    sunflower_worker(lo, began)


def sunflower_worker(owner, began):
    x0 = 4 * (owner % 8)
    y0 = 8 * (owner // 8)
    sunflower_move(x0, y0)
    current = 0
    for cycle in range(128):
        sowing = 3.8
        growth = max(0.4, 0.4 + 1.35 * 0.78 ** (cycle - 1))
        maturity = 1.4 + 1.6 * 0.78 ** cycle
        extra = 0
        if cycle == 0:
            sowing = 10.5
            growth = 4.5
            extra = 0.78
        sow_end = began + sowing
        harvest_start = sow_end + growth
        buckets = [[], [], [], [], [], [], []]
        work = [0, 0, 0, 0, 0, 0, 0]
        last = [0, 0, 0, 0, 0, 0, 0]
        # 固定蛇形顺序形成同瓣路径；播种时间不足时停止重抽。
        for row in range(8):
            for column in range(4):
                x = column
                if row % 2:
                    x = 3 - column
                index = row * 4 + x
                current = sunflower_local(index, current)
                if cycle == 0:
                    if get_ground_type() != Grounds.Soil:
                        till()
                if get_entity_type() != None:
                    harvest()
                cutoff = sow_end - (31 - row * 4 - column) * 0.083
                value = sunflower_sow(index, harvest_start, extra, maturity, cutoff, buckets, work, last)
                if value >= 9:
                    rank = value - 9
                    if buckets[rank]:
                        previous = last[rank]
                        work[rank] += (abs(previous % 4 - x) + abs(previous // 4 - row)) * 200 + 215
                    else:
                        work[rank] = 215
                    buckets[rank].append(index)
                    last[rank] = index
        stage_end = harvest_start
        sunflower_wait(harvest_start)
        for value in range(15, 8, -1):
            duration = 0.72
            if cycle == 0 and value == 15:
                duration = 1.5
            stage_end += duration
            positions = buckets[value - 9]
            if positions:
                first = positions[0]
                final = positions[-1]
                cx = current % 4
                cy = current // 4
                if abs(first % 4 - cx) + abs(first // 4 - cy) > abs(final % 4 - cx) + abs(final // 4 - cy):
                    positions = positions[::-1]
                for position in positions:
                    current = sunflower_local(position, current)
                    harvest()
                    if num_items(Items.Power) >= 100010:
                        quick_print("sunflowers_done", cycle, get_time(), num_items(Items.Power))
                        clear()
                        return
            sunflower_wait(stage_end)
        began = stage_end
        if owner == 0:
            quick_print("sunflower_cycle", cycle, get_time(), num_items(Items.Power))


def sunflower_sow(index, harvest_start, extra, maturity, cutoff, buckets, work, last):
    plant(Entities.Sunflower)
    value = measure()
    phase = harvest_start
    while True:
        invalid = value < 9  # ty: ignore[unsupported-operator] # Sunflower的measure返回瓣数。
        if not invalid:
            rank = value - 9  # ty: ignore[unsupported-operator]
            phase = harvest_start + (15 - value) * 0.72  # ty: ignore[unsupported-operator]
            if value < 15:  # ty: ignore[unsupported-operator]
                phase += extra
            previous = last[rank]
            added = (abs(previous % 4 - index % 4) + abs(previous // 4 - index // 4)) * 200 + 215
            invalid = phase - get_time() < maturity or len(buckets[rank]) >= 8 or (buckets[rank] and work[rank] + added > 3800)
        if not invalid:
            break
        if get_time() >= cutoff:
            if value >= 9 and get_time() < harvest_start - 0.3:  # ty: ignore[unsupported-operator]
                harvest()
                return 0
            return value
        harvest()
        plant(Entities.Sunflower)
        value = measure()
    left = phase - get_time()
    if left < 7:
        water = get_water()
        wanted = 7 / max(left, 0.05) - 1 - 4 * water
        amount = wanted // 1
        if amount < wanted:
            amount += 1
        capacity = (1 - water) * 4
        maximum = capacity // 1
        if maximum < capacity:
            maximum += 1
        amount = min(4, amount, maximum, num_items(Items.Water) // 1)
        if amount > 0:
            use_item(Items.Water, amount)  # ty: ignore[invalid-argument-type] # 向上取整后的游戏Number。
    return value


def sunflower_local(target, current):
    dx = target % 4 - current % 4
    dy = target // 4 - current // 4
    for count, positive, negative in [(dx, East, West), (dy, North, South)]:
        direction = positive
        if count < 0:
            count = -count
            direction = negative
        for _ in range(count):
            move(direction)
    return target


def sunflower_move(x, y):
    for target, current, positive, negative in [(x, get_pos_x(), East, West), (y, get_pos_y(), North, South)]:
        count = (target - current) % 32
        direction = positive
        if count > 16:
            count = 32 - count
            direction = negative
        for _ in range(count):
            move(direction)


def sunflower_wait(target):
    while get_time() + 1 < target:
        do_a_flip()
    while get_time() < target:
        for _ in range(16):
            pass


if __name__ == "__main__":
    lb_sunflowers()
