from __builtins__ import *
# 成就入口：把函数作为参数传给另一个函数。
# 最长运行300游戏秒。
MAX_GAME_SECONDS = 300


def identity():
    return 1


def apply(function):
    return function()


def higher_order_programming():
    if get_time() < MAX_GAME_SECONDS:
        result = apply(identity)
        quick_print("函数参数调用结果：", result)


if __name__ == "__main__":
    higher_order_programming()
