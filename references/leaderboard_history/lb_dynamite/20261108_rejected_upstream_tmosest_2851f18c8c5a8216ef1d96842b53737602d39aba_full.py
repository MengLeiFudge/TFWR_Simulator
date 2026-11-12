# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/upstream/tmosest/2851f18c8c5a8216ef1d96842b53737602d39aba/dynamite_full.py
from traversal import move_to, move_to_center
from dig_util import dig_parallel_to_ground

clear()
jump(Unlocks.Dynamite)
dig_parallel_to_ground(Grounds.Dynamite)
# ==========================================
# MINESWEEPER SOLVER
# The Farmer Was Replaced
# Parallel drone implementation
# ==========================================

SIZE = get_world_size()
TOTAL = SIZE * SIZE

UNKNOWN = 0
SOOT = 1
MINE = 2
SAFE = 3

WORKERS = 8
MAX_DRONES = 31
MAX_COMPONENT_SIZE = 18

dx = [-1, 0, 1, -1, 1, -1, 0, 1]
dy = [-1, -1, -1, 0, 0, 1, 1, 1]

state = []
numbers = []

for i in range(TOTAL):
	state.append(UNKNOWN)
	numbers.append(0)


# ==========================================
# GENERAL HELPERS
# ==========================================

def get_index(x, y):
	return x + y * SIZE


def inside(x, y):
	if x < 0:
		return False

	if y < 0:
		return False

	if x >= SIZE:
		return False

	if y >= SIZE:
		return False

	return True


def contains_cell(cells, cell):

	for i in range(len(cells)):
		if cells[i] == cell:
			return True

	return False


def same_cells(a, b):

	if len(a) != len(b):
		return False

	for i in range(len(a)):
		if not contains_cell(b, a[i]):
			return False

	return True


def is_subset(a, b):

	if len(a) > len(b):
		return False

	for i in range(len(a)):
		if not contains_cell(b, a[i]):
			return False

	return True


def difference_cells(a, b):

	result = []

	for i in range(len(a)):

		if not contains_cell(b, a[i]):
			result.append(a[i])

	return result


def add_constraint(cells_list, mines_list, cells, mines):

	for i in range(len(cells_list)):

		if same_cells(cells_list[i], cells):

			if mines_list[i] != mines:
				return -1

			return 0

	cells_list.append(cells)
	mines_list.append(mines)

	return 1


# ==========================================
# PARALLEL SCANNING
# ==========================================

worker_state = []
worker_numbers = []
worker_start = 0
worker_end = 0

def dig_worker(target):

	target_x = target % SIZE
	target_y = target // SIZE

	# Move to assigned tile.
	while get_pos_x() < target_x:
		move(East)

	while get_pos_x() > target_x:
		move(West)

	while get_pos_y() < target_y:
		move(North)

	while get_pos_y() > target_y:
		move(South)

	# Dig the guaranteed-safe tile.
	dig()

	# Return the discovered number.
	return [target, measure()]
	
def dig_safe_cells_parallel():

	drones = []

	# Reserve one drone for the coordinator.
	capacity = max_drones() - 1

	if capacity < 1:
		capacity = 1

	# Spawn workers for known-safe tiles.
	for cell in range(TOTAL):

		if state[cell] == SAFE:

			if len(drones) >= capacity:
				break

			drone = spawn_drone(dig_worker, cell)

			if drone != None:
				drones.append(drone)
			else:
				break

	# If spawning failed entirely, let the starter dig.
	if len(drones) == 0:

		for cell in range(TOTAL):

			if state[cell] == SAFE:

				move_to_cell(cell)
				dig()

				state[cell] = SOOT
				numbers[cell] = measure()

				return 1

		return 0

	# Collect results.
	for i in range(len(drones)):

		result = wait_for(drones[i])

		target = result[0]
		number = result[1]

		state[target] = SOOT
		numbers[target] = number

	return len(drones)


def scan_constraints_worker():

	cells_result = []
	mines_result = []

	error = 0

	for index in range(worker_start, worker_end):

		if worker_state[index] == SOOT:

			x = index % SIZE
			y = index // SIZE

			unknown = []
			known_mines = 0

			for d in range(8):

				nx = x + dx[d]
				ny = y + dy[d]

				if inside(nx, ny):

					neighbor = get_index(nx, ny)
					value = worker_state[neighbor]

					if value == UNKNOWN:
						unknown.append(neighbor)

					elif value == MINE:
						known_mines += 1

			remaining = worker_numbers[index] - known_mines

			if remaining < 0:
				error = 1

			elif remaining > len(unknown):
				error = 1

			elif len(unknown) > 0:

				cells_result.append(unknown)
				mines_result.append(remaining)

			elif remaining != 0:

				error = 1

	return [cells_result, mines_result, error]


