from __builtins__ import *  # 导入所有内置函数和类


def first_plant_pumpkin(region_moves):  # 第一次种植南瓜的函数,接收移动路径列表
    broken_ls = []  # 初始化未成熟位置列表
    for mov in region_moves:  # 遍历所有移动方向
        if num_items(Items.Pumpkin) >= 200000000:  # 如果南瓜数量达到目标
            break  # 退出循环
        plant(Entities.Pumpkin)  # 种植南瓜
        move(mov)  # 按指定方向移动
    for mov in region_moves:  # 再次遍历所有移动方向
        if num_items(Items.Pumpkin) >= 200000000:  # 如果南瓜数量达到目标
            break  # 退出循环
        if get_entity_type() != Entities.Pumpkin:  # 如果当前位置不是南瓜
            plant(Entities.Pumpkin)  # 种植南瓜
        if get_water() < 0.85 and num_items(Items.Water) > 30:  # 如果含水量低于0.85且水足够
            use_item(Items.Water)  # 使用水
        if not can_harvest():  # 如果不能收获
            x_pos = get_pos_x()  # 获取当前x坐标
            y_pos = get_pos_y()  # 获取当前y坐标
            broken_ls.append((x_pos, y_pos))  # 将未成熟位置添加到列表
        move(mov)  # 按指定方向移动

    return broken_ls  # 返回未成熟位置列表


def normal_plant(region_moves, plant_time):  # 正常种植函数,接收移动路径和种植时间
    start_tick = get_tick_count()  # 记录开始时的时钟周期数
    broken_ls = first_plant_pumpkin(region_moves)  # 执行第一次种植,获取未成熟位置列表
    while len(broken_ls) > 0:  # 当还有未成熟位置时循环
        broken_ls_len = len(broken_ls)  # 获取未成熟位置数量
        broken_ls_new = copy_list(broken_ls)  # 复制未成熟位置列表
        for i in range(broken_ls_len):  # 遍历所有未成熟位置
            if num_items(Items.Pumpkin) >= 200000000:  # 如果南瓜数量达到目标
                break  # 退出循环
            dst = broken_ls[i]  # 获取目标位置
            goto(dst[0], dst[1])  # 移动到目标位置
            broken_ls_new_len = len(broken_ls_new)  # 获取新列表的长度
            if broken_ls_new_len == 1:  # 如果只剩一个未成熟位置
                if get_entity_type() == Entities.Dead_Pumpkin:  # 如果是死亡的南瓜
                    plant(Entities.Pumpkin)  # 重新种植南瓜
                if get_tick_count() - start_tick > plant_time * 0.95:  # 如果时间超过种植时间的95%
                    use_item(Items.Fertilizer)  # 使用肥料

                if can_harvest():  # 如果可以收获
                    broken_ls_new.remove(dst)  # 从新列表中移除该位置
                    continue  # 继续下一个位置
                if get_water() < 0.75:  # 如果含水量低于0.75
                    use_item(Items.Water)  # 使用水
                if can_harvest():  # 如果可以收获
                    broken_ls_new.remove(dst)  # 从新列表中移除该位置
                    continue  # 继续下一个位置
                if get_water() < 0.95 and num_items(Items.Water) > 100:  # 如果含水量低于0.95且水充足
                    use_item(Items.Water)  # 使用水
                if can_harvest():  # 如果可以收获
                    broken_ls_new.remove(dst)  # 从新列表中移除该位置
                    continue  # 继续下一个位置
            else:  # 如果有多个未成熟位置
                if get_entity_type() == Entities.Dead_Pumpkin:  # 如果是死亡的南瓜
                    plant(Entities.Pumpkin)  # 重新种植南瓜
                if get_water() < 0.8:  # 如果含水量低于0.8
                    use_item(Items.Water)  # 使用水
                if can_harvest():  # 如果可以收获
                    broken_ls_new.remove(dst)  # 从新列表中移除该位置
        broken_ls = broken_ls_new  # 更新未成熟位置列表
        if num_items(Items.Pumpkin) >= 200000000:  # 如果南瓜数量达到目标
            break  # 退出循环


