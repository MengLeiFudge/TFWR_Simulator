from __builtins__ import *
# 完整轮时间：未取得（本地游戏随机完整抽样均值 6:44.261）。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。

def lb_pumpkins_single():
    set_world_size(6)
    clear()
    wave_first()
    for _ in range(88):
        wave_6x6()
    while True:
        have = num_items(Items.Pumpkin)
        if have >= 10000000:
            return
        need = 10000000 - have
        if need <= 32768:
            wave_small(4)
        elif need <= 64000:
            wave_small(5)
        else:
            wave_6x6()


def plant_w1():
    till()
    plant(Entities.Pumpkin)
    nw = num_items(Items.Water)
    if nw >= 4:
        use_item(Items.Water, 4)
    elif nw >= 3:
        use_item(Items.Water, 3)
    elif nw >= 2:
        use_item(Items.Water, 2)
    elif nw >= 1:
        use_item(Items.Water, 1)


def is_full(x, y):
    v = measure()
    if v == None:
        return False
    if y == 0:
        if v == measure(South):
            return True
    elif y == 5:
        if v == measure(North):
            return True
    if x == 0:
        if v == measure(West):
            return True
    elif x == 5:
        if v == measure(East):
            return True
    return False


def step_to_near(cx, cy, tx, ty):
    dx_e = (tx - cx) % 6
    if dx_e <= 3:
        dx = dx_e
        dir_x = East
    else:
        dx = 6 - dx_e
        dir_x = West
    dy_n = (ty - cy) % 6
    if dy_n <= 3:
        dy = dy_n
        dir_y = North
    else:
        dy = 6 - dy_n
        dir_y = South
    if dx == 0 and dy == 0:
        return None
    if dy > 0:
        dy -= 1
        last_d = dir_y
    else:
        dx -= 1
        last_d = dir_x
    for _ in range(dx):
        move(dir_x)
    for _ in range(dy):
        move(dir_y)
    return last_d


def fert_to_done(tx, ty, unripes, max_grow):
    while True:
        use_item(Items.Fertilizer)
        if can_harvest():
            return True
        if get_entity_type() == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
        if num_items(Items.Fertilizer) <= 0:
            unripes.append((tx, ty, get_time() + max_grow))
            return False


def repair_queue(unripes, max_grow):
    # Nearest-neighbor with 0-move neighbor peek, border merge early exit, and zero bouncing!
    while unripes:
        cx = get_pos_x()
        cy = get_pos_y()
        # Early exit if whole 6x6 already merged!
        if (cx == 0 or cx == 5 or cy == 0 or cy == 5) and is_full(cx, cy):
            return
        now = get_time()
        n = len(unripes)

        # Pick best target: prefer ready tiles (closest first); if none ready, pick earliest rt
        best_i = 0
        best_ready = False
        best_key = 999999999.0
        for i in range(n):
            tx, ty, rt = unripes[i]
            dx = (tx - cx) % 6
            if dx > 3:
                dx = 6 - dx
            dy = (ty - cy) % 6
            if dy > 3:
                dy = 6 - dy
            d = dx + dy
            if now >= rt:
                if not best_ready or d < best_key:
                    best_ready = True
                    best_key = d
                    best_i = i
            elif not best_ready:
                # Score by distance + remaining wait
                key = d * 0.04 + (rt - now)
                if key < best_key:
                    best_key = key
                    best_i = i

        tx, ty, rt = unripes.pop(best_i)
        last_d = step_to_near(cx, cy, tx, ty)

        if last_d == None:
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                if True and num_items(Items.Fertilizer) > 0:
                    fert_to_done(tx, ty, unripes, max_grow)
                else:
                    unripes.append((tx, ty, get_time() + max_grow))
            elif not can_harvest():
                if True and num_items(Items.Fertilizer) > 0:
                    fert_to_done(tx, ty, unripes, max_grow)
                elif not unripes:
                    while not can_harvest():
                        if get_entity_type() == Entities.Dead_Pumpkin:
                            plant(Entities.Pumpkin)
                            if True and num_items(Items.Fertilizer) > 0:
                                fert_to_done(tx, ty, unripes, max_grow)
                                break
                else:
                    unripes.append((tx, ty, rt))
        else:
            if get_entity_type(last_d) == Entities.Dead_Pumpkin:
                move(last_d)
                plant(Entities.Pumpkin)
                if True and num_items(Items.Fertilizer) > 0:
                    fert_to_done(tx, ty, unripes, max_grow)
                else:
                    unripes.append((tx, ty, get_time() + max_grow))
            elif get_time() >= rt:
                continue
            else:
                m = measure()
                if m != None and m == measure(last_d):
                    continue
                move(last_d)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    if True and num_items(Items.Fertilizer) > 0:
                        fert_to_done(tx, ty, unripes, max_grow)
                    else:
                        unripes.append((tx, ty, get_time() + max_grow))
                elif not can_harvest():
                    if True and num_items(Items.Fertilizer) > 0:
                        fert_to_done(tx, ty, unripes, max_grow)
                    elif not unripes:
                        while not can_harvest():
                            if get_entity_type() == Entities.Dead_Pumpkin:
                                plant(Entities.Pumpkin)
                                if True and num_items(Items.Fertilizer) > 0:
                                    fert_to_done(tx, ty, unripes, max_grow)
                                    break
                    else:
                        unripes.append((tx, ty, rt))


