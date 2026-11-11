from __builtins__ import *
# 探矿者：支付铁调用1000次石英勘探；命中矿层不是累计次数的前提。
MAX_GAME_SECONDS = 300
PROSPECTS = 1000


def prospector():
    deadline = get_time() + MAX_GAME_SECONDS - 1
    done = 0
    while done < PROSPECTS and get_time() < deadline:
        before = num_items(Items.Iron)
        if before < 1:
            break
        prospect_quartz()
        if num_items(Items.Iron) >= before:
            break
        done += 1
    quick_print("本次支付铁的勘探次数：", done, "目标：", PROSPECTS)


if __name__ == "__main__":
    prospector()
