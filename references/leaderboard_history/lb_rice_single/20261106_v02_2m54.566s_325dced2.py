from __builtins__ import *
# 历史提交归档：lb_rice_single | 初次提交 2026-11-06 (325dced2) | 优化：稻米上下层流水并记录完整实机改善
# 完整轮时间：174.566秒（构建26462009，42轮官方完整统计；请求345）。

def lb_rice_single():
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    for batch in range(128):
        if num_items(Items.Rice) >= 100000:
            quick_print("rice_done", True, batch, get_time(), num_items(Items.Rice))
            return
        # 上一批所有句柄已回收，clear不会取消仍在工作的子机。
        clear()
        handles = []
        local = True
        for column in range(1, workers):
            handle = spawn_drone(rice_columns, column, workers, size, 100000, deadline)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not rice_columns(0, workers, size, 100000, deadline):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        quick_print("rice_batch", batch, local, get_time(), num_items(Items.Rice))
        if not local:
            quick_print("rice_failed", "batch", batch)
            return
    quick_print("rice_failed", "batch_limit", get_time(), num_items(Items.Rice))


def rice_columns(first, stride, size, goal, deadline):
    # 每柱唯一写者；先铺首层，再让第二层成熟与首层余下收割重叠。
    planted = []
    for x in range(first, size, stride):
        if not rice_move_to(x, 0, size):
            return False
        for y in range(size):
            if num_items(Items.Rice) >= goal:
                return True
            ground = get_ground_type()
            digs = 0
            while ground != Grounds.Clay and ground != Grounds.Rock and digs < 128:
                if get_time() > deadline or not dig():
                    return False
                ground = get_ground_type()
                digs += 1
            if ground == Grounds.Clay:
                if not plant(Entities.Rice):
                    return False
                planted.append((x, y))
            if not move(North):
                return False
    second = []
    for x, y in planted:
        if num_items(Items.Rice) >= goal:
            return True
        if not rice_move_to(x, y, size):
            return False
        while get_entity_type() == Entities.Rice and not can_harvest():
            if get_time() > deadline:
                return False
            do_a_flip()
        if get_entity_type() == Entities.Rice:
            # 干梯田可能仍承载成熟株；只有harvest成功后才下挖。
            if not harvest():
                return False
            if num_items(Items.Rice) < goal and get_ground_type() == Grounds.Dry_Rice_Terrace:
                if get_time() > deadline or not dig():
                    return False
                if get_ground_type() == Grounds.Clay:
                    if not plant(Entities.Rice):
                        return False
                    second.append((x, y))
    for x, y in second:
        if num_items(Items.Rice) >= goal:
            return True
        if not rice_move_to(x, y, size):
            return False
        while get_entity_type() == Entities.Rice and not can_harvest():
            if get_time() > deadline:
                return False
            do_a_flip()
        if get_entity_type() == Entities.Rice and not harvest():
            return False
    return True


def rice_move_to(tx, ty, size):
    # 常规帽子可跨高度移动；每次到柱后重新读取地层，不缓存塌方前深度。
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    lb_rice_single()