def goto(tx, ty):  # 移动到指定坐标的函数
    size = get_world_size()  # 获取世界大小
    half_size = size // 2  # 计算世界大小的一半
    x, y = get_pos_x(), get_pos_y()  # 获取当前坐标
    # x方向
    dx = (tx - x) % size  # 计算x方向的距离(考虑环绕)
    if dx <= half_size:  # 如果向东移动更近
        for _ in range(dx):  # 循环移动dx次
            move(East)  # 向东移动
    else:  # 如果向西移动更近
        for _ in range(size - dx):  # 循环移动(size-dx)次
            move(West)  # 向西移动
    # y方向
    dy = (ty - y) % size  # 计算y方向的距离(考虑环绕)
    if dy <= half_size:  # 如果向北移动更近
        for _ in range(dy):  # 循环移动dy次
            move(North)  # 向北移动
    else:  # 如果向南移动更近
        for _ in range(size - dy):  # 循环移动(size-dy)次
            move(South)  # 向南移动


def copy_list(original_list):  # 复制列表的函数
    new_list = []  # 创建新的空列表
    for item in original_list:  # 遍历原列表的每个元素
        new_list.append(item)  # 将元素添加到新列表
    return new_list  # 返回新列表


def main1():
    # 定义移动路径
    region_moves = [North, East, South, West]
    # 定义种植时间
    plant_time = 800
    # 执行正常种植
    normal_plant(region_moves, plant_time)


# 多无人机 每 2 台种一块 6x6 有间隔
# 16台无人机 一人一块3x6 每台再分一个助手 负责另外一半


def pick_start_pos(l):
    # '''每块南瓜田的左下角'''
    pumpkin_len = 6
    unit_size = pumpkin_len + 1
    pos = []
    for i in range(l):
        for j in range(l):
            if (i % unit_size) == 0 and (j % unit_size) == 0:
                pos.append((i, j))
    return pos


area_len_num = 4  # 一边有几个区块
l = area_len_num * (6 + 1) - 1

set_world_size(l)


def do_subtask(t):
    x0, y0 = t
    pumpkin_len = 6

    def action(x, y):
        map.append((x, y))
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        pourwater(.5)

    map = []
    snake_traverse(l, x0, y0, x0 + pumpkin_len - 1 - 3, y0 + pumpkin_len - 1, action)
    round = 0
    while 1:
        round += 1
        growing_map = []
        for pos in map:
            goto2(l, pos[0], pos[1])
            if not can_harvest():
                plant(Entities.Pumpkin)
                growing_map.append(pos)
                if round > 3:
                    pourwater(.9)
                    if num_items(Items.Fertilizer) > 5 and len(map) == 1:
                        use_item(Items.Fertilizer)
                elif round > 1:
                    pourwater(.75)

        map = growing_map
        if len(map) == 0:
            # harvest()
            # round = 0
            break


def do_task(t):
    x0, y0 = t
    pumpkin_len = 6

    def action(x, y):
        map.append((x, y))
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        pourwater(.5)

    while num_items(Items.Pumpkin) < 200000000:
        sub_drone = spawn_drone(create_task(do_subtask, (x0 + 3, y0)))
        map = []
        snake_traverse(l, x0, y0, x0 + pumpkin_len - 1 - 3, y0 + pumpkin_len - 1, action)
        round = 0
        while 1:
            round += 1
            growing_map = []
            for pos in map:
                goto2(l, pos[0], pos[1])
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    growing_map.append(pos)
                    if round > 3:
                        pourwater(.9)
                        if num_items(Items.Fertilizer) > 5 and len(map) == 1:
                            use_item(Items.Fertilizer)
                    elif round > 1:
                        pourwater(.75)

            map = growing_map
            if len(map) == 0:
                while 1:
                    if has_finished(sub_drone):
                        harvest()
                        break
                round = 0
                break


def main2():
    all_start_pos = pick_start_pos(l)
    for pos in all_start_pos[1:]:
        spawn_drone(create_task(do_task, pos))
    while num_items(Items.Pumpkin) < 200000000:
        do_task(all_start_pos[0])


def create_task(fn, args):
    # '''
    # 为无人机创建一个任务, fn 为 任务函数, args 为任务参数
    # !注意此处不支持写不定参数
    # '''
    def _task():
        fn(args)

    return _task


def goto2(length, x, y):
    # '''利用边界传送特性来移动'''
    cx, cy = get_pos_x(), get_pos_y()

    dx = x - cx
    dy = y - cy

    if dx != 0:
        if dx > 0:
            if dx > length - dx:
                dx = dx - length
                x_dir = West
            else:
                x_dir = East
        else:
            if -dx > length + dx:
                dx = length + dx
                x_dir = East
            else:
                x_dir = West
        for _ in range(abs(dx)):
            move(x_dir)

    if dy != 0:
        if dy > 0:
            if dy > length - dy:
                dy = dy - length
                y_dir = South
            else:
                y_dir = North
        else:
            if -dy > length + dy:
                dy = length + dy
                y_dir = North
            else:
                y_dir = South
        for _ in range(abs(dy)):
            move(y_dir)


