from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-cross-cover-v1/lb_mushrooms_single.py

def lb_mushrooms_single():
    began = get_time()
    blocks = make_blocks()
    for batch in range(128):
        if num_items(Items.Mushroom) >= 30000:
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
        if not dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch)
            return
        if not move_to(0, 0):
            return
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
        for result in results:
            if not result:
                quick_print("mushrooms_failed", "patch", batch)
                return
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def work_patch(block, top, levels):
    for layer in range(levels):
        if num_items(Items.Mushroom) >= 30000:
            return True
        result = work_layer(block, top - layer)
        if result == None:
            return False
        if result[2] == 0:
            return True
    return True


# Rock在邻格挖掘后自动清到当前挖深前一格；中心多挖一层M即可露出十字邻格。
# x+2y模5的中心互不相邻，准备阶段M高差至多1；保留(0,0)完整高度供主机测厚。
def dig_layer(target):
    size = get_world_size()
    groups = min(size, max_drones())
    return dig_cover(0, groups, groups, size, target)


def dig_cover(lo, hi, groups, size, target):
    if hi - lo > 1:
        mid = (lo + hi) // 2
        handle = spawn_drone(dig_cover, mid, hi, groups, size, target)
        ok = dig_cover(lo, mid, groups, size, target)
        if handle == None:
            right = dig_cover(mid, hi, groups, size, target)
        else:
            right = wait_for(handle)
        return ok and right
    for x in range(lo, size, groups):
        for offset in range(size):
            y = offset
            if x % 2:
                y = size - 1 - offset
            residue = (x + 2 * y) % 5
            center = residue == 0
            covered = center
            if residue == 1 and x > 0 and (x != 1 or y != 0):
                covered = True
            elif residue == 4 and x + 1 < size:
                covered = True
            elif residue == 2 and y > 0 and (x != 0 or y != 1):
                covered = True
            elif residue == 3 and y + 1 < size:
                covered = True
            if covered and not center:
                continue
            if not move_to(x, y):
                return False
            for step in range(256):
                if get_pos_z() <= target:
                    break
                if get_hardness() >= 10000000 or not dig():
                    return False
            if get_pos_z() != target or get_ground_type() != Grounds.Mushroom:
                return False
            if center and (x != 0 or y != 0):
                if not dig():
                    return False
    return True


# 主机只创建少量矩形边界，逐格坐标和邻格交给各子机就地计算。
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


# 蛇形遍历本分区，直接或中转配对后再挖掘，必要时接收邻柱。
# 各工人独立推进本分区；以实际柱顶处理塌方后的高度变化。
def work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    cache = {}
    floor = ceiling - 6
    pairs = 0
    digs = 0
    mushrooms = 0
    for y in range(y0, y1):
        for offset in range(x1 - x0):
            x = x0 + offset
            if (y - y0) % 2 != 0:
                x = x1 - 1 - offset
            if x == 0 and y == 0:
                continue
            if not move_to(x, y):
                return None
            neighbors = []
            if y + 1 < y1:
                neighbors.append(0)
            if x + 1 < x1:
                neighbors.append(1)
            if y > y0 and (x != 0 or y != 1):
                neighbors.append(2)
            if x > x0 and (x != 1 or y != 0):
                neighbors.append(3)
            z = get_pos_z()
            if z < floor:
                continue
            # 已公开柱可能高于上次计划高度；仍以当前柱顶处理。
            mushroom = get_ground_type() == Grounds.Mushroom
            if mushroom:
                mushrooms += 1
            if z >= ceiling and mushroom:
                count = carry_match(cache, x, y, neighbors, floor)
                if count == None:
                    return None
                pairs += count
                if count == 0:
                    if get_hardness() >= 10000000 or not dig():
                        return None
                    digs += 1
            cache["ready"] = False
            count = feed_column(neighbors, floor, cache, x, y)
            if count == None:
                return None
            pairs += count
            if not cache["ready"]:
                read_column(cache, x, y)
                for i in neighbors:
                    dx, dy = OFFSETS[i]
                    read_column(cache, x + dx, y + dy, DIRECTIONS[i])
    return pairs, digs, mushrooms


# 直接从脚下推送省去前往邻格再返回的两次移动。
def push_match(neighbors, floor):
    if get_ground_type() != Grounds.Mushroom:
        return 0
    t = measure()
    z = get_pos_z()
    for i in neighbors:
        direction = DIRECTIONS[i]
        if get_ground_type(direction) == Grounds.Mushroom:
            target = get_pos_z(direction)
            if floor < target and target < z and measure(direction) == t:
                if not push(direction):
                    return None
                return 1
    return 0


