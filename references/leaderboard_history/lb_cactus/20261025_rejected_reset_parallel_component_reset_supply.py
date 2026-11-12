from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-sol/reset/cactus-parallel-component/lb_reset_cactus_supply.py
# 完整Reset三值：本地模拟未取得；短时打榜未取得；游戏打榜未取得。组件时间未取得。


# 冷启动计费；列阶段与行阶段之间收齐所有句柄，成功后才收割整田。
def lb_reset_cactus_supply():
    deadline = 90
    log_supply_stage("start", deadline, None)
    clear()
    cost = get_cost(Entities.Cactus)
    size = get_world_size()
    if size != 12 or max_drones() != 8 or num_drones() != 1 or num_unlocked(Unlocks.Cactus) != 2 or num_unlocked(Unlocks.Pumpkins) != 3 or num_unlocked(Unlocks.Speed) != 5:
        log_supply_stage("invalid_scene", deadline, None)
        return False
    if num_items(Items.Cactus) != 0 or num_items(Items.Pumpkin) != 576 or num_items(Items.Power) < 2100 or num_items(Items.Water) != 4000 or get_time() >= deadline:
        log_supply_stage("invalid_stock_or_deadline", deadline, None)
        return False
    if not can_pay_seed_cost(cost, size * size):
        log_supply_stage("insufficient_material", deadline, None)
        return False
    log_supply_stage("inputs_ready", deadline, None)
    phases = []
    for phase in range(2):
        result = run_cactus_phase(phase, deadline, cost)
        phases.append(result)
        if not result["success"]:
            log_supply_stage("phase_failed", deadline, phase)
            return False
        if not goto_wrap(0, 0, deadline):
            log_supply_stage("root_return_failed", deadline, phase)
            return False
        log_supply_stage("barrier_complete", deadline, phase)
    if get_time() >= deadline or get_entity_type() != Entities.Cactus or not can_harvest():
        log_supply_stage("final_harvest_guard_failed", deadline, None)
        return False
    if not harvest():
        log_supply_stage("final_harvest_failed", deadline, None)
        return False
    quick_print("supply_result_count", "phases=", len(phases), "workers=", len(phases[0]["results"]) + len(phases[1]["results"]))
    log_supply_stage("final_state", deadline, None)
    completed = num_items(Items.Cactus) == 41472 and num_items(Items.Pumpkin) == 0 and num_drones() == 1 and get_time() < deadline
    quick_print("supply_done", "passed=", completed, "time=", get_time(), "tick=", get_tick_count())
    return completed


# 仅主机持有handles/results；失败也先回收全部已创建任务，不作串行fallback。
def run_cactus_phase(phase, deadline, cost):
    handles = []
    results = []
    passed = True
    reason = "passed"
    root_started = False
    for worker in range(1, 8):
        if get_time() >= deadline:
            passed = False
            reason = "dispatch_deadline"
            break
        handle = spawn_drone(cactus_worker, worker, phase, deadline, cost)
        if handle == None:
            passed = False
            reason = "spawn_failed"
            break
        handles.append(handle)
    if passed:
        root_started = True
        result = cactus_worker(0, phase, deadline, cost)
        results.append(result)
        quick_print("supply_parent_result", phase, result)
        if not result["success"]:
            passed = False
            reason = "root_worker_failed"
    log_supply_stage("join_before", deadline, phase)
    joined = 0
    # 截止只阻止新工作；wait不能因passed=False或deadline而跳过。
    for handle in handles:
        result = wait_for(handle)
        joined = joined + 1
        results.append(result)
        quick_print("supply_parent_result", phase, result)
        if not result["success"]:
            passed = False
            reason = "child_worker_failed"
    log_supply_stage("join_after", deadline, phase)
    if get_time() >= deadline or num_drones() != 1:
        passed = False
        reason = "deadline_or_live_workers"
    quick_print("supply_dispatch", "phase=", phase, "spawned=", len(handles), "joined=", joined, "root_started=", root_started, "passed=", passed, "reason=", reason)
    return {"phase": phase, "success": passed, "spawned": len(handles), "joined": joined, "root_started": root_started, "reason": reason, "results": results}


