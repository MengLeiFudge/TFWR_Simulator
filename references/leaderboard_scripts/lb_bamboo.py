from __builtins__ import *
# 完整轮时间：978.167秒（构建26462009，8轮官方完整统计；请求356）。

def lb_bamboo():
    clear()
    size = get_world_size()
    if size % 2 != 0 or max_drones() < size:
        quick_print("bamboo_failed", "row_worker_layout", size, max_drones())
        return
    deadline = get_time() + 3600
    handles = []
    ok = True
    for owner in range(1, size):
        row = 2 * (owner // 2)
        low = (owner % 2) * (size // 2)
        handle = spawn_drone(bamboo_row, row, low, low + size // 2 - 1, 500000000, deadline)
        if handle == None:
            ok = False
            break
        handles.append(handle)
    if not bamboo_row(0, 0, size // 2 - 1, 500000000, deadline):
        ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    quick_print("bamboo_done", ok, get_time(), num_items(Items.Bamboo))


def bamboo_row(row, low, high, goal, deadline):
    # 半行只有一个写者；低飞出入仅发生在本株与其上方空道之间。
    size = get_world_size()
    phases = []
    for _ in range(low, high + 1):
        phases.append(0)
    hover(18)
    x = low
    direction = East
    if not bamboo_move_to(x, row + 1, size):
        return False
    visits = 0
    while num_items(Items.Bamboo) < goal:
        if get_time() > deadline:
            quick_print("bamboo_failed", "deadline", row, low, get_time())
            return False
        if not move(South):
            return False
        if get_entity_type() != Entities.Bamboo:
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(Entities.Bamboo):
                return False
            phases[x - low] = 0
            hover(18)
        elif can_harvest():
            phase = phases[x - low]
            if phase < 2:
                height = measure()
                if not move(North):
                    return False
                hover(height)
                if not move(South):
                    return False
                if measure() <= height:
                    quick_print("bamboo_failed", "flower_not_cut", x, row, phase)
                    return False
                phases[x - low] = phase + 1
                hover(18)
            else:
                if not harvest() or not plant(Entities.Bamboo):
                    return False
                phases[x - low] = 0
                hover(18)
        if not move(North):
            return False
        # 端点访问后先移到相邻株再检查；全程留在自己的半行空道。
        if high > low:
            if x == high:
                direction = West
            elif x == low:
                direction = East
            if not move(direction):
                return False
            if direction == East:
                x += 1
            else:
                x -= 1
        visits += 1
        if row == 0 and low == 0 and visits % 128 == 0:
            quick_print("bamboo_row_visits", visits, get_time(), num_items(Items.Bamboo))
    return True


def bamboo_move_to(tx, ty, size):
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
