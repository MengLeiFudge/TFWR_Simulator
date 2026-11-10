from __builtins__ import *
# 成就入口：把32×32每格的含水量提高到至少0.5。
# 每格使用两份水；最多运行300游戏秒。
MAX_GAME_SECONDS = 300
FIELD_SIZE = 32


def mud_farm():
    deadline = get_time() + MAX_GAME_SECONDS
    set_world_size(FIELD_SIZE)
    clear()
    for y in range(FIELD_SIZE):
        for x in range(FIELD_SIZE):
            if get_time() >= deadline:
                quick_print("MUD_FARM 超过5分钟预算。")
                return
            if not use_item(Items.Water, 2):
                quick_print("水不足，至少需要2048份水。")
                return
            if x + 1 < FIELD_SIZE:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        if y + 1 < FIELD_SIZE:
            move(North)
            if not use_item(Items.Water, 2):
                quick_print("水不足，至少需要2048份水。")
                return
    quick_print("已为整块32×32农场补水。")


if __name__ == "__main__":
    mud_farm()
