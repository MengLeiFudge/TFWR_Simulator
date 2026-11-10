from __builtins__ import *

set_world_size(4)
for depth in range(72):
    cells = []
    for y in range(4):
        for x in range(4):
            cells.append((get_pos_z(), get_ground_type(), get_hardness(), get_stability()))
            if get_pos_z() == -depth:
                dig()
            move(East)
        move(North)
    quick_print("layer", depth, cells, num_items(Items.Iron), num_items(Items.Quartz), num_items(Items.Pumpkin), num_items(Items.Block), get_tick_count())
    if depth % 8 == 0:
        quick_print("prospect", prospect_iron(), prospect_quartz())
quick_print("end_ns", get_time() * 1000000000)
