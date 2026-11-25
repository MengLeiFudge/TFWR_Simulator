from __builtins__ import *
# 完整轮时间：尚无该版本的完整实机成绩。
# 8x8 单机扫雷：增量 has_act 约束传播 + 双侧差集 + 小前沿精确 CSP + 最低雷率猜格
# + 全雷已知 all_safe 快收 + 合法 use_item(Items.Dynamite) 居中(3,3)连续爆破下潜（避开雷层间距）。

def lb_dynamite_single():
    size = get_world_size()
    n_cells = size * size
    total_mines = (n_cells * 135 + 500) // 1000
    half = size // 2

    d8 = [
        [0, 1, 2, 3, 4, 3, 2, 1],
        [1, 0, 1, 2, 3, 4, 3, 2],
        [2, 1, 0, 1, 2, 3, 4, 3],
        [3, 2, 1, 0, 1, 2, 3, 4],
        [4, 3, 2, 1, 0, 1, 2, 3],
        [3, 4, 3, 2, 1, 0, 1, 2],
        [2, 3, 4, 3, 2, 1, 0, 1],
        [1, 2, 3, 4, 3, 2, 1, 0],
    ]

    near = []
    ortho = []
    o0 = []
    o1 = []
    o2 = []
    o3 = []
    d0_c = []
    d1_c = []
    d2_c = []
    d3_c = []
    cx_tab = []
    cy_tab = []

    for c in range(n_cells):
        x = c % size
        y = c // size
        cx_tab.append(x)
        cy_tab.append(y)
        nb = []
        ob = []
        if y > 0:
            if x > 0:
                nb.append(c - size - 1)
                d0_c.append(c - size - 1)
            else:
                d0_c.append(n_cells)
            nb.append(c - size)
            ob.append(c - size)
            o0.append(c - size)
            if x + 1 < size:
                nb.append(c - size + 1)
                d1_c.append(c - size + 1)
            else:
                d1_c.append(n_cells)
        else:
            o0.append(n_cells)
            d0_c.append(n_cells)
            d1_c.append(n_cells)
        if x > 0:
            nb.append(c - 1)
            ob.append(c - 1)
            o1.append(c - 1)
        else:
            o1.append(n_cells)
        if x + 1 < size:
            nb.append(c + 1)
            ob.append(c + 1)
            o2.append(c + 1)
        else:
            o2.append(n_cells)
        if y + 1 < size:
            if x > 0:
                nb.append(c + size - 1)
                d2_c.append(c + size - 1)
            else:
                d2_c.append(n_cells)
            nb.append(c + size)
            ob.append(c + size)
            o3.append(c + size)
            if x + 1 < size:
                nb.append(c + size + 1)
                d3_c.append(c + size + 1)
            else:
                d3_c.append(n_cells)
        else:
            o3.append(n_cells)
            d2_c.append(n_cells)
            d3_c.append(n_cells)
        near.append(nb)
        ortho.append(ob)

    zeros65 = []
    ones65 = []
    for _ in range(n_cells):
        zeros65.append(0)
        ones65.append(1)
    zeros65.append(0)
    ones65.append(0)
    mark = list(zeros65)
    tag = 0

    prev_z = 0
    has_board = False
    cur_x = 0
    cur_y = 0

    for cycle in range(512):
        dyn = num_items(Items.Dynamite)
        if dyn >= 100000:
            quick_print("dynamite_done", True, get_time(), dyn)
            return
        found = False
        if not has_board or dyn < 20:
            clear()
            move(East)
            move(North)
            cur_x = 1
            cur_y = 1
            for _ in range(20):
                if get_ground_type() == Grounds.Dynamite:
                    found = True
                    break
                if not dig():
                    break
        else:
            fast_move(cur_x, cur_y, 3, 3, size, half)
            cur_x = 3
            cur_y = 3
            for _ in range(36):
                if get_ground_type() == Grounds.Dynamite:
                    found = True
                    break
                dz = prev_z - get_pos_z()
                if dz <= 5 or (dz >= 12 and dz <= 20):
                    use_item(Items.Dynamite)
                else:
                    if not dig():
                        break
            if not found:
                clear()
                move(East)
                move(North)
                cur_x = 1
                cur_y = 1
                for _ in range(20):
                    if get_ground_type() == Grounds.Dynamite:
                        found = True
                        break
                    if not dig():
                        break
        if not found:
            quick_print("dynamite_failed", "find", cycle)
            return
        start_cell = cur_x + cur_y * size
        depth = get_pos_z()
        prev_z = depth
        has_board = True
        dig()
        number = measure()
        if number == None:
            continue

        # state: 1=UNKNOWN, 0=SAFE/OPENED, -1=MINE (sentinel 64 = 0)
        # safe:  1=SAFE(unopened), 0=otherwise (sentinel 64 = 0)
        state = list(ones65)
        safe = list(zeros65)
        rem = list(zeros65)
        slack = list(zeros65)
        exposed = list(zeros65)
        has_act = list(zeros65)

        state[start_cell] = 0
        exposed[start_cell] = 1
        unk_total = n_cells - 1
        rem_m = total_mines
        all_safe = False
        pending = []
        active = []
        active_cnt = 0
        safe_q = []

        if not number:
            for nb in near[start_cell]:
                state[nb] = 0
                safe[nb] = 1
                exposed[nb] = 1
                unk_total -= 1
                safe_q.append(nb)
        else:
            for nb in ortho[start_cell]:
                exposed[nb] = 1
            u = len(near[start_cell])
            rem[start_cell] = number
            slack[start_cell] = u - number
            if number == u:
                pending.append(start_cell)
            else:
                active.append(start_cell)
                active_cnt = 1
                for nb in near[start_cell]:
                    has_act[nb] = 1

        cursor = start_cell

        for _ in range(256):
            while pending:
                clue = pending.pop()
                r = rem[clue]
                sl = slack[clue]
                if not r and not sl:
                    continue
                if not r:
                    slack[clue] = 0
                    for nb in near[clue]:
                        if state[nb] > 0:
                            state[nb] = 0
                            safe[nb] = 1
                            unk_total -= 1
                            safe_q.append(nb)
                            if has_act[nb]:
                                for cl in near[nb]:
                                    s2 = slack[cl]
                                    if s2:
                                        s2 -= 1
                                        slack[cl] = s2
                                        if not s2:
                                            active_cnt -= 1
                                            pending.append(cl)
                elif not sl:
                    rem[clue] = 0
                    for nb in near[clue]:
                        if state[nb] > 0:
                            state[nb] = -1
                            unk_total -= 1
                            rem_m -= 1
                            if has_act[nb]:
                                for cl in near[nb]:
                                    r2 = rem[cl]
                                    if r2:
                                        r2 -= 1
                                        rem[cl] = r2
                                        if not r2:
                                            active_cnt -= 1
                                            pending.append(cl)

            if not rem_m and not all_safe:
                all_safe = True
                pending = []
                active_cnt = 0
                for c in range(n_cells):
                    if state[c] > 0:
                        state[c] = 0
                        safe[c] = 1
                        unk_total -= 1
                        safe_q.append(c)

            c0 = o0[cursor]
            if safe[c0]:
                move(South)
                cursor = c0
            else:
                c0 = o1[cursor]
                if safe[c0]:
                    move(West)
                    cursor = c0
                else:
                    c0 = o2[cursor]
                    if safe[c0]:
                        move(East)
                        cursor = c0
                    else:
                        c0 = o3[cursor]
                        if safe[c0]:
                            move(North)
                            cursor = c0
                        else:
                            c0 = d0_c[cursor]
                            if safe[c0] and exposed[c0]:
                                move(West)
                                move(South)
                                cursor = c0
                            else:
                                c0 = d1_c[cursor]
                                if safe[c0] and exposed[c0]:
                                    move(East)
                                    move(South)
                                    cursor = c0
                                else:
                                    c0 = d2_c[cursor]
                                    if safe[c0] and exposed[c0]:
                                        move(West)
                                        move(North)
                                        cursor = c0
                                    else:
                                        c0 = d3_c[cursor]
                                        if safe[c0] and exposed[c0]:
                                            move(East)
                                            move(North)
                                            cursor = c0
                                        else:
                                            cell = -1
                                            if safe_q:
                                                cx = cx_tab[cursor]
                                                cy = cy_tab[cursor]
                                                dxrow = d8[cx]
                                                dyrow = d8[cy]
                                                best_i = -1
                                                best_sc = 999
                                                i = 0
                                                nq = len(safe_q)
                                                while i < nq:
                                                    c = safe_q[i]
                                                    if not safe[c]:
                                                        nq -= 1
                                                        safe_q[i] = safe_q[nq]
                                                        safe_q.pop()
                                                        continue
                                                    sc = dxrow[cx_tab[c]] + dyrow[cy_tab[c]]
                                                    if not exposed[c]:
                                                        sc += 5
                                                    if sc < best_sc:
                                                        best_sc = sc
                                                        best_i = i
                                                        if sc == 1:
                                                            break
                                                    i += 1
                                                if best_i >= 0:
                                                    cell = safe_q[best_i]
                                                    safe_q[best_i] = safe_q[nq - 1]
                                                    safe_q.pop()
                                                    fast_move(cx, cy, cx_tab[cell], cy_tab[cell], size, half)
                                                    cursor = cell
                                                    if not exposed[cell]:
                                                        while get_pos_z() > depth:
                                                            dig()
                                                        exposed[cell] = 1
                                            if cell < 0:
                                                if not unk_total:
                                                    break
                                                rem_mines = rem_m
                                                progressed = False
                                                if not rem_mines or rem_mines == unk_total:
                                                    if not rem_mines:
                                                        for c in range(n_cells):
                                                            if state[c] > 0:
                                                                state[c] = 0
                                                                safe[c] = 1
                                                                unk_total -= 1
                                                                safe_q.append(c)
                                                                if active_cnt:
                                                                    for cl in near[c]:
                                                                        s2 = slack[cl]
                                                                        if s2:
                                                                            s2 -= 1
                                                                            slack[cl] = s2
                                                                            if not s2:
                                                                                active_cnt -= 1
                                                                                pending.append(cl)
                                                    else:
                                                        for c in range(n_cells):
                                                            if state[c] > 0:
                                                                state[c] = -1
                                                                unk_total -= 1
                                                                rem_m -= 1
                                                                if active_cnt:
                                                                    for cl in near[c]:
                                                                        r2 = rem[cl]
                                                                        if r2:
                                                                            r2 -= 1
                                                                            rem[cl] = r2
                                                                            if not r2:
                                                                                active_cnt -= 1
                                                                                pending.append(cl)
                                                    progressed = True

                                                if not progressed:
                                                    new_act = []
                                                    u_lists = []
                                                    for cl in active:
                                                        if rem[cl] and slack[cl]:
                                                            ua = []
                                                            for nb in near[cl]:
                                                                if state[nb] > 0:
                                                                    ua.append(nb)
                                                            if ua:
                                                                new_act.append(cl)
                                                                u_lists.append(ua)
                                                    active = new_act
                                                    na = len(active)
                                                    active_cnt = na

                                                    for ia in range(na):
                                                        ca = active[ia]
                                                        if not rem[ca] or not slack[ca]:
                                                            continue
                                                        xa = cx_tab[ca]
                                                        ya = cy_tab[ca]
                                                        ra = rem[ca]
                                                        ua = u_lists[ia]
                                                        n_ua = len(ua)
                                                        ta = 0
                                                        for ib in range(ia + 1, na):
                                                            cb = active[ib]
                                                            dc = cb - ca
                                                            if dc < -18 or dc > 18:
                                                                continue
                                                            dx = cx_tab[cb] - xa
                                                            if dx < -2 or dx > 2:
                                                                continue
                                                            dy = cy_tab[cb] - ya
                                                            if dy < -2 or dy > 2:
                                                                continue
                                                            if not rem[cb] or not slack[cb]:
                                                                continue
                                                            if not ta:
                                                                tag += 1
                                                                ta = tag
                                                                for nb in ua:
                                                                    mark[nb] = ta
                                                            rb = rem[cb]
                                                            ub = u_lists[ib]
                                                            shared = 0
                                                            for nb2 in ub:
                                                                if mark[nb2] == ta:
                                                                    shared += 1
                                                            if not shared:
                                                                continue
                                                            n_only_a = n_ua - shared
                                                            n_only_b = len(ub) - shared
                                                            if not n_only_a and not n_only_b:
                                                                continue
                                                            diff = ra - rb
                                                            if diff == n_only_a or -diff == n_only_b:
                                                                only_b = []
                                                                for nb2 in ub:
                                                                    if mark[nb2] != ta:
                                                                        only_b.append(nb2)
                                                                tag += 1
                                                                tb = tag
                                                                for nb2 in ub:
                                                                    mark[nb2] = tb
                                                                only_a = []
                                                                for nb in ua:
                                                                    if mark[nb] != tb:
                                                                        only_a.append(nb)
                                                                if diff == n_only_a:
                                                                    mines_to_set = only_a
                                                                    safes_to_set = only_b
                                                                else:
                                                                    mines_to_set = only_b
                                                                    safes_to_set = only_a
                                                                for c in mines_to_set:
                                                                    if state[c] > 0:
                                                                        state[c] = -1
                                                                        unk_total -= 1
                                                                        rem_m -= 1
                                                                        for cl in near[c]:
                                                                            r2 = rem[cl]
                                                                            if r2:
                                                                                r2 -= 1
                                                                                rem[cl] = r2
                                                                                if not r2:
                                                                                    active_cnt -= 1
                                                                                    pending.append(cl)
                                                                for c in safes_to_set:
                                                                    if state[c] > 0:
                                                                        state[c] = 0
                                                                        safe[c] = 1
                                                                        unk_total -= 1
                                                                        safe_q.append(c)
                                                                        for cl in near[c]:
                                                                            s2 = slack[cl]
                                                                            if s2:
                                                                                s2 -= 1
                                                                                slack[cl] = s2
                                                                                if not s2:
                                                                                    active_cnt -= 1
                                                                                    pending.append(cl)
                                                                progressed = True
                                                                break
                                                        if progressed and (safe_q or pending):
                                                            break

                                                if progressed:
                                                    continue

                                                if unk_total <= 9 and active:
                                                    csp_cell, csp_facts = endgame_csp(active, u_lists, rem, state, n_cells, rem_mines, unk_total,
                                                                                      exposed, cx_tab[cursor], cy_tab[cursor], cx_tab, cy_tab, d8)
                                                    if csp_facts:
                                                        for c, cv in csp_facts:
                                                            if state[c] > 0:
                                                                unk_total -= 1
                                                                if cv == 1:
                                                                    state[c] = 0
                                                                    safe[c] = 1
                                                                    safe_q.append(c)
                                                                    for cl in near[c]:
                                                                        s2 = slack[cl]
                                                                        if s2:
                                                                            s2 -= 1
                                                                            slack[cl] = s2
                                                                            if not s2:
                                                                                active_cnt -= 1
                                                                                pending.append(cl)
                                                                else:
                                                                    state[c] = -1
                                                                    rem_m -= 1
                                                                    for cl in near[c]:
                                                                        r2 = rem[cl]
                                                                        if r2:
                                                                            r2 -= 1
                                                                            rem[cl] = r2
                                                                            if not r2:
                                                                                active_cnt -= 1
                                                                                pending.append(cl)
                                                        continue
                                                    best_cell = csp_cell
                                                else:
                                                    cx = cx_tab[cursor]
                                                    cy = cy_tab[cursor]
                                                    dxrow = d8[cx]
                                                    dyrow = d8[cy]
                                                    best_cell = -1
                                                    best_p = 2.0
                                                    best_d = 999
                                                    tag += 1
                                                    tf = tag
                                                    f_cnt = 0
                                                    max_r = 0
                                                    for ia in range(na):
                                                        r_a = rem[active[ia]]
                                                        if r_a > max_r:
                                                            max_r = r_a
                                                        for nb in u_lists[ia]:
                                                            if mark[nb] != tf:
                                                                mark[nb] = tf
                                                                f_cnt += 1
                                                    outside = unk_total - f_cnt
                                                    if outside > 0:
                                                        est_out_m = rem_mines - max_r
                                                        if est_out_m < 0:
                                                            est_out_m = 0
                                                        g_p = est_out_m / outside
                                                    else:
                                                        g_p = 2.0
                                                    for c in range(n_cells):
                                                        if state[c] <= 0:
                                                            continue
                                                        if mark[c] == tf:
                                                            p = 0.0
                                                            for cl in near[c]:
                                                                r2 = rem[cl]
                                                                s2 = slack[cl]
                                                                if r2 and s2:
                                                                    ratio = r2 / (r2 + s2)
                                                                    if ratio > p:
                                                                        p = ratio
                                                        else:
                                                            p = g_p
                                                        d = dxrow[cx_tab[c]] + dyrow[cy_tab[c]]
                                                        if not exposed[c]:
                                                            d += 4
                                                        if p < best_p - 0.001 or (p <= best_p + 0.001 and d < best_d):
                                                            best_p = p
                                                            best_d = d
                                                            best_cell = c

                                                if best_cell < 0:
                                                    dig()
                                                    break
                                                fast_move(cx_tab[cursor], cy_tab[cursor], cx_tab[best_cell], cy_tab[best_cell], size, half)
                                                cursor = best_cell
                                                if not exposed[best_cell]:
                                                    while get_pos_z() > depth:
                                                        dig()
                                                    exposed[best_cell] = 1
                                                dig()
                                                number = measure()
                                                if number == None:
                                                    if get_entity_type() == Entities.Dynamite:
                                                        for _ in range(200):
                                                            if get_entity_type() != Entities.Dynamite:
                                                                break
                                                    break
                                                state[best_cell] = 0
                                                unk_total -= 1
                                                if active_cnt:
                                                    for cl in near[best_cell]:
                                                        s2 = slack[cl]
                                                        if s2:
                                                            s2 -= 1
                                                            slack[cl] = s2
                                                            if not s2:
                                                                active_cnt -= 1
                                                                pending.append(cl)
                                                if not number:
                                                    for nb in near[best_cell]:
                                                        exposed[nb] = 1
                                                        if state[nb]:
                                                            state[nb] = 0
                                                            safe[nb] = 1
                                                            unk_total -= 1
                                                            safe_q.append(nb)
                                                            if active_cnt:
                                                                for cl in near[nb]:
                                                                    s2 = slack[cl]
                                                                    if s2:
                                                                        s2 -= 1
                                                                        slack[cl] = s2
                                                                        if not s2:
                                                                            active_cnt -= 1
                                                                            pending.append(cl)
                                                else:
                                                    for nb in ortho[best_cell]:
                                                        exposed[nb] = 1
                                                    r = number
                                                    u = 0
                                                    for nb in near[best_cell]:
                                                        sn = state[nb]
                                                        if sn:
                                                            if sn > 0:
                                                                u += 1
                                                            else:
                                                                r -= 1
                                                    if u:
                                                        if not r:
                                                            for nb in near[best_cell]:
                                                                if state[nb] > 0:
                                                                    state[nb] = 0
                                                                    safe[nb] = 1
                                                                    unk_total -= 1
                                                                    safe_q.append(nb)
                                                                    if active_cnt:
                                                                        for cl in near[nb]:
                                                                            s2 = slack[cl]
                                                                            if s2:
                                                                                s2 -= 1
                                                                                slack[cl] = s2
                                                                                if not s2:
                                                                                    active_cnt -= 1
                                                                                    pending.append(cl)
                                                        elif r == u:
                                                            for nb in near[best_cell]:
                                                                if state[nb] > 0:
                                                                    state[nb] = -1
                                                                    unk_total -= 1
                                                                    rem_m -= 1
                                                                    if active_cnt:
                                                                        for cl in near[nb]:
                                                                            r2 = rem[cl]
                                                                            if r2:
                                                                                r2 -= 1
                                                                                rem[cl] = r2
                                                                                if not r2:
                                                                                    active_cnt -= 1
                                                                                    pending.append(cl)
                                                        else:
                                                            rem[best_cell] = r
                                                            slack[best_cell] = u - r
                                                            active.append(best_cell)
                                                            active_cnt += 1
                                                            for nb in near[best_cell]:
                                                                if state[nb] > 0:
                                                                    has_act[nb] = 1
                                                continue

            dig()
            safe[cursor] = 0
            if all_safe:
                continue
            number = measure()
            if number == None:
                break
            if not number:
                for nb in near[cursor]:
                    exposed[nb] = 1
                    if state[nb]:
                        state[nb] = 0
                        safe[nb] = 1
                        unk_total -= 1
                        safe_q.append(nb)
                        if has_act[nb]:
                            for cl in near[nb]:
                                s2 = slack[cl]
                                if s2:
                                    s2 -= 1
                                    slack[cl] = s2
                                    if not s2:
                                        active_cnt -= 1
                                        pending.append(cl)
            else:
                for nb in ortho[cursor]:
                    exposed[nb] = 1
                r = number
                u = 0
                last_u = -1
                for nb in near[cursor]:
                    sn = state[nb]
                    if sn:
                        if sn > 0:
                            u += 1
                            last_u = nb
                        else:
                            r -= 1
                if u:
                    if u == 1:
                        if not r:
                            state[last_u] = 0
                            safe[last_u] = 1
                            unk_total -= 1
                            safe_q.append(last_u)
                            if has_act[last_u]:
                                for cl in near[last_u]:
                                    s2 = slack[cl]
                                    if s2:
                                        s2 -= 1
                                        slack[cl] = s2
                                        if not s2:
                                            active_cnt -= 1
                                            pending.append(cl)
                        else:
                            state[last_u] = -1
                            unk_total -= 1
                            rem_m -= 1
                            if has_act[last_u]:
                                for cl in near[last_u]:
                                    r2 = rem[cl]
                                    if r2:
                                        r2 -= 1
                                        rem[cl] = r2
                                        if not r2:
                                            active_cnt -= 1
                                            pending.append(cl)
                    elif not r:
                        for nb in near[cursor]:
                            if state[nb] > 0:
                                state[nb] = 0
                                safe[nb] = 1
                                unk_total -= 1
                                safe_q.append(nb)
                                if has_act[nb]:
                                    for cl in near[nb]:
                                        s2 = slack[cl]
                                        if s2:
                                            s2 -= 1
                                            slack[cl] = s2
                                            if not s2:
                                                active_cnt -= 1
                                                pending.append(cl)
                    elif r == u:
                        for nb in near[cursor]:
                            if state[nb] > 0:
                                state[nb] = -1
                                unk_total -= 1
                                rem_m -= 1
                                if has_act[nb]:
                                    for cl in near[nb]:
                                        r2 = rem[cl]
                                        if r2:
                                            r2 -= 1
                                            rem[cl] = r2
                                            if not r2:
                                                active_cnt -= 1
                                                pending.append(cl)
                    else:
                        rem[cursor] = r
                        slack[cursor] = u - r
                        active.append(cursor)
                        active_cnt += 1
                        for nb in near[cursor]:
                            if state[nb] > 0:
                                has_act[nb] = 1
        cur_x = cx_tab[cursor]
        cur_y = cy_tab[cursor]

    quick_print("dynamite_failed", "cycle_limit")


