from __builtins__ import *
import production


# 星形四邻布局；首次Jump保留天然珍珠岩，后续调度用地表布局，浇水后恢复高飞。
def bamboo():
    prepare = not production.JUMP_USED
    if prepare:
        production.jump_once(Unlocks.Special_Soils)
    else:
        clear()
    size = get_world_size()
    if prepare and not bamboo_prepare(size):
        quick_print("bamboo_failed", "prepare")
        return
    if size < 4:
        quick_print("竹子采集需要至少4×4的农场。")
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
    handles = []
    results = []
    for owner in range(1, len(plans)):
        handle = spawn_drone(bamboo_fans, plans[owner])
        if handle == None:
            results.append(bamboo_fans(plans[owner]))
        else:
            handles.append(handle)
    results.append(bamboo_fans(plans[0]))
    for handle in handles:
        results.append(wait_for(handle))
    ok = True
    for result in results:
        if not result:
            ok = False
    quick_print("bamboo_done", ok, get_time(), num_items(Items.Bamboo))


def bamboo_fans(plan):
    size = get_world_size()
    phases = []
    for x, y, directions in plan:
        local = []
        for _ in directions:
            local.append(0)
        phases.append(local)
    hover(18)
    laps = 0
    while production.active(Items.Bamboo):
        for k in range(len(plan)):
            x, y, directions = plan[k]
            if not bamboo_move_to(x, y, size):
                return False
            for i in range(len(directions)):
                d = directions[i]
                direction = DIRECTIONS[d]
                back = DIRECTIONS[(d + 2) % 4]
                if not move(direction):
                    return False
                if get_water() < 0.25 and num_items(Items.Water) > 0:
                    use_item(Items.Water)
                    hover(18)
                if get_entity_type() != Entities.Bamboo:
                    ground = get_ground_type()
                    if ground == Grounds.Grassland or ground == Grounds.Loam:
                        till()
                    elif ground != Grounds.Soil and ground != Grounds.Dirt and ground != Grounds.Perlite:
                        if not place(Grounds.Dirt):
                            quick_print("bamboo_failed", "soil_cover", x, y, d)
                            return False
                    if not plant(Entities.Bamboo):
                        quick_print("bamboo_failed", "plant", x, y, d, get_ground_type())
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


# 找层期间读到的珍珠岩可能随后塌落；生产前仍逐格重读并补可种泥土。
def bamboo_prepare(size):
    handles = []
    results = []
    workers = min(size, max_drones())
    limit_z = get_pos_z() - 32
    for owner in range(1, workers):
        handle = spawn_drone(bamboo_prepare_columns, owner, workers, size, limit_z)
        if handle == None:
            results.append(bamboo_prepare_columns(owner, workers, size, limit_z))
        else:
            handles.append(handle)
    results.append(bamboo_prepare_columns(0, workers, size, limit_z))
    for handle in handles:
        results.append(wait_for(handle))
    perlite = 0
    for count in results:
        if count == None:
            return False
        perlite += count
    quick_print("bamboo_prepare_seen_perlite", perlite, size * size, get_time())
    return True


def bamboo_prepare_columns(first, stride, size, limit_z):
    perlite = 0
    for x in range(first, size, stride):
        if not bamboo_move_to(x, 0, size):
            return None
        for y in range(size):
            for step in range(48):
                ground = get_ground_type()
                if ground == Grounds.Perlite or ground == Grounds.Loam:
                    break
                if get_pos_z() <= limit_z or get_hardness() >= 10000000:
                    break
                if not dig():
                    return None
            if get_ground_type() == Grounds.Perlite:
                perlite += 1
            elif get_ground_type() != Grounds.Loam and get_ground_type() != Grounds.Dirt and get_ground_type() != Grounds.Soil:
                if not place(Grounds.Dirt):
                    return None
            if not move(North):
                return None
    return perlite


if __name__ == "__main__":
    bamboo()
