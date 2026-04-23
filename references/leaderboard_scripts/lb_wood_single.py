from __builtins__ import *


# 详细版本结论、失败对照与候选策略见同名 md。
# 当前默认入口：main11；可靠基线 `5:40.868`，5-seed≈`5:37.9`，2h≈`5:39.0`。


# 旧版本，保留做对照
def main1(count=500000000):
    # 初始化，3x3大小刚好合适
    set_world_size(3)

    # 二选一说明（左下角(0,0)，右上角(2,2)）
    # x+y=2 x+y=3 Tree2
    # x+y=1 Tree3 x+y=3
    # Tree1 x+y=1 x+y=2

    # 二选一格子种什么东西（二选一格子指的是x+y格子走哪个）
    two_option_entity = [None, None, None, None]
    # 往哪里走可以从树到下一个二选一格子
    two_option_position1 = [North, North, North, North]
    # 往哪里走可以从二选一格子到下一个树
    two_option_position2 = [East, East, East, East]

    # 除了左下-右上对角线都种灌木，并将地块类型换为soil以便后续直接种植其他三种伴生
    plant(Entities.Tree)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    move(North)
    till()
    plant(Entities.Bush)
    move(North)
    till()
    plant(Entities.Bush)
    move(East)
    till()
    plant(Entities.Bush)
    move(South)
    plant(Entities.Tree)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    move(South)
    till()
    plant(Entities.Bush)
    move(East)
    till()
    plant(Entities.Bush)
    move(North)
    till()
    plant(Entities.Bush)
    move(North)
    plant(Entities.Tree)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    use_item(Items.Water)
    move(North)
    move(East)

    # 开始收割，一直往右上走
    while num_items(Items.Wood) < count:
        # 现在在(0,0)
        use_water_and_fertilizer()
        plant(Entities.Tree)
        while True:
            ct, (cx, cy) = get_companion()
            xy_sum = cx + cy
            # 树的伴生不可能是树，所以如果伴生出现在 cx == cy，说明这个是废伴生
            if cx == cy or two_option_entity[xy_sum] != None:
                harvest()
                plant(Entities.Tree)
                continue
            two_option_entity[xy_sum] = ct
            if cy - cx == 1 or cx - cy == 2:
                two_option_position1[xy_sum] = North
                two_option_position2[xy_sum] = East
            else:
                two_option_position1[xy_sum] = East
                two_option_position2[xy_sum] = North
            break
        # 移动到x+y=1的二选一格子，处理，移动到下一个树
        move(two_option_position1[1])
        ct = two_option_entity[1]
        if ct != None:
            if get_entity_type() != ct:
                harvest()
                plant(ct)
            two_option_entity[1] = None
        move(two_option_position2[1])
        quick_print(get_time())

        # 现在在(1,1)
        use_water_and_fertilizer()
        plant(Entities.Tree)
        while True:
            ct, (cx, cy) = get_companion()
            xy_sum = cx + cy
            # 树的伴生不可能是树，所以如果伴生出现在 cx == cy，说明这个是废伴生
            if cx == cy or two_option_entity[xy_sum] != None:
                harvest()
                plant(Entities.Tree)
                continue
            two_option_entity[xy_sum] = ct
            if cy - cx == 1 or cx - cy == 2:
                two_option_position1[xy_sum] = North
                two_option_position2[xy_sum] = East
            else:
                two_option_position1[xy_sum] = East
                two_option_position2[xy_sum] = North
            break
        # 移动到x+y=3的二选一格子，处理，移动到下一个树
        move(two_option_position1[3])
        ct = two_option_entity[3]
        if ct != None:
            if get_entity_type() != ct:
                harvest()
                plant(ct)
            two_option_entity[3] = None
        move(two_option_position2[3])
        quick_print(get_time())

        # 现在在(2,2)
        use_water_and_fertilizer()
        plant(Entities.Tree)
        while True:
            ct, (cx, cy) = get_companion()
            xy_sum = cx + cy
            # 树的伴生不可能是树，所以如果伴生出现在 cx == cy，说明这个是废伴生
            if cx == cy or two_option_entity[xy_sum] != None:
                harvest()
                plant(Entities.Tree)
                continue
            two_option_entity[xy_sum] = ct
            if cy - cx == 1 or cx - cy == 2:
                two_option_position1[xy_sum] = North
                two_option_position2[xy_sum] = East
            else:
                two_option_position1[xy_sum] = East
                two_option_position2[xy_sum] = North
            break
        # 移动到x+y=2的二选一格子，处理，移动到下一个树
        move(two_option_position1[2])
        ct = two_option_entity[2]
        if ct != None:
            if get_entity_type() != ct:
                harvest()
                plant(ct)
            two_option_entity[2] = None
        move(two_option_position2[2])
        quick_print(get_time())


def use_water_and_fertilizer():
    if not can_harvest():
        if get_water() < 0.95:
            use_item(Items.Water)
        used_fertilizer = False
        while not can_harvest():
            if use_item(Items.Fertilizer):
                used_fertilizer = True
        if used_fertilizer:
            use_item(Items.Weird_Substance)
    harvest()


def goto(tx, ty):
    size = get_world_size()
    half_size = size // 2
    x = get_pos_x()
    y = get_pos_y()

    dx = (tx - x) % size
    if dx <= half_size:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)

    dy = (ty - y) % size
    if dy <= half_size:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


