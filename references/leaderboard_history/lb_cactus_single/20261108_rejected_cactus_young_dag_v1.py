from __builtins__ import *
# 淘汰候选归档：lb_cactus_single | 原实验路径 .codex/nonreset-100-20261108/cactus-young-dag-v1/lb_cactus_single.py


def lb_cactus_single():
    global px
    global py
    set_world_size(8)
    clear()
    px = get_pos_x()
    py = get_pos_y()
    initial = [-1] * 64
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
            initial[x + y * 8] = measure()
    planted = get_time()
    ordered = [-1] * 64
    last = [-1] * 64
    operations = []
    children = []
    remaining = []
    ready = []
    # 每个位置只依赖上次改写它的交换，未固定格子始终保持同一串行等价顺序。
    for diagonal in range(15):
        for x in range(max(0, diagonal - 7), min(7, diagonal) + 1):
            y = diagonal - x
            cell = x + y * 8
            ordered[cell] = initial[cell]
            cursor = cell
            value = initial[cell]
            for step in range(16):
                cx = cursor % 8
                cy = cursor // 8
                other = -1
                predecessor = value
                direction = None
                if cx > 0 and ordered[cursor - 1] > predecessor:
                    predecessor = ordered[cursor - 1]
                    other = cursor - 1
                    direction = West
                if cy > 0 and ordered[cursor - 8] > predecessor:
                    predecessor = ordered[cursor - 8]
                    other = cursor - 8
                    direction = South
                if other < 0:
                    break
                node = len(operations)
                operations.append((cursor, other, direction, value, predecessor))
                children.append([])
                degree = 0
                a = last[cursor]
                b = last[other]
                if a >= 0:
                    children[a].append(node)
                    degree += 1
                if b >= 0 and b != a:
                    children[b].append(node)
                    degree += 1
                remaining.append(degree)
                if degree == 0:
                    ready.append(node)
                last[cursor] = node
                last[other] = node
                ordered[cursor] = predecessor
                ordered[other] = value
                cursor = other
    planned = get_time()
    executed = 0
    while len(ready) > 0:
        best = 100
        choice = -1
        endpoint = -1
        reverse = False
        for index in range(len(ready)):
            node = ready[index]
            a, b, direction, va, vb = operations[node]
            distance = WRAP[a % 8 - px] + WRAP[a // 8 - py]
            if distance < best:
                best = distance
                choice = index
                endpoint = a
                reverse = False
            distance = WRAP[b % 8 - px] + WRAP[b // 8 - py]
            if distance < best:
                best = distance
                choice = index
                endpoint = b
                reverse = True
            if best == 0:
                break
        node = ready.pop(choice)
        a, b, direction, va, vb = operations[node]
        if reverse:
            direction = BACK[direction]
            va, vb = vb, va
        if not go(endpoint % 8, endpoint // 8):
            return
        if measure() != va or measure(direction) != vb or not swap(direction):
            quick_print("cactus_failed", "dependency", node)
            return
        executed += 1
        for child in children[node]:
            remaining[child] -= 1
            if remaining[child] == 0:
                ready.append(child)
    if executed != len(operations):
        quick_print("cactus_failed", "incomplete", executed, len(operations))
        return
    while get_time() - planted < 1:
        pass
    harvest()
    quick_print("cactus_done", num_items(Items.Cactus), get_time(), "swaps", executed,
                "plan", planned - planted)


# 空走使用真实8格环绕，交换由调度记录提供不越界的相邻端点。
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
BACK = {West: East, East: West, South: North, North: South}

if __name__ == "__main__":
    lb_cactus_single()
