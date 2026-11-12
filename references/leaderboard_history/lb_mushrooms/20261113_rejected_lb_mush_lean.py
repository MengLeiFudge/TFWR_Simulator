from __builtins__ import *
# 完整轮时间：未取得（精简实现候选；配对结构与现源相同，去掉逐格缓存与重复读数）。

DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


def lb_mushrooms_lean():
    began = get_time()
    blocks = make_blocks()
    for batch in range(128):
        if num_items(Items.Mushroom) >= 240000:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for covers in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if get_time() - began > 7200 or not dig():
                quick_print("mushrooms_failed", "find", batch)
                return
        if get_ground_type() != Grounds.Mushroom:
            quick_print("mushrooms_failed", "find_limit", batch)
            return
        top = get_pos_z()
        height = 0
        for step in range(7):
            if get_ground_type() != Grounds.Mushroom:
                break
            if not dig():
                quick_print("mushrooms_failed", "probe", batch)
                return
            height += 1
        if not height or height > 6:
            quick_print("mushrooms_failed", "height", batch, height)
            return
        quick_print("mushrooms_selected", batch, height, get_time())
        if height != 6:
            continue
        if not dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch)
            return
        if not move_to(0, 0):
            return
        levels = max(1, height - 1)
        quick_print("mushrooms_probe", batch, height, levels, get_time())
        handles = []
        results = []
        for k in range(1, len(blocks)):
            handle = spawn_drone(work_patch, blocks[k], top, levels)
            if handle == None:
                results.append(work_patch(blocks[k], top, levels))
            else:
                handles.append(handle)
        results.append(work_patch(blocks[0], top, levels))
        for handle in handles:
            results.append(wait_for(handle))
        complete = True
        for result in results:
            if not result:
                complete = False
                break
        if complete:
            quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
        else:
            quick_print("mushrooms_restart", "patch", batch, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def work_patch(block, top, levels):
    for layer in range(levels):
        if num_items(Items.Mushroom) >= 240000:
            return True
        result = work_layer(block, top - layer)
        if result == None:
            return False
        if result == 0:
            return True
    return True


def dig_layer(target):
    size = get_world_size()
    workers = min(size, max_drones())
    handles = []
    ok = True
    for x in range(workers - 1):
        if not move_to(x, 0):
            ok = False
            break
        handle = spawn_drone(dig_columns, x, workers, size, target)
        if handle == None:
            if not dig_columns(x, workers, size, target):
                ok = False
        else:
            handles.append(handle)
    if ok and not dig_columns(workers - 1, workers, size, target):
        ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


def dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
        if not move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() > target:
                return False
            if not move(North):
                return False
    return True


def make_blocks():
    size = get_world_size()
    limit = max(1, size // 4)
    capacity = max_drones()
    gx = 1
    gy = 1
    best = 1
    for ty in range(1, limit + 1):
        tx = min(limit, capacity // ty)
        if tx * ty > best:
            best = tx * ty
            gx = tx
            gy = ty
    blocks = []
    for k in range(best):
        bx = k % gx
        by = k // gx
        blocks.append((bx * size // gx, (bx + 1) * size // gx,
                       by * size // gy, (by + 1) * size // gy))
    return blocks


# 蛇形巡访：行内每步只走 1 次 move；行首才用 move_to 归位。
def work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    floor = ceiling - 2
    merges = 0
    for y in range(y0, y1):
        reverse = (y - y0) % 2 != 0
        xs = x0
        step = East
        if reverse:
            xs = x1 - 1
            step = West
        if not move_to(xs, y):
            return None
        for i in range(x1 - x0):
            if i > 0:
                if not move(step):
                    return None
            x = xs
            if reverse:
                x = xs - i
            else:
                x = xs + i
            if x == 0 and y == 0:
                continue
            count = work_cell(x, y, x0, x1, y0, y1, floor, ceiling)
            if count == None:
                return None
            merges += count
    return merges


# 单格处理：直接推 → 同层同色三推 → 邻格喂料；全都做不到就挖一格。
def work_cell(x, y, x0, x1, y0, y1, floor, ceiling):
    z = get_pos_z()
    if z < floor:
        return 0
    if get_ground_type() != Grounds.Mushroom:
        return prep_receiver(x, x0, x1, y, y0, y1, floor)
    t = measure()
    merges = 0
    if z >= ceiling:
        if direct_push(x, x0, x1, y, y0, y1, z, t, floor):
            merges += 1
        elif fixture_push(x, x0, x1, y, y0, y1, z, t, floor):
            merges += 1
        else:
            if get_hardness() >= 10000000 or not dig():
                return None
            if get_pos_z() != z - 1:
                return None
    count = feed_loop(x, x0, x1, y, y0, y1, floor)
    if count == None:
        return None
    return merges + count


# 把本格顶块直接推进更低的同色邻格；一次 merge。
def direct_push(x, x0, x1, y, y0, y1, z, t, floor):
    if y + 1 < y1 and get_ground_type(North) == Grounds.Mushroom:
        target = get_pos_z(North)
        if floor < target and target < z and measure(North) == t:
            if not push(North):
                return False
            return True
    if x + 1 < x1 and get_ground_type(East) == Grounds.Mushroom:
        target = get_pos_z(East)
        if floor < target and target < z and measure(East) == t:
            if not push(East):
                return False
            return True
    if y > y0 and get_ground_type(South) == Grounds.Mushroom:
        target = get_pos_z(South)
        if floor < target and target < z and measure(South) == t:
            if not push(South):
                return False
            return True
    if x > x0 and get_ground_type(West) == Grounds.Mushroom:
        target = get_pos_z(West)
        if floor < target and target < z and measure(West) == t:
            if not push(West):
                return False
            return True
    return False


# 本格与同层同色邻格 A 都有块、另有一个低两格的邻格 C 时，
# 先把 C 抬一格，再让 A 经本格合并进 C（三次 push、两次 move）。
def fixture_push(x, x0, x1, y, y0, y1, z, t, floor):
    if z - 2 < floor:
        return False
    if y + 1 < y1 and get_ground_type(North) == Grounds.Mushroom and get_pos_z(North) == z and measure(North) == t:
        return fixture_into(0, x, x0, x1, y, y0, y1, z)
    if x + 1 < x1 and get_ground_type(East) == Grounds.Mushroom and get_pos_z(East) == z and measure(East) == t:
        return fixture_into(1, x, x0, x1, y, y0, y1, z)
    if y > y0 and get_ground_type(South) == Grounds.Mushroom and get_pos_z(South) == z and measure(South) == t:
        return fixture_into(2, x, x0, x1, y, y0, y1, z)
    if x > x0 and get_ground_type(West) == Grounds.Mushroom and get_pos_z(West) == z and measure(West) == t:
        return fixture_into(3, x, x0, x1, y, y0, y1, z)
    return False


def fixture_into(i, x, x0, x1, y, y0, y1, z):
    if i != 0 and y + 1 < y1 and get_pos_z(North) == z - 2:
        return fixture_step(DIRECTIONS[i], BACKS[i], North)
    if i != 1 and x + 1 < x1 and get_pos_z(East) == z - 2:
        return fixture_step(DIRECTIONS[i], BACKS[i], East)
    if i != 2 and y > y0 and get_pos_z(South) == z - 2:
        return fixture_step(DIRECTIONS[i], BACKS[i], South)
    if i != 3 and x > x0 and get_pos_z(West) == z - 2:
        return fixture_step(DIRECTIONS[i], BACKS[i], West)
    return False


def fixture_step(source, back, sink):
    if not push(sink):
        return False
    if not move(source) or not push(back):
        return False
    if not move(back) or not push(sink):
        return False
    return True


# 反复把同色更高的邻格顶块推入本格（本格因此逐步下降）。
def feed_loop(x, x0, x1, y, y0, y1, floor):
    matched = 0
    while True:
        z = get_pos_z()
        if z < floor:
            return matched
        if get_ground_type() != Grounds.Mushroom:
            return matched
        t = measure()
        if y + 1 < y1 and get_ground_type(North) == Grounds.Mushroom and get_pos_z(North) > z and measure(North) == t:
            if not feed_from(North, South):
                return None
            matched += 1
            continue
        if x + 1 < x1 and get_ground_type(East) == Grounds.Mushroom and get_pos_z(East) > z and measure(East) == t:
            if not feed_from(East, West):
                return None
            matched += 1
            continue
        if y > y0 and get_ground_type(South) == Grounds.Mushroom and get_pos_z(South) > z and measure(South) == t:
            if not feed_from(South, North):
                return None
            matched += 1
            continue
        if x > x0 and get_ground_type(West) == Grounds.Mushroom and get_pos_z(West) > z and measure(West) == t:
            if not feed_from(West, East):
                return None
            matched += 1
            continue
        # 没有单块可喂时，找两块同色且高出本格两层的邻格依次推入。
        count = pair_feed(x, x0, x1, y, y0, y1, z, floor)
        if count == None:
            return None
        if count == 0:
            return matched
        matched += 1


def feed_from(source, back):
    if not move(source):
        return False
    pushed = push(back)
    if not move(back):
        return False
    return pushed


# 非蘑菇柱：挖到 floor 作为接收柱，再把两块同色高柱依次推入。
def prep_receiver(x, x0, x1, y, y0, y1, floor):
    while get_pos_z() > floor:
        if get_ground_type() == Grounds.Mushroom:
            return 0
        if get_hardness() >= 10000000 or not dig():
            return None
    if get_pos_z() != floor:
        return None
    if get_ground_type() == Grounds.Mushroom:
        return 0
    return pair_feed(x, x0, x1, y, y0, y1, floor, floor)


# 找两块同色、且都高出目标至少两格的邻格，依次推入本格完成一次 merge。
def pair_feed(x, x0, x1, y, y0, y1, z, floor):
    types = [-1, -1, -1, -1]
    heights = [0, 0, 0, 0]
    if y + 1 < y1 :
        if get_ground_type(North) == Grounds.Mushroom:
            types[0] = measure(North)
            heights[0] = get_pos_z(North)
    if x + 1 < x1 :
        if get_ground_type(East) == Grounds.Mushroom:
            types[1] = measure(East)
            heights[1] = get_pos_z(East)
    if y > y0 :
        if get_ground_type(South) == Grounds.Mushroom:
            types[2] = measure(South)
            heights[2] = get_pos_z(South)
    if x > x0 :
        if get_ground_type(West) == Grounds.Mushroom:
            types[3] = measure(West)
            heights[3] = get_pos_z(West)
    first = -1
    second = -1
    for i in range(4):
        if types[i] < 0 or heights[i] < z + 2:
            continue
        if first < 0:
            first = i
            continue
        if types[i] == types[first]:
            second = i
            break
    if second < 0:
        return 0
    if not feed_from(DIRECTIONS[first], BACKS[first]):
        return None
    if not feed_from(DIRECTIONS[second], BACKS[second]):
        return None
    return 1


def move_to(tx, ty):
    size = get_world_size()
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


if __name__ == "__main__":
    lb_mushrooms_lean()
