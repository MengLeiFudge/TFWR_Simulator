from __builtins__ import *
# 完整轮时间：本版尚未实机；本地默认随机完整验收结果见同名策略文档。


def lb_pyramids():
    # 先用两座 5×5 浅层塔快速获得 ~200 Power 开启 2× 全速（约 5.5s，且首座大塔不断电）
    if num_items(Items.Power) < 150:
        pyramid_fast_unlock_power(150)

    # 30×30 世界消除 32×32 下 W=31 溢出回退，同时规避 29×29 下 TryPlaceRandomly 的 size2==size 缺陷，完整解锁 29×29（3364 Power）
    set_world_size(30)
    Dirt = Grounds.Dirt
    Sand = Grounds.Sand
    Limestone = Grounds.Limestone
    Sunflower = Entities.Sunflower
    Power = Items.Power
    E = East
    W = West
    N = North
    S = South

    w_min = 21
    clear_every_towers = 20
    towers = 0
    since_clear = 0
    need_clear = True
    chunk_top = 0

    while num_items(Power) < 150000:
        # 16 机并行竖井按 chunk 下探定位（~0.21s/chunk），每 20 塔清一次控制深度
        hit = False
        while not hit:
            if need_clear or chunk_top <= -2400:
                clear()
                chunk_top = 0
                since_clear = 0
                for _ in range(14):
                    move(E)
                for _ in range(14):
                    move(N)
                need_clear = False
            else:
                pyramid_move_30(14, 14)
                delta = get_pos_z() - chunk_top
                if delta > 0:
                    pyramid_shaft_dig(delta)
            # 在 (14,14) 最多挖 1 块岩体（遇 Dirt 顺挖至多 2 块）筛中大型浅塔
            for d_i in range(2):
                g = get_ground_type()
                if g == Sand:
                    hit = True
                    break
                if g == Limestone:
                    break
                if d_i == 1:
                    if g == Dirt:
                        dig()
                        g2 = get_ground_type()
                        if g2 == Sand:
                            hit = True
                        elif g2 == Dirt:
                            dig()
                            if get_ground_type() == Sand:
                                hit = True
                    break
                dig()
            if not hit:
                chunk_top -= 16

        z_center = get_pos_z()
        chunk_bot = chunk_top - 15

        # 阶段一：4 机并行十字射线定位 (x0, x1, y0, y1, floor) 并为偶环清土建立多米诺起点
        h_e = spawn_drone(pyramid_ray_probe, 14, 14, z_center, 1, 0, E, chunk_bot)
        h_w = spawn_drone(pyramid_ray_probe, 14, 14, z_center, -1, 0, W, chunk_bot)
        h_n = spawn_drone(pyramid_ray_probe, 14, 14, z_center, 0, 1, N, chunk_bot)
        h_s = spawn_drone(pyramid_ray_probe, 14, 14, z_center, 0, -1, S, chunk_bot)
        res_e = wait_for(h_e)
        res_w = wait_for(h_w)
        res_n = wait_for(h_n)
        res_s = wait_for(h_s)

        x1 = res_e[0]
        x0 = res_w[0]
        y1 = res_n[0]
        y0 = res_s[0]
        width = x1 - x0 + 1
        height_y = y1 - y0 + 1
        ok_bounds = (width == height_y and width >= w_min and width % 2 == 1)
        floor = chunk_bot
        if ok_bounds:
            d_c = min(14 - x0, x1 - 14, 14 - y0, y1 - 14)
            floor = z_center - 1 - d_c
            if floor < chunk_bot or floor > chunk_top - 3:
                ok_bounds = False
        if ok_bounds:
            for rx, ry, rz in [res_e[1], res_w[1], res_n[1], res_s[1]]:
                if rx >= 0:
                    if rz != floor + 1 + min(rx - x0, x1 - rx, ry - y0, y1 - ry):
                        ok_bounds = False
        if not ok_bounds:
            chunk_top -= 16
            continue

        H = width // 2 + 1
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        ray_eroded = []
        for lst in [res_e[2], res_w[2], res_n[2], res_s[2]]:
            for cell in lst:
                ray_eroded.append(cell)

        # 阶段二：32 机八分偶环多米诺防塌清土 + 1t 向内窥视奇环，零二次全扫描
        tasks = pyramid_build_octant_tasks(x0, x1, y0, y1, floor, H)
        eroded_all = pyramid_dispatch_rings(tasks)
        for cell in ray_eroded:
            eroded_all.append(cell)

        # 阶段三：去重缺柱 + 挖缺柱与并行 2-Lipschitz 塌方锥计算重叠 + 锥内等块权持久化分层修复
        seen = {}
        true_eroded = []
        for ex, ey in eroded_all:
            if ex >= x0 and ex <= x1 and ey >= y0 and ey <= y1:
                k = ex * 32 + ey
                if k not in seen:
                    seen[k] = True
                    true_eroded.append((ex, ey))

        pyramid_move_30(cx, cy)
        if get_entity_type() != Sunflower:
            tz_c = floor + H
            while get_pos_z() > tz_c:
                dig()
            if get_ground_type() != Sand:
                k_c = cx * 32 + cy
                if k_c not in seen:
                    seen[k_c] = True
                    true_eroded.append((cx, cy))

        if get_entity_type() != Sunflower:
            n_er = len(true_eroded)
            if n_er > 0:
                h_dig = spawn_drone(pyramid_dispatch_dig_eroded, true_eroded, floor)
                cone_lists = pyramid_dispatch_compute_cones(true_eroded, x0, x1, y0, y1, H)
                affected = {}
                n_cl = len(cone_lists)
                for c_id in range(n_cl):
                    for px, py, d2, h_cell in cone_lists[c_id]:
                        k = px * 32 + py
                        if k not in affected or d2 < affected[k][0]:
                            affected[k] = (d2, h_cell, px, py, c_id)

                cone_cols = []
                cone_weights = []
                for _ in range(n_cl):
                    cone_cols.append([])
                    cone_weights.append(0)
                layer_counts = []
                for _ in range(H + 1):
                    layer_counts.append(0)
                total_needed = 0
                apex_missing_top = False
                for k in affected:
                    d2, h_cell, px, py, c_id = affected[k]
                    h_cur = d2
                    if h_cur == 0:
                        h_cur = 1
                    if h_cur < h_cell:
                        top_worker = h_cell
                        if px == cx and py == cy and top_worker == H:
                            top_worker = H - 1
                            apex_missing_top = True
                        if h_cur < top_worker:
                            span = top_worker - h_cur
                            cone_cols[c_id].append((px, py, h_cur, top_worker, span))
                            cone_weights[c_id] += span
                            L = h_cur + 1
                            while L <= top_worker:
                                layer_counts[L] += 1
                                total_needed += 1
                                L += 1

                if h_dig != None:
                    wait_for(h_dig)

                extra_req = total_needed + 2
                if apex_missing_top:
                    extra_req += 1
                if num_items(Items.Block) < extra_req:
                    pyramid_mine_extra_blocks(x0, x1, y0, y1, floor, extra_req)
                    pyramid_move_30(cx, cy)

                active_layers = []
                thresholds = []
                rem_block = num_items(Items.Block)
                for L in range(2, H):
                    c = layer_counts[L]
                    if c > 0:
                        rem_block -= c
                        active_layers.append(L)
                        thresholds.append(rem_block)

                non_empty = []
                ne_weights = []
                total_cols = 0
                total_w = 0
                for c_id in range(n_cl):
                    cols = cone_cols[c_id]
                    if len(cols) > 0:
                        non_empty.append(cols)
                        ne_weights.append(cone_weights[c_id])
                        total_cols += len(cols)
                        total_w += cone_weights[c_id]

                if len(active_layers) > 0 and total_cols > 0:
                    worker_jobs = []
                    n_cones = len(non_empty)
                    budget = 31
                    if total_cols <= budget:
                        for cols in non_empty:
                            for px, py, hc, ht, sp in cols:
                                worker_jobs.append([(px, py, hc, ht)])
                    else:
                        alloc = []
                        used = 0
                        for ci in range(n_cones):
                            w = (ne_weights[ci] * budget) // total_w
                            if w < 1:
                                w = 1
                            if w > len(non_empty[ci]):
                                w = len(non_empty[ci])
                            alloc.append(w)
                            used += w
                        while used < budget:
                            best_c = -1
                            best_ratio = 0.0
                            for ci in range(n_cones):
                                if alloc[ci] < len(non_empty[ci]):
                                    rv = ne_weights[ci] / alloc[ci]
                                    if rv > best_ratio:
                                        best_ratio = rv
                                        best_c = ci
                            if best_c < 0:
                                break
                            alloc[best_c] += 1
                            used += 1
                        while used > budget:
                            best_c = -1
                            best_w = 1
                            for ci in range(n_cones):
                                if alloc[ci] > best_w:
                                    best_w = alloc[ci]
                                    best_c = ci
                            if best_c < 0:
                                break
                            alloc[best_c] -= 1
                            used -= 1
                        for ci in range(n_cones):
                            cols = non_empty[ci]
                            nw = alloc[ci]
                            nc = len(cols)
                            if nw >= nc:
                                for px, py, hc, ht, sp in cols:
                                    worker_jobs.append([(px, py, hc, ht)])
                            else:
                                for i in range(1, nc):
                                    v = cols[i]
                                    vk = v[0] * 32 + v[1]
                                    j = i - 1
                                    while j >= 0 and (cols[j][0] * 32 + cols[j][1]) > vk:
                                        cols[j + 1] = cols[j]
                                        j -= 1
                                    cols[j + 1] = v
                                rem_w = ne_weights[ci]
                                idx = 0
                                for wi in range(nw):
                                    rem_workers = nw - wi
                                    target_w = rem_w / rem_workers
                                    bkt = []
                                    cur_w = 0
                                    max_idx = nc - (rem_workers - 1)
                                    while idx < max_idx:
                                        px, py, hc, ht, sp = cols[idx]
                                        if len(bkt) > 0 and cur_w + sp > target_w and cur_w >= target_w * 0.65:
                                            break
                                        bkt.append((px, py, hc, ht))
                                        cur_w += sp
                                        idx += 1
                                        if wi + 1 < nw and cur_w >= target_w:
                                            break
                                    if wi + 1 == nw:
                                        while idx < nc:
                                            px, py, hc, ht, sp = cols[idx]
                                            bkt.append((px, py, hc, ht))
                                            cur_w += sp
                                            idx += 1
                                    rem_w -= cur_w
                                    worker_jobs.append(bkt)

                    deadline = get_time() + 60
                    h_rep = spawn_drone(pyramid_dispatch_repair, worker_jobs, floor, active_layers, thresholds, deadline)
                    if h_rep == None:
                        pyramid_dispatch_repair(worker_jobs, floor, active_layers, thresholds, deadline)
                    else:
                        wait_for(h_rep)
                pyramid_move_30(cx, cy)
                if apex_missing_top and get_entity_type() != Sunflower:
                    place(Sand)

        if get_entity_type() != Sunflower:
            quick_print("pyramids_retry", towers, width, floor)
            need_clear = True
            continue
        harvest()
        towers += 1
        since_clear += 1
        if since_clear >= clear_every_towers:
            need_clear = True
        else:
            chunk_top -= 16

    quick_print("pyramids_done", True, towers, get_time(), num_items(Power))


