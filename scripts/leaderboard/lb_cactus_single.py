from __builtins__ import *
# 完整轮时间：未取得（47+44株稀疏连通田；本地完整目标已验证）。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt（move_to）。

def lb_cactus_single():
    global s
    global board
    set_world_size(8)
    clear()
    s = get_world_size()
    # 两张田均连通，西南偏序最长链为5；第二张只用第一张已翻好的土壤。
    layouts = [
        [
            (0, 0), (1, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
            (0, 1), (2, 1), (3, 1), (5, 1), (6, 1),
            (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (7, 2),
            (0, 3), (1, 3), (3, 3), (4, 3), (6, 3), (7, 3),
            (0, 4), (2, 4), (3, 4), (5, 4), (6, 4), (7, 4),
            (1, 5), (2, 5), (4, 5), (5, 5), (7, 5),
            (0, 6), (1, 6), (3, 6), (4, 6), (6, 6), (7, 6),
            (0, 7), (1, 7), (2, 7), (3, 7), (5, 7), (6, 7),
        ],
        [
            (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
            (0, 1), (2, 1), (3, 1), (5, 1), (6, 1),
            (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (7, 2),
            (0, 3), (1, 3), (3, 3), (4, 3), (6, 3), (7, 3),
            (0, 4), (2, 4), (3, 4), (5, 4), (6, 4), (7, 4),
            (1, 5), (2, 5), (4, 5), (5, 5), (7, 5),
            (0, 6), (1, 6), (3, 6), (4, 6), (6, 6), (7, 6),
            (0, 7), (1, 7), (2, 7), (3, 7), (6, 7),
        ],
    ]
    for batch in range(2):
        board = {}
        last_plant_time = get_time()
        for x, y in layouts[batch]:
            move_to(x, y)
            if batch == 0:
                till()
            plant(Entities.Cactus)
            last_plant_time = get_time()
            insert_value(x, y)
        while get_time() - last_plant_time < 1:
            continue
        harvest()
        quick_print("cactus_batch", batch, get_time(), num_items(Items.Cactus))


# 只向已种植的较大前驱插入；末次交换后无须跟随时留在原格。
def insert_value(x, y):
    value = measure()
    while True:
        west = (x - 1, y)
        south = (x, y - 1)
        previous = None
        previous_value = -1
        direction = West
        if west in board and board[west] > value:
            previous = west
            previous_value = board[west]
        if south in board and board[south] > value and board[south] > previous_value:
            previous = south
            previous_value = board[south]
            direction = South
        if previous == None:
            board[(x, y)] = value
            return
        board[(x, y)] = previous_value
        board[previous] = value
        swap(direction)
        px, py = previous
        more = False
        if (px - 1, py) in board and board[(px - 1, py)] > value:
            more = True
        if (px, py - 1) in board and board[(px, py - 1)] > value:
            more = True
        if not more:
            return
        move(direction)
        x, y = previous


def move_to(tx, ty):
    cx, cy = get_pos_x(), get_pos_y()

    dx_east = (tx - cx) % s
    dx_west = s - dx_east
    if dx_east < dx_west:
        for _ in range(dx_east):
            move(East)
    else:
        for _ in range(dx_west):
            move(West)

    dy_north = (ty - cy) % s
    dy_south = s - dy_north
    if dy_north < dy_south:
        for _ in range(dy_north):
            move(North)
    else:
        for _ in range(dy_south):
            move(South)


if __name__ == "__main__":
    lb_cactus_single()
