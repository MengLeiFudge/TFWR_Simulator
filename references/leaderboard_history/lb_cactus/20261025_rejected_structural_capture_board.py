from __builtins__ import *
# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-structural/capture_board.py
# 初盘采集组件；完整打榜时间未验证。
def capture_board():
    handles = []
    ok = True
    for y in range(31):
        handle = spawn_drone(fill_row)
        if handle == None:
            ok = False
            break
        handles.append(handle)
        if not move(North):
            ok = False
            break
    if ok:
        ok = fill_row()
    for handle in handles:
        if not wait_for(handle):
            ok = False
    quick_print("capture_finished", ok, get_time())


def fill_row():
    row = get_pos_y()
    for x in range(32):
        if get_ground_type() != Grounds.Soil:
            till()
        if not plant(Entities.Cactus):
            return False
        if x < 31:
            if not move(East):
                return False
    quick_print("capture_row", row, get_time())
    return True


if __name__ == "__main__":
    capture_board()