def pyramid_shaft_dig(n):
    if n <= 0:
        return
    if n == 1:
        dig()
        return
    m = n // 2
    h = spawn_drone(pyramid_shaft_dig, n - m)
    pyramid_shaft_dig(m)
    if h == None:
        pyramid_shaft_dig(n - m)
    else:
        wait_for(h)


def pyramid_dispatch_dig_eroded(eroded, floor):
    n = len(eroded)
    if n == 1:
        ex, ey = eroded[0]
        pyramid_move_30(ex, ey)
        while get_pos_z() > floor:
            dig()
        if get_pos_z() == floor:
            place(Grounds.Sand)
        return True
    mid = n // 2
    right_slice = []
    for i in range(mid, n):
        right_slice.append(eroded[i])
    left_slice = []
    for i in range(mid):
        left_slice.append(eroded[i])
    h = spawn_drone(pyramid_dispatch_dig_eroded, right_slice, floor)
    pyramid_dispatch_dig_eroded(left_slice, floor)
    if h == None:
        pyramid_dispatch_dig_eroded(right_slice, floor)
    else:
        wait_for(h)
    return True


def pyramid_dispatch_compute_cones(eroded, x0, x1, y0, y1, H):
    n = len(eroded)
    if n == 1:
        ex, ey = eroded[0]
        d_ex = ex - x0
        t_ex = x1 - ex
        if t_ex < d_ex:
            d_ex = t_ex
        d_ey = ey - y0
        t_ey = y1 - ey
        if t_ey < d_ey:
            d_ey = t_ey
        eh = 1 + d_ex
        if d_ey < d_ex:
            eh = 1 + d_ey
        rad = eh - 1
        max_r = (H - 1) // 2
        if rad > max_r:
            rad = max_r
        if rad < 0:
            rad = 0
        xmin = ex - rad
        if xmin < x0:
            xmin = x0
        xmax = ex + rad
        if xmax > x1:
            xmax = x1
        out = []
        for px in range(xmin, xmax + 1):
            adx = px - ex
            if adx < 0:
                adx = -adx
            rem = rad - adx
            dx_edge = px - x0
            if x1 - px < dx_edge:
                dx_edge = x1 - px
            py_lo = ey - rem
            if py_lo < y0:
                py_lo = y0
            py_hi = ey + rem
            if py_hi > y1:
                py_hi = y1
            for py in range(py_lo, py_hi + 1):
                ady = py - ey
                if ady < 0:
                    ady = -ady
                d2 = 2 * (adx + ady)
                dy_edge = py - y0
                if y1 - py < dy_edge:
                    dy_edge = y1 - py
                h_cell = 1 + dx_edge
                if dy_edge < dx_edge:
                    h_cell = 1 + dy_edge
                if d2 < h_cell:
                    out.append((px, py, d2, h_cell))
        return [out]
    mid = n // 2
    right_slice = []
    for i in range(mid, n):
        right_slice.append(eroded[i])
    left_slice = []
    for i in range(mid):
        left_slice.append(eroded[i])
    h = spawn_drone(pyramid_dispatch_compute_cones, right_slice, x0, x1, y0, y1, H)
    left = pyramid_dispatch_compute_cones(left_slice, x0, x1, y0, y1, H)
    if h == None:
        right = pyramid_dispatch_compute_cones(right_slice, x0, x1, y0, y1, H)
    else:
        right = wait_for(h)
    for item in right:
        left.append(item)
    return left


