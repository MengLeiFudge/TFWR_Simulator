from __builtins__ import *
# 泥泞农场：32台无人机并行浇水，使整田同时超过0.5含水量。
# 需要4096份水；截止前预留最后一次动作和回收时间。
MAX_GAME_SECONDS = 300
FIELD_SIZE = 32


def mud_farm():
    deadline = get_time() + MAX_GAME_SECONDS - 1
    set_world_size(FIELD_SIZE)
    clear()
    handles = []
    for _ in range(FIELD_SIZE - 1):
        handle = spawn_drone(water_column, deadline)
        if handle == None:
            break
        handles.append(handle)
        move(East)
    complete = water_column(deadline)
    for handle in handles:
        if not wait_for(handle):
            complete = False
    if complete and len(handles) == FIELD_SIZE - 1:
        quick_print("已为整块32×32农场补水。")
    else:
        quick_print("未完成整田补水；需要32台无人机和4096份水。")


def water_column(deadline):
    for _ in range(FIELD_SIZE):
        if get_time() >= deadline or not use_item(Items.Water, 4):
            return False
        move(North)
    return True


if __name__ == "__main__":
    mud_farm()
