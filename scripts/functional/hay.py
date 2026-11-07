from __builtins__ import *
import farm_support


def hay():
    # 持续收草；没有种植科技时使用clear后的自然草地。
    farm_support.run(Items.Hay, collect)


def collect(goal):
    # 供其他功能脚本按绝对库存目标补充干草。
    return farm_support.farm(Entities.Grass, Items.Hay, goal)


if __name__ == "__main__":
    hay()
