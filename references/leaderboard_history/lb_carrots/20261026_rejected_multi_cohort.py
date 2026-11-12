from __builtins__ import *
# 淘汰候选归档：lb_carrots | 原实验路径 .codex/leaderboard-astra/carrots-multi-cohort/lb_carrots.py
# 私有候选：32个独占4×8区域的冻结支撑批次。

def lb_carrots():
    set_world_size(32)
    clear()
    if max_drones() < 32:
        quick_print("multi_cohort_failed", "drones")
        return
    handles = []
    passed = True
    for worker in range(31):
        handle = spawn_drone(cohort_worker, worker % 8 * 4, worker // 8 * 8)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    rows = []
    if passed:
        result = cohort_worker(28, 24)
        if result == None:
            passed = False
        else:
            rows.append(result)
    for handle in handles:
        result = wait_for(handle)
        if result == None:
            passed = False
        else:
            rows.append(result)
    quick_print("multi_cohort_done", passed, get_time(), num_items(Items.Carrot), rows)


def cohort_worker(base_x, base_y):
    goto(base_x, base_y)
    route = [(0, 0, East), (1, 0, East), (2, 0, East), (3, 0, North)]
    for y in range(1, 8):
        if y % 2 == 1:
            for x in range(3, 0, -1):
                direction = West
                if x == 1 and y != 7:
                    direction = North
                route.append((x, y, direction))
        else:
            for x in range(1, 4):
                direction = East
                if x == 3:
                    direction = North
                route.append((x, y, direction))
    for y in range(7, 0, -1):
        route.append((0, y, South))
    queues = []
    targets = []
    requested = []
    active = []
    remaining = []
    support = []
    for _ in range(32):
        queues.append([])
        targets.append(-1)
        requested.append(None)
        active.append(False)
        remaining.append(0)
        support.append(Entities.Grass)
    produced = 0
    rejected = 0
    waiting = 0
    changes = 0
    unripe = 0
    for tour in range(1000):
        for x, y, direction in route:
            if num_items(Items.Carrot) >= 2000000000:
                return (produced, rejected, tour, waiting, changes, unripe)
            if get_time() > 1200:
                quick_print("multi_cohort_failed", "time", base_x, base_y)
                return None
            source = x + 4 * y
            if (x + y) % 2 == 0:
                if tour == 0:
                    if get_ground_type() != Grounds.Soil:
                        till()
                else:
                    water_once()
                if active[source]:
                    if can_harvest():
                        target = targets[source]
                        if support[target] != requested[source] or remaining[target] <= 0:
                            quick_print("multi_cohort_failed", "claim", base_x, base_y, source)
                            return None
                        if not harvest():
                            return None
                        remaining[target] -= 1
                        active[source] = False
                        targets[source] = -1
                        produced += 1
                        if num_items(Items.Carrot) >= 2000000000:
                            return (produced, rejected, tour, waiting, changes, unripe)
                    else:
                        unripe += 1
                elif targets[source] != -1:
                    waiting += 1
                if targets[source] == -1:
                    rolls = register_carrot(source, base_x, base_y, queues, targets, requested)
                    if rolls < 0:
                        return None
                    rejected += rolls
                    if tour == 0:
                        water_once()
            elif tour > 0 and remaining[source] == 0 and len(queues[source]) > 0:
                kind = queues[source][0][1]
                if support[source] != kind:
                    if support[source] != Entities.Grass:
                        if not harvest():
                            return None
                        changes += 1
                    if kind != Entities.Grass:
                        if not plant(kind):
                            return None
                        changes += 1
                    support[source] = kind
                deferred = []
                for origin, wanted in queues[source]:
                    if wanted == kind:
                        active[origin] = True
                        remaining[source] += 1
                    else:
                        deferred.append((origin, wanted))
                queues[source] = deferred
            if not move(direction):
                return None
        if base_x == 0 and base_y == 0 and tour % 10 == 0:
            quick_print("multi_cohort_progress", tour, get_time(), num_items(Items.Carrot), produced, rejected, waiting)
    quick_print("multi_cohort_failed", "tour", base_x, base_y)
    return None


def register_carrot(source, base_x, base_y, queues, targets, requested):
    for attempt in range(128):
        if not plant(Entities.Carrot):
            return -1
        companion = get_companion()
        if companion == None:
            return -1
        kind, position = companion
        x = position[0] - base_x
        y = position[1] - base_y
        if x >= 0 and x < 4 and y >= 0 and y < 8 and (x + y) % 2 == 1:
            target = x + 4 * y
            targets[source] = target
            requested[source] = kind
            queues[target].append((source, kind))
            return attempt
        if can_harvest() or not harvest():
            return -1
    quick_print("multi_cohort_failed", "reroll", base_x, base_y, source)
    return -1


def water_once():
    if get_water() >= 0.9:
        return
    water = num_items(Items.Water)
    if water > 384:
        use_item(Items.Water, 3)
    elif water > 192:
        use_item(Items.Water, 2)
    elif water > 64:
        use_item(Items.Water)


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
    lb_carrots()
