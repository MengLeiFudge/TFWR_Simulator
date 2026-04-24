from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main10；可靠手跑记录见 md，后续继续围绕 refresh43/44 优化。

# 旧 3x3 对照路线


# fertilizer_min: 化肥数目大于此值时才使用化肥催熟


# (移动-种植-浇水-递归-返回)-收获
# ox = original_x_position
# oy = original_y_position

# 3min37s

# 3min12s

# 2min51s
def main4(count=100000000):
    set_world_size(5)

    # 选定目标格为(4,3)和(4,4)后，(1,1)和(2,1)不会是伴生位置，不用管
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(West)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(West)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)

    p44 = (4, 4)
    p43 = (4, 3)

    # 1.收获 浇两桶水 循环刷伴生 北移
    harvest()
    # 浇两桶水提提速，不能不浇也不能浇太多
    use_item(Items.Water)
    use_item(Items.Water)
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            continue
        break
    move(North)

    # 2.收获 浇两桶水 循环刷伴生 南移
    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p43:
            harvest()
            continue
        break
    move(South)

    while True:
        # 3.检测状态 收获 检测数目 循环刷伴生 北移
        if not can_harvest():
            # 如果因为速率不够而浇了一桶水，浇完之后草必定成熟
            use_item(Items.Water)
            # 启用如下代码，以确定初始浇多少水
            # 经过测试，含水量需要在0.68以上，才能确保可以直接收割
            # 对应开局浇水次数为2
            # while not can_harvest():
            #     while True:
            #         do_a_flip()
        harvest()
        if num_items(Items.Hay) >= count:
            break
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p44:
                harvest()
                continue
            break
        move(North)

        # 4.检测状态 收获 检测数目 循环刷伴生 南移
        if not can_harvest():
            use_item(Items.Water)
            # while not can_harvest():
            #     while True:
            #         do_a_flip()
        harvest()
        if num_items(Items.Hay) >= count:
            break
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p43:
                harvest()
                continue
            break
        move(South)


# 4x4双草轮转 + 日志，待测

# main4原策略 + 日志

# main6基础上增加慢局标记日志

# main7基础上增加补水后二次确认，避免偶发过早收获

# main8基础上放行“另一块目标草位 + Grass companion”

# main6原策略 + 批量浇水
def main10(count=100000000):
    set_world_size(5)
    quick_print("main10 start")

    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(West)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(West)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)

    p44 = (4, 4)
    p43 = (4, 3)
    water_count = 0
    refresh_43 = 0
    refresh_44 = 0
    last_log_hay = 0
    last_log_time = 0
    last_log_refresh_43 = 0
    last_log_refresh_44 = 0
    last_cycle_time = get_time()
    last_cycle_hay = num_items(Items.Hay)
    last_cycle_water = water_count
    last_cycle_refresh_43 = refresh_43
    last_cycle_refresh_44 = refresh_44
    cycle_count = 0

    quick_print("main10 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    harvest()
    use_item(Items.Water, 2)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        break
    quick_print("main10 stage1_time=", get_time(), " refresh43=", refresh_43)
    move(North)

    harvest()
    use_item(Items.Water, 2)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p43:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        break
    quick_print("main10 stage2_time=", get_time(), " refresh44=", refresh_44)
    move(South)

    while True:
        cycle_count = cycle_count + 1

        south_ready = can_harvest()
        south_water_before = get_water()
        south_water_after_use = south_water_before
        if not south_ready:
            use_item(Items.Water)
            water_count = water_count + 1
            south_water_after_use = get_water()
        harvest()
        south_water_after_harvest = get_water()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            curr_hay = num_items(Items.Hay)
            curr_time = get_time()
            quick_print(
                "main10 progress hay=", curr_hay,
                " time=", curr_time,
                " water=", water_count,
                " refresh43=", refresh_43,
                " refresh44=", refresh_44,
                " dh=", curr_hay - last_log_hay,
                " dt=", curr_time - last_log_time,
                " dr43=", refresh_43 - last_log_refresh_43,
                " dr44=", refresh_44 - last_log_refresh_44,
            )
            last_log_hay = curr_hay
            last_log_time = curr_time
            last_log_refresh_43 = refresh_43
            last_log_refresh_44 = refresh_44
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p44:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            break
        move(North)

        north_ready = can_harvest()
        north_water_before = get_water()
        north_water_after_use = north_water_before
        if not north_ready:
            use_item(Items.Water)
            water_count = water_count + 1
            north_water_after_use = get_water()
        harvest()
        north_water_after_harvest = get_water()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            curr_hay = num_items(Items.Hay)
            curr_time = get_time()
            quick_print(
                "main10 progress hay=", curr_hay,
                " time=", curr_time,
                " water=", water_count,
                " refresh43=", refresh_43,
                " refresh44=", refresh_44,
                " dh=", curr_hay - last_log_hay,
                " dt=", curr_time - last_log_time,
                " dr43=", refresh_43 - last_log_refresh_43,
                " dr44=", refresh_44 - last_log_refresh_44,
            )
            last_log_hay = curr_hay
            last_log_time = curr_time
            last_log_refresh_43 = refresh_43
            last_log_refresh_44 = refresh_44
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p43:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            break
        move(South)

        if cycle_count <= 12 or cycle_count % 50 == 0:
            curr_time = get_time()
            curr_hay = num_items(Items.Hay)
            quick_print(
                "main10 cycle=", cycle_count,
                " time=", curr_time,
                " hay=", curr_hay,
                " water=", water_count,
                " refresh43=", refresh_43,
                " refresh44=", refresh_44,
                " dtime=", curr_time - last_cycle_time,
                " dhay=", curr_hay - last_cycle_hay,
                " dwater=", water_count - last_cycle_water,
                " dr43=", refresh_43 - last_cycle_refresh_43,
                " dr44=", refresh_44 - last_cycle_refresh_44,
                " s_ready=", south_ready,
                " s_w0=", south_water_before,
                " s_w1=", south_water_after_use,
                " s_w2=", south_water_after_harvest,
                " n_ready=", north_ready,
                " n_w0=", north_water_before,
                " n_w1=", north_water_after_use,
                " n_w2=", north_water_after_harvest,
            )
            last_cycle_time = curr_time
            last_cycle_hay = curr_hay
            last_cycle_water = water_count
            last_cycle_refresh_43 = refresh_43
            last_cycle_refresh_44 = refresh_44

    quick_print(
        "main10 done hay=", num_items(Items.Hay),
        " time=", get_time(),
        " water=", water_count,
        " refresh43=", refresh_43,
        " refresh44=", refresh_44,
        " dh=", num_items(Items.Hay) - last_log_hay,
        " dt=", get_time() - last_log_time,
        " dr43=", refresh_43 - last_log_refresh_43,
        " dr44=", refresh_44 - last_log_refresh_44,
    )



if __name__ == "__main__":
    main10()
