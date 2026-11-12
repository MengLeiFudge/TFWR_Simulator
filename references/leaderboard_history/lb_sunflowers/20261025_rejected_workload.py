from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-workload/lb_sunflowers.py
# 三批组件；完整本地/短测/官方时间均未取得。
def lb_sunflowers():
    clear()
    for wave in range(3):
        start = get_time()
        planted = launch(0, 32, 0, [], [], wave, start + 45)
        if not planted[0] or len(planted[1]) != 32:
            quick_print("workload_failed", wave, "plant_join", get_time())
            return
        records = planted[1]
        windows = []
        cursor = get_time() + 1.5
        for rank in range(9):
            ticks = 0
            ready = 0
            for record in records:
                ticks = max(ticks, record[2][rank])
                ready = max(ready, record[3][rank])
            cursor = max(cursor, ready)
            duration = ticks * 0.00016461 * 1.18 + 0.025
            if wave == 0 and rank == 0:
                duration *= 2
            windows.append([cursor, cursor + duration])
            cursor += duration
        quick_print("workload_plan", wave, get_time() - start, windows)
        collected = launch(0, 32, 1, records, windows, wave, start + 45)
        quick_print("workload_wave", wave, get_time(), num_items(Items.Power), collected)
        if not collected[0] or len(collected[1]) != 32:
            return


def launch(block, count, stage, records, windows, wave, deadline):
    ox = (block % 8) * 4
    oy = (block // 8) * 8
    if get_time() >= deadline or not goto(ox, oy):
        return [False, []]
    if count == 1:
        if stage == 0:
            result = plant_block(block, ox, oy, deadline)
        else:
            result = harvest_block(block, records[0], windows, wave, deadline)
        return [result[0], [result[1]]]
    half = count // 2
    right = records[half:]
    left = records[:half]
    def child():
        return launch(block + half, half, stage, right, windows, wave, deadline)
    handle = spawn_drone(child)
    if handle == None:
        return [False, []]
    local = launch(block, half, stage, left, windows, wave, deadline)
    other = wait_for(handle)
    if other == None:
        return [False, local[1]]
    for record in other[1]:
        local[1].append(record)
    return [local[0] and other[0], local[1]]


def plant_block(block, ox, oy, deadline):
    buckets = []
    ready = []
    for _ in range(9):
        buckets.append([])
        ready.append(0)
    for y in range(8):
        for i in range(4):
            x = i
            if y % 2 == 1:
                x = 3 - i
            if get_time() >= deadline or not goto(ox + x, oy + y):
                return [False, [block, "plant_move"]]
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Sunflower):
                return [False, [block, "plant"]]
            petals = measure()
            if petals == None or petals < 7 or petals > 15:
                return [False, [block, "petals"]]
            rank = 15 - petals
            buckets[rank].append([ox + x, oy + y])
            if get_water() < 0.425 and num_items(Items.Water) > 32:
                if not use_item(Items.Water):
                    return [False, [block, "water"]]
            # 以最大生长偏差和20%水量衰减留量估计，不当成成熟证明。
            ready[rank] = max(ready[rank], get_time() + 8.4 / (1 + 3.2 * get_water()))
    routes = []
    costs = []
    cx = ox
    cy = oy
    for rank in range(9):
        pending = buckets[rank]
        route = []
        moves = 0
        while len(pending) > 0:
            best = 0
            distance = 100
            for i in range(len(pending)):
                pos = pending[i]
                cost = abs(pos[0] - cx) + abs(pos[1] - cy)
                if cost < distance:
                    distance = cost
                    best = i
            pos = pending.pop(best)
            moves += distance
            route.append(pos)
            cx = pos[0]
            cy = pos[1]
        routes.append(route)
        costs.append(moves * 204 + len(route) * 250 + 20)
    return [True, [block, routes, costs, ready]]


def harvest_block(block, record, windows, wave, deadline):
    harvested = 0
    late = 0
    lateness = 0
    for rank in range(9):
        pause_until(windows[rank][0])
        for pos in record[1][rank]:
            if get_time() >= deadline or not goto(pos[0], pos[1]):
                return [False, [block, "harvest_move", harvested]]
            while not can_harvest():
                if get_time() >= deadline:
                    return [False, [block, "maturity", harvested]]
                pause_until(get_time() + 0.02)
            if not harvest():
                return [False, [block, "harvest", harvested]]
            harvested += 1
        if get_time() > windows[rank][1]:
            late += 1
            lateness = max(lateness, get_time() - windows[rank][1])
    quick_print("workload_block", wave, block, harvested, late, lateness, get_time())
    return [True, [block, harvested, late, lateness]]


def pause_until(deadline):
    while get_time() < deadline:
        count = 0
        while count < 64:
            count += 1


def goto(tx, ty):
    dx = (tx - get_pos_x()) % 32
    direction = East
    steps = dx
    if dx > 16:
        direction = West
        steps = 32 - dx
    for _ in range(steps):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % 32
    direction = North
    steps = dy
    if dy > 16:
        direction = South
        steps = 32 - dy
    for _ in range(steps):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_sunflowers()
