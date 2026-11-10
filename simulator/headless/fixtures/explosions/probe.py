from __builtins__ import *

set_world_size(4)
for mode in range(4):
    quick_print("start", mode, get_pos_z(), num_items(Items.Dynamite), num_items(Items.Block), num_items(Items.Coal), num_items(Items.Iron))
    if mode == 0:
        quick_print("use", use_item(Items.Dynamite, 2))
    elif mode == 1:
        quick_print("plant", plant(Entities.Dynamite), can_harvest(), get_cost(Entities.Dynamite))
        quick_print("dig", dig())
    elif mode == 2:
        change_hat(Hats.Explosive_Drill)
        quick_print("drill", dig())
    else:
        change_hat(Hats.Straw_Hat)
        quick_print("plant2", plant(Entities.Dynamite), harvest())
    cells = []
    for y in range(4):
        for x in range(4):
            cells.append((get_pos_z(), get_ground_type(), get_hardness(), get_stability(), get_entity_type()))
            move(East)
        move(North)
    quick_print("cells", mode, cells, get_tick_count())
quick_print("items", num_items(Items.Dynamite), num_items(Items.Block), num_items(Items.Coal), num_items(Items.Iron))
quick_print("end_ns", get_time() * 1000000000)
