from __builtins__ import *

# 游戏将硬度达到此值的方块视为不可破坏，直接 dig() 会等待极长时间。
UNBREAKABLE_HARDNESS = 10000000


def f0():
    # 从启动位置打竖井；每条煤脉处理完后回到这里继续向下。
    shaft_x = get_pos_x()
    shaft_y = get_pos_y()
    size = get_world_size()

    while True:
        if get_ground_type() != Grounds.Coal:
            if not dig_block():
                return
            continue

        layer = get_pos_z()
        before = num_items(Items.Coal)
        quick_print("发现煤层，z =", layer)
        if not mine_coal(size):
            return
        quick_print("煤脉搜索完成，起始层 z =", layer,
                    "，新增煤炭 =", num_items(Items.Coal) - before)
        if not go_to(shaft_x, shaft_y, size):
            return


def mine_coal(size):
    # 待查项保存煤块所在的 z；挖掉后当前位置会再下降一格。
    start = (get_pos_x(), get_pos_y(), get_pos_z())
    pending = [start]
    seen = {start}

    while pending:
        x, y, layer = pending.pop()
        if not go_to(x, y, size):
            return False

        # 相邻列可能仍有覆盖层。已挖过这一层的列无需继续下挖。
        while get_pos_z() >= layer:
            z = get_pos_z()
            coal = get_ground_type() == Grounds.Coal
            if z == layer and not coal:
                break
            if not dig_block():
                return False
            if not coal:
                continue

            # 覆盖层中遇到的煤也扩展分支，避免只挖走它而漏掉旁边的煤。
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx = x + dx
                    ny = y + dy
                    # 煤脉生成不跨边界；移动时仍可利用世界环绕抄近路。
                    if nx < 0 or nx >= size or ny < 0 or ny >= size:
                        continue
                    neighbor = (nx, ny, z)
                    if neighbor not in seen:
                        seen.add(neighbor)
                        pending.append(neighbor)

    return True


def go_to(x, y, size):
    # 沿两个坐标轴走较短的环绕路线；移动失败时保留现场并结束。
    steps = (x - get_pos_x()) % size
    direction = East
    if steps > size // 2:
        steps = size - steps
        direction = West
    for _ in range(steps):
        if not move(direction):
            quick_print("无法移动到", x, y, "，请检查帽子或地形后重新运行 f0。")
            return False

    steps = (y - get_pos_y()) % size
    direction = North
    if steps > size // 2:
        steps = size - steps
        direction = South
    for _ in range(steps):
        if not move(direction):
            quick_print("无法移动到", x, y, "，请检查帽子或地形后重新运行 f0。")
            return False
    return True


def dig_block():
    # 先排除无法破坏的方块，再确认挖掘确实使地面下降。
    if get_hardness() >= UNBREAKABLE_HARDNESS:
        quick_print("遇到不可破坏的方块，已停止。位置：",
                    get_pos_x(), get_pos_y(), get_pos_z())
        return False
    z = get_pos_z()
    if not dig() or get_pos_z() >= z:
        quick_print("挖掘没有使地面下降，已停止。位置：",
                    get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


if __name__ == "__main__":
    f0()
