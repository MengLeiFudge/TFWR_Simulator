from __builtins__ import *
# 牵线搭桥：全科技一次性入口，分区保块配对，最多运行5分钟（300游戏秒）。

WORLD_SIZE = 24
SECTION_SIZE = 6
SECTION_ROWS = 4
MAX_ATTEMPTS = 64
MAX_STRATUM_HEIGHT = 4
MAX_GAME_SECONDS = 300
DIRECTIONS = [North, East, South, West]
DEPOT = (0, 0)
DELIVERY = (1, 0)
MATCH_GOAL = None


# 分区处理后回收全部无人机，再合并余色；实际配对数必须严格超过整片95%。
def mushroom_matchmaker():
    global DEPOT
    global DELIVERY
    global MATCH_GOAL
    # 留出5游戏秒回收已派出的无人机，整次执行仍以300秒为上限。
    deadline = get_time() + MAX_GAME_SECONDS - 5
    set_world_size(WORLD_SIZE)
    clear()
    change_hat(Hats.Mining_Hat)
    jump(Unlocks.Mushrooms)
    reward = max(1, 2 ** (num_unlocked(Unlocks.Mushrooms) - 1))
    for attempt in range(MAX_ATTEMPTS):
        if get_time() >= deadline:
            quick_print("牵线搭桥达到5分钟上限，未完成。")
            return False
        if attempt > 0:
            clear()
            change_hat(Hats.Mining_Hat)
        MATCH_GOAL = None
        DEPOT = (0, 0)
        DELIVERY = (1, 0)
        bounds = match_prepare_stratum(deadline)
        if bounds == None:
            continue
        ceiling, bottom, missing = bounds
        if ceiling - bottom > MAX_STRATUM_HEIGHT:
            quick_print("本片厚度超出4层预算，换田。")
            continue
        total = WORLD_SIZE * WORLD_SIZE * (ceiling - bottom)
        if 100 * missing >= 5 * total:
            quick_print("本片采样损失过多，没有足够的95%配对预算，换田。")
            continue
        before = num_items(Items.Mushroom)
        MATCH_GOAL = before + 95 * total * reward / 200
        quick_print("蘑菇保块配对：第", attempt + 1, "片，原始总数", total)
        for plane in range(ceiling, bottom, -1):
            singles = match_region((0, WORLD_SIZE, 0, WORLD_SIZE), plane, deadline)
            if match_done():
                matched = 2 * (num_items(Items.Mushroom) - before) / reward
                quick_print("整片蘑菇配对：", matched, "/", total, "比例", 100 * matched / total, "游戏时间", get_time())
                quick_print("牵线搭桥配对条件已达到：严格超过95%，已回收全部无人机。")
                return True
            if singles == None:
                quick_print("保块配对停止或达到5分钟上限：层z", plane)
                return False
            for point, _tone in singles:
                if not match_move_to(point, deadline) or not match_dig(deadline):
                    return False
            matched = 2 * (num_items(Items.Mushroom) - before) / reward
            quick_print("整片蘑菇配对：", matched, "/", total, "比例", 100 * matched / total, "游戏时间", get_time())
            if 100 * matched > 95 * total:
                quick_print("牵线搭桥配对条件已达到：严格超过95%。")
                return True
        quick_print("本片未达到95%，换田。")
    quick_print("牵线搭桥未完成：已达到换田上限。")
    return False


# 整片目标由主机冻结并复制到子机；超过95%后停止继续整理余块。
def match_done():
    return MATCH_GOAL != None and num_items(Items.Mushroom) > MATCH_GOAL


# 每个矩形独占写入范围；两半完成即合并余色，不等待其他矩形的慢分区。
def match_region(bounds, plane, deadline):
    if get_time() >= deadline or match_done():
        return None
    x0, x1, y0, y1 = bounds
    columns = (x1 - x0) // SECTION_SIZE
    rows = (y1 - y0) // SECTION_ROWS
    if columns == 1 and rows == 1:
        return match_section(bounds, plane, deadline)
    if columns >= rows:
        middle = x0 + columns // 2 * SECTION_SIZE
        first = (x0, middle, y0, y1)
        second = (middle, x1, y0, y1)
    else:
        middle = y0 + rows // 2 * SECTION_ROWS
        first = (x0, x1, y0, middle)
        second = (x0, x1, middle, y1)
    handle = spawn_drone(match_region, second, plane, deadline)
    if handle == None:
        return None
    left = match_region(first, plane, deadline)
    right = wait_for(handle)
    if left == None or right == None:
        return None
    pool = {}
    for x in range(x0, x1):
        for y in range(y0, y1):
            pool[x, y] = -1
    for x in range(x0, x1, SECTION_SIZE):
        for y in range(y0, y1, SECTION_ROWS):
            pool[x, y] = -2
    for result in [left, right]:
        for point, tone in result:
            pool[point] = tone
    return match_merge(bounds, pool, plane, deadline)


