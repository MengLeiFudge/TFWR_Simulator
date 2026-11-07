from __builtins__ import *
import farm_support


def cactus():
    # 持续完成整田排序与连锁收获，种子南瓜不足时先补给。
    farm_support.run(Items.Cactus, collect)


def collect(goal):
    # 相邻交换的行列插入排序不依赖固定尺寸和无人机数量。
    if not farm_support.require(Unlocks.Cactus):
        return False
    width, size = farm_support.dimensions()
    while num_items(Items.Cactus) < goal:
        if not farm_support.seeds(Entities.Cactus, width * size):
            return False
        clear()
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y):
                    return False
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Cactus):
                    return False
        if not sort_all(width, size):
            return False
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y) or not farm_support.mature(Entities.Cactus):
                    return False
        if not harvest():
            return False
    return True


def sort_all(width, size):
    # 每行向东非降序，再每列向北非降序；纵向排序保持各行已有顺序。
    for y in range(size):
        for x in range(1, width):
            if not farm_support.move_to(x, y):
                return False
            position = x
            while position > 0 and measure(West) > measure():  # ty: ignore[unsupported-operator]  已种仙人掌的measure为整数。
                if not swap(West) or not move(West):
                    return False
                position -= 1
    for x in range(width):
        for y in range(1, size):
            if not farm_support.move_to(x, y):
                return False
            position = y
            while position > 0 and measure(South) > measure():  # ty: ignore[unsupported-operator]  已种仙人掌的measure为整数。
                if not swap(South) or not move(South):
                    return False
                position -= 1
    return True


if __name__ == "__main__":
    cactus()
