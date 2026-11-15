from __builtins__ import *


def reset_bamboo_stock(goal):
    clear()
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    handles = []
    passed = True
    for owner in range(1, workers):
        handle = spawn_drone(reset_bamboo_worker, owner, workers, size, goal, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed and not reset_bamboo_worker(0, workers, size, goal, deadline):
        passed = False
    for handle in handles:
        if not wait_for(handle):
            passed = False
    quick_print("bamboo_closed", passed, get_time(), num_items(Items.Bamboo))
    return passed and num_items(Items.Bamboo) >= goal


def reset_bamboo_worker(owner, workers, size, goal, deadline):
    first = owner * size // workers
    height = (owner + 1) * size // workers - first
    points = []
    for x in range(size):
        points.append((x, first))
    if height > 1:
        for column in range(size - 1):
            x = size - 1 - column
            if column % 2 == 0:
                for y in range(1, height):
                    points.append((x, first + y))
            else:
                for y in range(height - 1, 0, -1):
                    points.append((x, first + y))
        for y in range(height - 1, 0, -1):
            points.append((0, first + y))
    directions = []
    for i in range(len(points)):
        x, y = points[i]
        nx, ny = points[(i + 1) % len(points)]
        direction = South
        if nx > x:
            direction = East
        elif nx < x:
            direction = West
            if height == 1:
                direction = East
        elif ny > y:
            direction = North
        directions.append(direction)
    for _ in range(min(first, size - first)):
        direction = North
        if first > size // 2:
            direction = South
        move(direction)
    route = directions[:-1]
    last = directions[-1]
    lowest = 1

    for direction in route:
        move(direction)
        if get_ground_type() != Grounds.Soil:
            till()
        if not reset_bamboo_seed(deadline):
            return False
        lowest = min(lowest, reset_bamboo_water(1, 1))

    move(last)
    began = get_time()
    growth = 4
    sweep = len(route) * 200 / (800 * 1.5 ** num_unlocked(Unlocks.Speed))
    for cycle in range(512):
        if num_items(Items.Bamboo) >= goal:
            return True
        if get_time() > deadline:
            return False
        reset_bamboo_wait(began, growth, lowest, sweep)
        hover(4)
        for direction in route:
            move(direction)
        move(last)
        began = get_time()
        reset_bamboo_wait(began, 4, lowest, sweep)
        hover(8)
        growth = 3
        for direction in route:
            move(direction)
            growth = max(growth, measure() - 8)
        growth = min(growth, 5)
        move(last)
        began = get_time()
        reset_bamboo_wait(began, growth, lowest, sweep)
        hover(1)
        new_lowest = 1
        growth = 3
        watering_started = get_time()
        for i in range(len(route)):
            move(route[i])
            if num_items(Items.Bamboo) >= goal:
                return True

            new_lowest = min(new_lowest, reset_bamboo_water(1, 0.5))
        move(last)
        began = get_time()
        lowest = new_lowest * 0.99 ** (began - watering_started)
    return False


def reset_bamboo_seed(deadline):
    for attempt in range(128):
        if get_time() > deadline or not plant(Entities.Bamboo):
            return False
        if measure() == 4:
            return True
        harvest()
    return False


def reset_bamboo_water(target, threshold):
    water = get_water()
    if water < threshold:
        amount = (target - water) * 4 // 1
        if amount < 1:
            amount = 1
        amount = min(amount, num_items(Items.Water) // 1)
        if amount > 0:
            use_item(Items.Water, amount)
            water = get_water()
    return water


def reset_bamboo_wait(began, growth, water, sweep):
    target = began + growth / (1 + 4 * water) + 0.05 - sweep
    while get_time() + 1 < target:
        do_a_flip()
    while get_time() < target:
        for _ in range(16):
            pass