def wave_first():
    for c in range(3):
        for j in range(5):
            plant_w1()
            move(North)
        plant_w1()
        move(East)
        for j in range(5):
            plant_w1()
            move(South)
        plant_w1()
        if c < 2:
            move(East)
    move(East)
    unripes = []
    for c in range(3):
        for j in range(5):
            if get_water() < 0.75:
                water = num_items(Items.Water)
                if water >= 2:
                    use_item(Items.Water, 2)
                elif water >= 1:
                    use_item(Items.Water, 1)
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
            elif not can_harvest():
                unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
            move(North)
        if get_water() < 0.75:
            water = num_items(Items.Water)
            if water >= 2:
                use_item(Items.Water, 2)
            elif water >= 1:
                use_item(Items.Water, 1)
        if get_entity_type() == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
        elif not can_harvest():
            unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
        move(East)
        for j in range(5):
            if get_water() < 0.75:
                water = num_items(Items.Water)
                if water >= 2:
                    use_item(Items.Water, 2)
                elif water >= 1:
                    use_item(Items.Water, 1)
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
            elif not can_harvest():
                unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
            move(South)
        if get_water() < 0.75:
            water = num_items(Items.Water)
            if water >= 2:
                use_item(Items.Water, 2)
            elif water >= 1:
                use_item(Items.Water, 1)
        if get_entity_type() == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
        elif not can_harvest():
            unripes.append((get_pos_x(), get_pos_y(), get_time() + 1.13))
        if c < 2:
            move(East)
    repair_queue(unripes, 1.13)
    harvest()


def replant_col4(x, y, unripes, max_grow):
    plant(Entities.Pumpkin)
    if False and num_items(Items.Fertilizer) > 0:
        fert_to_done(x, y, unripes, max_grow)
    else:
        unripes.append((x, y, get_time() + max_grow))


