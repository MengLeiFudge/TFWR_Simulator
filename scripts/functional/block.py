from __builtins__ import *
import farm_support


def block():
    # 按实际地层持续开采建材，不要求跳跃或多无人机。
    farm_support.run(Items.Block, collect)


def collect(goal):
    # 地层遍历与科技检查由共用开采路径处理。
    return farm_support.mine(Items.Block, goal)


if __name__ == "__main__":
    block()
