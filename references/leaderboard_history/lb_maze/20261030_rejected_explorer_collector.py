from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-sol/open-directions/maze-explorer-collector/lb_maze.py
# 私有固定协议代表；完整时间尚未取得。
# 算法来源：zzlg-git/TheFarmerWasReplaced_Maze_1min28s，commit e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629。
# 复用上游DFS与路由；16座8×8，每宫两机按目标左右半区唯一分派。

WORLD = 32
TARGET_GOLD = 9863168
DRONES = 16
REUSE_LIMIT = 300

# 方向编号：0北、1东、2南、3西；BACK给出反向编号。
DIRS = [North, East, South, West]
BACK = [2, 3, 0, 1]
MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)


# ---------- 1. 开放地面移动与固定排布 ----------

def lb_maze():
	global run_until
	run_until = get_time() + 200
	# 已达标直接退出。
	if num_items(Items.Gold) >= TARGET_GOLD:
		return
	jobs = make_jobs()
	stock = num_items(Items.Weird_Substance)
	set_world_size(WORLD)
	clear()
	set_execution_speed(0)
	t0 = get_time()
	records = deploy(jobs, stock)
	elapsed = get_time() - t0

	# 全场结束后统计，可删除。
	generations = 0
	total_boxes = 0
	for n, count, boxes in records:
		generations += count
		total_boxes += boxes
	quick_print("结束，秒:", elapsed, "黄金:", num_items(Items.Gold), "版本: 16-team-static")
	quick_print("双机小组结果数:", len(records), "建图代数:", generations, "宝箱总数:", total_boxes)
	for side in [8]:
		count = 0
		boxes = 0
		for n, gen, b in records:
			if n == side:
				count += 1
				boxes += b
		quick_print("边长:", side, "台数:", count, "宝箱:", boxes,
					"每机黄金:", boxes * side * side * MULT / count)


def go_empty(tx, ty):
	# 仅用于所有迷宫生成前。利用32x32农场环绕，分别走较短的横、纵位移。
	dx = (tx - get_pos_x()) % WORLD
	if dx <= WORLD // 2:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(WORLD - dx):
			move(West)
	dy = (ty - get_pos_y()) % WORLD
	if dy <= WORLD // 2:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(WORLD - dy):
			move(South)


def go_home(cx, cy):
	# 仅在本宫已经harvest消失后调用；路线留在原方块内部，不环绕穿过邻宫。
	while get_pos_x() < cx:
		move(East)
	while get_pos_x() > cx:
		move(West)
	while get_pos_y() < cy:
		move(North)
	while get_pos_y() > cy:
		move(South)


def make_jobs():
    jobs = []
    for y in range(4):
        for x in range(4):
            jobs.append((8, 4 + x * 8, 4 + y * 8))
    return jobs


# ---------- 2. 几何邻接与每代一次的DFS建图 ----------

def geometry(n):
	# 本地格号 p=y*n+x；grid[p][方向]是几何邻居，-1表示本宫边界。
	# 几何表。
	grid = []
	for y in range(n):
		for x in range(n):
			p = y * n + x
			row = [-1, -1, -1, -1]
			if y < n - 1:
				row[0] = p + n
			if x < n - 1:
				row[1] = p + 1
			if y > 0:
				row[2] = p - n
			if x > 0:
				row[3] = p - 1
			grid.append(row)
	return grid


def explore(n, grid, home):
	# links记录实测通路；graph供DFS选择未访问的邻居，建图后不再返回。
	# walls记录当时仍有墙的方向；以后可能从两端之一发现该墙已经消失。
	count = n * n
	links = []
	graph = []
	walls = []
	seen = []
	parent = []
	up_hop = []
	down_hop = []
	for _ in range(count):
		links.append([-1, -1, -1, -1])
		graph.append([])
		walls.append([])
		seen.append(False)
		parent.append(-1)
		up_hop.append(None)
		down_hop.append(None)

	# order是父节点先于子节点的顺序；trail记录真正走过的DFS回退方向。
	order = []
	trail = []
	p = home
	visited = 0
	while True:
		if not seen[p]:
			# 正常取消条件：其它机可能已凑够黄金，没必要继续建这张图。
			if num_items(Items.Gold) >= TARGET_GOLD:
				return None
			seen[p] = True
			visited += 1
			order.append(p)
			for d in range(4):
				q = grid[p][d]
				# 边界不能跨；已从另一端记下的通路不用重复探测。
				if q == -1 or links[p][d] != -1:
					continue
				if can_move(DIRS[d]):
					back = BACK[d]
					links[p][d] = q
					links[q][back] = p
					graph[p].append((q, d))
					graph[q].append((p, back))
				else:
					walls[p].append(d)
			if visited == count:
				break

		choice = -1
		next_p = -1
		for q, d in graph[p]:
			if not seen[q]:
				choice = d
				next_p = q
				break
		if choice != -1:
			move(DIRS[choice])
			parent[next_p] = p
			up_hop[next_p] = (p, DIRS[BACK[choice]])
			down_hop[next_p] = (next_p, DIRS[choice])
			trail.append(BACK[choice])
			p = next_p
		else:
			# 连通树、尚有未访问节点：必然还有可以回退的祖先。
			d = trail.pop()
			move(DIRS[d])
			p = grid[p][d]

	# 初始根parent=-1；up_hop是往父节点走的指令，down_hop是相反指令。
	tree = (parent, up_hop, down_hop, order)
	return (p, links, walls, tree)