def main2(count=500000000):
    set_world_size(3)

    # 二选一格子的目标植物，以及从树走到目标格/再走到下一棵树的方向
    two_option_entity = [None, None, None, None]
    two_option_position1 = [North, North, North, North]
    two_option_position2 = [East, East, East, East]

    # 统计信息：
    # invalid_diag[i]       第 i 棵树掷到对角线废伴生的次数
    # invalid_conflict[i]   第 i 棵树掷到已被占用的目标槽位次数
    # accepted_sum[s]       最终接受到 x+y=s 的次数
    invalid_diag = [0, 0, 0, 0]
    invalid_conflict = [0, 0, 0, 0]
    accepted_sum = [0, 0, 0, 0]
    water_use = [0]
    fertilizer_use = [0]
    weird_use = [0]
    cycle_count = [0]
    last_log_wood = [0]
    last_cycle_log = [0]
    sample_diag = [0, 0, 0, 0]
    sample_conflict = [0, 0, 0, 0]

    init_wood_field()
    quick_print("main2 init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        cycle_start_time = get_time()
        run_tree_step(
            1,
            1,
            two_option_entity,
            two_option_position1,
            two_option_position2,
            invalid_diag,
            invalid_conflict,
            accepted_sum,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage1_time = get_time()
        run_tree_step(
            3,
            2,
            two_option_entity,
            two_option_position1,
            two_option_position2,
            invalid_diag,
            invalid_conflict,
            accepted_sum,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage2_time = get_time()
        run_tree_step(
            2,
            3,
            two_option_entity,
            two_option_position1,
            two_option_position2,
            invalid_diag,
            invalid_conflict,
            accepted_sum,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage3_time = get_time()

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_main2_cycle(
            cycle_start_time,
            stage1_time,
            stage2_time,
            stage3_time,
            last_cycle_log,
            cycle_count,
            sample_diag,
            sample_conflict,
            invalid_diag,
            invalid_conflict,
        )
        maybe_log_main2_progress(
            last_log_wood,
            cycle_count,
            water_use,
            fertilizer_use,
            weird_use,
            invalid_diag,
            invalid_conflict,
            accepted_sum,
        )

    quick_print(
        "main2 done wood=", num_items(Items.Wood),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " water=", water_use[0],
        " fertilizer=", fertilizer_use[0],
        " weird=", weird_use[0],
        " diag1=", invalid_diag[1],
        " diag2=", invalid_diag[2],
        " diag3=", invalid_diag[3],
        " conflict1=", invalid_conflict[1],
        " conflict2=", invalid_conflict[2],
        " conflict3=", invalid_conflict[3],
        " sum1=", accepted_sum[1],
        " sum2=", accepted_sum[2],
        " sum3=", accepted_sum[3],
    )


def init_wood_field():
    # 左下角树
    plant(Entities.Tree)
    use_item(Items.Water, 4)
    move(North)

    # 左列上方两个灌木位
    till()
    plant(Entities.Bush)
    move(North)
    till()
    plant(Entities.Bush)
    move(East)

    # 中列上方灌木位
    till()
    plant(Entities.Bush)
    move(South)

    # 中间树
    plant(Entities.Tree)
    use_item(Items.Water, 4)
    move(South)

    # 中列下方和右列下方灌木位
    till()
    plant(Entities.Bush)
    move(East)
    till()
    plant(Entities.Bush)
    move(North)

    # 右列中间灌木位
    till()
    plant(Entities.Bush)
    move(North)

    # 右上树，然后回到 (0, 0)
    plant(Entities.Tree)
    use_item(Items.Water, 4)
    move(North)
    move(East)


def run_tree_step(
        target_sum,
        tree_index,
        two_option_entity,
        two_option_position1,
        two_option_position2,
        invalid_diag,
        invalid_conflict,
        accepted_sum,
        water_use,
        fertilizer_use,
        weird_use):
    use_water_and_fertilizer_logged(water_use, fertilizer_use, weird_use)
    plant(Entities.Tree)
    roll_tree_companion(
        tree_index,
        two_option_entity,
        two_option_position1,
        two_option_position2,
        invalid_diag,
        invalid_conflict,
        accepted_sum,
    )

    move(two_option_position1[target_sum])
    apply_two_option_tile(target_sum, two_option_entity)
    move(two_option_position2[target_sum])


def roll_tree_companion(
        tree_index,
        two_option_entity,
        two_option_position1,
        two_option_position2,
        invalid_diag,
        invalid_conflict,
        accepted_sum):
    while True:
        ct, (cx, cy) = get_companion()
        xy_sum = cx + cy

        # 树的伴生不可能是树，所以落在对角线时，这个伴生必然不能直接满足。
        if cx == cy:
            invalid_diag[tree_index] = invalid_diag[tree_index] + 1
            harvest()
            plant(Entities.Tree)
            continue

        # 三棵树共用三个 x+y 槽位；同一圈内如果撞槽，就继续重掷。
        if two_option_entity[xy_sum] != None:
            invalid_conflict[tree_index] = invalid_conflict[tree_index] + 1
            harvest()
            plant(Entities.Tree)
            continue

        two_option_entity[xy_sum] = ct
        accepted_sum[xy_sum] = accepted_sum[xy_sum] + 1

        if cy - cx == 1 or cx - cy == 2:
            two_option_position1[xy_sum] = North
            two_option_position2[xy_sum] = East
        else:
            two_option_position1[xy_sum] = East
            two_option_position2[xy_sum] = North
        break


def apply_two_option_tile(target_sum, two_option_entity):
    ct = two_option_entity[target_sum]
    if ct != None:
        if get_entity_type() != ct:
            harvest()
            plant(ct)
        two_option_entity[target_sum] = None


def maybe_log_main2_cycle(
        cycle_start_time,
        stage1_time,
        stage2_time,
        stage3_time,
        last_cycle_log,
        cycle_count,
        sample_diag,
        sample_conflict,
        invalid_diag,
        invalid_conflict):
    if cycle_count[0] < last_cycle_log[0] + 2000:
        return

    d_diag1 = invalid_diag[1] - sample_diag[1]
    d_diag2 = invalid_diag[2] - sample_diag[2]
    d_diag3 = invalid_diag[3] - sample_diag[3]
    d_conflict1 = invalid_conflict[1] - sample_conflict[1]
    d_conflict2 = invalid_conflict[2] - sample_conflict[2]
    d_conflict3 = invalid_conflict[3] - sample_conflict[3]

    quick_print(
        "main2 cycle cycles=", cycle_count[0],
        " wood=", num_items(Items.Wood),
        " time=", stage3_time,
        " loop=", stage3_time - cycle_start_time,
        " t1=", stage1_time - cycle_start_time,
        " t2=", stage2_time - stage1_time,
        " t3=", stage3_time - stage2_time,
        " d_diag1=", d_diag1,
        " d_diag2=", d_diag2,
        " d_diag3=", d_diag3,
        " d_conflict1=", d_conflict1,
        " d_conflict2=", d_conflict2,
        " d_conflict3=", d_conflict3,
    )

    last_cycle_log[0] = cycle_count[0]
    sample_diag[1] = invalid_diag[1]
    sample_diag[2] = invalid_diag[2]
    sample_diag[3] = invalid_diag[3]
    sample_conflict[1] = invalid_conflict[1]
    sample_conflict[2] = invalid_conflict[2]
    sample_conflict[3] = invalid_conflict[3]


def maybe_log_main2_progress(
        last_log_wood,
        cycle_count,
        water_use,
        fertilizer_use,
        weird_use,
        invalid_diag,
        invalid_conflict,
        accepted_sum):
    curr_wood = num_items(Items.Wood)
    if curr_wood >= last_log_wood[0] + 20000000:
        last_log_wood[0] = curr_wood
        quick_print(
            "main2 progress wood=", curr_wood,
            " time=", get_time(),
            " cycles=", cycle_count[0],
            " water=", water_use[0],
            " fertilizer=", fertilizer_use[0],
            " weird=", weird_use[0],
            " diag1=", invalid_diag[1],
            " diag2=", invalid_diag[2],
            " diag3=", invalid_diag[3],
            " conflict1=", invalid_conflict[1],
            " conflict2=", invalid_conflict[2],
            " conflict3=", invalid_conflict[3],
            " sum1=", accepted_sum[1],
            " sum2=", accepted_sum[2],
            " sum3=", accepted_sum[3],
        )


def use_water_and_fertilizer_logged(water_use, fertilizer_use, weird_use):
    if not can_harvest():
        if get_water() < 0.95:
            if use_item(Items.Water):
                water_use[0] = water_use[0] + 1
        used_fertilizer = False
        while not can_harvest():
            if use_item(Items.Fertilizer):
                fertilizer_use[0] = fertilizer_use[0] + 1
                used_fertilizer = True
        if used_fertilizer:
            if use_item(Items.Weird_Substance):
                weird_use[0] = weird_use[0] + 1
    harvest()


def main3(count=500000000):
    set_world_size(3)

    # planned_entity[x][y] 只记录“本圈已经承诺给某棵树的精确 companion 格”
    planned_entity = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]

    invalid_diag = [0, 0, 0, 0]
    exact_conflict = [0, 0, 0, 0]
    shared_exact = [0, 0, 0, 0]
    water_use = [0]
    fertilizer_use = [0]
    weird_use = [0]
    cycle_count = [0]
    last_log_wood = [0]
    last_cycle_log = [0]
    sample_diag = [0, 0, 0, 0]
    sample_conflict = [0, 0, 0, 0]
    sample_shared = [0, 0, 0, 0]

    init_wood_field()
    quick_print("main3 init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        clear_cycle_plan(planned_entity)
        cycle_start_time = get_time()

        run_tree_step_exact(
            1, 1,
            planned_entity,
            invalid_diag,
            exact_conflict,
            shared_exact,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage1_time = get_time()

        run_tree_step_exact(
            2, 2,
            planned_entity,
            invalid_diag,
            exact_conflict,
            shared_exact,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage2_time = get_time()

        run_tree_step_exact(
            0, 0,
            planned_entity,
            invalid_diag,
            exact_conflict,
            shared_exact,
            water_use,
            fertilizer_use,
            weird_use,
        )
        stage3_time = get_time()

        cycle_count[0] = cycle_count[0] + 1
        maybe_log_main3_cycle(
            cycle_start_time,
            stage1_time,
            stage2_time,
            stage3_time,
            last_cycle_log,
            cycle_count,
            sample_diag,
            sample_conflict,
            sample_shared,
            invalid_diag,
            exact_conflict,
            shared_exact,
        )
        maybe_log_main3_progress(
            last_log_wood,
            cycle_count,
            water_use,
            fertilizer_use,
            weird_use,
            invalid_diag,
            exact_conflict,
            shared_exact,
        )

    quick_print(
        "main3 done wood=", num_items(Items.Wood),
        " time=", get_time(),
        " cycles=", cycle_count[0],
        " water=", water_use[0],
        " fertilizer=", fertilizer_use[0],
        " weird=", weird_use[0],
        " diag1=", invalid_diag[1],
        " diag2=", invalid_diag[2],
        " diag3=", invalid_diag[3],
        " exact1=", exact_conflict[1],
        " exact2=", exact_conflict[2],
        " exact3=", exact_conflict[3],
        " share1=", shared_exact[1],
        " share2=", shared_exact[2],
        " share3=", shared_exact[3],
    )


def clear_cycle_plan(planned_entity):
    planned_entity[0][0] = None
    planned_entity[0][1] = None
    planned_entity[0][2] = None
    planned_entity[1][0] = None
    planned_entity[1][1] = None
    planned_entity[1][2] = None
    planned_entity[2][0] = None
    planned_entity[2][1] = None
    planned_entity[2][2] = None


def run_tree_step_exact(
        next_x,
        next_y,
        planned_entity,
        invalid_diag,
        exact_conflict,
        shared_exact,
        water_use,
        fertilizer_use,
        weird_use):
    tree_index = get_pos_x() + 1

    use_water_and_fertilizer_logged(water_use, fertilizer_use, weird_use)
    plant(Entities.Tree)
    ct, cx, cy = roll_tree_companion_exact(
        tree_index,
        planned_entity,
        invalid_diag,
        exact_conflict,
        shared_exact,
    )

    goto(cx, cy)
    if get_entity_type() != ct:
        harvest()
        plant(ct)
    goto(next_x, next_y)


def roll_tree_companion_exact(
        tree_index,
        planned_entity,
        invalid_diag,
        exact_conflict,
        shared_exact):
    while True:
        ct, (cx, cy) = get_companion()

        # 3x3 木头路线里，对角线三格是树位，不能把 companion 落在这里。
        if cx == cy:
            invalid_diag[tree_index] = invalid_diag[tree_index] + 1
            harvest()
            plant(Entities.Tree)
            continue

        planned = planned_entity[cx][cy]
        if planned != None and planned != ct:
            exact_conflict[tree_index] = exact_conflict[tree_index] + 1
            harvest()
            plant(Entities.Tree)
            continue

        if planned == ct:
            shared_exact[tree_index] = shared_exact[tree_index] + 1

        planned_entity[cx][cy] = ct
        return ct, cx, cy


def maybe_log_main3_cycle(
        cycle_start_time,
        stage1_time,
        stage2_time,
        stage3_time,
        last_cycle_log,
        cycle_count,
        sample_diag,
        sample_conflict,
        sample_shared,
        invalid_diag,
        exact_conflict,
        shared_exact):
    if cycle_count[0] < last_cycle_log[0] + 20:
        return

    quick_print(
        "main3 cycle cycles=", cycle_count[0],
        " wood=", num_items(Items.Wood),
        " time=", stage3_time,
        " loop=", stage3_time - cycle_start_time,
        " t1=", stage1_time - cycle_start_time,
        " t2=", stage2_time - stage1_time,
        " t3=", stage3_time - stage2_time,
        " d_diag1=", invalid_diag[1] - sample_diag[1],
        " d_diag2=", invalid_diag[2] - sample_diag[2],
        " d_diag3=", invalid_diag[3] - sample_diag[3],
        " d_exact1=", exact_conflict[1] - sample_conflict[1],
        " d_exact2=", exact_conflict[2] - sample_conflict[2],
        " d_exact3=", exact_conflict[3] - sample_conflict[3],
        " d_share1=", shared_exact[1] - sample_shared[1],
        " d_share2=", shared_exact[2] - sample_shared[2],
        " d_share3=", shared_exact[3] - sample_shared[3],
    )

    last_cycle_log[0] = cycle_count[0]
    sample_diag[1] = invalid_diag[1]
    sample_diag[2] = invalid_diag[2]
    sample_diag[3] = invalid_diag[3]
    sample_conflict[1] = exact_conflict[1]
    sample_conflict[2] = exact_conflict[2]
    sample_conflict[3] = exact_conflict[3]
    sample_shared[1] = shared_exact[1]
    sample_shared[2] = shared_exact[2]
    sample_shared[3] = shared_exact[3]


def maybe_log_main3_progress(
        last_log_wood,
        cycle_count,
        water_use,
        fertilizer_use,
        weird_use,
        invalid_diag,
        exact_conflict,
        shared_exact):
    curr_wood = num_items(Items.Wood)
    if curr_wood >= last_log_wood[0] + 20000000:
        last_log_wood[0] = curr_wood
        quick_print(
            "main3 progress wood=", curr_wood,
            " time=", get_time(),
            " cycles=", cycle_count[0],
            " water=", water_use[0],
            " fertilizer=", fertilizer_use[0],
            " weird=", weird_use[0],
            " diag1=", invalid_diag[1],
            " diag2=", invalid_diag[2],
            " diag3=", invalid_diag[3],
            " exact1=", exact_conflict[1],
            " exact2=", exact_conflict[2],
            " exact3=", exact_conflict[3],
            " share1=", shared_exact[1],
            " share2=", shared_exact[2],
            " share3=", shared_exact[3],
        )


def run_main45(count, log_prefix, enable_watering, reject_carrot_mode, min_sweep_time):
    set_world_size(8)
    init_main45_support_soil()

    # support_entity / support_count 记录当前仍被某些树依赖的 companion 格状态
    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)

    # 每棵树自己的当前 companion claim；只有树被成功收获后，旧 claim 才会释放
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)

    water_use = [0]
    sweep_count = [0]
    harvest_count = [0]
    unready_count = [0]
    invalid_tree_target = [0]
    claim_conflict = [0]
    shared_claim = [0]
    reject_carrot_count = [0]
    accept_grass = [0]
    accept_bush = [0]
    accept_carrot = [0]
    pacing_wait = [0]
    pacing_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    last_cycle_log = [0]
    sample_harvest = [0]
    sample_unready = [0]
    sample_invalid = [0]
    sample_conflict = [0]
    sample_shared = [0]
    sample_reject = [0]
    sample_accept_grass = [0]
    sample_accept_bush = [0]
    sample_accept_carrot = [0]

    quick_print(log_prefix, " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        sweep_start_time = get_time()
        prev_harvest = harvest_count[0]
        prev_unready = unready_count[0]
        run_main45_sweep(
            support_entity,
            support_count,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
            enable_watering,
            reject_carrot_mode,
            water_use,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
        )
        maybe_apply_sweep_pacing(
            min_sweep_time,
            sweep_start_time,
            harvest_count[0] - prev_harvest,
            unready_count[0] - prev_unready,
            pacing_wait,
            pacing_count,
        )
        sweep_count[0] = sweep_count[0] + 1
        sweep_end_time = get_time()

        maybe_log_main45_cycle(
            log_prefix,
            sweep_start_time,
            sweep_end_time,
            sweep_count,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            pacing_wait,
            pacing_count,
            sample_harvest,
            sample_unready,
            sample_invalid,
            sample_conflict,
            sample_shared,
            sample_reject,
            sample_accept_grass,
            sample_accept_bush,
            sample_accept_carrot,
            last_cycle_log,
        )
        maybe_log_main45_progress(
            log_prefix,
            last_log_wood,
            last_log_time,
            sweep_count,
            water_use,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            pacing_wait,
            pacing_count,
        )

    quick_print(
        log_prefix, " done wood=", num_items(Items.Wood),
        " time=", get_time(),
        " sweeps=", sweep_count[0],
        " water=", water_use[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " invalid=", invalid_tree_target[0],
        " claim_conflict=", claim_conflict[0],
        " shared=", shared_claim[0],
        " reject_carrot=", reject_carrot_count[0],
        " accept_grass=", accept_grass[0],
        " accept_bush=", accept_bush[0],
        " accept_carrot=", accept_carrot[0],
        " pacing_wait=", pacing_wait[0],
        " pacing_count=", pacing_count[0],
    )


def main4(count=500000000):
    run_main45(count, "main4", True, "allow", 0)


def main5(count=500000000):
    run_main45(count, "main5", False, "allow", 0)


def main6(count=500000000):
    run_main45(count, "main6", False, "always", 0)


def main7(count=500000000):
    run_main45(count, "main7", False, "dynamic", 0)


def main8(count=500000000):
    run_main45(count, "main8", False, "dynamic", 8.6)


def main9(count=500000000):
    set_world_size(8)
    init_main45_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    claim_owner_ids = create_list_grid(8)

    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)

    harvest_count = [0]
    unready_count = [0]
    invalid_tree_target = [0]
    claim_conflict = [0]
    shared_claim = [0]
    reject_carrot_count = [0]
    accept_grass = [0]
    accept_bush = [0]
    accept_carrot = [0]
    accepted_tree_slot = [0]
    blocked_tree_slot = [0]
    sweep_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    last_cycle_log = [0]
    sample_harvest = [0]
    sample_unready = [0]
    sample_invalid = [0]
    sample_conflict = [0]
    sample_shared = [0]
    sample_reject = [0]
    sample_accept_grass = [0]
    sample_accept_bush = [0]
    sample_accept_carrot = [0]
    sample_tree_slot = [0]
    sample_blocked_tree = [0]

    quick_print("main9", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        sweep_start_time = get_time()
        run_main9_sweep(
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
        )
        sweep_count[0] = sweep_count[0] + 1
        sweep_end_time = get_time()

        maybe_log_main9_cycle(
            sweep_start_time,
            sweep_end_time,
            sweep_count,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
            sample_harvest,
            sample_unready,
            sample_invalid,
            sample_conflict,
            sample_shared,
            sample_reject,
            sample_accept_grass,
            sample_accept_bush,
            sample_accept_carrot,
            sample_tree_slot,
            sample_blocked_tree,
            last_cycle_log,
        )
        maybe_log_main9_progress(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
        )

    quick_print(
        "main9", " done wood=", num_items(Items.Wood),
        " time=", get_time(),
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " invalid=", invalid_tree_target[0],
        " claim_conflict=", claim_conflict[0],
        " shared=", shared_claim[0],
        " reject_carrot=", reject_carrot_count[0],
        " accept_grass=", accept_grass[0],
        " accept_bush=", accept_bush[0],
        " accept_carrot=", accept_carrot[0],
        " tree_slot_claim=", accepted_tree_slot[0],
        " blocked_tree_slot=", blocked_tree_slot[0],
    )


def main10(count=500000000):
    set_world_size(8)
    init_main45_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True

    quick_print("main10", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(8):
            if y % 2 == 0:
                start_x = 0
                end_x = 7
                step = 1
                move_dir = East
            else:
                start_x = 7
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_main4_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main10_tree_companion(support_entity, support_count)
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main4_support_slot(x, y, support_entity, support_count)

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        first_cycle = False

    quick_print("main10", " done wood=", num_items(Items.Wood), " time=", get_time())


MAIN11_TREE_OFF = {
    (0, 0),
    (1, 3),
    (2, 6),
    (3, 1),
    (4, 4),
    (5, 7),
    (6, 2),
    (7, 5),
}

MAIN12_TREE_OFF = {
    (0, 0),
    (0, 2),
    (0, 4),
    (0, 6),
    (1, 3),
    (2, 6),
    (3, 1),
    (5, 7),
}

MAIN13_TREES = {
    (0, 0),
    (0, 2),
    (0, 4),
    (0, 6),
    (1, 1),
    (1, 5),
    (1, 7),
    (2, 2),
    (3, 5),
    (3, 7),
    (4, 0),
    (4, 4),
    (4, 6),
    (5, 1),
    (5, 7),
    (6, 0),
    (6, 2),
    (6, 6),
    (7, 3),
    (7, 5),
}

MAIN14_BUFFER_TREE_SLOTS = {
    (6, 0),
    (1, 1),
    (6, 4),
    (1, 5),
}


def main11(count=500000000):
    set_world_size(8)
    init_main11_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True
    sweep_count = [0]
    harvest_count = [0]
    tree_reroll_count = [0]
    support_replant_count = [0]
    support_keep_count = [0]
    orphan_support_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    sample_harvest = [0]
    sample_reroll = [0]
    sample_replant = [0]
    sample_keep = [0]
    sample_orphan = [0]

    quick_print("main11", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(8):
            if y % 2 == 0:
                start_x = 0
                end_x = 7
                step = 1
                move_dir = East
            else:
                start_x = 7
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_main11_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main11_tree_companion(
                        support_entity,
                        support_count,
                        tree_reroll_count,
                    )
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main11_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                        support_replant_count,
                        support_keep_count,
                        orphan_support_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        sweep_count[0] = sweep_count[0] + 1
        maybe_log_main11_probe(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            tree_reroll_count,
            support_replant_count,
            support_keep_count,
            orphan_support_count,
            sample_harvest,
            sample_reroll,
            sample_replant,
            sample_keep,
            sample_orphan,
        )
        first_cycle = False

    quick_print("main11", " done wood=", num_items(Items.Wood), " time=", get_time())


def main12(count=500000000):
    set_world_size(8)
    init_main12_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True

    quick_print("main12", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(8):
            if y % 2 == 0:
                start_x = 0
                end_x = 7
                step = 1
                move_dir = East
            else:
                start_x = 7
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_main12_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main12_tree_companion(support_entity, support_count)
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main4_support_slot(x, y, support_entity, support_count)

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        first_cycle = False

    quick_print("main12", " done wood=", num_items(Items.Wood), " time=", get_time())


def main13(count=500000000):
    set_world_size(8)
    init_main13_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True
    sweep_count = [0]
    harvest_count = [0]
    tree_reroll_count = [0]
    support_replant_count = [0]
    support_keep_count = [0]
    orphan_support_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    sample_harvest = [0]
    sample_reroll = [0]
    sample_replant = [0]
    sample_keep = [0]
    sample_orphan = [0]

    quick_print("main13", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(8):
            if y % 2 == 0:
                start_x = 0
                end_x = 7
                step = 1
                move_dir = East
            else:
                start_x = 7
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_main13_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main13_tree_companion(
                        support_entity,
                        support_count,
                        tree_reroll_count,
                    )
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main11_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                        support_replant_count,
                        support_keep_count,
                        orphan_support_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        sweep_count[0] = sweep_count[0] + 1
        maybe_log_main13_probe(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            tree_reroll_count,
            support_replant_count,
            support_keep_count,
            orphan_support_count,
            sample_harvest,
            sample_reroll,
            sample_replant,
            sample_keep,
            sample_orphan,
        )
        first_cycle = False

    quick_print("main13", " done wood=", num_items(Items.Wood), " time=", get_time())


def main14(count=500000000):
    set_world_size(8)
    init_main45_support_soil()

    support_entity = create_entity_grid(8)
    support_count = create_number_grid(8)
    claim_owner_ids = create_list_grid(8)

    tree_companion_entity = create_entity_grid(8)
    tree_companion_x = create_number_grid(8)
    tree_companion_y = create_number_grid(8)
    needs_water = create_number_grid(8)
    first_cycle = True

    harvest_count = [0]
    unready_count = [0]
    invalid_tree_target = [0]
    claim_conflict = [0]
    shared_claim = [0]
    reject_carrot_count = [0]
    accept_grass = [0]
    accept_bush = [0]
    accept_carrot = [0]
    accepted_tree_slot = [0]
    blocked_tree_slot = [0]
    sweep_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    last_cycle_log = [0]
    sample_harvest = [0]
    sample_unready = [0]
    sample_invalid = [0]
    sample_conflict = [0]
    sample_shared = [0]
    sample_reject = [0]
    sample_accept_grass = [0]
    sample_accept_bush = [0]
    sample_accept_carrot = [0]
    sample_tree_slot = [0]
    sample_blocked_tree = [0]

    quick_print("main14", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        sweep_start_time = get_time()
        run_main14_sweep(
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
            needs_water,
            first_cycle,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
        )
        sweep_count[0] = sweep_count[0] + 1
        first_cycle = False
        sweep_end_time = get_time()

        maybe_log_main14_cycle(
            sweep_start_time,
            sweep_end_time,
            sweep_count,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
            sample_harvest,
            sample_unready,
            sample_invalid,
            sample_conflict,
            sample_shared,
            sample_reject,
            sample_accept_grass,
            sample_accept_bush,
            sample_accept_carrot,
            sample_tree_slot,
            sample_blocked_tree,
            last_cycle_log,
        )
        maybe_log_main14_progress(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            unready_count,
            invalid_tree_target,
            claim_conflict,
            shared_claim,
            reject_carrot_count,
            accept_grass,
            accept_bush,
            accept_carrot,
            accepted_tree_slot,
            blocked_tree_slot,
        )

    quick_print(
        "main14", " done wood=", num_items(Items.Wood),
        " time=", get_time(),
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " invalid=", invalid_tree_target[0],
        " claim_conflict=", claim_conflict[0],
        " shared=", shared_claim[0],
        " reject_carrot=", reject_carrot_count[0],
        " accept_grass=", accept_grass[0],
        " accept_bush=", accept_bush[0],
        " accept_carrot=", accept_carrot[0],
        " tree_slot_claim=", accepted_tree_slot[0],
        " blocked_tree_slot=", blocked_tree_slot[0],
    )


def main15(count=500000000):
    set_world_size(4)
    init_main15_support_soil()

    support_entity = create_entity_grid(4)
    support_count = create_number_grid(4)
    tree_companion_entity = create_entity_grid(4)
    tree_companion_x = create_number_grid(4)
    tree_companion_y = create_number_grid(4)
    needs_water = create_number_grid(4)
    first_cycle = True
    sweep_count = [0]
    harvest_count = [0]
    tree_reroll_count = [0]
    support_replant_count = [0]
    support_keep_count = [0]
    orphan_support_count = [0]
    last_log_wood = [0]
    last_log_time = [0]
    sample_harvest = [0]
    sample_reroll = [0]
    sample_replant = [0]
    sample_keep = [0]
    sample_orphan = [0]

    quick_print("main15", " init_time=", get_time(), " wood=", num_items(Items.Wood))

    while num_items(Items.Wood) < count:
        for y in range(4):
            if y % 2 == 0:
                start_x = 0
                end_x = 3
                step = 1
                move_dir = East
            else:
                start_x = 3
                end_x = 0
                step = -1
                move_dir = West

            x = start_x
            while True:
                if is_main15_tree_slot(x, y):
                    entity = get_entity_type()
                    if entity == Entities.Tree:
                        if not can_harvest():
                            needs_water[x][y] = 1
                            if x == end_x:
                                break
                            move(move_dir)
                            x = x + step
                            continue
                        release_main10_tree_claim(
                            x,
                            y,
                            support_entity,
                            support_count,
                            tree_companion_entity,
                            tree_companion_x,
                            tree_companion_y,
                        )
                        harvest()
                        harvest_count[0] = harvest_count[0] + 1
                    elif entity != None:
                        harvest()

                    plant(Entities.Tree)
                    if first_cycle:
                        use_item(Items.Water, 4)
                    elif needs_water[x][y] > 0:
                        use_item(Items.Water, 2)
                        needs_water[x][y] = 0

                    ct, cx, cy = roll_main15_tree_companion(
                        support_entity,
                        support_count,
                        tree_reroll_count,
                    )
                    tree_companion_entity[x][y] = ct
                    tree_companion_x[x][y] = cx
                    tree_companion_y[x][y] = cy
                    support_entity[cx][cy] = ct
                    support_count[cx][cy] = support_count[cx][cy] + 1
                else:
                    process_main11_support_slot(
                        x,
                        y,
                        support_entity,
                        support_count,
                        support_replant_count,
                        support_keep_count,
                        orphan_support_count,
                    )

                if x == end_x:
                    break
                move(move_dir)
                x = x + step

            move(North)

        sweep_count[0] = sweep_count[0] + 1
        maybe_log_main15_probe(
            last_log_wood,
            last_log_time,
            sweep_count,
            harvest_count,
            tree_reroll_count,
            support_replant_count,
            support_keep_count,
            orphan_support_count,
            sample_harvest,
            sample_reroll,
            sample_replant,
            sample_keep,
            sample_orphan,
        )
        first_cycle = False

    quick_print("main15", " done wood=", num_items(Items.Wood), " time=", get_time())


def create_entity_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        ret.append(row)
    return ret


def create_number_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(0)
        ret.append(row)
    return ret


def create_list_grid(size):
    ret = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append([])
        ret.append(row)
    return ret


def is_main11_tree_slot(x, y):
    if (x, y) in MAIN11_TREE_OFF:
        return False
    return (x + y) % 2 == 0


def is_main12_tree_slot(x, y):
    if (x, y) in MAIN12_TREE_OFF:
        return False
    return (x + y) % 2 == 0


def is_main13_tree_slot(x, y):
    return (x, y) in MAIN13_TREES


def is_main15_tree_slot(x, y):
    return (x + y) % 2 == 0


def init_main11_support_soil():
    for y in range(8):
        if y % 2 == 0:
            end_x = 7
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_main11_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def init_main12_support_soil():
    for y in range(8):
        if y % 2 == 0:
            end_x = 7
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_main12_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def init_main13_support_soil():
    for y in range(8):
        if y % 2 == 0:
            end_x = 7
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_main13_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def init_main15_support_soil():
    for y in range(4):
        if y % 2 == 0:
            end_x = 3
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_main15_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def release_main10_tree_claim(
        x,
        y,
        support_entity,
        support_count,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y):
    ct = tree_companion_entity[x][y]
    if ct == None:
        return

    cx = tree_companion_x[x][y]
    cy = tree_companion_y[x][y]
    support_count[cx][cy] = support_count[cx][cy] - 1
    if support_count[cx][cy] <= 0:
        support_count[cx][cy] = 0
        support_entity[cx][cy] = None

    tree_companion_entity[x][y] = None
    tree_companion_x[x][y] = 0
    tree_companion_y[x][y] = 0


def roll_main10_tree_companion(support_entity, support_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main4_tree_slot(cx, cy):
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def roll_main11_tree_companion(support_entity, support_count, tree_reroll_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main11_tree_slot(cx, cy):
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def process_main11_support_slot(
        x,
        y,
        support_entity,
        support_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count):
    entity = get_entity_type()
    if support_count[x][y] <= 0:
        if entity != None:
            orphan_support_count[0] = orphan_support_count[0] + 1
        return

    ct = support_entity[x][y]
    if entity == ct:
        support_keep_count[0] = support_keep_count[0] + 1
        return

    if entity != None:
        support_replant_count[0] = support_replant_count[0] + 1
        harvest()

    plant(ct)


def maybe_log_main11_probe(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        tree_reroll_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count,
        sample_harvest,
        sample_reroll,
        sample_replant,
        sample_keep,
        sample_orphan):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main11", " probe wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " tree_reroll=", tree_reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
        " orphan_support=", orphan_support_count[0],
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_reroll=", tree_reroll_count[0] - sample_reroll[0],
        " d_replant=", support_replant_count[0] - sample_replant[0],
        " d_keep=", support_keep_count[0] - sample_keep[0],
        " d_orphan=", orphan_support_count[0] - sample_orphan[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time
    sample_harvest[0] = harvest_count[0]
    sample_reroll[0] = tree_reroll_count[0]
    sample_replant[0] = support_replant_count[0]
    sample_keep[0] = support_keep_count[0]
    sample_orphan[0] = orphan_support_count[0]


def maybe_log_main13_probe(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        tree_reroll_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count,
        sample_harvest,
        sample_reroll,
        sample_replant,
        sample_keep,
        sample_orphan):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main13", " probe wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " tree_reroll=", tree_reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
        " orphan_support=", orphan_support_count[0],
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_reroll=", tree_reroll_count[0] - sample_reroll[0],
        " d_replant=", support_replant_count[0] - sample_replant[0],
        " d_keep=", support_keep_count[0] - sample_keep[0],
        " d_orphan=", orphan_support_count[0] - sample_orphan[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time
    sample_harvest[0] = harvest_count[0]
    sample_reroll[0] = tree_reroll_count[0]
    sample_replant[0] = support_replant_count[0]
    sample_keep[0] = support_keep_count[0]
    sample_orphan[0] = orphan_support_count[0]


def maybe_log_main15_probe(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        tree_reroll_count,
        support_replant_count,
        support_keep_count,
        orphan_support_count,
        sample_harvest,
        sample_reroll,
        sample_replant,
        sample_keep,
        sample_orphan):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main15", " probe wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " tree_reroll=", tree_reroll_count[0],
        " support_replant=", support_replant_count[0],
        " support_keep=", support_keep_count[0],
        " orphan_support=", orphan_support_count[0],
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_reroll=", tree_reroll_count[0] - sample_reroll[0],
        " d_replant=", support_replant_count[0] - sample_replant[0],
        " d_keep=", support_keep_count[0] - sample_keep[0],
        " d_orphan=", orphan_support_count[0] - sample_orphan[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time
    sample_harvest[0] = harvest_count[0]
    sample_reroll[0] = tree_reroll_count[0]
    sample_replant[0] = support_replant_count[0]
    sample_keep[0] = support_keep_count[0]
    sample_orphan[0] = orphan_support_count[0]


def roll_main12_tree_companion(support_entity, support_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main12_tree_slot(cx, cy):
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def roll_main13_tree_companion(support_entity, support_count, tree_reroll_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main13_tree_slot(cx, cy):
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def roll_main15_tree_companion(support_entity, support_count, tree_reroll_count):
    while True:
        ct, (cx, cy) = get_companion()
        if is_main15_tree_slot(cx, cy):
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        if support_count[cx][cy] > 0 and support_entity[cx][cy] != ct:
            tree_reroll_count[0] = tree_reroll_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue
        return ct, cx, cy


def init_main45_support_soil():
    # support 格未来可能承担 Carrot companion，统一在初始化时翻成 soil。
    for y in range(8):
        if y % 2 == 0:
            end_x = 7
            step = 1
            move_dir = East
        else:
            end_x = 0
            step = -1
            move_dir = West

        x = get_pos_x()
        while True:
            if not is_main4_tree_slot(x, y) and get_ground_type() != Grounds.Soil:
                till()

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def maybe_apply_sweep_pacing(
        min_sweep_time,
        sweep_start_time,
        harvest_delta,
        unready_delta,
        pacing_wait,
        pacing_count):
    if min_sweep_time <= 0:
        return

    # 只在出现半空 sweep 时限速，避免无意义地拖慢前中期满产 sweep。
    if harvest_delta >= 64 or unready_delta <= 0:
        return

    wait_needed = min_sweep_time - (get_time() - sweep_start_time)
    if wait_needed <= 0:
        return

    target_time = sweep_start_time + min_sweep_time
    while get_time() < target_time:
        pass
    pacing_wait[0] = pacing_wait[0] + wait_needed
    pacing_count[0] = pacing_count[0] + 1


def run_main45_sweep(
        support_entity,
        support_count,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        enable_watering,
        reject_carrot_mode,
        water_use,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot):
    for y in range(8):
        if y % 2 == 0:
            start_x = 0
            end_x = 7
            step = 1
            move_dir = East
        else:
            start_x = 7
            end_x = 0
            step = -1
            move_dir = West

        x = start_x
        while True:
            if is_main4_tree_slot(x, y):
                process_main45_tree_slot(
                    x,
                    y,
                    support_entity,
                    support_count,
                    tree_companion_entity,
                    tree_companion_x,
                    tree_companion_y,
                    enable_watering,
                    reject_carrot_mode,
                    water_use,
                    harvest_count,
                    unready_count,
                    invalid_tree_target,
                    claim_conflict,
                    shared_claim,
                    reject_carrot_count,
                    accept_grass,
                    accept_bush,
                    accept_carrot,
                )
            else:
                process_main4_support_slot(x, y, support_entity, support_count)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def is_main4_tree_slot(x, y):
    return (x + y) % 2 == 0


def get_main9_owner_id(x, y):
    return y * 8 + x


def get_main9_sweep_index(x, y):
    if y % 2 == 0:
        return y * 8 + x
    return y * 8 + (7 - x)


def append_claim_owner(claim_owner_ids, cx, cy, owner_id):
    append(claim_owner_ids[cx][cy], owner_id)


def remove_claim_owner(claim_owner_ids, cx, cy, owner_id):
    owners = claim_owner_ids[cx][cy]
    for i in range(len(owners)):
        if owners[i] == owner_id:
            pop(owners, i)
            return


def can_accept_main9_tree_slot(current_x, current_y, target_x, target_y, target_entity, support_entity, support_count):
    if support_count[target_x][target_y] > 0:
        return support_entity[target_x][target_y] == target_entity
    return get_main9_sweep_index(target_x, target_y) > get_main9_sweep_index(current_x, current_y)


def is_main14_buffer_tree_slot(x, y):
    return (x, y) in MAIN14_BUFFER_TREE_SLOTS


def can_accept_main14_tree_slot(current_x, current_y, target_x, target_y, target_entity, support_entity, support_count):
    if not is_main14_buffer_tree_slot(target_x, target_y):
        return False
    if support_count[target_x][target_y] > 0:
        return support_entity[target_x][target_y] == target_entity
    return get_main9_sweep_index(target_x, target_y) > get_main9_sweep_index(current_x, current_y)


def run_main9_sweep(
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    for y in range(8):
        if y % 2 == 0:
            start_x = 0
            end_x = 7
            step = 1
            move_dir = East
        else:
            start_x = 7
            end_x = 0
            step = -1
            move_dir = West

        x = start_x
        while True:
            if is_main4_tree_slot(x, y):
                process_main9_tree_slot(
                    x,
                    y,
                    support_entity,
                    support_count,
                    claim_owner_ids,
                    tree_companion_entity,
                    tree_companion_x,
                    tree_companion_y,
                    harvest_count,
                    unready_count,
                    invalid_tree_target,
                    claim_conflict,
                    shared_claim,
                    reject_carrot_count,
                    accept_grass,
                    accept_bush,
                    accept_carrot,
                    accepted_tree_slot,
                    blocked_tree_slot,
                )
            else:
                process_main4_support_slot(x, y, support_entity, support_count)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def run_main14_sweep(
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        needs_water,
        first_cycle,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    for y in range(8):
        if y % 2 == 0:
            start_x = 0
            end_x = 7
            step = 1
            move_dir = East
        else:
            start_x = 7
            end_x = 0
            step = -1
            move_dir = West

        x = start_x
        while True:
            if is_main4_tree_slot(x, y):
                process_main14_tree_slot(
                    x,
                    y,
                    support_entity,
                    support_count,
                    claim_owner_ids,
                    tree_companion_entity,
                    tree_companion_x,
                    tree_companion_y,
                    needs_water,
                    first_cycle,
                    harvest_count,
                    unready_count,
                    invalid_tree_target,
                    claim_conflict,
                    shared_claim,
                    reject_carrot_count,
                    accept_grass,
                    accept_bush,
                    accept_carrot,
                    accepted_tree_slot,
                    blocked_tree_slot,
                )
            else:
                process_main4_support_slot(x, y, support_entity, support_count)

            if x == end_x:
                break
            move(move_dir)
            x = x + step

        move(North)


def process_main9_tree_slot(
        x,
        y,
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    if support_count[x][y] > 0:
        process_main14_tree_support_slot(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
            harvest_count,
            blocked_tree_slot,
        )
        return

    entity = get_entity_type()
    if entity == Entities.Tree:
        if not can_harvest():
            unready_count[0] = unready_count[0] + 1
            return

        release_main9_tree_claim(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
        )
        harvest()
        harvest_count[0] = harvest_count[0] + 1
    elif entity != None:
        harvest()

    plant(Entities.Tree)
    owner_id = get_main9_owner_id(x, y)
    ct, cx, cy = roll_main9_tree_companion(
        x,
        y,
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
    )
    tree_companion_entity[x][y] = ct
    tree_companion_x[x][y] = cx
    tree_companion_y[x][y] = cy
    support_entity[cx][cy] = ct
    support_count[cx][cy] = support_count[cx][cy] + 1
    append_claim_owner(claim_owner_ids, cx, cy, owner_id)


def process_main14_tree_slot(
        x,
        y,
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        needs_water,
        first_cycle,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    if support_count[x][y] > 0:
        process_main14_tree_support_slot(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
            needs_water,
            harvest_count,
            blocked_tree_slot,
        )
        return

    entity = get_entity_type()
    if entity == Entities.Tree:
        if not can_harvest():
            needs_water[x][y] = 1
            unready_count[0] = unready_count[0] + 1
            return

        release_main9_tree_claim(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
        )
        harvest()
        harvest_count[0] = harvest_count[0] + 1
    elif entity != None:
        harvest()

    plant(Entities.Tree)
    if first_cycle:
        use_item(Items.Water, 4)
    elif needs_water[x][y] > 0:
        use_item(Items.Water, 2)
        needs_water[x][y] = 0

    owner_id = get_main9_owner_id(x, y)
    ct, cx, cy = roll_main14_tree_companion(
        x,
        y,
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
    )
    tree_companion_entity[x][y] = ct
    tree_companion_x[x][y] = cx
    tree_companion_y[x][y] = cy
    support_entity[cx][cy] = ct
    support_count[cx][cy] = support_count[cx][cy] + 1
    append_claim_owner(claim_owner_ids, cx, cy, owner_id)


def process_main9_tree_support_slot(
        x,
        y,
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        harvest_count,
        blocked_tree_slot):
    ct = support_entity[x][y]
    entity = get_entity_type()

    if entity == ct:
        return

    if entity == Entities.Tree:
        if not can_harvest():
            blocked_tree_slot[0] = blocked_tree_slot[0] + 1
            return

        release_main9_tree_claim(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
        )
        harvest()
        harvest_count[0] = harvest_count[0] + 1
    elif entity != None:
        harvest()

    plant(ct)


def process_main14_tree_support_slot(
        x,
        y,
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        needs_water,
        harvest_count,
        blocked_tree_slot):
    ct = support_entity[x][y]
    entity = get_entity_type()

    if entity == ct:
        return

    if entity == Entities.Tree:
        if not can_harvest():
            needs_water[x][y] = 1
            blocked_tree_slot[0] = blocked_tree_slot[0] + 1
            return

        release_main9_tree_claim(
            x,
            y,
            support_entity,
            support_count,
            claim_owner_ids,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
        )
        harvest()
        harvest_count[0] = harvest_count[0] + 1
    elif entity != None:
        harvest()

    plant(ct)


def release_main9_tree_claim(
        x,
        y,
        support_entity,
        support_count,
        claim_owner_ids,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y):
    ct = tree_companion_entity[x][y]
    if ct == None:
        return

    cx = tree_companion_x[x][y]
    cy = tree_companion_y[x][y]
    owner_id = get_main9_owner_id(x, y)
    support_count[cx][cy] = support_count[cx][cy] - 1
    remove_claim_owner(claim_owner_ids, cx, cy, owner_id)
    if support_count[cx][cy] <= 0:
        support_count[cx][cy] = 0
        support_entity[cx][cy] = None

    tree_companion_entity[x][y] = None
    tree_companion_x[x][y] = 0
    tree_companion_y[x][y] = 0


def roll_main9_tree_companion(
        current_x,
        current_y,
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot):
    while True:
        ct, (cx, cy) = get_companion()

        if is_main4_tree_slot(cx, cy):
            if not can_accept_main9_tree_slot(current_x, current_y, cx, cy, ct, support_entity, support_count):
                invalid_tree_target[0] = invalid_tree_target[0] + 1
                harvest()
                plant(Entities.Tree)
                continue

            if support_count[cx][cy] > 0 and support_entity[cx][cy] == ct:
                shared_claim[0] = shared_claim[0] + 1
            accepted_tree_slot[0] = accepted_tree_slot[0] + 1
            record_main45_accept(ct, accept_grass, accept_bush, accept_carrot)
            return ct, cx, cy

        if should_reject_carrot(ct, "allow"):
            reject_carrot_count[0] = reject_carrot_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue

        if support_count[cx][cy] > 0:
            if support_entity[cx][cy] != ct:
                claim_conflict[0] = claim_conflict[0] + 1
                harvest()
                plant(Entities.Tree)
                continue
            shared_claim[0] = shared_claim[0] + 1

        record_main45_accept(ct, accept_grass, accept_bush, accept_carrot)
        return ct, cx, cy


def roll_main14_tree_companion(
        current_x,
        current_y,
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot):
    while True:
        ct, (cx, cy) = get_companion()

        if is_main4_tree_slot(cx, cy):
            if not can_accept_main14_tree_slot(current_x, current_y, cx, cy, ct, support_entity, support_count):
                invalid_tree_target[0] = invalid_tree_target[0] + 1
                harvest()
                plant(Entities.Tree)
                continue

            if support_count[cx][cy] > 0 and support_entity[cx][cy] == ct:
                shared_claim[0] = shared_claim[0] + 1
            accepted_tree_slot[0] = accepted_tree_slot[0] + 1
            record_main45_accept(ct, accept_grass, accept_bush, accept_carrot)
            return ct, cx, cy

        if should_reject_carrot(ct, "allow"):
            reject_carrot_count[0] = reject_carrot_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue

        if support_count[cx][cy] > 0:
            if support_entity[cx][cy] != ct:
                claim_conflict[0] = claim_conflict[0] + 1
                harvest()
                plant(Entities.Tree)
                continue
            shared_claim[0] = shared_claim[0] + 1

        record_main45_accept(ct, accept_grass, accept_bush, accept_carrot)
        return ct, cx, cy


def record_main45_accept(ct, accept_grass, accept_bush, accept_carrot):
    if ct == Entities.Grass:
        accept_grass[0] = accept_grass[0] + 1
    elif ct == Entities.Bush:
        accept_bush[0] = accept_bush[0] + 1
    elif ct == Entities.Carrot:
        accept_carrot[0] = accept_carrot[0] + 1


def process_main45_tree_slot(
        x,
        y,
        support_entity,
        support_count,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y,
        enable_watering,
        reject_carrot_mode,
        water_use,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot):
    entity = get_entity_type()
    if entity == Entities.Tree:
        if not can_harvest():
            unready_count[0] = unready_count[0] + 1
            return

        release_main4_tree_claim(
            x,
            y,
            support_entity,
            support_count,
            tree_companion_entity,
            tree_companion_x,
            tree_companion_y,
        )
        harvest()
        harvest_count[0] = harvest_count[0] + 1
    elif entity != None:
        harvest()

    if enable_watering and get_water() < 0.95:
        if use_item(Items.Water):
            water_use[0] = water_use[0] + 1

    plant(Entities.Tree)
    ct, cx, cy = roll_main4_tree_companion(
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_mode,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
    )
    tree_companion_entity[x][y] = ct
    tree_companion_x[x][y] = cx
    tree_companion_y[x][y] = cy
    support_entity[cx][cy] = ct
    support_count[cx][cy] = support_count[cx][cy] + 1


def release_main4_tree_claim(
        x,
        y,
        support_entity,
        support_count,
        tree_companion_entity,
        tree_companion_x,
        tree_companion_y):
    ct = tree_companion_entity[x][y]
    if ct == None:
        return

    cx = tree_companion_x[x][y]
    cy = tree_companion_y[x][y]
    support_count[cx][cy] = support_count[cx][cy] - 1
    if support_count[cx][cy] <= 0:
        support_count[cx][cy] = 0
        support_entity[cx][cy] = None

    tree_companion_entity[x][y] = None
    tree_companion_x[x][y] = 0
    tree_companion_y[x][y] = 0


def roll_main4_tree_companion(
        support_entity,
        support_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_mode,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot):
    while True:
        ct, (cx, cy) = get_companion()

        if is_main4_tree_slot(cx, cy):
            invalid_tree_target[0] = invalid_tree_target[0] + 1
            harvest()
            plant(Entities.Tree)
            continue

        if should_reject_carrot(ct, reject_carrot_mode):
            reject_carrot_count[0] = reject_carrot_count[0] + 1
            harvest()
            plant(Entities.Tree)
            continue

        if support_count[cx][cy] > 0:
            if support_entity[cx][cy] != ct:
                claim_conflict[0] = claim_conflict[0] + 1
                harvest()
                plant(Entities.Tree)
                continue
            shared_claim[0] = shared_claim[0] + 1

        if ct == Entities.Grass:
            accept_grass[0] = accept_grass[0] + 1
        elif ct == Entities.Bush:
            accept_bush[0] = accept_bush[0] + 1
        elif ct == Entities.Carrot:
            accept_carrot[0] = accept_carrot[0] + 1

        return ct, cx, cy


def should_reject_carrot(ct, reject_carrot_mode):
    if ct != Entities.Carrot:
        return False
    if reject_carrot_mode == "always":
        return True
    if reject_carrot_mode == "dynamic":
        return not can_afford_entity(Entities.Carrot)
    return False


def can_afford_entity(entity):
    cost = get_cost(entity)
    if cost == None:
        return True
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True


def process_main4_support_slot(x, y, support_entity, support_count):
    if support_count[x][y] <= 0:
        return

    ct = support_entity[x][y]
    if get_entity_type() == ct:
        return

    if get_entity_type() != None:
        harvest()

    plant(ct)


def maybe_log_main45_cycle(
        log_prefix,
        sweep_start_time,
        sweep_end_time,
        sweep_count,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        pacing_wait,
        pacing_count,
        sample_harvest,
        sample_unready,
        sample_invalid,
        sample_conflict,
        sample_shared,
        sample_reject,
        sample_accept_grass,
        sample_accept_bush,
        sample_accept_carrot,
        last_cycle_log):
    if sweep_count[0] < last_cycle_log[0] + 2:
        return

    quick_print(
        log_prefix, " cycle sweeps=", sweep_count[0],
        " wood=", num_items(Items.Wood),
        " time=", sweep_end_time,
        " sweep=", sweep_end_time - sweep_start_time,
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_unready=", unready_count[0] - sample_unready[0],
        " d_invalid=", invalid_tree_target[0] - sample_invalid[0],
        " d_claim=", claim_conflict[0] - sample_conflict[0],
        " d_shared=", shared_claim[0] - sample_shared[0],
        " d_reject_carrot=", reject_carrot_count[0] - sample_reject[0],
        " d_accept_grass=", accept_grass[0] - sample_accept_grass[0],
        " d_accept_bush=", accept_bush[0] - sample_accept_bush[0],
        " d_accept_carrot=", accept_carrot[0] - sample_accept_carrot[0],
        " pacing_wait=", pacing_wait[0],
        " pacing_count=", pacing_count[0],
    )

    last_cycle_log[0] = sweep_count[0]
    sample_harvest[0] = harvest_count[0]
    sample_unready[0] = unready_count[0]
    sample_invalid[0] = invalid_tree_target[0]
    sample_conflict[0] = claim_conflict[0]
    sample_shared[0] = shared_claim[0]
    sample_reject[0] = reject_carrot_count[0]
    sample_accept_grass[0] = accept_grass[0]
    sample_accept_bush[0] = accept_bush[0]
    sample_accept_carrot[0] = accept_carrot[0]


def maybe_log_main45_progress(
        log_prefix,
        last_log_wood,
        last_log_time,
        sweep_count,
        water_use,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        pacing_wait,
        pacing_count):
    curr_wood = num_items(Items.Wood)
    if curr_wood >= last_log_wood[0] + 20000000:
        curr_time = get_time()
        quick_print(
            log_prefix, " progress wood=", curr_wood,
            " time=", curr_time,
            " sweeps=", sweep_count[0],
            " water=", water_use[0],
            " harvest=", harvest_count[0],
            " unready=", unready_count[0],
            " invalid=", invalid_tree_target[0],
            " claim_conflict=", claim_conflict[0],
            " shared=", shared_claim[0],
            " reject_carrot=", reject_carrot_count[0],
            " accept_grass=", accept_grass[0],
            " accept_bush=", accept_bush[0],
            " accept_carrot=", accept_carrot[0],
            " dwood=", curr_wood - last_log_wood[0],
            " dt=", curr_time - last_log_time[0],
            " pacing_wait=", pacing_wait[0],
            " pacing_count=", pacing_count[0],
        )
        last_log_wood[0] = curr_wood
        last_log_time[0] = curr_time


def maybe_log_main9_cycle(
        sweep_start_time,
        sweep_end_time,
        sweep_count,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot,
        sample_harvest,
        sample_unready,
        sample_invalid,
        sample_conflict,
        sample_shared,
        sample_reject,
        sample_accept_grass,
        sample_accept_bush,
        sample_accept_carrot,
        sample_tree_slot,
        sample_blocked_tree,
        last_cycle_log):
    if sweep_count[0] < last_cycle_log[0] + 2:
        return

    quick_print(
        "main9", " cycle sweeps=", sweep_count[0],
        " wood=", num_items(Items.Wood),
        " time=", sweep_end_time,
        " sweep=", sweep_end_time - sweep_start_time,
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_unready=", unready_count[0] - sample_unready[0],
        " d_invalid=", invalid_tree_target[0] - sample_invalid[0],
        " d_claim=", claim_conflict[0] - sample_conflict[0],
        " d_shared=", shared_claim[0] - sample_shared[0],
        " d_reject_carrot=", reject_carrot_count[0] - sample_reject[0],
        " d_accept_grass=", accept_grass[0] - sample_accept_grass[0],
        " d_accept_bush=", accept_bush[0] - sample_accept_bush[0],
        " d_accept_carrot=", accept_carrot[0] - sample_accept_carrot[0],
        " d_tree_slot_claim=", accepted_tree_slot[0] - sample_tree_slot[0],
        " d_blocked_tree_slot=", blocked_tree_slot[0] - sample_blocked_tree[0],
    )

    last_cycle_log[0] = sweep_count[0]
    sample_harvest[0] = harvest_count[0]
    sample_unready[0] = unready_count[0]
    sample_invalid[0] = invalid_tree_target[0]
    sample_conflict[0] = claim_conflict[0]
    sample_shared[0] = shared_claim[0]
    sample_reject[0] = reject_carrot_count[0]
    sample_accept_grass[0] = accept_grass[0]
    sample_accept_bush[0] = accept_bush[0]
    sample_accept_carrot[0] = accept_carrot[0]
    sample_tree_slot[0] = accepted_tree_slot[0]
    sample_blocked_tree[0] = blocked_tree_slot[0]


def maybe_log_main9_progress(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main9", " progress wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " invalid=", invalid_tree_target[0],
        " claim_conflict=", claim_conflict[0],
        " shared=", shared_claim[0],
        " reject_carrot=", reject_carrot_count[0],
        " accept_grass=", accept_grass[0],
        " accept_bush=", accept_bush[0],
        " accept_carrot=", accept_carrot[0],
        " tree_slot_claim=", accepted_tree_slot[0],
        " blocked_tree_slot=", blocked_tree_slot[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time


def maybe_log_main14_cycle(
        sweep_start_time,
        sweep_end_time,
        sweep_count,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot,
        sample_harvest,
        sample_unready,
        sample_invalid,
        sample_conflict,
        sample_shared,
        sample_reject,
        sample_accept_grass,
        sample_accept_bush,
        sample_accept_carrot,
        sample_tree_slot,
        sample_blocked_tree,
        last_cycle_log):
    if sweep_count[0] < last_cycle_log[0] + 2:
        return

    quick_print(
        "main14", " cycle sweeps=", sweep_count[0],
        " wood=", num_items(Items.Wood),
        " time=", sweep_end_time,
        " sweep=", sweep_end_time - sweep_start_time,
        " d_harvest=", harvest_count[0] - sample_harvest[0],
        " d_unready=", unready_count[0] - sample_unready[0],
        " d_invalid=", invalid_tree_target[0] - sample_invalid[0],
        " d_claim=", claim_conflict[0] - sample_conflict[0],
        " d_shared=", shared_claim[0] - sample_shared[0],
        " d_reject_carrot=", reject_carrot_count[0] - sample_reject[0],
        " d_accept_grass=", accept_grass[0] - sample_accept_grass[0],
        " d_accept_bush=", accept_bush[0] - sample_accept_bush[0],
        " d_accept_carrot=", accept_carrot[0] - sample_accept_carrot[0],
        " d_tree_slot_claim=", accepted_tree_slot[0] - sample_tree_slot[0],
        " d_blocked_tree_slot=", blocked_tree_slot[0] - sample_blocked_tree[0],
    )

    last_cycle_log[0] = sweep_count[0]
    sample_harvest[0] = harvest_count[0]
    sample_unready[0] = unready_count[0]
    sample_invalid[0] = invalid_tree_target[0]
    sample_conflict[0] = claim_conflict[0]
    sample_shared[0] = shared_claim[0]
    sample_reject[0] = reject_carrot_count[0]
    sample_accept_grass[0] = accept_grass[0]
    sample_accept_bush[0] = accept_bush[0]
    sample_accept_carrot[0] = accept_carrot[0]
    sample_tree_slot[0] = accepted_tree_slot[0]
    sample_blocked_tree[0] = blocked_tree_slot[0]


def maybe_log_main14_progress(
        last_log_wood,
        last_log_time,
        sweep_count,
        harvest_count,
        unready_count,
        invalid_tree_target,
        claim_conflict,
        shared_claim,
        reject_carrot_count,
        accept_grass,
        accept_bush,
        accept_carrot,
        accepted_tree_slot,
        blocked_tree_slot):
    curr_wood = num_items(Items.Wood)
    if curr_wood < last_log_wood[0] + 20000000:
        return

    curr_time = get_time()
    quick_print(
        "main14", " progress wood=", curr_wood,
        " time=", curr_time,
        " sweeps=", sweep_count[0],
        " harvest=", harvest_count[0],
        " unready=", unready_count[0],
        " invalid=", invalid_tree_target[0],
        " claim_conflict=", claim_conflict[0],
        " shared=", shared_claim[0],
        " reject_carrot=", reject_carrot_count[0],
        " accept_grass=", accept_grass[0],
        " accept_bush=", accept_bush[0],
        " accept_carrot=", accept_carrot[0],
        " tree_slot_claim=", accepted_tree_slot[0],
        " blocked_tree_slot=", blocked_tree_slot[0],
        " dwood=", curr_wood - last_log_wood[0],
        " dt=", curr_time - last_log_time[0],
    )
    last_log_wood[0] = curr_wood
    last_log_time[0] = curr_time


if __name__ == "__main__":
    main11()