def pyramid_dispatch_repair(worker_jobs, floor, active_layers, thresholds, deadline):
    n = len(worker_jobs)
    if n == 1:
        return pyramid_run_repair(worker_jobs[0], floor, active_layers, thresholds, deadline)
    mid = n // 2
    right_slice = []
    for i in range(mid, n):
        right_slice.append(worker_jobs[i])
    left_slice = []
    for i in range(mid):
        left_slice.append(worker_jobs[i])
    h = spawn_drone(pyramid_dispatch_repair, right_slice, floor, active_layers, thresholds, deadline)
    if h == None:
        return False
    left = pyramid_dispatch_repair(left_slice, floor, active_layers, thresholds, deadline)
    right = wait_for(h)
    return left and right


def pyramid_run_repair(cols, floor, active_layers, thresholds, deadline):
    Sand = Grounds.Sand
    Block = Items.Block
    n_layers = len(active_layers)
    n_cols = len(cols)
    if n_cols == 1:
        px, py, h_cur, h_top = cols[0]
        pyramid_move_30(px, py)
        for li in range(n_layers):
            L = active_layers[li]
            if h_cur < L and h_top >= L:
                if li + 1 == n_layers and get_pos_z() == floor:
                    return True
                place(Sand)
            if li + 1 < n_layers:
                thresh = thresholds[li]
                spins = 0
                while num_items(Block) > thresh:
                    spins += 1
                    if spins > 4000:
                        if get_time() > deadline:
                            return False
                        spins = 0
                    w = 0
                    while w < 6:
                        w += 1
        return True
    cur_x = get_pos_x()
    cur_y = get_pos_y()
    for li in range(n_layers):
        L = active_layers[li]
        thresh = thresholds[li]
        is_last = (li + 1 == n_layers)
        if li % 2 == 0:
            for ci in range(n_cols):
                px, py, h_cur, h_top = cols[ci]
                if h_cur < L and h_top >= L:
                    if cur_x != px or cur_y != py:
                        pyramid_move_from_to_30(cur_x, cur_y, px, py)
                        cur_x = px
                        cur_y = py
                    if is_last and get_pos_z() == floor:
                        return True
                    place(Sand)
        else:
            ci = n_cols - 1
            while ci >= 0:
                px, py, h_cur, h_top = cols[ci]
                if h_cur < L and h_top >= L:
                    if cur_x != px or cur_y != py:
                        pyramid_move_from_to_30(cur_x, cur_y, px, py)
                        cur_x = px
                        cur_y = py
                    if is_last and get_pos_z() == floor:
                        return True
                    place(Sand)
                ci -= 1
        if not is_last:
            spins = 0
            while num_items(Block) > thresh:
                spins += 1
                if spins > 4000:
                    if get_time() > deadline:
                        return False
                    spins = 0
                w = 0
                while w < 6:
                    w += 1
    return True


