from __builtins__ import *
# 全科技功能初版；来源 lb_dinosaur.py，本地对照见docs/functional-validation.md。
import production
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0a257bbd27f0520464f5efe3baefe74c7d4f7168。

def bone_dinosaur():
    # 保留完整排行榜生产周期，正常结算后开始下一轮。
    while production.active(Items.Bone):
        before = num_items(Items.Bone)
        production_cycle()
        if num_items(Items.Bone) <= before:
            quick_print("生产周期没有净收益，停止：", Items.Bone)
            return

def production_cycle():
    clear()
    change_hat(Hats.Dinosaur_Hat)
    state = greedy_prefix()
    if state != None:
        cycle_loop(state[0], state[1], state[2])
    change_hat(Hats.Brown_Hat)

def greedy_prefix():
    global tracked_body
    global tracked_apples
    global tracked_target
    tracked_body = []
    tracked_apples = 0
    tracked_target = (0, 0)
    for _ in range(50000):
        if tracked_apples >= 10:
            break
        if not chase_step():
            quick_print("bridge_failed", "prefix", tracked_apples)
            return None
    quick_print("bridge_prefix", tracked_apples, get_time(), get_pos_x(), get_pos_y())
    for attempt in range(400):
        if not clear_west_column():
            break
        if len(tracked_body) > 31:
            break
        if get_entity_type() != Entities.Apple:
            path = west_bridge_path()
            if path != None:
                for direction in path:
                    if not tracked_move(direction):
                        quick_print("bridge_failed", "path", get_time())
                        return None
                safe = get_pos_x() == 0 and get_pos_y() == 31
                for x, y in tracked_body:
                    if not x:
                        safe = False
                if safe:
                    for _ in range(31):
                        if not tracked_move(South):
                            quick_print("bridge_failed", "west_column", get_time())
                            return None
                    for x, y in tracked_body:
                        if x:
                            safe = False
                    if len(tracked_body) > 31:
                        safe = False
                    if safe:
                        quick_print("safe_handoff", tracked_apples, len(tracked_body), get_time(), get_pos_x(), get_pos_y())
                        return tracked_apples, tracked_target[0], tracked_target[1]
                    break
        if not chase_step():
            break
    quick_print("bridge_failed", "no_safe_handoff", tracked_apples, get_time(), (get_pos_x(), get_pos_y()), tracked_target, tracked_body[:3], tracked_body[-3:])
    return None


def clear_west_column():
    # 先把头与整段身体移到x>0，之后桥接路线才不会留下西列旧身体。
    for step in range(128):
        clear = get_pos_x() > 0
        for x, y in tracked_body:
            if not x:
                clear = False
        if clear:
            return True
        x, y = get_pos_x(), get_pos_y()
        moved = False
        for dx, dy, direction in [(1, 0, East), (0, 1, North), (0, -1, South)]:
            q = (x + dx, y + dy)
            if q == tracked_target or q[0] > 31 or q[1] < 0 or q[1] > 31:
                continue
            if tracked_move(direction):
                moved = True
                break
        if not moved or len(tracked_body) > 31:
            return False
    return False


def tracked_move(direction):
    global tracked_apples
    global tracked_target
    old = (get_pos_x(), get_pos_y())
    eating = get_entity_type() == Entities.Apple
    if eating:
        target = measure()
    if not move(direction):
        return False
    tracked_body.append(old)
    if eating:
        tracked_apples += 1
        tracked_target = target
    else:
        tracked_body.pop(0)
    return True


def chase_step():
    x, y = get_pos_x(), get_pos_y()
    wx, wy = tracked_target
    if x < wx and tracked_move(East):
        return True
    if x > wx and tracked_move(West):
        return True
    if y < wy and tracked_move(North):
        return True
    if y > wy and tracked_move(South):
        return True
    return tracked_move(North) or tracked_move(East) or tracked_move(South) or tracked_move(West)


