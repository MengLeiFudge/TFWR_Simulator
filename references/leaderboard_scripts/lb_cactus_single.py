from __builtins__ import *

# 0:21.199
def lb_cactus_single():
    set_world_size(8)
    goal = 131072
    while num_items(Items.Cactus) < goal:
        plant_and_sort_rows()
        sort_columns()
        goto(0, 0)
        harvest()
    quick_print("lb_cactus_single done cactus=", num_items(Items.Cactus), " time=", get_time())


def goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def plant_and_sort_rows():
    size = get_world_size()
    for y in range(size):
        goto(0, y)
        for x in range(size):
            if get_ground_type() == Grounds.Grassland:
                till()
            if get_entity_type() != Entities.Cactus:
                plant(Entities.Cactus)
            local_sort_after_plant(x, y)
            move(East)
        sort_one_way("x")


def local_sort_after_plant(x, y):
    size = get_world_size()
    current = measure()
    if current == None:
        return
    if x > 0:
        neighbor = measure(West)
        if neighbor != None and neighbor > current:
            swap(West)
            current = neighbor
    if y > 0:
        neighbor = measure(South)
        if neighbor != None and neighbor > current:
            swap(South)


def sort_columns():
    size = get_world_size()
    for x in range(size):
        goto(x, 0)
        sort_one_way("y")


def sort_one_way(dir="y"):
    size = get_world_size()
    if dir == "x":
        forward = East
        backward = West

        def move_to(tx):
            x = get_pos_x()
            dx = (tx - x) % size
            if dx <= size // 2:
                for _ in range(dx):
                    move(East)
            else:
                for _ in range(size - dx):
                    move(West)

    else:
        forward = North
        backward = South

        def move_to(ty):
            y = get_pos_y()
            dy = (ty - y) % size
            if dy <= size // 2:
                for _ in range(dy):
                    move(North)
            else:
                for _ in range(size - dy):
                    move(South)

    bound_low = 0
    bound_high = size - 1
    while True:
        swap_pos_last = -1
        move_to(bound_low)
        i = bound_low
        while i < bound_high - 1:
            move(forward)
            i = i + 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if a > b:
                swap(backward)
                swap_pos_last = max(swap_pos_last, i)
                a, b = b, a
            if b > c:
                swap(forward)
                swap_pos_last = max(swap_pos_last, i + 1)
                b, c = c, b
                if a > b:
                    swap(backward)
        if swap_pos_last == -1:
            break
        bound_high = swap_pos_last - 2
        if bound_low >= bound_high:
            break

        swap_pos_first = size
        move_to(bound_high)
        i = bound_high
        while i > bound_low + 1:
            move(backward)
            i = i - 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if b > c:
                swap(forward)
                swap_pos_first = min(swap_pos_first, i)
                b, c = c, b
            if a > b:
                swap(backward)
                swap_pos_first = min(swap_pos_first, i - 1)
                a, b = b, a
                if b > c:
                    swap(forward)
        if swap_pos_first == size:
            break
        bound_low = swap_pos_first + 2
        if bound_low >= bound_high:
            break

    if bound_low + 1 == bound_high:
        move_to(bound_low)
        a = measure()
        b = measure(forward)
        if a > b:
            swap(forward)


if __name__ == "__main__":
    lb_cactus_single()
