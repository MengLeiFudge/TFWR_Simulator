from __builtins__ import *
SIZE = get_world_size()
HALF = SIZE // 2

# inlined water: num_items is only asked when the tile is actually dry,
# that saves one tick on every tile that does not need water
def water_tile():
    if get_water() > 0.75:
        return
    if num_items(Items.Water) >= 1:
        use_item(Items.Water)

# one tile: harvest -> dig used-up layer -> plant -> move on
def sweep():
    while True:

        # harvest if possible; this also makes the clay layer used up
        if can_harvest():
            harvest()

        # dig the used-up / covering layer away, stop on clay or rock
        n = 0
        g = get_ground_type()
        while n < 4 and g != Grounds.Clay and g != Grounds.Rock:
            dig()
            g = get_ground_type()
            n += 1

        if g == Grounds.Clay:
            plant(Entities.Rice)
            water_tile()

        elif g == Grounds.Rock:
            # dead end only if the north neighbour is rock too
            if get_ground_type(North) == Grounds.Rock:
                return

        move(North)

# go back to y = 0 by the shorter route (the map wraps at the edge)
def back_to_start():
    if get_pos_y() > HALF:
        while get_pos_y() > 0:
            move(North)
    else:
        while get_pos_y() > 0:
            move(South)

def DRice():
    d = 0
    while d < 60:
        t = get_ground_type()
        if t == Grounds.Clay:
            break
        if t == Grounds.Rock:
            break
        dig()
        d += 1

    # pass 1: plant the whole column
    sweep()

    back_to_start()

    # pass 2: harvest what has ripened
    sweep()

# ---------------- main ----------------

def rice():
    while True:
        clear()

        i = 0
        while i < SIZE - 1:
            spawn_drone(DRice)
            move(East)
            i += 1

        DRice()

        t = 0
        while num_drones() > 1 and t < 2000:
            do_a_flip()
            t += 1

if __name__ == "__main__":
    rice()
