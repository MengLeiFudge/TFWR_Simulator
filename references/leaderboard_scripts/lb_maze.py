from __builtins__ import *

directions = [North, East, South, West]
substance = 128  # 4x4迷宫需要的奇异物质数目
target_gold_count = 9863168


# 21:12.142
# 32*32，一半无人机贴左墙，另一半贴右墙
def main1():
    def check_treasure_left():
        idx = 0
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                harvest()
            elif get_entity_type() == Entities.Hedge:
                idx = (idx - 1) % 4
                while not can_move(directions[idx]):
                    idx = (idx + 1) % 4
                move(directions[idx])

    def check_treasure_right():
        idx = 0
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                harvest()
            elif get_entity_type() == Entities.Hedge:
                idx = (idx - 1) % 4
                while not can_move(directions[idx]):
                    idx = (idx + 1) % 4
                move(directions[idx])

    def check_treasure_right_main():
        idx = 0
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                harvest()
            elif get_entity_type() == Entities.Hedge:
                idx = (idx - 1) % 4
                while not can_move(directions[idx]):
                    idx = (idx + 1) % 4
                move(directions[idx])
            else:
                plant(Entities.Bush)
                use_item(Items.Weird_Substance, substance)

    global substance
    substance = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    for _ in range(15):
        spawn_drone(check_treasure_left)
        spawn_drone(check_treasure_right)
        move(North)
        move(East)
    spawn_drone(check_treasure_left)
    check_treasure_right_main()


# 01:03.445
# 左下4x4 + 右下4x4，每格1个无人机
def main2():
    def main2_sub():
        move(West)
        spawn_drone(main2_create_drowns_north)
        move(West)
        spawn_drone(main2_create_drowns_north)
        move(West)
        spawn_drone(main2_create_drowns_north)
        move(West)
        main2_create_drowns_north()

    def main2_create_drowns_north():
        spawn_drone(main2_drown_thread)
        move(North)
        spawn_drone(main2_drown_thread)
        move(North)
        spawn_drone(main2_drown_thread)
        move(North)
        main2_drown_thread()

    def main2_drown_thread():
        if (get_pos_x() == 0 and get_pos_y() == 0) or (get_pos_x() == 31 and get_pos_y() == 0):
            # 负责左下角、右下角生成迷宫的无人机
            for _ in range(1582):
                pass
            while num_items(Items.Gold) < target_gold_count:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()
                elif get_entity_type() != Entities.Hedge:
                    plant(Entities.Bush)
                    use_item(Items.Weird_Substance, substance)
                    # 如果刚好脚底下又是宝箱...
                    if get_entity_type() == Entities.Treasure:
                        use_item(Items.Weird_Substance, substance)
        else:
            # 其余无人机
            while num_items(Items.Gold) < target_gold_count:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()

    global substance
    substance = 4 * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    spawn_drone(main2_sub)
    spawn_drone(main2_create_drowns_north)
    move(East)
    spawn_drone(main2_create_drowns_north)
    move(East)
    spawn_drone(main2_create_drowns_north)
    move(East)
    main2_create_drowns_north()


