from __builtins__ import *
import production


# ================================================================
# 竹子自动农场
# ----------------------------------------------------------------
# 布局：每隔 LANE_STEP 行留一条空通道行（y = 2, 5, 8, ...），
#       通道行的上一行和下一行种竹子。无人机停在通道格上，
#       就能同时照看南北两侧的两株竹子。
#       高度不是 3 的倍数时，最上面/最下面的行会空着（32 行时空 0 和 31）。
#
# 单株流程（果实位置用 measure() 读取，不需要写死高度）：
#   1. 种下（消耗水稻），等它长到第一个果实；
#   2. hover(measure()) 悬停到果实高度，move 飞进竹子摘掉果实；
#   3. 再等下一个果实，重复摘除；
#   4. 摘掉第三个果实后竹子不再长高，hover(0) 飞进去一次收掉整株，
#      产量 = 被破坏竹节数的平方；
#   5. 原地补种，回到第 1 步。
#
# 多无人机：把所有通道格按蛇形顺序切成连续几段，
#           每台无人机负责一段，互不重叠。
# ================================================================

LANE_START = 2   # 第一条通道行的 y
LANE_STEP = 3    # 通道行间距 = 1 行通道 + 2 行竹子

# 两次检查之间的等待时间。竹子每秒长 1 格（有水更快），
# 这里取“最多要长几格”再加一点余量；提前到访只会白跑一趟，
# 所以宁可比实际晚一点。
WAIT_FIRST = 5.4   # 种下 -> 第一个果实：最多 5 格
WAIT_NEXT = 6.6    # 摘果 -> 下个果实：最多 6 格
WAIT_TOP = 1.4     # 摘掉第三个果实 -> 长回最高：1 格
WAIT_RETRY = 1.0   # 果实还没长出来，过一会儿再来

WARNED = False     # 种不下去时只提示一次


# ----------------------------------------------------------------
# 通道格的蛇形编号
#   i = lane * size + k，偶数 lane 从西往东走，奇数 lane 从东往西走，
#   这样相邻两个编号在网格上也是相邻的。
# ----------------------------------------------------------------
def tile_x(i, size):
    lane = i // size
    if lane % 2 == 0:
        return i % size
    return size - 1 - (i % size)