def west_bridge_path():
    start = (get_pos_x(), get_pos_y())
    goal = (0, 31)
    release = {}
    for i in range(len(tracked_body)):
        release[tracked_body[i]] = i + 1
    previous = {start: None}
    depth = {start: 0}
    queue = [start]
    head = 0
    while head < len(queue) and goal not in previous:
        x, y = queue[head]
        head += 1
        for dx, dy, direction in [(0, 1, North), (1, 0, East), (0, -1, South), (-1, 0, West)]:
            q = (x + dx, y + dy)
            if q[0] < 0 or q[0] > 31 or q[1] < 0 or q[1] > 31:
                continue
            if q[0] == 0 and q != goal:
                continue
            if q == goal and (x, y) != (1, 31):
                continue
            if (q == tracked_target and q != goal) or q in previous:
                continue
            step = depth[(x, y)] + 1
            # 比释放时刻严格晚一拍，不依赖当前尾格的canMoveTo动画标志。
            if q in release and step <= release[q]:
                continue
            previous[q] = ((x, y), direction)
            depth[q] = step
            queue.append(q)
    if goal not in previous:
        return None
    reverse = []
    p = goal
    while p != start:
        p, direction = previous[p]
        reverse.append(direction)
    path = []
    for i in range(len(reverse) - 1, -1, -1):
        path.append(reverse[i])
    return path

def cycle_loop(snake, wx, wy):
    # 参照这个地址来实现
    # https://www.reddit.com/r/TheFarmerWasReplaced/comments/1o90hxs/my_sna_i_mean_dinosaur_algorithm/
    s = get_world_size()
    m = s - 1
    l = s * s // 2  # 苹果观测次数阈值；直段可能经过苹果，因此不等于精确尾长。

    dir = East
    while True:
        x, y = get_pos_x(), get_pos_y()
        if get_entity_type() == Entities.Apple:
            snake += 1
            wx, wy = measure()  # ty: ignore

        # 后期优先填满成对列间的空隙，缩小苹果可生成的区域。
        if snake > l:
            if y == 0 and can_move(North) and x % 2 == 1:
                for _ in range(m - 1):  # 避开最北的一行
                    # 碰尾只结束这段直走，下一轮仍按当前位置选路。
                    if not move(North):
                        break
                continue

        # 访问中心区域的果子
        if x != 0 and x != m:  # 不在左右两侧
            if (x == wx or x + 1 == wx) and x % 2 == 1:
                if can_move(North) and wy > y and wy != m:  # 向北可以到达苹果
                    for _ in range(wy - y):
                        move(North)
                    continue
            if (x == wx or x - 1 == wx) and x % 2 == 0:
                if can_move(South) and y > wy and wy != 0:  # 向南可以前往苹果
                    for _ in range(y - wy):
                        move(South)
                    continue

        # 围着操场逆时针转圈
        if dir == East:
            if y != 0 and can_move(South):
                while move(South) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == m:
                dir = North  # 在边界转向, 下面直接 move 节约一个循环
            if not (move(dir) or move(North)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == West:
            if y == m and can_move(dir) and x > wx + 1:
                for _ in range(x - wx - 1 - 1):  # 考虑到奇偶性，多减 1
                    move(dir)  # 快速移过最北边, 因为那是回程的线
            if y != m and can_move(North):
                while move(North) and get_entity_type() != Entities.Apple:
                    continue  # 回归边线
                continue
            if x == 0:
                dir = South  # 在边界转向
            if not (move(dir) or move(South)):  # 碰到边界或尾巴，向有空间的方向前进
                break
            continue
        if dir == South:
            if x != 0 and can_move(West):
                move(West)  # 回归边线
                continue
            if x == 0 and y != 0:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not (can_move(dir) or can_move(East)):
                    break  # 碰到尾巴
            dir = East  # 在边界转向
            continue
        if dir == North:
            if x != m and can_move(East):
                move(East)  # 回归边线
                continue
            if x == m and y != m:
                while move(dir) and get_entity_type() != Entities.Apple:
                    continue  # 边界上走直线，避免循环顶层大 while
                if not can_move(dir) and not can_move(West):
                    break  # 碰到尾巴
            dir = West  # 在边界转向
            continue


if __name__ == "__main__":
    bone_dinosaur()
