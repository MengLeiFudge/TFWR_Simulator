from __builtins__ import *


def f0():
    # 沿用 5×5 稻田：24 台子机加主机，每格一台。
    if max_drones() < 25 or num_drones() != 1:
        quick_print("需要至少 25 台无人机容量，请停止其他任务后重新运行 f0。")
        return
    if not num_unlocked(Unlocks.Rice):
        quick_print("请先解锁水稻，再运行 f0。")
        return
    set_world_size(5)
    if get_world_size() != 5:
        quick_print("世界未能设为 5×5，已停止。")
        return

    # jump 每次脚本只能使用一次；后续清场后直接从地表找黏土。
    jump(Unlocks.Rice)
    while True:
        prepared = run_grid(prepare_cell)
        if prepared == None:
            return
        ready = 0
        for result in prepared:
            if result < 0:
                return
            ready += result
        if not ready:
            # 所有整地任务都已回收，且上一批水稻已收完，此时才能清场。
            quick_print("黏土已用完，重置稻田。")
            clear()
            continue

        before = num_items(Items.Rice)
        results = run_grid(grow_cell)
        if results == None:
            return
        for ok in results:
            if not ok:
                return
        quick_print("本轮水稻收获完成，新增：", num_items(Items.Rice) - before,
                    "，总库存：", num_items(Items.Rice))


def run_grid(task):
    # 一轮只做整地或种收；等全部子机结束，再允许下一轮挖掘或清场。
    handles = []
    results = []
    dispatched = True
    for i in range(24):
        handle = spawn_drone(task)
        if handle == None:
            quick_print("无人机生成失败，本轮回收后停止。")
            dispatched = False
            break
        handles.append(handle)
        if not move(North):
            quick_print("无法向北移动，请检查帽子或地形。")
            dispatched = False
            break
        if (i + 1) % 5 == 0:
            if not move(East):
                quick_print("无法向东移动，请检查帽子或地形。")
                dispatched = False
                break

    if dispatched:
        results.append(task())
    for handle in handles:
        results.append(wait_for(handle))
    if not dispatched:
        return None
    return results


def prepare_cell():
    # 返回 1：露出黏土；0：本格黏土耗尽；-1：挖掘失败。
    covers = (Grounds.Grassland, Grounds.Soil, Grounds.Dirt,
              Grounds.Dry_Rice_Terrace)
    ground = get_ground_type()
    while ground != Grounds.Clay:
        # 黏土下方的岩石不继续挖；其他格子还能种时先保留它们。
        if ground not in covers:
            return 0
        if get_hardness() >= 10000000 or not dig():
            quick_print("整地失败：", get_pos_x(), get_pos_y(), get_pos_z())
            return -1
        ground = get_ground_type()
    return 1


def grow_cell():
    # 整地阶段已结束，整个种收阶段都不挖掘，避免塌方毁掉邻格稻苗。
    if get_ground_type() != Grounds.Clay:
        return True
    if not plant(Entities.Rice):
        quick_print("水稻种植失败：", get_pos_x(), get_pos_y(), get_pos_z())
        return False
    while not can_harvest():
        if get_entity_type() != Entities.Rice:
            quick_print("水稻消失，已停止：", get_pos_x(), get_pos_y(), get_pos_z())
            return False
    if not harvest():
        quick_print("水稻收获失败：", get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


if __name__ == "__main__":
    f0()