def tile_y(i, size):
    return LANE_START + (i // size) * LANE_STEP


# 走到某个格子（地图环绕，走较短的一边）。调用前应已在安全高度。
def walk_to(tx, ty, size):
    half = size // 2
    x = get_pos_x()
    d = (tx - x) % size
    if d <= half:
        while d > 0:
            move(East)
            d -= 1
    else:
        d = size - d
        while d > 0:
            move(West)
            d -= 1
    y = get_pos_y()
    d = (ty - y) % size
    if d <= half:
        while d > 0:
            move(North)
            d -= 1
    else:
        d = size - d
        while d > 0:
            move(South)
            d -= 1


# 走到相邻的通道格：同一行就走一格；换行要升到 18 再飞过竹林。
def step_to(a, b, size):
    la = a // size
    lb = b // size
    if la == lb:
        if tile_x(b, size) > tile_x(a, size):
            move(East)
        else:
            move(West)
        return
    hover(18)
    k = 0
    if lb > la:
        while k < LANE_STEP:
            move(North)
            k += 1
    else:
        while k < LANE_STEP:
            move(South)
            k += 1


# ----------------------------------------------------------------
# 照看一株竹子
#   d / back : 从通道格进入竹子的方向 / 回来的方向
#   idx      : 这株竹子在状态表里的下标
# 返回 False 表示该停机（水稻用完）。
# ----------------------------------------------------------------
def tend(d, back, idx, states, due):
    global WARNED

    s = states[idx]

    # 0：空地 —— 清掉残留、翻地、种竹子
    if s == 0:
        hover(0)
        move(d)
        if get_entity_type() != None:
            harvest()
        if get_ground_type() == Grounds.Grassland:
            till()
        if plant(Entities.Bamboo):
            states[idx] = 1
            due[idx] = get_time() + WAIT_FIRST
        else:
            if num_items(Items.Rice) < 1:
                quick_print("水稻用完了，竹子停机。")
                return False
            if not WARNED:
                WARNED = True
                quick_print("种不下竹子：", get_pos_x(), get_pos_y(),
                            "地面", get_ground_type(), "（需要土壤/泥土/珍珠岩）")
        move(back)
        return True

    now = get_time()
    if now < due[idx]:
        return True

    # 4：已经摘过第三个果实，等它长回最高再整株收获并补种
    if s == 4:
        hover(0)
        move(d)
        if plant(Entities.Bamboo):
            states[idx] = 1
            due[idx] = now + WAIT_FIRST
        else:
            states[idx] = 0
        move(back)
        return True

    # 1/2/3：等下一个果实，到高度后再飞进去摘掉
    m = measure(d)
    if m == None:
        states[idx] = 0
        return True

    hover(m)
    move(d)
    if s == 3:
        # 第三个果实：摘掉后竹子不再长高，can_harvest() 会变成 True
        if can_harvest():
            states[idx] = 4
            due[idx] = now + WAIT_TOP
        else:
            due[idx] = now + WAIT_RETRY
    else:
        n = measure()
        if n != None and n > m:
            # 果实摘掉了，measure() 会跳到下一个果实的高度
            states[idx] = s + 1
            due[idx] = now + WAIT_NEXT
        else:
            due[idx] = now + WAIT_RETRY
    move(back)
    return True


# 照看一个通道格（南北两株）
def service(i, lo, size, states, due):
    # 通道格上如果残留了竹子会把悬停高度挡住，先清掉；
    # 草之类的不用管，不影响悬停和移动。
    if get_entity_type() == Entities.Bamboo:
        harvest()
    base = (i - lo) * 2
    if not tend(North, South, base, states, due):
        return False
    if not tend(South, North, base + 1, states, due):
        return False
    return True


# ----------------------------------------------------------------
# 一台无人机的工作循环：在 [lo, hi) 这段通道格上来回走
# ----------------------------------------------------------------
def work(lo, hi, size):
    n = hi - lo
    states = []
    due = []
    k = 0
    while k < n:
        states.append(0)
        states.append(0)
        due.append(0.0)
        due.append(0.0)
        k += 1

    hover(18)
    walk_to(tile_x(lo, size), tile_y(lo, size), size)

    while production.active(Items.Bamboo):
        # 正向：lo -> hi-1
        if not service(lo, lo, size, states, due):
            return
        i = lo + 1
        while i < hi:
            step_to(i - 1, i, size)
            if not service(i, lo, size, states, due):
                return
            i += 1
        # 反向：hi-1 -> lo（折返时不再重复照看端点）
        i = hi - 2
        while i >= lo:
            step_to(i + 1, i, size)
            if not service(i, lo, size, states, due):
                return
            i -= 1


# ----------------------------------------------------------------
# 主入口
# ----------------------------------------------------------------
def bamboo():
    size = get_world_size()
    if num_unlocked(Unlocks.Bamboo) < 1:
        quick_print("还没解锁竹子（Unlocks.Bamboo）。")
        return
    if not hover(18):
        quick_print("当前帽子不能悬停（hover 失败），换一顶帽子再运行。")
        return

    lanes = 0
    y = LANE_START
    while y < size:
        lanes += 1
        y += LANE_STEP
    if lanes < 1:
        quick_print("农场太小，放不下竹子的通道行。")
        return

    total = lanes * size

    # 每台无人机至少管 4 个通道格（8 株），否则来回走路的开销太大
    n = max_drones()
    limit = total // 4
    if n > limit:
        n = limit
    if n < 1:
        n = 1

    # 把通道格切成 n 段连续区间。无人机够多时每段都在同一行里，
    # 这样工作循环里不需要换行。
    bounds = []
    bounds.append(0)
    if n >= lanes:
        base = n // lanes
        extra = n % lanes
        lane = 0
        while lane < lanes:
            if lane > 0:
                bounds.append(lane * size)
            k = base
            if lane < extra:
                k += 1
            s = 1
            while s < k:
                bounds.append(lane * size + s * size // k)
                s += 1
            lane += 1
    else:
        g = 1
        while g < n:
            bounds.append((g * lanes // n) * size)
            g += 1
    bounds.append(total)

    quick_print("竹子农场：", size, "x", size,
                "通道行", lanes, "无人机", n,
                "竹子株数", lanes * size * 2)

    handles = []
    k = 1
    while k < n:
        handle = spawn_drone(work, bounds[k], bounds[k + 1], size)
        if handle == None:
            quick_print("无人机数量到上限了，剩下的区域没有无人机。")
            break
        handles.append(handle)
        k += 1

    work(bounds[0], bounds[1], size)
    for handle in handles:
        wait_for(handle)


if __name__ == "__main__":
    bamboo()