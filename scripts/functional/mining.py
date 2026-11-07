from __builtins__ import *
import production


# 满科技普通田仅一台爆破钻；固定四格间距蛇形钻孔，收取真实爆破掉落。
def mine(item, kind, depth, unlock=None):
    size = get_world_size()
    first = unlock != None
    if first:
        production.jump_once(unlock)
    empty = 0
    while production.active(item):
        if not first:
            clear()
        first = False
        before = num_items(item)
        change_hat(Hats.Explosive_Drill)
        deadline = get_time() + 7200
        for row in range((size + 3) // 4):
            y = min(size - 1, 2 + row * 4)
            for offset in range((size + 3) // 4):
                column = offset
                if row % 2 == 1:
                    column = (size + 3) // 4 - 1 - offset
                x = min(size - 1, 2 + column * 4)
                if not move_to(x, y, size):
                    quick_print("采矿移动失败，停止：", item)
                    return
                while get_pos_z() > -depth:
                    if get_time() > deadline or get_hardness() >= 10000000:
                        quick_print("采矿到达时间或硬度边界，停止：", item, get_pos_z())
                        return
                    if num_items(Items.Dynamite) < 1 or not dig():
                        quick_print("炸药不足或爆破失败，停止：", item)
                        return
                while kind != None and get_ground_type() == kind:
                    if get_time() > deadline or num_items(Items.Dynamite) < 1 or not dig():
                        quick_print("矿层开采失败，停止：", item)
                        return
        gained = num_items(item) - before
        quick_print("mining_cycle", item, gained, get_time(), num_items(item))
        if gained <= 0:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有净收益，停止：", item)
                return
        else:
            empty = 0


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
