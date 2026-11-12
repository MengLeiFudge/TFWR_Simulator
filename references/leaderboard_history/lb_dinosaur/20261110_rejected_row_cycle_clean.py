from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/over50-screen-20261109/lb_dinosaur_row_cycle_clean.py
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0a257bbd27f0520464f5efe3baefe74c7d4f7168。

def lb_dinosaur():
    clear()
    change_hat(Hats.Dinosaur_Hat)
    cycle_loop(0, 0, 0)
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
    # 方向筛选：从桥接后的起点沿行蛇形Hamilton环前进，不使用原边界/成对列控制器。
    size = get_world_size()
    last = size - 1
    while snake < size * size:
        if get_entity_type() == Entities.Apple:
            snake += 1
        x = get_pos_x()
        y = get_pos_y()
        if y % 2 == 0:
            if x < last:
                if not move(East):
                    return
            else:
                if not move(North):
                    return
        else:
            if x > 0:
                if not move(West):
                    return
            else:
                if not move(North):
                    return


if __name__ == "__main__":
    lb_dinosaur()