# 并行清除覆盖层；只有角落采样柱挖穿整片，以原始地图面积乘厚度作为分母。
def match_prepare_stratum(deadline):
    if not match_move_to(DEPOT, deadline):
        return None
    # 无Jump的新田只找第一个可生成蘑菇的区块，避免为换片钻入高硬度深层。
    limit = get_pos_z() - 48
    while get_ground_type() != Grounds.Mushroom:
        if get_pos_z() <= limit or not match_dig(deadline):
            quick_print("本田未找到可达蘑菇片，换田。")
            return None
    ceiling = get_pos_z()
    while get_ground_type() == Grounds.Mushroom:
        if ceiling - get_pos_z() >= 6 or not match_dig(deadline):
            quick_print("蘑菇厚度超出3至6层范围或达到5分钟上限。")
            return None
    bottom = get_pos_z()
    if ceiling - bottom < 3:
        return None
    if ceiling - bottom > MAX_STRATUM_HEIGHT:
        return ceiling, bottom, ceiling - bottom
    handles = []
    ok = True
    for x in range(1, WORLD_SIZE):
        handle = spawn_drone(match_clear_column, x, ceiling, deadline)
        if handle == None:
            ok = False
            break
        handles.append(handle)
    if ok:
        ok = match_clear_column(0, ceiling, deadline)
    for handle in handles:
        if not wait_for(handle):
            ok = False
    if not ok:
        return None
    return ceiling, bottom, ceiling - bottom


# 每台无人机独占一列；只挖覆盖层，所有列到同一蘑菇顶面才开始搬运。
def match_clear_column(x, ceiling, deadline):
    for y in range(WORLD_SIZE):
        if (x, y) == DEPOT:
            continue
        if not match_move_to((x, y), deadline):
            return False
        while get_pos_z() > ceiling:
            if not match_dig(deadline):
                return False
        if get_pos_z() == ceiling and get_ground_type() != Grounds.Mushroom:
            quick_print("蘑菇顶面不完整：位置", x, y, get_pos_z())
            return False
    return True


# 无人机各自持有分区和接收坑；只把未配对余色交给主机，避免牺牲每区余数。
def match_section(bounds, plane, deadline):
    global DEPOT
    global DELIVERY
    x0, x1, y0, y1 = bounds
    DEPOT = (x0, y0)
    DELIVERY = (x0 + 1, y0)
    adjacent = {}
    for x in range(x0, x1):
        for y in range(y0, y1):
            adjacent[x, y] = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
    board = match_prepare_plane(plane, deadline, bounds)
    if board == None:
        return None
    result = match_layer(board, plane, adjacent, deadline, False)
    if result == False:
        if not match_done():
            quick_print("蘑菇分区搬运失败：范围", bounds, "位置", get_pos_x(), get_pos_y(), "游戏时间", get_time())
        return None
    return result


# 工作面保留本层蘑菇及低一格空位；低两格的接收坑允许原片下层自然配对。
def match_prepare_plane(plane, deadline, bounds):
    board = {DEPOT: -2}
    x0, x1, y0, y1 = bounds
    for x in range(x0, x1):
        for offset in range(y1 - y0):
            y = y0 + offset
            if x % 2 == 1:
                y = y1 - 1 - offset
            point = (x, y)
            if point == DEPOT:
                continue
            if not match_move_to(point, deadline):
                return None
            while get_pos_z() > plane or (get_pos_z() == plane and get_ground_type() != Grounds.Mushroom):
                if get_ground_type() == Grounds.Mushroom or not match_dig(deadline):
                    return None
            if get_pos_z() == plane:
                if get_stability() < 2:
                    quick_print("蘑菇稳定性不足以承受两格工作面，停止：位置", x, y)
                    return None
                board[point] = measure()
            else:
                if not match_fill(plane - 1, deadline):
                    return None
                board[point] = -1
    if not match_move_to(DEPOT, deadline):
        return None
    while get_pos_z() > plane - 2:
        if not match_dig(deadline):
            return None
    if not match_fill(plane - 2, deadline):
        return None
    return board


