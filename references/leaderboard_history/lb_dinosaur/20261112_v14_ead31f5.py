from __builtins__ import *
# 完整轮时间：本版本尚未取得实机完整统计；仅有本地模拟对照。
# Copyright (c) [2026] [lywlucas]; MIT许可见lywlucas_LICENSE.txt。
# 来源：https://github.com/lywlucas/The_Farmer_was_Replaced/tree/99091a59855da87276573fe37d1bb7e3854704de


def lb_dinosaur():
    before = num_items(Items.Bone)
    began = get_time()
    production_cycle()
    gain = num_items(Items.Bone) - before
    expected = (farm_size * farm_size - 1) ** 2 * 2 ** max(0, num_unlocked(Unlocks.Dinosaurs) - 1)
    quick_print("dinosaur_cycle", gain, get_time() - began)
    if gain < expected:
        quick_print("dinosaur_failed", "incomplete_cycle", gain, expected)


REVERSE = {East: West, West: East, North: South, South: North}
farm_size = 32
cycle_deadline = 0
# 主区域由每轮入口按田尺寸建立，区域查询只复用它。
main_area = None


# 主回路编号只用本轮固定田尺寸，避免每次坐标换算重新读取世界。
def cycle_index(x, y):
    n = farm_size
    if x == 0:
        return n - y
    elif y % 2 == 0:
        return n + (n - 1) * y + x
    else:
        return n + (n - 1) * y + n - x


# 判断目标是否仍在区域的前方，左右转向随区域旋转。
def in_region(location, area, upper=False, can_equal=True):
    size = farm_size
    (x_n, y_n), width, dir, up = area
    x, y = location
    if area == main_area:
        if upper == False:
            return x != 0
        else:
            a, b = (get_pos_x(), get_pos_y())
            return size < cycle_index(a, b) <= cycle_index(x, y)
    if upper == True:
        a, b = (get_pos_x(), get_pos_y())
        flg = False
        if in_region((a, b), area) == False:
            return False
        if up == East:
            if a > x:
                return False
            elif a == x:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif up == West:
            if a < x:
                return False
            elif a == x:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif up == North:
            if b > y:
                return False
            elif b == y:
                if can_equal == False:
                    return False
                else:
                    flg = True
        elif b < y:
            return False
        elif b == y:
            if can_equal == False:
                return False
            else:
                flg = True
        if flg != False:
            d = region_step(area, (a, b))
            if a > x:
                if d != West:
                    return False
            elif a < x:
                if d != East:
                    return False
            elif b > y:
                if d != South:
                    return False
            elif b < y:
                if d != North:
                    return False
    if dir == East:
        if x <= x_n - width or x > x_n:
            return False
    elif dir == West:
        if x < x_n or x >= x_n + width:
            return False
    elif dir == North:
        if y > y_n or y <= y_n - width:
            return False
    elif y < y_n or y >= y_n + width:
        return False
    if up == North:
        if y > y_n:
            return False
    elif up == West:
        if x < x_n:
            return False
    elif up == South:
        if y < y_n:
            return False
    elif x > x_n:
        return False
    return True


# 返回区域蛇形方向；给出模拟坐标时只计算，不移动。
def region_step(area, simulating=None):
    (x_n, y_n), width, dir, up = area
    if simulating == None:
        x, y = (get_pos_x(), get_pos_y())
        if in_region((x, y), area) == False:
            return None
    else:
        x, y = simulating
    if dir == East or dir == West:
        up_dist = abs(y - y_n)
        hor_dist = abs(x - x_n)
    else:
        up_dist = abs(x - x_n)
        hor_dist = abs(y - y_n)
    new_dir = dir
    if up_dist % 2 == 0:
        if hor_dist == 0 and up_dist != 0:
            new_dir = up
        else:
            pass
    elif hor_dist == width - 1:
        new_dir = up
    else:
        new_dir = REVERSE[dir]
    if simulating == None:
        move(new_dir)
    return new_dir


# 在当前安全矩形内沿剪枝路线到目标，返回最后转折点；超时交回上层。
def reach_in_region(target, area):
    a, b = target
    (x_n, y_n), width, dir, up = area
    break_point = None
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return None
    if in_region(target, area, True, True) == False:
        reach_in_region((x_n, y_n), area)
        region_step(area)
        return None
    while get_time() < cycle_deadline:
        x, y = (get_pos_x(), get_pos_y())
        if x == a and y == b:
            if break_point == None:
                break_point = (a, b)
            return break_point
        if dir == East or dir == West:
            if x == a:
                break_point = (x, y)
                for _ in range(abs(y - b)):
                    move(up)
                continue
            temp = region_step(area, (x, y))
            if temp == East:
                if x > a:
                    move(up)
                else:
                    for _ in range(a - x):
                        move(East)
            elif temp == West:
                if x < a:
                    move(up)
                else:
                    for _ in range(x - a):
                        move(West)
            else:
                move(temp)
        else:
            if y == b:
                break_point = (x, y)
                for _ in range(abs(x - a)):
                    move(up)
                continue
            temp = region_step(area, (x, y))
            if temp == North:
                if y > b:
                    move(up)
                else:
                    for _ in range(b - y):
                        move(North)
            elif temp == South:
                if y < b:
                    move(up)
                else:
                    for _ in range(y - b):
                        move(South)
            else:
                move(temp)
    return None


