from __builtins__ import *
# 完整轮时间：340.530秒（本地C#构建26732695，game_leaderboard_random 22轮累计7491.654秒，SD 12.304秒，标准95%CI±5.455秒／自适应95%CI±9.827秒，0失败0警告；尚待实机验证）。


def lb_ores_single():
    size = get_world_size()
    deadline = get_time() + 7200
    goal = 4000
    for cycle in range(128):
        cur_q = num_items(Items.Quartz)
        if cur_q >= goal:
            quick_print("ores_done", True, get_time(), cur_q)
            return
        rem_q = goal - cur_q
        iron_need = rem_q // 14 + 24
        if iron_need > 80:
            iron_need = 80
        if num_items(Items.Iron) < 20:
            if not ore_fund(iron_need, size, deadline):
                quick_print("ores_failed", "fund", cycle, get_time())
                return
        clear()
        before = cur_q
        # Single shallow Dirt anchor at (0,0) z=-8 (neighbors cave in for free; fallback to -11 if needed).
        if not ore_dig_to(-8):
            return
        spheres = []
        tried = {}
        just_mined = False
        voronoi_steps = 0
        for step in range(44):
            cur_q = num_items(Items.Quartz)
            if cur_q >= goal:
                break
            if num_items(Items.Iron) < 5:
                break
            if get_time() > deadline:
                return
            adj = ore_check_adj_quartz(size)
            if adj != None:
                tx, ty, tz = adj
                if not ore_move_to(tx, ty, size):
                    return
                if not ore_mine_quartz_col(goal):
                    return
                just_mined = True
                voronoi_steps = 0
                continue
            x0 = get_pos_x()
            y0 = get_pos_y()
            z0 = get_pos_z()
            d0 = prospect_quartz()
            if d0 == None:
                if z0 > -11:
                    if not ore_dig_to(-11):
                        return
                    continue
                break
            r0 = (d0 * d0 + 0.5) // 1
            spheres.append((x0, y0, z0, r0))
            target = None
            if just_mined and r0 <= 2:
                target = ore_track_shift(x0, y0, z0, r0, size, spheres)
                just_mined = False
            if target == None:
                res = ore_triangulate(x0, y0, z0, r0, size, spheres, tried, voronoi_steps < 2)
                if res == None:
                    if z0 > -11:
                        if not ore_move_to(x0, y0, size) or not ore_dig_to(-11):
                            return
                        continue
                    break
                if res[0] == -1:
                    voronoi_steps += 1
                    if not ore_move_to(res[1], res[2], size):
                        return
                    just_mined = False
                    continue
                target = res
            voronoi_steps = 0
            tx, ty, tz = target
            if not ore_approach_target(tx, ty, size):
                return
            iron_cap = (goal - cur_q) // 12 + 24
            if iron_cap > 96:
                iron_cap = 96
            found = False
            for _ in range(52):
                g = get_ground_type()
                if g == Grounds.Quartz:
                    if not dig():
                        return
                    found = True
                    if num_items(Items.Quartz) >= goal:
                        break
                    continue
                if found or get_pos_z() < tz:
                    break
                if not dig():
                    return
                if g == Grounds.Iron and num_items(Items.Iron) < iron_cap - 16:
                    ore_harvest_adj_iron(size, iron_cap)
            if found:
                just_mined = True
            else:
                tried[(tx, ty)] = get_pos_z()
                just_mined = False
        quick_print("ores_cycle", cycle, num_items(Items.Quartz) - before, get_time(), num_items(Items.Quartz), num_items(Items.Iron))
    quick_print("ores_failed", "cycle_limit", get_time())


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


def ore_mine_quartz_col(goal):
    for _ in range(52):
        if get_ground_type() == Grounds.Quartz:
            if not dig():
                return False
            if num_items(Items.Quartz) >= goal:
                return True
        else:
            break
    return True


def ore_harvest_adj_iron(size, cap_iron):
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
            if not move(rev_dir):
                return


def ore_approach_target(tx, ty, size):
    cx = get_pos_x()
    cy = get_pos_y()
    z_cur = get_pos_z()
    dx_nw = abs(tx - cx)
    dy_nw = abs(ty - cy)
    dist_nw = dx_nw + dy_nw
    if z_cur > -27 or dist_nw < 2:
        return ore_move_to(tx, ty, size)
    dx_w = dx_nw
    if dx_w > size - dx_w:
        dx_w = size - dx_w
    dy_w = dy_nw
    if dy_w > size - dy_w:
        dy_w = size - dy_w
    if dist_nw > dx_w + dy_w + 3:
        return ore_move_to(tx, ty, size)
    while cx != tx or cy != ty:
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
                if not dig():
                    return False
        if not move(d):
            return False
        cx = nx
        cy = ny
    return True


