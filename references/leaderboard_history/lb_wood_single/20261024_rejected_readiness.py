from __builtins__ import *
# 淘汰候选归档：lb_wood_single | 原实验路径 .codex/leaderboard-sol/wood-single/readiness-candidate/lb_wood_single.py
# 新版本完整轮时间：本地模拟/短时实机/完整官方均未取得；仅私有静态候选。
# 来源ca9e07bb。先在(2,0)准备一棵免费支撑Tree；生产成熟Tree须实际伴生就绪。


def lb_wood_single():
    count = 500000000
    set_world_size(8)
    # 准备尝试、就绪收获、成熟阻塞、树位初始草移除、支撑访问、支撑安装、plant失败、生产重抽、成熟重抽、巡回。
    stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if not bootstrap_free_tree(stats):
        return False
    init_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    installed_entity = create_entity_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True

    quick_print("lb_wood_single", " init_time=", get_time(), " wood=", num_items(Items.Wood))
    quick_print("wood_readiness", "initialized", "time=", get_time(), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood), "stats=", stats)

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
                    installed_entity[x][y] = entity
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        ct = tree_companion_entity[x][y]
                        cx = tree_companion_x[x][y]
                        cy = tree_companion_y[x][y]
                        if ct == None or ct not in (Entities.Grass, Entities.Bush, Entities.Carrot):
                            return fail_readiness("mature_missing_claim", x, y, ct)
                        if cx < 0 or cx >= 8 or cy < 0 or cy >= 8 or is_tree_slot(cx, cy):
                            return fail_readiness("mature_claim_coordinate", x, y, ct)
                        if support_count[cx][cy] <= 0 or support_entity[cx][cy] != ct:
                            return fail_readiness("mature_claim_reference", cx, cy, ct)
                        if installed_entity[cx][cy] != ct:
                            stats[2] = stats[2] + 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        if not release_tree_claim(
                                x, y, support_entity, support_count,
                                tree_companion_entity, tree_companion_x, tree_companion_y):
                            return False
                        installed_entity[x][y] = None
                        if not harvest():
                            return fail_readiness("mature_harvest_rejected", x, y, ct)
                        stats[1] = stats[1] + 1
                    elif entity != None:
                        if entity != Entities.Grass:
                            return fail_readiness("unexpected_tree_slot", x, y, entity)
                        installed_entity[x][y] = None
                        harvest()
                        stats[3] = stats[3] + 1

                    if not plant(Entities.Tree):
                        stats[6] = stats[6] + 1
                        return fail_readiness("production_tree_plant", x, y, Entities.Tree)
                    installed_entity[x][y] = Entities.Tree
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    companion = roll_tree_companion(
                        support_entity, support_count, installed_entity, x, y, stats)
                    if companion == None:
                        return False
                    ct, cx, cy = companion
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    if not process_support_slot(
                            x, y, support_entity, support_count, installed_entity, stats):
                        return False

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        first_cycle = False
        stats[9] = stats[9] + 1
        if stats[9] <= 2:
            quick_print("wood_readiness", "sweep", stats[9], "time=", get_time(), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood), "stats=", stats)

    quick_print("lb_wood_single", " done wood=", num_items(Items.Wood), " time=", get_time())
    quick_print("wood_readiness", "done", "time=", get_time(), "stats=", stats)
    return True


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
        return fail_readiness("release_missing_claim", x, y, ct)

    cx = tree_companion_x[x][y]
    cy = tree_companion_y[x][y]
    if cx < 0 or cx >= 8 or cy < 0 or cy >= 8 or is_tree_slot(cx, cy):
        return fail_readiness("release_coordinate", x, y, ct)
    if support_count[cx][cy] <= 0 or support_entity[cx][cy] != ct:
        return fail_readiness("release_reference", cx, cy, ct)
    support_count[cx][cy] = support_count[cx][cy] - 1
    if support_count[cx][cy] <= 0:
        support_count[cx][cy] = 0
        support_entity[cx][cy] = None

    tree_companion_entity[x][y] = None
    tree_companion_x[x][y] = 0
    tree_companion_y[x][y] = 0
    return True


def roll_tree_companion(support_entity, support_count, installed_entity, x, y, stats):
    while True:
        companion = get_companion()
        if companion == None:
            fail_readiness("roll_missing_companion", x, y, None)
            return None
        ct, (cx, cy) = companion
        if ct not in (Entities.Grass, Entities.Bush, Entities.Carrot):
            fail_readiness("roll_companion_type", cx, cy, ct)
            return None
        if cx < 0 or cx >= 8 or cy < 0 or cy >= 8:
            fail_readiness("roll_coordinate", cx, cy, ct)
            return None
        rejected = is_tree_slot(cx, cy)
        if not rejected:
            if support_count[cx][cy] < 0 or (support_count[cx][cy] == 0 and support_entity[cx][cy] != None):
                fail_readiness("roll_reference_state", cx, cy, ct)
                return None
            if support_count[cx][cy] > 0 and support_entity[cx][cy] == None:
                fail_readiness("roll_missing_expected", cx, cy, ct)
                return None
            rejected = support_count[cx][cy] > 0 and support_entity[cx][cy] != ct
        if rejected:
            if can_harvest():
                stats[8] = stats[8] + 1
            installed_entity[x][y] = None
            harvest()
            stats[7] = stats[7] + 1
            if not plant(Entities.Tree):
                stats[6] = stats[6] + 1
                fail_readiness("roll_tree_plant", x, y, Entities.Tree)
                return None
            installed_entity[x][y] = Entities.Tree
            continue
        return ct, cx, cy


