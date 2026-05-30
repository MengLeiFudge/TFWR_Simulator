from __builtins__ import *

# 10:22.851
def lb_wood():
    while True:
        if not spawn_drone(wood_worker):
            wood_worker()
            break
        move(East)
    quick_print("lb_wood done wood=", num_items(Items.Wood), " time=", get_time())


GOAL_WOOD = 10000000000


def wood_worker():
    while num_items(Items.Wood) < GOAL_WOOD:
        use_wood_water()
        if can_harvest():
            harvest()
        if (get_pos_x() + get_pos_y()) % 2 == 0:
            plant(Entities.Tree)
        else:
            plant(Entities.Bush)
        if num_items(Items.Fertilizer) > 100:
            use_item(Items.Fertilizer)
        move(North)


def use_wood_water():
    while get_water() < min(num_items(Items.Water) / 100, 0.75):
        use_item(Items.Water)


if __name__ == "__main__":
    lb_wood()
