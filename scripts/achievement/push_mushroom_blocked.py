from __builtins__ import *
# 成就入口：找到蘑菇并尝试向被更浅地层阻挡的方向推动。
# 最长运行300游戏秒。
MAX_GAME_SECONDS = 300
MAX_DEPTH = 128
DIRECTIONS = [North, East, South, West]


def push_mushroom_blocked():
    deadline = get_time() + MAX_GAME_SECONDS
    change_hat(Hats.Mining_Hat)
    for _ in range(MAX_DEPTH):
        if get_time() >= deadline:
            return
        if get_ground_type() == Grounds.Mushroom:
            for direction in DIRECTIONS:
                if not can_push(direction):
                    push(direction)
                    quick_print("已尝试推动受阻蘑菇。")
                    return
        if get_pos_z() <= -MAX_DEPTH or get_hardness() >= 10000000 or not dig():
            break
    quick_print("当前柱未找到受阻蘑菇，保留现场供人工继续。")


if __name__ == "__main__":
    push_mushroom_blocked()
