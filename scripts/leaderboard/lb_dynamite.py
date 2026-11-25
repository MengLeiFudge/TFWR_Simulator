from __builtins__ import *
# 完整轮时间：尚无该版本的完整实机成绩。
# 32x32 多机扫雷：8 机并行预建表 + 异步 has_finished() 64x(4x4) 事件驱动调度
# + safe_q/clue_q 双优先级边界唤醒 + 延迟 halo 扫描 + 合法连续爆破下潜与深埋保护 + 精确 duds 阈值即时煤灰结算。

def lb_dynamite():
    size = get_world_size()
    n_cells = size * size
    total_mines = (n_cells * 135 + 500) // 1000
    half = size // 2
    max_workers = max_drones() - 1

    # Parallel 8-drone startup: each drone builds 4 rows (128 cells) + 8 tiles!
    sh = []
    for k in range(8):
        sh.append(spawn_drone(build_slice, k * 4, k * 4 + 4, size, n_cells))

    near = []
    cx_tab = []
    cy_tab = []
    o0 = []
    o1 = []
    o2 = []
    o3 = []
    tile_of = []
    wake_of = []
    tile_cells = []
    tile_halo2 = []

    for h in sh:
        s_near, s_cx, s_cy, s_o0, s_o1, s_o2, s_o3, s_tof, s_wof, s_tc, s_th = wait_for(h)
        for v in s_near:
            near.append(v)
        for v in s_cx:
            cx_tab.append(v)
        for v in s_cy:
            cy_tab.append(v)
        for v in s_o0:
            o0.append(v)
        for v in s_o1:
            o1.append(v)
        for v in s_o2:
            o2.append(v)
        for v in s_o3:
            o3.append(v)
        for v in s_tof:
            tile_of.append(v)
        for v in s_wof:
            wake_of.append(v)
        for v in s_tc:
            tile_cells.append(v)
        for v in s_th:
            tile_halo2.append(v)

    tile_of.append(-1)
    n_tiles = 64

    neg3_1025 = []
    zeros1025 = []
    for _ in range(n_cells + 1):
        neg3_1025.append(-3)
        zeros1025.append(0)
    neg3_1025[n_cells] = 0
    zeros64 = []
    for _ in range(n_tiles):
        zeros64.append(0)
    mark = list(zeros1025)
    tag = 0

    sx = 15
    sy = 15
    start_cell = sx + sy * size
    started = get_time()
    prev_z = 0
    has_board = False
    since_clear = 0
    cx = 0
    cy = 0

    for cycle in range(256):
        dyn = num_items(Items.Dynamite)
        if dyn >= 10000000:
            quick_print("dynamite_done", True, get_time(), dyn)
            return
        if get_time() - started > 24000:
            quick_print("dynamite_failed", "time_limit")
            return
        began = get_time()
        before = dyn
        found = False
        if not has_board or dyn < 20 or since_clear >= 12:
            clear()
            for _ in range(15):
                move(East)
            for _ in range(15):
                move(North)
            since_clear = 0
            cx = sx
            cy = sy
            for _ in range(24):
                if get_ground_type() == Grounds.Dynamite:
                    found = True
                    break
                if not dig():
                    break
        else:
            if cx != sx or cy != sy:
                cx, cy = move_to_xy(cx, cy, sx, sy, size, half)
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
                for _ in range(15):
                    move(East)
                for _ in range(15):
                    move(North)
                cx = sx
                cy = sy
                for _ in range(24):
                    if get_ground_type() == Grounds.Dynamite:
                        found = True
                        break
                    if not dig():
                        break
        if not found:
            quick_print("dynamite_failed", "find_stratum", cycle)
            return
        depth = get_pos_z()
        prev_z = depth
        has_board = True
        since_clear += 1
        prepared = get_time()
        dig()
        number = measure()
        if number == None:
            continue

        known = list(neg3_1025)
        # tile_dirty: 0=clean, 1=clue-only queued/pending, 2=safe/mine priority queued/pending
        tile_dirty = list(zeros64)
        tile_done = list(zeros64)
        in_flight = list(zeros64)

        safe_q = []
        clue_q = []
        if not number:
            known[start_cell] = 0
            for nb in near[start_cell]:
                known[nb] = -2
                g = tile_of[nb]
                if tile_dirty[g] < 2:
                    tile_dirty[g] = 2
                    safe_q.append(g)
        else:
            known[start_cell] = number
            g = tile_of[start_cell]
            tile_dirty[g] = 2
            safe_q.append(g)

        cx = sx
        cy = sy
        running = []
        spawns = 0
        done_cnt = 0
        settling = False
        board_status = "running"

        for tick_iter in range(6000):
            if not settling:
                while safe_q and len(running) < max_workers:
                    g = safe_q.pop(0)
                    if tile_done[g] or in_flight[g]:
                        continue
                    tile_dirty[g] = 0
                    h = spawn_drone(work_tile, g, tile_cells[g], tile_halo2[g], known, near, tile_of, wake_of, cx_tab, cy_tab, o0, o1, o2, o3, size, half, depth, cx, cy)
                    if h == None:
                        tile_dirty[g] = 2
                        safe_q.insert(0, g)
                        break
                    in_flight[g] = 1
                    running.append((g, h))
                    spawns += 1

                if not safe_q and clue_q and len(running) < 16:
                    while clue_q and len(running) < 16:
                        g = clue_q.pop(0)
                        if tile_done[g] or in_flight[g] or not tile_dirty[g]:
                            continue
                        tile_dirty[g] = 0
                        h = spawn_drone(work_tile, g, tile_cells[g], tile_halo2[g], known, near, tile_of, wake_of, cx_tab, cy_tab, o0, o1, o2, o3, size, half, depth, cx, cy)
                        if h == None:
                            tile_dirty[g] = 1
                            clue_q.insert(0, g)
                            break
                        in_flight[g] = 1
                        running.append((g, h))
                        spawns += 1

            if running:
                got_any = False
                i = 0
                nr = len(running)
                while i < nr:
                    g, h = running[i]
                    if has_finished(h):
                        got_any = True
                        nr -= 1
                        running[i] = running[nr]
                        running.pop()
                        in_flight[g] = 0
                        w_g, w_state, updates, prio_touched, clue_touched, is_done = wait_for(h)
                        if w_state == "ended":
                            board_status = "ended"
                            settling = True
                        if is_done and not tile_done[w_g]:
                            tile_done[w_g] = 1
                            done_cnt += 1
                        if updates:
                            for c in updates:
                                ov = known[c]
                                if ov:
                                    nv = updates[c]
                                    if not nv or nv > ov:
                                        known[c] = nv
                            if not settling:
                                if prio_touched:
                                    for nti in prio_touched:
                                        if not tile_done[nti] and tile_dirty[nti] < 2:
                                            tile_dirty[nti] = 2
                                            if not in_flight[nti]:
                                                safe_q.append(nti)
                                if clue_touched:
                                    for nti in clue_touched:
                                        if not tile_done[nti] and not tile_dirty[nti]:
                                            tile_dirty[nti] = 1
                                            if not in_flight[nti]:
                                                clue_q.append(nti)
                        if not settling and not tile_done[w_g]:
                            td = tile_dirty[w_g]
                            if td == 2:
                                safe_q.append(w_g)
                            elif td == 1:
                                clue_q.append(w_g)
                    else:
                        i += 1

                if got_any:
                    if not settling:
                        duds_dyn = num_items(Items.Dynamite) - before
                        if duds_dyn >= 13840 or done_cnt >= 62:
                            settling = True
                    continue

                for _ in range(28):
                    pass
                continue

            if board_status != "running" or settling:
                break
            if safe_q or clue_q:
                continue

            duds_dyn = num_items(Items.Dynamite) - before
            if duds_dyn >= 12160 or done_cnt >= 52:
                board_status = "stalled"
                break

            active_clues = []
            unk_total = 0
            mine_count = 0
            for c in range(n_cells):
                kv = known[c]
                if kv > 0:
                    active_clues.append(c)
                elif kv == -3:
                    unk_total += 1
                elif kv == -1:
                    mine_count += 1
                elif kv == -2:
                    g = tile_of[c]
                    if tile_done[g]:
                        tile_done[g] = 0
                        done_cnt -= 1
                    if tile_dirty[g] < 2:
                        tile_dirty[g] = 2
                        safe_q.append(g)

            if safe_q:
                continue
            if unk_total <= 55:
                board_status = "stalled"
                break
            rem_mines = total_mines - mine_count
            if not rem_mines or rem_mines == unk_total:
                board_status = "stalled"
                break

            p_u, tag, done_cnt = global_solve_step(known, active_clues, near, tile_of, tile_dirty, tile_done, safe_q, done_cnt, mark, tag)
            if p_u:
                continue

            guess_cell = pick_guess(known, active_clues, near, n_cells, rem_mines, unk_total, cx, cy, cx_tab, cy_tab, size, half, mark, tag)
            tag += 1
            if guess_cell < 0:
                board_status = "stalled"
                break
            cx, cy = move_to_xy(cx, cy, cx_tab[guess_cell], cy_tab[guess_cell], size, half)
            if get_pos_z() - depth > 30:
                board_status = "stalled"
                break
            while get_pos_z() > depth:
                dig()
            dig()
            gnum = measure()
            if gnum == None:
                if get_entity_type() == Entities.Dynamite:
                    for _ in range(200):
                        if get_entity_type() != Entities.Dynamite:
                            break
                board_status = "ended"
                break
            if not gnum:
                known[guess_cell] = 0
                for nb in near[guess_cell]:
                    if known[nb] == -3:
                        known[nb] = -2
                        g = tile_of[nb]
                        if tile_done[g]:
                            tile_done[g] = 0
                            done_cnt -= 1
                        if tile_dirty[g] < 2:
                            tile_dirty[g] = 2
                            safe_q.append(g)
            else:
                known[guess_cell] = gnum
                gti = tile_of[guess_cell]
                if tile_done[gti]:
                    tile_done[gti] = 0
                    done_cnt -= 1
                if tile_dirty[gti] < 2:
                    tile_dirty[gti] = 2
                    safe_q.append(gti)
                wt = wake_of[guess_cell]
                if wt:
                    for nti in wt:
                        if not tile_done[nti] and not tile_dirty[nti]:
                            tile_dirty[nti] = 1
                            clue_q.append(nti)

        for g, h in running:
            wait_for(h)

        if board_status != "ended":
            if get_ground_type() == Grounds.Soot and measure() != None:
                dig()
            else:
                cx, cy = move_to_xy(cx, cy, sx, sy, size, half)
                if get_ground_type() == Grounds.Soot and measure() != None:
                    dig()
            board_status = "ended"

        if board_status != "ended":
            return
    quick_print("dynamite_failed", "cycle_limit")


