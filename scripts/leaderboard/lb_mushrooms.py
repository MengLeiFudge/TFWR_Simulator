from __builtins__ import *
# 完整轮时间：1:54.541（本地7200游戏秒完整抽样63轮，游戏随机，SD=4.172s，95%自适应CI±2.133s，0失败0警告；尚无本版实机）。

def lb_mushrooms():
    h_min = 5
    t_budget_6 = 14.0
    t_budget_5 = 11.0

    for batch in range(512):
        cur_mush = num_items(Items.Mushroom)
        if cur_mush >= 240000:
            return
        clear()
        while get_ground_type() != Grounds.Mushroom:
            if not dig():
                return
        top = get_pos_z()
        ok_h = True
        for _ in range(h_min - 1):
            if get_ground_type() != Grounds.Mushroom:
                ok_h = False
                break
            dig()
        if not ok_h or get_ground_type() != Grounds.Mushroom:
            continue
        dig()
        if get_ground_type() == Grounds.Mushroom:
            h_actual = 6
            budget = t_budget_6
        else:
            h_actual = 5
            budget = t_budget_5
        bottom = top - h_actual
        check_goal = cur_mush >= 195000
        deadline = get_time() + budget
        tree_worker(0, 32, top, bottom, deadline, check_goal)


def tree_worker(lo, hi, top, bottom, deadline, check_goal):
    handles = []
    while hi - lo > 1:
        mid = (lo + hi) // 2
        h = spawn_drone(tree_worker, mid, hi, top, bottom, deadline, check_goal)
        if h != None:
            handles.append(h)
        hi = mid
    bx, by = BLOCKS[lo]
    work_block(bx, by, top, bottom, deadline, check_goal)
    for h in handles:
        wait_for(h)


def resync_pair(u, v, d, bottom, z_arr, c_arr, buried):
    zu = get_pos_z()
    z_arr[u] = zu
    buried[u] = []
    if zu > bottom:
        mc = measure()
        if mc == None:
            c_arr[u] = -1
        else:
            c_arr[u] = mc
    else:
        c_arr[u] = -1
    zv = get_pos_z(d)
    z_arr[v] = zv
    buried[v] = []
    if zv > bottom:
        mv = measure(d)
        if mv == None:
            c_arr[v] = -1
        else:
            c_arr[v] = mv
    else:
        c_arr[v] = -1


