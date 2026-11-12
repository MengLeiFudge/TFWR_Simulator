from __builtins__ import *
# 淘汰候选归档：lb_pumpkins | 原实验路径 .codex/leaderboard-sol/open-directions/pumpkins-partial/lb_pumpkins.py
# P1：成熟子块即收，不持有跨收割的成熟或修补缓存。

def lb_pumpkins():
    set_world_size(32)
    clear()
    return dispatch(0, 32, get_time() + 60)


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
    result = work(first, until)
    for handle in handles:
        result = wait_for(handle) and result
    return result


def work(worker, until):
    bx = worker % 8 * 4
    by = worker // 8 * 8
    seeded = False
    visits = 0
    mature = 0
    began = get_time()
    while get_time() < until and num_items(Items.Pumpkin) < 200000000:
        for x in range(4):
            for i in range(8):
                y = i
                if x % 2:
                    y = 7 - i
                goto(bx + x, by + y)
                if get_ground_type() != Grounds.Soil:
                    till()
                if can_harvest():
                    harvest()
                    mature += 1
                entity = get_entity_type()
                if entity == None or entity == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                elif entity == Entities.Pumpkin:
                    if seeded and get_time() - began > 5.5 and num_items(Items.Fertilizer) > 32:
                        use_item(Items.Fertilizer)
                    if get_water() < 0.80 and num_items(Items.Water) > 32:
                        use_item(Items.Water)
                visits += 1
        seeded = True
    quick_print("partial_region", worker, visits, mature, get_time())
    return True


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
    lb_pumpkins()
