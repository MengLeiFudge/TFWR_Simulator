from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-small-field/failed-shared-marker/lb_sunflowers.py
# 小田与计数屏障固定六批组件，不代表完整打榜成绩。

def lb_sunflowers():
    clear()
    set_world_size(16)
    quick_print("small_begin", get_time(), num_items(Items.Power))
    result = launch_farm(0, 16, get_time() + 300)
    quick_print("small_done", result, get_time(), num_items(Items.Power))

def launch_farm(pod, count, deadline):
    if not go(pod * 16 + 4, deadline):
        return False
    if count == 1:
        return farm(pod, deadline)
    half = count // 2
    def child():
        return launch_farm(pod + half, half, deadline)
    handle = spawn_drone(child)
    if handle == None:
        quick_print("pair_farm_failed", "launch", pod)
        return False
    local = launch_farm(pod, half, deadline)
    other = wait_for(handle)
    return local and other

def pause():
    for _ in range(32):
        pass

def go(index, deadline):
    tx, ty = points[index]
    dx = (tx - get_pos_x()) % 16
    direction = East
    if dx > 8:
        direction = West
        dx = 16 - dx
    for _ in range(dx):
        if get_time() > deadline or not move(direction):
            return False
    dy = (ty - get_pos_y()) % 16
    direction = North
    if dy > 8:
        direction = South
        dy = 16 - dy
    for _ in range(dy):
        if get_time() > deadline or not move(direction):
            return False
    return True

def water():
    if get_water() < 0.425 and num_items(Items.Water) > 32:
        return use_item(Items.Water)
    return True

def seed(pod, side, cycle, deadline):
    buckets = []
    for _ in range(9):
        buckets.append([])
    began = get_time()
    for cell in range(side * 8, side * 8 + 8):
        if not go(pod * 16 + cell, deadline):
            return None
        if cell % 8 == 4:
            continue
        if get_ground_type() != Grounds.Soil:
            till()
        if not plant(Entities.Sunflower):
            return None
        petals = measure()
        if petals == None or petals < 7 or petals > 15:
            return None
        buckets[15 - petals].append(cell)
        if not water():
            return None
    seeded = get_time()
    if not go(pod * 16 + side * 8 + 4, deadline):
        return None
    # 所有224次种花与32次信号消耗完成后，才能开始收割。
    limit = initial_carrots - cycle * 164064 - 224 - 16384
    if not barrier(limit, deadline):
        return None
    quick_print("pair_seed", pod, side, cycle, began, seeded, get_time())
    return buckets

def routes(pod, buckets):
    positions = [4, 12]
    plans = [[], []]
    for rank in range(9):
        cells = buckets[rank]
        assigned = [[], []]
        if len(cells) > 0:
            # 闭环中最长的一条边不再进入线性花序；同长保留原断口。
            gap = table[cells[-1]][cells[0]]
            start = 0
            for i in range(1, len(cells)):
                distance = table[cells[i - 1]][cells[i]]
                if distance > gap:
                    gap = distance
                    start = i
            if start:
                cells = cells[start:] + cells[:start]
            prefix = [0]
            for i in range(1, len(cells)):
                prefix.append(prefix[-1] + table[cells[i - 1]][cells[i]] + 1)
            order = [0, 1]
            if (positions[0] - cells[0]) % 16 > (positions[1] - cells[0]) % 16:
                order = [1, 0]
            cut, cost = split(positions, cells, order, prefix)
            reverse = [order[1], order[0]]
            other_cut, other_cost = split(positions, cells, reverse, prefix)
            if other_cost < cost:
                cut = other_cut
                cost = other_cost
                order = reverse
            reverse_cells = []
            reverse_prefix = []
            end = prefix[-1]
            for i in range(len(cells) - 1, -1, -1):
                reverse_cells.append(cells[i])
                reverse_prefix.append(end - prefix[i])
            reverse = [order[1], order[0]]
            back_cut, back_cost = split(positions, reverse_cells, order, reverse_prefix)
            other_cut, other_cost = split(positions, reverse_cells, reverse, reverse_prefix)
            if other_cost < back_cost:
                back_cut = other_cut
                back_cost = other_cost
                back_order = reverse
            else:
                back_order = order
            if back_cost < cost:
                cut = back_cut
                cells = reverse_cells
                order = back_order
            stops = [cut, len(cells)]
            index = 0
            for j in range(2):
                worker = order[j]
                stop = stops[j]
                if stop > index:
                    assigned[worker] = cells[index:stop]
                    positions[worker] = cells[stop - 1]
                index = stop
        plans[0].append(assigned[0])
        plans[1].append(assigned[1])
    return plans

