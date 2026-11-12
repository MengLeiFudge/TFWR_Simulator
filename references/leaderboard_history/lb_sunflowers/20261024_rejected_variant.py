from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-sol/sunflowers/candidate/lb_sunflowers.py
# 本地有界候选；尚无游戏打榜时间。
def lb_sunflowers():
    if get_world_size() != FIELD_SIZE:
        quick_print("sunflowers_batch stopped: unexpected field size")
        return
    workers = []
    for by in range(0, FIELD_SIZE, BLOCK_HEIGHT):
        for bx in range(0, FIELD_SIZE, BLOCK_WIDTH):
            if bx == 28 and by == 24:
                continue
            goto(bx, by)
            worker = spawn_drone(block_worker)
            if worker == None:
                quick_print("sunflowers_batch stopped: dispatch failed", bx, by)
                return
            workers.append(worker)
    goto(28, 24)
    block_worker()
    for worker in workers:
        wait_for(worker)


FIELD_SIZE = 32
BLOCK_WIDTH = 4
BLOCK_HEIGHT = 8
WORKER_COUNT = 32
SIGNAL_HAY = 512
POWER_GOAL = 100000
MAX_BATCHES = 64
WAIT_LIMIT_SECONDS = 30
MATURE_LIMIT_SECONDS = 12


def block_worker():
    bx = get_pos_x()
    by = get_pos_y()
    deadline = get_time() + WAIT_LIMIT_SECONDS
    # 派发未完成前不进入32人Hay屏障；失败时各worker有界退出。
    while num_drones() < WORKER_COUNT:
        if get_time() >= deadline:
            quick_print("sunflowers_batch stopped: launch timeout", bx, by)
            return
    route = block_route(bx, by)
    phase = 0
    for batch in range(1, MAX_BATCHES + 1):
        if num_items(Items.Power) >= POWER_GOAL:
            return
        buckets = []
        for _ in range(9):
            buckets.append([])
        for pos in route:
            goto(pos[0], pos[1])
            if batch == 1:
                # 翻地移除自然草，不产生额外Hay信号。
                if get_ground_type() != Grounds.Soil:
                    till()
            if not plant(Entities.Sunflower):
                quick_print("sunflowers_batch stopped: plant failed", pos)
                return
            if get_water() < 0.425 and num_items(Items.Water) > FIELD_SIZE:
                use_item(Items.Water)
            petals = measure()
            if petals < 7 or petals > 15:
                quick_print("sunflowers_batch stopped: invalid petals", petals)
                return
            buckets[petals - 7].append(pos)
        phase += 1
        if not synchronize(bx, by, phase):
            return
        if bx == 28 and by == 24:
            quick_print("sunflowers_batch planted", "batch=", batch, "phase=", phase, "time=", get_time(), "hay=", num_items(Items.Hay), "power=", num_items(Items.Power))
        for petals in range(15, 6, -1):
            for pos in buckets[petals - 7]:
                if num_items(Items.Power) >= POWER_GOAL:
                    return
                goto(pos[0], pos[1])
                deadline = get_time() + MATURE_LIMIT_SECONDS
                while not can_harvest():
                    if num_items(Items.Power) >= POWER_GOAL:
                        return
                    if get_time() >= deadline:
                        quick_print("sunflowers_batch stopped: mature timeout", pos)
                        return
                harvest()
            phase += 1
            if not synchronize(bx, by, phase):
                return
        if bx == 28 and by == 24:
            quick_print("sunflowers_batch harvested", "batch=", batch, "phase=", phase, "time=", get_time(), "hay=", num_items(Items.Hay), "power=", num_items(Items.Power))
    if bx == 28 and by == 24:
        quick_print("sunflowers_batch bounded_end", "batches=", MAX_BATCHES, "time=", get_time(), "hay=", num_items(Items.Hay), "power=", num_items(Items.Power))


def synchronize(bx, by, phase):
    if num_items(Items.Power) >= POWER_GOAL:
        return False
    goto(bx, by)
    deadline = get_time() + WAIT_LIMIT_SECONDS
    while not can_harvest():
        if num_items(Items.Power) >= POWER_GOAL:
            return False
        if get_time() >= deadline:
            quick_print("sunflowers_batch stopped: signal mature timeout", bx, by, phase)
            return False
    if get_entity_type() != Entities.Grass:
        quick_print("sunflowers_batch stopped: missing signal grass", bx, by, phase)
        return False
    harvest()
    target = phase * WORKER_COUNT * SIGNAL_HAY
    while num_items(Items.Hay) < target:
        if num_items(Items.Power) >= POWER_GOAL:
            return False
        if get_time() >= deadline:
            quick_print("sunflowers_batch stopped: barrier timeout", bx, by, phase, "hay=", num_items(Items.Hay))
            return False
    return num_items(Items.Power) < POWER_GOAL


def block_route(bx, by):
    route = []
    for y in range(1, BLOCK_HEIGHT):
        route.append((bx, by + y))
    for y in range(BLOCK_HEIGHT - 1, 0, -1):
        route.append((bx + 1, by + y))
    for y in range(1, BLOCK_HEIGHT):
        route.append((bx + 2, by + y))
    for y in range(BLOCK_HEIGHT - 1, -1, -1):
        route.append((bx + 3, by + y))
    route.append((bx + 2, by))
    route.append((bx + 1, by))
    return route


def goto(tx, ty):
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % FIELD_SIZE
    if dx <= FIELD_SIZE // 2:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(FIELD_SIZE - dx):
            move(West)
    dy = (ty - y) % FIELD_SIZE
    if dy <= FIELD_SIZE // 2:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(FIELD_SIZE - dy):
            move(South)


if __name__ == "__main__":
    lb_sunflowers()
