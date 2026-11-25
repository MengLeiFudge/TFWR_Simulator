from __builtins__ import *
# 完整轮时间：90.326秒（本地C#构建26732695，game_leaderboard_random 80轮累计7226.053秒，SD 2.468秒，标准95%CI±0.549秒／自适应95%CI±1.142秒，0失败0警告；尚待实机验证）。


def lb_ores():
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 7200
    goal = 20000
    order = ore_spawn_order(workers, size)
    for cycle in range(128):
        cur_q = num_items(Items.Quartz)
        if cur_q >= goal:
            quick_print("ores_done", True, get_time(), cur_q)
            return
        clear()
        before = cur_q
        rem_q = goal - before
        cur_iron = num_items(Items.Iron)
        is_final = rem_q <= 2600 and cur_iron >= 420
        need_iron = not is_final
        if is_final:
            iron_cap = 0
        elif cycle == 0:
            iron_cap = 1150
        else:
            iron_cap = 850
        cycle_start = get_time()
        if is_final:
            t_start = cycle_start + 25.0
            t_hard = t_start + 5.0
        else:
            t_start = cycle_start + 13.5
            t_hard = t_start + 1.0
        handles = []
        ok = True
        for i in range(workers - 1):
            wid = order[i]
            h = spawn_drone(ore_worker, wid, size, goal, need_iron, iron_cap, t_start, t_hard, deadline)
            if h == None:
                ok = False
                break
            handles.append(h)
        if not ore_worker(order[workers - 1], size, goal, need_iron, iron_cap, t_start, t_hard, deadline):
            ok = False
        for h in handles:
            if not wait_for(h):
                ok = False
        quick_print("ores_cycle", cycle, ok, num_items(Items.Quartz) - before, get_time(), num_items(Items.Quartz), num_items(Items.Iron))
        if not ok:
            quick_print("ores_failed", "cycle", cycle)
            return
    quick_print("ores_failed", "cycle_limit", get_time(), num_items(Items.Quartz))


def ore_start_xy(wid):
    # 45-degree rotated square lattice: 5.66 spacing between drones, <= 4.0 distance to any tile.
    row = wid // 4
    col = wid % 4
    sy = row * 4 + 2
    if row % 2 == 0:
        sx = col * 8 + 2
    else:
        sx = col * 8 + 6
    return (sx, sy)


def ore_spawn_order(workers, size):
    # Spawn farthest lattice anchors first on the 32x32 torus so all 32 drones arrive together.
    pairs = []
    for wid in range(workers):
        sx, sy = ore_start_xy(wid)
        dx = sx
        if dx > size // 2:
            dx = size - dx
        dy = sy
        if dy > size // 2:
            dy = size - dy
        pairs.append((dx + dy, wid))
    n = len(pairs)
    for i in range(n):
        best = i
        for j in range(i + 1, n):
            if pairs[j][0] > pairs[best][0]:
                best = j
        if best != i:
            tmp = pairs[i]
            pairs[i] = pairs[best]
            pairs[best] = tmp
    res = []
    for i in range(n):
        res.append(pairs[i][1])
    return res


def ore_harvest_iron_cluster(size, cap_iron):
    ox = get_pos_x()
    oy = get_pos_y()
    for d_dir, rev_dir, dx, dy in [(East, West, 1, 0), (West, East, -1, 0), (North, South, 0, 1), (South, North, 0, -1)]:
        if num_items(Items.Iron) >= cap_iron:
            break
        nx = ox + dx
        ny = oy + dy
        if nx < 0 or nx >= size or ny < 0 or ny >= size:
            continue
        if get_ground_type(d_dir) == Grounds.Iron:
            if not move(d_dir):
                return
            while get_ground_type() == Grounds.Iron and num_items(Items.Iron) < cap_iron:
                if not dig():
                    return
            hx = get_pos_x()
            hy = get_pos_y()
            for d2, r2, dx2, dy2 in [(East, West, 1, 0), (West, East, -1, 0), (North, South, 0, 1), (South, North, 0, -1)]:
                if num_items(Items.Iron) >= cap_iron:
                    break
                nx2 = hx + dx2
                ny2 = hy + dy2
                if nx2 < 0 or nx2 >= size or ny2 < 0 or ny2 >= size:
                    continue
                if get_ground_type(d2) == Grounds.Iron:
                    if not move(d2):
                        return
                    while get_ground_type() == Grounds.Iron and num_items(Items.Iron) < cap_iron:
                        if not dig():
                            return
                    if not move(r2):
                        return
            if not move(rev_dir):
                return


