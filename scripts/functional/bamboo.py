from __builtins__ import *
import production

# 按行分片；先选择可切收的竹子高度，再以固定间隔巡回整片收获。
def bamboo(target=-1):
    if not production.active(Items.Bamboo, target):
        return
    size = get_world_size()
    if size < 4:
        quick_print("竹子采集需要至少4×4的农场。")
        return
    workers = min(max_drones(), size)
    clear()
    ready = False
    while production.active(Items.Bamboo, target):
        goal = target
        if goal == -1:
            goal = num_items(Items.Bamboo) + 500000000
        handles = []
        results = []
        ok = True
        for owner in range(1, workers):
            y0 = owner * size // workers
            rows = (owner + 1) * size // workers - y0
            handle = spawn_drone(bamboo_batch, y0, rows, goal, 0.25, 3, ready)
            if handle == None:
                ok = False
                break
            handles.append(handle)
        if ok:
            results.append(bamboo_batch(0, size // workers, goal, 0.25, 3, ready))
        for handle in handles:
            results.append(wait_for(handle))
        for result in results:
            if not result:
                ok = False
        quick_print("bamboo_all_done", ok, get_time(), num_items(Items.Bamboo))
        if not ok:
            return
        # 所有行已筛完，后续回收只重派切收工人，保留同一片竹桩。
        ready = True



def bamboo_batch(y0, rows, goal, water_level, interval, ready):
    size = get_world_size()
    hover(18)
    for _ in range(y0):
        move(North)
    if not ready:
        selected = []
        for _ in range(rows):
            flags = []
            for x in range(size - 1):
                flags.append(False)
            selected.append(flags)
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
    bamboo()
