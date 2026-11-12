# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/github-cactus-search2/RubenNijhuis/cactus.py
import movement
import utils
import crops
import multi


def is_line_sorted(start_pos, length, forward_dir):
	# Quick O(n) check if already sorted
	movement.go_to(start_pos)
	for _ in range(length - 1):
		if measure() > measure(forward_dir):
			return False
		move(forward_dir)
	return True


def sort_line(start_pos, length, forward_dir, backward_dir, is_row):
	# Skip if already sorted
	if is_line_sorted(start_pos, length, forward_dir):
		return

	# Bidirectional bubble sort
	start_x, start_y = start_pos
	start_idx = 0
	end_idx = length - 1

	while start_idx < end_idx:
		last_forward_swap = start_idx
		last_backward_swap = end_idx

		# Forward pass
		if is_row:
			movement.go_to((start_x + start_idx, start_y))
		else:
			movement.go_to((start_x, start_y + start_idx))

		i = start_idx
		while i < end_idx:
			if measure() > measure(forward_dir):
				swap(forward_dir)
				last_forward_swap = i
			move(forward_dir)
			i = i + 1

		end_idx = last_forward_swap

		if start_idx >= end_idx:
			break

		# Backward pass
		if is_row:
			movement.go_to((start_x + end_idx, start_y))
		else:
			movement.go_to((start_x, start_y + end_idx))

		i = end_idx
		while i > start_idx:
			if measure() < measure(backward_dir):
				swap(backward_dir)
				last_backward_swap = i
			move(backward_dir)
			i = i - 1

		start_idx = last_backward_swap


def sort_rows_in_area(area):
	pos, size = area
	width, height = size

	for row in range(height):
		row_start = (pos[0], pos[1] + row)
		sort_line(row_start, width, East, West, True)


def sort_columns_in_area(area):
	pos, size = area
	width, height = size

	for col in range(width):
		col_start = (pos[0] + col, pos[1])
		sort_line(col_start, height, North, South, False)


def sort_field(area):
	opts_rows = {"direction": "vertical"}
	opts_cols = {"direction": "horizontal"}

	multi.run_func(area, sort_rows_in_area, {"slices": utils.create_slices(area, opts_rows)})
	multi.run_func(area, sort_columns_in_area, {"slices": utils.create_slices(area, opts_cols)})


def plant_full(area):
	utils.map_over_area(area, crops.farm_crop_at(Entities.Cactus))


# Plants cacti and sorts them (no harvest)
def plant_field(area):
	multi.run_func(area, plant_full)
	sort_field(area)


# Full cycle: plant, sort, then harvest the sorted chain
def farm_field(area):
	pos = area[0]
	plant_field(area)
	movement.go_to(pos)
	harvest()


# Farm cactus until we have at least 'amount'
# Cactus already uses parallel drones internally for sorting
# so we just loop farm_field (no Megafarm check needed)
def farm(area, amount):
	def has_enough():
		return num_items(Items.Cactus) >= amount

	if has_enough():
		return

	while not has_enough():
		farm_field(area)
