from __builtins__ import *
# 完整轮时间：未取得（本地游戏随机完整抽样均值 4:18.670）。
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。

def lb_wood_single():
    global c_hay
    global c_wood
    global IS_EVEN
    global is_tree
    global is_soil
    global wants
    global trees_done
    set_world_size(8)
    clear()
    cost = get_cost(Entities.Carrot)
    c_hay = cost[Items.Hay]
    c_wood = cost[Items.Wood]
    IS_EVEN = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]
    is_tree = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    is_soil = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    wants = {}
    trees_done = 0
    while True:
        if do_even(0):
            return
        move(North)
        # 双列折返只访问 y=1..7，最后一段一起扫 y=0。
        for base in range(0, 64, 16):
            do_odd(base + 1)
            #@unroll
            for offset in range(2, 8, 2):
                move(North)
                if do_even(base + offset):
                    return
                move(North)
                do_odd(base + offset + 1)
            move(East)
            if do_even(base + 15):
                return
            #@unroll
            for offset in range(14, 8, -2):
                move(South)
                do_odd(base + offset)
                move(South)
                if do_even(base + offset - 1):
                    return
            if base < 48:
                move(East)
        move(South)
        do_odd(56)
        #@unroll
        for idx in range(48, 15, -16):
            move(West)
            if do_even(idx):
                return
            move(West)
            do_odd(idx - 8)
        move(West)

def do_even(idx):
    global trees_done
    if idx in wants:
        c = wants.pop(idx)
        if is_tree[idx]:
            harvest()
            is_tree[idx] = 0
            trees_done += 1
            if trees_done >= 1218 and num_items(Items.Wood) >= 500000000:
                return True
            if c == Entities.Grass:
                if is_soil[idx]:
                    till()
                    is_soil[idx] = 0
            elif c == Entities.Bush:
                plant(Entities.Bush)
            else:
                if num_items(Items.Hay) >= c_hay and num_items(Items.Wood) >= c_wood:
                    if not is_soil[idx]:
                        till()
                        is_soil[idx] = 1
                    plant(Entities.Carrot)
                else:
                    plant(Entities.Bush)
        else:
            e = get_entity_type()
            if e != c:
                if c == Entities.Grass:
                    if is_soil[idx]:
                        till()
                        is_soil[idx] = 0
                    else:
                        harvest()
                elif c == Entities.Bush:
                    if e != Entities.Grass and e != None:
                        harvest()
                    plant(Entities.Bush)
                else:
                    if num_items(Items.Hay) >= c_hay and num_items(Items.Wood) >= c_wood:
                        if not is_soil[idx]:
                            till()
                            is_soil[idx] = 1
                        elif e != Entities.Grass and e != None:
                            harvest()
                        plant(Entities.Carrot)
                    else:
                        if e != Entities.Grass and e != None:
                            harvest()
                        plant(Entities.Bush)
        return False
    if is_tree[idx]:
        harvest()
        is_tree[idx] = 0
        trees_done += 1
        if trees_done >= 1218 and num_items(Items.Wood) >= 500000000:
            return True
    else:
        e = get_entity_type()
        if e == Entities.Grass:
            if num_items(Items.Hay) < 4096 and can_harvest():
                harvest()
        elif e != None:
            harvest()
    if get_water() < 0.2 and num_items(Items.Water) >= 4:
        use_item(Items.Water, 4)
    while True:
        plant(Entities.Tree)
        c, p = get_companion()
        pi = p[0] * 8 + p[1]
        if pi in wants:
            if wants[pi] != c:
                harvest()
                continue
            is_tree[idx] = 1
            return False
        if IS_EVEN[pi] and c == Entities.Carrot:
            harvest()
            continue
        wants[pi] = c
        is_tree[idx] = 1
        return False

def do_odd(idx):
    if idx in wants:
        c = wants.pop(idx)
        e = get_entity_type()
        if e != c:
            if c == Entities.Grass:
                if is_soil[idx]:
                    till()
                    is_soil[idx] = 0
                else:
                    harvest()
            elif c == Entities.Bush:
                if e != Entities.Grass and e != None:
                    harvest()
                plant(Entities.Bush)
            else:
                if num_items(Items.Hay) >= c_hay and num_items(Items.Wood) >= c_wood:
                    if not is_soil[idx]:
                        till()
                        is_soil[idx] = 1
                    elif e != Entities.Grass and e != None:
                        harvest()
                    plant(Entities.Carrot)
                else:
                    if e != Entities.Grass and e != None:
                        harvest()
                    plant(Entities.Bush)

if __name__ == "__main__":
    lb_wood_single()
