from __builtins__ import *
import farm_support


def bone_dinosaur():
    # 恐龙帽结算尾巴后补充仙人掌，持续生产骨头。
    farm_support.run(Items.Bone, collect)


def collect(goal):
    # 偶数边使用覆盖整场的固定环；双奇数小图以可走方向保守采集后结算。
    if not farm_support.require(Unlocks.Dinosaurs):
        return False
    width, size = farm_support.dimensions()
    if width * size < 2:
        quick_print("恐龙需要至少两个相连地块。")
        return False
    while num_items(Items.Bone) < goal:
        if not farm_support.seeds(Entities.Apple, width * size):
            return False
        clear()
        change_hat(Hats.Dinosaur_Hat)
        before = num_items(Items.Bone)
        for _ in range(2 * (width * size) ** 2):
            x = get_pos_x()
            y = get_pos_y()
            direction = None
            if width % 2 == 0 and size > 1:
                direction = cycle_step(x, y, width, size, [East, North, West, South])
            elif size % 2 == 0 and width > 1:
                direction = cycle_step(y, x, size, width, [North, East, South, West])
            else:
                for candidate in [North, East, South, West]:
                    if can_move(candidate):
                        direction = candidate
                        break
            if direction == None or not move(direction):
                break
        # 换帽是正常结算路径；所有补料和clear都在尾巴结算之后。
        change_hat(Hats.Straw_Hat)
        if num_items(Items.Bone) <= before:
            quick_print("本轮恐龙没有骨头收益，停止。")
            return False
    return True


def cycle_step(x, y, width, size, directions):
    # 底边向右，余下列蛇形回到左边；偶数width保证闭环且不穿边。
    east, north, west, south = directions
    if y == 0:
        if x + 1 < width:
            return east
        return north
    if x == 0:
        return south
    if x % 2 == 1:
        if y + 1 < size:
            return north
        return west
    if y > 1:
        return south
    return west


if __name__ == "__main__":
    bone_dinosaur()
