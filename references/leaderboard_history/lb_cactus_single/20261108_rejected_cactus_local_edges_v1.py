from __builtins__ import *
# 淘汰候选归档：lb_cactus_single | 原实验路径 .codex/nonreset-100-20261108/cactus-local-edges-v1/lb_cactus_single.py


def lb_cactus_single():
    global px
    global py
    set_world_size(8)
    clear()
    px = get_pos_x()
    py = get_pos_y()
    board = [-1] * 64
    for y in range(8):
        for offset in range(8):
            x = offset
            if y % 2:
                x = 7 - offset
            if not go(x, y):
                return
            till()
            if not plant(Entities.Cactus):
                return
            board[x + y * 8] = measure()
    planted = get_time()
    incident = []
    endpoints = []
    flags = []
    counts = [0] * 64
    bad = set()
    for cell in range(64):
        incident.append([])
    for cell in range(64):
        if cell % 8 < 7:
            edge = len(endpoints)
            endpoints.append((cell, cell + 1, East, West))
            flags.append(board[cell] > board[cell + 1])
            incident[cell].append(edge)
            incident[cell + 1].append(edge)
        if cell // 8 < 7:
            edge = len(endpoints)
            endpoints.append((cell, cell + 8, North, South))
            flags.append(board[cell] > board[cell + 8])
            incident[cell].append(edge)
            incident[cell + 8].append(edge)
    for edge in range(len(flags)):
        if flags[edge]:
            a, b, forward, reverse = endpoints[edge]
            counts[a] += 1
            counts[b] += 1
            bad.add(a)
            bad.add(b)
    swaps = 0
    for step in range(10000):
        if len(bad) == 0:
            break
        cursor = px + py * 8
        if cursor not in bad:
            best = 100
            target = -1
            for cell in bad:
                distance = WRAP[cell % 8 - px] + WRAP[cell // 8 - py]
                if distance < best:
                    best = distance
                    target = cell
                if best == 1:
                    break
            if not go(target % 8, target // 8):
                return
            cursor = target
        selected = -1
        difference = 0
        for edge in incident[cursor]:
            if not flags[edge]:
                continue
            a, b, forward, reverse = endpoints[edge]
            value = board[a] - board[b]
            if value > difference:
                difference = value
                selected = edge
        if selected < 0:
            quick_print("cactus_failed", "stale", cursor)
            return
        a, b, direction, reverse = endpoints[selected]
        if cursor == b:
            direction = reverse
        if not swap(direction):
            quick_print("cactus_failed", "swap", a, b)
            return
        board[a], board[b] = board[b], board[a]
        swaps += 1
        # 只有被交换端点的关联边可能改变；其余逆序信息保持有效。
        for cell in [a, b]:
            for edge in incident[cell]:
                if cell == b and edge == selected:
                    continue
                u, v, forward, reverse = endpoints[edge]
                updated = board[u] > board[v]
                if updated == flags[edge]:
                    continue
                flags[edge] = updated
                change = -1
                if updated:
                    change = 1
                for point in [u, v]:
                    counts[point] += change
                    if counts[point] == 0:
                        bad.remove(point)
                    elif counts[point] == 1 and updated:
                        bad.add(point)
    if len(bad) > 0:
        quick_print("cactus_failed", "limit", len(bad))
        return
    while get_time() - planted < 1:
        pass
    harvest()
    quick_print("cactus_done", num_items(Items.Cactus), get_time(), "swaps", swaps)


# 空走使用农场环绕，交换边本身由实际坐标建立。
def go(tx, ty):
    global px
    global py
    dx = (tx - px) % 8
    direction = East
    if dx > 4:
        dx = 8 - dx
        direction = West
    for step in range(dx):
        if not move(direction):
            return False
    dy = (ty - py) % 8
    direction = North
    if dy > 4:
        dy = 8 - dy
        direction = South
    for step in range(dy):
        if not move(direction):
            return False
    px = tx
    py = ty
    return True


WRAP = [0, 1, 2, 3, 4, 3, 2, 1]

if __name__ == "__main__":
    lb_cactus_single()