def snake_traverse(length, x0, y0, x1, y1, action):
    # '''蛇形遍历 从给定的初始位置开始'''
    goto2(length, x0, y0)
    for x in range(x0, x1 + 1):
        if (x - x0) % 2 == 0:
            # 从下到上
            for y in range(y0, y1 + 1):
                action(x, y)
                if y < y1:
                    move(North)
        else:
            # 从上到下
            for y in range(y1, y0 - 1, -1):
                action(x, y)
                if y > y0:
                    move(South)
        if x < x1:
            move(East)


def pourwater(p=.75):
    # '''浇水, 若地皮含水量不足p值,则浇到p为止'''
    while num_items(Items.Water) > 5 and get_water() < p:
        use_item(Items.Water)


# 当前默认多机入口：16 块 6x6 南瓜田并行波次。
# 更早版本和策略对照见同名 md。
def main3():
    # 16 块 6x6，每块 +1 缓冲 => 7*4 - 1 = 27。32 世界里剩下的 column/row 做边界缓冲。
    set_world_size(27)

    # 主机占 (0, 0) 这块；剩余 15 块用 spawn_drone（先 goto 再 spawn 确保子机起点正确）。
    for kx in range(4):
        for ky in range(4):
            if kx == 0 and ky == 0:
                continue
            main3_goto(kx * 7, ky * 7)
            spawn_drone(main3_region_thread)

    main3_goto(0, 0)
    main3_region_thread()


def main3_goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()
    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)
    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


# 每块子线程只靠“起点 == (x0, y0)”识别自己的 6x6 田。
# 从 (x0, y0) 开始蛇形扫 6x6：种 -> 轮询没熟的位置 -> 全熟后一起收。
def main3_region_thread():
    x0 = get_pos_x()
    y0 = get_pos_y()
    goal = 200000000
    while num_items(Items.Pumpkin) < goal:
        main3_plant_block(x0, y0)
        main3_wait_block(x0, y0)
        main3_harvest_block(x0, y0)


def main3_plant_block(x0, y0):
    # 初次种植：回到 (x0, y0)，6x6 全种。死南瓜 / 空格也填回 Pumpkin。
    main3_goto(x0, y0)
    for dy in range(6):
        if dy % 2 == 0:
            dirs = East
            end_dx = 5
            step = 1
        else:
            dirs = West
            end_dx = 0
            step = -1
        dx = get_pos_x() - x0
        while True:
            if get_ground_type() != Grounds.Soil:
                till()
            entity = get_entity_type()
            if entity != Entities.Pumpkin:
                if entity != None:
                    harvest()
                plant(Entities.Pumpkin)
            main3_water()
            if dx == end_dx:
                break
            move(dirs)
            dx = dx + step
        if dy < 5:
            move(North)


def main3_wait_block(x0, y0):
    # 等整块成熟；每轮回查 6x6 未熟格子，空/死格补种，否则补水。
    while True:
        pending = 0
        main3_goto(x0, y0)
        for dy in range(6):
            if dy % 2 == 0:
                dirs = East
                end_dx = 5
                step = 1
            else:
                dirs = West
                end_dx = 0
                step = -1
            dx = get_pos_x() - x0
            while True:
                entity = get_entity_type()
                if entity == Entities.Pumpkin:
                    if not can_harvest():
                        pending = pending + 1
                        main3_water()
                else:
                    if entity != None and entity != Entities.Dead_Pumpkin:
                        harvest()
                    plant(Entities.Pumpkin)
                    pending = pending + 1
                    main3_water()
                if dx == end_dx:
                    break
                move(dirs)
                dx = dx + step
            if dy < 5:
                move(North)
        if pending == 0:
            return


def main3_harvest_block(x0, y0):
    main3_goto(x0, y0)
    for dy in range(6):
        if dy % 2 == 0:
            dirs = East
            end_dx = 5
            step = 1
        else:
            dirs = West
            end_dx = 0
            step = -1
        dx = get_pos_x() - x0
        while True:
            if get_entity_type() == Entities.Pumpkin and can_harvest():
                harvest()
            if dx == end_dx:
                break
            move(dirs)
            dx = dx + step
        if dy < 5:
            move(North)


def main3_water():
    if get_water() < 0.5 and num_items(Items.Water) > 5:
        use_item(Items.Water)


if __name__ == "__main__":
    main3()
