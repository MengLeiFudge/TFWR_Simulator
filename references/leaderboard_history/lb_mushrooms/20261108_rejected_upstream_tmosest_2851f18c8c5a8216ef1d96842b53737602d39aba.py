# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/upstream/tmosest/2851f18c8c5a8216ef1d96842b53737602d39aba/mushrooms.py
# Very ineffective way of doing it.
# Clear out each alternating column and then just try to push East
from mega_farm import wait_for_drones
from traversal import move_to
from dig_util import *
		
def harvest_mushrooms_column():
	for _ in range(get_world_size()):
		
		mushroom = measure()

		move(East)
		
		next_mushroom = measure()
		
		move(West)
		
		if next_mushroom == mushroom:
			push(East)
			
		else:
			dig()
			
		move(North)
	

def dig_parallel_odd():
	drones = []
	for i in range(get_world_size()):
		if i % 2 == 1:
			drones.append(spawn_drone(dig_feild_column))
		move(East)
		
	wait_for_drones(drones)

def push_mushrooms_parallel():
	drones = []
	for i in range(get_world_size()):
		if i % 2 == 0:
			drones.append(spawn_drone(harvest_mushrooms_column))
		move(East)
		
	wait_for_drones(drones)
	
def harvest_mushrooms_parallel():
	move_to(0, 0)
	while get_ground_type() == Grounds.Mushroom:
		dig_parallel_odd()
		move_to(0, 0)
		push_mushrooms_parallel()
	
if __name__ == "__main__":
	jump(Unlocks.Mushrooms)
	dig_parallel_to_ground(Grounds.Mushroom)
	harvest_mushrooms_parallel()