def ore_fund(goal_iron, size, deadline):
    for cycle in range(16):
        if num_items(Items.Iron) >= goal_iron:
            return True
        if get_time() > deadline:
            return False
        clear()
        for cx, cy in [(0, 0), (4, 4), (0, 4), (4, 0)]:
            if num_items(Items.Coal) >= 12:
                break
            if not ore_move_to(cx, cy, size) or not ore_dig_to(-16):
                return False
        for vein_step in range(12):
            if num_items(Items.Iron) >= goal_iron or num_items(Items.Coal) < 1:
                break
            reached = False
            for _ in range(2 * size):
                if num_items(Items.Coal) < 1:
                    break
                direction = prospect_iron()
                if direction == None:
                    reached = True
                    break
                if not move(direction):
                    return False
            if not reached:
                break
            found = False
            for _ in range(34):
                if num_items(Items.Iron) >= goal_iron:
                    return True
                if get_ground_type() == Grounds.Iron:
                    if not dig():
                        return False
                    found = True
                    ore_harvest_adj_iron(size, goal_iron)
                elif found or get_pos_z() <= -32:
                    break
                else:
                    if not dig():
                        return False
            if not found:
                break
        quick_print("ores_fund", cycle, num_items(Items.Coal), num_items(Items.Iron), get_time())
    return num_items(Items.Iron) >= goal_iron


def ore_track_shift(x0, y0, z0, r0, size, spheres):
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
        spheres.append((nx, y0, z1, r1))
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
        spheres.append((x0, ny, z2, r2))
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
        spheres.append((nx, y0, z1, r1))
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
        spheres.append((x0, ny, z2, r2))
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


def ore_triangulate(x0, y0, z0, r0, size, spheres, tried, allow_escape):
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
    spheres.append((nx1, y0, z1, r1))

    if z0 > -32:
        if not move(dy_dir):
            return None
        z2 = get_pos_z()
        d2 = prospect_quartz()
        if d2 == None:
            return None
        r2 = (d2 * d2 + 0.5) // 1
        spheres.append((nx1, ny2, z2, r2))
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
        spheres.append((x0, ny2, z3, r3))
        p = ore_solve_l_shape(x0, y0, z0, r0, nx1, z1, r1, ny2, z3, r3, size, tried)
        if p != None:
            return p
        p = ore_solve_l_shape(x0, ny2, z3, r3, nx1, z2, r2, y0, z0, r0, size, tried)
        if p != None:
            return p
        p = ore_solve_l_shape(nx1, ny2, z2, r2, x0, z3, r3, y0, z1, r1, size, tried)
        if p != None:
            return p
        if allow_escape and num_items(Items.Iron) >= 9:
            return ore_voronoi_escape(x0, y0, r0, nx1, y0, r1, x0, ny2, r3, nx1, ny2, r2, size)
        return ore_fallback_sphere(x0, y0, z0, r0, nx1, y0, z1, r1, x0, ny2, z3, r3, nx1, ny2, z2, r2, size, spheres, tried)

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
    spheres.append((x0, ny2, z2, r2))

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
    spheres.append((nx1, ny2, z3, r3))

    p = ore_solve_l_shape(nx1, ny2, z3, r3, x0, z2, r2, y0, z1, r1, size, tried)
    if p != None:
        return p
    p = ore_solve_l_shape(nx1, y0, z1, r1, x0, z0, r0, ny2, z3, r3, size, tried)
    if p != None:
        return p
    p = ore_solve_l_shape(x0, ny2, z2, r2, nx1, z3, r3, y0, z0, r0, size, tried)
    if p != None:
        return p
    if allow_escape and num_items(Items.Iron) >= 9:
        return ore_voronoi_escape(x0, y0, r0, nx1, y0, r1, x0, ny2, r2, nx1, ny2, r3, size)
    return ore_fallback_sphere(x0, y0, z0, r0, nx1, y0, z1, r1, x0, ny2, z2, r2, nx1, ny2, z3, r3, size, spheres, tried)


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
    if bx == x0 and x0 != x1:
        tx = bx + (x0 - x1)
    else:
        tx = bx + (x1 - x0)
    if by == y0 and y0 != y2:
        ty = by + (y0 - y2)
    else:
        ty = by + (y2 - y0)
    if tx < 0:
        tx = 0
    if tx >= size:
        tx = size - 1
    if ty < 0:
        ty = 0
    if ty >= size:
        ty = size - 1
    if tx == x0 and ty == y0:
        tx = bx
        ty = by
    return (-1, tx, ty)


def ore_fallback_sphere(x0, y0, z0, r0, x1, y1, z1, r1, x2, y2, z2, r2, x3, y3, z3, r3, size, spheres, tried):
    best = None
    best_score = 100000000
    n_sp = len(spheres)
    start_sp = n_sp - 8
    if start_sp < 0:
        start_sp = 0
    for x in range(size):
        dx = x - x0
        dx2 = dx * dx
        if dx2 > r0:
            continue
        for y in range(size):
            dy = y - y0
            sq = r0 - dx2 - dy * dy
            if sq < 0:
                continue
            dz = (sq ** 0.5 + 0.5) // 1
            if dz * dz != sq:
                continue
            for z in [z0 - dz, z0 + dz]:
                if z > -32 or z < -47:
                    continue
                if (x, y) in tried and z > tried[(x, y)]:
                    continue
                valid = True
                for i in range(start_sp, n_sp):
                    sx, sy, sz, sr = spheres[i]
                    if (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2 < sr:
                        valid = False
                        break
                if not valid:
                    continue
                score = (x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2 - r1
                score += (x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2 - r2
                score += (x - x3) ** 2 + (y - y3) ** 2 + (z - z3) ** 2 - r3
                if score < best_score:
                    best_score = score
                    best = (x, y, z)
    return best


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
    lb_ores_single()