# 01:02.604
# 左下5x5，右下2x2，右下靠左3个1x1，每格1个无人机
def main3():
    def main4_5x5_sub():
        global substance
        substance = 5 * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        spawn_drone(main4_5x5_sub2)
        move(East)
        spawn_drone(main4_5x5_sub2)
        move(East)
        spawn_drone(main4_5x5_sub2)
        move(East)
        spawn_drone(main4_5x5_sub2)
        move(East)
        main4_5x5_sub2()

    def main4_5x5_sub2():
        spawn_drone(main4_drown_thread_5x5)
        move(North)
        spawn_drone(main4_drown_thread_5x5)
        move(North)
        spawn_drone(main4_drown_thread_5x5)
        move(North)
        spawn_drone(main4_drown_thread_5x5)
        move(North)
        main4_drown_thread_5x5()

    def main4_drown_thread_5x5():
        if get_pos_x() == 0 and get_pos_y() == 0:
            # 负责左下角生成迷宫的无人机
            for _ in range(2383):
                pass
            while num_items(Items.Gold) < target_gold_count:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()
                        # quick_print("5x5收获金币，当前金币：", num_items(Items.Gold))
                elif get_entity_type() != Entities.Hedge:
                    plant(Entities.Bush)
                    use_item(Items.Weird_Substance, substance)
                    # 如果刚好脚底下又是宝箱...
                    if get_entity_type() == Entities.Treasure:
                        use_item(Items.Weird_Substance, substance)
        else:
            # 其余无人机
            while num_items(Items.Gold) < target_gold_count:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()
                        # quick_print("5x5收获金币，当前金币：", num_items(Items.Gold))

    def main4_2x2_sub():
        global substance
        substance = 2 * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        spawn_drone(main4_2x2_sub2)
        move(West)
        main4_2x2_sub2()

    def main4_2x2_sub2():
        spawn_drone(main4_drown_thread_2x2)
        move(North)
        main4_drown_thread_2x2()

    def main4_drown_thread_2x2():
        if get_pos_x() == 31 and get_pos_y() == 0:
            # 负责右下角生成迷宫的无人机
            # 9863168-240800(5x5收获一次的金币)=9622368
            while num_items(Items.Gold) < 9622368:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()
                        # quick_print("2x2收获金币，当前金币：", num_items(Items.Gold))
                elif get_entity_type() != Entities.Hedge:
                    plant(Entities.Bush)
                    use_item(Items.Weird_Substance, substance)
                    # 如果刚好脚底下又是宝箱...
                    if get_entity_type() == Entities.Treasure:
                        use_item(Items.Weird_Substance, substance)
        else:
            # 其余无人机
            # 9863168-240800(5x5收获一次的金币)=9622368
            while num_items(Items.Gold) < 9622368:
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        harvest()
                        # quick_print("2x2收获金币，当前金币：", num_items(Items.Gold))

    def main4_1x1_sub():
        global substance
        substance = 1 * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        spawn_drone(main4_1x1_sub2)
        spawn_drone(main4_1x1_sub3)
        main4_drown_thread_1x1()

    def main4_1x1_sub2():
        move(North)
        main4_drown_thread_1x1()

    def main4_1x1_sub3():
        move(West)
        main4_drown_thread_1x1()

    def main4_drown_thread_1x1():
        # 9863168-240800(5x5收获一次的金币)=9622368
        while num_items(Items.Gold) < 9622368:
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, substance)
            harvest()
            # quick_print("1x1收获金币，当前金币：", num_items(Items.Gold))

    spawn_drone(main4_5x5_sub)
    move(West)
    spawn_drone(main4_2x2_sub)
    move(West)
    move(West)
    main4_1x1_sub()


# 01:00.683
# 左下5x5，每格1-2个无人机
def main4():
    def main5_sub_col1():
        # 22221(*1111)
        spawn_drone(main5_sub_col1_sub)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        main5_drown_thread_single()

    def main5_sub_col1_sub():
        # 22221(21110)
        spawn_drone(main5_drown_thread_plant_bush)
        spawn_drone(main5_drown_thread_create_maze)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        main5_drown_thread_multiple()

    def main5_sub_col2():
        # 22211(*1111)
        spawn_drone(main5_sub_col2_sub)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_single)
        move(North)
        main5_drown_thread_single()

    def main5_sub_col2_sub():
        # 22211(21100)
        spawn_drone(main5_drown_thread_multiple)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        spawn_drone(main5_drown_thread_multiple)
        move(North)
        main5_drown_thread_multiple()

    def main5_sub_col345():
        # 11111
        spawn_drone(main5_drown_thread_single)
        move(North)
        spawn_drone(main5_drown_thread_single)
        move(North)
        spawn_drone(main5_drown_thread_single)
        move(North)
        spawn_drone(main5_drown_thread_single)
        move(North)
        main5_drown_thread_single()

    def main5_drown_thread_plant_bush():
        for _ in range(2383):
            pass
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                ws_count = num_items(Items.Weird_Substance)
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        if num_items(Items.Weird_Substance) == ws_count:
                            if get_entity_type() == Entities.Treasure:
                                harvest()
            elif get_entity_type() != Entities.Hedge:
                plant(Entities.Bush)

    def main5_drown_thread_create_maze():
        for _ in range(2383):
            pass
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                ws_count = num_items(Items.Weird_Substance)
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        if num_items(Items.Weird_Substance) == ws_count:
                            if get_entity_type() == Entities.Treasure:
                                harvest()
            elif get_entity_type() == Entities.Bush:
                use_item(Items.Weird_Substance, substance)
                # 如果刚好脚底下又是宝箱...
                if get_entity_type() == Entities.Treasure:
                    use_item(Items.Weird_Substance, substance)

    def main5_drown_thread_single():
        # quick_print("single", get_pos_x(), get_pos_y())
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                if not use_item(Items.Weird_Substance, substance):
                    harvest()

    def main5_drown_thread_multiple():
        # quick_print("multiple", get_pos_x(), get_pos_y())
        while num_items(Items.Gold) < target_gold_count:
            if get_entity_type() == Entities.Treasure:
                ws_count = num_items(Items.Weird_Substance)
                if get_entity_type() == Entities.Treasure:
                    if not use_item(Items.Weird_Substance, substance):
                        if num_items(Items.Weird_Substance) == ws_count:
                            if get_entity_type() == Entities.Treasure:
                                harvest()

    global substance
    substance = 5 * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    spawn_drone(main5_sub_col1)
    move(East)
    spawn_drone(main5_sub_col2)
    move(East)
    spawn_drone(main5_sub_col345)
    move(East)
    spawn_drone(main5_sub_col345)
    move(East)
    main5_sub_col345()


