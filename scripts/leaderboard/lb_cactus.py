from __builtins__ import *
# 完整轮时间：0:34.634（2026-11-03，build26385848，官方完整208轮，request249）。

def lb_cactus():
    while num_items(Items.Cactus) < 33554432:
        dispatch_lines(0, max_drone_num, False)
        dispatch_lines(0, max_drone_num, True)
        goto(0, size - 1)
        harvest()


def dispatch_lines(first, count, columns):
    # 每个分发者也处理一条线；最多31次spawn，子树结束后才返回。
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch_lines, first + left, count - left, columns)
        if handle == None:
            # 容量意外不足时按同一分区顺序执行，不丢弃任务。
            dispatch_lines(first + left, count - left, columns)
        else:
            handles.append(handle)
        count = left
    index = size - 1 - first
    if columns:
        goto(index, 0)
        sort_one_way()
    else:
        goto(0, index)
        plant_and_sort_x()
    for handle in handles:
        wait_for(handle)


size = get_world_size()
max_drone_num = min(max_drones(), size)


def goto(tx, ty):
    size = get_world_size()
    half_size = size // 2
    x, y = get_pos_x(), get_pos_y()
    # x方向
    dx = (tx - x) % size
    if dx <= half_size:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    # y方向
    dy = (ty - y) % size
    if dy <= half_size:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def plant_and_sort_x():
    # plant each row
    for _ in range(size):  # x
        entity = get_entity_type()
        if entity == None or entity == Entities.Grass:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
        # 利用本行铺田的既有访问先消除左邻逆序。
        if get_pos_x() > 0 and measure(West) > measure():
            swap(West)
        move(East)
    # sort x
    sort_one_way("x")


def sort_one_way(dir="y"):
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
        # move forward
        swap_pos_last = -1
        move_to(bound_low)
        i = bound_low
        while i < bound_high - 1:
            move(forward)
            i += 1
            # sort window 3
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
        if swap_pos_last == -1:  # no update
            break
        bound_high = swap_pos_last - 2
        if bound_low >= bound_high:
            break

        # move backward
        swap_pos_first = size
        move_to(bound_high)
        i = bound_high
        while i > bound_low + 1:
            move(backward)
            i -= 1
            # sort window 3
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
        if swap_pos_first == size:  # no update
            break
        bound_low = swap_pos_first + 2
        if bound_low >= bound_high:
            break

    if bound_low + 1 == bound_high:
        move_to(bound_low)
        # sort window 2
        a = measure()
        b = measure(forward)
        if a > b:
            swap(forward)


if __name__ == "__main__":
    lb_cactus()
