# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/github-cactus-search2/KyleGough/cactus/cactus_odd_even_sort.py
from utils import sleep, toil
from movement import goto
from distribute_column import distribute_drones

start = num_items(Items.Cactus)
required = start + 33554432

# Delays drones to synchronise sorting actions.
def delay_drone(i, drone_count):
	sleep(i * 602)

# Distribute drones more efficiently for max world size and drone count runs.
def plant_stage(drone_count, size):
	if drone_count == size:
		def plant_row():
			for _ in range(size):
				toil()
				plant(Entities.Cactus)
				move(East)
		distribute_drones(plant_row)
		# Smallest delay to allow all drones to spawn in sort stage.
		sleep(201)
	else:
		plant_cacti(drone_count, size)

# Plant cacti across multiple rows.
def plant_cacti_partition(height, size):
	for _ in range(height):
		for _ in range(size):
			toil()
			plant(Entities.Cactus)
			move(East)
		move(South)

# Distribute drones in bands to plant the grid.
def plant_cacti(drone_count, size):
	partition = size / drone_count
	for _ in range(drone_count - 1):
		spawn_drone(plant_cacti_partition, partition, size)
		for _ in range(partition):
			move(South)
	plant_cacti_partition(partition, size)

# Synchronised column sort.
def sort_column(size):
	for _ in range(size - 1):
		if measure() < measure(South):
			swap(South)
		elif get_pos_y() != size - 1 and measure(North) < measure():
			swap(North)
		else:
			set_execution_speed(-1)

# Synchronised row sort.
def sort_row(size):
	for _ in range(size - 1):
		if measure() < measure(West):
			swap(West)
		elif get_pos_x() != size - 1 and measure(East) < measure():
			swap(East)
		else:
			set_execution_speed(-1)

# Sort columns from left to right.
def sort_all_columns(i, drone_count, partition, size):
	delay_drone(i, drone_count)
	for _ in range(get_world_size() / partition):
		sort_column(size)
		move(East)

# Sort rows from bottom to top.
def sort_all_rows(i, drone_count, partition, size):
	delay_drone(i, drone_count)
	for _ in range(get_world_size() / partition):
		sort_row(size)
		move(North)

# Distribute drones along the column.
def column_sort(drone_count, partition, size):
	height = get_world_size() / drone_count
	for i in range(drone_count - 1):
		spawn_drone(sort_all_columns, drone_count - i, drone_count, partition, size)
		for _ in range(height):
			move(South)
	sort_all_columns(1, drone_count, partition, size)

# Distribute drones along the row.
def row_sort(drone_count, partition, size):
	height = get_world_size() / drone_count
	for i in range(drone_count - 1):
		spawn_drone(sort_all_rows, drone_count - i, drone_count, partition, size)
		for _ in range(height):
			move(East)
	sort_all_rows(1, drone_count, partition, size)

def parallel_column_sort(drone_count, size):
	goto(get_world_size() / 2, get_world_size() - 1)
	column_sort(drone_count, 2, size)

def parallel_row_sort(drone_count, size):
	goto(get_world_size() - 1, get_world_size() / 2)
	row_sort(drone_count, 2, size)

def execute(drone_count, halt):
	move(South)
	d = drone_count / 2
	size = get_world_size()

	while not halt():
		plant_stage(drone_count, size)
		pcs_drone = spawn_drone(parallel_column_sort, d, size)
		column_sort(d, 2, size)
		goto(get_world_size() - 1, 0)
		wait_for(pcs_drone)
		prs_drone = spawn_drone(parallel_row_sort, d, size)
		row_sort(d, 2, size)
		wait_for(prs_drone)
		harvest()

def leaderboard_halt():
	return num_items(Items.Cactus) >= required

if __name__ == "__main__":
	execute(32, leaderboard_halt)
