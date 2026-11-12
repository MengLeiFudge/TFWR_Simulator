from __builtins__ import *
# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-demand-exploration/lb_maze.py
# 私有按需探索候选，完整游戏打榜未取得。
# 算法来源：zzlg-git/TheFarmerWasReplaced_Maze_1min28s，commit e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629。
# 保留32座小迷宫与独占生命周期；未知边乐观BFS，遇墙修图后重规划。

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
	quick_print("结束，秒:", elapsed, "黄金:", num_items(Items.Gold), "版本: demand-bfs")
	quick_print("无人机结果数:", len(records), "建图代数:", generations, "宝箱总数:", total_boxes)
	for side in [5, 6, 7]:
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





# ---------- 3. 全点对路由初始化与单条新边的增量更新 ----------







# ---------- 4. 出发点探墙与单宫收割 ----------




def solve_one(n, bx, by, grid, mapped, blank):
    p = mapped
    graph = []
    walls = []
    for row in grid:
        graph.append(list(row))
        walls.append([])
    relocations = 0
    cost = n * MULT
    while num_items(Items.Gold) < TARGET_GOLD:
        target = measure()
        goal = (target[1] - by) * n + target[0] - bx
        remaining = []
        for side in walls[p]:
            if graph[p][side] != -1:
                continue
            if can_move(DIRS[side]):
                q = grid[p][side]
                graph[p][side] = q
                graph[q][BACK[side]] = p
            else:
                remaining.append(side)
        walls[p] = remaining
        while p != goal:
            path = optimistic_path(p, goal, graph, blank)
            if path == None:
                quick_print("maze_demand_failed", "no_path", p, goal)
                return relocations
            for side in path:
                q = grid[p][side]
                if not can_move(DIRS[side]):
                    graph[p][side] = -1
                    graph[q][BACK[side]] = -1
                    walls[p].append(side)
                    walls[q].append(BACK[side])
                    break
                if not move(DIRS[side]):
                    quick_print("maze_demand_failed", "move", p, side)
                    return relocations
                p = q
            if num_items(Items.Gold) >= TARGET_GOLD:
                return relocations
        if num_items(Items.Gold) >= TARGET_GOLD:
            return relocations
        if relocations >= REUSE_LIMIT:
            harvest()
            return relocations + 1
        if not use_item(Items.Weird_Substance, cost):
            quick_print("maze_demand_failed", "reuse", relocations)
            return relocations
        relocations += 1
    return relocations


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
		mapped = home
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
