# 淘汰候选归档：lb_mushrooms | 原实验路径 .codex/nonreset-100-20261108/upstream/tmosest/2851f18c8c5a8216ef1d96842b53737602d39aba/mushrooms_efficient.py
# Did a lot of this manually...
# Matchmaker acheivement
from mega_farm import wait_for_drones
from traversal import move_to
from dig_util import *

def harvest_mushrooms_efficient_parallel():
	move_to(0, 0)
	
def loop_and_push_east():
	while True:
		for i in range(get_world_size()):
			for _ in range(get_world_size()):
				move(East)
				push(West)
				
def loop_and_push_north():
	while True:
		for i in range(get_world_size()):
			for _ in range(get_world_size()):
				move(North)
				push(South)
				
def loop_and_push_parallel():
	move_to(0, 0)
	for i in range(get_world_size() - 1):
		spawn_drone(loop_and_push_north)
		move(East)
	loop_and_push_north()

if __name__ == "__main__":
	# jump(Unlocks.Mushrooms)
	
	# dig_parallel_to_ground(Grounds.Mushroom)
	# harvest_mushrooms_efficient_parallel()
	# dig()
	# move_to(1, 2)
	# for _ in range(get_world_size()):
		# move(North)
		# push(South)
	move_to(0, 0)
	# dig()
	loop_and_push_east()
	# loop_and_push_north()
	# move(North)
	# place(Grounds.Block_Blue)
	# loop_and_push_parallel()
