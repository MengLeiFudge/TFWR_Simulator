from __builtins__ import *
# 历史提交归档：lb_bamboo_single | 初次提交 2026-11-06 (6c5c5e64) | 优化：竹子空中心四邻布局通过单双机完整复验
# 完整轮时间：956.579秒（构建26462009，8轮官方完整统计；请求364）。

def lb_bamboo_single():
    clear()
    size = get_world_size()
    if size < 4:
        quick_print("bamboo_failed", "world_size", size)
        return
    centers = set()
    for y in range(size):
        for x in range(size):
            if (x + 2 * y) % 5 == 0:
                centers.add((x, y))
    covered = set(centers)
    for x, y in centers:
        for dx, dy in STEPS:
            covered.add(((x + dx) % size, (y + dy) % size))
    # 环边不能直接套无限格点；未被覆盖的格子也保留为空中心。
    for y in range(size):
        for x in range(size):
            if (x, y) not in covered:
                centers.add((x, y))
    fans = {}
    for center in centers:
        fans[center] = []
    plants = 0
    for y in range(size):
        for x in range(size):
            if (x, y) in centers:
                continue
            for i in range(4):
                dx, dy = STEPS[i]
                center = ((x + dx) % size, (y + dy) % size)
                if center in centers:
                    fans[center].append((i + 2) % 4)
                    plants += 1
                    break
    gx = 1
    gy = 1
    while gx * gy * 2 <= max_drones():
        if gx <= gy and gx * 2 <= size:
            gx *= 2
        elif gy * 2 <= size:
            gy *= 2
        else:
            break
    plans = []
    for owner in range(gx * gy):
        x0 = (owner % gx) * size // gx
        x1 = (owner % gx + 1) * size // gx
        y0 = (owner // gx) * size // gy
        y1 = (owner // gx + 1) * size // gy
        plan = []
        for y in range(y0, y1):
            for offset in range(x1 - x0):
                x = x0 + offset
                if (y - y0) % 2 != 0:
                    x = x1 - 1 - offset
                if (x, y) in fans and len(fans[(x, y)]) > 0:
                    plan.append((x, y, fans[(x, y)]))
        plans.append(plan)
    quick_print("bamboo_star_plan", plants, len(centers), len(plans), get_time())
    deadline = get_time() + 3600
    handles = []
    results = []
    for owner in range(1, len(plans)):
        handle = spawn_drone(bamboo_fans, plans[owner], 25000000, deadline)
        if handle == None:
            results.append(bamboo_fans(plans[owner], 25000000, deadline))
        else:
            handles.append(handle)
    results.append(bamboo_fans(plans[0], 25000000, deadline))
    for handle in handles:
        results.append(wait_for(handle))
    ok = True
    for result in results:
        if not result:
            ok = False
    quick_print("bamboo_done", ok, get_time(), num_items(Items.Bamboo))


def bamboo_fans(plan, goal, deadline):
    size = get_world_size()
    phases = []
    for x, y, directions in plan:
        local = []
        for _ in directions:
            local.append(0)
        phases.append(local)
    hover(18)
    laps = 0
    while num_items(Items.Bamboo) < goal:
        if get_time() > deadline:
            quick_print("bamboo_failed", "deadline", get_time())
            return False
        for k in range(len(plan)):
            x, y, directions = plan[k]
            if not bamboo_move_to(x, y, size):
                return False
            for i in range(len(directions)):
                if num_items(Items.Bamboo) >= goal:
                    return True
                d = directions[i]
                direction = DIRECTIONS[d]
                back = DIRECTIONS[(d + 2) % 4]
                if not move(direction):
                    return False
                if get_entity_type() != Entities.Bamboo:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if not plant(Entities.Bamboo):
                        return False
                    phases[k][i] = 0
                    hover(18)
                elif can_harvest():
                    if phases[k][i] < 2:
                        height = measure()
                        if not move(back):
                            return False
                        hover(height)
                        if not move(direction):
                            return False
                        if measure() <= height:
                            quick_print("bamboo_failed", "flower_not_cut", x, y, d)
                            return False
                        phases[k][i] += 1
                        hover(18)
                    else:
                        if not harvest() or not plant(Entities.Bamboo):
                            return False
                        phases[k][i] = 0
                        hover(18)
                if not move(back):
                    return False
        laps += 1
        if len(plan) > 0 and plan[0][0] == 0 and laps % 16 == 0:
            quick_print("bamboo_star_lap", laps, get_time(), num_items(Items.Bamboo))
    return True


def bamboo_move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


STEPS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRECTIONS = [North, East, South, West]

if __name__ == "__main__":
    lb_bamboo_single()
