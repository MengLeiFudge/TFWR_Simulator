from __builtins__ import *
import farm_support


def fertilizer():
    # 肥料由科技被动补给，等待期间保留当前农田和已有库存。
    farm_support.run(Items.Fertilizer, collect)


def collect(goal):
    # 未解锁肥料科技时停止；不以施肥动作伪造肥料产量。
    return farm_support.stock(Items.Fertilizer, goal)


if __name__ == "__main__":
    fertilizer()
