from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/leaderboard-sol/dinosaur/contiguous-candidate/lb_dinosaur.py
def lb_dinosaur():
    size = 32
    total = size * size
    last = size - 1
    half = total // 2
    clear()
    if get_world_size() != size:
        return fail("expected 32x32 field")
    if num_unlocked(Unlocks.Dinosaurs) != 6:
        return fail("expected Dinosaurs level 6")
    if num_items(Items.Cactus) < 64 * total:
        return fail("insufficient Cactus reserve")
    if num_items(Items.Power) < 1000000000:
        return fail("insufficient initial Power")

    ranks = []
    for x in range(size):
        column = []
        for y in range(size):
            column.append(0)
        ranks.append(column)

    directions = []
    neighbors = []
    for _ in range(total):
        directions.append(None)
        neighbors.append([])

    for x in range(size):
        for y in range(size):
            if y == 0:
                rank = x
                direction = East
                if x == last:
                    direction = North
            elif x == 0:
                rank = total - y
                direction = South
            else:
                base = size + (last - x) * last
                if x % 2 == 1:
                    rank = base + y - 1
                    direction = North
                    if y == last:
                        direction = West
                else:
                    rank = base + last - y
                    direction = South
                    if y == 1:
                        direction = West
            ranks[x][y] = rank
            directions[rank] = direction

    for x in range(size):
        for y in range(size):
            rank = ranks[x][y]
            edges = neighbors[rank]
            if x < last:
                edges.append((ranks[x + 1][y], East))
            if y < last:
                edges.append((ranks[x][y + 1], North))
            if x > 0:
                edges.append((ranks[x - 1][y], West))
            if y > 0:
                edges.append((ranks[x][y - 1], South))
    directions2 = directions + directions

    change_hat(Hats.Dinosaur_Hat)
    head = 0
    length = 1
    pending = True
    target_rank = read_target_rank(ranks, size)
    if target_rank == None:
        return False

    while True:
        if length >= half:
            if not pending:
                if not run_segment(directions2, head, remaining):
                    return False
                head = (head + remaining) % total
            return finish_ring(directions2, head, length, True, total)

        remaining = (target_rank - head) % total
        post_length = length
        if pending:
            post_length = length + 1
        gap = total - length + 1
        if remaining <= 0 or remaining >= gap:
            return fail("target outside forward free arc")

        best = 1
        direction = None
        for edge in neighbors[head]:
            distance = (edge[0] - head) % total
            if distance > best and distance < gap and remaining - distance >= post_length:
                best = distance
                direction = edge[1]

        if best > 1:
            if not move(direction):
                return fail("shortcut move failed")
            start = (head + best) % total
            # 完整恢复成功前不提交头状态；恢复段没有内部离Apple增长。
            if not run_segment(directions2, start, post_length):
                return False
            head = (start + post_length) % total
            remaining = remaining - best - post_length
        else:
            if not run_segment(directions2, head, 1):
                return False
            head = (head + 1) % total
            remaining = remaining - 1

        length = post_length
        pending = remaining == 0
        if pending:
            target_rank = read_target_rank(ranks, size)
            if target_rank == None:
                return False


def run_segment(directions, start, count):
    for direction in directions[start:start + count]:
        if not move(direction):
            return fail("fixed segment move failed")
    return True


def finish_ring(directions, start, length, pending, total):
    while True:
        for direction in directions[start:start + total]:
            if not move(direction):
                return fail("suffix move failed")
            if pending:
                length = length + 1
            pending = get_entity_type() == Entities.Apple
            if length == total:
                clear()
                return True


def read_target_rank(ranks, size):
    if get_entity_type() != Entities.Apple:
        fail("expected Apple at target boundary")
        return None
    target = measure()
    if target == None:
        fail("missing Apple target")
        return None
    if len(target) != 2:
        fail("invalid Apple target dimensions")
        return None
    x = target[0]
    y = target[1]
    if x < 0 or x >= size or y < 0 or y >= size:
        fail("Apple target outside field")
        return None
    if x % 1 != 0 or y % 1 != 0:
        fail("nonintegral Apple target")
        return None
    return ranks[x][y]


def fail(reason):
    quick_print("lb_dinosaur stopped:", reason, "actual_position=", get_pos_x(), get_pos_y(), "time=", get_time())
    return False


if __name__ == "__main__":
    lb_dinosaur()
