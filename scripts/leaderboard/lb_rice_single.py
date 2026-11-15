from __builtins__ import *
# 完整轮时间：本版尚无完整实机成绩；本地完整目标对照见同名单榜文档。


def lb_rice_single():
    clear()
    rice_worker(True)

def rice_worker(single):
    directions = []
    if single:
        for x in range(8):
            direction = North
            if x % 2:
                direction = South
            for _ in range(7):
                directions.append(direction)
            directions.append(East)
    else:
        for _ in range(32):
            directions.append(North)
    goal = 2000000
    if single:
        goal = 100000
    for band in range(128):
        remaining = goal - num_items(Items.Rice)
        if remaining <= 8192:
            rice_final((remaining + 127) // 128, directions, goal)
            return
        # 每个Clay带有两茬；不重生世界，下一带利用已挖深度与坍塌。
        for direction in directions:
            for _ in range(128):
                if get_ground_type() == Grounds.Clay:
                    break
                if not dig():
                    quick_print("rice_failed", "clay", band)
                    return
            if not plant(Entities.Rice):
                quick_print("rice_failed", "plant", band)
                return
            rice_water(single)
            move(direction)
        for direction in directions:
            if rice_harvest():
                if num_items(Items.Rice) >= goal:
                    clear()
                    return
                if get_ground_type() == Grounds.Dry_Rice_Terrace:
                    dig()
                    plant(Entities.Rice)
                    rice_water(single)
            move(direction)
        for direction in directions:
            rice_harvest()
            if num_items(Items.Rice) >= goal:
                clear()
                return
            move(direction)
        quick_print("rice_band", band, get_pos_z(), get_time(), num_items(Items.Rice))


def rice_final(needed, directions, goal):
    # 单机没有相邻工人干扰；每株128，末段只种真实缺口所需株数。
    for i in range(needed):
        while get_ground_type() != Grounds.Clay:
            if not dig():
                return
        plant(Entities.Rice)
        rice_water(True)
        move(directions[i])
    for target, current, positive, negative in [(0, get_pos_x(), East, West), (0, get_pos_y(), North, South)]:
        count = (target - current) % 8
        direction = positive
        if count > 4:
            count = 8 - count
            direction = negative
        for _ in range(count):
            move(direction)
    for i in range(needed):
        rice_harvest()
        if num_items(Items.Rice) >= goal:
            clear()
            return
        move(directions[i])
    quick_print("rice_failed", "final", get_time(), num_items(Items.Rice))


def rice_harvest():
    if get_entity_type() != Entities.Rice:
        return False
    if not can_harvest():
        if get_water() < 0.25 and num_items(Items.Water) >= 1:
            use_item(Items.Water)
        while get_entity_type() == Entities.Rice and not can_harvest():
            for _ in range(16):
                pass
    if get_entity_type() == Entities.Rice:
        return harvest()
    return False


def rice_water(single):
    water = get_water()
    if single:
        if water < 0.15:
            amount = (1 - water) * 4 // 1
            if water + amount * 0.25 < 1:
                amount += 1
            amount = min(amount, num_items(Items.Water) // 1)
            if amount > 0:
                use_item(Items.Water, amount)  # ty: ignore[invalid-argument-type] # 向上取整后的游戏Number。
    elif water < 0.25:
        if num_items(Items.Water) > 100:
            use_item(Items.Water, 2)
        elif water < 0.1 and num_items(Items.Water) >= 1:
            use_item(Items.Water)


if __name__ == "__main__":
    lb_rice_single()
