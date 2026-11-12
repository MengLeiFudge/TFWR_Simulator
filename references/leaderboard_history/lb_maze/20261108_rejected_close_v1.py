from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/nonreset-100-20261108/maze-close-v1/lb_maze.py
# 算法来源：zzlg-git/TheFarmerWasReplaced_Maze_1min28s，commit e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629。
# 保留32座小迷宫、出发点探墙与增量路由；初始表改为对称构建，许可信息见同名文档。

WORLD = 32
TARGET_GOLD = 9863168
DRONES = 32
REUSE_LIMIT = 300

# 方向编号：0北、1东、2南、3西；BACK给出反向编号。
DIRS = [North, East, South, West]
BACK = [2, 3, 0, 1]
MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)


# ---------- 1. 开放地面移动与固定排布 ----------

def lb_maze():
    if num_items(Items.Gold) >= TARGET_GOLD:
        return
    jobs = make_jobs()
    stock = num_items(Items.Weird_Substance)
    set_world_size(WORLD)
    clear()
    set_execution_speed(0)
    records = deploy(jobs, stock)
    quick_print("maze_done", get_time(), num_items(Items.Gold), len(records))


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
	# 记录格式：(边长, 固定生成中心x, 固定生成中心y)。
	# 20座5x5 + 6座6x6 + 6座7x7。覆盖1010格；不一定是全局最优布局。
	jobs = []
	for y in range(2):
		for x in range(5):
			jobs.append((5, 2 + 5 * x, 2 + 5 * y))
			jobs.append((5, 9 + 5 * x, 24 + 5 * y))
	for y in range(2):
		for x in range(3):
			jobs.append((6, 10 + 6 * x, 13 + 6 * y))
	for y in range(3):
		jobs.append((7, 3, 14 + 7 * y))
		jobs.append((7, 28, 4 + 7 * y))
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
	p, links, walls, tree = mapped
	cost = n * MULT
	routes = build_all_routes(tree, blank)
	relocations = 0
	while num_items(Items.Gold) < TARGET_GOLD:
		# 一机一宫；measure一定返回本宫当前宝箱坐标。
		t = measure()
		goal = (t[1] - by) * n + t[0] - bx  # ty: ignore[not-subscriptable]  本机始终处于独占迷宫，measure返回坐标。
		if p != goal:
			# 第一次搬箱前还没有开新墙，不重复扫描刚建图时测过的墙。
			if relocations > 0 and len(walls[p]) > 0:
				scan_departure(p, links, walls, grid, routes)
			dist, hop = routes[goal]
			# 沿已确认的路线移动；不查实体、不重复核对坐标、不检查move返回值。
			for _ in range(dist[p]):
				p, direction = hop[p]
				move(direction)

		# 正常终止条件：行走期间其它宫可能已达到目标，不再多收/多搬一箱。
		if num_items(Items.Gold) >= TARGET_GOLD:
			return relocations
		if relocations >= REUSE_LIMIT:
			# 300次成功搬迁之后，走到最后一个箱子并harvest，本宫才会消失。
			harvest()
			return relocations + 1
		use_item(Items.Weird_Substance, cost)
		relocations += 1
	return relocations


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
	# 32台各用两次WS：感染再恢复。全场合计消耗64，构成到位计数。
	for _ in range(2):
		use_item(Items.Weird_Substance, 1)
	while num_items(Items.Weird_Substance) > start_stock - 2 * DRONES:
		change_hat(Hats.Straw_Hat)

	while num_items(Items.Gold) < TARGET_GOLD:
		go_home(cx, cy)
		# 普通场地清理：有草才收，没有植物就直接种灌木。
		if get_entity_type() != None:
			harvest()
		plant(Entities.Bush)
		use_item(Items.Weird_Substance, n * MULT)
		mapped = explore(n, grid, home)
		generations += 1
		if mapped == None:
			# explore只有一种None含义：其它机已经达到黄金目标，正常取消。
			break
		boxes += solve_one(n, bx, by, grid, mapped, blank)
		# 完整收掉本宫后才进入下一代；下次go_home仍然回同一个固定中心。
	return (n, generations, boxes)


def deploy(jobs, start_stock):
	# 二叉分发：每个参与分发的无人机最终也负责一个任务。
	# 32个任务恰好需要31次spawn。
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
