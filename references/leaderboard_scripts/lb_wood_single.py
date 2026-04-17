from __builtins__ import *


# Wood single 版本结论
# main1: 老 3x3 对角树 + 二选一伴生版本。文件内旧注释“3min40s”已不可信，
#        游戏更新后需要按当前版本重新测量。
# main2: 保留 main1 的核心 3x3 思路，补适合当前版本复盘的阶段日志，并把初始化
#        四次浇水合并为 use_item(Items.Water, 4)。这个版本先服务于“跑完就能读日志继续优化”。
# main3: 改成“按精确 companion 坐标即时落格”，不再把同一 x+y 的两格压成一个槽位。
#        只在“同一精确格且实体不同”时重掷，目标是砍掉 main2 里大量伪 conflict。
# main4: 改成 8x8 全图蛇形扫图。偶数奇偶格种树，另一半格子做动态 support。
#        每棵树维护自己的 active companion claim，support 格只按 active claim 改种，
#        目标是把“无伴生收获”从主路径里清出去。
# main5: 保留 main4 的 8x8 + active claim，但去掉树位常规浇水。
#        main4 日志里 `unready=0` 且 `water≈harvest`，说明“每次都浇水”大概率是纯成本。
# main6: 在 main5 基础上拒绝 `Entities.Carrot` companion。
#        `output.txt` 已出现 “没有种植 Entities.Carrot 所需的物品” 的真实警告，
#        说明 wood 路线里接受 Carrot claim 等于接受一个永远无法满足的 0 收益伴生。
# main7: Carrot 改成“按当前材料是否足够动态接受”，并在初始化时把所有 support 格预翻成 soil。
#        leaderboard 开局资源为 0，所以早期该拒绝；但当 `get_cost(Entities.Carrot)` 已经付得起时，
#        就不该像 main6 一样继续无脑重掷。同时把未来可能承担胡萝卜的格子一次性 `till()` 到位。
# main8: 在 main7 基础上给 sweep 加最小节奏控制。
#        main7 日志里后半段频繁出现 `d_harvest=32, d_unready=32` 这种半空回访，
#        说明当前不是单纯缺 companion，而是回访树位太快。
# main9: 保留 main5 的 8x8 checkerboard + always Carrot，但允许“当前 sweep 后半段的树位”
#        被前半段新树直接 claim 成 support。
#        目标是先砍掉一批 “target 落在树位上” 的无谓 reroll；只在目标树位位于当前 sweep 更后面时
#        才接受，避免把已经处理过的树位回滚成 support。
#        后验结论：这条线会把活树数压得太低，单机下不划算，保留做失败对照。
# main10: 回到 main5 的固定 tree/support 主路径，但引入“便宜补水”：
#         - 第一轮所有树位统一 `use_item(Items.Water, 4)`。
#         - 后续只有当某树位上一轮没熟时，下一次重种后才补 `use_item(Items.Water, 2)`。
#         目标是在不承担 main4 那种全量浇水成本的前提下，把 `unready` 和总 sweeps 压下去。
# main11: 在 main10 基础上不再追求 32 棵树满铺，而是挖掉 8 个均匀分散的树位，
#         用更稀的 tree/support 网络换更低的 reroll / support 冲突。
#         当前 8 个空洞坐标是：
#         `(0,0) (1,3) (2,6) (3,1) (4,4) (5,7) (6,2) (7,5)`
#         目标是牺牲少量树位，换更低的 `invalid` / `claim conflict` 和更短的均值。
#         当前阶段结论：
#         - 这版已做过游戏内实测，`5:40.868`，且与模拟器结果一致，可以作为当前可靠基线。
#         - 在已对齐的模拟器口径下，5-seed 均值约 `5:37.9`，2h 均值约 `5:39.0`。
#         - 一换洞、二换洞、随机 8 洞 sparse layout 搜索目前都还没稳定打过这组空洞。
#         - `Carrot allow` 仍然优于 `dynamic` / `always reject`；support 全 `soil` 仍然优于混合地块。
#         - 当前更像瓶颈的是 support 改写抖动，而不是树长不熟；探针里 `invalid / claim / support_replants`
#           明显偏高，而 `unready` 已经不算主矛盾。
# main12: 延续 main11 的 sparse-tree 思路，但把 8 个空洞重新排成更规整的斜向条带：
#         `(0,0) (0,2) (0,4) (0,6) (1,3) (2,6) (3,1) (5,7)`
#         目标不是进一步减少树位数量，而是让 support 空间更连续，减少 sweep 内改种抖动。
#         后验结论：
#         - fresh 5-seed 均值约 `5:46.3`，2h 均值约 `5:48.5`，比 main11 更慢。
#         - 这组“条带型”空洞布局不是更优解，保留做失败对照。
# main13: 根据 main11 probe，改成“非棋盘 20 树布局”。
#         坐标：
#         `(0,0) (0,2) (0,4) (0,6) (1,1) (1,5) (1,7) (2,2) (3,5) (3,7)
#           (4,0) (4,4) (4,6) (5,1) (5,7) (6,0) (6,2) (6,6) (7,3) (7,5)`
#         目标是直接降低 3 步 companion 命中 tree slot 的概率，把 `tree_reroll`
#         从 main11 那种接近 `1 reroll / 1 harvest` 的状态拉下来。
#         这版先保留 probe，看 fresh 5-seed 是否值得继续。
# main14: 回到 main11 的 24 树 checkerboard 基线，但只开放少量固定 buffer tree slot
#         给 later-sweep companion 临时占用。
#         当前 4 个 buffer tree slot：
#         `(6,0) (1,1) (6,4) (1,5)`
#         目标是吃到一部分 tree-slot accept 的收益，同时避免 main9 那种“整片树位都能降级”
#         导致的活树数明显下滑。
# main15: 把 tree/support 网络直接缩到 4x4 checkerboard。
#         草稿里的“双树轮转”按当前木头产量测算吞吐明显不够，所以这里保留“小地图降移动成本”
#         的方向，但把活树位稳定在 8 格，优先验证“紧凑地图 + 更低 support 抖动”
#         能不能压过 main11 的 8x8 稀疏布局。
#
# 当前建议：
# 1. 默认从 main11 继续优化。
# 2. main15 单 seed 约 `6:36.94`，明显慢于 main11 的 `5:46.64`，保留做失败对照。
# 3. wood_single 后续默认把“未伴生收获”视为策略错误，而不是正常波动。
# 4. 目前 sparse layout 本身已经接近局部最优；后续优先改 companion 接受/分配策略，减少 support 改写抖动。
# 5. 如果 companion 侧仍然压不下去，再回头做更大范围的 sparse layout 搜索，而不是继续做一换洞小修。
# 6. main11 / main15 后续探针的失败标准：如果 `tree_reroll` 或 `support_replant` 仍和 `harvest`
#    同量级增长，就说明当前主路径还在用大量动作换低效 companion，必须继续改主路径。


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
