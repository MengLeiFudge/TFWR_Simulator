from __builtins__ import *
# 牵线搭桥：单机保块搬运，按整片全部厚度的实际配对数判断是否严格超过95%。

WORLD_SIZE = 16
MAX_ATTEMPTS = 4
MAX_GAME_SECONDS = 20000
DIRECTIONS = [North, East, South, West]
DEPOT = (0, 0)
DELIVERY = (1, 0)


# 独立运行，角落采样柱测厚后作为接收坑；一片达标便保留现场并退出。
def mushroom_matchmaker():
    set_world_size(WORLD_SIZE)
    clear()
    change_hat(Hats.Mining_Hat)
    jump(Unlocks.Mushrooms)
    deadline = get_time() + MAX_GAME_SECONDS
    adjacent = {}
    for x in range(WORLD_SIZE):
        for y in range(WORLD_SIZE):
            adjacent[x, y] = [(x, (y + 1) % WORLD_SIZE), ((x + 1) % WORLD_SIZE, y),
                              (x, (y - 1) % WORLD_SIZE), ((x - 1) % WORLD_SIZE, y)]
    reward = max(1, 2 ** (num_unlocked(Unlocks.Mushrooms) - 1))
    for attempt in range(MAX_ATTEMPTS):
        if attempt > 0:
            clear()
            change_hat(Hats.Mining_Hat)
        bounds = match_prepare_stratum(deadline)
        if bounds == None:
            return False
        ceiling, bottom, missing = bounds
        total = WORLD_SIZE * WORLD_SIZE * (ceiling - bottom)
        # 每层最多六个颜色余数和一个启动空位，先为整片保留严格小于5%的损失预算。
        if 100 * (missing + 7 * (ceiling - bottom)) >= 5 * total:
            quick_print("本片采样损失过多，没有足够的95%配对预算，换田。")
            continue
        before = num_items(Items.Mushroom)
        quick_print("蘑菇保块配对：第", attempt + 1, "片，原始总数", total)
        for plane in range(ceiling, bottom, -1):
            board = match_prepare_plane(plane, deadline)
            if board == None or not match_layer(board, plane, adjacent, deadline):
                quick_print("保块配对停止：层z", plane)
                return False
            matched = 2 * (num_items(Items.Mushroom) - before) / reward
            quick_print("整片蘑菇配对：", matched, "/", total, "比例", 100 * matched / total)
            if 100 * matched > 95 * total:
                quick_print("牵线搭桥配对条件已达到：严格超过95%。")
                return True
        quick_print("本片未达到95%，换田。")
    quick_print("牵线搭桥未完成：已达到换田上限。")
    return False


# 先只清覆盖层；角落采样最多六块，原始总数包含采样损失和所有后续损失。
def match_prepare_stratum(deadline):
    if not match_move_to(DEPOT, deadline):
        return None
    limit = get_pos_z() - 48
    while get_ground_type() != Grounds.Mushroom:
        if get_pos_z() <= limit or not match_dig(deadline):
            quick_print("未找到可达蘑菇层，停止。")
            return None
    ceiling = get_pos_z()
    for x in range(WORLD_SIZE):
        for offset in range(WORLD_SIZE):
            y = offset
            if x % 2 == 1:
                y = WORLD_SIZE - 1 - offset
            if not match_move_to((x, y), deadline):
                return None
            while get_pos_z() > ceiling:
                if not match_dig(deadline):
                    return None
            if get_pos_z() != ceiling or get_ground_type() != Grounds.Mushroom:
                quick_print("蘑菇顶面不完整，停止：位置", x, y, get_pos_z())
                return None
    if not match_move_to(DEPOT, deadline):
        return None
    while get_ground_type() == Grounds.Mushroom:
        if ceiling - get_pos_z() >= 6 or not match_dig(deadline):
            quick_print("蘑菇厚度超出已核对的3至6层范围，停止。")
            return None
    bottom = get_pos_z()
    if ceiling - bottom < 3:
        return None
    missing = 0
    for x in range(WORLD_SIZE):
        for offset in range(WORLD_SIZE):
            y = offset
            if x % 2 == 1:
                y = WORLD_SIZE - 1 - offset
            if not match_move_to((x, y), deadline):
                return None
            missing += min(ceiling - bottom, max(0, ceiling - get_pos_z()))
    return ceiling, bottom, missing


# 工作面只保留本层蘑菇和低一格的空位；接收坑低两格且以普通土隔开下层颜色。
def match_prepare_plane(plane, deadline):
    board = {DEPOT: -2}
    for x in range(WORLD_SIZE):
        for offset in range(WORLD_SIZE):
            y = offset
            if x % 2 == 1:
                y = WORLD_SIZE - 1 - offset
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
        if get_ground_type() == Grounds.Mushroom or not match_dig(deadline):
            return None
    if not match_fill(plane - 2, deadline) or get_ground_type() == Grounds.Mushroom:
        return None
    # 满面没有空位时只牺牲一块启动；以后所有移动都由这个空位或配对产生的空位完成。
    has_hole = False
    for point in board:
        if board[point] == -1:
            has_hole = True
            break
    if not has_hole:
        if not match_move_to(DELIVERY, deadline) or not match_dig(deadline):
            return None
        board[DELIVERY] = -1
    return board