def ore_worker(wid, size, goal, need_iron, iron_cap, t_start, t_hard, deadline):
    sx, sy = ore_start_xy(wid)
    if not ore_move_to(sx, sy, size):
        return False
    if need_iron:
        # Pre-cave the 45-deg lattice to z=-31: lowers whole map via Chunk 1 cave-ins & self-sustains Iron.
        my_coal = 0
        for _ in range(34):
            if get_pos_z() <= -31:
                break
            g = get_ground_type()
            if g == Grounds.Coal:
                my_coal += 2
            if not dig():
                return False
            if g == Grounds.Iron and num_items(Items.Iron) < iron_cap:
                ore_harvest_iron_cluster(size, iron_cap)
        if num_items(Items.Iron) < 500 and my_coal >= 2:
            reached = False
            while my_coal > 0 and num_items(Items.Iron) < iron_cap:
                d = prospect_iron()
                my_coal -= 1
                if d == None:
                    reached = True
                    break
                if not move(d):
                    return False
            if reached:
                found_i = False
                for _ in range(34):
                    if num_items(Items.Iron) >= iron_cap:
                        break
                    g = get_ground_type()
                    if g == Grounds.Iron:
                        if not dig():
                            return False
                        found_i = True
                        ore_harvest_iron_cluster(size, iron_cap)
                    elif found_i or get_pos_z() <= -32:
                        break
                    else:
                        if not dig():
                            return False
    else:
        if not ore_dig_to(-8):
            return False

    tried = {}
    just_mined = False
    fails = 0
    skips = 0
    veins = 0
    for step in range(34):
        if num_items(Items.Quartz) >= goal:
            return True
        if get_time() >= t_start or get_time() > deadline:
            return True
        if num_items(Items.Iron) < 36:
            return True
        adj = ore_check_adj_quartz(size)
        if adj != None:
            tx, ty, tz = adj
            if not ore_move_to(tx, ty, size):
                return False
            for _ in range(20):
                if get_ground_type() == Grounds.Quartz:
                    if not dig():
                        return False
                    if num_items(Items.Quartz) >= goal:
                        return True
                else:
                    break
            just_mined = True
            veins += 1
            fails = 0
            skips = 0
            continue
        x0 = get_pos_x()
        y0 = get_pos_y()
        z0 = get_pos_z()
        d0 = prospect_quartz()
        if d0 == None:
            if z0 > -11:
                if not ore_dig_to(-11):
                    return False
                continue
            return True
        r0 = (d0 * d0 + 0.5) // 1
        if veins >= 1 and z0 <= -32 and r0 > 225:
            return True
        target = None
        if just_mined and r0 <= 2:
            target = ore_track_shift(x0, y0, z0, r0, size)
            just_mined = False
        if target == None:
            res = ore_triangulate(x0, y0, z0, r0, size, tried)
            if res == None:
                if z0 > -11:
                    if not ore_move_to(x0, y0, size) or not ore_dig_to(-11):
                        return False
                    continue
                return True
            if res[0] == -1:
                fails += 1
                if fails >= 4:
                    return True
                if not ore_move_to(res[1], res[2], size):
                    return False
                just_mined = False
                continue
            target = res
        fails = 0
        tx, ty, tz = target
        if not ore_approach_target(tx, ty, size, t_hard):
            return True
        if get_pos_z() < tz and get_ground_type() != Grounds.Quartz:
            tried[(tx, ty)] = get_pos_z()
            skips += 1
            just_mined = False
            if skips >= 3:
                return True
            jx = (tx + 4 * (1 - 2 * (wid % 2))) % size
            jy = (ty + 4 * (1 - 2 * ((wid // 2) % 2))) % size
            if not ore_move_to(jx, jy, size):
                return False
            continue
        found = False
        for _ in range(52):
            g = get_ground_type()
            if g == Grounds.Quartz:
                if not dig():
                    return False
                found = True
                if num_items(Items.Quartz) >= goal:
                    return True
                continue
            if found or get_pos_z() < tz:
                break
            if get_time() >= t_hard:
                return True
            if not dig():
                return False
            if g == Grounds.Iron and num_items(Items.Iron) < iron_cap - 200:
                ore_harvest_iron_cluster(size, iron_cap)
        if found:
            just_mined = True
            veins += 1
            skips = 0
        else:
            tried[(tx, ty)] = get_pos_z()
            skips += 1
            just_mined = False
            if skips >= 3:
                return True
            jx = (tx + 4 * (1 - 2 * (wid % 2))) % size
            jy = (ty + 4 * (1 - 2 * ((wid // 2) % 2))) % size
            if not ore_move_to(jx, jy, size):
                return False
    return True


def ore_check_adj_quartz(size):
    x = get_pos_x()
    y = get_pos_y()
    if x + 1 < size and get_ground_type(East) == Grounds.Quartz:
        return (x + 1, y, get_pos_z(East))
    if x > 0 and get_ground_type(West) == Grounds.Quartz:
        return (x - 1, y, get_pos_z(West))
    if y + 1 < size and get_ground_type(North) == Grounds.Quartz:
        return (x, y + 1, get_pos_z(North))
    if y > 0 and get_ground_type(South) == Grounds.Quartz:
        return (x, y - 1, get_pos_z(South))
    return None


def ore_approach_target(tx, ty, size, t_hard):
    cx = get_pos_x()
    cy = get_pos_y()
    z_cur = get_pos_z()
    dist_nw = abs(tx - cx) + abs(ty - cy)
    if z_cur > -27 or dist_nw < 2 or dist_nw > 12:
        return ore_move_to(tx, ty, size)
    while cx != tx or cy != ty:
        if get_time() >= t_hard:
            return False
        if cx != tx and cy != ty:
            if cx < tx:
                dx_d = East
                nx_x = cx + 1
            else:
                dx_d = West
                nx_x = cx - 1
            if cy < ty:
                dy_d = North
                ny_y = cy + 1
            else:
                dy_d = South
                ny_y = cy - 1
            zx = get_pos_z(dx_d)
            zy = get_pos_z(dy_d)
            if zx <= zy:
                d = dx_d
                nx = nx_x
                ny = cy
                z_next = zx
            else:
                d = dy_d
                nx = cx
                ny = ny_y
                z_next = zy
        elif cx < tx:
            d = East
            nx = cx + 1
            ny = cy
            z_next = get_pos_z(d)
        elif cx > tx:
            d = West
            nx = cx - 1
            ny = cy
            z_next = get_pos_z(d)
        elif cy < ty:
            d = North
            nx = cx
            ny = cy + 1
            z_next = get_pos_z(d)
        else:
            d = South
            nx = cx
            ny = cy - 1
            z_next = get_pos_z(d)
        z_here = get_pos_z()
        if z_next > -31 and z_here <= -27 and z_here >= -31 and z_next - z_here >= 2:
            while get_pos_z() > -32:
                if get_time() >= t_hard or not dig():
                    return False
        if not move(d):
            return False
        cx = nx
        cy = ny
    return True


def ore_track_shift(x0, y0, z0, r0, size):
    if r0 == 1:
        if x0 + 1 < size:
            dx_dir = East
            back_x = West
            nx = x0 + 1
            ox = x0 - 1
        else:
            dx_dir = West
            back_x = East
            nx = x0 - 1
            ox = x0 + 1
        if not move(dx_dir):
            return None
        if get_ground_type() == Grounds.Quartz:
            return (nx, y0, get_pos_z())
        z1 = get_pos_z()
        d1 = prospect_quartz()
        if d1 == None:
            return None
        r1 = (d1 * d1 + 0.5) // 1
        dz1 = z0 - z1
        if r1 <= dz1 * dz1:
            return (nx, y0, z0)
        if ox >= 0 and ox < size and (r1 == 4 + dz1 * dz1 or r1 == 4):
            return (ox, y0, z0)
        if not move(back_x):
            return None
        if y0 + 1 < size:
            dy_dir = North
            ny = y0 + 1
            oy = y0 - 1
        else:
            dy_dir = South
            ny = y0 - 1
            oy = y0 + 1
        if not move(dy_dir):
            return None
        if get_ground_type() == Grounds.Quartz:
            return (x0, ny, get_pos_z())
        z2 = get_pos_z()
        d2 = prospect_quartz()
        if d2 == None:
            return None
        r2 = (d2 * d2 + 0.5) // 1
        dz2 = z0 - z2
        if r2 <= dz2 * dz2:
            return (x0, ny, z0)
        if oy >= 0 and oy < size and (r2 == 4 + dz2 * dz2 or r2 == 4):
            return (x0, oy, z0)
        return (x0, y0, z0 - 1)
    if r0 == 2:
        if x0 + 1 < size:
            dx_dir = East
            nx = x0 + 1
            ox = x0 - 1
        else:
            dx_dir = West
            nx = x0 - 1
            ox = x0 + 1
        if not move(dx_dir):
            return None
        z1 = get_pos_z()
        d1 = prospect_quartz()
        if d1 == None:
            return None
        r1 = (d1 * d1 + 0.5) // 1
        dz1 = z0 - z1
        if r1 == 1 or r1 == 1 + dz1 * dz1:
            tx = nx
        elif ox >= 0 and ox < size and (r1 == 5 or r1 == 5 + dz1 * dz1):
            tx = ox
        else:
            return None
        if y0 + 1 < size:
            ny = y0 + 1
            oy = y0 - 1
        else:
            ny = y0 - 1
            oy = y0 + 1
        if not ore_move_to(x0, ny, size):
            return None
        z2 = get_pos_z()
        d2 = prospect_quartz()
        if d2 == None:
            return None
        r2 = (d2 * d2 + 0.5) // 1
        dz2 = z0 - z2
        if r2 == 1 or r2 == 1 + dz2 * dz2:
            ty = ny
        elif oy >= 0 and oy < size and (r2 == 5 or r2 == 5 + dz2 * dz2):
            ty = oy
        else:
            return None
        if ty == ny:
            if get_pos_z() > z0:
                if not dig():
                    return None
        else:
            if not ore_move_to(tx, y0, size):
                return None
            if get_pos_z() > z0:
                if not dig():
                    return None
        return (tx, ty, z0)
    return None


def ore_triangulate(x0, y0, z0, r0, size, tried):
    if x0 + 1 < size:
        nx1 = x0 + 1
        dx_dir = East
        back_x = West
    else:
        nx1 = x0 - 1
        dx_dir = West
        back_x = East
    if y0 + 1 < size:
        ny2 = y0 + 1
        dy_dir = North
    else:
        ny2 = y0 - 1
        dy_dir = South

    if not move(dx_dir):
        return None
    if get_ground_type() == Grounds.Quartz:
        return (nx1, y0, get_pos_z())
    z1 = get_pos_z()
    d1 = prospect_quartz()
    if d1 == None:
        return None
    r1 = (d1 * d1 + 0.5) // 1

    if z0 > -32:
        if not move(dy_dir):
            return None
        z2 = get_pos_z()
        d2 = prospect_quartz()
        if d2 == None:
            return None
        r2 = (d2 * d2 + 0.5) // 1
        p = ore_solve_l_shape(nx1, y0, z1, r1, x0, z0, r0, ny2, z2, r2, size, tried)
        if p != None:
            return p
        if not move(back_x):
            return None
        z3 = get_pos_z()
        d3 = prospect_quartz()
        if d3 == None:
            return None
        r3 = (d3 * d3 + 0.5) // 1
        p = ore_solve_l_shape(x0, y0, z0, r0, nx1, z1, r1, ny2, z3, r3, size, tried)
        if p != None:
            return p
        p = ore_solve_l_shape(x0, ny2, z3, r3, nx1, z2, r2, y0, z0, r0, size, tried)
        if p != None:
            return p
        p = ore_solve_l_shape(nx1, ny2, z2, r2, x0, z3, r3, y0, z1, r1, size, tried)
        if p != None:
            return p
        return ore_voronoi_escape(x0, y0, r0, nx1, y0, r1, x0, ny2, r3, nx1, ny2, r2, size)

    if not move(back_x):
        return None
    if not move(dy_dir):
        return None
    if get_ground_type() == Grounds.Quartz:
        return (x0, ny2, get_pos_z())
    z2 = get_pos_z()
    d2 = prospect_quartz()
    if d2 == None:
        return None
    r2 = (d2 * d2 + 0.5) // 1

    p = ore_solve_l_shape(x0, y0, z0, r0, nx1, z1, r1, ny2, z2, r2, size, tried)
    if p != None:
        return p

    if not move(dx_dir):
        return None
    z3 = get_pos_z()
    d3 = prospect_quartz()
    if d3 == None:
        return None
    r3 = (d3 * d3 + 0.5) // 1

    p = ore_solve_l_shape(nx1, ny2, z3, r3, x0, z2, r2, y0, z1, r1, size, tried)
    if p != None:
        return p
    p = ore_solve_l_shape(nx1, y0, z1, r1, x0, z0, r0, ny2, z3, r3, size, tried)
    if p != None:
        return p
    p = ore_solve_l_shape(x0, ny2, z2, r2, nx1, z3, r3, y0, z0, r0, size, tried)
    if p != None:
        return p
    return ore_voronoi_escape(x0, y0, r0, nx1, y0, r1, x0, ny2, r2, nx1, ny2, r3, size)


def ore_voronoi_escape(x0, y0, r0, x1, y1, r1, x2, y2, r2, x3, y3, r3, size):
    bx = x0
    by = y0
    br = r0
    if r1 < br:
        bx = x1
        by = y1
        br = r1
    if r2 < br:
        bx = x2
        by = y2
        br = r2
    if r3 < br:
        bx = x3
        by = y3
        br = r3
    if bx == x0:
        tx = bx + 2 * (x0 - x1)
    else:
        tx = bx + 2 * (x1 - x0)
    if by == y0:
        ty = by + 2 * (y0 - y2)
    else:
        ty = by + 2 * (y2 - y0)
    if tx < 0:
        tx = 0
    if tx >= size:
        tx = size - 1
    if ty < 0:
        ty = 0
    if ty >= size:
        ty = size - 1
    return (-1, tx, ty)


def ore_solve_l_shape(x0, y0, z0, r0, x1, z1, r1, y2, z2, r2, size, tried):
    dx1 = x1 - x0
    dy2 = y2 - y0
    sx_sum = x0 + x1
    sy_sum = y0 + y2
    drx = r0 - r1
    dry = r0 - r2

    if z0 <= -32 and z1 <= -32 and z2 <= -32:
        nx2 = sx_sum + dx1 * drx
        if nx2 % 2 == 0:
            x = nx2 // 2
            if x >= 0 and x < size:
                ny2 = sy_sum + dy2 * dry
                if ny2 % 2 == 0:
                    y = ny2 // 2
                    if y >= 0 and y < size:
                        if (x - x0) ** 2 + (y - y0) ** 2 == r0:
                            if not ((x, y) in tried and z0 > tried[(x, y)]):
                                return (x, y, z0)

    z0_sq = z0 * z0
    bx2 = sx_sum + dx1 * (drx - z0_sq + z1 * z1)
    if bx2 % 2 != 0:
        return None
    by2 = sy_sum + dy2 * (dry - z0_sq + z2 * z2)
    if by2 % 2 != 0:
        return None
    bx = bx2 // 2
    by = by2 // 2
    mx = dx1 * (z0 - z1)
    my = dy2 * (z0 - z2)
    if z0 > -32:
        z_end = -40
    else:
        z_end = -48
    if mx == 0 and my == 0:
        if bx < 0 or bx >= size or by < 0 or by >= size:
            return None
        sq = r0 - (bx - x0) ** 2 - (by - y0) ** 2
        if sq < 0:
            return None
        dz = (sq ** 0.5 + 0.5) // 1
        if dz * dz != sq:
            return None
        for z in [z0 - dz, z0 + dz]:
            if z <= -32 and z >= -47:
                if not ((bx, by) in tried and z > tried[(bx, by)]):
                    return (bx, by, z)
        return None
    for z in range(-32, z_end, -1):
        x = bx + mx * z
        if x < 0 or x >= size:
            continue
        y = by + my * z
        if y < 0 or y >= size:
            continue
        if (x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2 == r0:
            if not ((x, y) in tried and z > tried[(x, y)]):
                return (x, y, z)
    return None


def ore_dig_to(depth):
    for _ in range(52):
        if get_pos_z() <= depth:
            return True
        if not dig():
            return False
    return get_pos_z() <= depth


def ore_move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_ores()