def build_constraints_parallel():

	global worker_state
	global worker_numbers
	global worker_start
	global worker_end

	constraint_cells = []
	constraint_mines = []

	workers = WORKERS

	if workers > MAX_DRONES:
		workers = MAX_DRONES

	chunk_size = TOTAL // workers

	drones = []

	# Launch workers.
	for i in range(workers):

		worker_state = state
		worker_numbers = numbers

		worker_start = i * chunk_size

		if i == workers - 1:
			worker_end = TOTAL
		else:
			worker_end = (i + 1) * chunk_size

		drone = spawn_drone(scan_constraints_worker)

		drones.append(drone)

	# Collect results.
	for i in range(len(drones)):

		result = wait_for(drones[i])

		cells = result[0]
		mines = result[1]
		error = result[2]

		if error == 1:
			return constraint_cells, constraint_mines, -1

		for j in range(len(cells)):

			constraint_cells.append(cells[j])
			constraint_mines.append(mines[j])

	return constraint_cells, constraint_mines, 1


# ==========================================
# PARALLEL SUBSET DEDUCTION
# ==========================================

subset_worker_cells = []
subset_worker_mines = []
subset_worker_start = 0
subset_worker_end = 0


def subset_deduction_worker():

	derived_cells = []
	derived_mines = []

	safe_cells = []
	mine_cells = []

	error = 0

	count = len(subset_worker_cells)

	for i in range(subset_worker_start, subset_worker_end):

		a = subset_worker_cells[i]
		mines_a = subset_worker_mines[i]

		# Direct deductions.
		if mines_a < 0 or mines_a > len(a):

			error = 1

		elif mines_a == 0:

			for j in range(len(a)):
				if not contains_cell(safe_cells, a[j]):
					safe_cells.append(a[j])

		elif mines_a == len(a):

			for j in range(len(a)):
				if not contains_cell(mine_cells, a[j]):
					mine_cells.append(a[j])

		# Compare with all later constraints.
		for j in range(i + 1, count):

			b = subset_worker_cells[j]
			mines_b = subset_worker_mines[j]

			# A is a subset of B.
			if is_subset(a, b):

				difference = difference_cells(b, a)
				remaining = mines_b - mines_a

				if remaining < 0:
					error = 1

				elif remaining > len(difference):
					error = 1

				elif len(difference) > 0:

					derived_cells.append(difference)
					derived_mines.append(remaining)

			# B is a subset of A.
			if is_subset(b, a):

				difference = difference_cells(a, b)
				remaining = mines_a - mines_b

				if remaining < 0:
					error = 1

				elif remaining > len(difference):
					error = 1

				elif len(difference) > 0:

					derived_cells.append(difference)
					derived_mines.append(remaining)

	return [
		derived_cells,
		derived_mines,
		safe_cells,
		mine_cells,
		error
	]