def wave_6x6():
    max_grow = 1.13
    col5_ready = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for c in range(3):
        for j in range(5):
            plant(Entities.Pumpkin)
            if get_water() < 0.6:
                use_item(Items.Water, 2)
            move(North)
        plant(Entities.Pumpkin)
        if get_water() < 0.6:
            use_item(Items.Water, 2)
        move(East)
        if c == 2:
            for j in range(5):
                plant(Entities.Pumpkin)
                w = get_water()
                if w < 0.6:
                    use_item(Items.Water, 2)
                    w = 1.0
                col5_ready[j] = get_time() + 3.82 / (1.0 + 4.0 * w)
                move(South)
            plant(Entities.Pumpkin)
            w = get_water()
            if w < 0.6:
                use_item(Items.Water, 2)
                w = 1.0
            col5_ready[5] = get_time() + 3.82 / (1.0 + 4.0 * w)
        else:
            for j in range(5):
                plant(Entities.Pumpkin)
                if get_water() < 0.6:
                    use_item(Items.Water, 2)
                move(South)
            plant(Entities.Pumpkin)
            if get_water() < 0.6:
                use_item(Items.Water, 2)
            move(East)

    unripes = []
    move(East)
    move(East)
    cx = get_pos_x()
    cy = get_pos_y()
    wx = (cx - 1) % 6
    ex = (cx + 1) % 6

    # Walk col x0+1 North with vertical chaining
    j = 0
    while j < 6:
        if get_entity_type() == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            unripes.append((cx, cy, get_time() + max_grow))
        e_dead = get_entity_type(East) == Entities.Dead_Pumpkin
        w_dead = get_entity_type(West) == Entities.Dead_Pumpkin
        if e_dead and w_dead:
            move(East)
            plant(Entities.Pumpkin)
            unripes.append((ex, cy, get_time() + max_grow))
            move(West)
            move(West)
            plant(Entities.Pumpkin)
            unripes.append((wx, cy, get_time() + max_grow))
            if j < 5 and get_entity_type(North) == Entities.Dead_Pumpkin:
                move(North)
                j += 1
                cy = (cy + 1) % 6
                plant(Entities.Pumpkin)
                unripes.append((wx, cy, get_time() + max_grow))
                move(East)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unripes.append((cx, cy, get_time() + max_grow))
                if get_entity_type(East) == Entities.Dead_Pumpkin:
                    move(East)
                    plant(Entities.Pumpkin)
                    unripes.append((ex, cy, get_time() + max_grow))
                    move(West)
            else:
                move(East)
        elif w_dead:
            move(West)
            plant(Entities.Pumpkin)
            unripes.append((wx, cy, get_time() + max_grow))
            if j < 5 and get_entity_type(North) == Entities.Dead_Pumpkin:
                move(North)
                j += 1
                cy = (cy + 1) % 6
                plant(Entities.Pumpkin)
                unripes.append((wx, cy, get_time() + max_grow))
                move(East)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unripes.append((cx, cy, get_time() + max_grow))
                if get_entity_type(East) == Entities.Dead_Pumpkin:
                    move(East)
                    plant(Entities.Pumpkin)
                    unripes.append((ex, cy, get_time() + max_grow))
                    move(West)
            else:
                move(East)
        elif e_dead:
            move(East)
            plant(Entities.Pumpkin)
            unripes.append((ex, cy, get_time() + max_grow))
            if j < 5 and get_entity_type(North) == Entities.Dead_Pumpkin:
                move(North)
                j += 1
                cy = (cy + 1) % 6
                plant(Entities.Pumpkin)
                unripes.append((ex, cy, get_time() + max_grow))
                move(West)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unripes.append((cx, cy, get_time() + max_grow))
                if get_entity_type(West) == Entities.Dead_Pumpkin:
                    move(West)
                    plant(Entities.Pumpkin)
                    unripes.append((wx, cy, get_time() + max_grow))
                    move(East)
            else:
                move(West)
        if j < 5:
            move(North)
            cy = (cy + 1) % 6
        j += 1

    # Move East 3 to col x0+4
    move(East)
    move(East)
    move(East)
    cx = (cx + 3) % 6
    wx = (cx - 1) % 6
    ex = (cx + 1) % 6

    j = 0
    while j < 6:
        if get_entity_type() == Entities.Dead_Pumpkin:
            replant_col4(cx, cy, unripes, max_grow)
        elif not can_harvest():
            unripes.append((cx, cy, get_time() + max_grow))
        w_dead = get_entity_type(West) == Entities.Dead_Pumpkin
        e_dead = get_entity_type(East) == Entities.Dead_Pumpkin
        if not e_dead and get_time() < col5_ready[j]:
            unripes.append((ex, cy, col5_ready[j]))
        if w_dead and e_dead:
            move(West)
            replant_col4(wx, cy, unripes, max_grow)
            move(East)
            move(East)
            replant_col4(ex, cy, unripes, max_grow)
            move(West)
        elif w_dead:
            move(West)
            replant_col4(wx, cy, unripes, max_grow)
            if j < 5 and get_entity_type(South) == Entities.Dead_Pumpkin:
                move(South)
                j += 1
                cy = (cy - 1) % 6
                replant_col4(wx, cy, unripes, max_grow)
                move(East)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    replant_col4(cx, cy, unripes, max_grow)
                elif not can_harvest():
                    unripes.append((cx, cy, get_time() + max_grow))
                if get_entity_type(East) == Entities.Dead_Pumpkin:
                    move(East)
                    replant_col4(ex, cy, unripes, max_grow)
                    move(West)
                elif get_time() < col5_ready[j]:
                    unripes.append((ex, cy, col5_ready[j]))
            else:
                move(East)
        elif e_dead:
            move(East)
            replant_col4(ex, cy, unripes, max_grow)
            if j < 5 and get_entity_type(South) == Entities.Dead_Pumpkin:
                move(South)
                j += 1
                cy = (cy - 1) % 6
                replant_col4(ex, cy, unripes, max_grow)
                move(West)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    replant_col4(cx, cy, unripes, max_grow)
                elif not can_harvest():
                    unripes.append((cx, cy, get_time() + max_grow))
                if get_entity_type(West) == Entities.Dead_Pumpkin:
                    move(West)
                    replant_col4(wx, cy, unripes, max_grow)
                    move(East)
            else:
                move(West)
        if j < 5:
            move(South)
            cy = (cy - 1) % 6
        j += 1

    repair_queue(unripes, max_grow)
    harvest()


def move_to_exact(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx_e = (tx - cx) % 6
    if dx_e <= 3:
        for _ in range(dx_e):
            move(East)
    else:
        for _ in range(6 - dx_e):
            move(West)
    dy_n = (ty - cy) % 6
    if dy_n <= 3:
        for _ in range(dy_n):
            move(North)
    else:
        for _ in range(6 - dy_n):
            move(South)


def wave_small(k):
    move_to_exact(0, 0)
    unripes = []
    for x in range(k):
        if x % 2 == 0:
            for y in range(k):
                plant(Entities.Pumpkin)
                if get_water() < 0.6:
                    use_item(Items.Water, 2)
                unripes.append((x, y, get_time() + 1.13))
                if y < k - 1:
                    move(North)
        else:
            for y in range(k - 1, -1, -1):
                plant(Entities.Pumpkin)
                if get_water() < 0.6:
                    use_item(Items.Water, 2)
                unripes.append((x, y, get_time() + 1.13))
                if y > 0:
                    move(South)
        if x < k - 1:
            move(East)
    repair_queue(unripes, 1.13)
    if get_pos_x() >= k or get_pos_y() >= k:
        move_to_exact(0, 0)
    harvest()


if __name__ == "__main__":
    lb_pumpkins_single()