# ---------- 3. 全点对路由初始化与单条新边的增量更新 ----------

def build_all_routes(tree, blank):
	# rows[目标][0][起点] = 最短距离。
	# rows[目标][1][起点] = (下一格, 游戏方向对象)。注意第一维是“目标”。
	parent, up_hop, down_hop, order = tree
	rows = []
	for goal in range(len(blank)):
		dist = list(blank)
		hop = list(up_hop)
		dist[goal] = 0
		hop[goal] = None
		rows.append([dist, hop])
	# 每加入一个叶节点，只算它与已加入节点的无序点对，并填写双向首步。
	visited = []
	for v in order:
		p = parent[v]
		if p != -1:
			dist_v, toward_v = rows[v]
			parent_hop = rows[p][1]
			up = up_hop[v]
			down = down_hop[v]
			for u in visited:
				dist_u, toward_u = rows[u]
				distance = dist_u[p] + 1
				dist_u[v] = distance
				toward_u[v] = up
				dist_v[u] = distance
				if u == p:
					toward_v[u] = down
				else:
					toward_v[u] = parent_hop[u]
		visited.append(v)
	return rows


def add_route_edge(rows, a, b, hop_ab, hop_ba):
	# 已知图刚新增一条无向单位边a--b。
	# 新最短路只能是：旧路、经a->b、经b->a。无需重新跑BFS。
	da, ha = rows[a]
	db, hb = rows[b]
	left = []
	right = []

	# 必须先冻结两侧距离与首步，再开始修改rows。
	# left: D(u,a)+1 < D(u,b)；right: D(v,b)+1 < D(v,a)。
	# 只有左右两组之间的点对可能变短；快照里仅一侧加1，代表新边长度。
	for u in range(len(rows)):
		x = da[u]
		y = db[u]
		if x + 1 < y:
			next_hop = ha[u]
			if u == a:
				next_hop = hop_ab
			left.append((u, x + 1, next_hop, rows[u]))
		elif y + 1 < x:
			next_hop = hb[u]
			if u == b:
				next_hop = hop_ba
			right.append((u, y, next_hop, rows[u]))

	# 把较小集合放外层；x+y仍然只包含一次新边长度，互换不改变计算。
	if len(left) > len(right):
		left, right = right, left
	for u, x, hop_u, row_u in left:
		dist_u, toward_u = row_u
		for v, y, hop_v, row_v in right:
			candidate = x + y
			# 这是算法条件：只更新严格更短的路线，等长时保留原首步。
			if candidate < dist_u[v]:
				dist_u[v] = candidate
				# row_u的目标是u，因此起点v应采用hop_v，而不是hop_u。
				toward_u[v] = hop_v
				dist_v, toward_v = row_v
				dist_v[u] = candidate
				toward_v[u] = hop_u


# ---------- 4. 出发点探墙与单宫收割 ----------

def scan_departure(p, links, walls, grid, routes):
	# 固定原SENSOR_MODE=1：只在上一箱位置、下一次出发前检查原来的墙。
	# 发现一条边便完整更新路由表。
	remaining = []
	for side in walls[p]:
		# 同一条墙可能早已从另一端发现，必须去重。
		if links[p][side] != -1:
			continue
		if can_move(DIRS[side]):
			q = grid[p][side]
			back = BACK[side]
			links[p][side] = q
			links[q][back] = p
			add_route_edge(routes, p, q, (q, DIRS[side]), (p, DIRS[back]))
		else:
			remaining.append(side)
	walls[p] = remaining


def solve_one(n, bx, by, grid, mapped, blank):
    p = mapped
    graph = []
    for row in grid:
        graph.append(list(row))
    helper = spawn_drone(explore_for_collector, n, grid, p)
    boxes = 0
    keep = True
    while num_items(Items.Gold) < TARGET_GOLD and get_time() < run_until:
        if helper != None and has_finished(helper):
            observed = wait_for(helper)
            helper = None
            if observed != None:
                graph = observed
        target = measure()
        if target == None:
            break
        goal = (target[1] - by) * n + target[0] - bx
        for d in range(4):
            q = grid[p][d]
            if q != -1 and graph[p][d] == -1 and can_move(DIRS[d]):
                graph[p][d] = q
                graph[q][BACK[d]] = p
        while p != goal:
            path = optimistic_path(p, goal, graph, blank)
            if path == None:
                keep = False
                break
            for d in path:
                q = grid[p][d]
                if not can_move(DIRS[d]):
                    graph[p][d] = -1
                    graph[q][BACK[d]] = -1
                    break
                if not move(DIRS[d]):
                    keep = False
                    break
                p = q
            if not keep:
                break
        if not keep or num_items(Items.Gold) >= TARGET_GOLD or get_time() >= run_until:
            break
        cost = n * MULT
        if num_items(Items.Weird_Substance) < cost:
            keep = False
            break
        if use_item(Items.Weird_Substance, cost):
            boxes += 1
        else:
            if get_entity_type() != Entities.Treasure or not harvest():
                keep = False
            else:
                boxes += 1
            break
    if helper != None:
        wait_for(helper)
    if not keep:
        return None
    return boxes


