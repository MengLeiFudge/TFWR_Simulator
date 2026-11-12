from __builtins__ import *
# 淘汰候选归档：lb_bamboo_single | 原实验路径 .codex/nonreset-100-20261108/bamboo-batch-v1/lb_bamboo_single.py
# 本地研究：统一花节、保留树桩、按高度整片切收；未实机。

def lb_bamboo_single():
    clear()
    bamboo_batch(0, get_world_size(), 25000000, 0.7, 1.5)


def bamboo_batch(y0, rows, goal, water_level, interval):
    size = get_world_size()
    hover(18)
    for _ in range(y0):
        move(North)
    selected = []
    for _ in range(rows):
        selected.append([False] * (size - 1))
    left = rows * (size - 1)
    laps = 0
    while left > 0:
        hover(4)
        for row in range(rows):
            for x in range(size - 1):
                move(East)
                if not selected[row][x]:
                    if get_entity_type() != Entities.Bamboo:
                        if get_ground_type() != Grounds.Soil:
                            till()
                        if not bamboo_seed():
                            return False
                    elif measure() == 8:
                        selected[row][x] = True
                        left -= 1
                    elif measure() != 4:
                        harvest()
                        if not bamboo_seed():
                            return False
                    bamboo_water(water_level)
                    hover(4)
            move(East)
            move(North)
        for _ in range(rows):
            move(South)
        laps += 1
        if laps % 4 == 0:
            quick_print("bamboo_select", y0, left, get_time())
        if laps > 100:
            quick_print("bamboo_failed", "selection", y0, left)
            return False
    hover(1)
    bamboo_sweep(rows, water_level)
    quick_print("bamboo_selected", y0, get_time(), num_items(Items.Bamboo))
    last = get_time() - interval
    cycles = 0
    while num_items(Items.Bamboo) < goal:
        for height in [4, 8, 1]:
            while get_time() < last + interval:
                do_a_flip()
            last = get_time()
            hover(height)
            bamboo_sweep(rows, water_level if height == 1 else -1)
        cycles += 1
        if cycles % 4 == 0:
            quick_print("bamboo_batch", y0, cycles, get_time(), num_items(Items.Bamboo))
        if get_time() > 3600:
            quick_print("bamboo_failed", "deadline", y0)
            return False
    quick_print("bamboo_done", y0, get_time(), num_items(Items.Bamboo))
    return True


def bamboo_seed():
    for _ in range(256):
        if not plant(Entities.Bamboo):
            return False
        if measure() == 4:
            return True
        harvest()
    return False


def bamboo_water(level):
    if get_water() < level:
        amount = 4
        if level < 0.5:
            amount = 1
        if num_items(Items.Water) >= amount:
            use_item(Items.Water, amount)


def bamboo_sweep(rows, water_level):
    size = get_world_size()
    for _ in range(rows):
        for x in range(size - 1):
            move(East)
            if water_level > 0:
                bamboo_water(water_level)
        move(East)
        move(North)
    for _ in range(rows):
        move(South)


if __name__ == "__main__":
    lb_bamboo_single()
