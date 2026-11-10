from __builtins__ import *
# 成就入口：挖到岩石后调用 till；最多运行300游戏秒。
MAX_GAME_SECONDS = 300
MAX_DEPTH = 128


def till_rock():
    deadline = get_time() + MAX_GAME_SECONDS
    change_hat(Hats.Mining_Hat)
    for _ in range(MAX_DEPTH):
        if get_time() >= deadline:
            quick_print("TILL_ROCK 超过5分钟预算。")
            return
        if get_ground_type() == Grounds.Rock:
            till()
            quick_print("已对岩石调用 till。")
            return
        if get_pos_z() <= -MAX_DEPTH or get_hardness() >= 10000000 or not dig():
            break
    quick_print("当前柱未找到岩石，保留现场供人工继续。")


if __name__ == "__main__":
    till_rock()
