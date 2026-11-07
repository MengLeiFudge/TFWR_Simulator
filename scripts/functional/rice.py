from __builtins__ import *
import farm_support


def rice():
    # 将存档的逐柱稻米采集改为有限批次，全部工人回收后重生下一片。
    farm_support.run(Items.Rice, collect)


def collect(goal):
    # 不要求Jump；每柱两层粘土用尽后回地表，低科技同样使用自然成熟。
    if not farm_support.require(Unlocks.Rice) or not farm_support.require(Unlocks.Mining):
        return False
    if not farm_support.require(Unlocks.Plant):
        return False
    width, size = farm_support.dimensions()
    empty = 0
    while num_items(Items.Rice) < goal:
        before = num_items(Items.Rice)
        clear()
        workers = min(width, farm_support.capacity())
        handles = []
        ok = True
        for first in range(1, workers):
            handle = spawn_drone(columns, first, workers, width, size, goal)
            if handle == None:
                if not columns(first, workers, width, size, goal):
                    ok = False
            else:
                handles.append(handle)
        if not columns(0, workers, width, size, goal):
            ok = False
        for handle in handles:
            if not wait_for(handle):
                ok = False
        if not ok:
            quick_print("稻米种植或采收失败，已回收子机。")
            return False
        if num_items(Items.Rice) == before:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有可收获的稻米，停止。")
                return False
        else:
            empty = 0
    return True


def columns(first, stride, width, size, goal):
    # 每列唯一写者；只在harvest成功后继续下挖，避免破坏尚未成熟的稻米。
    for layer in range(2):
        planted = []
        for x in range(first, width, stride):
            for y in range(size):
                if num_items(Items.Rice) >= goal:
                    return True
                if not farm_support.move_to(x, y):
                    return False
                for _ in range(128):
                    ground = get_ground_type()
                    if ground == Grounds.Clay or ground == Grounds.Rock or ground == Grounds.Bedrock:
                        break
                    if not dig():
                        return False
                if get_ground_type() == Grounds.Clay:
                    if not plant(Entities.Rice):
                        return False
                    farm_support.water()
                    planted.append((x, y))
        for x, y in planted:
            if num_items(Items.Rice) >= goal:
                return True
            if not farm_support.move_to(x, y):
                return False
            if get_entity_type() == Entities.Rice:
                if not farm_support.mature(Entities.Rice) or not harvest():
                    return False
    return True


if __name__ == "__main__":
    rice()
