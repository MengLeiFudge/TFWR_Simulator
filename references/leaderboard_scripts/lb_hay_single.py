from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main10；可靠手跑记录见 md，后续继续围绕 refresh43/44 优化。

# 旧 3x3 对照路线
def main1():
    set_world_size(3)

    entities = [
        Entities.Grass, Entities.Grass, Entities.Grass,
        Entities.Grass, Entities.Grass, Entities.Grass,
        Entities.Grass, Entities.Grass, Entities.Grass,
    ]
    states = [
        False, False, False,
        False, False, False,
        False, False, False,
    ]

    # (0,0)种一棵树（萝卜要木头），直接收获，因为此时收获的木头（喜好非草2560，喜好草409600）就够后续使用
    plant(Entities.Tree)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    harvest_with_fertilizer()

    # (1,1)开始收割草
    goto(1, 1)
    if get_ground_type() != Grounds.Grassland:
        till()
        plant(Entities.Grass)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    while num_items(Items.Hay) < 100000000:
        # 中心格极有可能遇到连续满足喜好的情况，所以速率必须拉满
        if get_water() < 0.95:
            use_item(Items.Water)
        plant_companion_then_back_and_harvest(1, 1, entities, states)


def harvest_without_fertilizer():
    while not can_harvest():
        pass
    harvest()


# fertilizer_min: 化肥数目大于此值时才使用化肥催熟
def harvest_with_fertilizer(fertilizer_min=0):
    used_fertilizer = False
    while not can_harvest():
        if num_items(Items.Fertilizer) > fertilizer_min:
            used_fertilizer = use_item(Items.Fertilizer)
    if used_fertilizer:
        use_item(Items.Weird_Substance)
    harvest()


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


# (移动-种植-浇水-递归-返回)-收获
# ox = original_x_position
# oy = original_y_position
def plant_companion_then_back_and_harvest(ox, oy, entities, states):
    (ct, (cx, cy)) = get_companion()
    idx = cx * 3 + cy
    # 只有喜好不一样，并且这一轮未被处理过，并且目标不是(1,1)，才需要移动过去种植新的植物
    if entities[idx] != ct and not states[idx] and not (cx == 1 and cy == 1):
        # 移动
        goto(cx, cy)
        # 种植
        harvest()
        if ct == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        elif ct == Entities.Grass and get_ground_type() != Grounds.Grassland:
            till()
        if plant(ct):
            entities[idx] = ct
            # 浇水
            while get_water() < 0.4:
                use_item(Items.Water)
            # 递归
            if ct == Entities.Grass:
                states[idx] = True
                plant_companion_then_back_and_harvest(cx, cy, entities, states)
                states[idx] = False
        # 返回
        goto(ox, oy)
    # 收获
    harvest_without_fertilizer()


# 3min37s
def main2():
    # 初始化，3x3大小刚好合适
    set_world_size(3)

    # 种一圈灌木（赌草的喜好伴生是灌木）
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(West)
    plant(Entities.Bush)
    move(North)

    # (1,1)开始收割草，赌草的喜好伴生是灌木
    while num_items(Items.Hay) < 100000000:
        if get_water() < 0.9:
            use_item(Items.Water)
        while get_companion()[0] != Entities.Bush:
            harvest()
        while not can_harvest():
            pass
        harvest()


