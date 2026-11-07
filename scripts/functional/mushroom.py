from __builtins__ import *
import farm_support

# 配对主体来自Save0/Mushroom.py；普通地形按层推进，不依赖Jump或爆破钻。
DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


def mushroom():
    # 持续采集，上一批所有子机结束后才重生下一片。
    farm_support.run(Items.Mushroom, collect)


def collect(goal):
    # 每层主机采样柱最后推进，保持各分区共同的两格高度带。
    if not farm_support.require(Unlocks.Mushrooms) or not farm_support.require(Unlocks.Mining):
        return False
    if not farm_support.require(Unlocks.Underground_Senses):
        return False
    width, size = farm_support.dimensions()
    if width * size < 2:
        quick_print("蘑菇配对需要至少两个地块。")
        return False
    empty = 0
    while num_items(Items.Mushroom) < goal:
        clear()
        before = num_items(Items.Mushroom)
        for _ in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if get_hardness() >= 10000000 or not dig():
                break
        if get_ground_type() != Grounds.Mushroom:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有可达蘑菇层，停止。")
                return False
            continue
        ceiling = get_pos_z()
        if not dig_layer(ceiling) or not move_to(0, 0):
            return False
        blocks = make_blocks()
        while get_ground_type() == Grounds.Mushroom and num_items(Items.Mushroom) < goal:
            result = run_layer(blocks, ceiling)
            if result == None:
                quick_print("蘑菇配对失败，已回收子机。")
                return False
            if not move_to(0, 0) or get_pos_z() != ceiling or not dig():
                return False
            ceiling -= 1
        if num_items(Items.Mushroom) > before:
            empty = 0
        else:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有蘑菇配对收益，停止。")
                return False
    return True


def make_blocks():
    # 矩形分区不小于4格；小地图使用一个分区，兼容1×3农场。
    width, size = farm_support.dimensions()
    gx = max(1, width // 4)
    gy = max(1, size // 4)
    while gx * gy > farm_support.capacity():
        if gx >= gy and gx > 1:
            gx -= 1
        else:
            gy -= 1
    blocks = []
    for k in range(gx * gy):
        bx = k % gx
        by = k // gx
        blocks.append((bx * width // gx, (bx + 1) * width // gx,
                       by * size // gy, (by + 1) * size // gy))
    return blocks


def move_to(tx, ty):
    # 统一使用真实地图宽高的导航。
    return farm_support.move_to(tx, ty)


def dig_layer(target):
    width, size = farm_support.dimensions()
    workers = min(width, farm_support.capacity())
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
    width, size = farm_support.dimensions()
    for x in range(first_x, width, stride):
        if not move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() != target:
                return False
            if not move(North):
                return False
    return True

def run_layer(blocks, ceiling):
    handles = []
    results = []
    for k in range(1, len(blocks)):
        handle = None
        if farm_support.capacity() > 1:
            handle = spawn_drone(work_layer, blocks[k], ceiling)
        if handle == None:
            results.append(work_layer(blocks[k], ceiling))
        else:
            handles.append(handle)
    results.append(work_layer(blocks[0], ceiling))
    for handle in handles:
        results.append(wait_for(handle))
    pairs = 0
    digs = 0
    for result in results:
        if result == None:
            return None
        pairs += result[0]
        digs += result[1]
    return pairs, digs

def work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    floor = ceiling - 2
    pairs = 0
    digs = 0
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
            if z < floor or z > ceiling:
                return None
            if z == ceiling:
                count = push_match(neighbors, floor)
                if count == None:
                    return None
                pairs += count
                if count == 0:
                    if get_hardness() >= 10000000 or not dig():
                        return None
                    if get_pos_z() != z - 1:
                        return None
                    digs += 1
            count = feed_column(neighbors, floor)
            if count == None:
                return None
            pairs += count
    return pairs, digs

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

def push_neighbor(i):
    if not move(DIRECTIONS[i]):
        return False
    pushed = push(BACKS[i])
    if not move(BACKS[i]):
        return False
    return pushed

def feed_column(neighbors, floor):
    matched = 0
    while True:
        z = get_pos_z()
        if z < floor:
            return None
        if get_ground_type() != Grounds.Mushroom:
            return matched
        t = measure()
        types = [-1, -1, -1, -1]
        heights = [0, 0, 0, 0]
        hit = -1
        for i in neighbors:
            direction = DIRECTIONS[i]
            if get_ground_type(direction) == Grounds.Mushroom:
                types[i] = measure(direction)
                heights[i] = get_pos_z(direction)
                if z > floor and types[i] == t and heights[i] > z:
                    hit = i
                    break
        if hit >= 0:
            if not push_neighbor(hit):
                return None
            matched += 1
            continue
        pair_a = -1
        pair_b = -1
        for i in neighbors:
            if types[i] < 0 or types[i] == t or heights[i] < z + 2:
                continue
            for j in neighbors:
                if j > i and types[j] == types[i] and heights[j] >= z + 2:
                    pair_a = i
                    pair_b = j
                    break
            if pair_a >= 0:
                break
        if pair_a < 0:
            return matched
        if not push_neighbor(pair_a):
            return None
        if not push_neighbor(pair_b):
            return None
        matched += 1


if __name__ == "__main__":
    mushroom()
