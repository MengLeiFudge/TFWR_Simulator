from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-sol/open-directions/cactus-active-edges/lb_cactus.py
# C2固定活动逆序边队列代表，非正式成绩。

def lb_cactus():
    while num_items(Items.Cactus) < 33554432:
        dispatch_lines(0, max_drone_num, False)
        dispatch_lines(0, max_drone_num, True)
        goto(0, size - 1)
        harvest()


def dispatch_lines(first, count, columns):
    # 每个分发者也处理一条线；最多31次spawn，子树结束后才返回。
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch_lines, first + left, count - left, columns)
        if handle == None:
            # 容量意外不足时按同一分区顺序执行，不丢弃任务。
            dispatch_lines(first + left, count - left, columns)
        else:
            handles.append(handle)
        count = left
    index = size - 1 - first
    if columns:
        goto(index, 0)
        sort_one_way()
    else:
        goto(0, index)
        plant_and_sort_x()
    for handle in handles:
        wait_for(handle)


size = get_world_size()
max_drone_num = min(max_drones(), size)


def goto(tx, ty):
    size = get_world_size()
    half_size = size // 2
    x, y = get_pos_x(), get_pos_y()
    # x方向
    dx = (tx - x) % size
    if dx <= half_size:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    # y方向
    dy = (ty - y) % size
    if dy <= half_size:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def plant_and_sort_x():
    # plant each row
    for _ in range(size):  # x
        entity = get_entity_type()
        if entity == None or entity == Entities.Grass:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
        # 利用本行铺田的既有访问先消除左邻逆序。
        if get_pos_x() > 0 and measure(West) > measure():
            swap(West)
        move(East)
    # sort x
    sort_one_way("x")


def sort_one_way(axis="y"):
    forward = North
    x, y = get_pos_x(), get_pos_y()
    if axis == "x":
        forward = East
    queued = []
    pending = []
    incoming = []
    for i in range(32):
        queued.append(i < 31)
        if i < 31:
            incoming.append(i)
    while incoming or pending:
        if not pending:
            while incoming:
                pending.append(incoming.pop())
        edge = pending.pop()
        queued[edge] = False
        if axis == "x":
            goto(edge, y)
        else:
            goto(x, edge)
        if measure() > measure(forward):
            swap(forward)
            # 当前边已修复，只把可能因本次交换失序的相邻边重新入队。
            for other in [edge - 1, edge + 1]:
                if 0 <= other < 31 and not queued[other]:
                    queued[other] = True
                    incoming.append(other)


if __name__ == "__main__":
    lb_cactus()
