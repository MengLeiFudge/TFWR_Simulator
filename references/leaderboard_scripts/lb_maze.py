from __builtins__ import *

directions = [North, East, South, West]
substance = 128  # 4x4迷宫需要的奇异物质数目
target_gold_count = 9863168


# 21:12.142
# 32*32，一半无人机贴左墙，另一半贴右墙

# 01:03.445
# 左下4x4 + 右下4x4，每格1个无人机

# 01:02.604
# 左下5x5，右下2x2，右下靠左3个1x1，每格1个无人机

# 01:00.683
# 左下5x5，每格1-2个无人机

# 00:57.395
# 左下4x4，每格2个无人机

# 00:53.454
# 左下4x4，每格2个无人机，疯狂撒奇异物质加快速度

# 00:51.378
# 左下4x4，每格2个无人机，最慢的5个格子兼职开迷宫

# 00:50.990
# 左下4x4，每格2个无人机，所有格子都兼职开迷宫
def main8():
    def sleep(tick):
        for i in range(tick - 3):
            pass

    # id  t0  t1  t2  t3
    # 00  01  02  04  08
    # 01      03  05  09
    # 02          06  10
    # 03          07  11
    # 04              12
    # 05              13
    # 06              14
    # 07              15
    def drone0():
        spawn_drone(drone1)
        spawn_drone(drone2)
        spawn_drone(drone4)
        spawn_drone(drone8)
        sleep(400)
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone1():
        spawn_drone(drone3)
        spawn_drone(drone5)
        spawn_drone(drone9)
        move(East)
        sleep(200)
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone2():
        spawn_drone(drone6)
        spawn_drone(drone10)
        move(East)
        move(East)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone3():
        spawn_drone(drone7)
        spawn_drone(drone11)
        move(West)
        sleep(200)
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone4():
        spawn_drone(drone12)
        move(North)
        sleep(200)
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone5():
        spawn_drone(drone13)
        move(North)
        move(East)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone6():
        spawn_drone(drone14)
        move(North)
        move(East)
        move(East)
        pass
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone7():
        spawn_drone(drone15)
        move(North)
        move(West)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone8():
        move(North)
        move(North)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone9():
        move(North)
        move(North)
        move(East)
        pass
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone10():
        move(North)
        move(North)
        move(East)
        move(East)
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone11():
        move(North)
        move(North)
        move(West)
        pass
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone12():
        move(South)
        sleep(200)
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone13():
        move(South)
        move(East)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone14():
        move(South)
        move(East)
        move(East)
        pass
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def drone15():
        move(South)
        move(West)
        pass
        pass
        spawn_drone(inf_use_and_harvest)
        inf_plant_and_use()

    def inf_plant_and_use():
        while num_items(Items.Gold) < 9863168:
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)

    def inf_use_and_harvest():
        while num_items(Items.Gold) < 9863168:
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            # 多次判断，确保301次才收
            if get_entity_type() == Entities.Treasure:
                if not use_item(Items.Weird_Substance, 128):
                    if get_entity_type() == Entities.Treasure:
                        if not use_item(Items.Weird_Substance, 128):
                            if get_entity_type() == Entities.Treasure:
                                harvest()

    set_world_size(4)
    drone0()


if __name__ == "__main__":
    main8()
