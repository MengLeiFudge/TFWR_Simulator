# 淘汰候选归档：lb_dynamite | 原实验路径 .codex/nonreset-100-20261108/upstream/tmosest/2851f18c8c5a8216ef1d96842b53737602d39aba/dynamite.py
from hats import random_hats
from mega_farm import wait_for_drones
from traversal import move_to, move_to_center
from dig_util import dig_parallel_to_ground

def generate_table():
	table = []
	for _ in range(get_world_size()):
		list = []
		for _ in range(get_world_size()):
			list.append(-1)
		table.append(list)
	
	return table
	
def count_zeros(table):
	count = 0
	
	for i in range(len(table)):
		for j in range(len(table[i])):
			if table[i][j] == 0:
				count += 1
	
	return count

# TODO use linear algebra and probabilities to pick better
def get_random(table):
	list = []
	for i in range(len(table)):
		list.append(i)
	# random * len: Doesn't return integers...
	# Use list because int() is undefined...
	x = list[random() * len(table)]
	y = list[random() * len(table)]
	return (x, y)

def get_circle_positions():
	x, y = get_pos_x(), get_pos_y()
	
	positions = []
	
	if x - 1 > -1:
		next_position = (x - 1, y)
		positions.append(next_position)
	
	if x + 1 < get_world_size():
		next_position = (x + 1, y)
		positions.append(next_position)
		
	if y - 1 > -1:
		next_position = (x, y - 1)
		positions.append(next_position)
	
	if y + 1 < get_world_size():
		next_position = (x, y + 1)
		positions.append(next_position)
		
	if x - 1 > -1 and y - 1 > -1:
		next_position = (x - 1, y - 1)
		positions.append(next_position)
	
	if x - 1 > -1 and y + 1 < get_world_size():
		next_position = (x - 1, y + 1)
		positions.append(next_position)
		
	if x + 1 < get_world_size() and y - 1 > -1:
		next_position = (x + 1, y - 1)
		positions.append(next_position)
	
	if x + 1 < get_world_size() and y + 1 < get_world_size():
		next_position = (x + 1, y + 1)
		positions.append(next_position)
			
	move_to(x, y)
	
	return positions
	
def dig_circle(table):
	positions = get_circle_positions()
	
	for position in positions:	
		move_to(position[0], position[1])
		while get_ground_type() != Grounds.Soot:
			dig()
			table[position[0]][position[1]] = measure()

def get_zero_positions_in_circle():
	positions = get_circle_positions()
	
	results = set()
	
	for position in positions:	
		move_to(position[0], position[1])
		if get_ground_type() == Grounds.Soot and measure() == 0:
			results.add(position)

	return results

# Has a top right bias...	
def mine_zeros(start):
	stack = []
	stack.append(start)
	
	visited = set()
	
	while len(stack) > 0:
		pos = stack.pop(0)
		
		if pos not in visited:
			move_to(pos[0], pos[1])
			# dig_circle()
			for position in get_zero_positions_in_circle():
				stack.append(position)
		
		visited.add(pos)
		
def mine_zero_table(table):
	while count_zeros(table) > 0:
		for i in range(len(table)):
			for j in range(len(table[i])):
				if table[i][j] == 0:
					move_to(i, j)
					dig_circle(table)
					table[i][j] = -2
					
def mine_random_table(table):
	while count_zeros(table) == 0:
		pos = get_random(table)
		move_to(pos[0], pos[1])
		if get_ground_type() != Grounds.Soot:
			dig()
			table[get_pos_x()][get_pos_y()] = measure()
			if get_ground_type() != Grounds.Soot:
				break
					
					
def dynamite():
	dig_parallel_to_ground(Grounds.Dynamite)
	
	move_to_center()
	dig()
	
	table = generate_table()
	table[get_pos_x()][get_pos_y()] = measure()
	
	while get_ground_type() == Grounds.Soot:
	
		mine_zero_table(table)
		mine_random_table(table)


if __name__ == "__main__":
	# Bug with set world size...
	# set_world_size(16)
	clear()
	jump(Unlocks.Dynamite)
	while True:
		dynamite()
		while get_ground_type() != Grounds.Dynamite:
			move_to(0, 0)
			dig()
	
	
