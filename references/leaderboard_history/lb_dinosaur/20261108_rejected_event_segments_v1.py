from __builtins__ import *
# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/nonreset-100-20261108/dinosaur-event-segments-v1/lb_dinosaur.py
# Copyright (c) 2026 enihsyou；MIT许可见enihsyou_LICENSE.txt。
# 来源：enihsyou/The-Farmer-Was-Replaced，blob 0a257bbd27f0520464f5efe3baefe74c7d4f7168。

def lb_dinosaur():
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
    global event_x
    global event_y
    global event_gx
    global event_gy
    global event_length
    global event_pending
    global event_moves
    global event_goal
    event_x = get_pos_x()
    event_y = get_pos_y()
    event_gx = wx
    event_gy = wy
    event_length = snake
    event_pending = False
    event_moves = 0
    s = get_world_size()
    m = s - 1
    l = s * s // 2
    event_goal = s * s - 1
    direction = East
    while event_moves < 200000 and event_length < event_goal:
        if not event_pending and event_x == event_gx and event_y == event_gy:
            read_event_target()
        x, y = event_x, event_y
        wx, wy = event_gx, event_gy
        route_length = event_length
        if event_pending:
            route_length += 1
        if route_length > l:
            if y == 0 and can_move(North) and x % 2 == 1:
                walk_event_segment(North, m - 1, False)
                continue
        if x != 0 and x != m:
            if (x == wx or x + 1 == wx) and x % 2 == 1:
                if can_move(North) and wy > y and wy != m:
                    walk_event_segment(North, wy - y, False)
                    continue
            if (x == wx or x - 1 == wx) and x % 2 == 0:
                if can_move(South) and y > wy and wy != 0:
                    walk_event_segment(South, y - wy, False)
                    continue
        if direction == East:
            if y != 0 and can_move(South):
                walk_event_segment(South, y, True)
                continue
            if x == m:
                direction = North
            if not (walk_event_segment(direction, 1, False) or walk_event_segment(North, 1, False)):
                break
            continue
        if direction == West:
            if y == m and can_move(direction) and x > wx + 1:
                walk_event_segment(direction, x - wx - 2, False)
            if y != m and can_move(North):
                walk_event_segment(North, m - y, True)
                continue
            if x == 0:
                direction = South
            if not (walk_event_segment(direction, 1, False) or walk_event_segment(South, 1, False)):
                break
            continue
        if direction == South:
            if x != 0 and can_move(West):
                walk_event_segment(West, 1, False)
                continue
            if x == 0 and y != 0:
                walk_event_segment(direction, y, True)
                if not (can_move(direction) or can_move(East)):
                    break
            direction = East
            continue
        if direction == North:
            if x != m and can_move(East):
                walk_event_segment(East, 1, False)
                continue
            if x == m and y != m:
                walk_event_segment(direction, m - y, True)
                if not can_move(direction) and not can_move(West):
                    break
            direction = West
    quick_print("dinosaur_event_end", event_length, event_moves, get_time())


def read_event_target():
    global event_gx
    global event_gy
    global event_pending
    future = measure()
    if future == None:
        event_gx, event_gy = -1, -1
    else:
        event_gx, event_gy = future
    event_pending = True


# 只在已知苹果处拆开直段；坐标和增长在真实move成功后提交。
def walk_event_segment(direction, steps, stop_at_apple):
    global event_x
    global event_y
    global event_length
    global event_pending
    global event_moves
    dx, dy = EVENT_STEP[direction]
    steps = min(steps, 200000 - event_moves)
    if steps <= 0:
        return True
    while steps > 0:
        if event_pending:
            if not move(direction):
                return False
            event_x += dx
            event_y += dy
            event_length += 1
            event_pending = False
            event_moves += 1
            steps -= 1
            if event_length >= event_goal:
                return True
            if stop_at_apple and event_x == event_gx and event_y == event_gy:
                return True
            continue
        if event_x == event_gx and event_y == event_gy:
            read_event_target()
            continue
        span = steps
        if dx != 0 and event_y == event_gy and (event_gx - event_x) * dx > 0:
            span = min(span, abs(event_gx - event_x))
        elif dy != 0 and event_x == event_gx and (event_gy - event_y) * dy > 0:
            span = min(span, abs(event_gy - event_y))
        taken = 0
        for step in range(span):
            if not move(direction):
                event_x += dx * taken
                event_y += dy * taken
                event_moves += taken
                return False
            taken += 1
        event_x += dx * taken
        event_y += dy * taken
        event_moves += taken
        steps -= taken
        if stop_at_apple and event_x == event_gx and event_y == event_gy:
            return True
    return True


EVENT_STEP = {North: (0, 1), East: (1, 0), South: (0, -1), West: (-1, 0)}


if __name__ == "__main__":
    lb_dinosaur()