def build_slice(y0, y1, size, n_cells):
    s_near = []
    s_cx = []
    s_cy = []
    s_o0 = []
    s_o1 = []
    s_o2 = []
    s_o3 = []
    s_tof = []
    s_wof = []
    s_tc = []
    s_th = []
    ty = y0 // 4
    for tx in range(8):
        tx0 = tx * 4
        tx1 = tx0 + 4
        tc = []
        for y in range(y0, y1):
            ro = y * size
            for x in range(tx0, tx1):
                tc.append(x + ro)
        s_tc.append(tc)
        hx0 = tx0 - 2
        if hx0 < 0:
            hx0 = 0
        hx1 = tx1 + 2
        if hx1 > size:
            hx1 = size
        hy0 = y0 - 2
        if hy0 < 0:
            hy0 = 0
        hy1 = y1 + 2
        if hy1 > size:
            hy1 = size
        hc = []
        for y in range(hy0, hy1):
            ro = y * size
            for x in range(hx0, hx1):
                hc.append(x + ro)
        s_th.append(hc)

    for y in range(y0, y1):
        ro = y * size
        by = y % 4
        dy_t = 0
        if by == 0 and ty > 0:
            dy_t = -8
        elif by == 3 and ty < 7:
            dy_t = 8
        for x in range(size):
            c = x + ro
            s_cx.append(x)
            s_cy.append(y)
            tx = x // 4
            g = tx + ty * 8
            s_tof.append(g)
            nb = []
            if y > 0:
                if x > 0:
                    nb.append(c - size - 1)
                nb.append(c - size)
                s_o0.append(c - size)
                if x + 1 < size:
                    nb.append(c - size + 1)
            else:
                s_o0.append(n_cells)
            if x > 0:
                nb.append(c - 1)
                s_o1.append(c - 1)
            else:
                s_o1.append(n_cells)
            if x + 1 < size:
                nb.append(c + 1)
                s_o2.append(c + 1)
            else:
                s_o2.append(n_cells)
            if y + 1 < size:
                if x > 0:
                    nb.append(c + size - 1)
                nb.append(c + size)
                s_o3.append(c + size)
                if x + 1 < size:
                    nb.append(c + size + 1)
            else:
                s_o3.append(n_cells)
            s_near.append(nb)

            bx = x % 4
            dx_t = 0
            if bx == 0 and tx > 0:
                dx_t = -1
            elif bx == 3 and tx < 7:
                dx_t = 1
            if dx_t and dy_t:
                s_wof.append((g + dx_t, g + dy_t, g + dx_t + dy_t))
            elif dx_t:
                s_wof.append((g + dx_t,))
            elif dy_t:
                s_wof.append((g + dy_t,))
            else:
                s_wof.append(None)
    return s_near, s_cx, s_cy, s_o0, s_o1, s_o2, s_o3, s_tof, s_wof, s_tc, s_th


