from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2，8x8 随机种植后行列排序统一 harvest；main1 保留作对照。


def main1():
    set_world_size(8)
    goal = 131072
    while num_items(Items.Cactus) < goal:
        goto(0, 0)
        plant_row_wave()
        goto(0, 0)
        harvest()
    quick_print("main1 done cactus=", num_items(Items.Cactus), " time=", get_time())


def main2():
    set_world_size(8)
    goal = 131072
    while num_items(Items.Cactus) < goal:
        plant_and_sort_rows()
        sort_columns()
        goto(0, 0)
        harvest()
    quick_print("main2 done cactus=", num_items(Items.Cactus), " time=", get_time())


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


# 蛇形扫图种 cactus，每格 reroll 到 variant=9；扫完全图后统一 harvest 一次。
def plant_row_wave():
    size = get_world_size()
    for y in range(size):
        if y % 2 == 0:
            end_x = size - 1
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if get_ground_type() == Grounds.Grassland:
                till()
            plant(Entities.Cactus)
            while measure() != 9:
                harvest()
                plant(Entities.Cactus)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        if y < size - 1:
            move(North)


def plant_and_sort_rows():
    size = get_world_size()
    for y in range(size):
        goto(0, y)
        for _ in range(size):
            if get_ground_type() == Grounds.Grassland:
                till()
            if get_entity_type() != Entities.Cactus:
                plant(Entities.Cactus)
            move(East)
        sort_one_way("x")


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
    main2()
