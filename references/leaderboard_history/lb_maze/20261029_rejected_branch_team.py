from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-branch-team/lb_maze.py
# 私有双机并行分枝建图与树距离分区，完整时间未取得。
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
	quick_print("结束，秒:", elapsed, "黄金:", num_items(Items.Gold), "版本: 16-team-branch-tree")
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


def branch_map(p, previous, back, grid, allow_fork):
    records = []
    handles = []
    def visit(p, previous, back):
        row = [-1, -1, -1, -1]
        closed = []
        children = []
        for d in range(4):
            q = grid[p][d]
            if q == -1:
                continue
            if q == previous or can_move(DIRS[d]):
                row[d] = q
                if q != previous:
                    children.append((q, d))
            else:
                closed.append(d)
        records.append((p, previous, back, row, closed))
        # 尚未搬迁的初始迷宫是树；去掉父边后，各子枝不相交。
        for q, d in children:
            forked = False
            if allow_fork and not handles and len(children) > 1:
                handle = spawn_drone(enter_branch, q, p, d, grid)
                if handle != None:
                    handles.append(handle)
                    forked = True
            if not forked:
                move(DIRS[d])
                visit(q, p, BACK[d])
                move(DIRS[BACK[d]])
    visit(p, previous, back)
    for handle in handles:
        for record in wait_for(handle):
            records.append(record)
    return records


def enter_branch(p, previous, direction, grid):
    move(DIRS[direction])
    return branch_map(p, previous, BACK[direction], grid, False)


def explore(n, grid, home):
    started = get_time()
    records = branch_map(home, -1, -1, grid, True)
    links = []
    walls = []
    parent = []
    up_hop = []
    down_hop = []
    for _ in range(n * n):
        links.append(None)
        walls.append(None)
        parent.append(-1)
        up_hop.append(None)
        down_hop.append(None)
    order = []
    for p, previous, back, row, closed in records:
        if links[p] != None:
            quick_print("maze_branch_failed", "duplicate", p)
            return None
        links[p] = row
        walls[p] = closed
        parent[p] = previous
        if previous != -1:
            up_hop[p] = (previous, DIRS[back])
            down_hop[p] = (p, DIRS[BACK[back]])
        order.append(p)
    if len(order) != n * n:
        quick_print("maze_branch_failed", "coverage", len(order))
        return None
    quick_print("branch_map", get_pos_x(), get_pos_y(), len(order), get_time() - started)
    return home, links, walls, (parent, up_hop, down_hop, order)


def choose_stations(routes):
    # 用树直径的四分点，不枚举中心组合；所有格的归属在开墙前固定。
    a = 0
    for p in range(len(routes)):
        if routes[0][0][p] > routes[0][0][a]:
            a = p
    b = a
    for p in range(len(routes)):
        if routes[a][0][p] > routes[a][0][b]:
            b = p
    length = routes[a][0][b]
    path = [b]
    p = b
    for _ in range(length):
        p, direction = routes[a][1][p]
        path.append(p)
    stations = [path[length // 4], path[(3 * length) // 4]]
    owners = []
    for p in range(len(routes)):
        owner = 0
        if routes[stations[1]][0][p] < routes[stations[0]][0][p]:
            owner = 1
        owners.append(owner)
    return stations, owners


def solve_one(n, bx, by, grid, mapped, blank):
    p, links, walls, tree = mapped
    started = get_time()
    routes = build_all_routes(tree, blank)
    stations, owners = choose_stations(routes)
    quick_print("branch_plan", bx, by, stations, get_time() - started)
    def partner():
        return serve(n, bx, by, grid, p, links, walls, routes, 1, stations, owners)
    handle = spawn_drone(partner)
    if handle == None:
        return None
    left, local_ok = serve(n, bx, by, grid, p, links, walls, routes, 0, stations, owners)
    right, other_ok = wait_for(handle)
    if not local_ok or not other_ok:
        return None
    return left + right


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





def serve(n, bx, by, grid, p, links, walls, routes, side, stations, owners):
    # 按初始树最近驻点唯一分派；归属在开墙后保持不变。
    # 初始图由spawn复制，后续各自发现新边；旧边不会关闭。
    cost = n * MULT
    home = stations[side]
    boxes = 0
    while num_items(Items.Gold) < TARGET_GOLD:
        target = measure()
        if target == None:
            # 另一责任机收掉第301箱后，本宫消失；父机等待双方退出再重建。
            return (boxes, True)
        goal = (target[1] - by) * n + target[0] - bx
        owner = owners[goal]
        if owner == side:
            if len(walls[p]) > 0:
                scan_departure(p, links, walls, grid, routes)
            dist, hop = routes[goal]
            for _ in range(dist[p]):
                p, direction = hop[p]
                if not move(direction):
                    return (boxes, False)
            if num_items(Items.Gold) >= TARGET_GOLD:
                return (boxes, True)
            if num_items(Items.Weird_Substance) < cost:
                return (boxes, False)
            if use_item(Items.Weird_Substance, cost):
                boxes += 1
            else:
                # 唯一责任者、足额材料、足额尺寸；正常失败表示已满300次迁移。
                # 前一次use_item已支付200t，且期间有measure与分支，不在结算窗重入。
                if get_entity_type() != Entities.Treasure or not harvest():
                    return (boxes, False)
                boxes += 1
                return (boxes, True)
        elif p != home:
            # 非责任者逐步回本半区中心，每步后重新读取目标，不追同一箱子聚集。
            p, direction = routes[home][1][p]
            if not move(direction):
                return (boxes, False)
        else:
            for _ in range(32):
                pass
    return (boxes, True)


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
