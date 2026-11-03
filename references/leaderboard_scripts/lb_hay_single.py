from __builtins__ import *
# 完整轮时间：2:52.449（2026-11-03，build26385848，官方完整42轮，request256）。

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
    ct, cp = get_companion()
    while ct != Entities.Bush or cp == p44:
        harvest()
        ct, cp = get_companion()
    move(North)

    # 2.收获 浇一桶水 循环刷伴生 南移
    harvest()
    use_item(Items.Water)
    ct, cp = get_companion()
    while ct != Entities.Bush or cp == p43:
        harvest()
        ct, cp = get_companion()
    move(South)

    while True:
        # 3.检测状态 收获 检测数目 循环刷伴生 北移
        if not can_harvest():
            # 补水后继续检查成熟；超过等待上限则退出，避免提前收割。
            use_item(Items.Water)
            maturity_deadline = get_time() + 0.5
            while not can_harvest():
                if get_time() >= maturity_deadline:
                    return
            # 启用如下代码，以确定初始浇多少水
            # request 475/476/487/488 显示过度补水会变慢，循环内保持单桶。
            # while not can_harvest():
            #     while True:
            #         do_a_flip()
        harvest()
        if num_items(Items.Hay) >= count:
            break
        ct, cp = get_companion()
        while ct != Entities.Bush or cp == p44:
            harvest()
            ct, cp = get_companion()
        move(North)

        # 4.检测状态 收获 检测数目 循环刷伴生 南移
        if not can_harvest():
            use_item(Items.Water)
            maturity_deadline = get_time() + 0.5
            while not can_harvest():
                if get_time() >= maturity_deadline:
                    return
            # while not can_harvest():
            #     while True:
            #         do_a_flip()
        harvest()
        if num_items(Items.Hay) >= count:
            break
        ct, cp = get_companion()
        while ct != Entities.Bush or cp == p43:
            harvest()
            ct, cp = get_companion()
        move(South)


if __name__ == "__main__":
    lb_hay_single()
