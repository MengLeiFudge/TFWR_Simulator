from __builtins__ import *
# 完整轮时间：5:17.898（2026-10-26，官方完整23轮，request 106）。

def lb_carrots_single():
    set_world_size(8)
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
        support.append(Entities.Grass)
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
                                quick_print("cohort_failed", "claim", source, target)
                                return
                            if not harvest():
                                quick_print("cohort_failed", "harvest", source)
                                return
                            remaining[target] -= 1
                            active[source] = False
                            targets[source] = -1
                            produced += 1
                            if num_items(Items.Carrot) >= 100000000:
                                quick_print("cohort_done", get_time(), tour, produced, rejected, batches, changes, waiting, unripe)
                                return
                        else:
                            unripe += 1
                    elif targets[source] != -1:
                        waiting += 1
                    if targets[source] == -1:
                        rolls = register_carrot(source, queues, targets, requested)
                        if rolls < 0:
                            return
                        rejected += rolls
                        if tour == 0:
                            water_once()
                elif tour > 0 and remaining[source] == 0 and len(queues[source]) > 0:
                    kind = queues[source][0][1]
                    if support[source] != kind:
                        if support[source] != Entities.Grass:
                            if not harvest():
                                quick_print("cohort_failed", "support_harvest", source)
                                return
                            changes += 1
                        if kind != Entities.Grass:
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


def register_carrot(source, queues, targets, requested):
    for attempt in range(128):
        if not plant(Entities.Carrot):
            quick_print("cohort_failed", "carrot_plant", source, get_time())
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


def water_once():
    if get_water() < 0.9:
        water = num_items(Items.Water)
        if water > 0:
            use_item(Items.Water, min(4, water))


if __name__ == "__main__":
    lb_carrots_single()
