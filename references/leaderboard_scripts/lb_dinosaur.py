from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main6，固定哈密顿回路；旧 main1..main5 保留做对照。






head = East  # 当前移动方向
now_pos = (0, 0)  # 当前位置
last_goal = None  # 上一次的目标位置
stuck_count = 0  # 卡住计数器







# 固定哈密顿回路设计（32x32）：
#   1. (0,0) → East 到 (31,0)                          [row0 全扫]
#   2. 对 y=1..31：North 1，y 奇数向 West 到 (1,y)，偶数向 East 到 (31,y)
#   3. 最后 y=31（奇数），末尾在 (1,31)；West 1 到 (0,31)；South 31 步回到 (0,0)
# 每圈恰好 1024 步，覆盖 1024 格。DinosaurTailView 会把“尾末端格”置为可走，
# 因此只要按回路顺序，永不自撞。苹果每吃一枚就随机补一枚，统计意义上每过 ~1024
# 步能吃到接近每格一枚；1000 枚左右 tail 即接近满，一次 cash-out 拿到 ~1024^2 * 32 bones。
def main6():
    size = get_world_size()
    goal_bones = 33488928
    # bonus = tail^2 * 2^(Dinosaurs-1)。Dinosaurs=6 时倍率 32，
    # 需要 tail^2 >= goal_bones/32 = 1046529 => tail >= 1023（正好 size*size-1）。
    target_tail = size * size - 1
    while num_items(Items.Bone) < goal_bones:
        goto_wrap(0, 0)
        change_hat(Hats.Dinosaur_Hat)
        run_hamiltonian(size, target_tail)
        change_hat(Hats.Straw_Hat)
    quick_print("main6 done bones=", num_items(Items.Bone), " time=", get_time())


def goto_wrap(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def run_hamiltonian(size, target_tail):
    # 走一整圈覆盖所有格子；途中用 measure(direction) 侦测下一格是否 Apple（返回 tuple 即是），
    # 以此累计 apples_eaten，等同于 tail 长度（开局 change_hat 会在脚下放一颗 Apple，踩上去吃掉即 tail=1）。
    # 达到 target_tail 就返回，让外层 change_hat(Straw_Hat) 一次性结算。
    apples_eaten = 0
    while apples_eaten < target_tail:
        # row 0: East size-1 次到 (size-1, 0)
        n = snake_move(East, size - 1, target_tail, apples_eaten)
        if n < 0:
            return
        apples_eaten = apples_eaten + n
        if apples_eaten >= target_tail:
            return
        # y=1..size-1：先 North 1，再水平扫
        for y in range(1, size):
            n = snake_move(North, 1, target_tail, apples_eaten)
            if n < 0:
                return
            apples_eaten = apples_eaten + n
            if apples_eaten >= target_tail:
                return
            if y % 2 == 1:
                dir_h = West
            else:
                dir_h = East
            n = snake_move(dir_h, size - 2, target_tail, apples_eaten)
            if n < 0:
                return
            apples_eaten = apples_eaten + n
            if apples_eaten >= target_tail:
                return
        # 末行末尾 West 1 到 (0, size-1)
        n = snake_move(West, 1, target_tail, apples_eaten)
        if n < 0:
            return
        apples_eaten = apples_eaten + n
        if apples_eaten >= target_tail:
            return
        # 沿 x=0 列向南 size-1 步回到 (0,0)
        n = snake_move(South, size - 1, target_tail, apples_eaten)
        if n < 0:
            return
        apples_eaten = apples_eaten + n


# 一次性沿 direction 走 count 步；每步先读当前格是否 Apple（踩在 apple 上才是“下一次 move 会吃”），
# 再 can_move 再 move。返回累计吃到的苹果数；can_move 失败（理论上哈密顿回路里不该发生）返回 -1。
# drone.py 的 `_after_dinosaur_move` 用 `current_obj = get_entity_object(old_pos)` 判定是否吃，
# 所以吃苹果发生在“离开 apple 格”这一步，也就是“当前格是 Apple”的 move 才会触发吃。
def snake_move(direction, count, target_tail, already_eaten):
    eaten = 0
    for _ in range(count):
        if already_eaten + eaten >= target_tail:
            return eaten
        ate_this = (get_entity_type() == Entities.Apple)
        if not can_move(direction):
            return -1
        move(direction)
        if ate_this:
            eaten = eaten + 1
    return eaten


if __name__ == "__main__":
    main6()
