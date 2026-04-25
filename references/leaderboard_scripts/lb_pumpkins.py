from __builtins__ import *


def get_pos():
    return get_pos_x(), get_pos_y()


def move_to(pos):
    x, y = pos
    size = get_world_size()
    dx = x - get_pos_x()
    if abs(dx) > size // 2:
        if dx > 0:
            for _ in range(size - dx):
                move(West)
        else:
            for _ in range(size + dx):
                move(East)
    else:
        if dx < 0:
            for _ in range(-dx):
                move(West)
        elif dx > 0:
            for _ in range(dx):
                move(East)
    dy = y - get_pos_y()
    if abs(dy) > size // 2:
        if dy > 0:
            for _ in range(size - dy):
                move(South)
        else:
            for _ in range(size + dy):
                move(North)
    else:
        if dy < 0:
            for _ in range(-dy):
                move(South)
        elif dy > 0:
            for _ in range(dy):
                move(North)


def move_n(direction, count):
    for _ in range(count):
        move(direction)


clear()
# 3x6 哈密顿路径
# ↓←←
# ↓→↑
# ↓↑←
# ↓→↑
# ↓↑←
# →→↑
def path_36(func):
    dir_list = [
        East , East , North, West , North, East , North, West , North, East ,
        North, West , West , South, South, South, South, South
    ]
    for dir in dir_list:
        func()
        move(dir)
# 6x6 哈密顿路径
# ↓←←↓←←
# →↓↑↓→↑
# ↓←↑←↑←
# →↓→↓→↑
# ↓←↑↓↑←
# →→↑→→↑
def path_66(func):
    dir_list = [
        East , East , North, North, East , South, South, East , East , North,
        West , North, East , North, West , North, East , North, West , West ,
        South, South, West , North, North, West , West , South, East , South,
        West , South, East , South, West , South,
    ]
    for dir in dir_list:
        func()
        move(dir)
# 5x5 哈密顿路径
# ↓←←↓←
# →↓↑←↑
#  →↓→↑
# ↑←←↑←
# →→→→↑
def path_55(func):
    dir_list = [
        East , East , East , East , North, West , North, East , North, North,
        West , South, West , North, West , West , South, East , South, East ,
        South, West , West , North
    ]
    for dir in dir_list:
        func()
        move(dir)
    func()
    move(South)
    move(South)
# 4x4 哈密顿路径
# ↓←←←
# →↓→↑
# ↓←↑←
# →→→↑
def path_44(func):
    dir_list = [
        East , East , East , North, West , North, East , North,
        West , West , West , South, East , South, West , South
    ]
    for dir in dir_list:
        func()
        move(dir)

def plant_pumpkin():
    while get_water() + 0.25 <= min(num_items(Items.Water) / 100, 1.0):
        use_item(Items.Water)
    plant(Entities.Pumpkin)
unchecked = []
PUMPKIN3_LAST_LOG_TIME = -9999
PUMPKIN3_LAST_LOG_PUMPKIN = -1


def reset_pumpkin3_state():
    global unchecked
    global PUMPKIN3_LAST_LOG_TIME
    global PUMPKIN3_LAST_LOG_PUMPKIN
    unchecked = []
    PUMPKIN3_LAST_LOG_TIME = -9999
    PUMPKIN3_LAST_LOG_PUMPKIN = -1


def log_pumpkin3_progress():
    global PUMPKIN3_LAST_LOG_TIME
    global PUMPKIN3_LAST_LOG_PUMPKIN
    now = get_time()
    pumpkin = num_items(Items.Pumpkin)
    if now - PUMPKIN3_LAST_LOG_TIME >= 20 or pumpkin - PUMPKIN3_LAST_LOG_PUMPKIN >= 25000000:
        quick_print("pumpkin3 progress pumpkin=", pumpkin, " time=", now)
        PUMPKIN3_LAST_LOG_TIME = now
        PUMPKIN3_LAST_LOG_PUMPKIN = pumpkin


