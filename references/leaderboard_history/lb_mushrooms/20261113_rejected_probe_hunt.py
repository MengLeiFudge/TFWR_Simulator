from __builtins__ import *

# 探针 H：带地图的贪心调度。地图缓存每格 (z, 颜色)；只走向"已知可推"的格，
# 到位后用新鲜读数复核再推；候选耗尽时挖最浅的一层制造新高度差。
# 目的：测「每对配对的走访数与动作数」，判断地图调度能否把 visits/merge 压到 2 以下。

DIRECTIONS = [North, East, South, West]
OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def probe(area, deadline):
    began = get_time()
    clear()
    for step in range(256):
        if get_ground_type() == Grounds.Mushroom:
            break
        dig()
    if get_ground_type() != Grounds.Mushroom:
        quick_print("probe_failed", "no_stratum")
        return
    top = get_pos_z()
    height = 0
    for step in range(7):
        if get_ground_type() != Grounds.Mushroom:
            break
        dig()
        height += 1
    quick_print("probe_stratum", height, top, get_time())
    level(top, area)
    quick_print("probe_leveled", get_time())
    hunt(top, area, deadline, began)


def level(top, area):
    for j in range(area):
        for i in range(area):
            x = i
            if j % 2 != 0:
                x = area - 1 - i
            if not move_to(x, j):
                return False
            while get_pos_z() > top:
                if not dig():
                    return False
    return True


def hunt(top, area, deadline, began):
    MAP = {}
    scans = 0
    pushes = 0
    visits = 0
    reseeds = 0
    rounds = 0
    scan_area(MAP, area)
    while get_time() < deadline:
        rounds += 1
        cands = collect(MAP, area)
        scans += 1
        if len(cands) == 0:
            if not reseed(MAP, area):
                quick_print("probe_done", rounds, visits, pushes,
                            num_items(Items.Mushroom), reseeds, get_time() - began)
                return
            reseeds += 1
            continue
        for k in range(len(cands)):
            if get_time() >= deadline:
                break
            cand = cands[k]
            if not move_to(cand[0], cand[1]):
                quick_print("probe_failed", "move", cand)
                return
            visits += 1
            refresh(MAP, cand[0], cand[1])
            if push_here(MAP, cand[0], cand[1]):
                pushes += 1
        if get_time() - began > 4:
            quick_print("probe_round", rounds, scans, visits, pushes,
                        len(cands), reseeds, num_items(Items.Mushroom), get_time())
    quick_print("probe_done", rounds, visits, pushes,
                num_items(Items.Mushroom), reseeds, get_time() - began)


# 逐格读取 z 与颜色，建立初始地图。
def scan_area(MAP, area):
    for j in range(area):
        for i in range(area):
            x = i
            if j % 2 != 0:
                x = area - 1 - i
            move_to(x, j)
            read_here(MAP, x, j)
            for k in range(4):
                read_dir(MAP, x, j, k)


def read_here(MAP, x, y):
    z = get_pos_z()
    t = -1
    if get_ground_type() == Grounds.Mushroom:
        t = measure()
    MAP[(x, y)] = [z, t]
    return z


def read_dir(MAP, x, y, k):
    direction = DIRECTIONS[k]
    dx = OFFSETS[k][0]
    dy = OFFSETS[k][1]
    key = key_of(x + dx, y + dy)
    z = get_pos_z(direction)
    t = -1
    if get_ground_type(direction) == Grounds.Mushroom:
        t = measure(direction)
    MAP[key] = [z, t]


def key_of(x, y):
    size = get_world_size()
    return ((x + size) % size, (y + size) % size)


# 读出当前格与四邻。
def refresh(MAP, x, y):
    read_here(MAP, x, y)
    for k in range(4):
        read_dir(MAP, x, y, k)


# 地图扫描：列出所有「顶面有更深的同色蘑菇邻居」的格。
def collect(MAP, area):
    cands = []
    for y in range(area):
        for x in range(area):
            key = (x, y)
            if key not in MAP:
                continue
            cell = MAP[key]
            if cell[1] < 0:
                continue
            for k in range(4):
                nkey = key_of(x + OFFSETS[k][0], y + OFFSETS[k][1])
                if nkey not in MAP:
                    continue
                other = MAP[nkey]
                if other[1] < 0:
                    continue
                if other[0] < cell[0] and other[1] == cell[1]:
                    cands.append(key)
                    break
    return cands


# 站在 (x,y) 上按新鲜读数找匹配目标并推送。
def push_here(MAP, x, y):
    cell = MAP[(x, y)]
    if cell[1] < 0:
        return False
    for k in range(4):
        nkey = key_of(x + OFFSETS[k][0], y + OFFSETS[k][1])
        if nkey not in MAP:
            continue
        other = MAP[nkey]
        if other[1] != cell[1]:
            continue
        if other[0] >= cell[0]:
            continue
        if not push(DIRECTIONS[k]):
            continue
        return True
    return False


# 候选耗尽：把当前最浅的一层按棋盘子集挖掉，重建高度差。
def reseed(MAP, area):
    shallow = -100000
    have = False
    for y in range(area):
        for x in range(area):
            key = (x, y)
            if key not in MAP:
                continue
            cell = MAP[key]
            if cell[1] < 0:
                continue
            if not have or cell[0] > shallow:
                shallow = cell[0]
                have = True
    if not have:
        return False
    dug = 0
    for y in range(area):
        for x in range(area):
            key = (x, y)
            if key not in MAP:
                continue
            cell = MAP[key]
            if cell[1] < 0 or cell[0] != shallow:
                continue
            if (x + y) % 2 != 0:
                continue
            if not move_to(x, y):
                return dug > 0
            read_here(MAP, x, y)
            if MAP[key][0] != shallow:
                continue
            if dig():
                dug += 1
                read_here(MAP, x, y)
                for k in range(4):
                    read_dir(MAP, x, y, k)
    return dug > 0


def move_to(tx, ty):
    size = get_world_size()
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for step in range(dx):
        if not move(horizontal):
            return False
    for step in range(dy):
        if not move(vertical):
            return False
    return True


if __name__ == "__main__":
    probe(12, 40)