def work_tile(g, my_cells, halo_cells, known, near, tile_of, wake_of, cx_tab, cy_tab, o0, o1, o2, o3, size, half, depth, cx, cy):
    updates = {}
    prio_touched = set()
    clue_touched = set()
    targets = []
    for c in my_cells:
        if known[c] == -2:
            targets.append(c)

    rem = {}
    slack = {}
    pending = []
    halo_scanned = False

    cursor = cx + cy * size
    in_tile = False

    for step in range(48):
        while pending:
            cl = pending.pop()
            r = rem[cl]
            sl = slack[cl]
            if not r and not sl:
                continue
            known[cl] = 0
            updates[cl] = 0
            if not r:
                slack[cl] = 0
                for nb in near[cl]:
                    if known[nb] == -3:
                        known[nb] = -2
                        updates[nb] = -2
                        nti = tile_of[nb]
                        if nti == g:
                            targets.append(nb)
                        else:
                            prio_touched.add(nti)
                        if slack:
                            for cl2 in near[nb]:
                                if cl2 in slack:
                                    s2 = slack[cl2]
                                    if s2:
                                        s2 -= 1
                                        slack[cl2] = s2
                                        if not s2:
                                            pending.append(cl2)
            elif not sl:
                rem[cl] = 0
                for nb in near[cl]:
                    if known[nb] == -3:
                        known[nb] = -1
                        updates[nb] = -1
                        nti = tile_of[nb]
                        if nti != g:
                            prio_touched.add(nti)
                        wt = wake_of[nb]
                        if wt:
                            for nti2 in wt:
                                if nti2 != g:
                                    prio_touched.add(nti2)
                        if rem:
                            for cl2 in near[nb]:
                                if cl2 in rem:
                                    r2 = rem[cl2]
                                    if r2:
                                        r2 -= 1
                                        rem[cl2] = r2
                                        if not r2:
                                            pending.append(cl2)

        if not targets:
            is_done = True
            for c in my_cells:
                if known[c] < -1:
                    is_done = False
                    break
            if is_done:
                return g, "running", updates, prio_touched, clue_touched, True

            if not halo_scanned:
                halo_scanned = True
                for c in halo_cells:
                    v = known[c]
                    if v > 0:
                        r = v
                        u = 0
                        for nb in near[c]:
                            kn = known[nb]
                            if kn < 0:
                                if kn == -3:
                                    u += 1
                                elif kn == -1:
                                    r -= 1
                        if not u:
                            known[c] = 0
                            updates[c] = 0
                        elif not r or r == u:
                            rem[c] = r
                            slack[c] = u - r
                            pending.append(c)
                        else:
                            rem[c] = r
                            slack[c] = u - r
                if pending:
                    continue

            if len(rem) >= 2:
                c_u = {}
                c_r = {}
                for cl in rem:
                    r = rem[cl]
                    if r and slack[cl]:
                        ua = set()
                        for nb in near[cl]:
                            if known[nb] == -3:
                                ua.add(nb)
                        if ua:
                            c_u[cl] = ua
                            c_r[cl] = r
                diff_prog = False
                for ca in c_u:
                    ua = c_u[ca]
                    ra = c_r[ca]
                    for cb in near[ca]:
                        if cb <= ca or cb not in c_u:
                            continue
                        ub = c_u[cb]
                        rb = c_r[cb]
                        only_a = []
                        for nb in ua:
                            if nb not in ub:
                                only_a.append(nb)
                        only_b = []
                        for nb in ub:
                            if nb not in ua:
                                only_b.append(nb)
                        if not only_a and not only_b:
                            continue
                        diff = ra - rb
                        if diff == len(only_a) or -diff == len(only_b):
                            if diff == len(only_a):
                                ms = only_a
                                ss = only_b
                            else:
                                ms = only_b
                                ss = only_a
                            for c in ms:
                                if known[c] == -3:
                                    known[c] = -1
                                    updates[c] = -1
                                    diff_prog = True
                                    nti = tile_of[c]
                                    if nti != g:
                                        prio_touched.add(nti)
                                    wt = wake_of[c]
                                    if wt:
                                        for nti2 in wt:
                                            if nti2 != g:
                                                prio_touched.add(nti2)
                                    for cl2 in near[c]:
                                        if cl2 in rem:
                                            r2 = rem[cl2]
                                            if r2:
                                                r2 -= 1
                                                rem[cl2] = r2
                                                if not r2:
                                                    pending.append(cl2)
                            for c in ss:
                                if known[c] == -3:
                                    known[c] = -2
                                    updates[c] = -2
                                    diff_prog = True
                                    nti = tile_of[c]
                                    if nti == g:
                                        targets.append(c)
                                    else:
                                        prio_touched.add(nti)
                                    for cl2 in near[c]:
                                        if cl2 in slack:
                                            s2 = slack[cl2]
                                            if s2:
                                                s2 -= 1
                                                slack[cl2] = s2
                                                if not s2:
                                                    pending.append(cl2)
                if diff_prog:
                    continue
            break

        while targets:
            cell = -1
            if in_tile:
                c0 = o0[cursor]
                if known[c0] == -2 and tile_of[c0] == g:
                    move(South)
                    cell = c0
                    cy -= 1
                else:
                    c0 = o1[cursor]
                    if known[c0] == -2 and tile_of[c0] == g:
                        move(West)
                        cell = c0
                        cx -= 1
                    else:
                        c0 = o2[cursor]
                        if known[c0] == -2 and tile_of[c0] == g:
                            move(East)
                            cell = c0
                            cx += 1
                        else:
                            c0 = o3[cursor]
                            if known[c0] == -2 and tile_of[c0] == g:
                                move(North)
                                cell = c0
                                cy += 1

            if cell < 0:
                best_i = -1
                best_sc = 999
                i = 0
                nt = len(targets)
                while i < nt:
                    c = targets[i]
                    if known[c] != -2:
                        nt -= 1
                        targets[i] = targets[nt]
                        targets.pop()
                        continue
                    if in_tile:
                        dx = cx_tab[c] - cx
                        if dx < 0:
                            dx = -dx
                        dy = cy_tab[c] - cy
                        if dy < 0:
                            dy = -dy
                    else:
                        dx = (cx_tab[c] - cx) % size
                        if dx > half:
                            dx = size - dx
                        dy = (cy_tab[c] - cy) % size
                        if dy > half:
                            dy = size - dy
                    sc = dx + dy
                    if sc < best_sc:
                        best_sc = sc
                        best_i = i
                        if sc == 1:
                            break
                    i += 1
                if best_i < 0:
                    break
                cell = targets[best_i]
                targets[best_i] = targets[len(targets) - 1]
                targets.pop()
                need = False
                for nb in near[cell]:
                    kv = known[nb]
                    if kv == -3 or kv == -1:
                        need = True
                        break
                if not need:
                    known[cell] = 0
                    updates[cell] = 0
                    continue
                cx, cy = move_to_xy(cx, cy, cx_tab[cell], cy_tab[cell], size, half)
                in_tile = True
                if get_pos_z() - depth > 30:
                    known[cell] = 0
                    updates[cell] = 0
                    continue
                while get_pos_z() > depth:
                    dig()

            cursor = cell
            dig()
            number = measure()
            if number == None:
                return g, "ended", updates, prio_touched, clue_touched, True
            if not number:
                known[cell] = 0
                updates[cell] = 0
                for nb in near[cell]:
                    if known[nb] == -3:
                        known[nb] = -2
                        updates[nb] = -2
                        nti = tile_of[nb]
                        if nti == g:
                            targets.append(nb)
                        else:
                            prio_touched.add(nti)
                        if slack:
                            for cl2 in near[nb]:
                                if cl2 in slack:
                                    s2 = slack[cl2]
                                    if s2:
                                        s2 -= 1
                                        slack[cl2] = s2
                                        if not s2:
                                            pending.append(cl2)
            else:
                known[cell] = number
                updates[cell] = number
                wt = wake_of[cell]
                if wt:
                    for nti in wt:
                        clue_touched.add(nti)
                r = number
                u = 0
                last_u = -1
                for nb in near[cell]:
                    kn = known[nb]
                    if kn < 0:
                        if kn == -3:
                            u += 1
                            last_u = nb
                        elif kn == -1:
                            r -= 1
                if not u:
                    known[cell] = 0
                    updates[cell] = 0
                elif u == 1:
                    known[cell] = 0
                    updates[cell] = 0
                    if not r:
                        known[last_u] = -2
                        updates[last_u] = -2
                        nti = tile_of[last_u]
                        if nti == g:
                            targets.append(last_u)
                        else:
                            prio_touched.add(nti)
                        if slack:
                            for cl2 in near[last_u]:
                                if cl2 in slack:
                                    s2 = slack[cl2]
                                    if s2:
                                        s2 -= 1
                                        slack[cl2] = s2
                                        if not s2:
                                            pending.append(cl2)
                    else:
                        known[last_u] = -1
                        updates[last_u] = -1
                        nti = tile_of[last_u]
                        if nti != g:
                            prio_touched.add(nti)
                        wt2 = wake_of[last_u]
                        if wt2:
                            for nti2 in wt2:
                                if nti2 != g:
                                    prio_touched.add(nti2)
                        if rem:
                            for cl2 in near[last_u]:
                                if cl2 in rem:
                                    r2 = rem[cl2]
                                    if r2:
                                        r2 -= 1
                                        rem[cl2] = r2
                                        if not r2:
                                            pending.append(cl2)
                elif not r:
                    known[cell] = 0
                    updates[cell] = 0
                    for nb in near[cell]:
                        if known[nb] == -3:
                            known[nb] = -2
                            updates[nb] = -2
                            nti = tile_of[nb]
                            if nti == g:
                                targets.append(nb)
                            else:
                                prio_touched.add(nti)
                            if slack:
                                for cl2 in near[nb]:
                                    if cl2 in slack:
                                        s2 = slack[cl2]
                                        if s2:
                                            s2 -= 1
                                            slack[cl2] = s2
                                            if not s2:
                                                pending.append(cl2)
                elif r == u:
                    known[cell] = 0
                    updates[cell] = 0
                    for nb in near[cell]:
                        if known[nb] == -3:
                            known[nb] = -1
                            updates[nb] = -1
                            nti = tile_of[nb]
                            if nti != g:
                                prio_touched.add(nti)
                            wt2 = wake_of[nb]
                            if wt2:
                                for nti2 in wt2:
                                    if nti2 != g:
                                        prio_touched.add(nti2)
                            if rem:
                                for cl2 in near[nb]:
                                    if cl2 in rem:
                                        r2 = rem[cl2]
                                        if r2:
                                            r2 -= 1
                                            rem[cl2] = r2
                                            if not r2:
                                                pending.append(cl2)
                else:
                    rem[cell] = r
                    slack[cell] = u - r
                if pending:
                    break

    is_done = True
    for c in my_cells:
        if known[c] < -1:
            is_done = False
            break
    return g, "running", updates, prio_touched, clue_touched, is_done


