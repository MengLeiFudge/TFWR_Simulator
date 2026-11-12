from __builtins__ import *
# 淘汰候选归档：lb_cactus_single | 原实验路径 .codex/leaderboard-astra/iteration-20261026/cactus-young-insertion/lb_cactus_single.py
# 私有候选：逐株西南插入有序区域；完整轮时间待验证。

def lb_cactus_single():
    set_world_size(8)
    board = []
    for y in range(8):
        board.append([None, None, None, None, None, None, None, None])
    swaps = 0
    for y in range(8):
        for x in range(8):
            goto(x, y)
            if get_ground_type() == Grounds.Grassland:
                till()
            if not plant(Entities.Cactus):
                quick_print("insertion_failed", "plant", x, y)
                return
            value = measure()
            board[y][x] = value
            cx, cy = x, y
            while True:
                px, py = cx, cy
                largest = value
                if cx > 0 and board[cy][cx - 1] > largest:
                    px, py = cx - 1, cy
                    largest = board[py][px]
                if cy > 0 and board[cy - 1][cx] > largest:
                    px, py = cx, cy - 1
                    largest = board[py][px]
                if px == cx and py == cy:
                    break
                direction = West
                if py < cy:
                    direction = South
                if not swap(direction):
                    quick_print("insertion_failed", "swap", cx, cy)
                    return
                board[cy][cx] = largest
                board[py][px] = value
                swaps += 1
                if not move(direction):
                    quick_print("insertion_failed", "move", cx, cy)
                    return
                cx, cy = px, py
        quick_print("insertion_row", y, swaps, get_time())
    for y in range(8):
        for x in range(8):
            if x > 0 and board[y][x - 1] > board[y][x]:
                quick_print("insertion_failed", "row", x, y)
                return
            if y > 0 and board[y - 1][x] > board[y][x]:
                quick_print("insertion_failed", "column", x, y)
                return
    goto(0, 0)
    while not can_harvest() and get_time() < 40:
        pass
    harvest()
    quick_print("insertion_done", get_time(), num_items(Items.Cactus), swaps)


def goto(tx, ty):
    dx = (tx - get_pos_x()) % 8
    if dx <= 4:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(8 - dx):
            move(West)
    dy = (ty - get_pos_y()) % 8
    if dy <= 4:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(8 - dy):
            move(South)


if __name__ == "__main__":
    lb_cactus_single()
