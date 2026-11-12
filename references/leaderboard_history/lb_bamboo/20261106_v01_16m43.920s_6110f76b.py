from __builtins__ import *
# 历史提交归档：lb_bamboo | 初次提交 2026-11-06 (6110f76b) | 文档：记录新版竹子单双机正式完整成绩
# 完整轮时间：1003.920秒（构建26462009，8轮官方完整统计；请求340）。

def lb_bamboo():
    # 每列唯一写者；子机只通过全局库存判断结束，不共享私有作用域。
    clear()
    size = get_world_size()
    workers = min(size, max_drones())
    deadline = get_time() + 3600
    handles = []
    for column in range(1, workers):
        handle = spawn_drone(bamboo_columns, column, workers, size, 500000000, deadline)
        if handle == None:
            quick_print("bamboo_failed", "spawn", column)
            break
        handles.append(handle)
    local = bamboo_columns(0, workers, size, 500000000, deadline)
    for handle in handles:
        if not wait_for(handle):
            local = False
    quick_print("bamboo_done", local, get_time(), num_items(Items.Bamboo))


def bamboo_columns(first, stride, size, goal, deadline):
    # 偶数行种竹，奇数行留通道；低飞切花的出入不会碰到另一株竹子。
    phases = {}
    for x in range(first, size, stride):
        for y in range(0, size - 1, 2):
            phases[(x, y)] = 0
    hover(18)
    rounds = 0
    while num_items(Items.Bamboo) < goal:
        if get_time() > deadline:
            quick_print("bamboo_failed", "deadline", first, get_time())
            return False
        for x in range(first, size, stride):
            for y in range(0, size - 1, 2):
                if num_items(Items.Bamboo) >= goal:
                    return True
                if not bamboo_move_to(x, y + 1, size) or not move(South):
                    return False
                if get_entity_type() != Entities.Bamboo:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if not plant(Entities.Bamboo):
                        return False
                    phases[(x, y)] = 0
                    hover(18)
                elif can_harvest():
                    phase = phases[(x, y)]
                    if phase < 2:
                        height = measure()
                        if not move(North):
                            return False
                        hover(height)
                        if not move(South):
                            return False
                        if measure() <= height:
                            quick_print("bamboo_failed", "flower_not_cut", x, y, phase)
                            return False
                        phases[(x, y)] = phase + 1
                        hover(18)
                    else:
                        if not harvest() or not plant(Entities.Bamboo):
                            return False
                        phases[(x, y)] = 0
                        hover(18)
                if not move(North):
                    return False
        rounds += 1
        if first == 0 and rounds % 8 == 0:
            quick_print("bamboo_round", rounds, get_time(), num_items(Items.Bamboo))
    return True


def bamboo_move_to(tx, ty, size):
    # 定位期间高飞，切花仅在专属空通道与目标竹子之间往返。
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
    lb_bamboo()
