from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main11；可靠基线 `5:40.868`，5-seed≈`5:37.9`，2h≈`5:39.0`。


# 旧版本，保留做对照

























MAIN11_TREE_OFF = {
    (0, 0),
    (1, 3),
    (2, 6),
    (3, 1),
    (4, 4),
    (5, 7),
    (6, 2),
    (7, 5),
}

MAIN12_TREE_OFF = {
    (0, 0),
    (0, 2),
    (0, 4),
    (0, 6),
    (1, 3),
    (2, 6),
    (3, 1),
    (5, 7),
}

MAIN13_TREES = {
    (0, 0),
    (0, 2),
    (0, 4),
    (0, 6),
    (1, 1),
    (1, 5),
    (1, 7),
    (2, 2),
    (3, 5),
    (3, 7),
    (4, 0),
    (4, 4),
    (4, 6),
    (5, 1),
    (5, 7),
    (6, 0),
    (6, 2),
    (6, 6),
    (7, 3),
    (7, 5),
}

def main11(count=500000000):
    set_world_size(8)
    init_main11_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True
    sweep_count = [0]
    harvest_count = [0]
    tree_reroll_count = [0]
    support_replant_count = [0]
    support_keep_count = [0]
    orphan_support_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    sample_harvest = [0]
    sample_reroll = [0]
    sample_replant = [0]
    sample_keep = [0]
    sample_orphan = [0]

    quick_print("main11", " init_time=", get_time(), " wood=", num_items(Items.Wood))

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
                if is_main11_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main11_tree_companion(
                        support_entity,
                        support_count,
                        tree_reroll_count,
                    )
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main11_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                        support_replant_count,
                        support_keep_count,
                        orphan_support_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        sweep_count[0] = sweep_count[0] + 1
        maybe_log_main11_probe(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            tree_reroll_count,
            support_replant_count,
            support_keep_count,
            orphan_support_count,
            sample_harvest,
            sample_reroll,
            sample_replant,
            sample_keep,
            sample_orphan,
        )
        first_cycle = False

    quick_print("main11", " done wood=", num_items(Items.Wood), " time=", get_time())





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



def is_main11_tree_slot(x, y):
    if (x, y) in MAIN11_TREE_OFF:
        return False
    return (x + y) % 2 == 0





def init_main11_support_soil():
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
            if not is_main11_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)





def release_main10_tree_claim(
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



def roll_main11_tree_companion(support_entity, support_count, tree_reroll_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main11_tree_slot(cx, cy):
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def process_main11_support_slot(
        x,
        y,
        support_entity,
        support_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count):
    entity = get_entity_type()
    if support_count[x][y] <= 0:
        if entity != None:
            orphan_support_count[0] = orphan_support_count[0] + 1
        return

    ct = support_entity[x][y]
    if entity == ct:
        support_keep_count[0] = support_keep_count[0] + 1
        return

    if entity != None:
        support_replant_count[0] = support_replant_count[0] + 1
        harvest()

    plant(ct)


def maybe_log_main11_probe(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        tree_reroll_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count,
        sample_harvest,
        sample_reroll,
        sample_replant,
        sample_keep,
        sample_orphan):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main11", " probe wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " tree_reroll=", tree_reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
        " orphan_support=", orphan_support_count[0],
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_reroll=", tree_reroll_count[0] - sample_reroll[0],
        " d_replant=", support_replant_count[0] - sample_replant[0],
        " d_keep=", support_keep_count[0] - sample_keep[0],
        " d_orphan=", orphan_support_count[0] - sample_orphan[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time
    sample_harvest[0] = harvest_count[0]
    sample_reroll[0] = tree_reroll_count[0]
    sample_replant[0] = support_replant_count[0]
    sample_keep[0] = support_keep_count[0]
    sample_orphan[0] = orphan_support_count[0]








































if __name__ == "__main__":
    main11()
