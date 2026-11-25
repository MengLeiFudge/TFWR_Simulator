from __builtins__ import *
# 完整轮时间：未取得（当前算法仅完成本地7200秒完整随机模拟验证）。
# 8x8 单机在线边探边收 + in_d/sensed分离 + 增量D表 + 收益门限低频沿途探墙，300次正常迁移+1次收割。

TARGET_GOLD = 616448
REUSE_LIMIT = 300
DIRS = [North, East, South, West]
BACK = [2, 3, 0, 1]
MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)


def lb_maze_single():
	n = get_world_size()
	cost = n * MULT
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, cost)
	solve_fast(n, cost)


def add_edge_dist(D, in_d_list, a, b):
	da = D[a]
	db = D[b]
	if da[b] <= 1:
		return
	left = []
	right = []
	for u, du in in_d_list:
		x = da[u]
		y = db[u]
		if x + 1 < y:
			left.append((u, x + 1, du))
		elif y + 1 < x:
			right.append((u, y, du))
	if len(left) > len(right):
		left, right = right, left
	for u, x, du in left:
		for v, y, dv in right:
			c = x + y
			if c < du[v]:
				du[v] = c
				dv[u] = c


def add_node_to_D(D, in_d, in_d_list, node, parent):
	in_d[node] = True
	dnode = D[node]
	dnode[node] = 0
	if parent != -1:
		dpar = D[parent]
		for u, du in in_d_list:
			d = dpar[u] + 1
			du[node] = d
			dnode[u] = d
	in_d_list.append((node, dnode))


def remove_wall_pair(walls, p, q):
	rem_p = []
	for item in walls[p]:
		if item[0] != q:
			rem_p.append(item)
	walls[p] = rem_p
	rem_q = []
	for item in walls[q]:
		if item[0] != p:
			rem_q.append(item)
	walls[q] = rem_q


def scan_cell_walls(p, reloc, walls, linked, adj, in_d, in_d_list, sensed, frontier, in_frontier, D, next_scan, scan_gap, prof_thresh):
	wp = walls[p]
	next_scan[p] = reloc + scan_gap
	opened = []
	for item in wp:
		if can_move(item[2]):
			opened.append(item)
	if not opened:
		return False
	lnkp = linked[p]
	updated = False
	rem_boxes = REUSE_LIMIT - reloc
	for q, d, dr, bdr in opened:
		b = BACK[d]
		lnkp[d] = True
		linked[q][b] = True
		adj[p].append((q, dr))
		adj[q].append((p, bdr))
		remove_wall_pair(walls, p, q)
		if not walls[q]:
			next_scan[q] = 999
		if not in_d[q]:
			add_node_to_D(D, in_d, in_d_list, q, p)
			updated = True
		else:
			if rem_boxes * (D[p][q] - 1) >= prof_thresh:
				add_edge_dist(D, in_d_list, p, q)
				updated = True
		if not sensed[q] and not in_frontier[q]:
			frontier.append(q)
			in_frontier[q] = True
	if not walls[p]:
		next_scan[p] = 999
	return updated


