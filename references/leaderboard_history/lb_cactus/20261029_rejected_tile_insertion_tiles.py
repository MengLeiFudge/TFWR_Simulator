# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-tile-insertion/tiles.py
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
