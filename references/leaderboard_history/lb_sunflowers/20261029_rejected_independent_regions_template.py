from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-independent-regions/template.py
# 私有32独立区域三批组件，不是完整10万目标成绩。

def lb_sunflowers():
    clear()
    set_world_size(32)
    result = dispatch(0, 32, get_time() + 400)
    quick_print("independent_done", result, get_time(), num_items(Items.Power))


def dispatch(first, count, deadline):
    if not go(first * 32, deadline):
        return False
    if count == 1:
        return worker(first, deadline)
    half = count // 2
    def child():
        return dispatch(first + half, count - half, deadline)
    handle = spawn_drone(child)
    if handle == None:
        return False
    local = dispatch(first, half, deadline)
    other = wait_for(handle)
    return local and other


def empty_buckets():
    buckets = []
    for _ in range(9):
        buckets.append([])
    return buckets


def plant_cell(cell, buckets, deadline):
    if not go(cell, deadline):
        return False
    if get_ground_type() != Grounds.Soil:
        till()
    if not plant(Entities.Sunflower):
        return False
    petals = measure()
    if petals == None or petals < 7 or petals > 15:
        return False
    buckets[15 - petals].append(cell)
    return water()


def worker(job, deadline):
    buckets = empty_buckets()
    for cycle in range(3):
        began = get_time()
        if not rolling or cycle == 0:
            buckets = empty_buckets()
            for cell in range(job * 32, job * 32 + 32):
                if not plant_cell(cell, buckets, deadline):
                    return False
        planted = get_time()
        following = empty_buckets()
        for rank in range(9):
            for cell in buckets[rank]:
                if not go(cell, deadline):
                    return False
                while not can_harvest():
                    if get_time() > deadline or not water():
                        return False
                    pause()
                if not harvest():
                    return False
                if rolling and cycle < 2:
                    if not plant_cell(cell, following, deadline):
                        return False
        buckets = following
        quick_print("independent_wave", job, cycle, began, planted, get_time(), num_items(Items.Power))
    return True
