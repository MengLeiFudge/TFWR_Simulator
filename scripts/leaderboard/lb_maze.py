from __builtins__ import *
# 完整轮时间：未取得（当前算法仅完成本地7200秒完整随机模拟验证）。
# 32x32 合法流水线重建 + d<=1 狙击：9种植+9生成+9错失收割+5纯狙击（四角+内点），无重复收箱。

WORLD = 32
TARGET_GOLD = 9863168
DRONES = 32
P = 9
H = 9
F = 5
M = P + H + F
DIRS = [North, East, South, West]
BACK = [2, 3, 0, 1]
MULT = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
COST = WORLD * MULT


def lb_maze():
	if num_items(Items.Gold) >= TARGET_GOLD:
		return
	start_ws = num_items(Items.Weird_Substance)
	cells = make_cells()

	hit_set = set()
	hit_set.add(None)
	for ci in range(M):
		hit_set.add(cells[ci])

	dx_list = [0, 1, 0, -1]
	dy_list = [1, 0, -1, 0]
	for ci in range(P + H, M):
		cx, cy = cells[ci]
		for d in range(4):
			nx = cx + dx_list[d]
			ny = cy + dy_list[d]
			if nx >= 0 and nx < WORLD and ny >= 0 and ny < WORLD:
				hit_set.add((nx, ny))

	deploy(0, DRONES, cells, hit_set, start_ws, True)


def make_cells():
	# 9种植/生成配对格（d=0，含4个sym(1,1)高概率格）+ 9错失收割格（d=0）+ 5纯狙击格（四角+内点，d<=1）
	# 所有坐标距(0,0)环绕距离<=11，压缩开局布阵耗时
	return [
		(1, 1), (30, 1), (1, 30), (30, 30),
		(6, 3), (25, 3), (6, 28), (25, 28),
		(3, 7),
		(28, 7), (3, 24), (28, 24),
		(9, 4), (22, 4), (9, 27), (22, 27),
		(4, 11), (27, 11),
		(0, 0), (31, 0), (0, 31), (31, 31),
		(4, 4),
	]


def go_empty(tx, ty):
	dx = (tx - get_pos_x()) % WORLD
	if dx <= 16:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(WORLD - dx):
			move(West)
	dy = (ty - get_pos_y()) % WORLD
	if dy <= 16:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(WORLD - dy):
			move(South)


def deploy(lo, hi, cells, hit_set, start_ws, root=False):
	handles = []
	while hi - lo > 1:
		mid = (lo + hi) // 2
		handles.append(spawn_drone(deploy, mid, hi, cells, hit_set, start_ws))
		hi = mid
	run_drone(lo, cells, hit_set, start_ws)
	if root and num_items(Items.Gold) >= TARGET_GOLD:
		clear()
		return
	for h in handles:
		wait_for(h)


def return_home(back_dir):
	tries = 0
	while not move(back_dir):
		if num_items(Items.Gold) >= TARGET_GOLD:
			return
		tries += 1
		if tries >= 20:
			harvest()
			tries = 0


