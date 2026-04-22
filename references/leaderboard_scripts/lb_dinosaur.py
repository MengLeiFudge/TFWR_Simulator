from __builtins__ import *


# Dinosaur 版本结论
# main1..main4: 早期贪心/局部打分方案，单局死亡过早，bones 结算依赖多局累积，慢。
# main5: 两阶段贪心 + parity 限制路径。本地模拟器触发 max_cycles，落后 1# 约 11 分钟。
# main6: 固定哈密顿回路。drone.py 源码证实 bones 一次结算公式为
#        `tail_length^2 * 2^(Dinosaurs-1)`，默认 Dinosaurs=6 得倍率 32，
#        因此尾巴长到 ~1023 时单局即可凑到 33488928 bones。
#        做法：走一条覆盖全部 32x32 格子的固定回路，DinosaurTailView 允许踩到自己尾端，
#        所以只要按回路顺序走就永远不会自撞。苹果随机生成在空格，
#        每过一圈必然吃到；累计约 1000 枚后 cash-out 即可达标。


def main1():
    size = get_world_size()
    while num_items(Items.Bone) < 33488928:
        change_hat(Hats.Dinosaur_Hat)
        while (
                can_move(East) or
                can_move(West) or
                can_move(North) or
                can_move(South)
        ):
            move(North)
            for _ in range(size // 2):
                for _ in range(size - 2):
                    move(North)
                move(East)
                for _ in range(size - 2):
                    move(South)
                move(East)
            move(South)
            for _ in range(size - 1):
                move(West)
        change_hat(Hats.Straw_Hat)


def main2():
    while num_items(Items.Bone) < 33488928:
        change_hat(Hats.Dinosaur_Hat)

        apple_x, apple_y = 0, 0
        while True:
            # 检查是否还有移动方向
            if not (can_move(East) or can_move(West) or can_move(North) or can_move(South)):
                break

            # 获取苹果坐标
            pos = measure()
            if pos != None:
                (apple_x, apple_y) = pos

            # 获取当前头部坐标
            x = get_pos_x()
            y = get_pos_y()

            # 计算曼哈顿距离和方向偏好
            dx = apple_x - x
            dy = apple_y - y

            # 根据曼哈顿距离优先级排序方向
            directions = []
            if abs(dx) > abs(dy):
                # 水平方向优先
                if dx > 0:
                    directions.append(East)
                elif dx < 0:
                    directions.append(West)
                if dy > 0:
                    directions.append(North)
                elif dy < 0:
                    directions.append(South)
            else:
                # 垂直方向优先
                if dy > 0:
                    directions.append(North)
                elif dy < 0:
                    directions.append(South)
                if dx > 0:
                    directions.append(East)
                elif dx < 0:
                    directions.append(West)

            # 添加其他安全方向作为备选
            all_directions = [East, West, North, South]
            for d in all_directions:
                if d not in directions:
                    directions.append(d)

            # 选择第一个安全方向
            direction = None
            for d in directions:
                if can_move(d):
                    direction = d
                    break

            # 如果没有安全方向，退出
            if direction == None:
                break

            move(direction)

        change_hat(Hats.Straw_Hat)


def main3():
    while num_items(Items.Bone) < 33488928:
        change_hat(Hats.Dinosaur_Hat)

        apple_x, apple_y = 0, 0
        last_direction = East
        move_count = 0

        while True:
            # 检查是否还有移动方向
            if not (can_move(East) or can_move(West) or can_move(North) or can_move(South)):
                break

            # 获取苹果坐标
            pos = measure()
            if pos != None:
                (apple_x, apple_y) = pos

            # 获取当前头部坐标
            x = get_pos_x()
            y = get_pos_y()

            # 计算曼哈顿距离
            dx = apple_x - x
            dy = apple_y - y

            # 优先选择直接减少曼哈顿距离的方向
            directions = []

            # 水平方向
            if dx > 0 and can_move(East):
                directions.append(East)
            elif dx < 0 and can_move(West):
                directions.append(West)

            # 垂直方向
            if dy > 0 and can_move(North):
                directions.append(North)
            elif dy < 0 and can_move(South):
                directions.append(South)

            # 如果直接方向不可用，尝试其他安全方向
            if not directions:
                # 优先保持上次移动方向
                if can_move(last_direction):
                    directions.append(last_direction)

                # 添加其他安全方向
                if can_move(East) and East not in directions:
                    directions.append(East)
                if can_move(North) and North not in directions:
                    directions.append(North)
                if can_move(West) and West not in directions:
                    directions.append(West)
                if can_move(South) and South not in directions:
                    directions.append(South)

            # 选择第一个可用的方向
            direction = None
            if directions:
                direction = directions[0]

            # 如果没有安全方向，退出
            if direction == None:
                break

            # 在移动前再次检查方向是否安全
            if can_move(direction):
                move(direction)
                last_direction = direction
                move_count = move_count + 1

                # 每移动一定次数，尝试重置方向以避免陷入循环
                if move_count % 50 == 0:
                    last_direction = East
            else:
                # 如果方向不再安全，重新计算方向
                continue

        change_hat(Hats.Straw_Hat)


def main4():
    while num_items(Items.Bone) < 33488928:
        change_hat(Hats.Dinosaur_Hat)

        # 初始化蛇身状态
        snake_body = [(0, 0)]  # 蛇身位置列表，第一个元素是蛇头
        apple_x, apple_y = 0, 0
        on_apple = True  # 初始时蛇头在苹果上

        # 记录历史移动方向，用于检测循环
        move_history = []

        while True:
            # 检查是否还有移动方向
            available_directions = []
            for d in [East, West, North, South]:
                if can_move(d):
                    available_directions.append(d)

            if not available_directions:
                break  # 没有可移动方向，结束游戏

            # 获取苹果坐标
            pos = measure()
            if pos != None:
                (apple_x, apple_y) = pos

            # 获取当前头部坐标
            x, y = snake_body[0]

            # 判断当前是否在苹果上
            on_apple = (x == apple_x and y == apple_y)

            # 计算曼哈顿距离
            dx = apple_x - x
            dy = apple_y - y

            # 评估所有可用方向的安全性
            directions = []
            direction_scores = []

            for direction in available_directions:
                # 计算移动后的位置
                if direction == East:
                    new_x, new_y = x + 1, y
                elif direction == West:
                    new_x, new_y = x - 1, y
                elif direction == North:
                    new_x, new_y = x, y + 1
                else:  # South
                    new_x, new_y = x, y - 1

                # 确保新位置在边界内
                if new_x < 0 or new_x >= 32 or new_y < 0 or new_y >= 32:
                    continue  # 跳过这个方向，因为它会导致越界

                # 检查新位置是否在蛇身中
                collision = False
                if on_apple:
                    # 如果在苹果上，移动后蛇身增长，所以新位置不能是任何蛇身部分
                    for body_part in snake_body:
                        if new_x == body_part[0] and new_y == body_part[1]:
                            collision = True
                            break
                else:
                    # 如果不在苹果上，移动后蛇尾移动，所以新位置不能是除蛇尾外的任何蛇身部分
                    for i in range(len(snake_body) - 1):
                        body_part = snake_body[i]
                        if new_x == body_part[0] and new_y == body_part[1]:
                            collision = True
                            break

                if collision:
                    continue  # 跳过这个方向，因为它会导致碰撞

                # 计算方向得分
                score = 0

                # 减少曼哈顿距离的得分
                new_dx = apple_x - new_x
                new_dy = apple_y - new_y
                new_dist = abs(new_dx) + abs(new_dy)
                old_dist = abs(dx) + abs(dy)
                if new_dist < old_dist:
                    score += 8  # 减少距离得分

                # 计算新位置的自由度（周围可移动方向的数量）
                liberty = 0
                for d2 in [East, West, North, South]:
                    if d2 == East:
                        next_x, next_y = new_x + 1, new_y
                    elif d2 == West:
                        next_x, next_y = new_x - 1, new_y
                    elif d2 == North:
                        next_x, next_y = new_x, new_y + 1
                    else:  # South
                        next_x, next_y = new_x, new_y - 1

                    # 检查新位置是否在边界内
                    if next_x < 0 or next_x >= 32 or next_y < 0 or next_y >= 32:
                        continue

                    # 检查新位置是否在蛇身中
                    collision2 = False
                    if on_apple:
                        for body_part in snake_body:
                            if next_x == body_part[0] and next_y == body_part[1]:
                                collision2 = True
                                break
                    else:
                        for i in range(len(snake_body) - 1):
                            body_part = snake_body[i]
                            if next_x == body_part[0] and next_y == body_part[1]:
                                collision2 = True
                                break

                    if not collision2:
                        liberty += 1

                # 自由度得分 - 这是最重要的因素
                score += liberty * 5  # 大幅增加自由度权重

                # 检查是否会进入封闭区域
                if liberty <= 1:
                    # 如果只有一个或零个方向可走，可能进入死胡同
                    score -= 10

                # 避免边界的得分
                distance_to_edge = min(new_x, 31 - new_x, new_y, 31 - new_y)
                score += distance_to_edge // 4  # 每4格增加1分，更重视远离边界

                # 检查是否会导致循环
                if len(move_history) > 10:
                    # 手动统计方向出现的次数
                    direction_count = 0
                    for i in range(len(move_history) - 10, len(move_history)):
                        if move_history[i] == direction:
                            direction_count += 1

                    if direction_count > 3:
                        # 如果这个方向在最近10次移动中出现超过3次，可能陷入循环
                        score -= 5

                directions.append(direction)
                direction_scores.append(score)

            # 如果没有可用方向，退出
            if not directions:
                break

            # 选择得分最高的方向
            best_score = -1000
            best_direction = None
            for i in range(len(directions)):
                if direction_scores[i] > best_score:
                    best_score = direction_scores[i]
                    best_direction = directions[i]

            # 在移动前再次检查方向是否安全
            if can_move(best_direction):
                # 计算新头部位置
                if best_direction == East:
                    new_head = (x + 1, y)
                elif best_direction == West:
                    new_head = (x - 1, y)
                elif best_direction == North:
                    new_head = (x, y + 1)
                else:  # South
                    new_head = (x, y - 1)

                # 移动
                move(best_direction)

                # 更新蛇身
                snake_body.insert(0, new_head)
                if not on_apple:
                    snake_body.pop()  # 移除蛇尾

                # 记录移动历史
                move_history.append(best_direction)
                if len(move_history) > 20:
                    move_history.pop(0)  # 保持历史记录长度为20
            else:
                # 如果方向不再安全，重新计算方向
                continue

        change_hat(Hats.Straw_Hat)


head = East  # 当前移动方向
now_pos = (0, 0)  # 当前位置
last_goal = None  # 上一次的目标位置
stuck_count = 0  # 卡住计数器


def can_turn(p):
    # """根据位置奇偶性返回允许的转向方向"""
    out = [head]  # 总是可以保持当前方向
    if (p[1]) % 2 == 0:  # y坐标为偶数
        out.append(East)
    else:
        out.append(West)
    if (p[0]) % 2 == 0:  # x坐标为偶数
        out.append(South)
    else:
        out.append(North)
    return out


def greed(now, goal):
    # """计算贪心方向（曼哈顿距离最短）"""
    out = []
    x1, y1 = now
    x2, y2 = goal

    # 计算距离差
    dx = x2 - x1
    dy = y2 - y1

    # 优先选择距离差更大的方向
    if abs(dx) >= abs(dy):
        if dx > 0:
            out.append(East)
        elif dx < 0:
            out.append(West)
        if dy > 0:
            out.append(North)
        elif dy < 0:
            out.append(South)
    else:
        if dy > 0:
            out.append(North)
        elif dy < 0:
            out.append(South)
        if dx > 0:
            out.append(East)
        elif dx < 0:
            out.append(West)

    return out


def step(goal):
    # """第一阶段：贪心追逐"""
    global now_pos
    global head
    global stuck_count

    way_allow = can_turn(now_pos)  # 允许的转向
    greed_way = greed(now_pos, goal)  # 贪心方向

    # 优先级1：保持方向且是贪心方向
    if head in greed_way and can_move(head):
        move(head)
        now_pos = (get_pos_x(), get_pos_y())
        stuck_count = 0  # 重置卡住计数
        return True

    # 优先级2：贪心方向中符合转向约束的
    for g in greed_way:
        if g in way_allow and can_move(g):
            move(g)
            head = g
            now_pos = (get_pos_x(), get_pos_y())
            stuck_count = 0
            return True

    # 优先级3：保持当前方向（如果符合约束）
    if head in way_allow and can_move(head):
        move(head)
        now_pos = (get_pos_x(), get_pos_y())
        stuck_count += 1  # 没有接近目标，增加卡住计数
        return True

    # 优先级4：任意符合约束的方向
    for w in way_allow:
        if can_move(w):
            move(w)
            head = w
            now_pos = (get_pos_x(), get_pos_y())
            stuck_count += 1
            return True

    return False  # 无路可走


def step_2nd(goal):
    # """第二阶段：固定路径遍历（优化版）"""
    global now_pos
    global head

    way_allow = can_turn(now_pos)
    x, y = now_pos

    # 策略1：在左边界（x=0）时，优先垂直移动
    if x == 0:
        for direction in [South, North]:
            if direction in way_allow and can_move(direction):
                move(direction)
                head = direction
                now_pos = (get_pos_x(), get_pos_y())
                return True

    # 策略2：在x=1且向西时，强制向北
    elif x == 1 and head == West:
        if North in way_allow and can_move(North):
            move(North)
            head = North
            now_pos = (get_pos_x(), get_pos_y())
            return True

    # 策略3：其他位置优先水平移动
    else:
        for direction in [East, West]:
            if direction in way_allow and can_move(direction):
                move(direction)
                head = direction
                now_pos = (get_pos_x(), get_pos_y())
                return True

    # 备选：任意符合约束的方向
    for w in way_allow:
        if can_move(w):
            move(w)
            head = w
            now_pos = (get_pos_x(), get_pos_y())
            return True

    return False


def main5():
    # """优化的贪吃蛇主函数"""
    global now_pos
    global head
    global last_goal
    global stuck_count

    # 初始化
    clear()
    change_hat(Hats.Dinosaur_Hat)
    now_pos = (0, 0)
    head = East
    stuck_count = 0

    goal = measure()
    if goal == None:
        goal = (16, 16)  # 默认目标

    length = 1
    phase_1_threshold = 32 * 16  # 第一阶段阈值：416

    # 第一阶段：贪心追逐
    while length < phase_1_threshold:
        # 更新目标
        goal_tmp = measure()
        if goal_tmp != None:
            goal = goal_tmp
            length += 1
            stuck_count = 0  # 吃到苹果，重置卡住计数

        # 检测是否卡住（连续10步没有接近目标）
        if stuck_count > 32:
            # 尝试随机方向突破
            for direction in [North, South, East, West]:
                if can_move(direction):
                    move(direction)
                    head = direction
                    now_pos = (get_pos_x(), get_pos_y())
                    stuck_count = 0
                    break

        # 执行移动
        if not step(goal):
            change_hat(Hats.Brown_Hat)
            return

    # 第二阶段：固定路径遍历
    while True:
        # 更新目标
        goal_tmp = measure()
        if goal_tmp != None:
            goal = goal_tmp
            length += 1

        # 执行移动
        if not step_2nd(goal):
            change_hat(Hats.Brown_Hat)
            return


# main6: 固定哈密顿回路。
# 回路设计（32x32）：
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
