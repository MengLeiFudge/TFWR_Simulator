from __builtins__ import *
# 淘汰候选归档：lb_pumpkins | 原实验路径 .codex/leaderboard-sol/pumpkins/full-cover-component/lb_pumpkins.py


def lb_pumpkins():
    started_at = get_time()
    total_deadline = started_at + 90
    quick_print("pumpkin_full_cover start", "time=", started_at,
                "worker_columns=", ["id", "ok", "reason", "started", "arrived", "seeded", "ready", "finished", "initial", "dead_replant", "unripe", "water_calls", "move_calls", "pending_visits", "plant_attempts", "tills"],
                "wave_columns=", ["wave", "dispatch_start", "dispatch_end", "main_done", "join_done", "origin_done", "harvest_before", "harvest_after", "pumpkin_before", "pumpkin_after", "gain", "carrot_before", "carrot_after", "water_before", "water_after", "power_before", "power_after", "return_moves", "ok", "reason"])
    if get_world_size() != 32:
        return finish_component(False, 0, started_at, "world_size")
    clear()
    completed = 0
    for wave in range(4):
        wave_started = get_time()
        wave_deadline = wave_started + 20
        phase = [wave + 1, wave_started, None, None, None, None, None, None,
                 num_items(Items.Pumpkin), None, 0,
                 num_items(Items.Carrot), None, num_items(Items.Water), None,
                 num_items(Items.Power), None, 0, False, None]
        results = []
        for _ in range(32):
            results.append(None)
        handles = []
        reason = None
        for worker_id in range(1, 32):
            reason = deadline_reason(wave_deadline, total_deadline)
            if reason != None:
                break
            handle = spawn_drone(make_worker(worker_id, wave == 0, wave_deadline, total_deadline))
            if handle == None:
                reason = "spawn_failed"
                break
            handles.append((worker_id, handle))
        phase[2] = get_time()
        if reason == None:
            results[0] = prepare_region(0, wave == 0, wave_deadline, total_deadline)
        else:
            results[0] = new_worker_result(0)
            fail_worker(results[0], reason)
        phase[3] = get_time()
        if not results[0][1] and reason == None:
            reason = "main_worker_failed"
        # 失败后仍回收每个已创建任务；尚未派发的位置保留None。
        for worker_id, handle in handles:
            result = wait_for(handle)
            results[worker_id] = result
            if result == None or result == False:
                if reason == None:
                    reason = "missing_worker_result"
            elif len(result) != 16 or result[0] != worker_id or not result[1]:
                if reason == None:
                    reason = "worker_failed"
        phase[4] = get_time()
        if reason == None:
            reason = deadline_reason(wave_deadline, total_deadline)
        if reason == None:
            moved, calls, move_reason = go_to(0, 0, wave_deadline, total_deadline)
            phase[17] = calls
            if not moved:
                reason = move_reason
            else:
                phase[5] = get_time()
        if reason == None:
            if get_entity_type() != Entities.Pumpkin:
                reason = "harvest_entity"
            elif not can_harvest():
                reason = "harvest_not_ready"
        if reason == None:
            reason = deadline_reason(wave_deadline, total_deadline)
        if reason == None:
            before = num_items(Items.Pumpkin)
            phase[6] = get_time()
            if not harvest():
                reason = "harvest_failed"
            phase[7] = get_time()
            after = num_items(Items.Pumpkin)
            phase[10] = after - before
            if reason == None and phase[10] != 3145728:
                reason = "harvest_gain"
            if reason == None:
                reason = deadline_reason(wave_deadline, total_deadline)
        phase[9] = num_items(Items.Pumpkin)
        phase[12] = num_items(Items.Carrot)
        phase[14] = num_items(Items.Water)
        phase[16] = num_items(Items.Power)
        if reason == None:
            reason = deadline_reason(wave_deadline, total_deadline)
        phase[18] = reason == None
        phase[19] = reason
        quick_print("pumpkin_full_cover wave", "phase=", phase, "workers=", results)
        if reason == None:
            reason = deadline_reason(wave_deadline, total_deadline)
        if reason != None:
            quick_print("pumpkin_full_cover failed", "wave=", wave + 1, "reason=", reason, "time=", get_time())
            return finish_component(False, completed, started_at, reason)
        completed = completed + 1
    return finish_component(True, completed, started_at, None)


def make_worker(worker_id, first_wave, wave_deadline, total_deadline):
    # 每次工厂调用绑定自己的参数；spawn复制该闭包，不依赖共享全局状态。
    def worker():
        return prepare_region(worker_id, first_wave, wave_deadline, total_deadline)
    return worker