def solve_fast(n, cost):
	count = n * n
	grid = []
	cx = []
	cy = []
	blank_d = []
	adj = []
	walls = []
	linked = []
	in_d = []
	sensed = []
	next_scan = []
	in_frontier = []
	for y in range(n):
		for x in range(n):
			u = y * n + x
			cx.append(x)
			cy.append(y)
			row = [-1, -1, -1, -1]
			if y < n - 1:
				row[0] = u + n
			if x < n - 1:
				row[1] = u + 1
			if y > 0:
				row[2] = u - n
			if x > 0:
				row[3] = u - 1
			grid.append(row)
			blank_d.append(999)
			adj.append([])
			walls.append([])
			linked.append([False, False, False, False])
			in_d.append(False)
			sensed.append(False)
			next_scan.append(999)
			in_frontier.append(False)

	D = []
	for _ in range(count):
		D.append(list(blank_d))

	in_d_list = []
	frontier = []
	scan_gap = 6
	prof_thresh = 150
	path_scan_mod = 2
	stop_scan = 255
	sensed_cnt = [0]

	def sense_cell(u, reloc):
		sensed[u] = True
		sensed_cnt[0] += 1
		in_frontier[u] = False
		rowp = grid[u]
		lnkp = linked[u]
		adjp = adj[u]
		wp = walls[u]
		extra = []
		for d in range(4):
			q = rowp[d]
			if q == -1 or lnkp[d]:
				continue
			dr = DIRS[d]
			b = BACK[d]
			bdr = DIRS[b]
			if can_move(dr):
				lnkp[d] = True
				linked[q][b] = True
				adjp.append((q, dr))
				adj[q].append((u, bdr))
				if not in_d[q]:
					add_node_to_D(D, in_d, in_d_list, q, u)
				else:
					extra.append(q)
				if not sensed[q] and not in_frontier[q]:
					frontier.append(q)
					in_frontier[q] = True
			else:
				if not sensed[q]:
					wp.append((q, d, dr, bdr))
					walls[q].append((u, b, bdr, dr))
		if wp:
			ns = reloc + scan_gap
			if ns < 10:
				ns = 10
			next_scan[u] = ns
		for q in extra:
			add_edge_dist(D, in_d_list, u, q)

	p = 0
	add_node_to_D(D, in_d, in_d_list, 0, -1)
	sense_cell(0, 0)

	for relocations in range(REUSE_LIMIT + 1):
		t = measure()
		gx = t[0]
		gy = t[1]
		goal = gy * n + gx

		if sensed_cnt[0] == count:
			if p != goal:
				if relocations < stop_scan and relocations >= next_scan[p]:
					scan_cell_walls(p, relocations, walls, linked, adj, in_d, in_d_list, sensed, frontier, in_frontier, D, next_scan, scan_gap, prof_thresh)
				dg = D[goal]
				cur_d = dg[p]
				if relocations < stop_scan and relocations % path_scan_mod == 0:
					while cur_d > 1:
						for q, dr in adj[p]:
							if dg[q] < cur_d:
								move(dr)
								p = q
								cur_d -= 1
								break
						if relocations >= next_scan[p]:
							if scan_cell_walls(p, relocations, walls, linked, adj, in_d, in_d_list, sensed, frontier, in_frontier, D, next_scan, scan_gap, prof_thresh):
								cur_d = dg[p]
					if cur_d == 1:
						for q, dr in adj[p]:
							if q == goal:
								move(dr)
								p = q
								break
				else:
					for cur_d in range(cur_d, 0, -1):
						for q, dr in adj[p]:
							if dg[q] < cur_d:
								move(dr)
								p = q
								break
		else:
			while p != goal:
				if in_d[goal]:
					if not sensed[p]:
						sense_cell(p, relocations)
					elif relocations < stop_scan and relocations >= next_scan[p]:
						scan_cell_walls(p, relocations, walls, linked, adj, in_d, in_d_list, sensed, frontier, in_frontier, D, next_scan, scan_gap, prof_thresh)
					dg = D[goal]
					cur_d = dg[p]
					if relocations < stop_scan and relocations > 8 and relocations % path_scan_mod == 0:
						while cur_d > 1:
							for q, dr in adj[p]:
								if dg[q] < cur_d:
									move(dr)
									p = q
									cur_d -= 1
									break
							if not sensed[p]:
								sense_cell(p, relocations)
								cur_d = dg[p]
							elif relocations >= next_scan[p]:
								if scan_cell_walls(p, relocations, walls, linked, adj, in_d, in_d_list, sensed, frontier, in_frontier, D, next_scan, scan_gap, prof_thresh):
									cur_d = dg[p]
						if cur_d == 1:
							for q, dr in adj[p]:
								if q == goal:
									move(dr)
									p = q
									break
						if not sensed[p]:
							sense_cell(p, relocations)
					else:
						for cur_d in range(cur_d, 0, -1):
							for q, dr in adj[p]:
								if dg[q] < cur_d:
									move(dr)
									p = q
									break
							if not sensed[p]:
								sense_cell(p, relocations)
								if dg[p] < cur_d - 1:
									break
				else:
					dp = D[p]
					best_f = -1
					best_score = 99999
					new_frontier = []
					for f in frontier:
						if not sensed[f]:
							new_frontier.append(f)
							dx = cx[f] - gx
							if dx < 0:
								dx = -dx
							dy = cy[f] - gy
							if dy < 0:
								dy = -dy
							sc = dp[f] + dx + dy
							if sc < best_score:
								best_score = sc
								best_f = f
					frontier = new_frontier

					df = D[best_f]
					for cur_d in range(df[p], 0, -1):
						for q, dr in adj[p]:
							if df[q] < cur_d:
								move(dr)
								p = q
								break
						if not sensed[p]:
							sense_cell(p, relocations)
							if in_d[goal]:
								break

			if not sensed[p]:
				sense_cell(p, relocations)

		if relocations < REUSE_LIMIT:
			use_item(Items.Weird_Substance, cost)
		else:
			harvest()


if __name__ == "__main__":
	lb_maze_single()