def find_dead_pumpkin():
    if not can_harvest():
        unchecked.append(get_pos())
    plant(Entities.Pumpkin)

def task_with_exit(path, height, final_check, exit_condition, should_log):
    def _task():
        global unchecked
        pos_o = get_pos()
        fixed_y = get_pos_y()
        if get_ground_type() != Grounds.Soil:
            path(till)
        while not exit_condition():
            if should_log:
                log_pumpkin3_progress()
            path(plant_pumpkin)
            path(find_dead_pumpkin)
            if exit_condition():
                return
            while unchecked:
                if exit_condition():
                    return
                to_remove = []
                for pos in unchecked:
                    if exit_condition():
                        return
                    move_to(pos)
                    if can_harvest():
                        to_remove.append(pos)
                        continue
                    plant_pumpkin()
                    while len(unchecked) <= 5 and get_water() < 0.9 and num_items(Items.Water) > 10:
                        use_item(Items.Water)
                for pos in to_remove:
                    unchecked.remove(pos)
                if len(unchecked) == 1 and num_items(Items.Fertilizer) > 10:
                    move_to(unchecked[0])
                    while not can_harvest():
                        plant_pumpkin()
                        use_item(Items.Fertilizer)
                    break
            if exit_condition():
                return
            if not final_check:
                harvest()
                move_to(pos_o)
                continue
            pos_a = (get_pos_x(), fixed_y + 1)
            pos_b = (get_pos_x(), fixed_y + height - 2)
            move_to(pos_a)
            a = measure(South)
            move_to(pos_b)
            b = measure(North)
            c = measure()
            while a != b and a and b and c:
                move_to(pos_a)
                a = measure(South)
                move_to(pos_b)
                b = measure(North)
                c = measure()
            if a or b:
                harvest()
            if exit_condition():
                return
            move_to(pos_o)
    return _task

def task(path, height, final_check = False, end_value = 200000000, should_log = False):
    def exit_condition():
        return num_items(Items.Pumpkin) >= end_value
    return task_with_exit(path, height, final_check, exit_condition, should_log)

def main1():
    reset_pumpkin3_state()
    quick_print("pumpkin3 start")
    spawn_drone(task(path_55, 5))
    move_n(East, 6)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 4)
    spawn_drone(task(path_66, 6))
    move_n(East, 7)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 4)
    spawn_drone(task(path_55, 5))
    move_to((0, 6))
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_to((7, 7))
    spawn_drone(task(path_55, 5))
    move_n(East, 6)
    spawn_drone(task(path_66, 6))
    move_n(East, 7)
    spawn_drone(task(path_55, 5))
    move_to((26, 6))
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_to((0, 13))
    spawn_drone(task(path_66, 6))
    move_n(East, 7)
    spawn_drone(task(path_66, 6))
    move_n(East, 12)
    spawn_drone(task(path_66, 6))
    move_n(East, 7)
    spawn_drone(task(path_66, 6))
    move_to((0, 20))
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 4)
    spawn_drone(task(path_55, 5))
    move_to((13, 19))
    spawn_drone(task(path_66, 6))
    move_to((20, 20))
    spawn_drone(task(path_55, 5))
    move_n(East, 6)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_to((0, 27))
    spawn_drone(task(path_55, 5))
    move_to((6, 26))
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 4)
    spawn_drone(task(path_66, 6))
    move_n(East, 7)
    spawn_drone(task(path_36, 6, True))
    move_n(East, 3)
    spawn_drone(task(path_36, 6, True))
    move_to((27, 27))
    task(path_55, 5, False, 200000000, True)()
def main2():
    set_world_size(27)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_to((0, 7))
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_to((0, 14))
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_to((0, 21))
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    spawn_drone(task(path_36, 6))
    move_n(East, 4)
    spawn_drone(task(path_36, 6))
    move_n(East, 3)
    task(path_36, 6)()
if __name__ == '__main__':
    main1()
