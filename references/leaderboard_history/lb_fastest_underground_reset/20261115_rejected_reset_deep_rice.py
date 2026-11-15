from __builtins__ import *


def reset_rice_stock(goal):
    clear()
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    handles = []
    passed = True
    for first in range(1, workers):
        handle = spawn_drone(reset_rice_worker, first, workers, size, goal, deadline)
        if handle == None:
            passed = False
            break
        handles.append(handle)
    if passed and not reset_rice_worker(0, workers, size, goal, deadline):
        passed = False
    for handle in handles:
        if not wait_for(handle):
            passed = False
    quick_print("rice_deep", passed, get_time(), num_items(Items.Rice))
    return passed and num_items(Items.Rice) >= goal


def reset_rice_worker(first, stride, size, goal, deadline):
    points = []
    for x in range(first, size, stride):
        for y in range(size):
            points.append((x, y))
    for band in range(128):
        for x, y in points:
            if num_items(Items.Rice) >= goal:
                return True
            reset_rice_move(x, y, size)
            for depth in range(128):
                if get_ground_type() == Grounds.Clay:
                    break
                if get_time() > deadline or not dig():
                    return False
            if not plant(Entities.Rice):
                return False
            reset_rice_water()
        for x, y in points:
            if num_items(Items.Rice) >= goal:
                return True
            reset_rice_move(x, y, size)
            if reset_rice_harvest(deadline):
                if num_items(Items.Rice) >= goal:
                    return True
                if get_ground_type() == Grounds.Dry_Rice_Terrace:
                    if not dig() or not plant(Entities.Rice):
                        return False
                    reset_rice_water()
        for x, y in points:
            if num_items(Items.Rice) >= goal:
                return True
            reset_rice_move(x, y, size)
            reset_rice_harvest(deadline)
        if get_time() > deadline:
            return False
    return False


def reset_rice_water():
    if get_water() < 0.25 and num_items(Items.Water) >= 1:
        use_item(Items.Water)


def reset_rice_harvest(deadline):
    while get_entity_type() == Entities.Rice and not can_harvest():
        if get_time() > deadline:
            return False
        do_a_flip()
    if get_entity_type() == Entities.Rice:
        return harvest()
    return False


def reset_rice_move(x, y, size):
    for target, current, positive, negative in [(x, get_pos_x(), East, West), (y, get_pos_y(), North, South)]:
        count = (target - current) % size
        direction = positive
        if count > size // 2:
            count = size - count
            direction = negative
        for _ in range(count):
            move(direction)
