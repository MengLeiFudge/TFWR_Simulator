from __builtins__ import *
# 淘汰候选归档：lb_wood | 原实验路径 .codex/leaderboard-sol/wood/quarter-component/lb_wood.py

def lb_wood():
    clear()
    if get_world_size() != FIELD_SIZE:
        quick_print("wood_quarter failed world_size", get_time())
        return
    quick_print("wood_quarter clear_done time=", get_time(), "wood=", num_items(Items.Wood), "water=", num_items(Items.Water))
    handles = []
    all_ok = True
    for worker_id in range(WORKERS - 1):
        handle = spawn_drone(run_block, worker_id)
        if handle == None:
            quick_print("wood_quarter failed dispatch wid=", worker_id, "time=", get_time())
            all_ok = False
            break
        handles.append(handle)
    quick_print("wood_quarter dispatch_done time=", get_time(), "children=", len(handles))
    if len(handles) == WORKERS - 1:
        if not run_block(WORKERS - 1):
            all_ok = False
    for handle in handles:
        if not wait_for(handle):
            all_ok = False
    wood = num_items(Items.Wood)
    water = num_items(Items.Water)
    quick_print("wood_quarter all_done time=", get_time(), "ok=", all_ok, "wood=", wood, "water=", water)


FIELD_SIZE = 32
WORKERS = 32
TARGET_PER_WORKER = 64
PLANT_LIMIT = 128
VISIT_LIMIT = 512
GAME_LIMIT = 60
WATER_THRESHOLD = 0.75
WATER_RESERVE = 64
BLOCK_EDGES = (East, North, North, North, West, South, South, South)


def run_block(worker_id):
    base_x = (worker_id % 8) * 4
    base_y = (worker_id // 8) * 8
    goto_moves = goto(base_x, base_y)
    if goto_moves < 0:
        return False
    arrived = get_time()
    quick_print("wood_quarter arrived wid=", worker_id, "time=", arrived, "moves=", goto_moves)
    seeded = [False, False, False, False, False, False, False, False]
    index = 0
    harvested = 0
    unready = 0
    initial_accepts = 0
    initial_attempts = 0
    initial_rejects = 0
    replant_accepts = 0
    replant_attempts = 0
    replant_rejects = 0
    water_calls = 0
    low_water_visits = 0
    for visit in range(VISIT_LIMIT):
        visits = visit + 1
        if get_time() >= GAME_LIMIT:
            quick_print("wood_quarter failed game_limit wid=", worker_id, "time=", get_time())
            return False
        if not seeded[index]:
            ok, attempts, rejects = plant_matching_tree(worker_id)
            initial_attempts += attempts
            initial_rejects += rejects
            if not ok:
                return False
            initial_accepts += 1
            seeded[index] = True
        used, skipped = water_anchor()
        water_calls += used
        low_water_visits += skipped
        if can_harvest():
            harvest()
            harvested += 1
            if harvested == 32:
                record_point(worker_id, harvested, arrived, visits, unready, initial_accepts, initial_attempts, initial_rejects, replant_accepts, replant_attempts, replant_rejects, water_calls, low_water_visits, goto_moves)
            elif harvested == TARGET_PER_WORKER:
                record_point(worker_id, harvested, arrived, visits, unready, initial_accepts, initial_attempts, initial_rejects, replant_accepts, replant_attempts, replant_rejects, water_calls, low_water_visits, goto_moves)
                return True
            ok, attempts, rejects = plant_matching_tree(worker_id)
            replant_attempts += attempts
            replant_rejects += rejects
            if not ok:
                return False
            replant_accepts += 1
        else:
            unready += 1
        direction = BLOCK_EDGES[index]
        if not move_once(direction):
            return False
        if not move_once(direction):
            return False
        index = (index + 1) % 8
    quick_print("wood_quarter failed visit_limit wid=", worker_id, "time=", get_time(), "harvested=", harvested)
    return False


def plant_matching_tree(worker_id):
    attempts = 0
    rejects = 0
    for _ in range(PLANT_LIMIT):
        if get_time() >= GAME_LIMIT:
            quick_print("wood_quarter failed game_limit_plant wid=", worker_id, "time=", get_time())
            return False, attempts, rejects
        attempts += 1
        if not plant(Entities.Tree):
            quick_print("wood_quarter failed plant wid=", worker_id, "time=", get_time())
            return False, attempts, rejects
        companion = get_companion()
        if companion != None and companion[0] == Entities.Grass:
            tx, ty = companion[1]
            if tx % 2 != 0 or ty % 2 != 0:
                return True, attempts, rejects
        # 非生产移除必须仍未成熟；异常时保留诊断，不把低倍收获计入组件。
        if can_harvest():
            quick_print("wood_quarter failed mature_reject wid=", worker_id, "time=", get_time(), "attempts=", attempts)
            return False, attempts, rejects
        harvest()
        rejects += 1
    quick_print("wood_quarter failed plant_limit wid=", worker_id, "time=", get_time())
    return False, attempts, rejects


def water_anchor():
    used = 0
    skipped = 0
    for _ in range(4):
        if get_water() >= WATER_THRESHOLD:
            break
        if num_items(Items.Water) < WATER_RESERVE:
            skipped = 1
            break
        use_item(Items.Water)
        used += 1
    return used, skipped


def record_point(worker_id, harvested, arrived, visits, unready, initial_accepts, initial_attempts, initial_rejects, replant_accepts, replant_attempts, replant_rejects, water_calls, low_water_visits, goto_moves):
    water_stock = num_items(Items.Water)
    quick_print("wood_quarter milestone wid=", worker_id, "harvested=", harvested, "time=", get_time(), "arrived=", arrived, "visits=", visits, "unready=", unready, "initial_accepts=", initial_accepts, "initial_attempts=", initial_attempts, "initial_rejects=", initial_rejects, "replant_accepts=", replant_accepts, "replant_attempts=", replant_attempts, "replant_rejects=", replant_rejects, "water_calls=", water_calls, "low_water_visits=", low_water_visits, "goto_moves=", goto_moves, "water_stock=", water_stock)


def move_once(direction):
    if not move(direction):
        quick_print("wood_quarter failed move", direction, get_time())
        return False
    return True


def goto(tx, ty):
    moved = 0
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % FIELD_SIZE
    if dx <= FIELD_SIZE // 2:
        for _ in range(dx):
            if not move_once(East):
                return -1
            moved += 1
    else:
        for _ in range(FIELD_SIZE - dx):
            if not move_once(West):
                return -1
            moved += 1
    dy = (ty - y) % FIELD_SIZE
    if dy <= FIELD_SIZE // 2:
        for _ in range(dy):
            if not move_once(North):
                return -1
            moved += 1
    else:
        for _ in range(FIELD_SIZE - dy):
            if not move_once(South):
                return -1
            moved += 1
    return moved


if __name__ == "__main__":
    lb_wood()
