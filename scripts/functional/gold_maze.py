from __builtins__ import *
import farm_support


def gold_maze():
    # 每座迷宫只收取一次宝藏，再生成新宫，持续获取金币。
    farm_support.run(Items.Gold, collect)


def collect(goal):
    # 新迷宫使用DFS，不依赖满科技重定位次数或固定8×8区域。
    if not farm_support.require(Unlocks.Mazes) or not farm_support.require(Unlocks.Plant):
        return False
    width, size = farm_support.dimensions()
    side = min(width, size)
    while num_items(Items.Gold) < goal:
        amount = side * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        if not farm_support.stock(Items.Weird_Substance, amount):
            return False
        clear()
        if get_entity_type() != None:
            harvest()
        if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, amount):
            quick_print("迷宫生成失败。")
            return False
        if not find_treasure(side):
            return False
    return True


def find_treasure(side):
    # 栈记录每条实际走过的边；访问过的节点不再递归，找到宝藏后立即收获。
    directions = [North, East, South, West]
    backs = [South, West, North, East]
    visited = {(get_pos_x(), get_pos_y())}
    stack = []
    for _ in range(8 * side * side + 1):
        if get_entity_type() == Entities.Treasure:
            return harvest()
        advanced = False
        for i in range(4):
            if not can_move(directions[i]):
                continue
            x = get_pos_x()
            y = get_pos_y()
            if i == 0:
                y += 1
            elif i == 1:
                x += 1
            elif i == 2:
                y -= 1
            else:
                x -= 1
            if (x, y) in visited:
                continue
            if not move(directions[i]):
                return False
            visited.add((x, y))
            stack.append(backs[i])
            advanced = True
            break
        if not advanced:
            if len(stack) == 0 or not move(stack.pop()):
                quick_print("迷宫内未找到可达宝藏，停止。")
                return False
    quick_print("迷宫搜索超过完整遍历预算，停止。")
    return False


if __name__ == "__main__":
    gold_maze()
