from __builtins__ import *


def move_to(pos):
    x, y = pos
    size = get_world_size()
    dx = x - get_pos_x()
    if abs(dx) > size // 2:
        if dx > 0:
            for _ in range(size - dx):
                move(West)
        else:
            for _ in range(size + dx):
                move(East)
    else:
        if dx < 0:
            for _ in range(-dx):
                move(West)
        elif dx > 0:
            for _ in range(dx):
                move(East)
    dy = y - get_pos_y()
    if abs(dy) > size // 2:
        if dy > 0:
            for _ in range(size - dy):
                move(South)
        else:
            for _ in range(size + dy):
                move(North)
    else:
        if dy < 0:
            for _ in range(-dy):
                move(South)
        elif dy > 0:
            for _ in range(dy):
                move(North)


set_world_size(6)
size = get_world_size()
def main():
    while True:
        power = []
        for _ in range(16):
            power.append([])
        for i in range(size):
            for j in range(size):
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Sunflower)
                power[measure()].append((i, j))
                if get_water() < num_items(Items.Water) / 100:
                    use_item(Items.Water)
                move(North)
            move(East)
        t = size * size
        for sunflowers in range(15, 6, -1):
            for pos in power[sunflowers]:
                move_to(pos)
                while not can_harvest():
                    if get_water() < num_items(Items.Water) / 100:
                        use_item(Items.Water)
                harvest()
                if num_items(Items.Power) >= 10000:
                    return
                t -= 1
                if t < 10:
                    break
main()