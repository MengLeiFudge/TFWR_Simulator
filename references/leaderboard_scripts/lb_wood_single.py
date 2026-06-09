from __builtins__ import *

# 5:36.679
def lb_wood_single():
    count = 500000000
    set_world_size(8)
    init_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True

    quick_print("lb_wood_single", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(8):
            if y % 2 == 0:
                start_x = 0
                end_x = 7
                step = 1
                move_dir = East
            else:
                start_x = 7
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_tree_companion(
                        support_entity,
                        support_count,
                    )
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        first_cycle = False

    quick_print("lb_wood_single", " done wood=", num_items(Items.Wood), " time=", get_time())


TREE_OFF = {
    (0, 0),
    (1, 3),
    (2, 6),
    (3, 1),
    (4, 4),
    (5, 7),
    (6, 2),
    (7, 5),
}


def create_entity_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        ret.append(row)
    return ret


def create_number_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(0)
        ret.append(row)
    return ret



def is_tree_slot(x, y):
    if (x, y) in TREE_OFF:
        return False
    return (x + y) % 2 == 0





def init_support_soil():
    for y in range(8):
        if y % 2 == 0:
            end_x = 7
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)





def release_tree_claim(
        x,
        y,
        support_entity,
        support_count,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y):
    ct = tree_companion_entity[x][y]
    if ct == None:
        return

    cx = tree_companion_x[x][y]
    cy = tree_companion_y[x][y]
    support_count[cx][cy] = support_count[cx][cy] - 1
    if support_count[cx][cy] <= 0:
        support_count[cx][cy] = 0
        support_entity[cx][cy] = None

    tree_companion_entity[x][y] = None
    tree_companion_x[x][y] = 0
    tree_companion_y[x][y] = 0



def roll_tree_companion(support_entity, support_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_tree_slot(cx, cy):
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def process_support_slot(
        x,
        y,
        support_entity,
        support_count):
    entity = get_entity_type()
    if support_count[x][y] <= 0:
        return

    ct = support_entity[x][y]
    if entity == ct:
        return

    if entity != None:
        harvest()

    plant(ct)








































if __name__ == "__main__":
    lb_wood_single()
