from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-parity-waves-v1/lb_mushrooms_single.py


def lb_mushrooms_single():
    mushroom_waves(30000)


def mushroom_waves(goal):
    size = get_world_size()
    groups = min(max_drones(), size)
    if size % 2:
        quick_print("mushrooms_failed", "even_world_required")
        return
    for batch in range(128):
        if num_items(Items.Mushroom) >= goal:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if not dig():
                return
        if get_ground_type() != Grounds.Mushroom:
            return
        top = get_pos_z()
        if not prepare(0, groups, groups, size, top):
            quick_print("mushrooms_failed", "cover", batch)
            return
        prepared = get_time()
        forced = 0
        for phase in range(128):
            before = num_items(Items.Mushroom)
            columns = 0
            pushes = 0
            for parity in range(2):
                ok, count, seen = wave(0, groups, groups, size, parity, False)
                if not ok:
                    quick_print("mushrooms_failed", "push", batch, phase)
                    return
                columns += seen
                pushes += count
            stock = num_items(Items.Mushroom)
            if phase % 4 == 0:
                quick_print("mushrooms_wave", batch, phase, stock - before, pushes, get_time(), stock)
            if stock >= goal or columns == 0:
                break
            if stock == before:
                ok, count, seen = wave(0, groups, groups, size, forced % 2, True)
                if not ok:
                    quick_print("mushrooms_failed", "holes", batch, phase)
                    return
                forced += 1
                if count == 0 or forced >= 6:
                    break
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom), "work", get_time() - prepared, "holes", forced)


# 准备阶段所有列高差至多1，结束后才开始接收区共享推送。
def prepare(lo, hi, groups, size, top):
    if hi - lo > 1:
        mid = (lo + hi) // 2
        handle = spawn_drone(prepare, mid, hi, groups, size, top)
        ok = prepare(lo, mid, groups, size, top)
        if handle == None:
            other = prepare(mid, hi, groups, size, top)
        else:
            other = wait_for(handle)
        return ok and other
    for y in range(lo, size, groups):
        x = 0
        direction = East
        if y % 2:
            x = size - 1
            direction = West
        if not go(x, y, size):
            return False
        for offset in range(size):
            target = top - (x + y) % 2
            for step in range(256):
                if get_pos_z() <= target:
                    break
                if not dig():
                    return False
            if offset + 1 < size:
                if not move(direction):
                    return False
                if direction == East:
                    x += 1
                else:
                    x -= 1
    return True


# 同一波的源格互不相邻，其他机只会向相反颜色的接收格推送。
# 竞争接收格时可能不配对或push返回False，因此只统计动作，收益读全局实际库存。
def wave(lo, hi, groups, size, parity, digging):
    if hi - lo > 1:
        mid = (lo + hi) // 2
        handle = spawn_drone(wave, mid, hi, groups, size, parity, digging)
        ok, count, seen = wave(lo, mid, groups, size, parity, digging)
        if handle == None:
            right_ok, right_count, right_seen = wave(mid, hi, groups, size, parity, digging)
        else:
            right_ok, right_count, right_seen = wait_for(handle)
        return ok and right_ok, count + right_count, seen + right_seen
    count = 0
    seen = 0
    for y in range(lo, size, groups):
        x = (parity - y) % 2
        direction = East
        if y % 2:
            x = size - 1 - ((size - 1 + y - parity) % 2)
            direction = West
        if not go(x, y, size):
            return False, count, seen
        for offset in range(size // 2):
            if get_ground_type() == Grounds.Mushroom:
                seen += 1
                if digging:
                    if get_hardness() >= 10000000 or not dig():
                        return False, count, seen
                    count += 1
                else:
                    for attempt in range(16):
                        if get_ground_type() != Grounds.Mushroom:
                            break
                        z = get_pos_z()
                        color = measure()
                        pushed = False
                        for target in DIRECTIONS:
                            if get_pos_z(target) >= z or get_ground_type(target) != Grounds.Mushroom or measure(target) != color:
                                continue
                            if push(target):
                                count += 1
                                pushed = True
                                break
                        if not pushed:
                            break
            if offset + 1 < size // 2:
                if not move(direction) or not move(direction):
                    return False, count, seen
    return True, count, seen


def go(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for step in range(dx):
        if not move(horizontal):
            return False
    for step in range(dy):
        if not move(vertical):
            return False
    return True


DIRECTIONS = [North, East, South, West]


if __name__ == "__main__":
    lb_mushrooms_single()
