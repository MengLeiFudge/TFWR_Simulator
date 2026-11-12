from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-rank-cull/lb_sunflowers.py
# 私有三循环主动清除未成熟最大档；完整三类时间尚未取得。
def lb_sunflowers():
    clear()
    set_world_size(32)
    deadline = get_time() + 90
    result = launch(0, 32, deadline)
    quick_print("stream_done", get_time(), num_items(Items.Power), result)


def launch(block, count, deadline):
    ox = block % 8 * 4
    oy = block // 8 * 8
    if not goto(ox, oy, deadline):
        return False
    if count == 1:
        return worker(block, ox, oy, deadline)
    half = count // 2
    def child():
        return launch(block + half, half, deadline)
    handle = spawn_drone(child)
    if handle == None:
        quick_print("stream_failed", "spawn", block, get_time())
        return False
    local = launch(block, half, deadline)
    other = wait_for(handle)
    return local and other


def pause():
    i = 0
    while i < 64:
        i += 1


def goto(tx, ty, deadline):
    dx = (tx - get_pos_x()) % 32
    direction = East
    if dx > 16:
        direction = West
        dx = 32 - dx
    for _ in range(dx):
        if get_time() > deadline or not move(direction):
            return False
    dy = (ty - get_pos_y()) % 32
    direction = North
    if dy > 16:
        direction = South
        dy = 32 - dy
    for _ in range(dy):
        if get_time() > deadline or not move(direction):
            return False
    return True


def water():
    if get_water() < 0.5 and num_items(Items.Water) >= 2:
        use_item(Items.Water, 2)
    return True


def barrier(marker, phase, deadline):
    if not goto(marker[0], marker[1], deadline):
        return False
    while not can_harvest():
        if get_time() > deadline:
            return False
        pause()
    # 全场只保留Grass信号点与Sunflower。Grass请求的三种伴生均不存在。
    if not harvest():
        return False
    target = phase * 32 * 512
    while num_items(Items.Hay) < target:
        if num_items(Items.Power) >= 100000:
            return True
        if get_time() > deadline:
            return False
        pause()
    return True


def sow_quota(position, buckets, deadline):
    if not goto(position[0], position[1], deadline):
        return False
    for attempt in range(128):
        if get_time() > deadline or not plant(Entities.Sunflower):
            return False
        petals = measure()
        if petals == None or petals < 7 or petals > 15:
            return False
        if len(buckets[petals]) < 5:
            buckets[petals].append(position)
            return water()
        harvest()
    return False


def worker(block, ox, oy, deadline):
    marker = (ox + 1, oy + 3)
    positions = []
    for y in range(8):
        for i in range(4):
            x = i
            if y % 2 == 1:
                x = 3 - i
            pos = (ox + x, oy + y)
            if pos != marker:
                positions.append(pos)
    phase = 0
    harvested = 0
    for cycle in range(3):
        start = get_time()
        buckets = {}
        for petals in range(7, 16):
            buckets[petals] = []
        for pos in positions:
            if not goto(pos[0], pos[1], deadline):
                quick_print("quota_failed", "seed_move", block, cycle, get_time())
                return False
            if get_ground_type() != Grounds.Soil:
                till()
            if not sow_quota(pos, buckets, deadline):
                quick_print("quota_failed", "seed", block, cycle, get_time())
                return False
        seeded = get_time()
        counts = []
        for petals in range(7, 16):
            counts.append(len(buckets[petals]))
        phase += 1
        if not barrier(marker, phase, deadline):
            quick_print("quota_failed", "seed_barrier", block, cycle, get_time())
            return False
        ready = get_time()
        ledger = []
        for maximum in range(15, 6, -1):
            began = get_time()
            maturity = 0
            pending = buckets[maximum]
            while len(pending) > 0:
                best = 0
                distance = 100
                cx = get_pos_x()
                cy = get_pos_y()
                for index in range(len(pending)):
                    pos = pending[index]
                    cost = abs(pos[0] - cx) + abs(pos[1] - cy)
                    if cost < distance:
                        distance = cost
                        best = index
                pos = pending.pop(best)
                if not goto(pos[0], pos[1], deadline):
                    return False
                if not can_harvest():
                    maturity += 1
                if not harvest():
                    return False
                harvested += 1
            finished = get_time()
            phase += 1
            if not barrier(marker, phase, deadline):
                quick_print("quota_failed", "rank_barrier", block, cycle, maximum, get_time())
                return False
            ledger.append((maximum, began, finished, get_time(), maturity))
        quick_print("quota_cycle", block, cycle, start, seeded, ready, get_time(), num_items(Items.Power), counts, ledger)
    quick_print("quota_worker", block, harvested, get_time())
    return True


if __name__ == "__main__":
    lb_sunflowers()
