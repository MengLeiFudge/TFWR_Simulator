from __builtins__ import *

set_world_size(4)
for y in range(4):
    for x in range(4):
        while get_pos_z() > -48:
            dig()
        move(East)
    move(North)
for y in range(4):
    for x in range(4):
        if y != 3 or x >= 2:
            dig()
        quick_print("cell", x, y, get_pos_z(), get_ground_type(), measure(), num_items(Items.Dynamite), num_items(Items.Block), get_tick_count())
        move(East)
    move(North)
quick_print("final", get_pos_z(), get_ground_type(), measure(), num_items(Items.Dynamite), get_tick_count())
quick_print("end_ns", get_time() * 1000000000)