def pyramid_build_octant_tasks(x0, x1, y0, y1, floor, H):
    E = East
    W = West
    N = North
    S = South
    outer_tasks = []
    grp_a = []
    grp_b = []
    for _ in range(8):
        grp_a.append([])
        grp_b.append([])
    r = 0
    while r <= H - 2:
        ax = x0 + r
        bx = x1 - r
        ay = y0 + r
        by = y1 - r
        tz = floor + 1 + r
        mx = 14
        if mx < ax:
            mx = ax
        if mx > bx:
            mx = bx
        my = 14
        if my < ay:
            my = ay
        if my > by:
            my = by
        oct_segs = [None, None, None, None, None, None, None, None]
        oct_segs[0] = (mx, ay, tz, E, bx - mx, N, ax + 1, bx - 1)
        if mx > ax:
            oct_segs[1] = (mx - 1, ay, tz, W, mx - 1 - ax, N, ax + 1, bx - 1)
        oct_segs[2] = (mx, by, tz, E, bx - mx, S, ax + 1, bx - 1)
        if mx > ax:
            oct_segs[3] = (mx - 1, by, tz, W, mx - 1 - ax, S, ax + 1, bx - 1)
        if by - ay >= 2:
            my_c = my
            if my_c < ay + 1:
                my_c = ay + 1
            if my_c > by - 1:
                my_c = by - 1
            oct_segs[4] = (bx, my_c, tz, N, by - 1 - my_c, W, ay + 2, by - 2)
            if my_c > ay + 1:
                oct_segs[5] = (bx, my_c - 1, tz, S, my_c - 1 - (ay + 1), W, ay + 2, by - 2)
            oct_segs[6] = (ax, my_c, tz, N, by - 1 - my_c, E, ay + 2, by - 2)
            if my_c > ay + 1:
                oct_segs[7] = (ax, my_c - 1, tz, S, my_c - 1 - (ay + 1), E, ay + 2, by - 2)
        if r <= 2:
            for oi in range(8):
                if oct_segs[oi] != None:
                    outer_tasks.append([oct_segs[oi]])
        elif r == 4 or r == 10:
            for oi in range(8):
                if oct_segs[oi] != None:
                    grp_a[oi].append(oct_segs[oi])
        else:
            for oi in range(8):
                if oct_segs[oi] != None:
                    grp_b[oi].append(oct_segs[oi])
        r += 2
    for oi in range(8):
        if len(grp_a[oi]) > 0:
            outer_tasks.append(grp_a[oi])
        if len(grp_b[oi]) > 0:
            outer_tasks.append(grp_b[oi])
    return outer_tasks


