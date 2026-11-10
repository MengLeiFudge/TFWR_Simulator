from __builtins__ import *
# 成就入口：导入两个互相导入的游戏模块，触发 CIRCULAR_IMPORT。
# 运行前必须把同目录的 circular_import_a.py 与 circular_import_b.py 一起保留。
MAX_GAME_SECONDS = 300


def circular_import():
    if get_time() < MAX_GAME_SECONDS:
        import circular_import_a
        quick_print("已启动循环导入。")


if __name__ == "__main__":
    circular_import()