def global_solve_step(known, active_clues, near, tile_of, tile_dirty, tile_done, safe_q, done_cnt, mark, tag):
    c_u = []
    c_r = []
    prog = 0
    for cl in active_clues:
        r = known[cl]
        ua = []
        for nb in near[cl]:
            kn = known[nb]
            if kn == -3:
                ua.append(nb)
            elif kn == -1:
                r -= 1
        nu = len(ua)
        if not nu:
            known[cl] = 0
        elif not r:
            known[cl] = 0
            for nb in ua:
                if known[nb] == -3:
                    known[nb] = -2
                    prog += 1
                    g = tile_of[nb]
                    if tile_done[g]:
                        tile_done[g] = 0
                        done_cnt -= 1
                    if tile_dirty[g] < 2:
                        tile_dirty[g] = 2
                        safe_q.append(g)
        elif r == nu:
            known[cl] = 0
            for nb in ua:
                if known[nb] == -3:
                    known[nb] = -1
                    prog += 1
                    for nb2 in near[nb]:
                        g = tile_of[nb2]
                        if not tile_done[g] and tile_dirty[g] < 2:
                            tile_dirty[g] = 2
                            safe_q.append(g)
        else:
            c_u.append(ua)
            c_r.append(r)
    if prog:
        return prog, tag, done_cnt

    na = len(c_u)
    for ia in range(na):
        ua = c_u[ia]
        ra = c_r[ia]
        n_ua = len(ua)
        tag += 1
        ta = tag
        for nb in ua:
            mark[nb] = ta
        for ib in range(ia + 1, na):
            ub = c_u[ib]
            shared = 0
            for nb in ub:
                if mark[nb] == ta:
                    shared += 1
            if not shared:
                continue
            n_oa = n_ua - shared
            n_ob = len(ub) - shared
            if not n_oa and not n_ob:
                continue
            diff = ra - c_r[ib]
            if diff == n_oa or -diff == n_ob:
                only_a = []
                for nb in ua:
                    if nb not in ub:
                        only_a.append(nb)
                only_b = []
                for nb in ub:
                    if mark[nb] != ta:
                        only_b.append(nb)
                if diff == n_oa:
                    ms = only_a
                    ss = only_b
                else:
                    ms = only_b
                    ss = only_a
                for c in ms:
                    if known[c] == -3:
                        known[c] = -1
                        prog += 1
                        for nb2 in near[c]:
                            g = tile_of[nb2]
                            if not tile_done[g] and tile_dirty[g] < 2:
                                tile_dirty[g] = 2
                                safe_q.append(g)
                for c in ss:
                    if known[c] == -3:
                        known[c] = -2
                        prog += 1
                        g = tile_of[c]
                        if tile_done[g]:
                            tile_done[g] = 0
                            done_cnt -= 1
                        if tile_dirty[g] < 2:
                            tile_dirty[g] = 2
                            safe_q.append(g)
                if prog >= 6:
                    return prog, tag, done_cnt
    return prog, tag, done_cnt


