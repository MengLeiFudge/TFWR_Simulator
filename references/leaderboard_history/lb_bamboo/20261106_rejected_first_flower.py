from __builtins__ import *
# 淘汰候选归档：lb_bamboo | 原实验路径 .codex/leaderboard-sol/underground-strategies/bamboo/first-flower/lb_bamboo.py

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
    # 高飞入格保持整株，harvest/plant会重置高度，因此每次补种后重新升高。
    hover(18)
    rounds = 0
    while num_items(Items.Bamboo) < goal:
        if get_time() > deadline:
            quick_print("bamboo_failed", "deadline", first, get_time())
            return False
        for x in range(first, size, stride):
            if not bamboo_move_to(x, 0, size):
                return False
            for _ in range(size):
                if num_items(Items.Bamboo) >= goal:
                    return True
                if get_entity_type() == Entities.Bamboo:
                    if can_harvest():
                        if not harvest() or not plant(Entities.Bamboo):
                            return False
                        hover(18)
                else:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if not plant(Entities.Bamboo):
                        return False
                    hover(18)
                if not move(North):
                    return False
        rounds += 1
        if first == 0 and rounds % 8 == 0:
            quick_print("bamboo_round", rounds, get_time(), num_items(Items.Bamboo))
    return True


def bamboo_move_to(tx, ty, size):
    # 平面农场按环绕短路定位；调用者保持18格高度以免切断路过的竹子。
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