def fast_move(cx, cy, tx, ty, size, half):
    dx = (tx - cx) % size
    if dx:
        if dx <= half:
            for _ in range(dx):
                move(East)
        else:
            for _ in range(size - dx):
                move(West)
    dy = (ty - cy) % size
    if dy:
        if dy <= half:
            for _ in range(dy):
                move(North)
        else:
            for _ in range(size - dy):
                move(South)


def endgame_csp(active, u_lists, rem, state, n_cells, rem_mines, unk_total,
                exposed, cx, cy, cx_tab, cy_tab, d8):
    vars_list = []
    var_idx = {}
    for c in range(n_cells):
        if state[c] > 0:
            var_idx[c] = len(vars_list)
            vars_list.append(c)
    n_vars = len(vars_list)
    v_cons = []
    for _ in range(n_vars):
        v_cons.append([])
    c_rem = []
    c_unk = []
    for ci in range(len(active)):
        c_rem.append(rem[active[ci]])
        ua = u_lists[ci]
        c_unk.append(len(ua))
        for v in ua:
            v_cons[var_idx[v]].append(ci)
    assign = []
    hits = []
    for _ in range(n_vars):
        assign.append(0)
        hits.append(0)
    sol_count = [0]
    budget = [120]
    def dfs(i, m_used):
        if budget[0] <= 0:
            return
        budget[0] -= 1
        if m_used > rem_mines or m_used + (n_vars - i) < rem_mines:
            return
        if i == n_vars:
            sol_count[0] += 1
            for j in range(n_vars):
                if assign[j]:
                    hits[j] += 1
            return
        for val_b in (0, 1):
            ok = True
            for ci in v_cons[i]:
                c_unk[ci] -= 1
                c_rem[ci] -= val_b
                if c_rem[ci] < 0 or c_rem[ci] > c_unk[ci]:
                    ok = False
            if ok:
                assign[i] = val_b
                dfs(i + 1, m_used + val_b)
            for ci in v_cons[i]:
                c_unk[ci] += 1
                c_rem[ci] += val_b
    dfs(0, 0)
    sc = sol_count[0]
    facts = []
    if sc > 0 and budget[0] > 0:
        for j in range(n_vars):
            if not hits[j]:
                facts.append((vars_list[j], 1))
            elif hits[j] == sc:
                facts.append((vars_list[j], -1))
        if facts:
            return -1, facts
        dxrow = d8[cx]
        dyrow = d8[cy]
        best_cell = -1
        best_h = sc + 1
        best_d = 999
        for j in range(n_vars):
            h = hits[j]
            c = vars_list[j]
            d = dxrow[cx_tab[c]] + dyrow[cy_tab[c]]
            if not exposed[c]:
                d += 4
            if h < best_h or (h == best_h and d < best_d):
                best_h = h
                best_d = d
                best_cell = c
        return best_cell, facts
    return vars_list[0], facts


if __name__ == "__main__":
    lb_dynamite_single()
