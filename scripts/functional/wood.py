from __builtins__ import *
import farm_support


def wood():
    # 早期种灌木，解锁树后使用树与灌木交错布局。
    farm_support.run(Items.Wood, collect)


def collect(goal):
    # 种植和地图处理共用地表生产路径。
    return farm_support.farm(Entities.Bush, Items.Wood, goal)


if __name__ == "__main__":
    wood()
