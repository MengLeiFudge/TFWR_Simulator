from __builtins__ import *
import farm_support


def bamboo():
    # 参考存档的空通道切花方式，持续生产竹子并按批补充稻米。
    farm_support.run(Items.Bamboo, collect)


def collect(goal):
    # 偶数行种竹、北侧留通道，兼容1×3早期地图；不要求固定32机。
    if not farm_support.require(Unlocks.Bamboo) or not farm_support.require(Unlocks.Plant):
        return False
    width, size = farm_support.dimensions()
    if size < 2:
        quick_print("竹子需要种植格和相邻通道格。")
        return False
    while num_items(Items.Bamboo) < goal:
        count = width * (size // 2)
        if not farm_support.seeds(Entities.Bamboo, count):
            return False
        clear()
        workers = min(width, farm_support.capacity())
        handles = []
        ok = True
        for first in range(1, workers):
            handle = spawn_drone(columns, first, workers, width, size)
            if handle == None:
                if not columns(first, workers, width, size):
                    ok = False
            else:
                handles.append(handle)
        if not columns(0, workers, width, size):
            ok = False
        for handle in handles:
            if not wait_for(handle):
                ok = False
        if not ok:
            quick_print("竹子切花或收获失败，已回收子机。")
            return False
    return True


def columns(first, stride, width, size):
    # 每株只种一次，切前两处花节后等待第三阶段成熟并整株收获。
    hover(18)
    for x in range(first, width, stride):
        for y in range(0, size - 1, 2):
            if not farm_support.move_to(x, y):
                return False
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Bamboo):
                return False
            farm_support.water()
            hover(18)
    for x in range(first, width, stride):
        for y in range(0, size - 1, 2):
            hover(18)
            if not farm_support.move_to(x, y):
                return False
            for phase in range(3):
                # 等待期间保持高飞；浇水会重置悬浮高度，不能在这里调用。
                waiting = 0
                while not can_harvest():
                    if waiting >= 64:
                        return False
                    do_a_flip()
                    waiting += 1
                if phase < 2:
                    height = measure()
                    if not move(North) or not hover(height) or not move(South):  # ty: ignore[invalid-argument-type]  已成熟竹子的measure是花节高度。
                        return False
                    hover(18)
                elif not harvest():
                    return False
    return True


if __name__ == "__main__":
    bamboo()
