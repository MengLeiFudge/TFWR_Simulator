from __builtins__ import *
import farm_support


def pumpkin():
    # 持续维护整田南瓜，补死株后等待合并，再一次收获。
    farm_support.run(Items.Pumpkin, collect)


def collect(goal):
    # 每批预留重种种子，种子不足时先收成熟株再回收田地补料。
    if not farm_support.require(Unlocks.Pumpkins) or not farm_support.require(Unlocks.Plant):
        return False
    width, size = farm_support.dimensions()
    empty = 0
    while num_items(Items.Pumpkin) < goal:
        if not farm_support.seeds(Entities.Pumpkin, 2 * width * size):
            return False
        clear()
        before = num_items(Items.Pumpkin)
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y):
                    return False
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Pumpkin):
                    return False
                farm_support.water()
        for _ in range(128):
            ready = True
            refuel = False
            for x in range(width):
                for y in range(size):
                    if not farm_support.move_to(x, y):
                        return False
                    if get_entity_type() != Entities.Pumpkin:
                        if not plant(Entities.Pumpkin):
                            refuel = True
                        ready = False
                    elif not can_harvest():
                        ready = False
                    farm_support.water()
            if ready or refuel:
                break
            do_a_flip()
        # 全田成熟时首株可能收掉整组；补料前也保留其他已经成熟的独立组收益。
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y):
                    return False
                if get_entity_type() == Entities.Pumpkin and can_harvest():
                    if not harvest():
                        return False
        if num_items(Items.Pumpkin) == before:
            empty += 1
            if empty >= 8:
                quick_print("连续八批没有成熟南瓜，停止。")
                return False
        else:
            empty = 0
    return True


if __name__ == "__main__":
    pumpkin()
