from __builtins__ import *
# 淘汰候选归档：lb_maze_single | 原实验路径 .codex/leaderboard-astra/maze-single-path-scan/lb_maze_single_path_scan.py
# 私有候选：沿途检查新通路，尚无正式完整成绩。
# 算法来源：zzlg-git/TheFarmerWasReplaced_Maze_1min28s，commit e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629。
# 从多机的独立小迷宫算法迁入8x8单机；对称建表、出发点探墙和增量更新，许可信息见同名文档。

def lb_maze_single():
	clear()
	n = get_world_size()
	half = n // 2
	for _ in range(half):
		move(North)
		move(East)
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, n * MULT)
	grid = geometry(n)
	blank = []
	for _ in range(n * n):
		blank.append(-1)
	mapped = explore(n, grid, half * n + half)
	if mapped != None:
		solve_one(n, 0, 0, grid, mapped, blank)

TARGET_GOLD = 616448
REUSE_LIMIT = 300
DIRS = [North, East, South, West]
BACK = [2, 3, 0, 1]
MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)


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
			# 达标时提前结束；保留来源算法的统一退出条件。
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

def build_all_routes(tree, blank):
	# 每加入一个叶节点，只算它与已加入节点的无序点对，并填写双向首步。
	parent, up_hop, down_hop, order = tree
	rows = []
	for goal in range(len(blank)):
		dist = list(blank)
		hop = list(up_hop)
		dist[goal] = 0
		hop[goal] = None
		rows.append([dist, hop])
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

def scan_departure(p, links, walls, grid, routes):
	# 只在上一箱位置、下一次出发前检查原来的墙。
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
			# 新捷径可能缩短剩余路径，按当前位置结束，不冻结旧步数。
			while p != goal:
				p, direction = hop[p]
				move(direction)
				if p != goal and relocations > 0 and len(walls[p]) > 0:
					scan_departure(p, links, walls, grid, routes)

		# 达标时退出；单机完整轮正常在第301箱harvest结束。
		if num_items(Items.Gold) >= TARGET_GOLD:
			return relocations
		if relocations >= REUSE_LIMIT:
			# 300次成功搬迁之后，走到最后一个箱子并harvest，本宫才会消失。
			harvest()
			return relocations + 1
		use_item(Items.Weird_Substance, cost)
		relocations += 1
	return relocations

if __name__ == "__main__":
	lb_maze_single()
