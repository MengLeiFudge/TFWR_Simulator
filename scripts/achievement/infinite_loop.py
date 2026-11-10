from __builtins__ import *
# 成就入口：字面量while True会触发 INFINITE_LOOP。
# 达成后必须手动停止；本地模拟器用有限预算回收它。
MAX_GAME_SECONDS = 300


def infinite_loop():
    while True:
        do_a_flip()


if __name__ == "__main__":
    infinite_loop()
