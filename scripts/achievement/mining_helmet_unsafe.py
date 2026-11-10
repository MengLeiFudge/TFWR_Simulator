from __builtins__ import *
# 成就入口：不戴采矿帽完成一次挖掘，触发 MINING_HELMET_UNSAFE。
# 最长运行300游戏秒。
MAX_GAME_SECONDS = 300


def mining_helmet_unsafe():
    deadline = get_time() + MAX_GAME_SECONDS
    change_hat(Hats.Top_Hat)
    while get_time() < deadline:
        if get_hardness() >= 10000000:
            quick_print("没有可挖地层，停止。")
            return
        if dig():
            quick_print("已用非采矿帽完成挖掘。")
            return
        break


if __name__ == "__main__":
    mining_helmet_unsafe()