# 3min12s
def main3(count=100000000):
    # 初始化，3x3大小刚好合适
    set_world_size(3)

    # 种一圈灌木，并将地块类型换为soil以便后续直接种植其他三种伴生
    plant(Entities.Bush)
    move(North)
    till()
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    till()
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    till()
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(West)
    till()
    plant(Entities.Bush)
    move(North)
    # 此时位置在(1,1)

    e01 = Entities.Bush  # (0,1)种植的实体
    e21 = Entities.Bush  # (2,1)种植的实体
    e10 = Entities.Bush  # (1,0)种植的实体
    e12 = Entities.Bush  # (1,2)种植的实体

    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)

    # 开始收割草
    while num_items(Items.Hay) < count:
        ct, (cx, cy) = get_companion()
        if cx == 1 or cy == 1:
            # 如果能一步到位，那么去种植伴生，然后返回
            if ct == Entities.Carrot and num_items(Items.Wood) < 512:
                # 种胡萝卜要草和木头。木头不足，重置
                harvest()
                continue
            if cx == 0:
                # 伴生在(0,1)
                if e01 != ct:
                    move(West)
                    harvest()
                    plant(ct)
                    e01 = ct
                    move(East)
            elif cx == 2:
                # 伴生在(2,1)
                if e21 != ct:
                    move(East)
                    harvest()
                    plant(ct)
                    e21 = ct
                    move(West)
            elif cy == 0:
                # 伴生在(1,0)
                if e10 != ct:
                    move(South)
                    harvest()
                    plant(ct)
                    e10 = ct
                    move(North)
            elif cy == 2:
                # 伴生在(1,2)
                if e12 != ct:
                    move(North)
                    harvest()
                    plant(ct)
                    e12 = ct
                    move(South)
        elif ct != Entities.Bush:
            # 如果伴生在角落并且伴生不是灌木，太远了不去，直接刷新
            harvest()
            continue
        # 等待收获
        if not can_harvest():
            use_item(Items.Water)
            while not can_harvest():
                pass
        # 收获
        harvest()


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
def main5(count=100000000):
    set_world_size(4)
    quick_print("main5 start")

    p30 = (3, 0)
    p31 = (3, 1)

    # 蛇形铺满 4x4，保留 (3,0) 和 (3,1) 两个草位做轮转目标
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
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
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(South)
    move(South)

    water_count = 0
    refresh_30 = 0
    refresh_31 = 0
    last_log_hay = 0

    quick_print("main5 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    # 先把下方草位刷到合格，再北移
    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p31:
            harvest()
            refresh_30 = refresh_30 + 1
            continue
        break
    move(North)

    # 再把上方草位刷到合格，再南移回起点
    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p30:
            harvest()
            refresh_31 = refresh_31 + 1
            continue
        break
    move(South)

    while True:
        # 下方草位：检测成熟 -> 收获 -> 刷伴生 -> 北移
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main5 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh30=", refresh_30, " refresh31=", refresh_31)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p31:
                harvest()
                refresh_30 = refresh_30 + 1
                continue
            break
        move(North)

        # 上方草位：检测成熟 -> 收获 -> 刷伴生 -> 南移
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main5 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh30=", refresh_30, " refresh31=", refresh_31)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p30:
                harvest()
                refresh_31 = refresh_31 + 1
                continue
            break
        move(South)

    quick_print("main5 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh30=", refresh_30, " refresh31=", refresh_31)


# main4原策略 + 日志
def main6(count=100000000):
    set_world_size(5)
    quick_print("main6 start")

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
    last_log_time = 0
    last_log_refresh_43 = 0
    last_log_refresh_44 = 0

    quick_print("main6 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    # 1.收获 浇两桶水 循环刷伴生 北移
    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        break
    quick_print("main6 stage1_time=", get_time(), " refresh43=", refresh_43)
    move(North)

    # 2.收获 浇两桶水 循环刷伴生 南移
    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p43:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        break
    quick_print("main6 stage2_time=", get_time(), " refresh44=", refresh_44)
    move(South)

    while True:
        # 3.检测状态 收获 检测数目 循环刷伴生 北移
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main6 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p44:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            break
        move(North)

        # 4.检测状态 收获 检测数目 循环刷伴生 南移
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main6 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p43:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            break
        move(South)

    quick_print("main6 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)


# main6基础上增加慢局标记日志
def main7(count=100000000):
    set_world_size(5)
    quick_print("main7 start")

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

    quick_print("main7 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        break
    quick_print("main7 stage1_time=", get_time(), " refresh43=", refresh_43)
    move(North)

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p43:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        break
    quick_print("main7 stage2_time=", get_time(), " refresh44=", refresh_44)
    move(South)

    while True:
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main7 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)
            if last_log_hay == 20070912 or last_log_hay == 20071424:
                if get_time() > 37.2:
                    quick_print("main7 slow checkpoint20 time=", get_time(), " refresh43=", refresh_43, " refresh44=", refresh_44)
            elif last_log_hay == 40141312 or last_log_hay == 40141824:
                if get_time() > 71.2:
                    quick_print("main7 slow checkpoint40 time=", get_time(), " refresh43=", refresh_43, " refresh44=", refresh_44)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p44:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            break
        move(North)

        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main7 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)
            if last_log_hay == 20070912 or last_log_hay == 20071424:
                if get_time() > 37.2:
                    quick_print("main7 slow checkpoint20 time=", get_time(), " refresh43=", refresh_43, " refresh44=", refresh_44)
            elif last_log_hay == 40141312 or last_log_hay == 40141824:
                if get_time() > 71.2:
                    quick_print("main7 slow checkpoint40 time=", get_time(), " refresh43=", refresh_43, " refresh44=", refresh_44)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p43:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            break
        move(South)

    quick_print("main7 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44)


# main7基础上增加补水后二次确认，避免偶发过早收获
def main8(count=100000000):
    set_world_size(5)
    quick_print("main8 start")

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
    late_wait_count = 0

    quick_print("main8 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        break
    quick_print("main8 stage1_time=", get_time(), " refresh43=", refresh_43)
    move(North)

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p43:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        break
    quick_print("main8 stage2_time=", get_time(), " refresh44=", refresh_44)
    move(South)

    while True:
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
            if not can_harvest():
                late_wait_count = late_wait_count + 1
                while not can_harvest():
                    pass
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main8 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p44:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            break
        move(North)

        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
            if not can_harvest():
                late_wait_count = late_wait_count + 1
                while not can_harvest():
                    pass
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main8 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count)
        while True:
            ct, cp = get_companion()
            if ct != Entities.Bush or cp == p43:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            break
        move(South)

    quick_print("main8 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count)


# main8基础上放行“另一块目标草位 + Grass companion”
def main9(count=100000000):
    set_world_size(5)
    quick_print("main9 start")

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
    late_wait_count = 0
    accept_other_grass_43 = 0
    accept_other_grass_44 = 0

    quick_print("main9 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if cp == p44:
            if ct == Entities.Grass:
                accept_other_grass_43 = accept_other_grass_43 + 1
                break
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        if ct != Entities.Bush:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        break
    quick_print("main9 stage1_time=", get_time(), " refresh43=", refresh_43, " other_grass43=", accept_other_grass_43)
    move(North)

    harvest()
    use_item(Items.Water)
    use_item(Items.Water)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if cp == p43:
            if ct == Entities.Grass:
                accept_other_grass_44 = accept_other_grass_44 + 1
                break
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        if ct != Entities.Bush:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        break
    quick_print("main9 stage2_time=", get_time(), " refresh44=", refresh_44, " other_grass44=", accept_other_grass_44)
    move(South)

    while True:
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
            if not can_harvest():
                late_wait_count = late_wait_count + 1
                while not can_harvest():
                    pass
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main9 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count, " other_grass43=", accept_other_grass_43, " other_grass44=", accept_other_grass_44)
        while True:
            ct, cp = get_companion()
            if cp == p44:
                if ct == Entities.Grass:
                    accept_other_grass_43 = accept_other_grass_43 + 1
                    break
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            if ct != Entities.Bush:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            break
        move(North)

        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
            if not can_harvest():
                late_wait_count = late_wait_count + 1
                while not can_harvest():
                    pass
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main9 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count, " other_grass43=", accept_other_grass_43, " other_grass44=", accept_other_grass_44)
        while True:
            ct, cp = get_companion()
            if cp == p43:
                if ct == Entities.Grass:
                    accept_other_grass_44 = accept_other_grass_44 + 1
                    break
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            if ct != Entities.Bush:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            break
        move(South)

    quick_print("main9 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " late_wait=", late_wait_count, " other_grass43=", accept_other_grass_43, " other_grass44=", accept_other_grass_44)


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


def main11(count=100000000):
    set_world_size(5)
    quick_print("main11 start")

    # 六个一步可达的动态改种位，预先翻成 soil，便于种 Bush / Tree / Carrot
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
    till()
    plant(Entities.Bush)   # (0,3)
    move(North)
    till()
    plant(Entities.Bush)   # (0,4)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    till()
    plant(Entities.Bush)   # (3,4)
    move(East)
    plant(Entities.Bush)
    move(South)
    till()
    plant(Entities.Bush)   # (3,3)
    move(West)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(East)
    plant(Entities.Bush)
    move(South)
    plant(Entities.Bush)
    move(South)
    till()
    plant(Entities.Bush)   # (4,0)
    move(East)
    plant(Entities.Bush)
    move(North)
    plant(Entities.Bush)
    move(North)
    till()
    plant(Entities.Bush)   # (4,2)
    move(North)

    p44 = (4, 4)
    p43 = (4, 3)

    e03 = Entities.Bush
    e04 = Entities.Bush
    e33 = Entities.Bush
    e34 = Entities.Bush
    e40 = Entities.Bush
    e42 = Entities.Bush

    water_count = 0
    refresh_43 = 0
    refresh_44 = 0
    adapt_43 = 0
    adapt_44 = 0
    last_log_hay = 0

    quick_print("main11 init_time=", get_time(), " pos=", get_pos_x(), ",", get_pos_y())

    harvest()
    use_item(Items.Water, 2)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if cp == p44:
            harvest()
            refresh_43 = refresh_43 + 1
            continue
        if cp == (3, 3):
            if e33 == ct:
                break
            move(West)
            harvest()
            plant(ct)
            e33 = ct
            adapt_43 = adapt_43 + 1
            move(East)
            break
        if cp == (4, 2):
            if e42 == ct:
                break
            move(South)
            harvest()
            plant(ct)
            e42 = ct
            adapt_43 = adapt_43 + 1
            move(North)
            break
        if cp == (0, 3):
            if e03 == ct:
                break
            move(East)
            harvest()
            plant(ct)
            e03 = ct
            adapt_43 = adapt_43 + 1
            move(West)
            break
        if ct == Entities.Bush:
            break
        harvest()
        refresh_43 = refresh_43 + 1
    quick_print("main11 stage1_time=", get_time(), " refresh43=", refresh_43, " adapt43=", adapt_43)
    move(North)

    harvest()
    use_item(Items.Water, 2)
    water_count = water_count + 2
    while True:
        ct, cp = get_companion()
        if cp == p43:
            harvest()
            refresh_44 = refresh_44 + 1
            continue
        if cp == (3, 4):
            if e34 == ct:
                break
            move(West)
            harvest()
            plant(ct)
            e34 = ct
            adapt_44 = adapt_44 + 1
            move(East)
            break
        if cp == (4, 0):
            if e40 == ct:
                break
            move(North)
            harvest()
            plant(ct)
            e40 = ct
            adapt_44 = adapt_44 + 1
            move(South)
            break
        if cp == (0, 4):
            if e04 == ct:
                break
            move(East)
            harvest()
            plant(ct)
            e04 = ct
            adapt_44 = adapt_44 + 1
            move(West)
            break
        if ct == Entities.Bush:
            break
        harvest()
        refresh_44 = refresh_44 + 1
    quick_print("main11 stage2_time=", get_time(), " refresh44=", refresh_44, " adapt44=", adapt_44)
    move(South)

    while True:
        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main11 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " adapt43=", adapt_43, " adapt44=", adapt_44)
        while True:
            ct, cp = get_companion()
            if cp == p44:
                harvest()
                refresh_43 = refresh_43 + 1
                continue
            if cp == (3, 3):
                if e33 == ct:
                    break
                move(West)
                harvest()
                plant(ct)
                e33 = ct
                adapt_43 = adapt_43 + 1
                move(East)
                break
            if cp == (4, 2):
                if e42 == ct:
                    break
                move(South)
                harvest()
                plant(ct)
                e42 = ct
                adapt_43 = adapt_43 + 1
                move(North)
                break
            if cp == (0, 3):
                if e03 == ct:
                    break
                move(East)
                harvest()
                plant(ct)
                e03 = ct
                adapt_43 = adapt_43 + 1
                move(West)
                break
            if ct == Entities.Bush:
                break
            harvest()
            refresh_43 = refresh_43 + 1
        move(North)

        if not can_harvest():
            use_item(Items.Water)
            water_count = water_count + 1
        harvest()
        if num_items(Items.Hay) >= count:
            break
        if num_items(Items.Hay) >= last_log_hay + 20000000:
            last_log_hay = num_items(Items.Hay)
            quick_print("main11 progress hay=", last_log_hay, " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " adapt43=", adapt_43, " adapt44=", adapt_44)
        while True:
            ct, cp = get_companion()
            if cp == p43:
                harvest()
                refresh_44 = refresh_44 + 1
                continue
            if cp == (3, 4):
                if e34 == ct:
                    break
                move(West)
                harvest()
                plant(ct)
                e34 = ct
                adapt_44 = adapt_44 + 1
                move(East)
                break
            if cp == (4, 0):
                if e40 == ct:
                    break
                move(North)
                harvest()
                plant(ct)
                e40 = ct
                adapt_44 = adapt_44 + 1
                move(South)
                break
            if cp == (0, 4):
                if e04 == ct:
                    break
                move(East)
                harvest()
                plant(ct)
                e04 = ct
                adapt_44 = adapt_44 + 1
                move(West)
                break
            if ct == Entities.Bush:
                break
            harvest()
            refresh_44 = refresh_44 + 1
        move(South)

    quick_print("main11 done hay=", num_items(Items.Hay), " time=", get_time(), " water=", water_count, " refresh43=", refresh_43, " refresh44=", refresh_44, " adapt43=", adapt_43, " adapt44=", adapt_44)


if __name__ == "__main__":
    main10()
