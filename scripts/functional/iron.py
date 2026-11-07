from __builtins__ import *
import farm_support


def iron():
    # 持续开采实际铁矿，不消耗煤做前置勘探。
    farm_support.run(Items.Iron, collect)


def collect(goal):
    # 无勘探科技时仍沿公开地层采集。
    return farm_support.mine(Items.Iron, goal)


if __name__ == "__main__":
    iron()
