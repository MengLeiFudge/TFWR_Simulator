from __builtins__ import *
# 宝藏猎人：生成覆盖32×32农场的大迷宫，有界深度优先搜索后收获宝藏。
MAX_GAME_SECONDS = 300
SIZE = 32
DIRECTIONS = [North, East, South, West]
OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def treasure_hunter():
    deadline = get_time() + MAX_GAME_SECONDS - 1
    set_world_size(SIZE)
    clear()
    if not plant(Entities.Bush):
        return
    if not use_item(Items.Weird_Substance, SIZE * 2 ** (num_unlocked(Unlocks.Mazes) - 1)):
        quick_print("怪异物质不足，未生成整田迷宫。")
        return
    visited = {(0, 0)}
    path = []
    while get_time() < deadline:
        if get_entity_type() == Entities.Treasure:
            harvest()
            quick_print("已收获32×32整田迷宫宝藏。")
            return
        advanced = False
        for index in range(4):
            dx, dy = OFFSETS[index]
            neighbor = ((get_pos_x() + dx) % SIZE, (get_pos_y() + dy) % SIZE)
            if neighbor not in visited and can_move(DIRECTIONS[index]):
                move(DIRECTIONS[index])
                visited.add(neighbor)
                path.append(index)
                advanced = True
                break
        if not advanced:
            if not path:
                break
            move(DIRECTIONS[(path.pop() + 2) % 4])
    quick_print("5分钟内未找到整田迷宫宝藏。")


if __name__ == "__main__":
    treasure_hunter()
