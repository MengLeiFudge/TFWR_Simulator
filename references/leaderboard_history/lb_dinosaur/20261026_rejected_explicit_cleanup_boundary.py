from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/leaderboard-astra/dinosaur-explicit-cleanup/boundary.py

def lb_dinosaur():
    global size
    global path
    global x
    global y
    global mx
    global my
    global length
    global step

    clear()
    size = get_world_size()

    path = []
    for _ in range(size):
        path.append([])
        for _ in range(size):
            path[-1].append(None)

    for i in range(size - 1):
        path[i][0] = East
    path[-1][0] = North

    line = size - 1
    for _ in range(size // 2):
        for i in range(1, size - 1):
            path[line][i] = North
        path[line][-1] = West
        line -= 1
        for i in range(2, size):
            path[line][i] = South
        path[line][1] = West
        line -= 1
    path[0][1] = South

    change_hat(Hats.Dinosaur_Hat)

    x, y = (0, 0)
    mx, my = measure()
    length = 1
    step = 0
    length = 2
    path[0][0] = West
    if not run_dinosaur_path():
        quick_print("lb_dinosaur stopped: chase move failed")
        clear()
        return


def update_and_move(dir):
    global length
    global step
    global x
    global y
    global mx
    global my

    if not move(dir):
        quick_print("lb_dinosaur crash", dir, x, y, mx, my, length, step, get_time())
        return None

    step += 1

    if dir == North:
        y += 1
    elif dir == South:
        y -= 1
    elif dir == East:
        x += 1
    else:
        x -= 1

    if x == mx and y == my:
        pos = measure()
        if pos:
            mx, my = pos
            length += 1

    return x == 0


def simple_update_and_move(dir):
    global x
    global y

    if not move(dir):
        return False

    if dir == North:
        y += 1
    elif dir == South:
        y -= 1
    elif dir == East:
        x += 1
    else:
        x -= 1

    return True


def run_dinosaur_path():
    global step

    chase_limit = size * size * 9 / 25
    while length < chase_limit:
        step = 0
        while step < length * 15 // 16:
            if update_and_move(path[x][y]) == None:
                return False
        while x < mx:
            if update_and_move(East) == None:
                return False
        while y == 0:
            if x % 2 == 0:
                if update_and_move(East) == None:
                    return False
            else:
                if update_and_move(North) == None:
                    return False
        while x >= mx:
            mx_ = mx
            my_ = my
            if my_ == 0:
                break
            while y < my_:
                if can_move(North):
                    if update_and_move(North) == None:
                        return False
                else:
                    at_left = update_and_move(West)
                    if at_left == None:
                        return False
                    if at_left:
                        break
            if x == 0:
                break
            while y > my_:
                if can_move(South):
                    if update_and_move(South) == None:
                        return False
                else:
                    at_left = update_and_move(West)
                    if at_left == None:
                        return False
                    if at_left:
                        break
            if x == 0:
                break
            while x > mx_:
                at_left = update_and_move(West)
                if at_left == None:
                    return False
                if at_left:
                    break
            if x == 0:
                break
        while x > 0:
            if can_move(West):
                if update_and_move(West) == None:
                    return False
            else:
                if update_and_move(path[x][y]) == None:
                    return False
        while y > 0:
            if can_move(South):
                if update_and_move(South) == None:
                    return False
            else:
                if update_and_move(path[x][y]) == None:
                    return False
    route = []
    rx = 0
    ry = 0
    for _ in range(size * size):
        direction = path[rx][ry]
        route.append(direction)
        if direction == North:
            ry += 1
        elif direction == South:
            ry -= 1
        elif direction == East:
            rx += 1
        else:
            rx -= 1
    while True:
        for direction in route:
            if not move(direction):
                clear()
                return True


if __name__ == "__main__":
    lb_dinosaur()
