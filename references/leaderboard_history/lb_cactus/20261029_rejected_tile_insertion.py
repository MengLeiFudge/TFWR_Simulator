from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-tile-insertion/lb_cactus.py
# 私有32块二维插入加全局行列合并代表；完整时间未取得。

def lb_cactus():
    set_world_size(32)
    clear()
    dispatch_tiles(0, 32)
    quick_print("tile_ready", get_time())
    dispatch_lines(0, 32, False)
    quick_print("rows_ready", get_time())
    dispatch_lines(0, 32, True)
    quick_print("columns_ready", get_time())
    goto(0, 31)
    harvest()
    return num_items(Items.Cactus) >= 33554432


def dispatch_tiles(first, count):
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch_tiles, first + left, count - left)
        if handle == None:
            dispatch_tiles(first + left, count - left)
        else:
            handles.append(handle)
        count = left
    tile(first % 8 * 4, first // 8 * 8)
    for handle in handles:
        wait_for(handle)


def tile(bx, by):
    board = []
    for _ in range(32):
        board.append(-1)
    # 每条反对角线开始前，其所有西/南前驱已种植并保持二维偏序。
    for diagonal in range(11):
        for x in range(4):
            y = diagonal - x
            if y < 0 or y >= 8:
                continue
            goto(bx + x, by + y)
            till()
            plant(Entities.Cactus)
            value = measure()
            px, py = x, y
            current = px * 8 + py
            board[current] = value
            while True:
                west = -1
                south = -1
                if px:
                    west = board[current - 8]
                if py:
                    south = board[current - 1]
                if west > value and west >= south:
                    board[current] = west
                    current -= 8
                    board[current] = value
                    swap(West)
                    move(West)
                    px -= 1
                elif south > value:
                    board[current] = south
                    current -= 1
                    board[current] = value
                    swap(South)
                    move(South)
                    py -= 1
                else:
                    break


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
        sort_one_way("x")
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
