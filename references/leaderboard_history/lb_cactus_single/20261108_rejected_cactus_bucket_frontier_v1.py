from __builtins__ import *
# 淘汰候选归档：lb_cactus_single | 原实验路径 .codex/nonreset-100-20261108/cactus-bucket-frontier-v1/lb_cactus_single.py


def lb_cactus_single():
    global board
    global buckets
    global px
    global py
    set_world_size(8)
    clear()
    board = [-1] * 64
    buckets = []
    for value in range(10):
        buckets.append(set())
    px = get_pos_x()
    py = get_pos_y()
    for y in range(8):
        for offset in range(8):
            x = offset
            if y % 2:
                x = 7 - offset
            go(x, y)
            till()
            if not plant(Entities.Cactus):
                quick_print("cactus_failed", "plant")
                return
            cell = x + y * 8
            value = measure()
            board[cell] = value
            buckets[value].add(cell)
    planted = get_time()
    fixed = set()
    frontier = {0}
    swaps = 0
    for value in range(10):
        while len(buckets[value]) > 0:
            best = 100000
            source = -1
            target = -1
            for cell in buckets[value]:
                sx = cell % 8
                sy = cell // 8
                travel = WRAP[sx - px] + WRAP[sy - py]
                for goal in frontier:
                    distance = ABS[sx - goal % 8] + ABS[sy - goal // 8]
                    cost = travel + distance * 2
                    if cost < best:
                        best = cost
                        source = cell
                        target = goal
            buckets[value].remove(source)
            go(source % 8, source // 8)
            tx = target % 8
            ty = target // 8
            # 未固定区域是东北上闭集：先升到两端较高行，再横移、再向南到前沿。
            for step in range(max(0, ty - py)):
                carry(North, value)
                swaps += 1
            direction = East
            dx = tx - px
            if dx < 0:
                dx = -dx
                direction = West
            for step in range(dx):
                carry(direction, value)
                swaps += 1
            for step in range(max(0, py - ty)):
                carry(South, value)
                swaps += 1
            if px != tx or py != ty or board[target] != value:
                quick_print("cactus_failed", "route", source, target, px, py)
                return
            fixed.add(target)
            frontier.remove(target)
            if tx < 7 and (ty == 0 or target - 7 in fixed):
                frontier.add(target + 1)
            if ty < 7 and (tx == 0 or target + 7 in fixed):
                frontier.add(target + 8)
    while get_time() - planted < 1:
        pass
    harvest()
    quick_print("cactus_done", num_items(Items.Cactus), get_time(), "swaps", swaps)


# 把手里的最小值送过一格；其余值的公开位置同步更新到桶。
def carry(direction, value):
    global px
    global py
    source = px + py * 8
    tx = px
    ty = py
    if direction == North:
        ty += 1
    elif direction == South:
        ty -= 1
    elif direction == East:
        tx += 1
    else:
        tx -= 1
    target = tx + ty * 8
    displaced = board[target]
    buckets[displaced].remove(target)
    buckets[displaced].add(source)
    board[source] = displaced
    board[target] = value
    if not swap(direction) or not move(direction):
        quick_print("cactus_failed", "carry", source, target)
        return False
    px = tx
    py = ty
    return True


# 空走可使用农场环绕；交换路线自身始终在0至7之间。
def go(tx, ty):
    global px
    global py
    dx = (tx - px) % 8
    direction = East
    if dx > 4:
        dx = 8 - dx
        direction = West
    for step in range(dx):
        move(direction)
    dy = (ty - py) % 8
    direction = North
    if dy > 4:
        dy = 8 - dy
        direction = South
    for step in range(dy):
        move(direction)
    px = tx
    py = ty


ABS = [0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1]
WRAP = [0, 1, 2, 3, 4, 3, 2, 1]

if __name__ == "__main__":
    lb_cactus_single()
