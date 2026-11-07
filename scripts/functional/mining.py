from __builtins__ import *

# 派工与按列沟挖来自lb_ores.py；普通全科技田加入单次Jump和爆破钻头。

def mine(item, kind, depth, unlock=None):
    size = get_world_size()
    workers = min(size, max_drones())
    first = unlock != None
    if first:
        jump(unlock)
    empty = 0
    while True:
        if not first:
            clear()
        first = False
        before = num_items(item)
        change_hat(Hats.Explosive_Drill)
        deadline = get_time() + 7200
        handles = []
        local = True
        for owner in range(1, workers):
            handle = spawn_drone(trench, owner, workers, size, kind, depth, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not trench(0, workers, size, kind, depth, deadline):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        gained = num_items(item) - before
        quick_print("mining_cycle", item, gained, get_time(), num_items(item))
        if not local:
            quick_print("采矿动作失败，停止：", item)
            return
        if gained <= 0:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有净收益，停止：", item)
                return
        else:
            empty = 0


def trench(first, stride, size, kind, depth, deadline):
    # 每列一个写者；钻头直接收集的物品计入库存，塌落损失不计产量。
    for x in range(first, size, stride):
        if not move_to(x, 0, size):
            return False
        for y in range(size):
            while get_pos_z() > -depth:
                if get_time() > deadline or get_hardness() >= 10000000:
                    return False
                if num_items(Items.Dynamite) < 1:
                    quick_print("爆破钻头缺少炸药，停止。")
                    return False
                if not dig():
                    return False
            while kind != None and get_ground_type() == kind:
                if get_time() > deadline or num_items(Items.Dynamite) < 1 or not dig():
                    return False
            if y + 1 < size and not move(North):
                return False
    return True


def move_to(tx, ty, size):
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
