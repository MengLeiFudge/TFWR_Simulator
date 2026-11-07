from __builtins__ import *
import farm_support


def carrot():
    # 持续产胡萝卜；种子所需干草和木材由生产路径按当前成本补齐。
    farm_support.run(Items.Carrot, collect)


def collect(goal):
    # 科技未解锁时明确返回失败。
    return farm_support.farm(Entities.Carrot, Items.Carrot, goal)


if __name__ == "__main__":
    carrot()