# 每种颜色先耗尽同色对；途中自动配对同样计入收益，只丢弃每种颜色最终的一块余数。
def match_layer(board, plane, adjacent, deadline):
    for turn in range(WORLD_SIZE * WORLD_SIZE):
        groups = {}
        for point in board:
            tone = board[point]
            if tone == -1 or tone == -2:
                continue
            if tone not in groups:
                groups[tone] = []
            groups[tone].append(point)
        pair = None
        for tone in groups:
            if len(groups[tone]) > 1:
                pair = groups[tone]
                break
        if pair == None:
            for point in board:
                if board[point] != -1 and board[point] != -2:
                    if not match_move_to(point, deadline) or not match_dig(deadline):
                        return False
                    board[point] = -1
            return True
        tone = board[pair[0]]
        result = match_transport(board, pair[0], plane, adjacent, deadline)
        if result == False:
            return False
        if result == None:
            continue
        # 搬运途中可能已消耗原定的另一块；确认仍有伙伴后才占用接收坑。
        partner = None
        for point in board:
            if point != DELIVERY and board[point] == tone:
                partner = point
                break
        if partner == None:
            continue
        if not match_push(board, DELIVERY, DEPOT, plane, adjacent, deadline):
            return False
        for _ in range(WORLD_SIZE * WORLD_SIZE):
            partner = None
            for point in board:
                if board[point] == tone:
                    partner = point
                    break
            if partner == None:
                # 最后一位伙伴已与下一层自然配对；坑内余块仍是该颜色唯一余数。
                if not match_move_to(DEPOT, deadline) or not match_dig(deadline):
                    return False
                break
            result = match_transport(board, partner, plane, adjacent, deadline)
            if result == False:
                return False
            if result == None:
                continue
            if not match_push(board, DELIVERY, DEPOT, plane, adjacent, deadline):
                return False
            break
        if not match_move_to(DEPOT, deadline) or get_pos_z() != plane - 2 or get_ground_type() == Grounds.Mushroom:
            return False
        if turn % 16 == 0:
            quick_print("保块搬运：层z", plane, "配对批次", turn + 1)
    quick_print("保块搬运达到本层批次上限，停止。")
    return False


# 把选定蘑菇送到固定交付格；None表示途中已自然配对，调用者重新选择伙伴。
def match_transport(board, source, plane, adjacent, deadline):
    found = match_search(board, source, DELIVERY, {DEPOT}, adjacent)
    if found == None:
        return False
    parents, point = found
    route = []
    while point != source:
        route.append(point)
        point = parents[point]
    while len(route) > 0:
        target = route.pop()
        found = match_search(board, target, None, {DEPOT, source}, adjacent)
        if found == None:
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
def match_search(board, start, goal, blocked, adjacent):
    parents = {start: start}
    queue = [start]
    head = 0
    while head < len(queue):
        point = queue[head]
        head += 1
        if point == goal or (goal == None and board[point] == -1):
            return parents, point
        for neighbor in adjacent[point]:
            if neighbor not in blocked and neighbor not in parents:
                parents[neighbor] = point
                queue.append(neighbor)
    return None


# 一次推送后只重读两端；普通空位若自动配对则补土，保持低一格的搬运高度。
def match_push(board, source, target, plane, adjacent, deadline):
    if not match_move_to(source, deadline) or get_pos_z() != plane or get_ground_type() != Grounds.Mushroom:
        return False
    direction = None
    for i in range(4):
        if adjacent[source][i] == target:
            direction = DIRECTIONS[i]
            break
    if direction == None or not can_push(direction) or not push(direction):
        return False
    if get_pos_z() != plane - 1:
        return False
    board[source] = -1
    if not match_move_to(target, deadline):
        return False
    if target == DEPOT:
        return get_pos_z() == plane - 1 or get_pos_z() == plane - 2
    if get_pos_z() == plane:
        board[target] = measure()
        return True
    if get_pos_z() != plane - 2 or not match_fill(plane - 1, deadline):
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
    if get_time() >= deadline or get_hardness() >= 10000000 or not dig():
        quick_print("蘑菇保块下挖失败：位置", get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


# 单机访问采用环绕短路径，不把地层状态交给其他无人机修改。
def match_move_to(point, deadline):
    if get_time() >= deadline:
        return False
    x, y = point
    for delta, forward, backward in [(x - get_pos_x(), East, West), (y - get_pos_y(), North, South)]:
        steps = delta % WORLD_SIZE
        direction = forward
        if steps > WORLD_SIZE // 2:
            steps = WORLD_SIZE - steps
            direction = backward
        for _ in range(steps):
            if not move(direction):
                return False
    return True


if __name__ == "__main__":
    mushroom_matchmaker()
