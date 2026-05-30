from __builtins__ import *

# 2:58.741
def lb_hay_single():
    count = 100000000
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

    # 1.收获 浇一桶水 循环刷伴生 北移
    harvest()
    # 真实验证 request 487/488：开局单桶比两桶和零桶更快。
    use_item(Items.Water)
    while True:
        ct, cp = get_companion()
        if ct != Entities.Bush or cp == p44:
            harvest()
            continue
        break
    move(North)

    # 2.收获 浇一桶水 循环刷伴生 南移
    harvest()
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
            # request 475/476/487/488 显示过度补水会变慢，循环内保持单桶。
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


if __name__ == "__main__":
    lb_hay_single()
