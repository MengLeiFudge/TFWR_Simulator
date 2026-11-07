from __builtins__ import *
import farm_support


def quartz():
    # 持续开采实际石英，不要求初始铁矿或满级科技。
    farm_support.run(Items.Quartz, collect)


def collect(goal):
    # 普通地下地形使用逐层开采，避免套用矿石榜的固定深度。
    return farm_support.mine(Items.Quartz, goal)


if __name__ == "__main__":
    quartz()
