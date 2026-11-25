from __builtins__ import *
# 完整轮时间：本版尚无完整实机成绩；本地完整目标随机抽样均值见同名单榜文档。


def lb_bamboo_single():
    clear()
    status = []
    good = []
    aux_ready = []
    for _ in range(64):
        status.append(-1)
        good.append(False)
        aux_ready.append(False)

    # 蛇形扫全图筛选 bambooNoise 高噪声格（measure == 5 -> 首花 6），并做贝叶斯弱格早停。
    good_ids = []
    probed = 0
    for y in range(8):
        for step in range(8):
            x = get_pos_x()
            gid = y * 8 + x
            n0 = 0
            n1 = 0
            if x > 0:
                st = status[gid - 1]
                if st == 0:
                    n0 += 1
                elif st == 1:
                    n1 += 1
            if x < 7:
                st = status[gid + 1]
                if st == 0:
                    n0 += 1
                elif st == 1:
                    n1 += 1
            d0 = 0
            if y > 0:
                st = status[gid - 8]
                if st == 0:
                    n0 += 1
                elif st == 1:
                    n1 += 1
                if x > 0 and status[gid - 9] == 0:
                    d0 += 1
                if x < 7 and status[gid - 7] == 0:
                    d0 += 1

            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Bamboo)
            m = measure()
            if n1 == 0 and n0 >= 2 and d0 >= 1 and len(good_ids) * 2 >= probed - 4:
                if m != 5 and m != 2:
                    harvest()
                    plant(Entities.Bamboo)
                    m = measure()
            else:
                while m != 5 and m != 2:
                    harvest()
                    plant(Entities.Bamboo)
                    m = measure()
            probed += 1
            if m == 5:
                good[gid] = True
                status[gid] = 1
                good_ids.append(gid)
                w_avail = num_items(Items.Water) // 1
                if w_avail >= 4:
                    use_item(Items.Water, 4)
                elif w_avail > 0:
                    use_item(Items.Water, w_avail)
            else:
                status[gid] = 0
                if m == 4:
                    aux_ready[gid] = True
            if step < 7:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        if y < 7:
            move(North)

    t_probe = get_time()
    num_all = len(good_ids)

    # 三起点自适应 Warnsdorff + 环面距离表 2-opt + 单点重插 or-opt + 1/2 节点毛刺剪枝。
    td = [1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1]
    nb_e = []
    nb_w = []
    nb_n = []
    nb_s = []
    px_tbl = []
    py_tbl = []
    px7_tbl = []
    py7_tbl = []
    for gid in range(64):
        gx = gid % 8
        gy = gid // 8
        px_tbl.append(gx)
        py_tbl.append(gy)
        px7_tbl.append(gx + 7)
        py7_tbl.append(gy + 7)
        nb_e.append(gy * 8 + ((gx + 1) % 8))
        nb_w.append(gy * 8 + ((gx - 1) % 8))
        nb_n.append(((gy + 1) % 8) * 8 + gx)
        nb_s.append(((gy - 1) % 8) * 8 + gx)

    s0 = good_ids[0]
    best_dg = 9
    for gid in good_ids:
        dg = good[nb_e[gid]] + good[nb_w[gid]] + good[nb_n[gid]] + good[nb_s[gid]]
        if dg < best_dg:
            best_dg = dg
            s0 = gid
    starts = [s0, good_ids[num_all // 3], good_ids[(num_all * 2) // 3]]

    tour = []
    L = 9999
    for si in range(3):
        if si == 1 and L <= num_all + 2:
            break
        if si == 2 and L <= num_all + 4:
            break
        start_id = starts[si]
        rem = good[:]
        tr = [start_id]
        rem[start_id] = False
        cur = start_id
        for _ in range(num_all - 1):
            best = -1
            best_dg = 9
            nb = nb_e[cur]
            if rem[nb]:
                dg = rem[nb_e[nb]] + rem[nb_w[nb]] + rem[nb_n[nb]] + rem[nb_s[nb]]
                if dg < best_dg:
                    best_dg = dg
                    best = nb
            nb = nb_w[cur]
            if rem[nb]:
                dg = rem[nb_e[nb]] + rem[nb_w[nb]] + rem[nb_n[nb]] + rem[nb_s[nb]]
                if dg < best_dg:
                    best_dg = dg
                    best = nb
            nb = nb_n[cur]
            if rem[nb]:
                dg = rem[nb_e[nb]] + rem[nb_w[nb]] + rem[nb_n[nb]] + rem[nb_s[nb]]
                if dg < best_dg:
                    best_dg = dg
                    best = nb
            nb = nb_s[cur]
            if rem[nb]:
                dg = rem[nb_e[nb]] + rem[nb_w[nb]] + rem[nb_n[nb]] + rem[nb_s[nb]]
                if dg < best_dg:
                    best_dg = dg
                    best = nb
            if best == -1:
                cx7 = px7_tbl[cur]
                cy7 = py7_tbl[cur]
                best_d = 99
                for gid in good_ids:
                    if rem[gid]:
                        d = td[cx7 - px_tbl[gid]] + td[cy7 - py_tbl[gid]]
                        if d < best_d:
                            best_d = d
                            best = gid
                            if d == 2:
                                break
            tr.append(best)
            rem[best] = False
            cur = best
        cur_L = 0
        for i in range(num_all):
            a = tr[i]
            b = tr[(i + 1) % num_all]
            cur_L += td[px7_tbl[a] - px_tbl[b]] + td[py7_tbl[a] - py_tbl[b]]
        if cur_L < L:
            L = cur_L
            tour = tr

    m = len(tour)

    for _ in range(4):
        if L <= m:
            break
        improved = False
        for i in range(m):
            a = tour[i]
            ni = i + 1
            if ni == m:
                ni = 0
            b = tour[ni]
            ax7 = px7_tbl[a]
            ay7 = py7_tbl[a]
            dab = td[ax7 - px_tbl[b]] + td[ay7 - py_tbl[b]]
            if dab <= 1:
                continue
            bx7 = px7_tbl[b]
            by7 = py7_tbl[b]
            for j in range(m):
                if j == i or j == ni:
                    continue
                nj = j + 1
                if nj == m:
                    nj = 0
                if nj == i:
                    continue
                c = tour[j]
                dac = td[ax7 - px_tbl[c]] + td[ay7 - py_tbl[c]]
                if dac >= dab + 2:
                    continue
                e = tour[nj]
                gain = dab + td[px7_tbl[c] - px_tbl[e]] + td[py7_tbl[c] - py_tbl[e]] - (dac + td[bx7 - px_tbl[e]] + td[by7 - py_tbl[e]])
                if gain > 0:
                    if i < j:
                        lo = i + 1
                        hi = j
                    else:
                        lo = j + 1
                        hi = i
                    while lo < hi:
                        tmp = tour[lo]
                        tour[lo] = tour[hi]
                        tour[hi] = tmp
                        lo += 1
                        hi -= 1
                    L -= gain
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    for _ in range(3):
        if L <= m:
            break
        improved = False
        for i in range(m):
            a = tour[(i - 1) % m]
            v = tour[i]
            b = tour[(i + 1) % m]
            vx7 = px7_tbl[v]
            vy7 = py7_tbl[v]
            rem_gain = td[px7_tbl[a] - px_tbl[v]] + td[py7_tbl[a] - py_tbl[v]] + td[vx7 - px_tbl[b]] + td[vy7 - py_tbl[b]] - td[px7_tbl[a] - px_tbl[b]] - td[py7_tbl[a] - py_tbl[b]]
            if rem_gain < 2:
                continue
            for j in range(m):
                if j == i or j == (i - 1) % m:
                    continue
                c = tour[j]
                dvc = td[vx7 - px_tbl[c]] + td[vy7 - py_tbl[c]]
                if dvc >= rem_gain:
                    continue
                e = tour[(j + 1) % m]
                add_cost = dvc + td[vx7 - px_tbl[e]] + td[vy7 - py_tbl[e]] - td[px7_tbl[c] - px_tbl[e]] - td[py7_tbl[c] - py_tbl[e]]
                if add_cost < rem_gain:
                    tour.pop(i)
                    ins = j + 1
                    if i < j:
                        ins = j
                    tour.insert(ins, v)
                    L -= (rem_gain - add_cost)
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    for _ in range(6):
        if L <= 32 or m <= 27:
            break
        best_g = 0
        best_i = -1
        best_k = 1
        for i in range(m):
            a = tour[(i - 1) % m]
            b = tour[i]
            c = tour[(i + 1) % m]
            ax7 = px7_tbl[a]
            ay7 = py7_tbl[a]
            g1 = td[ax7 - px_tbl[b]] + td[ay7 - py_tbl[b]] + td[px7_tbl[b] - px_tbl[c]] + td[py7_tbl[b] - py_tbl[c]] - td[ax7 - px_tbl[c]] - td[ay7 - py_tbl[c]]
            if g1 > best_g:
                best_g = g1
                best_i = i
        if best_g < 2 and m > 28 and L >= 36:
            for i in range(m):
                a = tour[(i - 1) % m]
                b = tour[i]
                c = tour[(i + 1) % m]
                d = tour[(i + 2) % m]
                ax7 = px7_tbl[a]
                ay7 = py7_tbl[a]
                g2 = td[ax7 - px_tbl[b]] + td[ay7 - py_tbl[b]] + td[px7_tbl[b] - px_tbl[c]] + td[py7_tbl[b] - py_tbl[c]] + td[px7_tbl[c] - px_tbl[d]] + td[py7_tbl[c] - py_tbl[d]] - td[ax7 - px_tbl[d]] - td[py7_tbl[d]]
                if g2 > best_g:
                    best_g = g2
                    best_i = i
                    best_k = 2
        if best_k == 1 and best_g < 2:
            break
        if best_k == 2 and best_g < 4:
            break
        L_new = L - best_g
        if L_new < 32:
            break
        m_new = m - best_k
        p_old = L * 0.032922 + 0.033
        if p_old < 1.11:
            p_old = 1.11
        p_new = L_new * 0.032922 + 0.033
        if p_new < 1.11:
            p_new = 1.11
        if ((L_new * 0.032922 + 0.033) + 2 * p_new) / m_new < ((L * 0.032922 + 0.033) + 2 * p_old) / m:
            if best_k == 1:
                tour.pop(best_i)
            else:
                i2 = (best_i + 1) % m
                if i2 > best_i:
                    tour.pop(i2)
                    tour.pop(best_i)
                else:
                    tour.pop(best_i)
                    tour.pop(i2)
            m = m_new
            L = L_new
        else:
            break

    kept = []
    for _ in range(64):
        kept.append(False)
    for gid in tour:
        kept[gid] = True

    raw_steps = []
    raw_ids = []
    px = px_tbl[tour[0]]
    py = py_tbl[tour[0]]
    for i in range(m):
        ni = i + 1
        if ni == m:
            ni = 0
        tx = px_tbl[tour[ni]]
        ty = py_tbl[tour[ni]]
        dx = (tx - px) % 8
        if dx <= 4:
            for _ in range(dx):
                px = (px + 1) % 8
                raw_steps.append(East)
                raw_ids.append(py * 8 + px)
        else:
            for _ in range(8 - dx):
                px = (px - 1) % 8
                raw_steps.append(West)
                raw_ids.append(py * 8 + px)
        dy = (ty - py) % 8
        if dy <= 4:
            for _ in range(dy):
                py = (py + 1) % 8
                raw_steps.append(North)
                raw_ids.append(py * 8 + px)
        else:
            for _ in range(8 - dy):
                py = (py - 1) % 8
                raw_steps.append(South)
                raw_ids.append(py * 8 + px)

    total_steps = len(raw_steps)
    well_idx = -1
    for s in range(total_steps):
        if not kept[raw_ids[s]]:
            well_idx = s
            break
    if well_idx == -1:
        well_idx = total_steps - 1
        kept[raw_ids[well_idx]] = False

    well_id = raw_ids[well_idx]
    steps = []
    is_plant = []
    need_aux = []
    seen = []
    for _ in range(64):
        seen.append(False)
    p_idx = 0
    aux_cnt = 0
    for k in range(total_steps):
        s = (well_idx + 1 + k) % total_steps
        steps.append(raw_steps[s])
        rid = raw_ids[s]
        if kept[rid] and not seen[rid]:
            seen[rid] = True
            is_plant.append(p_idx)
            need_aux.append(False)
            p_idx += 1
        else:
            is_plant.append(-1)
            if rid != well_id and not seen[rid]:
                seen[rid] = True
                aux_cnt += 1
                need_aux.append(not aux_ready[rid])
            else:
                need_aux.append(False)

    num_good = p_idx
    move_to(px_tbl[well_id], py_tbl[well_id])
    harvest()

    # 主循环：5 -> 10 -> 1 保桩批量切收，首轮跳过 10 趟快速重筛二花，终盘 hover(0) 连根收官。
    goal = 25000000
    state = []
    for _ in range(num_good):
        state.append(0)
    unverified = num_good
    locked_h0 = aux_cnt * 3200
    locked_growth3 = 4

    pass_dur = (total_steps + 1) * 0.032922
    w_need = (5 / (pass_dur - 0.032) - 1) / (4 * 0.97)
    if w_need > 0.85:
        w_need = 0.85
    if w_need < 0.65:
        w_need = 0.65

    new_lowest = 0.85
    w_avg = 0.92
    p3_end = t_probe
    growth1 = 5

    for cycle in range(512):
        w1 = new_lowest * 0.985
        target = p3_end + growth1 / (1 + 4 * w1) + 0.015 - (total_steps * 0.032922)
        while get_time() < target:
            pass
        p1_start = get_time()
        hover(5)
        if unverified == 0:
            for d in steps:
                move(d)
        else:
            allow_reroll = num_items(Items.Bamboo) < 20500000
            for s in range(total_steps):
                move(steps[s])
                idx = is_plant[s]
                if idx >= 0 and state[idx] == 0:
                    nf = measure()
                    if nf == 10:
                        state[idx] = 3
                    elif nf != 5:
                        if allow_reroll:
                            state[idx] = 1
                        else:
                            state[idx] = 2
                            unverified -= 1

        if cycle > 0:
            w2 = new_lowest * 0.975
            target = p1_start + 5 / (1 + 4 * w2) + 0.032
            while get_time() < target:
                pass
            p2_start = get_time()
            hover(10)
            if unverified == 0:
                for d in steps:
                    move(d)
                growth3 = locked_growth3
            else:
                growth3 = locked_growth3
                for s in range(total_steps):
                    move(steps[s])
                    idx = is_plant[s]
                    if idx >= 0 and state[idx] == 3:
                        nf = measure()
                        g = nf - 10
                        if g > 5:
                            g = 5
                        if g > locked_growth3:
                            locked_growth3 = g
                            growth3 = g
                        h = nf + 1
                        locked_h0 += h * h * 128
                        state[idx] = 2
                        unverified -= 1

            w3 = (w_avg * 0.60 + new_lowest * 0.40) * 0.98
            target = p2_start + growth3 / (1 + 4 * w3) + 0.015
            while get_time() < target:
                pass

        cur_b = num_items(Items.Bamboo)
        if cur_b + locked_h0 >= goal:
            hover(0)
            for d in steps:
                move(d)
                if num_items(Items.Bamboo) >= goal:
                    clear()
                    return
            for s in range(total_steps):
                move(steps[s])
                if is_plant[s] >= 0:
                    plant(Entities.Bamboo)
            unverified = 0
            locked_h0 = 0
            growth1 = 5
            p3_end = get_time()
            continue

        hover(1)
        growth1 = 4
        new_lowest = 1.0
        w_sum = 0.0
        check_done = cur_b >= goal - num_good * 32000
        w_cur = w_need
        if cur_b >= goal - num_good * 60000:
            w_cur = w_need - 0.06
        if unverified == 0 and not check_done and cycle > 0:
            for s in range(total_steps):
                move(steps[s])
                if is_plant[s] >= 0:
                    level = get_water()
                    if level < w_cur:
                        amt = 2
                        if level >= 0.75:
                            amt = 1
                        use_item(Items.Water, amt)
                        level += amt * 0.25
                        if level > 1.0:
                            level = 1.0
                    w_sum += level
                    if level < new_lowest:
                        new_lowest = level
        else:
            for s in range(total_steps):
                move(steps[s])
                idx = is_plant[s]
                if idx >= 0:
                    if check_done and num_items(Items.Bamboo) >= goal:
                        clear()
                        return
                    if state[idx] == 1:
                        harvest()
                        plant(Entities.Bamboo)
                        while measure() != 5:
                            harvest()
                            plant(Entities.Bamboo)
                        state[idx] = 0
                        growth1 = 5
                    level = get_water()
                    if level < w_cur:
                        amt = 2
                        if level >= 0.75:
                            amt = 1
                        use_item(Items.Water, amt)
                        level += amt * 0.25
                        if level > 1.0:
                            level = 1.0
                    w_sum += level
                    if level < new_lowest:
                        new_lowest = level
                elif cycle == 0 and need_aux[s]:
                    harvest()
                    plant(Entities.Bamboo)
                    while measure() != 4:
                        harvest()
                        plant(Entities.Bamboo)
        w_avg = w_sum / num_good
        p3_end = get_time()


def move_to(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx = (tx - cx) % 8
    if dx <= 4:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(8 - dx):
            move(West)
    dy = (ty - cy) % 8
    if dy <= 4:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(8 - dy):
            move(South)


if __name__ == "__main__":
    lb_bamboo_single()