def pick_guess(known, active_clues, near, n_cells, rem_mines, unk_total, cx, cy, cx_tab, cy_tab, size, half, mark, tag):
    tf = tag + 1
    f_cnt = 0
    max_r = 0
    best_p = 2.0
    best_d = 999
    best_c = -1
    clue_p = {}
    for cl in active_clues:
        r = known[cl]
        u = 0
        for nb in near[cl]:
            kn = known[nb]
            if kn == -3:
                u += 1
                if mark[nb] != tf:
                    mark[nb] = tf
                    f_cnt += 1
            elif kn == -1:
                r -= 1
        if u > 0 and r > 0:
            if r > max_r:
                max_r = r
            clue_p[cl] = r / u

    outside = unk_total - f_cnt
    if outside > 0:
        est_m = rem_mines - max_r
        if est_m < 0:
            est_m = 0
        g_p = est_m / outside
    else:
        g_p = 2.0

    for c in range(n_cells):
        if known[c] != -3:
            continue
        if mark[c] == tf:
            p = 0.0
            for cl in near[c]:
                if cl in clue_p:
                    cp = clue_p[cl]
                    if cp > p:
                        p = cp
        else:
            p = g_p
        dx = (cx_tab[c] - cx) % size
        if dx > half:
            dx = size - dx
        dy = (cy_tab[c] - cy) % size
        if dy > half:
            dy = size - dy
        d = dx + dy
        if p < best_p - 0.001 or (p <= best_p + 0.001 and d < best_d):
            best_p = p
            best_d = d
            best_c = c
    return best_c


def move_to_xy(cx, cy, tx, ty, size, half):
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
    return tx, ty


if __name__ == "__main__":
    lb_dynamite()
