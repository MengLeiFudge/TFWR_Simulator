from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/leaderboard-astra/github-dinosaur-search/lb_dinosaur_martin.py
# 私有候选：MartinOpat蛇形Hamilton回路与水平捷径；未取得完整成绩。
# 来源固定树6754008045a62dcf46f51acd6e33d1f68f341b99，原仓库未附许可。

def lb_dinosaur():
    set_world_size(32)
    do_dinosaur()
    change_hat(Hats.Brown_Hat)

apos = [-1, -1]
length = 1
n = 32
eaten = True
done = False


arr = []
head = 0
tail = 0
max_size = 8
empty = True
full = False


def queue_init(_max_size=8):
    global arr
    global head
    global tail
    global max_size
    global empty
    global full

    arr = []
    head = 0
    tail = 0
    empty = True
    full = False

    max_size = _max_size
    for i in range(max_size):
        arr.append(None)


def queue_is_full():
    global full

    return full


def queue_is_empty():
    global empty

    return empty


def queue_add(el):
    global arr
    global tail
    global max_size
    global empty
    global full

    if full:
        print("Error: tried adding to q when full")

    empty = False
    arr[tail] = el
    tail = (tail + 1) % max_size

    if tail == head:
        full = True


def queue_pop():
    global arr
    global head
    global tail
    global max_size
    global empty
    global full

    if empty:
        print("Error: Tried to pop from an empty q")

    full = False
    el = arr[head]
    head = (head + 1) % max_size

    if head == tail:
        empty = True

    return el


def queue_get_first():
    global head
    global arr

    return arr[head]


def obs_apple():
    global apos
    global done

    # This is only called if we are sure we are over an apple
    pos = measure()
    if pos:
        apos[0], apos[1] = pos
    else:
        quick_print("dinosaur_full")
        done = True


def check_apple():
    global apos
    global length
    global eaten

    x = get_pos_x()
    y = get_pos_y()

    if x == apos[0] and y == apos[1]:
        length += 1
        eaten = True
        obs_apple()

        return True
    return False


def safe_move(dir):
    global eaten

    # if not move(dir):
    # print("Something is wrong")

    if not move(dir):
        return False

    if eaten:
        queue_add((get_pos_x(), get_pos_y()))
        eaten = False
    else:
        queue_pop()
        queue_add((get_pos_x(), get_pos_y()))
    check_apple()
    return True


def ord_idx(x, y):
    # Index of tile in Ham. cycle

    n = get_world_size()
    neff = n - 1

    if y == n - 1:
        return n * n - x - 1

    if x % 2 == 1:
        return x * neff + y
    else:
        return x * neff + (n - 2) - y


def is_between(idx, H, T):
    # Is idx safely position between H and T
    if H < T:
        return H < idx < T
    else:
        return idx > H or idx < T


def do_dinosaur():
    global done
    global apos
    global length
    global n
    global eaten

    change_hat(Hats.Brown_Hat)

    clear()
    # set_world_size(8)

    change_hat(Hats.Dinosaur_Hat)
    ax, ay = measure()
    apos = [ax, ay]
    length = 1

    n = get_world_size()

    # snake pos
    queue_init(n * n)
    queue_add((0, 0))
    eaten = True
    done = False

    while not done:
        # safe_move(East)
        up = True

        cx = n - 1
        while cx > 0:
            if not safe_move(East):
                return
            cy = n - 2
            while cy > 0:
                x = get_pos_x()
                y = get_pos_y()

                # Horizontal skip to apple ahead
                if x < apos[0] and y == apos[1]:
                    iters = apos[0] - x
                    for k in range(iters):
                        x = get_pos_x()
                        y = get_pos_y()
                        nidx = ord_idx(x + 1, y)
                        hidx = ord_idx(x, y)
                        tx, ty = queue_get_first()
                        tidx = ord_idx(tx, ty)
                        if is_between(nidx, hidx, tidx):
                            if not safe_move(East):
                                return

                            up = not up
                            cy = n - 2 - cy
                            cx -= 1
                        else:
                            break

                # Horizontal skip to the very right, apple is behind us
                if apos[0] < x:
                    for k in range(n - 2 - x):
                        x = get_pos_x()
                        y = get_pos_y()
                        nidx = ord_idx(x + 1, y)
                        hidx = ord_idx(x, y)
                        tx, ty = queue_get_first()
                        tidx = ord_idx(tx, ty)
                        if is_between(nidx, hidx, tidx):
                            if not safe_move(East):
                                return
                            up = not up
                            cy = n - 2 - cy
                            cx -= 1
                        else:
                            break

                if not cy:
                    break

                if up:
                    if not safe_move(North):
                        return
                else:
                    if not safe_move(South):
                        return
                cy -= 1

            up = not up
            cx -= 1

        if not safe_move(North):
            return
        for i in range(n - 1):
            if not safe_move(West):
                return

        for i in range(n - 1):
            if not safe_move(South):
                return


if __name__ == "__main__":
    lb_dinosaur()