def close_constraints_parallel(constraint_cells, constraint_mines):

	global subset_worker_cells
	global subset_worker_mines
	global subset_worker_start
	global subset_worker_end

	stable = False

	safe_cells = []
	mine_cells = []

	while not stable:

		count = len(constraint_cells)

		if count == 0:
			stable = True
			break

		workers = WORKERS

		if workers > count:
			workers = count

		chunk_size = count // workers

		drones = []

		# Each worker receives the same constraint snapshot.
		for i in range(workers):

			subset_worker_cells = constraint_cells
			subset_worker_mines = constraint_mines

			subset_worker_start = i * chunk_size

			if i == workers - 1:
				subset_worker_end = count
			else:
				subset_worker_end = (i + 1) * chunk_size

			drone = spawn_drone(subset_deduction_worker)

			drones.append(drone)

		new_count = 0

		safe_cells = []
		mine_cells = []

		# Collect deductions and new constraints.
		for i in range(len(drones)):

			result = wait_for(drones[i])

			derived_cells = result[0]
			derived_mines = result[1]

			worker_safe = result[2]
			worker_mines = result[3]

			error = result[4]

			if error == 1:
				return constraint_cells, constraint_mines, safe_cells, mine_cells, -1

			for j in range(len(worker_safe)):

				if not contains_cell(safe_cells, worker_safe[j]):
					safe_cells.append(worker_safe[j])

			for j in range(len(worker_mines)):

				if not contains_cell(mine_cells, worker_mines[j]):
					mine_cells.append(worker_mines[j])

			for j in range(len(derived_cells)):

				added = add_constraint(
					constraint_cells,
					constraint_mines,
					derived_cells[j],
					derived_mines[j]
				)

				if added == -1:
					return constraint_cells, constraint_mines, safe_cells, mine_cells, -1

				if added == 1:
					new_count += 1

		# Check for contradictory deductions.
		for i in range(len(safe_cells)):

			if contains_cell(mine_cells, safe_cells[i]):
				return constraint_cells, constraint_mines, safe_cells, mine_cells, -1

		if new_count == 0:
			stable = True

		# Safety limit for constraint growth.
		if len(constraint_cells) > 2000:
			return constraint_cells, constraint_mines, safe_cells, mine_cells, -1

	return constraint_cells, constraint_mines, safe_cells, mine_cells, 1


# ==========================================
# COMPONENT PROBABILITY WORKER
# ==========================================

component_worker_size = 0
component_worker_constraints = []
component_worker_mines = []


def solve_component_worker():

	size = component_worker_size

	assignment = []
	mine_frequency = []

	for i in range(size):
		assignment.append(0)
		mine_frequency.append(0)

	total_assignments = 1

	for i in range(size):
		total_assignments = total_assignments * 2

	solutions = 0
	assignment_number = 0

	while assignment_number < total_assignments:

		valid = True

		for i in range(len(component_worker_constraints)):

			mines_found = 0

			row = component_worker_constraints[i]

			for j in range(len(row)):
				mines_found += assignment[row[j]]

			if mines_found != component_worker_mines[i]:

				valid = False
				break

		if valid:

			solutions += 1

			for i in range(size):

				if assignment[i] == 1:
					mine_frequency[i] += 1

		# Increment binary assignment.
		position = 0
		carry = 1

		while position < size and carry == 1:

			if assignment[position] == 0:

				assignment[position] = 1
				carry = 0

			else:

				assignment[position] = 0
				position += 1

		assignment_number += 1

	return [mine_frequency, solutions]


# ==========================================
# CONNECTED COMPONENT PROBABILITIES
# ==========================================

def calculate_component_probabilities(constraint_cells, constraint_mines):

	global component_worker_size
	global component_worker_constraints
	global component_worker_mines

	frontier = []

	# Build unique frontier.
	for i in range(len(constraint_cells)):

		for j in range(len(constraint_cells[i])):

			cell = constraint_cells[i][j]

			if not contains_cell(frontier, cell):
				frontier.append(cell)

	frontier_count = len(frontier)

	frequencies = []
	solution_counts = []

	for i in range(frontier_count):

		frequencies.append(0)
		solution_counts.append(0)

	if frontier_count == 0:
		return frontier, frequencies, solution_counts, 1

	# Convert constraints into frontier indexes.
	constraint_vars = []

	for i in range(len(constraint_cells)):

		row = []

		for j in range(len(constraint_cells[i])):

			found = -1

			for k in range(frontier_count):

				if frontier[k] == constraint_cells[i][j]:
					found = k
					break

			row.append(found)

		constraint_vars.append(row)

	# Build connected components.
	component_labels = []

	for i in range(frontier_count):
		component_labels.append(i)

	changed = True

	while changed:

		changed = False

		for i in range(len(constraint_vars)):

			row = constraint_vars[i]

			if len(row) > 1:

				smallest = component_labels[row[0]]

				for j in range(1, len(row)):

					label = component_labels[row[j]]

					if label < smallest:
						smallest = label

				for j in range(len(row)):

					index = row[j]

					if component_labels[index] != smallest:

						component_labels[index] = smallest
						changed = True

	# Prepare independent component tasks.
	task_cells = []
	task_constraints = []
	task_mines = []

	for component in range(frontier_count):

		if component_labels[component] == component:

			component_vars = []

			for i in range(frontier_count):

				if component_labels[i] == component:
					component_vars.append(i)

			component_size = len(component_vars)

			if component_size > MAX_COMPONENT_SIZE:

				return frontier, frequencies, solution_counts, -1

			# Map frontier indexes to local component indexes.
			local_index = []

			for i in range(frontier_count):
				local_index.append(-1)

			for i in range(component_size):

				global_index = component_vars[i]
				local_index[global_index] = i

			component_constraints = []
			component_mines_list = []

			for i in range(len(constraint_vars)):

				row = constraint_vars[i]

				if len(row) > 0:

					if component_labels[row[0]] == component:

						local_row = []

						for j in range(len(row)):
							local_row.append(local_index[row[j]])

						component_constraints.append(local_row)
						component_mines_list.append(constraint_mines[i])

			task_cells.append(component_vars)
			task_constraints.append(component_constraints)
			task_mines.append(component_mines_list)

	# Execute component workers in batches.
	task_count = len(task_cells)
	task_start = 0

	while task_start < task_count:

		batch_size = task_count - task_start

		if batch_size > MAX_DRONES:
			batch_size = MAX_DRONES

		drones = []

		for i in range(batch_size):

			task = task_start + i

			component_worker_size = len(task_cells[task])
			component_worker_constraints = task_constraints[task]
			component_worker_mines = task_mines[task]

			drone = spawn_drone(solve_component_worker)

			drones.append(drone)

		# Collect results.
		for i in range(batch_size):

			task = task_start + i

			result = wait_for(drones[i])

			mine_frequency = result[0]
			solutions = result[1]

			if solutions == 0:

				return frontier, frequencies, solution_counts, 0

			for j in range(len(task_cells[task])):

				global_index = task_cells[task][j]

				frequencies[global_index] = mine_frequency[j]
				solution_counts[global_index] = solutions

		task_start += batch_size

	return frontier, frequencies, solution_counts, 1


