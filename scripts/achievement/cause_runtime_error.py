from __builtins__ import *
# 成就入口：故意触发一次运行时错误，触发后脚本应停止。
# 入口本身不应进入生产目录或被自动重试。
MAX_GAME_SECONDS = 300


def cause_runtime_error():
    if get_time() < MAX_GAME_SECONDS:
        value = 1 / 0
        quick_print(value)


if __name__ == "__main__":
    cause_runtime_error()
