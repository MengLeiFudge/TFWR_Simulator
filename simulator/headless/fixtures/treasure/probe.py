from __builtins__ import *

set_world_size(4)
for step in range(100):
    if get_ground_type() == Grounds.Basalt:
        break
    dig()
quick_print("basalt", get_pos_z(), get_ground_type(), measure(), get_tick_count())
x, y = measure()
while get_pos_x() != x:
    move(East)
while get_pos_y() != y:
    move(North)
for step in range(10):
    if get_ground_type() == Grounds.Treasure_Map:
        break
    dig()
path = measure()
quick_print("map", get_pos_z(), get_ground_type(), path, get_tick_count())
quick_print("same", measure() == path)
for step in path:
    if step == "D":
        dig()
    elif step == "N":
        move(North)
    elif step == "E":
        move(East)
    elif step == "S":
        move(South)
    elif step == "W":
        move(West)
    quick_print("step", step, get_pos_x(), get_pos_y(), get_pos_z(), get_ground_type(), get_entity_type(), get_tick_count())
quick_print("reward", get_entity_type(), can_harvest(), measure(), harvest(), num_items(Items.Gold), get_tick_count())
quick_print("end_ns", get_time() * 1000000000)
