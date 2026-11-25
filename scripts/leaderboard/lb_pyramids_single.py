from __builtins__ import *
# 完整轮时间：本版尚未实机；本地默认随机完整验收结果见同名策略文档。


def lb_pyramids_single():
    set_world_size(5)
    Dirt = Grounds.Dirt
    Sand = Grounds.Sand
    Limestone = Grounds.Limestone
    Sunflower = Entities.Sunflower
    Power = Items.Power
    E = East
    W = West
    N = North
    S = South

    while num_items(Power) < 30000:
        # 零移动浅层重掷：仅在 floor == -3 时 (0,0)/(1,0)/(0,1) 表层会出现 Dirt
        clear()
        while get_ground_type() != Dirt and get_ground_type(E) != Dirt and get_ground_type(N) != Dirt:
            clear()
        # (0,0) 挖至 -2；若非 Sand 则验 -3 是否为 Limestone（排错并原地补底）
        dig()
        dig()
        pe = False
        if get_ground_type() != Sand:
            dig()
            if get_ground_type() != Limestone:
                continue
            place(Sand)
            pe = True
        eroded_mid = []
        # s 状态：0=前格挖至-2（当前格已自动塌至-1，只需1 dig）；1=前格挖至-3（当前格已至-2，0 dig）；2=前格跳过dig（需查z）
        s = 0
        if pe:
            s = 1

        # (1,0) 1t 向北窥视 (1,1)
        move(E)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(N) != Sand or (s == 2 and get_pos_z(N) != -1):
            eroded_mid.append((1, 1))

        # (2,0) 1t 向北窥视 (2,1)
        move(E)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(N) != Sand or (s == 2 and get_pos_z(N) != -1):
            eroded_mid.append((2, 1))

        # (3,0) 1t 向北窥视 (3,1)
        move(E)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(N) != Sand or (s == 2 and get_pos_z(N) != -1):
            eroded_mid.append((3, 1))

        # (4,0)
        move(E)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (4,1)
        move(N)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (4,2) 1t 向西窥视 (3,2)
        move(N)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(W) != Sand or (s == 2 and get_pos_z(W) != -1):
            eroded_mid.append((3, 2))

        # (4,3)
        move(N)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (4,4)
        move(N)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (3,4) 1t 向南窥视 (3,3)
        move(W)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(S) != Sand or (s == 2 and get_pos_z(S) != -1):
            eroded_mid.append((3, 3))

        # (2,4) 1t 向南窥视 (2,3)
        move(W)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(S) != Sand or (s == 2 and get_pos_z(S) != -1):
            eroded_mid.append((2, 3))

        # (1,4) 1t 向南窥视 (1,3)
        move(W)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1
        if get_ground_type(S) != Sand or (s == 2 and get_pos_z(S) != -1):
            eroded_mid.append((1, 3))

        # (0,4)
        move(W)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (0,3)
        move(S)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
            s = 0
        else:
            s = 2
        if get_ground_type() != Sand:
            dig()
            place(Sand)
            s = 1

        # (0,2)：按 (0,1) 与中环缺柱位置择优决定下挖 (0,2) 至 -3 自动清 (0,1) 或直接步入 (0,1)
        move(S)
        if s == 0:
            dig()
        elif s == 2:
            if get_pos_z() == 0:
                dig()
            dig()
        if get_ground_type(E) != Sand or (s == 1 and get_pos_z(E) != -1):
            eroded_mid.append((1, 2))
        cx = 0
        cy = 2
        if pe:
            if get_ground_type() != Sand:
                dig()
                place(Sand)
                if get_pos_z() == -3:
                    move(E)
                    move(E)
                    harvest()
                    continue
            if get_ground_type(S) != Sand:
                move(S)
                cy = 1
                dig()
                place(Sand)
                if get_pos_z() == -3:
                    move(E)
                    move(E)
                    move(N)
                    harvest()
                    continue
        elif len(eroded_mid) == 0:
            dig()
            place(Sand)
            if get_pos_z() == -3:
                move(E)
                move(E)
                harvest()
                continue
            if get_ground_type(S) != Sand:
                move(S)
                cy = 1
                dig()
                place(Sand)
                if get_pos_z() == -3:
                    move(E)
                    move(E)
                    move(N)
                    harvest()
                    continue
        else:
            if get_ground_type() != Sand:
                dig()
                place(Sand)
                if get_pos_z() == -3:
                    move(E)
                    move(E)
                    harvest()
                    continue
                if get_ground_type(S) != Sand:
                    move(S)
                    cy = 1
                    dig()
                    place(Sand)
                    if get_pos_z() == -3:
                        move(E)
                        move(E)
                        move(N)
                        harvest()
                        continue
            else:
                has_bot = False
                for ex, ey in eroded_mid:
                    if ey == 1:
                        has_bot = True
                        break
                if has_bot:
                    move(S)
                    cy = 1
                    dig()
                    if get_pos_z() == -3:
                        move(E)
                        move(E)
                        move(N)
                        harvest()
                        continue
                    if get_ground_type() != Sand:
                        dig()
                        place(Sand)
                        if get_pos_z() == -3:
                            move(E)
                            move(E)
                            move(N)
                            harvest()
                            continue
                else:
                    dig()
                    place(Sand)
                    if get_pos_z() == -3:
                        move(E)
                        move(E)
                        harvest()
                        continue
                    if get_ground_type(S) != Sand:
                        move(S)
                        cy = 1
                        dig()
                        place(Sand)
                        if get_pos_z() == -3:
                            move(E)
                            move(E)
                            move(N)
                            harvest()
                            continue

        n_mid = len(eroded_mid)
        if n_mid == 0:
            move(E)
            move(E)
            if cy == 1:
                move(N)
            if get_entity_type() != Sunflower:
                while get_ground_type() != Limestone:
                    dig()
                place(Sand)
                place(Sand)
                place(Sand)
            harvest()
            continue

        # 按 5×5 环面最近邻顺序修复中环缺柱底层，必要时先补中心底层再回填二层
        done = False
        need_layer2 = []
        while len(eroded_mid) > 0:
            best_i = 0
            best_d = 99
            for k in range(len(eroded_mid)):
                tx, ty = eroded_mid[k]
                dx = (tx - cx) % 5
                if dx > 2:
                    dx = 5 - dx
                dy = (ty - cy) % 5
                if dy > 2:
                    dy = 5 - dy
                d = dx + dy
                if d < best_d:
                    best_d = d
                    best_i = k
            mx, my = eroded_mid.pop(best_i)
            pyramid_move_5(cx, cy, mx, my)
            cx = mx
            cy = my
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
        if done:
            pyramid_move_5(cx, cy, 2, 2)
            harvest()
            continue
        n2 = len(need_layer2)
        if n2 > 0:
            center_eroded = False
            lx, ly = need_layer2[n2 - 1]
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
                    pyramid_move_5(cx, cy, 2, 2)
                    cx = 2
                    cy = 2
                    while get_ground_type() != Limestone:
                        dig()
                    place(Sand)
                i = len(need_layer2) - 1
                while i >= 0:
                    mx, my = need_layer2[i]
                    pyramid_move_5(cx, cy, mx, my)
                    cx = mx
                    cy = my
                    if get_pos_z() == -3:
                        done = True
                        break
                    place(Sand)
                    if get_pos_z() == -3:
                        done = True
                        break
                    i -= 1
        pyramid_move_5(cx, cy, 2, 2)
        if not done and get_entity_type() != Sunflower:
            if get_ground_type() != Sand and get_ground_type() != Limestone:
                while get_ground_type() != Limestone:
                    dig()
            for _ in range(3):
                if get_entity_type() == Sunflower:
                    break
                place(Sand)
        harvest()


def pyramid_move_5(cx, cy, tx, ty):
    dx = (tx - cx) % 5
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
    dy = (ty - cy) % 5
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
    lb_pyramids_single()
