from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main2，32x32 每行一机，优先收高花瓣格。


def main1():
    for _ in range(31):
        spawn_drone(main1_drone_thread)
        move(North)
    main1_drone_thread()


def main1_drone_thread():
    # 暴力种植向日葵，加水保证一轮下来基本可以熟，好了就收
    # 初始化
    for _ in range(32):
        till()
        plant(Entities.Sunflower)
        use_item(Items.Water)
        move(East)
    # 获取时间不需要消耗tick？运行固定时间（约4:26）
    while get_tick_count() < 1620000:
        if can_harvest():
            harvest()
            plant(Entities.Sunflower)
            # magic number，最佳值在0.41-0.44，有随机性测不准
            if get_water() < 0.425:
                use_item(Items.Water)
        move(East)
    # 运行直到收尾
    while num_items(Items.Power) < 99500:
        if can_harvest():
            harvest()
            plant(Entities.Sunflower)
            if get_water() < 0.425:
                use_item(Items.Water)
        move(East)
    # 收尾不需要再种地
    while num_items(Items.Power) < 100003:
        if can_harvest():
            harvest()
        move(East)


# 每行 1 个无人机，每机维护自己行内 32 个 petal 值。
# 主循环优先收高花瓣格，收尾阶段再考虑放松阈值。
def main2():
    for _ in range(31):
        spawn_drone(main2_drone_thread)
        move(North)
    main2_drone_thread()


def main2_drone_thread():
    # 行内花瓣表：32 格，一维列表即可。起点 (x=0, y=drone_y)，沿 East 扫。
    petals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 初始化：每格 till + plant + water + measure，记录初始 petal。
    for idx in range(32):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Sunflower)
        # 初始灌满一次，保证同步成熟节奏；0.425 是 main1 已验证的门限。
        use_item(Items.Water)
        petals[idx] = measure()
        move(East)

    # 主循环：只收 petals==15 的。理由（drone.py/entities.py 反推）：
    # 1) sunflower.harvest 里 max_petals 是全场最大值；若收非最大，`get_boost=False`。
    # 2) 一旦 get_boost=False，grid.had_incorrect_sunflower_harvest 被置 True，
    #    **永久**拦截所有后续 boost（只会被 clear() 重置）。
    # 3) 花瓣数随机 7..15，1024 株里约 113 株是 15；只要随时还有人带 15，
    #    全场 max 就是 15，收 15 必拿 x8 倍率。
    # 4) 收非 15 的风险远大于收益，直接跳过即可。
    while num_items(Items.Power) < 99500:
        for idx in range(32):
            if petals[idx] == 15 and can_harvest():
                harvest()
                plant(Entities.Sunflower)
                if get_water() < 0.425:
                    use_item(Items.Water)
                petals[idx] = measure()
            elif not can_harvest():
                # 还没熟，顺手补水保持节奏；熟了但非 15 的格子就放着，等全场 15 株补充。
                if get_water() < 0.425:
                    use_item(Items.Water)
            move(East)

    # 收尾：目标将达，放松到任意成熟 15 花瓣都收；不再 plant/measure。
    while num_items(Items.Power) < 100003:
        if petals[get_pos_x()] == 15 and can_harvest():
            harvest()
        move(East)


if __name__ == "__main__":
    main2()
