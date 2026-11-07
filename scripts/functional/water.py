from __builtins__ import *
import farm_support


def water():
    # 水由浇水科技被动补给，等待期间不清场、不消耗已有水。
    farm_support.run(Items.Water, collect)


def collect(goal):
    # 未解锁浇水科技时明确停止，已有库存可以直接用于其他脚本。
    return farm_support.stock(Items.Water, goal)


if __name__ == "__main__":
    water()