# 从邻格推向当前格并返回，移动或推送失败交给主机停止本轮。
def push_neighbor(i):
    if not move(DIRECTIONS[i]):
        return False
    pushed = push(BACKS[i])
    if not move(BACKS[i]):
        return False
    return pushed


# 直接匹配会使目标下降一格；双邻配对保持目标高度，但不能提前同型消除。
def feed_column(neighbors, floor, cache, x, y):
    matched = 0
    while True:
        z = get_pos_z()
        if z < floor:
            return matched
        mushroom = get_ground_type() == Grounds.Mushroom
        t = -1
        if mushroom:
            t = measure()
        types = [-1, -1, -1, -1]
        heights = [0, 0, 0, 0]
        hit = -1
        for i in neighbors:
            direction = DIRECTIONS[i]
            heights[i] = get_pos_z(direction)
            if get_ground_type(direction) == Grounds.Mushroom:
                types[i] = measure(direction)
                if mushroom and z > floor and types[i] == t and heights[i] > z:
                    hit = i
                    break
        if hit >= 0:
            if not push_neighbor(hit):
                return None
            matched += 1
            continue
        # 非蘑菇柱只有确认两块同色且都高于floor至少两格后才准备。
        target = z
        pair_a = -1
        pair_b = -1
        for i in neighbors:
            if types[i] < 0 or types[i] == t or heights[i] < target + 2:
                continue
            for j in neighbors:
                if j > i and types[j] == types[i] and heights[j] >= target + 2:
                    pair_a = i
                    pair_b = j
                    break
            if pair_a >= 0:
                break
        if pair_a < 0:
            cache[(x, y)] = (z, t)
            for i in neighbors:
                dx, dy = OFFSETS[i]
                cache[(x + dx, y + dy)] = (heights[i], types[i])
            cache["ready"] = True
            return matched
        if not push_neighbor(pair_a):
            return None
        if not push_neighbor(pair_b):
            return None
        matched += 1


# 利用边界环绕走较短路径，坐标只读一次。
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
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


# 缓存只保存本分区已公开的柱顶；每次修改后更新涉及的柱。
def read_column(cache, x, y, direction=None):
    if direction == None:
        z = get_pos_z()
        ground = get_ground_type()
        t = -1
        if ground == Grounds.Mushroom:
            t = measure()
    else:
        z = get_pos_z(direction)
        ground = get_ground_type(direction)
        t = -1
        if ground == Grounds.Mushroom:
            t = measure(direction)
    cache[(x, y)] = (z, t)


# 直接匹配优先；两步搬运只经过已公开的同高低台，不建立搜索队列。
def carry_match(cache, x, y, neighbors, floor):
    direct = push_match(neighbors, floor)
    if direct != 0:
        return direct
    read_column(cache, x, y)
    z, t = cache[(x, y)]
    if t < 0 or z - 1 <= floor:
        return 0
    for i in neighbors:
        dx, dy = OFFSETS[i]
        read_column(cache, x + dx, y + dy, DIRECTIONS[i])
    for i in neighbors:
        dx, dy = OFFSETS[i]
        mx = x + dx
        my = y + dy
        height = cache[(mx, my)][0]
        if height >= z:
            continue
        for j in range(4):
            ex, ey = OFFSETS[j]
            end = (mx + ex, my + ey)
            if end not in cache:
                continue
            target, color = cache[end]
            if target > height or target <= floor or color != t:
                continue
            if not push(DIRECTIONS[i]):
                return None
            read_column(cache, x, y)
            if not move(DIRECTIONS[i]) or not push(DIRECTIONS[j]):
                return None
            read_column(cache, mx, my)
            read_column(cache, end[0], end[1], DIRECTIONS[j])
            if not move(BACKS[i]):
                return None
            return 1
    return fixture_match(neighbors, floor)


# 当前柱B与邻柱A同高同色时，把B暂存到低两格的C，再让A经B合并到C。
# C最终回到原高度，A/B各降低一格，不挖掉这两块蘑菇。
def fixture_match(neighbors, floor):
    if get_ground_type() != Grounds.Mushroom:
        return 0
    z = get_pos_z()
    if z - 2 < floor:
        return 0
    t = measure()
    for i in neighbors:
        source = DIRECTIONS[i]
        if get_pos_z(source) != z or get_ground_type(source) != Grounds.Mushroom or measure(source) != t:
            continue
        for j in neighbors:
            if i == j or get_pos_z(DIRECTIONS[j]) > z - 2:
                continue
            if not push(DIRECTIONS[j]):
                return None
            if not move(source) or not push(BACKS[i]):
                return None
            if not move(BACKS[i]) or not push(DIRECTIONS[j]):
                return None
            return 1
    return 0


OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


if __name__ == "__main__":
    lb_mushrooms_single()
