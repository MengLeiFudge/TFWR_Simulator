from __builtins__ import *
# 淘汰候选归档：lb_pumpkins | 原实验路径 .codex/leaderboard-astra/pumpkins-eight-worker/lb_pumpkins.py
# 私有代表：四个15×15隔离区，各八机合作；完整时间待验证。
# 修补政策与移动函数沿用enihsyou；MIT许可见references/leaderboard_scripts/enihsyou_LICENSE.txt。

def lb_pumpkins():
    global s
    s = 32
    set_world_size(s)
    clear()
    handles = []
    for x, y in [(16, 0), (0, 16), (16, 16)]:
        handle = spawn_drone(region, x, y)
        if handle != None:
            handles.append(handle)
    ok = region(0, 0)
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def region(bx, by):
    paths = []
    for worker in range(8):
        path = []
        for i in range(worker * 225 // 8, (worker + 1) * 225 // 8):
            x = i // 15
            y = i % 15
            if x % 2:
                y = 14 - y
            path.append((bx + x, by + y))
        paths.append(path)
    first = True
    waves = 0
    move_to((bx, by))
    while num_items(Items.Pumpkin) < 200000000:
        started = get_time()
        handles = []
        deferred = []
        for worker in range(1, 8):
            handle = spawn_drone(repair, paths[worker], first, started)
            if handle == None:
                deferred.append(worker)
            else:
                handles.append(handle)
        repair(paths[0], first, started)
        for worker in deferred:
            repair(paths[worker], first, started)
        for handle in handles:
            wait_for(handle)
        move_to((bx, by))
        # 所有互斥写者已退出，225株都成熟；区际有空行列阻止合并。
        if not can_harvest():
            quick_print("pumpkin_region_failed", bx, by, waves)
            return False
        harvest()
        first = False
        waves += 1
    quick_print("region_done", bx, by, waves, get_time())
    return True


def repair(path, first, started):
    pending_in = []
    pending_out = []

    def check():
        if can_harvest():
            return
        plant(Entities.Pumpkin)
        if get_time() - started > 5.5 and num_items(Items.Fertilizer) > 32:
            use_item(Items.Fertilizer)
        if can_harvest():
            return
        if get_water() < 0.80 and num_items(Items.Water) > 32:
            use_item(Items.Water)
        if can_harvest():
            return
        pending_in.append((get_pos_x(), get_pos_y()))

    for pos in path:
        move_to(pos)
        if first:
            till()
        plant(Entities.Pumpkin)
    for pos in path:
        move_to(pos)
        check()
    while pending_in or pending_out:
        if not pending_out:
            while pending_in:
                pending_out.append(pending_in.pop())
        last_d = move_to_without_last_move(pending_out.pop())
        if last_d:
            merged = measure()
            if merged != None and merged == measure(last_d):
                continue
            move(last_d)
        check()
    return True


def move_to(pos):
    cx, cy = get_pos_x(), get_pos_y()
    tx, ty = pos

    dx_east = (tx - cx) % s
    dx_west = s - dx_east
    if dx_east < dx_west:
        for _ in range(dx_east):
            move(East)
    else:
        for _ in range(dx_west):
            move(West)

    dy_north = (ty - cy) % s
    dy_south = s - dy_north
    if dy_north < dy_south:
        for _ in range(dy_north):
            move(North)
    else:
        for _ in range(dy_south):
            move(South)


def move_to_without_last_move(pos):
    cx, cy = get_pos_x(), get_pos_y()
    tx, ty = pos

    dx = abs(tx - cx)
    dy = abs(ty - cy)
    if dx == 0 and dy == 0:
        return None
    if cx < tx:
        dir_x = East
    else:
        dir_x = West
    if cy < ty:
        dir_y = North
    else:
        dir_y = South

    if dy > 0:
        dy -= 1
        return_d = dir_y
    elif dx > 0:
        dx -= 1
        return_d = dir_x
    for _ in range(dx):
        move(dir_x)
    for _ in range(dy):
        move(dir_y)
    return return_d


if __name__ == "__main__":
    lb_pumpkins()
