from __builtins__ import *
# 历史提交归档：lb_bamboo | 初次提交 2026-11-09 (be0e2c24) | 修复：按游戏原版解析语法并纠正竹子条件表达式
# 完整轮时间：未取得（统一花节批量保桩；当前版本未实机验证）。

def lb_bamboo():
    clear()
    size = get_world_size()
    workers = min(max_drones(), size)
    handles = []
    results = []
    for owner in range(1, workers):
        y0 = owner * size // workers
        rows = (owner + 1) * size // workers - y0
        handle = spawn_drone(bamboo_batch, y0, rows, 500000000, 0.25, 3)
        if handle == None:
            results.append(bamboo_batch(y0, rows, 500000000, 0.25, 3))
        else:
            handles.append(handle)
    results.append(bamboo_batch(0, size // workers, 500000000, 0.25, 3))
    for handle in handles:
        results.append(wait_for(handle))
    ok = True
    for result in results:
        if not result:
            ok = False
    quick_print("bamboo_all_done", ok, get_time(), num_items(Items.Bamboo))


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
    # 花节随树桩保留；首两节统一为5和9后可以整片使用同一切割高度。
    while left > 0:
        hover(4)
        for row in range(rows):
            for x in range(size - 1):
                move(East)
                if not selected[row][x]:
                    seeded = False
                    if get_entity_type() != Entities.Bamboo:
                        if get_ground_type() != Grounds.Soil:
                            till()
                        if not bamboo_seed():
                            return False
                        seeded = True
                    elif measure() == 8:
                        selected[row][x] = True
                        left -= 1
                    elif measure() != 4:
                        harvest()
                        if not bamboo_seed():
                            return False
                        seeded = True
                    watered = bamboo_water(water_level)
                    if seeded or watered:
                        hover(4)
            move(East)
            if row + 1 < rows:
                move(North)
        bamboo_return(rows, size)
        laps += 1
        if laps % 4 == 0:
            quick_print("bamboo_select", y0, left, get_time())
        if laps > 100:
            quick_print("bamboo_failed", "selection", y0, left)
            return False
    hover(1)
    last = get_time()
    bamboo_sweep(rows, water_level)
    quick_print("bamboo_selected", y0, get_time(), num_items(Items.Bamboo))
    cycles = 0
    while num_items(Items.Bamboo) < goal:
        for height in [4, 8, 1]:
            # 按每趟起点计时，上一趟巡回本身也计入生长间隔。
            while get_time() < last + interval:
                do_a_flip()
            last = get_time()
            hover(height)
            if height == 1:
                bamboo_sweep(rows, water_level)
            else:
                bamboo_sweep(rows, -1)
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
            return use_item(Items.Water, amount)
    return False


def bamboo_sweep(rows, water_level):
    size = get_world_size()
    for row in range(rows):
        for x in range(size - 1):
            move(East)
            # 仅在切回高度1时浇水，避免供水把切花阶段的飞行高度重置。
            if water_level > 0:
                bamboo_water(water_level)
        move(East)
        if row + 1 < rows:
            move(North)
    bamboo_return(rows, size)


def bamboo_return(rows, size):
    if rows == size:
        move(North)
    else:
        for _ in range(rows - 1):
            move(South)


if __name__ == "__main__":
    lb_bamboo()
