from __builtins__ import *


def f0():
    # 24 台子机加主机，正好占满 5×5 的 25 个位置。
    if max_drones() < 25 or num_drones() != 1:
        quick_print("需要至少 25 台无人机容量，请停止其他任务后重新运行 f0。")
        return
    set_world_size(5)
    if get_world_size() != 5:
        quick_print("世界未能设为 5×5，已停止派发。")
        return

    handles = []
    for i in range(24):
        handle = spawn_drone(dig_column)
        if handle == None:
            quick_print("无人机生成失败，请停止程序后重新运行 f0。")
            return
        handles.append(handle)
        if not move(North):
            quick_print("无法向北移动，请停止程序并检查帽子或地形。")
            return
        # 每走完一列，向东换列；环绕使任意初始位置都能遍历全图。
        if (i + 1) % 5 == 0:
            if not move(East):
                quick_print("无法向东移动，请停止程序并检查帽子或地形。")
                return

    quick_print("25 个挖掘位置已派发，主机开始挖最后一格。")
    dig_column()
    # 主机所在列停止后，其余无人机仍继续挖，直到用户停止程序。
    for handle in handles:
        wait_for(handle)


def dig_column():
    # 固守当前位置向下挖，不巡视、不换层扫图，也不等待其他列。
    while True:
        if get_hardness() >= 10000000:
            quick_print("遇到不可挖方块，本机停止：",
                        get_pos_x(), get_pos_y(), get_pos_z())
            return
        if not dig():
            quick_print("挖掘失败，本机停止：",
                        get_pos_x(), get_pos_y(), get_pos_z())
            return


if __name__ == "__main__":
    f0()
