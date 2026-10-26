from __builtins__ import *
# 完整轮时间：5:37.970（2026-10-26，官方完整22轮，request 109）。

def lb_wood_single():
    set_world_size(8)
    if not bootstrap():
        return
    clear()
    queues = []
    targets = []
    requested = []
    active = []
    remaining = []
    support = []
    for _ in range(64):
        queues.append([])
        targets.append(-1)
        requested.append(None)
        active.append(False)
        remaining.append(0)
        support.append(None)
    produced = 0
    rejected = 0
    batches = 0
    changes = 0
    waiting = 0
    unripe = 0
    for tour in range(1000):
        before = produced
        for y in range(8):
            direction = East
            columns = range(8)
            if y % 2 == 1:
                direction = West
                columns = range(7, -1, -1)
            for x in columns:
                if get_time() > 1200:
                    quick_print("cohort_failed", "time_limit", get_time())
                    return
                source = x + 8 * y
                if tour == 0:
                    deadline = get_time() + 15
                    while not can_harvest():
                        if get_time() > deadline:
                            quick_print("cohort_failed", "initial_grass_deadline", source)
                            return
                    if not harvest():
                        quick_print("cohort_failed", "initial_grass", source)
                        return
                    if (x + y) % 2 == 1:
                        till()
                if (x + y) % 2 == 0:
                    if tour > 0:
                        water_once()
                    if active[source]:
                        if can_harvest():
                            target = targets[source]
                            if support[target] != requested[source] or remaining[target] <= 0:
                                quick_print("cohort_failed", "claim", source, target)
                                return
                            if not harvest():
                                quick_print("cohort_failed", "harvest", source)
                                return
                            remaining[target] -= 1
                            active[source] = False
                            targets[source] = -1
                            produced += 1
                            if num_items(Items.Wood) >= 500000000:
                                quick_print("cohort_done", get_time(), tour, produced, rejected, batches, changes, waiting, unripe)
                                return
                        else:
                            unripe += 1
                    elif targets[source] != -1:
                        waiting += 1
                    if targets[source] == -1:
                        rolls = register_tree(source, queues, targets, requested)
                        if rolls < 0:
                            return
                        rejected += rolls
                        if tour == 0:
                            water_once()
                elif tour > 0 and remaining[source] == 0 and len(queues[source]) > 0:
                    kind = queues[source][0][1]
                    if support[source] != kind:
                        cost = get_cost(kind)
                        for item in cost:
                            if num_items(item) < cost[item]:
                                quick_print("cohort_failed", "support_material", source, kind, item, get_time())
                                return
                        if support[source] != None:
                            if not harvest():
                                quick_print("cohort_failed", "support_harvest", source)
                                return
                            changes += 1
                        if not plant(kind):
                            quick_print("cohort_failed", "support_plant", source)
                            return
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
                    batches += 1
                if x != 7 and direction == East or x != 0 and direction == West:
                    move(direction)
            move(North)
        quick_print("cohort_tour", tour, get_time(), produced - before, produced, rejected, batches, changes, waiting, unripe)
    quick_print("cohort_failed", "tour_limit", get_time())


def register_tree(source, queues, targets, requested):
    for attempt in range(128):
        if not plant(Entities.Tree):
            quick_print("cohort_failed", "tree_plant", source, get_time())
            return -1
        companion = get_companion()
        if companion == None:
            quick_print("cohort_failed", "companion", source)
            return -1
        kind, position = companion
        x, y = position
        if (x + y) % 2 == 1:
            target = x + 8 * y
            targets[source] = target
            requested[source] = kind
            queues[target].append((source, kind))
            return attempt
        if can_harvest() or not harvest():
            quick_print("cohort_failed", "mature_rejection", source)
            return -1
    quick_print("cohort_failed", "reroll_limit", source)
    return -1


def bootstrap():
    clear()
    accepted = False
    for attempt in range(128):
        if not plant(Entities.Tree):
            return False
        companion = get_companion()
        if companion != None and companion[0] == Entities.Grass:
            accepted = True
            break
        if can_harvest() or not harvest():
            return False
    if not accepted:
        quick_print("cohort_failed", "bootstrap_reroll")
        return False
    deadline = get_time() + 15
    while not can_harvest():
        if get_time() > deadline:
            quick_print("cohort_failed", "bootstrap_deadline")
            return False
        water_once()
    before = num_items(Items.Wood)
    if not harvest() or num_items(Items.Wood) - before != 409600:
        quick_print("cohort_failed", "bootstrap_yield")
        return False
    quick_print("cohort_bootstrap", get_time(), num_items(Items.Wood))
    return True


def water_once():
    if get_water() < 0.9:
        water = num_items(Items.Water)
        if water > 0:
            use_item(Items.Water, min(4, water))


if __name__ == "__main__":
    lb_wood_single()
