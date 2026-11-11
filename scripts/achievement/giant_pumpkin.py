from __builtins__ import *
# 巨型南瓜：整块32×32同步成熟并合并后，只收获一次；不切分生产区域。
MAX_GAME_SECONDS = 300
SIZE = 32


def giant_pumpkin():
    deadline = get_time() + MAX_GAME_SECONDS - 2
    set_world_size(SIZE)
    clear()
    if max_drones() - num_drones() < SIZE - 1:
        quick_print("需要32台可用无人机。")
        return
    handles = []
    for _ in range(SIZE - 1):
        handles.append(spawn_drone(grow_column, deadline))
        move(East)
    ready = grow_column(deadline)
    for handle in handles:
        if not wait_for(handle):
            ready = False
    if ready and get_time() < deadline:
        before = num_items(Items.Pumpkin)
        harvest()
        quick_print("整田巨型南瓜已收获，净增：", num_items(Items.Pumpkin) - before)
    else:
        quick_print("5分钟内未完成整田成熟；请检查种植材料、水和肥料。")


def grow_column(deadline):
    while get_time() < deadline:
        ready = True
        for _ in range(SIZE):
            if get_time() >= deadline:
                return False
            if get_ground_type() != Grounds.Soil:
                till()
            if not can_harvest() or get_entity_type() != Entities.Pumpkin:
                ready = False
                if get_entity_type() != Entities.Pumpkin:
                    if not plant(Entities.Pumpkin):
                        return False
                    use_item(Items.Water, 4)
                use_item(Items.Fertilizer, 4)
            move(North)
        if ready:
            return True
    return False


if __name__ == "__main__":
    giant_pumpkin()