# ==========================================
# MOVEMENT
# ==========================================

def move_to_cell(target):

	target_x = target % SIZE
	target_y = target // SIZE

	while get_pos_x() < target_x:
		move(East)

	while get_pos_x() > target_x:
		move(West)

	while get_pos_y() < target_y:
		move(North)

	while get_pos_y() > target_y:
		move(South)


# ==========================================
# STARTING TILE
# ==========================================

start = get_index(get_pos_x(), get_pos_y())

dig()

state[start] = SOOT
numbers[start] = measure()


# ==========================================
# MAIN SOLVER
# ==========================================

running = True

while running:

	# --------------------------------------
	# 1. Scan the board in parallel.
	# --------------------------------------

	constraint_cells, constraint_mines, scan_status = build_constraints_parallel()

	if scan_status != 1:

		running = False
		break

	# --------------------------------------
	# 2. Close deterministic constraints.
	# --------------------------------------

	constraint_cells, constraint_mines, safe_cells, mine_cells, deduction_status = close_constraints_parallel(
		constraint_cells,
		constraint_mines
	)

	if deduction_status != 1:

		running = False
		break

	# --------------------------------------
	# 3. Apply deductions centrally.
	# --------------------------------------

	changed = False

	for i in range(len(mine_cells)):

		cell = mine_cells[i]

		if state[cell] == UNKNOWN:

			state[cell] = MINE
			changed = True

	for i in range(len(safe_cells)):

		cell = safe_cells[i]

		if state[cell] == UNKNOWN:

			state[cell] = SAFE
			changed = True

	# --------------------------------------
	# 4. Dig all known-safe tiles in parallel.
	# --------------------------------------

	dug = dig_safe_cells_parallel()

	if dug > 0:

		continue

	if changed:

		continue

	 # --------------------------------------
	# 5. No guaranteed-safe tiles.
	#    Calculate probabilities.
	# --------------------------------------

	frontier, frequencies, solution_counts, probability_status = calculate_component_probabilities(
		constraint_cells,
		constraint_mines
	)

	if probability_status != 1:

		running = False
		break

	best = -1

	for i in range(len(frontier)):

		if solution_counts[i] > 0:

			if best == -1:

				best = i

			else:

				left = frequencies[i] * solution_counts[best]
				right = frequencies[best] * solution_counts[i]

				if left < right:
					best = i

	if best == -1:

		running = False
		break

	# --------------------------------------
	# 6. Make one probabilistic guess.
	# --------------------------------------

	target = frontier[best]

	move_to_cell(target)

	dig()

	state[target] = SOOT
	numbers[target] = measure()

# ==========================================
# SOLVER FINISHED
# ==========================================
	
