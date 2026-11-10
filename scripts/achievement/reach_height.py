from __builtins__ import *
# 成就入口：在z=-150或更深的位置放置一块彩色方块。
# 最长运行300游戏秒；需要预先准备Block。
MAX_GAME_SECONDS = 300
TARGET_DEPTH = 149


def reach_height():
    deadline = get_time() + MAX_GAME_SECONDS
    change_hat(Hats.Mining_Hat)
    while get_pos_z() > -TARGET_DEPTH:
        if get_time() >= deadline or get_hardness() >= 10000000 or not dig():
            quick_print("未能在5分钟内到达目标深度。")
            return
    if place(Grounds.Block_Red):
        quick_print("已在z<=-150的位置放置彩色方块。")
    else:
        quick_print("放置失败；需要Block库存或可放置高度。")


if __name__ == "__main__":
    reach_height()