# 每区耗尽可配对颜色，把每色余数交给父矩形；全局达标后合作停止。
def match_layer(board, plane, adjacent, deadline, dynamic_depot):
    global DEPOT
    global DELIVERY
    for turn in range(WORLD_SIZE * WORLD_SIZE):
        if get_time() >= deadline or match_done():
            return False
        groups = {}
        for point in board:
            tone = board[point]
            if tone == -1 or tone == -2:
                continue
            if tone not in groups:
                groups[tone] = []
            groups[tone].append(point)
        pair = None
        if DELIVERY in board and board[DELIVERY] in groups and len(groups[board[DELIVERY]]) > 1:
            pair = [DELIVERY]
        else:
            for tone in groups:
                if len(groups[tone]) > 1:
                    pair = groups[tone]
                    break
        if pair == None:
            singles = []
            for point in board:
                if board[point] != -1 and board[point] != -2:
                    singles.append((point, board[point]))
            return singles
        if dynamic_depot:
            best = WORLD_SIZE * 2
            sx, sy = pair[0]
            for point in board:
                if board[point] == -2:
                    x, y = point
                    dx = abs(x - sx)
                    dy = abs(y - sy)
                    distance = min(dx, WORLD_SIZE - dx) + min(dy, WORLD_SIZE - dy)
                    if distance < best:
                        best = distance
                        DEPOT = point
            DELIVERY = adjacent[DEPOT][1]
        for point in adjacent[DEPOT]:
            if point in board and board[point] in groups and len(groups[board[point]]) > 1:
                DELIVERY = point
                pair = [point]
                break
        has_hole = False
        for point in board:
            if board[point] == -1:
                has_hole = True
                break
        if not has_hole and pair[0] != DELIVERY:
            # 坑边只剩各自唯一的颜色时，挖去其中一块作为首个空位。
            if not match_move_to(DELIVERY, deadline) or not match_dig(deadline):
                return False
            board[DELIVERY] = -1
            continue
        tone = board[pair[0]]
        result = match_transport(board, pair[0], plane, adjacent, deadline, DELIVERY, [DEPOT])
        if result == False:
            return False
        if result == None:
            continue
        # 有空位时先把两块都送到坑边，再提交配对，保留运输中失去伙伴的余块。
        committed = True
        for point in board:
            if board[point] == -1:
                committed = False
                break
        goal = adjacent[DEPOT][0]
        if goal == DELIVERY:
            goal = adjacent[DEPOT][1]
        blocked = [DEPOT, DELIVERY]
        if committed:
            if not match_push(board, DELIVERY, DEPOT, plane, adjacent, deadline):
                return False
            if get_pos_z() < plane - 1:
                if not match_fill(plane - 2, deadline):
                    return False
                continue
            goal = DELIVERY
            blocked = [DEPOT]
        for _ in range(len(board)):
            partner = None
            for point in board:
                if (committed or point != DELIVERY) and board[point] == tone:
                    partner = point
                    break
            if partner == None:
                if committed and (not match_move_to(DEPOT, deadline) or not match_dig(deadline)):
                    return False
                break
            result = match_transport(board, partner, plane, adjacent, deadline, goal, blocked)
            if result == False:
                return False
            if result == None:
                continue
            if not committed:
                if not match_push(board, DELIVERY, DEPOT, plane, adjacent, deadline):
                    return False
                if get_pos_z() < plane - 1:
                    if not match_fill(plane - 2, deadline):
                        return False
                    break
            if not match_push(board, goal, DEPOT, plane, adjacent, deadline):
                return False
            break
        if not match_move_to(DEPOT, deadline) or not match_fill(plane - 2, deadline):
            return False
        if turn % 16 == 0:
            quick_print("保块搬运：层z", plane, "配对批次", turn + 1)
    quick_print("保块搬运达到本层批次上限，停止。")
    return False


# 四个邻接小区并行合并余色，返回每色至多一块，缩小最后一次全场搬运。
def match_merge(bounds, pool, plane, deadline):
    global DEPOT
    global DELIVERY
    x0, x1, y0, y1 = bounds
    DEPOT = (x0, y0)
    DELIVERY = (x0 + 1, y0)
    board = {}
    adjacent = {}
    for x in range(x0, x1):
        for y in range(y0, y1):
            point = (x, y)
            board[point] = pool[point]
            adjacent[point] = [(x, (y + 1) % WORLD_SIZE), ((x + 1) % WORLD_SIZE, y),
                               (x, (y - 1) % WORLD_SIZE), ((x - 1) % WORLD_SIZE, y)]
    result = match_layer(board, plane, adjacent, deadline, True)
    if result == False:
        return None
    return result


