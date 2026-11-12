from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-sol/open-directions/sunflowers-pipeline/lb_sunflowers.py
# S3：每机三条带，先播下一带，再收更早一带，保留两代在田中成熟。

def lb_sunflowers():
    set_world_size(32)
    clear()
    dispatch(0, 32, get_time() + 120)
    quick_print("pipeline_done", get_time(), num_items(Items.Power))


def dispatch(first, count, until):
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch, first + left, count - left, until)
        if handle == None:
            dispatch(first + left, count - left, until)
        else:
            handles.append(handle)
        count = left
    pipeline(first, until)
    for handle in handles:
        wait_for(handle)


def seed_zone(worker, zone):
    buckets = []
    for _ in range(9):
        buckets.append([])
    first = zone * 32 // 3
    last = (zone + 1) * 32 // 3
    for x in range(first, last):
        goto(x, worker)
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Sunflower)
        buckets[15 - measure()].append(x)
        water()
    return buckets


def collect_zone(worker, buckets, until):
    for rank in range(9):
        for x in buckets[rank]:
            goto(x, worker)
            while not can_harvest():
                if get_time() >= until:
                    return False
                water()
                for _ in range(32):
                    pass
            harvest()
    return True


def pipeline(worker, until):
    offset = worker % 3
    queue = []
    for zone in range(2):
        queue.append(seed_zone(worker, (zone + offset) % 3))
    for cycle in range(6):
        queue.append(seed_zone(worker, (cycle + 2 + offset) % 3))
        if not collect_zone(worker, queue.pop(0), until):
            quick_print("pipeline_failed", worker, cycle, get_time())
            return False
    for buckets in queue:
        if not collect_zone(worker, buckets, until):
            return False
    quick_print("pipeline_worker", worker, get_time())
    return True


def water():
    if get_water() < 0.425 and num_items(Items.Water) > 32:
        use_item(Items.Water)


def goto(tx, ty):
    dx = (tx - get_pos_x()) % 32
    if dx <= 16:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(32 - dx):
            move(West)
    dy = (ty - get_pos_y()) % 32
    if dy <= 16:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(32 - dy):
            move(South)


if __name__ == "__main__":
    lb_sunflowers()
