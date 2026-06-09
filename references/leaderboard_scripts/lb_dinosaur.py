from __builtins__ import *

# 15:26.484
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
    run_dinosaur_path()


def update_and_move(dir):
    global length
    global step
    global x
    global y
    global mx
    global my

    if not can_move(dir):
        while True:
            pass

    move(dir)
    step += 1

    x = get_pos_x()
    y = get_pos_y()

    if x == mx and y == my:
        pos = measure()
        if pos:
            mx, my = pos
            length += 1

    return x == 0


def simple_update_and_move(dir):
    global x
    global y

    if not can_move(dir):
        return False

    move(dir)

    x = get_pos_x()
    y = get_pos_y()

    return True


def run_dinosaur_path():
    global step

    while length < size * size / 3:
        step = 0
        while step < length:
            update_and_move(path[x][y])
        while x < mx:
            update_and_move(East)
        while y == 0:
            if x % 2 == 0:
                update_and_move(East)
            else:
                update_and_move(North)
        while x >= mx:
            mx_ = mx
            my_ = my
            if my_ == 0:
                break
            while y < my_:
                if can_move(North):
                    update_and_move(North)
                else:
                    if update_and_move(West):
                        break
            if x == 0:
                break
            while y > my_:
                if can_move(South):
                    update_and_move(South)
                else:
                    if update_and_move(West):
                        break
            if x == 0:
                break
            while x > mx_:
                if update_and_move(West):
                    break
            if x == 0:
                break
        while x > 0:
            update_and_move(West)
        while y > 0:
            update_and_move(South)
    while simple_update_and_move(path[x][y]):
        pass
    clear()


if __name__ == "__main__":
    lb_dinosaur()
