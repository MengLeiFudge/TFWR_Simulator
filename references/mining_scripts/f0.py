from __builtins__ import *

# 游戏将硬度达到此值的方块视为不可破坏，直接 dig() 会等待极长时间。
UNBREAKABLE_HARDNESS = 10000000


def f0():
    # 开局即分派多机巡视全图；之后每轮完成同一层，再一起降低目标 z。
    size = get_world_size()
    count = min(max_drones(), size * size)
    regions = divide_regions(size, count)
    jobs = []
    for region in regions:
        jobs.append((region, size))
    layer = get_pos_z()
    for ok, top in run_jobs(survey_region, jobs):
        if not ok:
            return
        layer = max(layer, top)
    quick_print("煤矿已分为", len(regions), "个区域，从 z =", layer, "开始。")

    while True:
        jobs = []
        for region in regions:
            jobs.append((region, size, layer))
        before = num_items(Items.Coal)
        results = run_jobs(mine_region, jobs)
        for ok in results:
            if not ok:
                return
        quick_print("本层完成，z =", layer,
                    "，新增煤炭 =", num_items(Items.Coal) - before)
        layer -= 1


def divide_regions(size, count):
    # 反复平分最大矩形，保证各区非空、不相交，并覆盖所有列。
    regions = [(0, size, 0, size)]
    while len(regions) < count:
        largest = 0
        area = 0
        for i in range(len(regions)):
            x0, x1, y0, y1 = regions[i]
            current = (x1 - x0) * (y1 - y0)
            if current > area:
                largest = i
                area = current
        x0, x1, y0, y1 = regions.pop(largest)
        if x1 - x0 >= y1 - y0:
            middle = (x0 + x1) // 2
            regions.append((x0, middle, y0, y1))
            regions.append((middle, x1, y0, y1))
        else:
            middle = (y0 + y1) // 2
            regions.append((x0, x1, y0, middle))
            regions.append((x0, x1, middle, y1))
    return regions


def region_cells(region):
    # 蛇形巡视本区全部列，找矿位置不固定在某一根竖井。
    x0, x1, y0, y1 = region
    cells = []
    for y in range(y0, y1):
        xs = range(x0, x1)
        if (y - y0) % 2:
            xs = range(x1 - 1, x0 - 1, -1)
        for x in xs:
            cells.append((x, y))
    return cells


def survey_region(job):
    # 读取各列现有高度，从全图最高露出层开始，兼容已有深坑。
    region, size = job
    if not go_to(region[0], region[2], size):
        return False, 0
    top = get_pos_z()
    for x, y in region_cells(region):
        if not go_to(x, y, size):
            return False, 0
        top = max(top, get_pos_z())
    return True, top


def run_jobs(task, jobs):
    # 参数是各机独立副本。主机也干活，并在返回前回收所有已启动任务。
    handles = []
    fallback = []
    for i in range(1, len(jobs)):
        handle = spawn_drone(task, jobs[i])
        if handle == None:
            fallback.append(jobs[i])
        else:
            handles.append(handle)
    results = [task(jobs[0])]
    for job in fallback:
        results.append(task(job))
    for handle in handles:
        results.append(wait_for(handle))
    return results


def mine_region(job):
    # 只挖本区的列；跨边界的煤由邻区巡视发现，避免两机争挖同一列。
    region, size, layer = job
    seen = set()
    for x, y in region_cells(region):
        if not go_to(x, y, size):
            return False
        while get_pos_z() >= layer:
            if get_ground_type() == Grounds.Coal:
                if not mine_coal(region, size, seen):
                    return False
                # 追煤会走到分支末端，返回正在巡视的列再判断高度。
                if not go_to(x, y, size):
                    return False
            elif not dig_block():
                return False
    return True


def mine_coal(region, size, seen):
    # 待查项保存煤块所在的 z；挖掉后当前位置会再下降一格。
    x0, x1, y0, y1 = region
    start = (get_pos_x(), get_pos_y(), get_pos_z())
    pending = [start]
    seen.add(start)

    while pending:
        x, y, layer = pending.pop()
        if not go_to(x, y, size):
            return False

        # 相邻列可能仍有覆盖层。已挖过这一层的列无需继续下挖。
        while get_pos_z() >= layer:
            z = get_pos_z()
            coal = get_ground_type() == Grounds.Coal
            if z == layer and not coal:
                break
            if not dig_block():
                return False
            if not coal:
                continue

            # 覆盖层中遇到的煤也扩展分支，避免只挖走它而漏掉旁边的煤。
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx = x + dx
                    ny = y + dy
                    # 每台机只扩展本区；邻区的同层煤由邻区完整巡视覆盖。
                    if nx < x0 or nx >= x1 or ny < y0 or ny >= y1:
                        continue
                    neighbor = (nx, ny, z)
                    if neighbor not in seen:
                        seen.add(neighbor)
                        pending.append(neighbor)

    return True


def go_to(x, y, size):
    # 沿两个坐标轴走较短的环绕路线；移动失败时保留现场并结束。
    steps = (x - get_pos_x()) % size
    direction = East
    if steps > size // 2:
        steps = size - steps
        direction = West
    for _ in range(steps):
        if not move(direction):
            quick_print("无法移动到", x, y, "，请检查帽子或地形后重新运行 f0。")
            return False

    steps = (y - get_pos_y()) % size
    direction = North
    if steps > size // 2:
        steps = size - steps
        direction = South
    for _ in range(steps):
        if not move(direction):
            quick_print("无法移动到", x, y, "，请检查帽子或地形后重新运行 f0。")
            return False
    return True


def dig_block():
    # 先排除无法破坏的方块，再确认挖掘确实使地面下降。
    if get_hardness() >= UNBREAKABLE_HARDNESS:
        quick_print("遇到不可破坏的方块，已停止。位置：",
                    get_pos_x(), get_pos_y(), get_pos_z())
        return False
    z = get_pos_z()
    if not dig() or get_pos_z() >= z:
        quick_print("挖掘没有使地面下降，已停止。位置：",
                    get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


if __name__ == "__main__":
    f0()