# 参数按spawn接口复制；result仅属于本worker，prepared保存每列准备完成时刻。
def cactus_worker(worker, phase, deadline, cost):
    result = {"phase": phase, "worker": worker, "success": False, "lines": 0, "plants": 0, "passes": 0, "start": get_time(), "prepared": [], "end": None, "reason": "not_finished", "line": None, "position": None}
    size = get_world_size()
    line = worker
    while line < size:
        if get_time() >= deadline:
            return finish_cactus_worker(result, False, "worker_deadline", line)
        started = get_time()
        if phase == 0:
            if not goto_wrap(line, 0, deadline):
                return finish_cactus_worker(result, False, "column_route_failed", line)
            prepared = prepare_cactus_column(deadline, cost)
            result["plants"] = result["plants"] + prepared[1]
            quick_print("supply_line", phase, worker, line, "prepared", "start=", started, "time=", get_time(), "passed=", prepared[0], "plants=", prepared[1])
            if not prepared[0]:
                return finish_cactus_worker(result, False, prepared[2], line)
            result["prepared"].append((line, get_time()))
            mature = wait_cactus_column(deadline)
            result["passes"] = result["passes"] + mature[1]
            quick_print("supply_line", phase, worker, line, "mature", "time=", get_time(), "passed=", mature[0], "passes=", mature[1])
            if not mature[0]:
                return finish_cactus_worker(result, False, mature[2], line)
            if not sort_cactus_line(North, South, deadline):
                return finish_cactus_worker(result, False, "column_sort_failed", line)
        else:
            if not goto_wrap(0, line, deadline):
                return finish_cactus_worker(result, False, "row_route_failed", line)
            if not sort_cactus_line(East, West, deadline):
                return finish_cactus_worker(result, False, "row_sort_failed", line)
        result["lines"] = result["lines"] + 1
        quick_print("supply_line", phase, worker, line, "sorted", "time=", get_time())
        line = line + 8
    if get_time() >= deadline:
        return finish_cactus_worker(result, False, "worker_deadline", None)
    return finish_cactus_worker(result, True, "worker_done", None)


# success之外的字段在普通失败时也完整返回；位置取真实坐标，不复用计划值。
def finish_cactus_worker(result, passed, reason, line):
    result["success"] = passed
    result["end"] = get_time()
    result["reason"] = reason
    result["line"] = line
    result["position"] = (get_pos_x(), get_pos_y())
    quick_print("supply_worker", result)
    return result


# 从本列y=0铺12格并闭合回y=0；返回[成功,已成功plant数,原因]。
def prepare_cactus_column(deadline, cost):
    size = get_world_size()
    planted = 0
    for _ in range(size):
        if get_time() >= deadline:
            return [False, planted, "plant_deadline"]
        entity = get_entity_type()
        if entity != None:
            if entity != Entities.Grass:
                return [False, planted, "unexpected_initial_entity"]
            if not harvest():
                return [False, planted, "initial_harvest_failed"]
        if get_ground_type() == Grounds.Grassland:
            till()
        if not can_pay_seed_cost(cost, 1):
            return [False, planted, "seed_cost_failed"]
        if not plant(Entities.Cactus):
            return [False, planted, "plant_failed"]
        planted = planted + 1
        if not move(North):
            return [False, planted, "plant_move_failed"]
    if get_time() >= deadline:
        return [False, planted, "plant_deadline"]
    return [True, planted, "planted"]


# passes计已启动巡回，失败时可能未走完；正常每轮12次成熟查询、12次类型查询和12move。
def wait_cactus_column(deadline):
    size = get_world_size()
    passes = 0
    for _ in range(4):
        if get_time() >= deadline:
            return [False, passes, "maturity_deadline"]
        passes = passes + 1
        ready = 0
        for _ in range(size):
            if get_time() >= deadline or get_entity_type() != Entities.Cactus:
                return [False, passes, "maturity_entity_or_deadline"]
            if can_harvest():
                ready = ready + 1
            if not move(North):
                return [False, passes, "maturity_move_failed"]
        if get_time() >= deadline:
            return [False, passes, "maturity_deadline"]
        if ready == size:
            return [True, passes, "mature"]
    return [False, passes, "maturity_limit"]