def work_block(bx, by, top, bottom, deadline, check_goal):
    move_world(bx + 1, by)

    z_arr = []
    c_arr = []
    buried = []
    for _ in range(32):
        z_arr.append(0)
        c_arr.append(-1)
        buried.append([])
    # 哨兵槽 32：颜色 -2 永不匹配，高度 9999 永不更低，消除热循环越界分支。
    z_arr.append(9999)
    c_arr.append(-2)

    rem_blocks = 0
    for idx in range(16):
        if idx > 0:
            move(U_DIRS[idx - 1])
        sc = U_CELLS[idx]
        zc = get_pos_z()
        if zc > top:
            while get_pos_z() > top:
                dig()
            dig()
            zc = get_pos_z()
        elif zc == top:
            dig()
            zc = get_pos_z()
        if idx < 8:
            side_nb = sc - 1
            side_d = West
        else:
            side_nb = sc + 1
            side_d = East
        zn = get_pos_z(side_d)
        if zn > top:
            dig()
            zc = get_pos_z()
            zn = get_pos_z(side_d)
        z_arr[sc] = zc
        if zc > bottom:
            mc = measure()
            if mc != None:
                c_arr[sc] = mc
                rem_blocks += zc - bottom
        z_arr[side_nb] = zn
        if zn <= top and zn > bottom:
            mn = measure(side_d)
            if mn != None:
                c_arr[side_nb] = mn
                rem_blocks += zn - bottom

    cur = 2
    min_stack_z = bottom + 2
    early_stop = 30
    max_idle = 10

    ready = []
    for a in range(32):
        ca = c_arr[a]
        if ca < 0:
            continue
        za = z_arr[a]
        nb = N0[a]
        if c_arr[nb] == ca:
            zn = z_arr[nb]
            if za > zn:
                ready.append((a, nb, North))
            elif zn > za:
                ready.append((nb, a, South))
        nb = N1[a]
        if c_arr[nb] == ca:
            zn = z_arr[nb]
            if za > zn:
                ready.append((a, nb, East))
            elif zn > za:
                ready.append((nb, a, West))

    idle = 0
    scan_cur = 0
    while rem_blocks > early_stop and get_time() < deadline:
        if check_goal and num_items(Items.Mushroom) >= 240000:
            return
        cu = c_arr[cur]
        zu = z_arr[cur]

        # 1+2：原地四邻直推（200t）与邻格反推（400t）合并一次扫描。
        if cu >= 0:
            v = -1
            rv = -1
            nb = N0[cur]
            if c_arr[nb] == cu:
                zn = z_arr[nb]
                if zn < zu:
                    v = nb
                    d = North
                elif zn > zu:
                    rv = nb
                    rd = North
                    rbd = South
            if v < 0:
                nb = N1[cur]
                if c_arr[nb] == cu:
                    zn = z_arr[nb]
                    if zn < zu:
                        v = nb
                        d = East
                    elif rv < 0 and zn > zu:
                        rv = nb
                        rd = East
                        rbd = West
            if v < 0:
                nb = N2[cur]
                if c_arr[nb] == cu:
                    zn = z_arr[nb]
                    if zn < zu:
                        v = nb
                        d = South
                    elif rv < 0 and zn > zu:
                        rv = nb
                        rd = South
                        rbd = North
            if v < 0:
                nb = N3[cur]
                if c_arr[nb] == cu:
                    zn = z_arr[nb]
                    if zn < zu:
                        v = nb
                        d = West
                    elif rv < 0 and zn > zu:
                        rv = nb
                        rd = West
                        rbd = East
            if v >= 0:
                if not push(d):
                    resync_pair(cur, v, d, bottom, z_arr, c_arr, buried)
                    continue
                zu -= 1
                z_arr[cur] = zu
                zv = z_arr[v] - 1
                z_arr[v] = zv
                bu = buried[cur]
                if bu:
                    nc = bu.pop()
                elif zu > bottom:
                    nc = measure()
                    if nc == None:
                        nc = -1
                        z_arr[cur] = get_pos_z()
                else:
                    nc = -1
                c_arr[cur] = nc
                bv = buried[v]
                if bv:
                    nv = bv.pop()
                elif zv > bottom:
                    nv = measure(d)
                    if nv == None:
                        nv = -1
                        z_arr[v] = get_pos_z(d)
                else:
                    nv = -1
                c_arr[v] = nv
                rem_blocks -= 2
                idle = 0
                if nv >= 0:
                    add_edges_b(v, nv, zv, z_arr, c_arr, ready)
                continue

            if rv >= 0:
                old = cur
                move(rd)
                cur = rv
                if not push(rbd):
                    resync_pair(cur, old, rbd, bottom, z_arr, c_arr, buried)
                    continue
                zc = z_arr[cur] - 1
                z_arr[cur] = zc
                zu -= 1
                z_arr[old] = zu
                bu = buried[cur]
                if bu:
                    nc = bu.pop()
                elif zc > bottom:
                    nc = measure()
                    if nc == None:
                        nc = -1
                        z_arr[cur] = get_pos_z()
                else:
                    nc = -1
                c_arr[cur] = nc
                bv = buried[old]
                if bv:
                    nv = bv.pop()
                elif zu > bottom:
                    nv = measure(rbd)
                    if nv == None:
                        nv = -1
                        z_arr[old] = get_pos_z(rbd)
                else:
                    nv = -1
                c_arr[old] = nv
                rem_blocks -= 2
                idle = 0
                if nv >= 0:
                    add_edges_b(old, nv, zu, z_arr, c_arr, ready)
                continue

        # 3：展开式两步过桥（600t）与双邻汇合（800t）。
        if cu >= 0:
            bm = -1
            fm = -1
            m = N0[cur]
            zm = z_arr[m]
            if zm < zu:
                w = N0[m]
                if c_arr[w] == cu:
                    zw = z_arr[w]
                    if zw <= zm:
                        bm = m
                        bw = w
                        md1 = North
                        pd2 = North
                    elif zw >= zm + 2:
                        fm = m
                        fw = w
                        fmd1 = North
                        fpd2 = South
                if bm < 0:
                    w = N1[m]
                    if c_arr[w] == cu:
                        zw = z_arr[w]
                        if zw <= zm:
                            bm = m
                            bw = w
                            md1 = North
                            pd2 = East
                        elif fm < 0 and zw >= zm + 2:
                            fm = m
                            fw = w
                            fmd1 = North
                            fpd2 = West
                if bm < 0:
                    w = N3[m]
                    if c_arr[w] == cu:
                        zw = z_arr[w]
                        if zw <= zm:
                            bm = m
                            bw = w
                            md1 = North
                            pd2 = West
                        elif fm < 0 and zw >= zm + 2:
                            fm = m
                            fw = w
                            fmd1 = North
                            fpd2 = East
            if bm < 0:
                m = N1[cur]
                zm = z_arr[m]
                if zm < zu:
                    w = N0[m]
                    if c_arr[w] == cu:
                        zw = z_arr[w]
                        if zw <= zm:
                            bm = m
                            bw = w
                            md1 = East
                            pd2 = North
                        elif fm < 0 and zw >= zm + 2:
                            fm = m
                            fw = w
                            fmd1 = East
                            fpd2 = South
                    if bm < 0:
                        w = N1[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = East
                                pd2 = East
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = East
                                fpd2 = West
                    if bm < 0:
                        w = N2[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = East
                                pd2 = South
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = East
                                fpd2 = North
            if bm < 0:
                m = N2[cur]
                zm = z_arr[m]
                if zm < zu:
                    w = N1[m]
                    if c_arr[w] == cu:
                        zw = z_arr[w]
                        if zw <= zm:
                            bm = m
                            bw = w
                            md1 = South
                            pd2 = East
                        elif fm < 0 and zw >= zm + 2:
                            fm = m
                            fw = w
                            fmd1 = South
                            fpd2 = West
                    if bm < 0:
                        w = N2[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = South
                                pd2 = South
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = South
                                fpd2 = North
                    if bm < 0:
                        w = N3[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = South
                                pd2 = West
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = South
                                fpd2 = East
            if bm < 0:
                m = N3[cur]
                zm = z_arr[m]
                if zm < zu:
                    w = N0[m]
                    if c_arr[w] == cu:
                        zw = z_arr[w]
                        if zw <= zm:
                            bm = m
                            bw = w
                            md1 = West
                            pd2 = North
                        elif fm < 0 and zw >= zm + 2:
                            fm = m
                            fw = w
                            fmd1 = West
                            fpd2 = South
                    if bm < 0:
                        w = N2[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = West
                                pd2 = South
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = West
                                fpd2 = North
                    if bm < 0:
                        w = N3[m]
                        if c_arr[w] == cu:
                            zw = z_arr[w]
                            if zw <= zm:
                                bm = m
                                bw = w
                                md1 = West
                                pd2 = West
                            elif fm < 0 and zw >= zm + 2:
                                fm = m
                                fw = w
                                fmd1 = West
                                fpd2 = East

            if bm >= 0:
                if not push(md1):
                    resync_pair(cur, bm, md1, bottom, z_arr, c_arr, buried)
                    continue
                zu -= 1
                z_arr[cur] = zu
                bu = buried[cur]
                if bu:
                    nc = bu.pop()
                elif zu > bottom:
                    nc = measure()
                    if nc == None:
                        nc = -1
                        z_arr[cur] = get_pos_z()
                else:
                    nc = -1
                c_arr[cur] = nc
                old = cur
                move(md1)
                cur = bm
                if not push(pd2):
                    resync_pair(cur, bw, pd2, bottom, z_arr, c_arr, buried)
                    if nc >= 0:
                        add_edges_b(old, nc, zu, z_arr, c_arr, ready)
                    continue
                zw = z_arr[bw] - 1
                z_arr[bw] = zw
                bv = buried[bw]
                if bv:
                    nv = bv.pop()
                elif zw > bottom:
                    nv = measure(pd2)
                    if nv == None:
                        nv = -1
                        z_arr[bw] = get_pos_z(pd2)
                else:
                    nv = -1
                c_arr[bw] = nv
                rem_blocks -= 2
                idle = 0
                if nc >= 0:
                    add_edges_b(old, nc, zu, z_arr, c_arr, ready)
                if nv >= 0:
                    add_edges_b(bw, nv, zw, z_arr, c_arr, ready)
                continue

            if fm >= 0:
                if not push(fmd1):
                    resync_pair(cur, fm, fmd1, bottom, z_arr, c_arr, buried)
                    continue
                zu -= 1
                z_arr[cur] = zu
                bu = buried[cur]
                if bu:
                    nc = bu.pop()
                elif zu > bottom:
                    nc = measure()
                    if nc == None:
                        nc = -1
                        z_arr[cur] = get_pos_z()
                else:
                    nc = -1
                c_arr[cur] = nc
                old = cur
                cur = move_local(cur, fw)
                if not push(fpd2):
                    resync_pair(cur, fm, fpd2, bottom, z_arr, c_arr, buried)
                    if nc >= 0:
                        add_edges_b(old, nc, zu, z_arr, c_arr, ready)
                    continue
                zw = z_arr[fw] - 1
                z_arr[fw] = zw
                bv = buried[fw]
                if bv:
                    nv = bv.pop()
                elif zw > bottom:
                    nv = measure()
                    if nv == None:
                        nv = -1
                        z_arr[fw] = get_pos_z()
                else:
                    nv = -1
                c_arr[fw] = nv
                rem_blocks -= 2
                idle = 0
                if nc >= 0:
                    add_edges_b(old, nc, zu, z_arr, c_arr, ready)
                continue

        # 4：弹出LIFO就绪边；若距离>=3优先原地0移动异色堆叠蓄色。
        fa = -1
        ux = CX[cur]
        uy = CY[cur]
        while ready:
            a, b, d = ready.pop()
            if c_arr[a] == c_arr[b] and z_arr[a] > z_arr[b]:
                if idle < 3 and zu >= min_stack_z:
                    da = abs(CX[a] - ux) + abs(CY[a] - uy)
                    if da >= 3:
                        sv = -1
                        best_zv = 999
                        nb = N0[cur]
                        if z_arr[nb] < zu and z_arr[nb] < best_zv:
                            best_zv = z_arr[nb]
                            sv = nb
                            sd = North
                        nb = N1[cur]
                        if z_arr[nb] < zu and z_arr[nb] < best_zv:
                            best_zv = z_arr[nb]
                            sv = nb
                            sd = East
                        nb = N2[cur]
                        if z_arr[nb] < zu and z_arr[nb] < best_zv:
                            best_zv = z_arr[nb]
                            sv = nb
                            sd = South
                        nb = N3[cur]
                        if z_arr[nb] < zu and z_arr[nb] < best_zv:
                            best_zv = z_arr[nb]
                            sv = nb
                            sd = West
                        if sv >= 0:
                            ready.append((a, b, d))
                            if not push(sd):
                                resync_pair(cur, sv, sd, bottom, z_arr, c_arr, buried)
                                fa = -2
                                break
                            zu -= 1
                            z_arr[cur] = zu
                            zv = z_arr[sv] + 1
                            z_arr[sv] = zv
                            if c_arr[sv] >= 0:
                                buried[sv].append(c_arr[sv])
                            c_arr[sv] = cu
                            bu = buried[cur]
                            if bu:
                                nc = bu.pop()
                            elif zu > bottom:
                                nc = measure()
                                if nc == None:
                                    nc = -1
                                    z_arr[cur] = get_pos_z()
                            else:
                                nc = -1
                            c_arr[cur] = nc
                            idle += 1
                            add_edges_b(sv, cu, zv, z_arr, c_arr, ready)
                            fa = -2
                            break
                fa = a
                fb = b
                fd = d
                break

        if fa == -2:
            continue
        if fa >= 0:
            cur = move_local(cur, fa)
            if not push(fd):
                resync_pair(fa, fb, fd, bottom, z_arr, c_arr, buried)
                continue
            za = z_arr[fa] - 1
            z_arr[fa] = za
            zb = z_arr[fb] - 1
            z_arr[fb] = zb
            bu = buried[fa]
            if bu:
                nc = bu.pop()
            elif za > bottom:
                nc = measure()
                if nc == None:
                    nc = -1
                    z_arr[fa] = get_pos_z()
            else:
                nc = -1
            c_arr[fa] = nc
            bv = buried[fb]
            if bv:
                nv = bv.pop()
            elif zb > bottom:
                nv = measure(fd)
                if nv == None:
                    nv = -1
                    z_arr[fb] = get_pos_z(fd)
            else:
                nv = -1
            c_arr[fb] = nv
            rem_blocks -= 2
            idle = 0
            if nv >= 0:
                add_edges_b(fb, nv, zb, z_arr, c_arr, ready)
            continue

        # 5：就绪栈为空时，原地异色堆叠暴露新色。
        if idle >= max_idle:
            break
        if zu >= min_stack_z:
            sv = -1
            best_zv = 999
            nb = N0[cur]
            if z_arr[nb] < zu and z_arr[nb] < best_zv:
                best_zv = z_arr[nb]
                sv = nb
                sd = North
            nb = N1[cur]
            if z_arr[nb] < zu and z_arr[nb] < best_zv:
                best_zv = z_arr[nb]
                sv = nb
                sd = East
            nb = N2[cur]
            if z_arr[nb] < zu and z_arr[nb] < best_zv:
                best_zv = z_arr[nb]
                sv = nb
                sd = South
            nb = N3[cur]
            if z_arr[nb] < zu and z_arr[nb] < best_zv:
                best_zv = z_arr[nb]
                sv = nb
                sd = West
            if sv >= 0:
                if not push(sd):
                    resync_pair(cur, sv, sd, bottom, z_arr, c_arr, buried)
                    continue
                zu -= 1
                z_arr[cur] = zu
                zv = z_arr[sv] + 1
                z_arr[sv] = zv
                if c_arr[sv] >= 0:
                    buried[sv].append(c_arr[sv])
                c_arr[sv] = cu
                bu = buried[cur]
                if bu:
                    nc = bu.pop()
                elif zu > bottom:
                    nc = measure()
                    if nc == None:
                        nc = -1
                        z_arr[cur] = get_pos_z()
                else:
                    nc = -1
                c_arr[cur] = nc
                idle += 1
                add_edges_b(sv, cu, zv, z_arr, c_arr, ready)
                continue

        # 6：O(1) 均摊环形游标兜底。
        sa = -1
        tries = 32
        while tries:
            tries -= 1
            a = scan_cur
            scan_cur = (scan_cur + 1) % 32
            za = z_arr[a]
            if za < min_stack_z:
                continue
            nb = N0[a]
            if z_arr[nb] < za:
                sa = a
                sv = nb
                sd = North
                break
            nb = N1[a]
            if z_arr[nb] < za:
                sa = a
                sv = nb
                sd = East
                break
            nb = N2[a]
            if z_arr[nb] < za:
                sa = a
                sv = nb
                sd = South
                break
            nb = N3[a]
            if z_arr[nb] < za:
                sa = a
                sv = nb
                sd = West
                break
        if sa < 0:
            break
        cur = move_local(cur, sa)
        ca = c_arr[sa]
        if not push(sd):
            resync_pair(sa, sv, sd, bottom, z_arr, c_arr, buried)
            continue
        za = z_arr[sa] - 1
        z_arr[sa] = za
        zv = z_arr[sv] + 1
        z_arr[sv] = zv
        if c_arr[sv] >= 0:
            buried[sv].append(c_arr[sv])
        c_arr[sv] = ca
        bu = buried[sa]
        if bu:
            nc = bu.pop()
        elif za > bottom:
            nc = measure()
            if nc == None:
                nc = -1
                z_arr[sa] = get_pos_z()
        else:
            nc = -1
        c_arr[sa] = nc
        idle += 1
        add_edges_b(sv, ca, zv, z_arr, c_arr, ready)


def move_world(tx, ty):
    dx = (tx - get_pos_x()) % 32
    if dx <= 16:
        while dx:
            move(East)
            dx -= 1
    else:
        dx = 32 - dx
        while dx:
            move(West)
            dx -= 1
    dy = (ty - get_pos_y()) % 32
    if dy <= 16:
        while dy:
            move(North)
            dy -= 1
    else:
        dy = 32 - dy
        while dy:
            move(South)
            dy -= 1


def move_local(cur, target):
    dx = CX[target] - CX[cur]
    if dx > 0:
        while dx:
            move(East)
            dx -= 1
    elif dx < 0:
        while dx:
            move(West)
            dx += 1
    dy = CY[target] - CY[cur]
    if dy > 0:
        while dy:
            move(North)
            dy -= 1
    elif dy < 0:
        while dy:
            move(South)
            dy += 1
    return target


def add_edges_b(p, cp, zp, z_arr, c_arr, ready):
    nb = N0[p]
    if c_arr[nb] == cp:
        zn = z_arr[nb]
        if zp > zn:
            ready.append((p, nb, North))
        elif zn > zp:
            ready.append((nb, p, South))
    nb = N1[p]
    if c_arr[nb] == cp:
        zn = z_arr[nb]
        if zp > zn:
            ready.append((p, nb, East))
        elif zn > zp:
            ready.append((nb, p, West))
    nb = N2[p]
    if c_arr[nb] == cp:
        zn = z_arr[nb]
        if zp > zn:
            ready.append((p, nb, South))
        elif zn > zp:
            ready.append((nb, p, North))
    nb = N3[p]
    if c_arr[nb] == cp:
        zn = z_arr[nb]
        if zp > zn:
            ready.append((p, nb, West))
        elif zn > zp:
            ready.append((nb, p, East))


U_CELLS = [
    1, 5, 9, 13, 17, 21, 25, 29,
    30, 26, 22, 18, 14, 10, 6, 2
]
U_DIRS = [
    North, North, North, North, North, North, North,
    East,
    South, South, South, South, South, South, South
]

N0 = [
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 32, 32, 32, 32
]
N1 = [
    1, 2, 3, 32, 5, 6, 7, 32, 9, 10, 11, 32, 13, 14, 15, 32,
    17, 18, 19, 32, 21, 22, 23, 32, 25, 26, 27, 32, 29, 30, 31, 32, 32
]
N2 = [
    32, 32, 32, 32, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 32
]
N3 = [
    32, 0, 1, 2, 32, 4, 5, 6, 32, 8, 9, 10, 32, 12, 13, 14,
    32, 16, 17, 18, 32, 20, 21, 22, 32, 24, 25, 26, 32, 28, 29, 30, 32
]
CX = [
    0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3,
    0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0
]
CY = [
    0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
    4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 0
]

BLOCKS = [
    (0, 0), (4, 0), (28, 0), (0, 8), (0, 24), (8, 0), (24, 0), (4, 8),
    (28, 8), (4, 24), (28, 24), (12, 0), (20, 0), (8, 8), (24, 8), (8, 24),
    (16, 16), (12, 16), (20, 16), (16, 8), (16, 24), (12, 8), (20, 8), (12, 24),
    (20, 24), (8, 16), (24, 16), (16, 0), (4, 16), (28, 16), (0, 16), (24, 24)
]


if __name__ == "__main__":
    lb_mushrooms()
