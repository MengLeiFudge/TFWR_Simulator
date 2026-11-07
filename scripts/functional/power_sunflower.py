from __builtins__ import *
import farm_support


def power_sunflower():
    # 持续种向日葵；不消耗目标Power补料之外的额外加速物品。
    farm_support.run(Items.Power, collect)


def collect(goal):
    # 先记录全场花瓣数，按最大花瓣优先收获，利用可用的向日葵倍率。
    if not farm_support.require(Unlocks.Sunflowers):
        return False
    width, size = farm_support.dimensions()
    while num_items(Items.Power) < goal:
        if not farm_support.seeds(Entities.Sunflower, width * size):
            return False
        clear()
        flowers = []
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y):
                    return False
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Sunflower):
                    return False
                farm_support.water()
                flowers.append((x, y, measure()))
        for petals in range(15, 6, -1):
            for x, y, count in flowers:
                if count == petals:
                    if not farm_support.move_to(x, y) or not farm_support.mature(Entities.Sunflower):
                        return False
                    if not harvest():
                        return False
    return True


if __name__ == "__main__":
    power_sunflower()
