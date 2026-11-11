from __builtins__ import *
# 梯田：3×3田只种不收，让所有地表同时覆盖水稻。
MAX_GAME_SECONDS = 300


def rice_terrace():
    deadline = get_time() + MAX_GAME_SECONDS - 2
    set_world_size(3)
    change_hat(Hats.Mining_Hat)
    for attempt in range(16):
        clear()
        planted = 0
        for cell in range(9):
            while get_ground_type() != Grounds.Clay and get_ground_type() != Grounds.Rock:
                if get_time() + get_hardness() / (1.5 ** num_unlocked(Unlocks.Mining)) >= deadline:
                    quick_print("5分钟内未完成整田水稻。")
                    return
                if not dig():
                    return
            if get_ground_type() != Grounds.Clay or not plant(Entities.Rice):
                break
            planted += 1
            move(East)
            if cell % 3 == 2:
                move(North)
        if planted == 9:
            quick_print("整块3×3田已覆盖水稻。")
            return
        if get_time() >= deadline:
            break
    quick_print("未找到整田可种水稻的地形，已停止。")


if __name__ == "__main__":
    rice_terrace()