def barrier(limit, deadline):
    if get_ground_type() != Grounds.Soil:
        till()
    if not plant(Entities.Pumpkin):
        return False
    if not harvest():
        return False
    while num_items(Items.Carrot) > limit:
        if get_time() > deadline:
            return False
        pause()
    return True

def collect(pod, side, cycle, plan, base, deadline):
    harvested = 0
    for rank in range(9):
        began = get_time()
        for cell in plan[rank]:
            if not go(pod * 16 + cell, deadline):
                return False
            while not can_harvest():
                if get_time() > deadline:
                    return False
                if not water():
                    return False
                pause()
            if not harvest():
                return False
            harvested += 1
        if not barrier(base - (rank + 2) * 16384, deadline):
            return False
        if pod == 0 and side == 0:
            quick_print("small_rank", cycle, rank, began, get_time(), num_items(Items.Power), num_items(Items.Water))
    quick_print("small_collect", pod, side, cycle, harvested, get_time())
    return True

def farm(pod, deadline):
    for cycle in range(6):
        wave_deadline = min(deadline, get_time() + 45)
        began = get_time()
        def second_seed():
            return seed(pod, 1, cycle, wave_deadline)
        handle = spawn_drone(second_seed)
        if handle == None:
            quick_print("pair_farm_failed", "seed_spawn", pod, cycle)
            return False
        first = seed(pod, 0, cycle, wave_deadline)
        second = wait_for(handle)
        if first == None or second == None:
            quick_print("pair_farm_failed", "seed", pod, cycle)
            return False
        base = initial_carrots - cycle * 164064 - 224
        for rank in range(9):
            first[rank] = first[rank] + second[rank]
        planning = get_time()
        plans = routes(pod, first)
        planned = get_time()
        def second_collect():
            return collect(pod, 1, cycle, plans[1], base, wave_deadline)
        handle = spawn_drone(second_collect)
        if handle == None:
            quick_print("pair_farm_failed", "collect_spawn", pod, cycle)
            return False
        local = collect(pod, 0, cycle, plans[0], base, wave_deadline)
        other = wait_for(handle)
        quick_print("pair_wave", pod, cycle, began, planning, planned, get_time(), num_items(Items.Power))
        if not local or not other:
            quick_print("pair_farm_failed", "collect", pod, cycle)
            return False
    return True

def split(positions, cells, order, prefix):
    n = len(cells)
    first = table[positions[order[0]]][cells[0]] + 1
    row = table[positions[order[1]]]
    end = prefix[-1]
    low = 0
    high = n
    while low < high:
        middle = (low + high) // 2
        left = 0
        if middle > 0:
            left = first + prefix[middle - 1]
        right = row[cells[middle]] + 1 + end - prefix[middle]
        if left < right:
            low = middle + 1
        else:
            high = middle
    right = 0
    if low < n:
        right = row[cells[low]] + 1 + end - prefix[low]
    left = 0
    if low > 0:
        left = first + prefix[low - 1]
    best = max(left, right)
    cut = low
    if low > 0:
        index = low - 1
        left = 0
        if index > 0:
            left = first + prefix[index - 1]
        right = row[cells[index]] + 1 + end - prefix[index]
        value = max(left, right)
        if value <= best:
            cut = index
            best = value
    return cut, best