def prepare_region(worker_id, first_wave, wave_deadline, total_deadline):
    result = new_worker_result(worker_id)
    anchor_x = (worker_id % 8) * 4
    anchor_y = (worker_id // 8) * 8
    if not worker_move(result, anchor_x, anchor_y, wave_deadline, total_deadline):
        return result
    result[4] = get_time()
    pending = []
    for dx, dy in region_path():
        x = anchor_x + dx
        y = anchor_y + dy
        if not worker_move(result, x, y, wave_deadline, total_deadline):
            return result
        if not within_budget(result, wave_deadline, total_deadline):
            return result
        if first_wave and get_ground_type() != Grounds.Soil:
            till()
            result[15] = result[15] + 1
        if get_ground_type() != Grounds.Soil:
            fail_worker(result, "soil_not_ready")
            return result
        entity = get_entity_type()
        if entity == None or entity == Entities.Dead_Pumpkin:
            if not plant_owned_cell(result, entity == Entities.Dead_Pumpkin, wave_deadline, total_deadline):
                return result
        elif entity != Entities.Pumpkin:
            fail_worker(result, "seed_entity")
            return result
        pending.append((x, y))
    if not worker_move(result, anchor_x, anchor_y, wave_deadline, total_deadline):
        return result
    result[5] = get_time()
    while pending:
        index = 0
        while index < len(pending):
            if not within_budget(result, wave_deadline, total_deadline):
                return result
            if result[13] >= 4096:
                fail_worker(result, "visit_limit")
                return result
            result[13] = result[13] + 1
            x, y = pending[index]
            if not worker_move(result, x, y, wave_deadline, total_deadline):
                return result
            entity = get_entity_type()
            if entity == Entities.Pumpkin:
                if can_harvest():
                    pending.pop(index)
                    continue
                result[10] = result[10] + 1
            elif entity == None or entity == Entities.Dead_Pumpkin:
                if not plant_owned_cell(result, entity == Entities.Dead_Pumpkin, wave_deadline, total_deadline):
                    return result
            else:
                fail_worker(result, "pending_entity")
                return result
            index = index + 1
    if not within_budget(result, wave_deadline, total_deadline):
        return result
    result[6] = get_time()
    result[1] = True
    result[2] = "ok"
    result[7] = get_time()
    return result


def new_worker_result(worker_id):
    # 0编号，1成功，2原因，3起步，4到位，5首种完，6就绪，7结束；
    # 8空格初植，9死苗重种，10未成熟访问，11水调用，12移动调用，13pending访问，14plant尝试，15翻地。
    return [worker_id, False, "in_progress", get_time(), None, None, None, None,
            0, 0, 0, 0, 0, 0, 0, 0]


def worker_move(result, x, y, wave_deadline, total_deadline):
    moved, calls, reason = go_to(x, y, wave_deadline, total_deadline)
    result[12] = result[12] + calls
    if not moved:
        return fail_worker(result, reason)
    return True


def go_to(tx, ty, wave_deadline, total_deadline):
    calls = 0
    reason = deadline_reason(wave_deadline, total_deadline)
    if reason != None:
        return False, calls, reason
    dx = (tx - get_pos_x()) % 32
    dy = (ty - get_pos_y()) % 32
    if dx <= 16:
        x_direction = East
        x_steps = dx
    else:
        x_direction = West
        x_steps = 32 - dx
    if dy <= 16:
        y_direction = North
        y_steps = dy
    else:
        y_direction = South
        y_steps = 32 - dy
    for _ in range(x_steps):
        reason = deadline_reason(wave_deadline, total_deadline)
        if reason != None:
            return False, calls, reason
        calls = calls + 1
        if not move(x_direction):
            return False, calls, "move_failed"
    for _ in range(y_steps):
        reason = deadline_reason(wave_deadline, total_deadline)
        if reason != None:
            return False, calls, reason
        calls = calls + 1
        if not move(y_direction):
            return False, calls, "move_failed"
    return True, calls, None


def plant_owned_cell(result, dead_replant, wave_deadline, total_deadline):
    if not within_budget(result, wave_deadline, total_deadline):
        return False
    if result[14] >= 512:
        return fail_worker(result, "plant_limit")
    water_calls = 0
    while get_water() + 0.25 <= min(num_items(Items.Water) / 100, 1.0):
        if not within_budget(result, wave_deadline, total_deadline):
            return False
        if water_calls >= 5:
            return fail_worker(result, "water_limit")
        water_calls = water_calls + 1
        result[11] = result[11] + 1
        if not use_item(Items.Water):
            return fail_worker(result, "water_failed")
    if not within_budget(result, wave_deadline, total_deadline):
        return False
    result[14] = result[14] + 1
    if not plant(Entities.Pumpkin):
        return fail_worker(result, "plant_failed")
    if dead_replant:
        result[9] = result[9] + 1
    else:
        result[8] = result[8] + 1
    return True


def within_budget(result, wave_deadline, total_deadline):
    reason = deadline_reason(wave_deadline, total_deadline)
    if reason != None:
        return fail_worker(result, reason)
    return True


def deadline_reason(wave_deadline, total_deadline):
    now = get_time()
    if now >= total_deadline:
        return "total_deadline"
    if now >= wave_deadline:
        return "wave_deadline"
    return None


def fail_worker(result, reason):
    result[1] = False
    result[2] = reason
    result[7] = get_time()
    return False


def region_path():
    return [(0, 0), (1, 0), (2, 0), (3, 0),
            (3, 1), (2, 1), (1, 1), (1, 2), (2, 2), (3, 2),
            (3, 3), (2, 3), (1, 3), (1, 4), (2, 4), (3, 4),
            (3, 5), (2, 5), (1, 5), (1, 6), (2, 6), (3, 6),
            (3, 7), (2, 7), (1, 7), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1)]


def finish_component(ok, completed, started_at, reason):
    if ok and get_time() >= started_at + 90:
        ok = False
        reason = "total_deadline"
    quick_print("pumpkin_full_cover end", "ok=", ok, "waves=", completed,
                "started=", started_at, "time=", get_time(), "reason=", reason,
                "pumpkin=", num_items(Items.Pumpkin), "carrot=", num_items(Items.Carrot),
                "water=", num_items(Items.Water), "power=", num_items(Items.Power))
    return ok


if __name__ == "__main__":
    lb_pumpkins()
