from __builtins__ import *
import production


# 启动时跳到蘑菇附近；每片结束后回到地表重新寻找，持续采集。
# 分区工人连续处理整片，各自保留两格高度带；(0,0)只用于公开测厚。
OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


def mushroom(target=-1):
    if not production.active(Items.Mushroom, target):
        return
    if num_unlocked(Unlocks.Mushrooms) < 1 or num_unlocked(Unlocks.Jump) < 1:
        quick_print("请先解锁蘑菇和 Jump，再运行蘑菇采集。")
        return
    production.jump_once(Unlocks.Mushrooms)
    blocks = make_blocks()
    batches = 0
    while production.active(Items.Mushroom, target):
        start = get_time()
        before = num_items(Items.Mushroom)
        change_hat(Hats.Mining_Hat)
        # 普通地形首个蘑菇区块从深度32开始；爆破仅用于地表至深度16的探孔。
        # 主机独占钻头，接近蘑菇层和派出子机前都换回采矿帽。
        drill = (get_pos_z() > -16 and num_unlocked(Unlocks.Explosive_Drill) > 0
                 and num_items(Items.Dynamite) > 0)
        if drill:
            change_hat(Hats.Explosive_Drill)
        top = get_pos_z()
        while get_ground_type() != Grounds.Mushroom:
            if drill and (get_pos_z() <= -16 or num_items(Items.Dynamite) < 1):
                change_hat(Hats.Mining_Hat)
                drill = False
            if top - get_pos_z() >= 48 or get_hardness() >= 10000000 or not dig():
                break
        if drill:
            change_hat(Hats.Mining_Hat)
        if get_ground_type() != Grounds.Mushroom:
            quick_print("本田未找到可达蘑菇层，换田：z", get_pos_z())
            clear()
            continue
        ceiling = get_pos_z()
        height = 0
        for _ in range(7):
            if get_ground_type() != Grounds.Mushroom:
                break
            if not dig():
                return
            height += 1
        if height == 0 or height > 6:
            quick_print("mushroom_failed", "height", height)
            return
        if not dig_layer(ceiling):
            quick_print("覆盖层挖掘或移动失败，已等待子机结束，停止：z", ceiling)
            return
        quick_print("mushroom_prepare", ceiling, height, get_time() - start)
        # 沿用榜单的末层取舍：保留两格工作窗口，避免低产底层及跨区高度差扩大。
        result = run_patch(blocks, ceiling, max(1, height - 1), target)
        if result == None:
            # 已回收整片全部工人；保留正常配对的收益，再换田恢复。
            quick_print("mushroom_restart", ceiling, get_time(), num_items(Items.Mushroom) - before)
            clear()
            continue
        batches += 1
        quick_print("mushroom_patch", batches, height, result[0], result[1],
                    num_items(Items.Mushroom) - before, get_time() - start, get_time())
        clear()


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


# 探孔定位后逐列挖到共同高度；塌方已清除的覆盖物不再重复挖掘。
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


# 各区只派发一次，完成整片后统一回收；内部不再为每层重新派工。
def run_patch(blocks, ceiling, levels, target):
    handles = []
    results = []
    for k in range(1, len(blocks)):
        handle = spawn_drone(work_patch, blocks[k], ceiling, levels, target)
        if handle == None:
            results.append(work_patch(blocks[k], ceiling, levels, target))
        else:
            handles.append(handle)
    results.append(work_patch(blocks[0], ceiling, levels, target))
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


def work_patch(block, ceiling, levels, target):
    # 只读真实柱顶和颜色；库存目标在每层完成后检查，确保退出时已正常入库。
    pairs = 0
    digs = 0
    for layer in range(levels):
        if not production.active(Items.Mushroom, target):
            break
        result = work_layer(block, ceiling - layer)
        if result == None:
            return None
        pairs += result[0]
        digs += result[1]
        if result[2] == 0:
            break
    return pairs, digs


# 各区在本地高度带内利用公开低台搬运，保留同高配对和双邻喂料。
def work_layer(block, ceiling):
    x0, x1, y0, y1 = block
    cache = {}
    floor = ceiling - 2
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
                    if get_pos_z() != z - 1:
                        return None
                    digs += 1
            count = feed_column(neighbors, floor)
            if count == None:
                return None
            pairs += count
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
def feed_column(neighbors, floor):
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
            if get_ground_type(direction) == Grounds.Mushroom:
                types[i] = measure(direction)
                heights[i] = get_pos_z(direction)
                if mushroom and z > floor and types[i] == t and heights[i] > z:
                    hit = i
                    break
        if hit >= 0:
            if not push_neighbor(hit):
                return None
            matched += 1
            continue
        target = z
        if not mushroom:
            target = floor
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
            return matched
        if not mushroom:
            while get_pos_z() > floor:
                if get_ground_type() == Grounds.Mushroom:
                    return matched
                if get_hardness() >= 10000000 or not dig():
                    return None
            if get_pos_z() != floor:
                return None
            if get_ground_type() == Grounds.Mushroom:
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


# 缓存仅保存本分区公开柱顶，搬运后更新全部受影响的柱。
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
        if height != z - 1 and height != z - 2:
            continue
        for j in range(4):
            ex, ey = OFFSETS[j]
            end = (mx + ex, my + ey)
            if end not in cache:
                continue
            target, color = cache[end]
            if target != z - 1 or color != t:
                continue
            if height == z - 2:
                if num_items(Items.Block) < 1:
                    continue
                if not move(DIRECTIONS[i]) or get_pos_z() != height:
                    return None
                if not place(Grounds.Dirt) or get_pos_z() != z - 1:
                    return None
                if not move(BACKS[i]):
                    return None
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


# 相邻同高同色A/B借低两格的C完成B→C、A→B、B→C。
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
            if i == j or get_pos_z(DIRECTIONS[j]) != z - 2:
                continue
            if not push(DIRECTIONS[j]):
                return None
            if not move(source) or not push(BACKS[i]):
                return None
            if not move(BACKS[i]) or not push(DIRECTIONS[j]):
                return None
            return 1
    return 0


if __name__ == "__main__":
    mushroom()
