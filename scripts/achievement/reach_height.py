from __builtins__ import *
# 摩天大楼：9台无人机同时垫高整块3×3田到z=+150，避免柱间高度差限制。
# 需要1350份建材；小田尺寸会在程序退出时由游戏恢复。
MAX_GAME_SECONDS = 300
TARGET_HEIGHT = 150


def reach_height():
    deadline = get_time() + MAX_GAME_SECONDS - 1
    set_world_size(3)
    clear()
    handles = []
    for cell in range(8):
        handle = spawn_drone(build_column, deadline)
        if handle == None:
            break
        handles.append(handle)
        move(East)
        if cell % 3 == 2:
            move(North)
    complete = False
    if len(handles) == 8:
        complete = build_column(deadline)
    for handle in handles:
        if not wait_for(handle):
            complete = False
    if complete:
        quick_print("整块3×3田已到达+150高度。", get_pos_z())
    else:
        quick_print("未完成垫高；需要9台无人机和1350份建材。")


def build_column(deadline):
    while get_pos_z() < TARGET_HEIGHT:
        if get_time() >= deadline or not place(Grounds.Block_Red):
            return False
    return True


if __name__ == "__main__":
    reach_height()
