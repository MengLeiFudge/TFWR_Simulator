from __builtins__ import *
import farm_support


def weird_substance():
    # 施肥感染草，再收获怪异物质；肥料由已解锁的被动补给产生。
    farm_support.run(Items.Weird_Substance, collect)


def collect(goal):
    # 在每株草成熟后施肥，避免依赖其他作物种子和迷宫材料。
    if not farm_support.require(Unlocks.Fertilizer):
        return False
    width, size = farm_support.dimensions()
    while num_items(Items.Weird_Substance) < goal:
        if not farm_support.stock(Items.Fertilizer, width * size):
            return False
        clear()
        for x in range(width):
            for y in range(size):
                if not farm_support.move_to(x, y) or not farm_support.mature(Entities.Grass):
                    return False
                if not use_item(Items.Fertilizer) or not harvest():
                    return False
                if num_items(Items.Weird_Substance) >= goal:
                    return True
    return True


if __name__ == "__main__":
    weird_substance()
