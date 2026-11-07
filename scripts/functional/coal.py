from __builtins__ import *
import farm_support


def coal():
    # 从存档煤脚本的探层思路迁入，按实际科技和地图重生开采。
    farm_support.run(Items.Coal, collect)


def collect(goal):
    # 稻米解锁后优先采首区块煤层，无需Jump或固定8×4派工。
    return farm_support.mine(Items.Coal, goal)


if __name__ == "__main__":
    coal()
