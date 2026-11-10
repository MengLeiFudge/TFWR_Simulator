from __builtins__ import *

set_world_size(4)
change_hat(Hats.Dinosaur_Hat)
quick_print("flat", measure(), get_tick_count())
for direction in [East, North, East, North, West, West, South, East]:
    quick_print("step", direction, can_move(direction), move(direction), get_pos_x(), get_pos_y(), measure(), get_tick_count())
change_hat(Hats.Straw_Hat)
clear()
dig()
move(East)
change_hat(Hats.Dinosaur_Hat)
quick_print("edge", can_move(West), move(West), measure(), get_pos_z(), get_tick_count())
move(North)
quick_print("surface", measure(), get_tick_count())
def lower_neighbor():
    move(East)
    move(East)
    dig()
wait_for(spawn_drone(lower_neighbor))
quick_print("changed", get_entity_type(East), move(East), get_entity_type(), measure(), get_tick_count())
change_hat(Hats.Straw_Hat)
quick_print("items", num_items(Items.Bone), num_items(Items.Cactus), num_items(Items.Block))
quick_print("end_ns", get_time() * 1000000000)
