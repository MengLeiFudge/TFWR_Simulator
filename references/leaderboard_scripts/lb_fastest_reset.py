from __builtins__ import *


def main():
    step1()
    step2()
    step3()
    step4()
    step5()


# 最开始的状态，点一些前期的东西直至解锁胡萝卜
def step1():
    # 速度1 20草
    while num_items(Items.Hay) < 20:
        harvest()
    unlock(Unlocks.Speed)

    # 扩张1 30草 1x1->1*3
    while num_items(Items.Hay) < 30:
        while not can_harvest():
            pass
        harvest()
    unlock(Unlocks.Expand)

    # 种植 50草
    while num_items(Items.Hay) < 50:
        while not can_harvest():
            pass
        harvest()
    unlock(Unlocks.Plant)

    # 扩张2 20木 1x3->3*3
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    while num_items(Items.Wood) < 20:
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
    unlock(Unlocks.Expand)

    # 胡萝卜 50木
    while num_items(Items.Wood) < 50:
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(North)
        while not can_harvest():
            pass
        harvest()
        plant(Entities.Bush)
        move(East)
    unlock(Unlocks.Carrots)


# 草、灌木、（树）、胡萝卜、（向日葵） 混种，速度升满，直至有1000能量
def step2():
    can_plant_tree = False
    can_use_water = False
    can_use_fertilizer = False
    can_plant_sunflower = False
    while num_items(Items.Power) < 1000:
        for _ in range(get_world_size()):
            if get_ground_type() == Grounds.Grassland:
                till()
            if can_use_water:
                water_needed = (min(0.75, num_items(Items.Water) / 100) - get_water()) // 0.25
                if water_needed > 0:
                    use_item(Items.Water, water_needed)
            if not can_harvest() and get_entity_type() != None:
                if can_use_fertilizer and get_entity_type() == Entities.Tree:
                    while not can_harvest():
                        if not use_item(Items.Fertilizer):
                            break
                    if not can_harvest():
                        move(North)
                        continue
                else:
                    move(North)
                    continue
            harvest()
            if can_plant_sunflower:
                if num_unlocked(Unlocks.Speed) < 5:
                    if num_items(Items.Power) < 100 and plant(Entities.Sunflower):
                        move(North)
                        continue
                else:
                    if can_plant_sunflower and plant(Entities.Sunflower):
                        move(North)
                        continue
            rand = random()
            if can_plant_tree:
                if rand < 0.25 and plant(Entities.Grass):
                    move(North)
                    continue
                if rand < 0.5 and plant(Entities.Bush):
                    move(North)
                    continue
                if rand < 0.75 and plant(Entities.Tree) and ((get_pos_x() + get_pos_y()) % 2 == 0):
                    move(North)
                    continue
                if plant(Entities.Carrot):
                    move(North)
                    continue
            else:
                if rand < 0.33 and plant(Entities.Grass):
                    move(North)
                    continue
                if rand < 0.66 and plant(Entities.Bush):
                    move(North)
                    continue
                if plant(Entities.Carrot):
                    move(North)
                    continue
            # 种最缺的
            hay = num_items(Items.Hay)
            wood = num_items(Items.Wood)
            carrot = num_items(Items.Carrot)
            if hay < wood and hay < carrot:
                if plant(Entities.Grass):
                    move(North)
                    continue
            elif wood < hay and wood < carrot:
                if can_plant_tree and ((get_pos_x() + get_pos_y()) % 2 == 0):
                    if plant(Entities.Tree):
                        move(North)
                        continue
                else:
                    if plant(Entities.Bush):
                        move(North)
                        continue
            else:
                if plant(Entities.Carrot):
                    move(North)
                    continue
            plant(Entities.Grass)
            move(North)
        move(East)
        unlock(Unlocks.Grass)
        unlock(Unlocks.Speed)
        unlock(Unlocks.Expand)
        unlock(Unlocks.Carrots)
        if unlock(Unlocks.Trees):
            can_plant_tree = True
        if unlock(Unlocks.Watering):
            can_use_water = True
        if unlock(Unlocks.Fertilizer):
            can_use_fertilizer = True
        if unlock(Unlocks.Sunflowers):
            can_plant_sunflower = True


# 无人机数目升级刷到最大（5级）
def step3():
    # 刷奇异物质到1200，解锁迷宫
    while num_items(Items.Weird_Substance) < 1300:
        for _ in range(get_world_size()):
            if (get_pos_x() + get_pos_y()) % 2 == 0:
                # 种树并用一次奇异物质
                if can_harvest():
                    harvest()
                    plant(Entities.Tree)
                    use_item(Items.Fertilizer)
                elif get_entity_type() == None:
                    plant(Entities.Tree)
                    use_item(Items.Fertilizer)
                move(North)
            else:
                # 种最缺的
                if not can_harvest():
                    plant(Entities.Grass)
                    move(North)
                    continue
                harvest()
                hay = num_items(Items.Hay)
                wood = num_items(Items.Wood)
                carrot = num_items(Items.Carrot)
                if hay < wood and hay < carrot:
                    plant(Entities.Grass)
                elif wood < hay and wood < carrot:
                    plant(Entities.Bush)
                else:
                    plant(Entities.Carrot)
        move(East)
        unlock(Unlocks.Grass)
        unlock(Unlocks.Trees)
        unlock(Unlocks.Carrots)
        unlock(Unlocks.Watering)
        unlock(Unlocks.Fertilizer)
    unlock(Unlocks.Mazes)
    # 刷奇异物质-刷金币-解锁更多无人机（能量不够要刷能量）
    idx = 0
    directions = [North, East, South, West]
    while num_items(Items.Gold) < 2000:
        if get_entity_type() == Entities.Treasure:
            harvest()
        elif get_entity_type() == Entities.Hedge:
            idx = (idx - 1) % 4
            while not can_move(directions[idx]):
                idx = (idx + 1) % 4
            move(directions[idx])
        else:
            harvest()
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1))
    unlock(Unlocks.Megafarm)


# 扩张升到最大（9级）
def step4():
    while True:
        do_a_flip()


# 解锁排行榜
def step5():
    while True:
        do_a_flip()


if __name__ == "__main__":
    main()
