from __builtins__ import *
# 历史提交归档：lb_mushrooms | 初次提交 2026-11-06 (22bf18ce) | 文档：补齐其余十个地下榜的正式实机基线
# 完整轮时间：572.673秒（构建26462009，13轮官方完整统计；请求348）。

def lb_mushrooms():
    began = get_time()
    for batch in range(128):
        if num_items(Items.Mushroom) >= 240000:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        # 只有上一批句柄全部回收后才重生，禁止clear取消仍在采集的子机。
        clear()
        covers = 0
        while get_ground_type() != Grounds.Mushroom:
            if covers >= 256 or get_time() - began > 7200 or not dig():
                quick_print("mushrooms_failed", "find_stratum", batch)
                return
            covers += 1
        top = get_pos_z()
        if not dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch, top)
            return
        quick_print("mushrooms_prepared", batch, covers, top, get_time())
        if not move_to(0, 0):
            return
        ceiling = get_pos_z()
        blocks = make_blocks()
        layers = 0
        while get_ground_type() == Grounds.Mushroom and num_items(Items.Mushroom) < 240000:
            result = run_layer(blocks, ceiling)
            if result == None:
                quick_print("mushrooms_failed", "layer", batch, layers, ceiling)
                return
            if not move_to(0, 0) or get_pos_z() != ceiling or not dig():
                quick_print("mushrooms_failed", "sample", batch, layers)
                return
            pairs, digs = result
            ceiling -= 1
            layers += 1
            quick_print("mushrooms_layer", batch, layers, pairs, digs + 1, get_time(), num_items(Items.Mushroom))
        quick_print("mushrooms_batch", batch, layers, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


# 每台无人机负责一列；无人机不足时按列步长分担，整层完成后才返回。
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


# 覆盖层起始高度一致，只需逐格挖到本次目标高度，无需识别地面类型。
def dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
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


# 各分区共用本层高度上限；先收回全部子机，再推进采样点和下一层。
def run_layer(blocks, ceiling):
    handles = []
    results = []
    for k in range(1, len(blocks)):
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


# 单遍蛇形处理：最高处先尝试直接推送，无法配对才挖，再接收邻格配对。
# 蘑菇稳定性为3；两格高度带也把内部地块承受的落差限制在一格。
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


DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


if __name__ == "__main__":
    lb_mushrooms()
