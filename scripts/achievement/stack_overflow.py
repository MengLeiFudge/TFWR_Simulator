from __builtins__ import *
# 成就入口：通过递归调用超过游戏执行栈上限。
# 达成后脚本会停止；不用于常规生产。
MAX_GAME_SECONDS = 300


def recurse(depth):
    if depth > 1200:
        return depth
    return recurse(depth + 1)


def stack_overflow():
    if get_time() < MAX_GAME_SECONDS:
        recurse(0)


if __name__ == "__main__":
    stack_overflow()