def pyramid_dispatch_rings(tasks):
    n = len(tasks)
    if n == 1:
        return pyramid_run_ring_task(tasks[0])
    mid = n // 2
    right_slice = []
    for i in range(mid, n):
        right_slice.append(tasks[i])
    left_slice = []
    for i in range(mid):
        left_slice.append(tasks[i])
    h = spawn_drone(pyramid_dispatch_rings, right_slice)
    left = pyramid_dispatch_rings(left_slice)
    if h == None:
        right = pyramid_dispatch_rings(right_slice)
    else:
        right = wait_for(h)
    for item in right:
        left.append(item)
    return left


def pyramid_run_ring_task(segs):
    Sand = Grounds.Sand
    E = East
    W = West
    N = North
    S = South
    eroded = []
    cur_x = get_pos_x()
    cur_y = get_pos_y()
    for sx, sy, tz, d, steps, pdir, plo, phi in segs:
        if cur_x != sx or cur_y != sy:
            pyramid_move_from_to_30(cur_x, cur_y, sx, sy)
            cur_x = sx
            cur_y = sy
        x = sx
        y = sy
        horiz = (d == E or d == W)
        dx = 0
        dy = 0
        if d == E:
            dx = 1
        elif d == W:
            dx = -1
        elif d == N:
            dy = 1
        else:
            dy = -1
        pdx = 0
        pdy = 0
        opp = S
        if pdir == E:
            pdx = 1
            opp = W
        elif pdir == W:
            pdx = -1
            opp = E
        elif pdir == N:
            pdy = 1
            opp = S
        else:
            pdy = -1
            opp = N
        for st in range(steps + 1):
            if st > 0:
                move(d)
                x += dx
                y += dy
            while get_pos_z() > tz:
                dig()
            if get_ground_type() != Sand:
                eroded.append((x, y))
            coord = y
            if horiz:
                coord = x
            if coord >= plo and coord <= phi:
                pz = get_pos_z(pdir)
                if pz > tz + 1:
                    move(pdir)
                    while get_pos_z() > tz + 1:
                        dig()
                    if get_ground_type() != Sand:
                        eroded.append((x + pdx, y + pdy))
                    move(opp)
                elif get_ground_type(pdir) != Sand:
                    eroded.append((x + pdx, y + pdy))
        cur_x = x
        cur_y = y
    return eroded


