from __builtins__ import *
# 成就入口：字面量while True会触发 INFINITE_LOOP。
# 原版在进入字面量循环时判定；循环体主动退出，不需要一直占用游戏。
MAX_GAME_SECONDS = 300


def infinite_loop():
    while True:
        do_a_flip()
        break


if __name__ == "__main__":
    infinite_loop()
