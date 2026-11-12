from __builtins__ import *
# 淘汰候选归档：lb_carrots_single | 原实验路径 .codex/leaderboard-sol/carrots-single/water-gate/lb_carrots_single.py
# 本地候选；尚无游戏打榜时间。
def lb_carrots_single():
    set_world_size(SINGLE_FIELD_SIZE)
    support_entity = create_grid(None)
    support_users = create_grid(0)
    claims = {(2, 1): None, (3, 1): None, (3, 2): None, (2, 2): None}
    if not init_anchors(support_entity, support_users, claims):
        return
    quick_print("lb_carrots_single", " init carrots=", num_items(Items.Carrot), " time=", get_time())

    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS and STATS["cycles"] < MAX_CYCLES:
        STATS["cycles"] += 1
        if not process_anchor(2, 1, support_entity, support_users, claims):
            return
        if not process_anchor(3, 1, support_entity, support_users, claims):
            return
        if not process_anchor(3, 2, support_entity, support_users, claims):
            return
        if not process_anchor(2, 2, support_entity, support_users, claims):
            return

    quick_print("lb_carrots_single", " done carrots=", num_items(Items.Carrot), " time=", get_time(), " stats=", STATS)


SINGLE_GOAL_CARROTS = 100000000
SINGLE_FIELD_SIZE = 5
MAX_CYCLES = 20000
MAX_REROLLS_PER_ANCHOR = 128
STATS = {"cycles": 0, "mature": 0, "mature_mismatch": 0, "unready": 0, "reroll": 0, "rewrite": 0, "conflict_reject": 0}
CARROT_COST = get_cost(Entities.Carrot)
CARROT_COST_ITEMS = (
    Items.Hay,
    Items.Wood,
    Items.Carrot,
    Items.Pumpkin,
    Items.Power,
    Items.Cactus,
    Items.Gold,
    Items.Bone,
    Items.Weird_Substance,
)


def goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def init_anchors(support_entity, support_users, claims):
    # 先准备全部支撑格，避免初始化覆盖已接受的伴生。
    for y in range(SINGLE_FIELD_SIZE):
        for x in range(SINGLE_FIELD_SIZE):
            if not is_anchor(x, y):
                goto(x, y)
                if get_entity_type() != Entities.Bush:
                    if get_entity_type() != None:
                        harvest()
                    plant(Entities.Bush)
                support_entity[x][y] = Entities.Bush
    for anchor in ((2, 1), (3, 1), (3, 2), (2, 2)):
        goto(anchor[0], anchor[1])
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
        plant(Entities.Carrot)
        if not roll_adaptive_companion(anchor, support_entity, support_users, claims):
            return False
    return True


def process_anchor(x, y, support_entity, support_users, claims):
    goto(x, y)
    anchor = (x, y)
    if get_entity_type() == Entities.Carrot:
        if not can_harvest():
            STATS["unready"] += 1
            water_anchor()
            return True
        companion = get_companion()
        STATS["mature"] += 1
        if companion == None or support_entity[companion[1][0]][companion[1][1]] != companion[0]:
            STATS["mature_mismatch"] += 1
        harvest()
    else:
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != None:
            harvest()
    # 待收胡萝卜结束后才释放；同类型的其他引用仍然有效。
    support = claims[anchor]
    if support != None:
        support_users[support[0]][support[1]] -= 1
        claims[anchor] = None
    plant(Entities.Carrot)
    if not roll_adaptive_companion(anchor, support_entity, support_users, claims):
        return False
    water_anchor()
    return True


def roll_adaptive_companion(anchor, support_entity, support_users, claims):
    rerolls = 0
    while num_items(Items.Carrot) < SINGLE_GOAL_CARROTS and rerolls < MAX_REROLLS_PER_ANCHOR:
        companion = get_companion()
        if companion != None:
            companion_entity = companion[0]
            cx = companion[1][0]
            cy = companion[1][1]
            if not is_anchor(cx, cy):
                known_entity = support_entity[cx][cy]
                if known_entity == companion_entity:
                    support_users[cx][cy] += 1
                    claims[anchor] = (cx, cy)
                    return True
                if support_users[cx][cy] > 0:
                    STATS["conflict_reject"] += 1
                elif companion_distance(cx, cy) <= 2:
                    if rewrite_adaptive_support(cx, cy, companion_entity, support_entity):
                        STATS["rewrite"] += 1
                        support_users[cx][cy] += 1
                        claims[anchor] = (cx, cy)
                        return True
        harvest()
        plant(Entities.Carrot)
        rerolls += 1
        STATS["reroll"] += 1
    if num_items(Items.Carrot) >= SINGLE_GOAL_CARROTS:
        return True
    quick_print("lb_carrots_single", " stopped: reroll limit", " time=", get_time(), " stats=", STATS)
    return False


def rewrite_adaptive_support(tx, ty, companion_entity, support_entity):
    ox = get_pos_x()
    oy = get_pos_y()
    goto(tx, ty)
    entity = get_entity_type()
    if entity != companion_entity:
        if entity != None:
            harvest()
        if companion_entity == Entities.Carrot:
            if get_ground_type() != Grounds.Soil:
                till()
            if get_ground_type() != Grounds.Soil or not can_pay_carrot_cost():
                goto(ox, oy)
                return False
        elif companion_entity != Entities.Grass:
            if get_ground_type() != Grounds.Grassland:
                till()
        if not plant(companion_entity):
            goto(ox, oy)
            return False
    support_entity[tx][ty] = companion_entity
    goto(ox, oy)
    return True


def companion_distance(tx, ty):
    size = get_world_size()
    x = get_pos_x()
    y = get_pos_y()
    dx = abs(tx - x)
    dy = abs(ty - y)
    return min(dx, size - dx) + min(dy, size - dy)


def can_pay_carrot_cost():
    cost = CARROT_COST
    if cost == None:
        return True
    for item in CARROT_COST_ITEMS:
        if item in cost and num_items(item) < cost[item]:
            return False
    return True


def water_anchor():
    if get_water() >= 0.9:
        return
    water = num_items(Items.Water)
    if water > 2:
        use_item(Items.Water, 3)
    elif water > 1:
        use_item(Items.Water, 2)
    elif water > 0:
        use_item(Items.Water)


def is_anchor(x, y):
    if x == 2 and y == 1:
        return True
    if x == 3 and y == 1:
        return True
    if x == 3 and y == 2:
        return True
    if x == 2 and y == 2:
        return True
    return False


def create_grid(value):
    rows = []
    for _ in range(SINGLE_FIELD_SIZE):
        row = []
        for _ in range(SINGLE_FIELD_SIZE):
            row.append(value)
        rows.append(row)
    return rows


if __name__ == "__main__":
    lb_carrots_single()