# 规则网格先走两个轴的短路径，只有被接收坑阻挡时才用BFS绕行。
def match_route(board, source, goal, blocked, adjacent, deadline):
    for order in [(0, 1), (1, 0)]:
        route = []
        point = source
        valid = True
        for axis in order:
            steps = (goal[axis] - point[axis]) % WORLD_SIZE
            direction = 1 - axis
            if steps > WORLD_SIZE // 2:
                steps = WORLD_SIZE - steps
                direction += 2
            for _ in range(steps):
                if get_time() >= deadline:
                    return None
                point = adjacent[point][direction]
                if point not in board or board[point] == -2 or point in blocked:
                    valid = False
                    break
                route.append(point)
            if not valid:
                break
        if valid:
            return route[::-1]
    found = match_search(board, source, goal, blocked, adjacent, deadline)
    if found == None:
        return None
    parents, point = found
    route = []
    while point != source:
        route.append(point)
        point = parents[point]
    return route


# 把选定蘑菇送到交付格；None表示途中已自然配对，调用者重新选择伙伴。
def match_transport(board, source, plane, adjacent, deadline, goal, blocked):
    route = match_route(board, source, goal, blocked, adjacent, deadline)
    if route == None:
        quick_print("蘑菇运输没有可达路径：", source, goal, "保护", blocked)
        return False
    while len(route) > 0:
        target = route.pop()
        found = match_search(board, target, None, blocked + [source], adjacent, deadline)
        if found == None:
            quick_print("蘑菇运输没有可达空位：", source, target, "保护", blocked)
            return False
        parents, hole = found
        while hole != target:
            previous = parents[hole]
            if not match_push(board, previous, hole, plane, adjacent, deadline):
                return False
            hole = previous
        if not match_push(board, source, target, plane, adjacent, deadline):
            return False
        if board[target] == -1:
            return None
        source = target
    return True


# BFS只遍历已公开的平面邻接；goal为空时寻找空位，屏蔽接收坑及正在运输的块。
def match_search(board, start, goal, blocked, adjacent, deadline):
    parents = {start: start}
    queue = [start]
    head = 0
    while head < len(queue):
        if get_time() >= deadline:
            return None
        point = queue[head]
        head += 1
        if point == goal or (goal == None and board[point] == -1):
            return parents, point
        for neighbor in adjacent[point]:
            if neighbor in board and board[neighbor] != -2 and neighbor not in blocked and neighbor not in parents:
                parents[neighbor] = point
                queue.append(neighbor)
    return None


# 一次推送后只重读两端；普通空位若自动配对则补土，保持低一格的搬运高度。
def match_push(board, source, target, plane, adjacent, deadline):
    if match_done():
        return False
    if not match_move_to(source, deadline) or get_pos_z() != plane or get_ground_type() != Grounds.Mushroom:
        quick_print("蘑菇推送源状态变化或超时：", source, target, "高度", get_pos_z(), "应为", plane)
        return False
    direction = None
    for i in range(4):
        if adjacent[source][i] == target:
            direction = DIRECTIONS[i]
            break
    if direction == None or not can_push(direction) or not push(direction):
        quick_print("蘑菇推送失败：", source, target)
        return False
    if match_done():
        return False
    if get_pos_z() != plane - 1:
        return False
    board[source] = -1
    if not match_move_to(target, deadline):
        return False
    if target == DEPOT:
        return plane - 3 <= get_pos_z() <= plane - 1
    if get_pos_z() == plane:
        board[target] = measure()
        return True
    if get_pos_z() != plane - 2 or not match_fill(plane - 1, deadline):
        quick_print("蘑菇推送目标高度异常：", source, target, "高度", get_pos_z(), "应为", plane, "或", plane - 2)
        return False
    board[target] = -1
    return True


# 土台搭在已空出的高度，不破坏下方未采蘑菇；后续工作层再拆土，每次place正常耗Block。
def match_fill(height, deadline):
    while get_pos_z() < height:
        if get_time() >= deadline or num_items(Items.Block) < 1 or not place(Grounds.Dirt):
            quick_print("临时土台材料不足、放置失败或达到时间上限。")
            return False
    return get_pos_z() == height


# 只用于覆盖层、已配对余数及土台；统一检查时间、硬度和动作结果。
def match_dig(deadline):
    if get_time() + get_hardness() / (1.5 ** num_unlocked(Unlocks.Mining)) >= deadline or get_hardness() >= 10000000 or not dig():
        quick_print("蘑菇保块下挖失败：位置", get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


# 分区写入各自范围；阶段间先回收子机，再由主机合并余色。
def match_move_to(point, deadline):
    if get_time() >= deadline or match_done():
        return False
    x, y = point
    for delta, forward, backward in [(x - get_pos_x(), East, West), (y - get_pos_y(), North, South)]:
        steps = delta % WORLD_SIZE
        direction = forward
        if steps > WORLD_SIZE // 2:
            steps = WORLD_SIZE - steps
            direction = backward
        for _ in range(steps):
            if get_time() >= deadline or not move(direction):
                return False
    return True


if __name__ == "__main__":
    mushroom_matchmaker()
