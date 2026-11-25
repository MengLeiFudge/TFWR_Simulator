from __builtins__ import *
# 完整轮时间：本版尚无完整实机成绩；本地完整目标随机抽样均值见同名单榜文档。


def lb_bamboo():
    clear()
    for _ in range(31):
        spawn_drone(bamboo_row)
        move(North)
    bamboo_row()


def bamboo_wait(target):
    while get_time() + 1 < target:
        do_a_flip()
    while get_time() < target:
        for _ in range(8):
            pass


def bamboo_row():
    goal = 500000000
    my_y = get_pos_y()
    good = []
    for _ in range(32):
        good.append(False)
    well_x = -1
    num_good = 0
    # 扫描整行识别 bambooNoise 高噪声格（首花 6），其余非升降井低噪声格顺路筛首花 5 吃免费无水副产。
    for x in range(32):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Bamboo)
        m = measure()
        while m != 5 and m != 2:
            harvest()
            plant(Entities.Bamboo)
            m = measure()
        if m == 5:
            good[x] = True
            num_good += 1
        elif well_x == -1:
            harvest()
            well_x = x
        else:
            harvest()
            plant(Entities.Bamboo)
            while measure() != 4:
                harvest()
                plant(Entities.Bamboo)
        move(East)

    if num_good == 0:
        return
    if well_x == -1:
        well_x = 0
        good[0] = False
        num_good -= 1
        harvest()

    if well_x <= 16:
        for _ in range(well_x):
            move(East)
    else:
        for _ in range(32 - well_x):
            move(West)

    is_good = []
    state = []
    for k in range(32):
        tx = (well_x + 1 + k) % 32
        if good[tx]:
            is_good.append(True)
            state.append(0)
        else:
            is_good.append(False)
            state.append(2)

    unverified = num_good
    sweep = 32 * 0.032922
    new_lowest = 0.0
    w_avg = 0.0
    p3_end = get_time() - 2.0
    growth1 = 5

    # 主循环：5 -> 10 -> 1 保桩批量切收，固定 growth3=4（13 阶最优单位水位产出），行内最低水位均衡浇水。
    for cycle in range(512):
        w1 = new_lowest * 0.975
        target = p3_end + growth1 / (1 + 4 * w1) + 0.015 - sweep
        bamboo_wait(target)
        p1_start = get_time()
        hover(5)
        if unverified == 0:
            for _ in range(32):
                move(East)
        else:
            allow_reroll = num_items(Items.Bamboo) < 425000000
            for k in range(32):
                move(East)
                if state[k] == 0:
                    nf = measure()
                    if nf == 10:
                        state[k] = 2
                        unverified -= 1
                    elif nf != 5:
                        if allow_reroll:
                            state[k] = 1
                        else:
                            state[k] = 2
                            unverified -= 1

        if cycle > 0 and not (cycle <= 2 and unverified * 2 > num_good and new_lowest < 0.50):
            w2 = new_lowest * 0.965
            target = p1_start + 5 / (1 + 4 * w2) + 0.032
            bamboo_wait(target)
            p2_start = get_time()
            hover(10)
            for _ in range(32):
                move(East)

            w3 = (w_avg * 0.80 + new_lowest * 0.20) * 0.985
            target = p2_start + 4 / (1 + 4 * w3) + 0.008
            bamboo_wait(target)

        cur_b = num_items(Items.Bamboo)
        if cur_b >= 485500000:
            hover(0)
            for _ in range(32):
                move(East)
                if num_items(Items.Bamboo) >= goal:
                    clear()
                    return
            for _ in range(3):
                if num_items(Items.Bamboo) >= goal:
                    clear()
                    return
                do_a_flip()
            if num_items(Items.Bamboo) >= goal:
                clear()
                return
            for k in range(32):
                move(East)
                if is_good[k]:
                    plant(Entities.Bamboo)
                    state[k] = 2
            unverified = 0
            growth1 = 5
            p3_end = get_time()
            continue

        hover(1)
        growth1 = 4
        w_goal = new_lowest + 0.06
        tank = num_items(Items.Water)
        max_w = 0.76
        if tank >= 40:
            max_w = 0.76 + (tank - 40) * 0.002
            if max_w > 0.85:
                max_w = 0.85
        if w_goal > max_w:
            w_goal = max_w
        min_tank = 4 + new_lowest * 26 + my_y * 0.35
        if unverified == 0:
            min_tank -= 8
            if min_tank < 4:
                min_tank = 4

        next_lowest = 1.0
        w_sum = 0.0
        check_done = cur_b >= 472000000
        if unverified == 0 and not check_done:
            for k in range(32):
                move(East)
                if is_good[k]:
                    level = get_water()
                    if level < w_goal and num_items(Items.Water) >= min_tank:
                        if use_item(Items.Water, 1):
                            level += 0.25
                            if level > 1.0:
                                level = 1.0
                    w_sum += level
                    if level < next_lowest:
                        next_lowest = level
        else:
            for k in range(32):
                move(East)
                if is_good[k]:
                    if check_done and num_items(Items.Bamboo) >= goal:
                        clear()
                        return
                    if state[k] == 1:
                        harvest()
                        plant(Entities.Bamboo)
                        while measure() != 5:
                            harvest()
                            plant(Entities.Bamboo)
                        state[k] = 0
                        growth1 = 5
                    level = get_water()
                    if level < w_goal and num_items(Items.Water) >= min_tank:
                        if use_item(Items.Water, 1):
                            level += 0.25
                            if level > 1.0:
                                level = 1.0
                    w_sum += level
                    if level < next_lowest:
                        next_lowest = level
        new_lowest = next_lowest
        w_avg = w_sum / num_good
        p3_end = get_time()


if __name__ == "__main__":
    lb_bamboo()