def pyramid_ray_probe(sx, sy, z_start, dx, dy, direction, chunk_bot):
    Sand = Grounds.Sand
    Limestone = Grounds.Limestone
    x = sx
    y = sy
    z = z_start
    last_ok = (sx, sy, z_start)
    end_coord = sx
    if dy != 0:
        end_coord = sy
    eroded = []
    min_sand_z = chunk_bot + 1
    while True:
        if z <= min_sand_z:
            break
        nx = x + dx
        ny = y + dy
        if nx < 0 or nx >= 30 or ny < 0 or ny >= 30:
            break
        move(direction)
        x = nx
        y = ny
        target = z - 1
        found_sand = False
        while get_pos_z() > target:
            if get_ground_type() == Sand:
                found_sand = True
                break
            if get_ground_type() == Limestone:
                break
            dig()
        if not found_sand and get_ground_type() == Sand:
            found_sand = True
        if found_sand:
            z = get_pos_z()
            last_ok = (x, y, z)
            if dx != 0:
                end_coord = x
            else:
                end_coord = y
        else:
            if z - 2 < min_sand_z:
                break
            nx2 = x + dx
            ny2 = y + dy
            if nx2 < 0 or nx2 >= 30 or ny2 < 0 or ny2 >= 30:
                break
            move(direction)
            t2 = z - 2
            found2 = False
            while get_pos_z() > t2:
                if get_ground_type() == Sand:
                    found2 = True
                    break
                if get_ground_type() == Limestone:
                    break
                dig()
            if not found2 and get_ground_type() == Sand:
                found2 = True
            if found2:
                eroded.append((x, y))
                x = nx2
                y = ny2
                z = get_pos_z()
                last_ok = (x, y, z)
                if dx != 0:
                    end_coord = x
                else:
                    end_coord = y
            else:
                break
    return (end_coord, last_ok, eroded)


def pyramid_mine_extra_blocks(x0, x1, y0, y1, floor, needed):
    spots = []
    for x in range(30):
        for y in range(30):
            if (x + y) % 2 != 0:
                continue
            if x >= x0 and x <= x1 and y >= y0 and y <= y1:
                continue
            spots.append((x, y))
            if len(spots) >= 16:
                break
        if len(spots) >= 16:
            break
    if len(spots) > 0:
        pyramid_dispatch_mine(spots, floor, needed)
    while num_items(Items.Block) < needed:
        if len(spots) > 0:
            pyramid_dispatch_mine(spots, floor - 16, needed)
        else:
            break


def pyramid_dispatch_mine(spots, min_z, needed):
    n = len(spots)
    if n == 1:
        mx, my = spots[0]
        pyramid_move_30(mx, my)
        while get_pos_z() > min_z and num_items(Items.Block) < needed:
            dig()
        return True
    mid = n // 2
    rs = []
    for i in range(mid, n):
        rs.append(spots[i])
    ls = []
    for i in range(mid):
        ls.append(spots[i])
    h = spawn_drone(pyramid_dispatch_mine, rs, min_z, needed)
    pyramid_dispatch_mine(ls, min_z, needed)
    if h == None:
        pyramid_dispatch_mine(rs, min_z, needed)
    else:
        wait_for(h)
    return True


def pyramid_move_30(tx, ty):
    pyramid_move_from_to_30(get_pos_x(), get_pos_y(), tx, ty)