initial_carrots = num_items(Items.Carrot)
table = [[0, 1, 2, 1, 2, 3, 4, 3, 4, 5, 6, 5, 4, 3, 2, 3], [1, 0, 1, 2, 3, 4, 3, 2, 3, 4, 5, 4, 3, 2, 1, 2], [2, 1, 0, 1, 2, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3], [1, 2, 1, 0, 1, 2, 3, 2, 3, 4, 5, 4, 3, 2, 3, 4], [2, 3, 2, 1, 0, 1, 2, 1, 2, 3, 4, 3, 4, 3, 4, 5], [3, 4, 3, 2, 1, 0, 1, 2, 3, 2, 3, 4, 5, 4, 5, 6], [4, 3, 2, 3, 2, 1, 0, 1, 2, 1, 2, 3, 4, 3, 4, 5], [3, 2, 1, 2, 1, 2, 1, 0, 1, 2, 3, 2, 3, 2, 3, 4], [4, 3, 2, 3, 2, 3, 2, 1, 0, 1, 2, 1, 2, 1, 2, 3], [5, 4, 3, 4, 3, 2, 1, 2, 1, 0, 1, 2, 3, 2, 3, 4], [6, 5, 4, 5, 4, 3, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3], [5, 4, 3, 4, 3, 4, 3, 2, 1, 2, 1, 0, 1, 2, 3, 2], [4, 3, 2, 3, 4, 5, 4, 3, 2, 3, 2, 1, 0, 1, 2, 1], [3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2], [2, 1, 2, 3, 4, 5, 4, 3, 2, 3, 4, 3, 2, 1, 0, 1], [3, 2, 3, 4, 5, 6, 5, 4, 3, 4, 3, 2, 1, 2, 1, 0]]
points = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (2, 2), (3, 2), (3, 3), (2, 3), (1, 3), (1, 2), (0, 2), (0, 3), (0, 4), (1, 4), (1, 5), (0, 5), (0, 6), (0, 7), (1, 7), (1, 6), (2, 6), (2, 7), (3, 7), (3, 6), (3, 5), (2, 5), (2, 4), (3, 4), (4, 4), (5, 4), (5, 5), (4, 5), (4, 6), (4, 7), (5, 7), (5, 6), (6, 6), (6, 7), (7, 7), (7, 6), (7, 5), (6, 5), (6, 4), (7, 4), (7, 3), (7, 2), (6, 2), (6, 3), (5, 3), (4, 3), (4, 2), (5, 2), (5, 1), (4, 1), (4, 0), (5, 0), (6, 0), (6, 1), (7, 1), (7, 0), (8, 0), (9, 0), (9, 1), (8, 1), (8, 2), (8, 3), (9, 3), (9, 2), (10, 2), (10, 3), (11, 3), (11, 2), (11, 1), (10, 1), (10, 0), (11, 0), (12, 0), (12, 1), (13, 1), (13, 0), (14, 0), (15, 0), (15, 1), (14, 1), (14, 2), (15, 2), (15, 3), (14, 3), (13, 3), (13, 2), (12, 2), (12, 3), (12, 4), (12, 5), (13, 5), (13, 4), (14, 4), (15, 4), (15, 5), (14, 5), (14, 6), (15, 6), (15, 7), (14, 7), (13, 7), (13, 6), (12, 6), (12, 7), (11, 7), (10, 7), (10, 6), (11, 6), (11, 5), (11, 4), (10, 4), (10, 5), (9, 5), (9, 4), (8, 4), (8, 5), (8, 6), (9, 6), (9, 7), (8, 7), (8, 8), (9, 8), (9, 9), (8, 9), (8, 10), (8, 11), (9, 11), (9, 10), (10, 10), (10, 11), (11, 11), (11, 10), (11, 9), (10, 9), (10, 8), (11, 8), (12, 8), (12, 9), (13, 9), (13, 8), (14, 8), (15, 8), (15, 9), (14, 9), (14, 10), (15, 10), (15, 11), (14, 11), (13, 11), (13, 10), (12, 10), (12, 11), (12, 12), (12, 13), (13, 13), (13, 12), (14, 12), (15, 12), (15, 13), (14, 13), (14, 14), (15, 14), (15, 15), (14, 15), (13, 15), (13, 14), (12, 14), (12, 15), (11, 15), (10, 15), (10, 14), (11, 14), (11, 13), (11, 12), (10, 12), (10, 13), (9, 13), (9, 12), (8, 12), (8, 13), (8, 14), (9, 14), (9, 15), (8, 15), (7, 15), (7, 14), (6, 14), (6, 15), (5, 15), (4, 15), (4, 14), (5, 14), (5, 13), (4, 13), (4, 12), (5, 12), (6, 12), (6, 13), (7, 13), (7, 12), (7, 11), (6, 11), (6, 10), (7, 10), (7, 9), (7, 8), (6, 8), (6, 9), (5, 9), (5, 8), (4, 8), (4, 9), (4, 10), (5, 10), (5, 11), (4, 11), (3, 11), (2, 11), (2, 10), (3, 10), (3, 9), (3, 8), (2, 8), (2, 9), (1, 9), (1, 8), (0, 8), (0, 9), (0, 10), (1, 10), (1, 11), (0, 11), (0, 12), (0, 13), (1, 13), (1, 12), (2, 12), (3, 12), (3, 13), (2, 13), (2, 14), (3, 14), (3, 15), (2, 15), (1, 15), (1, 14), (0, 14), (0, 15)]

if __name__ == "__main__":
    lb_sunflowers()
