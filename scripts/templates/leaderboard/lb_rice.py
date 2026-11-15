from __builtins__ import *
# 完整轮时间：本生成版本尚无完整实机成绩。


def lb_rice():
    clear()
    rice_launch(0, 32)


def rice_launch(lo, hi):
    while hi - lo > 1:
        mid = (lo + hi) // 2
        spawn_drone(rice_launch, mid, hi)
        hi = mid
    direction = East
    steps = lo
    if steps > 16:
        steps = 32 - steps
        direction = West
    for _ in range(steps):
        move(direction)
    rice_worker(False)

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
    prepared = False
    for band in range(128):
        # 每个Clay带有两茬；不重生世界，下一带利用已挖深度与坍塌。
        if not prepared:
            #@unroll
            for step in range(32):
                direction = North
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
        prepared = False
        #@unroll
        for step in range(32):
            direction = North
            if rice_harvest():
                if num_items(Items.Rice) >= goal:
                    clear()
                    return
                if get_ground_type() == Grounds.Dry_Rice_Terrace:
                    dig()
                    plant(Entities.Rice)
                    rice_water(single)
            move(direction)
        if band < 2:
            for direction in directions[:18]:
                rice_harvest()
                move(direction)
            for _ in range(14):
                move(North)
            if not rice_sow_segment(6):
                return
            for _ in range(12):
                move(North)
            for direction in directions[18:]:
                rice_harvest()
                move(direction)
            for _ in range(6):
                move(North)
            if not rice_sow_segment(26):
                return
            prepared = True
        else:
            #@unroll
            for step in range(32):
                direction = North
                rice_harvest()
                if num_items(Items.Rice) >= goal:
                    clear()
                    return
                move(direction)
        quick_print("rice_band", band, get_pos_z(), get_time(), num_items(Items.Rice))


def rice_sow_segment(count):
    for _ in range(count):
        while get_ground_type() != Grounds.Clay:
            if not dig():
                return False
        if not plant(Entities.Rice):
            return False
        rice_water(False)
        move(North)
    return True


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
    lb_rice()
