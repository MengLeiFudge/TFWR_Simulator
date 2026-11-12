from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-sol/open-directions/cactus-global-insertion/lb_cactus.py
# C3：真实采盘、解释器内全局Young插入规划、按位置依赖分层执行。

def lb_cactus():
    set_world_size(32)
    clear()
    started = get_time()
    rows = seed_rows(0, 32)
    board = []
    for _ in range(1024):
        board.append(0)
    for y, values in rows:
        for x in range(32):
            board[x * 32 + y] = values[x]
    touched = []
    for _ in range(1024):
        touched.append(-1)
    layers = []
    swaps = 0
    for diagonal in range(63):
        for x in range(32):
            y = diagonal - x
            if y < 0 or y >= 32:
                continue
            cell = x * 32 + y
            value = board[cell]
            px, py = x, y
            while True:
                west = -1
                south = -1
                if px:
                    west = board[cell - 32]
                if py:
                    south = board[cell - 1]
                other = -1
                direction = West
                if west > value and west >= south:
                    other = cell - 32
                    px -= 1
                elif south > value:
                    other = cell - 1
                    direction = South
                    py -= 1
                else:
                    break
                level = max(touched[cell], touched[other]) + 1
                while len(layers) <= level:
                    layers.append([])
                layers[level].append((cell, direction))
                touched[cell] = level
                touched[other] = level
                board[cell] = board[other]
                board[other] = value
                cell = other
                swaps += 1
    quick_print("insertion_planned", swaps, len(layers), get_time() - started)
    for layer in range(len(layers)):
        tasks = layers[layer]
        if tasks:
            width = min(32, len(tasks))
            apply_layer(0, width, width, tasks)
        if layer % 8 == 0:
            quick_print("insertion_layer", layer, get_time())
        if get_time() - started > 120:
            quick_print("insertion_gate", layer, get_time(), False)
            return False
    goto(0, 31)
    harvest()
    quick_print("insertion_done", get_time(), num_items(Items.Cactus))
    return num_items(Items.Cactus) >= 33554432


def seed_rows(first, count):
    handles = []
    rows = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(seed_rows, first + left, count - left)
        if handle == None:
            rows += seed_rows(first + left, count - left)




        else:
            handles.append(handle)
        count = left
    goto(0, first)
    values = []
    for _ in range(32):
        till()
        plant(Entities.Cactus)
        values.append(measure())
        move(East)
    rows.append((first, values))

    for handle in handles:
        other = wait_for(handle)
        for row in other:
            rows.append(row)
    return rows


def apply_layer(first, count, width, tasks):
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(apply_layer, first + left, count - left, width, tasks)
        if handle == None:
            apply_layer(first + left, count - left, width, tasks)
        else:
            handles.append(handle)
        count = left
    for index in range(first, len(tasks), width):
        cell, direction = tasks[index]
        goto(cell // 32, cell % 32)
        swap(direction)
    for handle in handles:
        wait_for(handle)


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
    lb_cactus()
