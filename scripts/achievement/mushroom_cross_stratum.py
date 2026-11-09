from __builtins__ import *
# 远距离友谊：保留原片的一块蘑菇，经地图两端环绕下送到另一片同色蘑菇。

WORLD_SIZE = 32
MAX_ATTEMPTS = 8
MAX_FALL = 12
MAX_DESCENT = 80
MAX_GAME_SECONDS = 3600


# 独立运行并只使用一次Jump；实际跨片配对后退出，失败时保留现场。
def mushroom_cross_stratum():
    set_world_size(WORLD_SIZE)
    clear()
    change_hat(Hats.Mining_Hat)
    jump(Unlocks.Mushrooms)
    deadline = get_time() + MAX_GAME_SECONDS
    for attempt in range(MAX_ATTEMPTS):
        if attempt > 0:
            clear()
            change_hat(Hats.Mining_Hat)
        quick_print("跨地层蘑菇：第", attempt + 1, "片")
        result = cross_attempt(deadline)
        if result != None:
            return result
    quick_print("跨地层配对未完成：已达到换田上限。")
    return False


# 两落点相隔31个实体格；每次只挖低12格，限制塌方传播接近另一端的机会。
def cross_attempt(deadline):
    if not cross_move_to(0, 0):
        return False
    limit = get_pos_z() - 128
    while get_ground_type() != Grounds.Mushroom:
        if get_pos_z() <= limit:
            return None
        step = cross_dig(deadline)
        if step != True:
            return step
    ceiling = get_pos_z()
    tone = measure()
    if not move(West):
        return False
    while get_pos_z() > ceiling:
        step = cross_dig(deadline)
        if step != True:
            return step
    if get_pos_z() != ceiling or get_ground_type() != Grounds.Mushroom:
        quick_print("两端首片蘑菇高度不一致，停止。")
        return False
    # 先取得原片下边界；目标必须越过这段原片且遇到同色，才可证明跨片。
    while get_ground_type() == Grounds.Mushroom:
        if ceiling - get_pos_z() >= MAX_FALL:
            return None
        step = cross_dig(deadline)
        if step != True:
            return step
    first_floor = get_pos_z()
    if get_pos_z(East) != ceiling or get_ground_type(East) != Grounds.Mushroom or measure(East) != tone:
        quick_print("保留蘑菇已变化，停止跨片搬运。")
        return False
    if not move(East) or not push(West) or not move(West):
        return False
    for hop in range(MAX_DESCENT):
        if get_ground_type() != Grounds.Mushroom or measure() != tone:
            quick_print("携带蘑菇丢失，停止：z", get_pos_z())
            return False
        source_z = get_pos_z()
        floor = max(ceiling - MAX_DESCENT, source_z - MAX_FALL)
        if floor >= source_z - 1:
            quick_print("本片下送范围内没有找到跨片同色，换田。")
            return None
        direction = West
        back = East
        if get_pos_x() == WORLD_SIZE - 1:
            direction = East
            back = West
        if not move(direction):
            return False
        matched = False
        while True:
            if get_ground_type() == Grounds.Mushroom and get_pos_z() < min(first_floor, source_z) and measure() == tone:
                matched = True
                break
            if get_pos_z() <= floor:
                break
            step = cross_dig(deadline)
            if step != True:
                return step
            if get_pos_z(back) != source_z or get_ground_type(back) != Grounds.Mushroom or measure(back) != tone:
                quick_print("下挖改变了携带柱，停止：第", hop + 1, "次")
                return False
        if get_pos_z(back) != source_z or get_ground_type(back) != Grounds.Mushroom or measure(back) != tone:
            quick_print("推送前携带柱校验失败，停止。")
            return False
        before = num_items(Items.Mushroom)
        if not move(back) or not push(direction) or not move(direction):
            return False
        gained = num_items(Items.Mushroom) - before
        if matched:
            if gained <= 0:
                quick_print("跨片同色推送没有产出，停止。")
                return False
            quick_print("跨地层同色配对完成：颜色", tone, "原片底部z", first_floor, "配对后z", get_pos_z())
            return True
        if gained > 0:
            quick_print("发生了未确认来源的提前配对，停止。")
            return False
        quick_print("蘑菇下送：第", hop + 1, "次，z", get_pos_z())
    quick_print("跨片下送达到次数上限，换田。")
    return None


# 所有下挖都受共同游戏时间和硬度边界限制，不使用爆破破坏保留块。
def cross_dig(deadline):
    ground = get_ground_type()
    if ground == Grounds.Soot or ground == Grounds.Dynamite:
        quick_print("原生炸药层阻断蘑菇下送，换田。")
        return None
    if get_time() >= deadline or get_hardness() >= 10000000 or not dig():
        quick_print("跨片下挖失败或达到时间上限：位置", get_pos_x(), get_pos_y(), get_pos_z())
        return False
    return True


# 初始定位使用环绕短路径；搬运阶段只在东西两端移动。
def cross_move_to(tx, ty):
    for delta, forward, backward in [(tx - get_pos_x(), East, West), (ty - get_pos_y(), North, South)]:
        steps = delta % WORLD_SIZE
        direction = forward
        if steps > WORLD_SIZE // 2:
            steps = WORLD_SIZE - steps
            direction = backward
        for _ in range(steps):
            if not move(direction):
                return False
    return True


if __name__ == "__main__":
    mushroom_cross_stratum()