def process_support_slot(
        x,
        y,
        support_entity,
        support_count,
        installed_entity,
        stats):
    entity = get_entity_type()
    installed_entity[x][y] = entity
    stats[4] = stats[4] + 1
    if support_count[x][y] < 0:
        return fail_readiness("support_negative_reference", x, y, support_entity[x][y])
    if support_count[x][y] == 0:
        if support_entity[x][y] != None:
            return fail_readiness("support_orphan_expected", x, y, support_entity[x][y])
        return True

    ct = support_entity[x][y]
    if ct == None or ct not in (Entities.Grass, Entities.Bush, Entities.Carrot):
        return fail_readiness("support_missing_expected", x, y, ct)
    if entity == ct:
        return True
    if entity != None and entity not in (Entities.Grass, Entities.Bush, Entities.Carrot):
        return fail_readiness("support_unexpected_entity", x, y, entity)

    installed_entity[x][y] = None
    if entity != None:
        harvest()

    if not plant(ct):
        stats[6] = stats[6] + 1
        return fail_readiness("support_plant", x, y, ct)
    installed_entity[x][y] = ct
    stats[5] = stats[5] + 1
    return True


def bootstrap_free_tree(stats):
    quick_print("wood_readiness", "bootstrap_start", "time=", get_time(), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood))
    if not goto_bootstrap(2, 0):
        return fail_readiness("bootstrap_start_move", 2, 0, Entities.Tree)
    entity = get_entity_type()
    if entity != None:
        if entity != Entities.Grass:
            return fail_readiness("bootstrap_initial_entity", 2, 0, entity)
        harvest()
    for attempt in range(128):
        planted_at = get_time()
        if not plant(Entities.Tree):
            stats[6] = stats[6] + 1
            return fail_readiness("bootstrap_tree_plant", 2, 0, Entities.Tree)
        stats[0] = stats[0] + 1
        companion = get_companion()
        if companion == None:
            return fail_readiness("bootstrap_missing_companion", 2, 0, None)
        ct, (cx, cy) = companion
        if ct not in (Entities.Grass, Entities.Bush, Entities.Carrot) or cx < 0 or cx >= 8 or cy < 0 or cy >= 8:
            return fail_readiness("bootstrap_companion_state", 2, 0, ct)
        if ct in (Entities.Grass, Entities.Bush) and not is_tree_slot(cx, cy):
            deadline = planted_at + 10
            if not goto_bootstrap(cx, cy):
                return fail_readiness("bootstrap_support_move", cx, cy, ct)
            entity = get_entity_type()
            if entity != ct:
                if entity != None:
                    if entity != Entities.Grass:
                        return fail_readiness("bootstrap_support_entity", cx, cy, entity)
                    harvest()
                if not plant(ct):
                    stats[6] = stats[6] + 1
                    return fail_readiness("bootstrap_support_plant", cx, cy, ct)
            if get_entity_type() != ct:
                return fail_readiness("bootstrap_support_not_installed", cx, cy, ct)
            if not goto_bootstrap(2, 0):
                return fail_readiness("bootstrap_return_tree", 2, 0, Entities.Tree)
            if get_entity_type() != Entities.Tree:
                return fail_readiness("bootstrap_tree_missing", 2, 0, Entities.Tree)
            while not can_harvest():
                if get_time() >= deadline:
                    return fail_readiness("bootstrap_maturity_deadline", 2, 0, Entities.Tree)
            if get_time() >= deadline:
                return fail_readiness("bootstrap_maturity_deadline", 2, 0, Entities.Tree)
            before = num_items(Items.Wood)
            if not harvest():
                return fail_readiness("bootstrap_harvest", 2, 0, Entities.Tree)
            gained = num_items(Items.Wood) - before
            if gained != 409600:
                return fail_readiness("bootstrap_wrong_yield", 2, 0, ct)
            quick_print("wood_readiness", "bootstrap_ready", "time=", get_time(), "attempts=", stats[0], "planted_at=", planted_at, "deadline=", deadline, "target=", (cx, cy), "type=", ct, "gained=", gained)
            if not goto_bootstrap(0, 0):
                return fail_readiness("bootstrap_restore_move", 0, 0, None)
            quick_print("wood_readiness", "bootstrap_restored", "time=", get_time(), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood), "power=", num_items(Items.Power), "water=", num_items(Items.Water), "fertilizer=", num_items(Items.Fertilizer))
            return True
        if attempt == 127:
            return fail_readiness("bootstrap_attempt_limit", 2, 0, ct)
        harvest()
    return fail_readiness("bootstrap_no_accepted_tree", 2, 0, None)


def goto_bootstrap(tx, ty):
    dx = (tx - get_pos_x()) % 8
    if dx <= 4:
        for _ in range(dx):
            if not move(East):
                return False
    else:
        for _ in range(8 - dx):
            if not move(West):
                return False
    dy = (ty - get_pos_y()) % 8
    if dy <= 4:
        for _ in range(dy):
            if not move(North):
                return False
    else:
        for _ in range(8 - dy):
            if not move(South):
                return False
    return True


def fail_readiness(reason, x, y, entity):
    quick_print("wood_readiness", "failed", reason, "time=", get_time(), "target=", (x, y), "type=", entity, "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood))
    return False


if __name__ == "__main__":
    lb_wood_single()
