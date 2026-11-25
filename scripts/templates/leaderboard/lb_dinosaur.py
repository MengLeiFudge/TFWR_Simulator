from __builtins__ import *
# 完整轮时间：见 docs/leaderboards/lb_dinosaur.md。

# 前半段在两组坐标轴之间追果，后半段沿固定梳形回路补满。

def lb_dinosaur():
    set_world_size(32)
    clear()
    change_hat(Hats.Dinosaur_Hat)

    vis = []
    i = 0
    while i < 1056:
        vis.append(0)
        i += 1

    # Start at (0, 0) standing on apple #0; measure() returns apple #1; move East to (1, 0) [Odd parity, q=1]
    ax, ay = next_apple()
    ac = ay * 32 + ax
    acx = ax * 32 + 31 - ay
    move(East)
    c = 1
    cx = 63
    ry = False
    eaten = 1
    gen = 2
    vis_L = 360
    switch_L = 500

    # 循环顶部在奇色格，ry 区分横坐标与纵坐标哪个为奇数。
    while True:
        # --- ODD STEP (q=1 if not ry, q=3 if ry) ---
        if c == ac:
            eaten += 1
            ax, ay = next_apple()
            ac = ay * 32 + ax
            acx = ax * 32 + 31 - ay
            if eaten == vis_L:
                break
        if ry:
            # q=3 (even x, odd y): CROSS=West, STAY=South
            if acx < cx:
                # 2-step straight West burst while cx - acx > 63 and ac < c
                while cx - acx > 63 and ac < c and move(West):
                    c -= 1
                    cx -= 32
                    if move(West):
                        c -= 1
                        cx -= 32
                    else:
                        move(North)
                        c += 32
                        cx -= 1
                        ry = False
                        break
                if not ry:
                    continue
                if c == ac:
                    eaten += 1
                    ax, ay = next_apple()
                    ac = ay * 32 + ax
                    acx = ax * 32 + 31 - ay
                    if eaten == vis_L:
                        break
                if acx < cx:
                    if move(West):
                        c -= 1
                        cx -= 32
                    else:
                        move(South)
                        c -= 32
                        cx += 1
                        ry = False
                else:
                    if move(South):
                        c -= 32
                        cx += 1
                        ry = False
                    else:
                        move(West)
                        c -= 1
                        cx -= 32
            else:
                # 2-step straight South burst while c - ac > 63
                while c - ac > 63 and move(South):
                    c -= 32
                    cx += 1
                    if move(South):
                        c -= 32
                        cx += 1
                    else:
                        move(East)
                        c += 1
                        cx += 32
                        ry = False
                        break
                if not ry:
                    continue
                if c == ac:
                    eaten += 1
                    ax, ay = next_apple()
                    ac = ay * 32 + ax
                    acx = ax * 32 + 31 - ay
                    if eaten == vis_L:
                        break
                if acx < cx:
                    if move(West):
                        c -= 1
                        cx -= 32
                    else:
                        move(South)
                        c -= 32
                        cx += 1
                        ry = False
                else:
                    if move(South):
                        c -= 32
                        cx += 1
                        ry = False
                    else:
                        move(West)
                        c -= 1
                        cx -= 32
        else:
            # q=1 (odd x, even y): CROSS=East, STAY=North
            if acx > cx:
                # 2-step straight East burst while acx - cx > 63 and ac > c
                while acx - cx > 63 and ac > c and move(East):
                    c += 1
                    cx += 32
                    if move(East):
                        c += 1
                        cx += 32
                    else:
                        move(South)
                        c -= 32
                        cx += 1
                        ry = True
                        break
                if ry:
                    continue
                if c == ac:
                    eaten += 1
                    ax, ay = next_apple()
                    ac = ay * 32 + ax
                    acx = ax * 32 + 31 - ay
                    if eaten == vis_L:
                        break
                if acx > cx:
                    if move(East):
                        c += 1
                        cx += 32
                    else:
                        move(North)
                        c += 32
                        cx -= 1
                        ry = True
                else:
                    if move(North):
                        c += 32
                        cx -= 1
                        ry = True
                    else:
                        move(East)
                        c += 1
                        cx += 32
            else:
                # 2-step straight North burst while ac - c > 63
                while ac - c > 63 and move(North):
                    c += 32
                    cx -= 1
                    if move(North):
                        c += 32
                        cx -= 1
                    else:
                        move(West)
                        c -= 1
                        cx -= 32
                        ry = True
                        break
                if ry:
                    continue
                if c == ac:
                    eaten += 1
                    ax, ay = next_apple()
                    ac = ay * 32 + ax
                    acx = ax * 32 + 31 - ay
                    if eaten == vis_L:
                        break
                if acx > cx:
                    if move(East):
                        c += 1
                        cx += 32
                    else:
                        move(North)
                        c += 32
                        cx -= 1
                        ry = True
                else:
                    if move(North):
                        c += 32
                        cx -= 1
                        ry = True
                    else:
                        move(East)
                        c += 1
                        cx += 32

        # --- EVEN STEP (q=2 if ry, q=0 if not ry) ---
        if c == ac:
            eaten += 1
            ax, ay = next_apple()
            ac = ay * 32 + ax
            acx = ax * 32 + 31 - ay
            if eaten == vis_L:
                # Need to enter Phase 1B at Odd parity -> take 1 Even step first!
                if ry:
                    if ac > c:
                        if move(North):
                            c += 32
                            cx -= 1
                            ry = False
                        else:
                            move(West)
                            c -= 1
                            cx -= 32
                    else:
                        if move(West):
                            c -= 1
                            cx -= 32
                        else:
                            move(North)
                            c += 32
                            cx -= 1
                            ry = False
                else:
                    if ac < c:
                        if move(South):
                            c -= 32
                            cx += 1
                            ry = True
                        else:
                            move(East)
                            c += 1
                            cx += 32
                    else:
                        if move(East):
                            c += 1
                            cx += 32
                        else:
                            move(South)
                            c -= 32
                            cx += 1
                            ry = True
                break
        if ry:
            # q=2 (odd x, odd y): CROSS=North, STAY=West
            if ac > c:
                if move(North):
                    c += 32
                    cx -= 1
                    ry = False
                else:
                    move(West)
                    c -= 1
                    cx -= 32
            else:
                if move(West):
                    c -= 1
                    cx -= 32
                else:
                    move(North)
                    c += 32
                    cx -= 1
                    ry = False
        else:
            # q=0 (even x, even y): CROSS=South, STAY=East
            if ac < c:
                if move(South):
                    c -= 32
                    cx += 1
                    ry = True
                else:
                    move(East)
                    c += 1
                    cx += 32
            else:
                if move(East):
                    c += 1
                    cx += 32
                else:
                    move(South)
                    c -= 32
                    cx += 1
                    ry = True

    # =========================================================
    # PHASE 1B: L = vis_L .. switch_L (Bipartite Zero-rx with padded vis[1056]!)
    # Invariant at top of loop: Odd parity!
    # =========================================================
    gen += 1
    odd_exit = True
    while True:
        # --- ODD STEP ---
        if c == ac:
            eaten += 1
            ax, ay = next_apple()
            ac = ay * 32 + ax
            acx = ax * 32 + 31 - ay
            gen += 1
            if eaten == switch_L:
                odd_exit = True
                break
        vis[c] = gen
        if ry:
            if acx < cx:
                if vis[c - 1] != gen and move(West):
                    c -= 1
                    cx -= 32
                elif move(South):
                    c -= 32
                    cx += 1
                    ry = False
                else:
                    move(West)
                    c -= 1
                    cx -= 32
            else:
                if vis[c - 32] != gen and move(South):
                    c -= 32
                    cx += 1
                    ry = False
                elif move(West):
                    c -= 1
                    cx -= 32
                else:
                    move(South)
                    c -= 32
                    cx += 1
                    ry = False
        else:
            if acx > cx:
                if vis[c + 1] != gen and move(East):
                    c += 1
                    cx += 32
                elif move(North):
                    c += 32
                    cx -= 1
                    ry = True
                else:
                    move(East)
                    c += 1
                    cx += 32
            else:
                if vis[c + 32] != gen and move(North):
                    c += 32
                    cx -= 1
                    ry = True
                elif move(East):
                    c += 1
                    cx += 32
                else:
                    move(North)
                    c += 32
                    cx -= 1
                    ry = True

        # --- EVEN STEP ---
        if c == ac:
            eaten += 1
            ax, ay = next_apple()
            ac = ay * 32 + ax
            acx = ax * 32 + 31 - ay
            gen += 1
            if eaten == switch_L:
                odd_exit = False
                break
        vis[c] = gen
        if ry:
            if ac > c:
                if vis[c + 32] != gen and move(North):
                    c += 32
                    cx -= 1
                    ry = False
                elif move(West):
                    c -= 1
                    cx -= 32
                else:
                    move(North)
                    c += 32
                    cx -= 1
                    ry = False
            else:
                if vis[c - 1] != gen and move(West):
                    c -= 1
                    cx -= 32
                elif move(North):
                    c += 32
                    cx -= 1
                    ry = False
                else:
                    move(West)
                    c -= 1
                    cx -= 32
        else:
            if ac < c:
                if vis[c - 32] != gen and move(South):
                    c -= 32
                    cx += 1
                    ry = True
                elif move(East):
                    c += 1
                    cx += 32
                else:
                    move(South)
                    c -= 32
                    cx += 1
                    ry = True
            else:
                if vis[c + 1] != gen and move(East):
                    c += 1
                    cx += 32
                elif move(South):
                    c -= 32
                    cx += 1
                    ry = True
                else:
                    move(East)
                    c += 1
                    cx += 32

    # =========================================================
    # PHASE 2: Unwind onto Pure Comb (~700-1400 moves) & align to (0, 0)
    # =========================================================
    hx = c % 32
    hy = c // 32
    rx = (hx % 2) == 1
    ry = (hy % 2) == 1
    unwound = 0
    while not (unwound >= eaten + 2 and c == 0):
        if c == ac:
            eaten += 1
            if eaten == 1023:
                break
            m = measure()
            if m == None:
                break
            ax, ay = m  # type: ignore
            ac = ay * 32 + ax  # type: ignore
        if ry:
            if rx:
                if hx == 1 and hy < 31:
                    if move(North):
                        hy += 1
                        c += 32
                        ry = False
                        unwound += 1
                    else:
                        move(West)
                        hx -= 1
                        c -= 1
                        rx = False
                        unwound = 0
                else:
                    if move(West):
                        hx -= 1
                        c -= 1
                        rx = False
                        unwound += 1
                    else:
                        move(North)
                        hy += 1
                        c += 32
                        ry = False
                        unwound = 0
            else:
                if hx > 0:
                    if move(West):
                        hx -= 1
                        c -= 1
                        rx = True
                        unwound += 1
                    else:
                        move(South)
                        hy -= 1
                        c -= 32
                        ry = False
                        unwound = 0
                else:
                    if move(South):
                        hy -= 1
                        c -= 32
                        ry = False
                        unwound += 1
                    else:
                        move(West)
                        hx -= 1
                        c -= 1
                        rx = True
                        unwound = 0
        else:
            if rx:
                if hx < 31:
                    if move(East):
                        hx += 1
                        c += 1
                        rx = False
                        unwound += 1
                    else:
                        move(North)
                        hy += 1
                        c += 32
                        ry = True
                        unwound = 0
                else:
                    if move(North):
                        hy += 1
                        c += 32
                        ry = True
                        unwound += 1
                    else:
                        move(East)
                        hx += 1
                        c += 1
                        rx = False
                        unwound = 0
            else:
                if hx == 0 and hy > 0:
                    if move(South):
                        hy -= 1
                        c -= 32
                        ry = True
                        unwound += 1
                    else:
                        move(East)
                        hx += 1
                        c += 1
                        rx = True
                        unwound = 0
                else:
                    if move(East):
                        hx += 1
                        c += 1
                        rx = True
                        unwound += 1
                    else:
                        move(South)
                        hy -= 1
                        c -= 32
                        ry = True
                        unwound = 0

    # 切回固定回路后，整行移动由生成器展开。
    if eaten < 1023:
        r15 = range(15)
        while True:
            if not move(East):
                break
            #@unroll
            for _step in range(30):
                move(East)
            if not move(North):
                break
            #@unroll
            for _step in range(30):
                move(West)
            ok = True
            for _ in r15:
                if not move(North):
                    ok = False
                    break
                #@unroll
                for _step in range(30):
                    move(East)
                if not move(North):
                    ok = False
                    break
                #@unroll
                for _step in range(30):
                    move(West)
            if not ok:
                break
            if not move(West):
                break
            #@unroll
            for _step in range(31):
                move(South)

    change_hat(Hats.Brown_Hat)


def next_apple():
    # type: () -> tuple[int, int]  # pyright: ignore[reportUndefinedVariable]
    # 只在第 500 颗之前站上苹果时调用，measure 返回下一颗的坐标。
    return measure()  # type: ignore


if __name__ == "__main__":
    lb_dinosaur()