# 保留原三元鸡尾酒比较、交换和边界更新；只补move的False出口。
def sort_cactus_line(forward, backward, deadline):
    size = get_world_size()
    bound_low = 0
    bound_high = size - 1
    while True:
        if get_time() >= deadline:
            return False
        swap_pos_last = -1
        if not move_cactus_line_to(forward, backward, bound_low, deadline):
            return False
        i = bound_low
        while i < bound_high - 1:
            if get_time() >= deadline:
                return False
            if not move(forward):
                return False
            i = i + 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if a > b:
                if not swap(backward):
                    return False
                swap_pos_last = max(swap_pos_last, i)
                a, b = b, a
            if b > c:
                if not swap(forward):
                    return False
                swap_pos_last = max(swap_pos_last, i + 1)
                b, c = c, b
                if a > b:
                    if not swap(backward):
                        return False
        if swap_pos_last == -1:
            break
        bound_high = swap_pos_last - 2
        if bound_low >= bound_high:
            break
        swap_pos_first = size
        if not move_cactus_line_to(forward, backward, bound_high, deadline):
            return False
        i = bound_high
        while i > bound_low + 1:
            if get_time() >= deadline:
                return False
            if not move(backward):
                return False
            i = i - 1
            a = measure(backward)
            b = measure()
            c = measure(forward)
            if b > c:
                if not swap(forward):
                    return False
                swap_pos_first = min(swap_pos_first, i)
                b, c = c, b
            if a > b:
                if not swap(backward):
                    return False
                swap_pos_first = min(swap_pos_first, i - 1)
                a, b = b, a
                if b > c:
                    if not swap(forward):
                        return False
        if swap_pos_first == size:
            break
        bound_low = swap_pos_first + 2
        if bound_low >= bound_high:
            break
    if bound_low + 1 == bound_high:
        if not move_cactus_line_to(forward, backward, bound_low, deadline):
            return False
        if get_time() >= deadline:
            return False
        if measure() > measure(forward):
            if not swap(forward):
                return False
    return get_time() < deadline


# 定位可绕边，方向选择沿用原实现；移动失败立即向排序调用方传播。
def move_cactus_line_to(forward, backward, target, deadline):
    size = get_world_size()
    if forward == North:
        current = get_pos_y()
    else:
        current = get_pos_x()
    delta = (target - current) % size
    if delta <= size // 2:
        for _ in range(delta):
            if get_time() >= deadline:
                return False
            if not move(forward):
                return False
    else:
        for _ in range(size - delta):
            if get_time() >= deadline:
                return False
            if not move(backward):
                return False
    return get_time() < deadline


# 主机和worker使用同一有限定位；不在失败后继续执行剩余轴。
def goto_wrap(tx, ty, deadline):
    size = get_world_size()
    half = size // 2
    dx = (tx - get_pos_x()) % size
    if dx <= half:
        for _ in range(dx):
            if get_time() >= deadline:
                return False
            if not move(East):
                return False
    else:
        for _ in range(size - dx):
            if get_time() >= deadline:
                return False
            if not move(West):
                return False
    dy = (ty - get_pos_y()) % size
    if dy <= half:
        for _ in range(dy):
            if get_time() >= deadline:
                return False
            if not move(North):
                return False
    else:
        for _ in range(size - dy):
            if get_time() >= deadline:
                return False
            if not move(South):
                return False
    return get_time() < deadline


# 全田和单株都使用实际get_cost；只读共享库存，不在此处补料。
def can_pay_seed_cost(cost, count):
    if cost == None or cost == {}:
        return False
    for item in cost:
        if num_items(item) < cost[item] * count:
            return False
    return True


# Power是全局库存快照；不把不同worker重叠区间的净降相加。
def log_supply_stage(stage, deadline, phase):
    quick_print("supply_stage", stage, "phase=", phase, "time=", get_time(), "tick=", get_tick_count(), "deadline=", deadline, "drones=", num_drones(), "carrot=", num_items(Items.Carrot), "pumpkin=", num_items(Items.Pumpkin), "cactus=", num_items(Items.Cactus), "power=", num_items(Items.Power), "water=", num_items(Items.Water), "fertilizer=", num_items(Items.Fertilizer), "hay=", num_items(Items.Hay), "wood=", num_items(Items.Wood))


if __name__ == "__main__":
    lb_reset_cactus_supply()
