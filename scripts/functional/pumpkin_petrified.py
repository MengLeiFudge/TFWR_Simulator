from __builtins__ import *
import farm_support


def pumpkin_petrified():
    # 从地下石化南瓜获取南瓜，与地表种植入口分开。
    farm_support.run(Items.Pumpkin, collect)


def collect(goal):
    # 当前解锁等级决定地层产量，普通逐层开采无需种子和Jump。
    if not farm_support.require(Unlocks.Petrified_Pumpkins):
        return False
    return farm_support.mine(Items.Pumpkin, goal)


if __name__ == "__main__":
    pumpkin_petrified()
