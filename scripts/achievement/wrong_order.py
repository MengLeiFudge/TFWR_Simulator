from __builtins__ import *
# 成就入口：在小田中种满成熟仙人掌，再按行列降序排列。
# 最长运行300游戏秒；需要准备至少9份仙人掌种子。
MAX_GAME_SECONDS = 300
FIELD_SIZE = 3


def goto(tx, ty):
    while get_pos_x() < tx:
        move(East)
    while get_pos_x() > tx:
        move(West)
    while get_pos_y() < ty:
        move(North)
    while get_pos_y() > ty:
        move(South)


def fill_field():
    for y in range(FIELD_SIZE):
        for x in range(FIELD_SIZE):
            goto(x, y)
            if get_ground_type() != Grounds.Soil:
                till()
            if get_entity_type() != Entities.Cactus:
                plant(Entities.Cactus)


def sort_field():
    for _ in range(20):
        for y in range(FIELD_SIZE):
            for x in range(FIELD_SIZE - 1):
                goto(x, y)
                if measure() < measure(East):  # ty: ignore[unsupported-operator]  仙人掌measure返回整数。
                    swap(East)
        for x in range(FIELD_SIZE):
            for y in range(FIELD_SIZE - 1):
                goto(x, y)
                if measure() < measure(North):  # ty: ignore[unsupported-operator]  仙人掌measure返回整数。
                    swap(North)


def wrong_order():
    deadline = get_time() + MAX_GAME_SECONDS
    set_world_size(FIELD_SIZE)
    clear()
    fill_field()
    while get_time() < deadline:
        ready = True
        for y in range(FIELD_SIZE):
            for x in range(FIELD_SIZE):
                goto(x, y)
                if not can_harvest():
                    ready = False
        if ready:
            sort_field()
            quick_print("已完成3×3仙人掌降序排列。")
            return
        do_a_flip()
    quick_print("仙人掌未在5分钟内全部成熟。")


if __name__ == "__main__":
    wrong_order()
