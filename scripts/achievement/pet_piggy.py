from __builtins__ import *
# 成就入口：执行一次抚摸小猪；最多运行300游戏秒。
MAX_GAME_SECONDS = 300


def pet_piggy():
    if get_time() < MAX_GAME_SECONDS:
        pet_the_piggy()
        quick_print("已执行 pet_the_piggy。")


if __name__ == "__main__":
    pet_piggy()
