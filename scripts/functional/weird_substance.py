from __builtins__ import *


def weird_substance():
    # 并行伴生树苗圃，成熟后感染并收获怪异物质。
    while True:
        goal = num_items(Items.Weird_Substance) + 1000000
        if not parallel_nursery_stock(Items.Weird_Substance, goal, True):
            return

def affordable(cost):
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True


def go(x, y):
    size = get_world_size()
    dx = (x - get_pos_x()) % size
    dy = (y - get_pos_y()) % size
    if dx > size // 2:
        for _ in range(size - dx):
            move(West)
    else:
        for _ in range(dx):
            move(East)
    if dy > size // 2:
        for _ in range(size - dy):
            move(South)
    else:
        for _ in range(dy):
            move(North)


def nursery_support_strip(worker, workers, size, support, deadline):
    first = worker * size // workers
    last = (worker + 1) * size // workers
    for y in range(first, last):
        for x in range(size):
            if get_time() > deadline:
                return False
            if x % 2 != 0 or y % 2 != 0:
                go(x, y)
                if not plant(support):
                    return False
    return True


def nursery_produce_strip(worker, workers, size, crop, support, item, target, weird, deadline):
    anchors = []
    for y in range(0, size, 2):
        if (y // 2) % workers == worker:
            for x in range(0, size, 2):
                anchors.append((x, y))
    accepted = []
    for _ in anchors:
        accepted.append(False)
    if len(anchors) == 0:
        return (True, 0, 0, 0)
    produced = 0
    rejected = 0
    unready = 0
    for visit in range(20000):
        if num_items(item) >= target:
            return (True, produced, rejected, unready)
        if get_time() > deadline:
            return (False, produced, rejected, unready)
        index = visit % len(anchors)
        x, y = anchors[index]
        go(x, y)
        if accepted[index]:
            if can_harvest():
                if weird and not use_item(Items.Fertilizer):
                    return (False, produced, rejected, unready)
                if not harvest():
                    return (False, produced, rejected, unready)
                accepted[index] = False
                produced += 1
                if num_items(item) >= target:
                    return (True, produced, rejected, unready)
            else:
                unready += 1
                if get_water() < 0.5 and num_items(Items.Water) >= 2:
                    use_item(Items.Water, 2)
                continue
        if crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        matched = False
        for attempt in range(128):
            if get_time() > deadline or not affordable(get_cost(crop)) or not plant(crop):
                return (False, produced, rejected, unready)
            companion = get_companion()
            if companion == None:
                return (False, produced, rejected, unready)
            kind, position = companion
            px, py = position
            if kind == support and (px % 2 != 0 or py % 2 != 0):
                matched = True
                break
            harvest()
            rejected += 1
        if not matched:
            return (False, produced, rejected, unready)
        if get_water() < 0.5 and num_items(Items.Water) >= 2:
            use_item(Items.Water, 2)
        accepted[index] = True
    return (False, produced, rejected, unready)


def parallel_nursery_stock(item, target, weird=False):
    if num_items(item) >= target:
        return True
    beginning = get_time()
    initial = num_items(item)
    size = get_world_size()
    workers = min(max_drones(), size // 2)
    crop = Entities.Tree
    support = Entities.Grass
    deadline = get_time() + 700
    if weird:
        gain = 5 * 2 ** (num_unlocked(Unlocks.Trees) - 1) * (5 * 2 ** num_unlocked(Unlocks.Polyculture)) // 2
        required = (target - num_items(item) + gain - 1) // gain + workers
        while num_items(Items.Fertilizer) < required:
            if get_time() > deadline:
                quick_print('directed_failed', 'nursery_fertilizer_reserve', get_time(), required)
                return False
            do_a_flip()
    clear()
    if support == Entities.Bush:
        handles = []
        passed = True
        for worker in range(1, workers):
            handle = spawn_drone(nursery_support_strip, worker, workers, size, support, deadline)
            if handle == None:
                passed = False
                break
            handles.append(handle)
        if passed:
            passed = nursery_support_strip(0, workers, size, support, deadline)
        for handle in handles:
            if not wait_for(handle):
                passed = False
        if not passed:
            quick_print('directed_failed', 'nursery_support_workers', get_time())
            return False
    handles = []
    passed = True
    results = []
    for worker in range(1, workers):
        handle = spawn_drone(nursery_produce_strip, worker, workers, size, crop, support, item, target, weird, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed:
        results.append(nursery_produce_strip(0, workers, size, crop, support, item, target, weird, deadline))
    for handle in handles:
        results.append(wait_for(handle))
    produced = 0
    rejected = 0
    unready = 0
    for result in results:
        if result == None:
            passed = False
        else:
            if not result[0]:
                passed = False
            produced += result[1]
            rejected += result[2]
            unready += result[3]
    if not passed or num_items(item) < target:
        quick_print('directed_failed', 'nursery_production_workers', item, get_time(), num_items(item), target)
        return False
    quick_print('directed_parallel_nursery', item, beginning, get_time(), workers, produced, rejected, unready, num_items(item) - initial)
    return True

if __name__ == "__main__":
    weird_substance()