def run_drone(my_id, cells, hit_set, start_ws):
	if my_id < P:
		role = 0
		idx = my_id
		cx, cy = cells[idx]
	elif my_id < 2 * P:
		role = 1
		idx = my_id - P
		cx, cy = cells[idx]
	elif my_id < 2 * P + H:
		role = 2
		idx = my_id - 2 * P
		cx, cy = cells[P + idx]
	else:
		role = 3
		idx = my_id - 2 * P - H
		cx, cy = cells[P + H + idx]

	go_empty(cx, cy)

	if get_entity_type() == None:
		plant(Entities.Grass)
	use_item(Items.Weird_Substance, 1)
	base_ws = start_ws - DRONES
	while num_items(Items.Weird_Substance) > base_ws:
		for _ in range(4):
			pass

	if role == 0:
		# 种植机 idx (0..P-1)
		step_ws = P * COST
		target_ws = base_ws - idx * COST
		if idx == 0:
			plant(Entities.Bush)
			target_ws -= step_ws

		while num_items(Items.Gold) < TARGET_GOLD:
			near_ws = target_ws + COST
			while num_items(Items.Weird_Substance) > near_ws:
				if get_entity_type() == Entities.Treasure:
					harvest()
					if num_items(Items.Gold) >= TARGET_GOLD:
						return
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
				for _ in range(4):
					pass
			while num_items(Items.Weird_Substance) > target_ws:
				if get_entity_type() == Entities.Treasure:
					harvest()
					if num_items(Items.Gold) >= TARGET_GOLD:
						return
				if num_items(Items.Weird_Substance) <= target_ws:
					break
				if num_items(Items.Weird_Substance) <= target_ws:
					break
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			if get_entity_type() == Entities.Treasure:
				harvest()
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			while not plant(Entities.Bush):
				if plant(Entities.Bush):
					break
				if plant(Entities.Bush):
					break
				if plant(Entities.Bush):
					break
				if plant(Entities.Bush):
					break
				if plant(Entities.Bush):
					break
				if plant(Entities.Bush):
					break
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			target_ws -= step_ws

	elif role == 1:
		# 生成机 idx (0..P-1)
		while num_items(Items.Gold) < TARGET_GOLD:
			while get_entity_type() != Entities.Bush:
				if get_entity_type() == Entities.Bush:
					break
				if get_entity_type() == Entities.Bush:
					break
				if get_entity_type() == Entities.Bush:
					break
				if get_entity_type() == Entities.Bush:
					break
				if get_entity_type() == Entities.Bush:
					break
				if get_entity_type() == Entities.Bush:
					break
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			use_item(Items.Weird_Substance, COST)

	elif role == 2:
		# 错失收割机 idx (0..H-1)
		my_pos = (cx, cy)
		my_hit = set(hit_set)
		my_hit.remove(my_pos)

		miss_step = H * COST
		next_miss_ws = base_ws - (idx + 1) * COST

		while num_items(Items.Gold) < TARGET_GOLD:
			near_ws = next_miss_ws + COST
			while num_items(Items.Weird_Substance) > near_ws:
				if get_entity_type() == Entities.Treasure:
					harvest()
					if num_items(Items.Gold) >= TARGET_GOLD:
						return
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
				for _ in range(4):
					pass
			if get_entity_type() == Entities.Treasure:
				harvest()
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			while num_items(Items.Weird_Substance) > next_miss_ws:
				if num_items(Items.Weird_Substance) <= next_miss_ws:
					break
				if num_items(Items.Weird_Substance) <= next_miss_ws:
					break
				if num_items(Items.Weird_Substance) <= next_miss_ws:
					break
				if num_items(Items.Weird_Substance) <= next_miss_ws:
					break
				if num_items(Items.Weird_Substance) <= next_miss_ws:
					break
				if get_entity_type() == Entities.Treasure:
					harvest()
				if num_items(Items.Gold) >= TARGET_GOLD:
					return
			if measure() not in my_hit:
				harvest()
			next_miss_ws -= miss_step

	else:
		# 纯狙击机 idx (0..F-1)：覆盖 d=0 与开放 d=1
		my_d1 = {}
		dx_list = [0, 1, 0, -1]
		dy_list = [1, 0, -1, 0]
		for d in range(4):
			nx = cx + dx_list[d]
			ny = cy + dy_list[d]
			if nx >= 0 and nx < WORLD and ny >= 0 and ny < WORLD:
				my_d1[(nx, ny)] = d

		last_ws = base_ws
		while num_items(Items.Gold) < TARGET_GOLD:
			cur_ws = num_items(Items.Weird_Substance)
			if cur_ws < last_ws:
				last_ws = cur_ws
				if get_entity_type() == Entities.Treasure:
					harvest()
					continue
				t = measure()
				if t in my_d1:
					d = my_d1[t]
					if can_move(DIRS[d]):
						move(DIRS[d])
						harvest()
						return_home(DIRS[BACK[d]])
					else:
						harvest()
			else:
				if get_entity_type() == Entities.Treasure:
					harvest()
				else:
					for _ in range(3):
						pass


if __name__ == "__main__":
	lb_maze()