# 按区域出口恢复父区域路线，避免任意短路破坏身体形状。
def leave_region(area):
    (x_n, y_n), width, dir, up = area
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return True
    if up == North or up == South:
        if y != y_n:
            move(up)
        for _ in range(abs(x - x_n) + 1):
            move(dir)
    else:
        if x != x_n:
            move(up)
        for _ in range(abs(y - y_n) + 1):
            move(dir)


# 沿当前矩形吃果，递归进入可恢复子区域，返回新目标与观测计数。
def collect_in_region(target, area, cnt):
    if get_time() >= cycle_deadline:
        return (target, cnt)
    (x_n, y_n), width, dir, up = area
    a, b = target
    x, y = (get_pos_x(), get_pos_y())
    if in_region((x, y), area) == False:
        return (target, cnt)
    if a == 0:
        reach_in_region((x_n, y_n), area)
        region_step(area)
        return (target, cnt)
    last_break = reach_in_region(target, area)
    if last_break == None:
        return (target, cnt)
    cnt += 1
    x, y = (get_pos_x(), get_pos_y())
    if x != a or y != b:
        return (target, cnt)
    newt = measure()
    if in_region(newt, area, True) == True:
        newt, cnt = collect_in_region(newt, area, cnt)
    else:
        # 目标需要跨区时才计算转折带；外侧区域仅在内侧不可达时构造。
        x_b, y_b = last_break
        x_g, y_g = (x, y)
        x_f, y_f = (x, y)
        if up == North or up == South:
            warn = abs(y - y_n)
            n_width = abs(y - y_b)
            if dir == East:
                x_f = x_n - width + 1
                x_g = x_n
            else:
                x_f = x_n + width - 1
                x_g = x_n
        else:
            warn = abs(x - x_n)
            n_width = abs(x - x_b)
            if dir == North:
                y_f = y_n - width + 1
                y_g = y_n
            else:
                y_f = y_n + width - 1
                y_g = y_n
        if warn != 0:
            area_ins = ((x_g, y_g), n_width - 1, up, dir)
            if in_region(newt, area_ins, True, False) == True:
                move(dir)
                newt, cnt = collect_in_region(newt, area_ins, cnt)
                newt, cnt = collect_in_region(newt, area, cnt)
            else:
                area_out = ((x_f, y_f), n_width - 1, up, REVERSE[dir])
                if in_region(newt, area_out, True, False) == True:
                    move(REVERSE[dir])
                    newt, cnt = collect_in_region(newt, area_out, cnt)
                    newt, cnt = collect_in_region(newt, area, cnt)
    if width < farm_size - 1:
        leave_region(area)
    elif cnt <= y * 2 + 1:
        leave_region(area)
    else:
        reach_in_region((x_n, y_n), area)
        region_step(area)
    return (newt, cnt)


# 按主回路的剩余段和后续整圈前进；失败后由入口统一换帽结算。
def fill_main_cycle(start, moves):
    count = len(moves)
    start = start % count
    while True:
        for i in range(start, count):
            if not move(moves[i]):
                return
        start = 0


# 一轮前半采用递归区域，后半按预建主回路填满；退出时换帽真实结算。
def production_cycle():
    global farm_size
    global cycle_deadline
    global main_area
    clear()
    size = get_world_size()
    farm_size = size
    cycle_deadline = get_time() + 1200
    A = size ** 2
    turn_point = A // 2
    main_area = ((1, size - 1), size - 1, West, North)
    main_move = {}
    for xi in range(size):
        for yi in range(size):
            i = cycle_index(xi, yi)
            if i < size:
                main_move[i] = South
            elif i == size:
                main_move[i] = East
            else:
                i = i % A
                main_move[i] = region_step(main_area, (xi, yi))
    change_hat(Hats.Dinosaur_Hat)
    cnt = 1
    next_x, next_y = measure()  # ty: ignore[not-iterable]  此处位于Apple上，measure返回下一苹果坐标。
    next_id = cycle_index(next_x, next_y)
    while get_time() < cycle_deadline:
        x, y = (get_pos_x(), get_pos_y())
        id = cycle_index(x, y)
        if id == next_id:
            cnt += 1
            next_x, next_y = measure()  # ty: ignore[not-iterable]  此处位于Apple上，measure返回下一苹果坐标。
            next_id = cycle_index(next_x, next_y)
        if cnt >= turn_point:
            quick_print('dinosaur_finish', cnt, get_time())
            fill_main_cycle(id, main_move)
            break
        ccnt = cnt - size + cnt // size
        if id < ccnt:
            if id < next_id <= ccnt:
                l = next_id - id
                for _ in range(l):
                    move(main_move[id])
                    id += 1
                continue
            else:
                l = ccnt - id
                for _ in range(l):
                    move(main_move[id])
                    id += 1
                continue
        elif x == 0:
            move(main_move[id])
            continue
        else:
            next_target, new_cnt = collect_in_region((next_x, next_y), main_area, cnt)
            next_x, next_y = next_target
            next_id = cycle_index(next_x, next_y)
            cnt = new_cnt
    change_hat(Hats.Brown_Hat)
    return


if __name__ == "__main__":
    lb_dinosaur()
