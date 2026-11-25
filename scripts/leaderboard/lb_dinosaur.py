from __builtins__ import *
# 完整轮时间：见 docs/leaderboards/lb_dinosaur.md。
# 生成自：scripts/templates/leaderboard/lb_dinosaur.py
# 生成配置：scripts/templates/leaderboard/lb_dinosaur.codegen.json
# 修改策略请编辑母版并重新生成，勿直接修改本文件。

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
            _step = 0
            move(East)
            _step = 1
            move(East)
            _step = 2
            move(East)
            _step = 3
            move(East)
            _step = 4
            move(East)
            _step = 5
            move(East)
            _step = 6
            move(East)
            _step = 7
            move(East)
            _step = 8
            move(East)
            _step = 9
            move(East)
            _step = 10
            move(East)
            _step = 11
            move(East)
            _step = 12
            move(East)
            _step = 13
            move(East)
            _step = 14
            move(East)
            _step = 15
            move(East)
            _step = 16
            move(East)
            _step = 17
            move(East)
            _step = 18
            move(East)
            _step = 19
            move(East)
            _step = 20
            move(East)
            _step = 21
            move(East)
            _step = 22
            move(East)
            _step = 23
            move(East)
            _step = 24
            move(East)
            _step = 25
            move(East)
            _step = 26
            move(East)
            _step = 27
            move(East)
            _step = 28
            move(East)
            _step = 29
            move(East)
            if not move(North):
                break
            _step = 0
            move(West)
            _step = 1
            move(West)
            _step = 2
            move(West)
            _step = 3
            move(West)
            _step = 4
            move(West)
            _step = 5
            move(West)
            _step = 6
            move(West)
            _step = 7
            move(West)
            _step = 8
            move(West)
            _step = 9
            move(West)
            _step = 10
            move(West)
            _step = 11
            move(West)
            _step = 12
            move(West)
            _step = 13
            move(West)
            _step = 14
            move(West)
            _step = 15
            move(West)
            _step = 16
            move(West)
            _step = 17
            move(West)
            _step = 18
            move(West)
            _step = 19
            move(West)
            _step = 20
            move(West)
            _step = 21
            move(West)
            _step = 22
            move(West)
            _step = 23
            move(West)
            _step = 24
            move(West)
            _step = 25
            move(West)
            _step = 26
            move(West)
            _step = 27
            move(West)
            _step = 28
            move(West)
            _step = 29
            move(West)
            ok = True
            for _ in r15:
                if not move(North):
                    ok = False
                    break
                _step = 0
                move(East)
                _step = 1
                move(East)
                _step = 2
                move(East)
                _step = 3
                move(East)
                _step = 4
                move(East)
                _step = 5
                move(East)
                _step = 6
                move(East)
                _step = 7
                move(East)
                _step = 8
                move(East)
                _step = 9
                move(East)
                _step = 10
                move(East)
                _step = 11
                move(East)
                _step = 12
                move(East)
                _step = 13
                move(East)
                _step = 14
                move(East)
                _step = 15
                move(East)
                _step = 16
                move(East)
                _step = 17
                move(East)
                _step = 18
                move(East)
                _step = 19
                move(East)
                _step = 20
                move(East)
                _step = 21
                move(East)
                _step = 22
                move(East)
                _step = 23
                move(East)
                _step = 24
                move(East)
                _step = 25
                move(East)
                _step = 26
                move(East)
                _step = 27
                move(East)
                _step = 28
                move(East)
                _step = 29
                move(East)
                if not move(North):
                    ok = False
                    break
                _step = 0
                move(West)
                _step = 1
                move(West)
                _step = 2
                move(West)
                _step = 3
                move(West)
                _step = 4
                move(West)
                _step = 5
                move(West)
                _step = 6
                move(West)
                _step = 7
                move(West)
                _step = 8
                move(West)
                _step = 9
                move(West)
                _step = 10
                move(West)
                _step = 11
                move(West)
                _step = 12
                move(West)
                _step = 13
                move(West)
                _step = 14
                move(West)
                _step = 15
                move(West)
                _step = 16
                move(West)
                _step = 17
                move(West)
                _step = 18
                move(West)
                _step = 19
                move(West)
                _step = 20
                move(West)
                _step = 21
                move(West)
                _step = 22
                move(West)
                _step = 23
                move(West)
                _step = 24
                move(West)
                _step = 25
                move(West)
                _step = 26
                move(West)
                _step = 27
                move(West)
                _step = 28
                move(West)
                _step = 29
                move(West)
            if not ok:
                break
            if not move(West):
                break
            _step = 0
            move(South)
            _step = 1
            move(South)
            _step = 2
            move(South)
            _step = 3
            move(South)
            _step = 4
            move(South)
            _step = 5
            move(South)
            _step = 6
            move(South)
            _step = 7
            move(South)
            _step = 8
            move(South)
            _step = 9
            move(South)
            _step = 10
            move(South)
            _step = 11
            move(South)
            _step = 12
            move(South)
            _step = 13
            move(South)
            _step = 14
            move(South)
            _step = 15
            move(South)
            _step = 16
            move(South)
            _step = 17
            move(South)
            _step = 18
            move(South)
            _step = 19
            move(South)
            _step = 20
            move(South)
            _step = 21
            move(South)
            _step = 22
            move(South)
            _step = 23
            move(South)
            _step = 24
            move(South)
            _step = 25
            move(South)
            _step = 26
            move(South)
            _step = 27
            move(South)
            _step = 28
            move(South)
            _step = 29
            move(South)
            _step = 30
            move(South)

    change_hat(Hats.Brown_Hat)


def next_apple():
    # type: () -> tuple[int, int]  # pyright: ignore[reportUndefinedVariable]
    # 只在第 500 颗之前站上苹果时调用，measure 返回下一颗的坐标。
    return measure()  # type: ignore


if __name__ == "__main__":
    lb_dinosaur()
