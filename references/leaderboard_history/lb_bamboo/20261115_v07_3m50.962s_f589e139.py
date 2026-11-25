from __builtins__ import *
# 完整轮时间：本版尚无完整实机成绩；本地完整目标对照见同名单榜文档。


def lb_bamboo():
    clear()
    for _ in range(31):
        spawn_drone(bamboo_row)
        move(North)
    bamboo_row()


def bamboo_row():
    directions = []
    for _ in range(32):
        directions.append(East)
    bamboo_cycle(directions, 500000000, False)

def bamboo_seed():
    plant(Entities.Bamboo)
    while measure() != 4:
        harvest()
        plant(Entities.Bamboo)


def bamboo_water(target, threshold):
    level = get_water()
    if level < threshold:
        amount = (target - level) * 4 // 1
        if amount < 1:
            amount = 1
        amount = min(amount, num_items(Items.Water) // 1)
        if amount > 0 and use_item(Items.Water, amount):  # ty: ignore[invalid-argument-type] # 整数桶数使用游戏Number。
            level += amount * 0.25
    return level


def bamboo_wait(began, growth, water, sweep):
    target = began + growth / (1 + 4 * water) + 0.05 - sweep
    while get_time() + 1 < target:
        do_a_flip()
    while get_time() < target:
        for _ in range(16):
            pass


def bamboo_cycle(directions, goal, single):
    inner = len(directions) - 1
    route = directions[:inner]
    last = directions[-1]
    lowest = 1
    bad = []
    for direction in route:
        move(direction)
        if get_ground_type() != Grounds.Soil:
            till()
        bamboo_seed()
        fill = 0.5
        if single:
            fill = 1
        lowest = min(lowest, bamboo_water(fill, fill))
        bad.append(False)
    move(last)
    began = get_time()
    growth = 4
    sweep = inner * 0.031
    for cycle in range(512):
        bamboo_wait(began, growth, lowest, sweep)
        hover(4)
        for i in range(inner):
            move(route[i])
            next_flower = measure()
            if next_flower != 8 and next_flower != 4:
                if single:
                    # 留到收割趟再换苗，先兑现本轮已经长出的竹子。
                    bad[i] = True
                else:
                    harvest()
                    bamboo_seed()
                    hover(4)
        move(last)
        began = get_time()
        bamboo_wait(began, 4, lowest, sweep)
        hover(8)
        growth = 3
        for direction in route:
            move(direction)
            growth = max(growth, measure() - 8)  # ty: ignore[unsupported-operator] # Bamboo的measure返回花节高度。
        growth = min(growth, 5)
        move(last)
        began = get_time()
        bamboo_wait(began, growth, lowest, sweep)
        hover(1)
        target = min(0.8, lowest / 0.97 + 0.1)
        threshold = target
        if single:
            target = 1
            threshold = 0.5
        new_lowest = 1
        growth = 3
        for i in range(inner):
            move(route[i])
            if num_items(Items.Bamboo) >= goal:
                quick_print("bamboo_done", cycle, get_time(), num_items(Items.Bamboo))
                clear()
                return
            if bad[i]:
                harvest()
                bamboo_seed()
                bad[i] = False
                growth = 4
            new_lowest = min(new_lowest, bamboo_water(target, threshold))
        move(last)
        began = get_time()
        lowest = new_lowest * 0.97
        if cycle % 8 == 0:
            quick_print("bamboo_cycle", cycle, get_time(), num_items(Items.Bamboo))


if __name__ == "__main__":
    lb_bamboo()
