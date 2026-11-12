from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-local-relaxation/lb_cactus.py
# 私有C5代表：横纵相邻违例交替扫描；完整时间未取得。

def lb_cactus():
    started = get_time()
    dispatch(0, 32, 0, False, True)
    quick_print("planted", get_time() - started)
    reverse = False
    for sweep in range(128):
        horizontal = dispatch(0, 32, 0, reverse, False)
        vertical = dispatch(0, 32, 1, reverse, False)
        quick_print("sweep", sweep, horizontal, vertical, get_time() - started)
        if not horizontal and not vertical:
            goto(0, 0)
            while not can_harvest():
                pass
            harvest()
            quick_print("done", get_time() - started, num_items(Items.Cactus))
            return True
        reverse = not reverse
    quick_print("sweep_limit", get_time() - started)
    return False


def dispatch(first, count, axis, reverse, planting):
    # 一次扫描内每行/列唯一写者；两轴之间等整棵派发树返回。
    handles = []
    changed = 0
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch, first + left, count - left, axis, reverse, planting)
        if handle == None:
            changed += dispatch(first + left, count - left, axis, reverse, planting)
        else:
            handles.append(handle)
        count = left
    changed += scan(first, axis, reverse, planting)
    for handle in handles:
        changed += wait_for(handle)
    return changed


def scan(line, axis, reverse, planting):
    if planting:
        goto(0, line)
        for _ in range(32):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
            move(East)
        return 0
    start = 0
    if reverse:
        start = 31
    if axis == 0:
        goto(start, line)
        forward = East
        if reverse:
            forward = West
    else:
        goto(line, start)
        forward = North
        if reverse:
            forward = South
    changes = 0
    current = measure()
    for _ in range(31):
        neighbor = measure(forward)
        bad = current > neighbor
        if reverse:
            bad = current < neighbor
        if bad:
            swap(forward)
            changes += 1
        else:
            current = neighbor
        move(forward)
    return changes


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
    lb_cactus()