def pyramid_move_from_to_30(cx, cy, tx, ty):
    dx = (tx - cx) % 30
    if dx <= 15:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(30 - dx):
            move(West)
    dy = (ty - cy) % 30
    if dy <= 15:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(30 - dy):
            move(South)


def pyramid_fast_unlock_power(target_power):
    set_world_size(5)
    Dirt = Grounds.Dirt
    Sand = Grounds.Sand
    Limestone = Grounds.Limestone
    Sunflower = Entities.Sunflower
    E = East
    W = West
    N = North
    S = South
    ring_steps = [
        (E, N, 1, 1), (E, N, 2, 1), (E, N, 3, 1), (E, None, 0, 0),
        (N, None, 0, 0), (N, W, 3, 2), (N, None, 0, 0), (N, None, 0, 0),
        (W, S, 3, 3), (W, S, 2, 3), (W, S, 1, 3), (W, None, 0, 0),
        (S, None, 0, 0), (S, E, 1, 2), (S, None, 0, 0),
    ]
    while num_items(Items.Power) < target_power:
        clear()
        while get_ground_type() != Dirt and get_ground_type(E) != Dirt and get_ground_type(N) != Dirt:
            clear()
        dig()
        dig()
        if get_ground_type() != Sand:
            dig()
            if get_ground_type() != Limestone:
                continue
            place(Sand)
        done = False
        eroded_mid = []
        for mdir, pdir, px, py in ring_steps:
            move(mdir)
            z = get_pos_z()
            if z == -3:
                done = True
                break
            while z > -2:
                dig()
                z = get_pos_z()
                if z == -3:
                    done = True
                    break
            if done:
                break
            if get_ground_type() != Sand:
                dig()
                place(Sand)
                if get_pos_z() == -3:
                    done = True
                    break
            if pdir != None:
                if get_ground_type(pdir) != Sand or get_pos_z(pdir) != -1:
                    eroded_mid.append((px, py))
        if done:
            pyramid_move_5(2, 2)
            harvest()
            continue
        need_layer2 = []
        for mx, my in eroded_mid:
            pyramid_move_5(mx, my)
            z = get_pos_z()
            if z == -3:
                done = True
                break
            if z == 0:
                dig()
                z = get_pos_z()
                if z == -3:
                    done = True
                    break
                if get_ground_type() == Sand:
                    continue
            while get_pos_z() > -3:
                dig()
            place(Sand)
            need_layer2.append((mx, my))
        if not done and len(need_layer2) > 0:
            center_eroded = False
            lx, ly = need_layer2[len(need_layer2) - 1]
            cdir = None
            if lx == 2 and ly == 1:
                cdir = N
            elif lx == 2 and ly == 3:
                cdir = S
            elif lx == 1 and ly == 2:
                cdir = E
            elif lx == 3 and ly == 2:
                cdir = W
            if cdir != None:
                if get_ground_type(cdir) != Sand:
                    center_eroded = True
            else:
                place(Sand)
                z = get_pos_z()
                if z == -3:
                    done = True
                elif z == -1:
                    need_layer2.pop()
                else:
                    center_eroded = True
            if not done:
                if center_eroded:
                    pyramid_move_5(2, 2)
                    while get_ground_type() != Limestone:
                        dig()
                    place(Sand)
                i = len(need_layer2) - 1
                while i >= 0:
                    mx, my = need_layer2[i]
                    pyramid_move_5(mx, my)
                    if get_pos_z() == -3:
                        done = True
                        break
                    place(Sand)
                    if get_pos_z() == -3:
                        done = True
                        break
                    i -= 1
        pyramid_move_5(2, 2)
        if not done and get_entity_type() != Sunflower:
            if get_ground_type() != Sand and get_ground_type() != Limestone:
                while get_ground_type() != Limestone:
                    dig()
            for _ in range(3):
                if get_entity_type() == Sunflower:
                    break
                place(Sand)
        harvest()


def pyramid_move_5(tx, ty):
    dx = (tx - get_pos_x()) % 5
    if dx == 1:
        move(East)
    elif dx == 2:
        move(East)
        move(East)
    elif dx == 3:
        move(West)
        move(West)
    elif dx == 4:
        move(West)
    dy = (ty - get_pos_y()) % 5
    if dy == 1:
        move(North)
    elif dy == 2:
        move(North)
        move(North)
    elif dy == 3:
        move(South)
        move(South)
    elif dy == 4:
        move(South)


if __name__ == "__main__":
    lb_pyramids()
