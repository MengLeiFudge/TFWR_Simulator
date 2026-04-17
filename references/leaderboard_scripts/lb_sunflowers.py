from __builtins__ import *


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


if __name__ == "__main__":
    main1()
