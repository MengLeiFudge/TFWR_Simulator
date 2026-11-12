from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-clock/lb_sunflowers.py
# 四批组件；完整打榜时间未取得。
def lb_sunflowers():
    clear()
    for wave in range(4):
        start = get_time()
        result = launch(0, 32, start, wave)
        quick_print("wave_end", wave, get_time(), num_items(Items.Power), result)
        if not result[0]:
            return


def launch(block, count, start, wave):
    ox = (block % 8) * 4
    oy = (block // 8) * 8
    if not goto(ox, oy):
        return [False, 0, 0]
    if count == 1:
        return run_block(block, ox, oy, start, wave)
    half = count // 2
    def child():
        return launch(block + half, half, start, wave)
    handle = spawn_drone(child)
    if handle == None:
        return [False, 0, 0]
    local = launch(block, half, start, wave)
    other = wait_for(handle)
    if other == None:
        return [False, local[1], local[2]]
    return [local[0] and other[0], local[1] + other[1], local[2] + other[2]]


def run_block(block, ox, oy, start, wave):
    deadline = start + 35
    buckets = []
    for _ in range(9):
        buckets.append([])
    for y in range(8):
        for i in range(4):
            x = i
            if y % 2 == 1:
                x = 3 - i
            if get_time() >= deadline or not goto(ox + x, oy + y):
                return [False, 0, 0]
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Sunflower):
                return [False, 0, 0]
            petals = measure()
            if petals == None or petals < 7 or petals > 15:
                return [False, 0, 0]
            buckets[15 - petals].append([ox + x, oy + y])
            if get_water() < 0.425 and num_items(Items.Water) > 32:
                if not use_item(Items.Water):
                    return [False, 0, 0]
    planted = get_time()
    opening = start + 5
    if wave == 0:
        opening = start + 12
    harvested = 0
    late = 0
    for rank in range(9):
        pause_until(opening + rank * 0.75)
        pending = buckets[rank]
        while len(pending) > 0:
            cx = get_pos_x()
            cy = get_pos_y()
            best = 0
            distance = 100
            for i in range(len(pending)):
                pos = pending[i]
                cost = abs(pos[0] - cx) + abs(pos[1] - cy)
                if cost < distance:
                    distance = cost
                    best = i
            pos = pending.pop(best)
            if get_time() >= deadline or not goto(pos[0], pos[1]):
                return [False, harvested, late]
            while not can_harvest():
                if get_time() >= deadline:
                    return [False, harvested, late]
                pause_until(get_time() + 0.02)
            if not harvest():
                return [False, harvested, late]
            harvested += 1
        if get_time() > opening + (rank + 1) * 0.75:
            late += 1
    quick_print("block_end", wave, block, planted - start, get_time() - start, late)
    return [True, harvested, late]


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