# 00:57.395
# 左下4x4，每格2个无人机
def main5():
    def main():
        global drone_id
        global level
        for i in range(-level, 0):
            level = level - 1
            spawn_drone(main)
            drone_id = drone_id + power2[i]
        in_place()

    def in_place():
        for i in range(drone_id % 4):
            move(North)
        for i in range(drone_id // 4):
            move(East)
        if drone_id == 0:
            for i in range(1187):
                pass
            while num_items(Items.Gold) < target_gold_count:
                start_maze()
        else:
            while num_items(Items.Gold) < target_gold_count:
                check_maze()

    def start_maze():
        if get_entity_type() == Entities.Grass:
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)
        check_maze()

    def check_maze():
        if get_entity_type() == Entities.Treasure:
            if not use_item(Items.Weird_Substance, 128):
                if get_entity_type() == Entities.Treasure:
                    harvest()

    drone_id = 0
    level = 5
    power2 = [0, 8, 4, 2, 1]
    main()


# 00:53.454
# 左下4x4，每格2个无人机，疯狂撒奇异物质加快速度
def main6():
    def full_produce():
        spawn_drone(col_no_produce)
        move(East)
        spawn_drone(col_no_produce)
        move(East)
        spawn_drone(col_no_produce)
        move(East)

        spawn_drone(inf_reset)
        move(North)
        spawn_drone(inf_reset)
        move(North)
        spawn_drone(inf_reset)
        move(North)
        inf_reset_and_harvest()

    def col_no_produce():
        spawn_drone(inf_reset)
        move(North)
        spawn_drone(inf_reset)
        move(North)
        spawn_drone(inf_reset)
        move(North)
        inf_reset()

    def full_produce_2():
        spawn_drone(col_produce)
        move(East)
        spawn_drone(col_produce)
        move(East)
        spawn_drone(col_produce)
        move(East)
        col_produce_2()

    def col_produce():
        spawn_drone(inf_reset_and_harvest)
        move(North)
        spawn_drone(inf_reset_and_harvest)
        move(North)
        spawn_drone(inf_reset_and_harvest)
        move(North)
        inf_reset_and_harvest()

    def col_produce_2():
        spawn_drone(inf_reset_and_harvest)
        move(North)
        spawn_drone(inf_reset_and_harvest)
        move(North)
        spawn_drone(inf_reset_and_harvest)
        move(North)
        inf_create_maze()

    def inf_create_maze():
        while num_items(Items.Gold) < 9863168:
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, 128)

    def inf_reset_and_harvest():
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
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            use_item(Items.Weird_Substance, 128)
            if get_entity_type() == Entities.Treasure:
                if not use_item(Items.Weird_Substance, 128) and get_entity_type() == Entities.Treasure:
                    harvest()

    def inf_reset():
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

    set_world_size(4)
    spawn_drone(full_produce)
    full_produce_2()


# 00:51.378
# 左下4x4，每格2个无人机，最慢的5个格子兼职开迷宫
def main7():
    def main():
        global drone_id
        global level
        for i in range(-level, 0):
            level = level - 1
            spawn_drone(main)
            drone_id = drone_id + power2[i]
        goto(drone_id // 4, drone_id % 4)
        spawn_drone(inf_use_and_harvest)
        if drone_id == 6 or drone_id == 9 or drone_id == 10 or drone_id == 11 or drone_id == 14:
            inf_plant_and_use()
        else:
            inf_use()

    def goto(tx, ty):
        size = get_world_size()
        half_size = size // 2
        x, y = get_pos_x(), get_pos_y()
        # x方向
        dx = (tx - x) % size
        if dx <= half_size:
            for _ in range(dx):
                move(East)
        else:
            for _ in range(size - dx):
                move(West)
        # y方向
        dy = (ty - y) % size
        if dy <= half_size:
            for _ in range(dy):
                move(North)
        else:
            for _ in range(size - dy):
                move(South)

    def plant_use_10():
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, 128)

    def use_10():
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

    def inf_plant_and_use():
        while num_items(Items.Gold) < 9863168:
            plant_use_10()

    def inf_use():
        while num_items(Items.Gold) < 9863168:
            use_10()
            use_10()

    def inf_use_and_harvest():
        while num_items(Items.Gold) < 9863168:
            use_10()
            use_10()
            if get_entity_type() == Entities.Treasure:
                if not use_item(Items.Weird_Substance, 128):
                    if get_entity_type() == Entities.Treasure:
                        if not use_item(Items.Weird_Substance, 128):
                            if get_entity_type() == Entities.Treasure:
                                harvest()  # 有概率不是300就收，但是无所谓

    set_world_size(4)
    drone_id = 0
    level = 4
    power2 = [8, 4, 2, 1]
    main()


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