def explore_for_collector(n, grid, p):
    links = []
    for _ in range(n * n):
        links.append([-1, -1, -1, -1])
    seen = {p}
    trail = []
    while get_time() < run_until:
        if get_entity_type() not in [Entities.Hedge, Entities.Treasure]:
            return None
        for d in range(4):
            q = grid[p][d]
            if q != -1 and can_move(DIRS[d]):
                links[p][d] = q
                links[q][BACK[d]] = p
        choice = -1
        for d in range(4):
            q = links[p][d]
            if q != -1 and q not in seen:
                choice = d
                break
        if choice != -1:
            p = grid[p][choice]
            move(DIRS[choice])
            seen.add(p)
            trail.append(BACK[choice])
        elif trail:
            d = trail.pop()
            p = grid[p][d]
            move(DIRS[d])
        else:
            return links
    return links


def optimistic_path(start, goal, graph, blank):
    # 未知边先按可通，只删实测墙；初始树的真实边从未关闭，始终保留可达路径。
    previous = list(blank)
    directions = list(blank)
    previous[start] = start
    queue = [start]
    head = 0
    while head < len(queue) and previous[goal] == -1:
        p = queue[head]
        head += 1
        for side in range(4):
            q = graph[p][side]
            if q != -1 and previous[q] == -1:
                previous[q] = p
                directions[q] = side
                queue.append(q)
    if previous[goal] == -1:
        return None
    backward = []
    p = goal
    while p != start:
        backward.append(directions[p])
        p = previous[p]
    path = []
    for i in range(len(backward) - 1, -1, -1):
        path.append(backward[i])
    return path





# ---------- 5. 每台机的生命周期与全场部署屏障 ----------

def worker(job, start_stock):
	n, cx, cy = job
	generations = 0
	boxes = 0
	go_empty(cx, cy)
	grid = geometry(n)
	blank = []
	for _ in range(n * n):
		blank.append(-1)
	half = n // 2
	home = half * n + half
	bx = cx - half
	by = cy - half

	# 正常初始化：中心若尚无自动生长的草，就主动种一株作为登记载体。
	if get_entity_type() == None:
		plant(Entities.Grass)
	# 16个领队各用两次WS：感染再恢复。全场合计消耗32，构成到位计数。
	for _ in range(2):
		use_item(Items.Weird_Substance, 1)
	while num_items(Items.Weird_Substance) > start_stock - 2 * DRONES:
		change_hat(Hats.Straw_Hat)

	while num_items(Items.Gold) < TARGET_GOLD and get_time() < run_until:
		go_home(cx, cy)
		# 普通场地清理：有草才收，没有植物就直接种灌木。
		if get_entity_type() != None:
			harvest()
		plant(Entities.Bush)
		use_item(Items.Weird_Substance, n * MULT)
		mapped = home
		generations += 1
		if mapped == None:
			# explore只有一种None含义：其它机已经达到黄金目标，正常取消。
			break
		found = solve_one(n, bx, by, grid, mapped, blank)
		if found == None:
			quick_print("maze_team_failed", cx, cy)
			return (n, generations, boxes)
		boxes += found
		# 完整收掉本宫后才进入下一代；下次go_home仍然回同一个固定中心。
	return (n, generations, boxes)


def deploy(jobs, start_stock):
	# 二叉分发：每个参与分发的无人机最终也负责一个任务。
	# 16个领队需要15次spawn，每代另生成16个搭档。
	handles = []
	while len(jobs) > 1:
		middle = len(jobs) // 2
		left = []
		right = []
		for i in range(middle):
			left.append(jobs[i])
		for i in range(middle, len(jobs)):
			right.append(jobs[i])
		h = spawn_drone(deploy, right, start_stock)  # ty: ignore[invalid-argument-type]  游戏支持转交args，类型桩仅声明无参Callable。
		handles.append(h)
		jobs = left
	records = [worker(jobs[0], start_stock)]
	# 主机完成本宫任务后仍要等后代退出，不让旧无人机残留到下一次运行。
	for h in handles:
		batch = wait_for(h)
		for rec in batch:  # ty: ignore[not-iterable]  本句柄对应deploy，返回记录列表。
			records.append(rec)
	return records



if __name__ == "__main__":
	lb_maze()
