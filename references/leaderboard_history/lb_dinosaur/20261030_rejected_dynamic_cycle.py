from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/leaderboard-sol/open-directions/dinosaur-dynamic-cycle/lb_dinosaur.py
# D2：仅反转身体以外的Hamilton前缀，保留一条完整安全环。

def lb_dinosaur():
    clear()
    change_hat(Hats.Dinosaur_Hat)
    successor = []
    for x in range(32):
        for y in range(32):
            if not y:
                if x:
                    successor.append((x - 1) * 32)
                else:
                    successor.append(1)
            elif not x % 2:
                if y < 31:
                    successor.append(x * 32 + y + 1)
                else:
                    successor.append((x + 1) * 32 + y)
            elif y > 1:
                successor.append(x * 32 + y - 1)
            elif x < 31:
                successor.append((x + 1) * 32 + y)
            else:
                successor.append(x * 32)
    body = []
    occupied = {}
    apples = 0
    rewires = 0
    started = get_time()
    while get_time() - started < 120 and apples < 64:
        p = get_pos_x() * 32 + get_pos_y()
        eating = get_entity_type() == Entities.Apple
        if eating:
            target = measure()
            goal = target[0] * 32 + target[1]
            if reverse_free_prefix(p, goal, successor, occupied):
                rewires += 1
        q = successor[p]
        direction = North
        if q == p - 1:
            direction = South
        elif q == p + 32:
            direction = East
        elif q == p - 32:
            direction = West
        if not move(direction):
            quick_print("dynamic_cycle_blocked", apples, p, q, get_time())
            break
        if not eating and body:
            tail = body.pop(0)
            occupied.pop(tail)
        body.append(p)
        occupied[p] = True
        if eating:
            apples += 1
    change_hat(Hats.Brown_Hat)
    quick_print("dynamic_cycle_done", apples, rewires, get_time(), num_items(Items.Bone))


def reverse_free_prefix(p, goal, successor, occupied):
    x, y = p // 32, p % 32
    neighbors = []
    if x:
        neighbors.append(p - 32)
    if x < 31:
        neighbors.append(p + 32)
    if y:
        neighbors.append(p - 1)
    if y < 31:
        neighbors.append(p + 1)
    b = successor[p]
    best = None
    saving = 0
    for c in neighbors:
        if c == b or c in occupied:
            continue
        d = successor[c]
        if abs(b // 32 - d // 32) + abs(b % 32 - d % 32) != 1:
            continue
        segment = []
        q = b
        target_step = -1
        for _ in range(1024):
            if q == p or q in occupied:
                break
            segment.append(q)
            if q == goal:
                target_step = len(segment)
            if q == c:
                break
            q = successor[q]
        if q != c or target_step == -1:
            continue
        saved = target_step - (len(segment) - target_step + 1)
        if saved > saving:
            saving = saved
            best = segment
    if best == None:
        return False
    c = best[-1]
    d = successor[c]
    successor[p] = c
    for i in range(len(best) - 1, 0, -1):
        successor[best[i]] = best[i - 1]
    successor[best[0]] = d
    return True


if __name__ == "__main__":
    lb_dinosaur()
