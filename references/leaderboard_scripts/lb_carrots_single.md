# lb_carrots_single

## 榜单目标

- 目标资源：`Items.Carrot`
- 单机路线
- 当前脚本默认目标数量为 `100000000`

## 收益机制说明

- 你补充的当前关键事实是：
  - 胡萝卜伴生命中时，产出是 `160` 倍
  - 因此 leaderboard 语境下的胡萝卜，没伴生基本就等于没收益
- 这意味着单榜胡萝卜不是“纯吞吐小图榜”，而是“想办法在单机上兑现 companion 的榜”。
- 2026-05-31 纠偏：
  - `gamesave/__builtins__.py` 文档显示 `Entities.Grass` 可种在 `grassland or soil`
  - 所以旧结论“胡萝卜的 Grass companion 物理上种不出来”不成立
  - 胡萝卜不会抽到胡萝卜 companion，因此可落地候选是 `Grass / Bush / Tree`
  - 真正的问题是同一 support 坐标一次只能放一种实体；静态单类型 support 只能吃一种类型概率
  - 后续要评估的是“多类型承接成本是否低于 reroll 成本”，而不是再按地块冲突直接排除 Grass

## 当前基线

- 当前默认入口：`lb_carrots_single()`
- 旧可靠基线是 `main3()`：外部 `Save0/carrot.py` 修真实目标后的 5x5 单列轮转胡萝卜；请求 `287` 两轮约 `23:49.323`。
- 当前版本复跑时间：2026-06-09 请求 `682` 完整统计 `finished=true runs=14 average=8:37.719`；最快完整轮 `8:31.992`。
- 上一个静态 Bush-only 相邻 2x2 版本：2026-05-31 请求 `622` 完整统计 `finished=true runs=14 average=8:44.832`；最快完整轮 `8:32.070`。
- 短跑验证：2026-05-31 请求 `621` 有效四轮 `8:44.335` / `8:51.718` / `8:44.099` / `8:45.799`，稳定均值 `8:46.488`；后续 `finished=false` 取消摘要不作为成绩。
- 上一个分散四锚点当前复跑：2026-05-30 请求 `611` 有效两轮 `9:46.899` / `9:42.343`，稳定均值 `9:44.621`；后续 `finished=false` 取消摘要不作为成绩。
- 历史完整统计：请求 `494` 完整统计 `13` 轮均值 `9:42.804`，请求 `495` 复跑完整统计 `13` 轮均值 `9:44.049`。
- 当前 companion 路线：5x5 上只保留 `(2,1)/(3,1)/(3,2)/(2,2)` 相邻 2x2 四个胡萝卜锚点；其余格初始预置 `Bush` 支撑，并维护 `support_entity` 记住每个非锚点 support 的当前类型。锚点直接接受已知类型匹配的非锚点 companion；若类型不匹配且距离 `<=2`，当前无人机临时改写 support 并保留新类型；距离更远的类型不匹配请求仍 reroll。
- 这条路线仍然没有真正解决 companion 兑现问题，但已经证明旧“无完成轮”主要是入口目标错误，而不是脚本完全无收益
- 证据来源：
  - `lb_carrots_single.py` 当前默认入口
  - 真实请求 `287`
  - 真实请求 `307`
  - 真实请求 `621`
  - 真实请求 `622`
  - 你本轮对收益机制的校正

## 通用注意事项下的榜单特化

- 单榜胡萝卜的关键不是“能不能把图扫得很快”，而是“有没有把 companion 真正兑现出来”
- 但 companion 也不是无差别接受：
  - `Grass / Bush / Tree` 都可落地，但必须匹配当前 support 实体
  - 简单放开类型后再走过去补种，通常会被移动、改种和回程成本吞掉收益
- 需要持续关注 `reroll / harvest / unready`，但这些计数的意义是判断“为 companion 付出的动作成本是否值得”，不是用来否定 companion 本身

## 当前版本结论

- `main1`
  - 5x5 checkerboard 胡萝卜位 + support claim
  - 至少方向上更接近正确问题：它在试图通过 claim 吃 companion
- `main2`
  - 5x5 满图胡萝卜
  - 旧 repo 默认入口
  - 但按当前已确认机制，它把胡萝卜过度当成“自然成熟吞吐作物”来处理，这个口径本身已经不对
- `main3`
  - 来源：外部 `Save0/carrot.py`，但原始入口 `always_not` 无限运行，必须改成真实目标
  - 请求 `287` 两轮有效完成：`23:28.046` / `24:10.599`
  - 已被 `main4` companion 路线大幅超过，当前 `.py` 不再保留该纯滚动实现；文档只保留它作为历史可结算基线
- `main4` 系列
  - 旧默认 companion 候选；当前已演进为 `lb_carrots_single()` 固定入口中的相邻 2x2 锚点策略
  - 只保留 4 个胡萝卜锚点，避免 5x5 满图互相吃掉 companion 空间
  - 只接受 `Bush` companion；这不是因为 `Grass` 物理无效，而是当前静态单类型 support 只能稳定承接一种类型
  - 请求 `303` 动态补支撑版本：`11` 轮均值 `11:02.118`
  - 请求 `307` 静态 Bush 支撑版本：`13` 轮均值 `9:45.844`
  - 请求 `400` 已知实体记录版本：`13` 轮均值 `9:45.406`
  - 请求 `494` no-known-entity 版本：`13` 轮均值 `9:42.804`
  - 请求 `495` no-known-entity 复跑：`13` 轮均值 `9:44.049`
  - 2026-05-30 当前版本复跑请求 `611`：有效两轮稳定均值 `9:44.621`
  - 2026-05-31 相邻 2x2 锚点请求 `621`：有效四轮稳定均值 `8:46.488`
  - 2026-05-31 相邻 2x2 锚点请求 `622`：完整统计 `finished=true runs=14 average=8:44.832`，最快完整轮 `8:32.070`
  - 2026-06-09 adaptive support memory 请求 `682`：完整统计 `finished=true runs=14 average=8:37.719`，最快完整轮 `8:31.992`
  - 结论：预置非锚点 Bush 支撑比命中后往返补支撑更快；静态支撑坐标足以判断成功命中，删除 `known_entity` 矩阵维护和查询后曾刷新到 `8:44.832`。本轮重新引入只记录 support 当前类型的轻量矩阵，并只在距离 `<=2` 时改写 mismatch support，完整统计继续刷新到 `8:37.719`，但仍慢于 #1 `3:46.963`
- 2026-05-31 相邻 2x2 锚点：
  - 改法：不改 `Bush-only` 静态支撑和三桶优先补水，只把分散四锚点 `(1,1)/(3,1)/(1,3)/(3,3)` 改为相邻 2x2 `(2,1)/(3,1)/(3,2)/(2,2)`，按环路访问。
  - 理论筛选：粗略周期模型中，分散四锚点每有效锚点约 `2040t`，相邻 2x2 约 `1771t`；收益来自移动环路缩短，同时有效 support 权重仍约 `21`。
  - 请求 `621` 短跑有效四轮稳定均值 `8:46.488`，已明显快于请求 `611` 的 `9:44.621`。
  - 请求 `622` 完整统计 `finished=true runs=14 average=8:44.832`，有效轮包括 `8:52.199`、`8:47.343`、`8:50.546`、`8:36.171`、`8:44.726`、`8:39.799`、`8:36.638`、`8:41.484`、`8:49.023`、`8:50.780`、`8:55.077`、`8:52.851`、`8:32.070`。
  - 结论：完整统计确认相邻 2x2 锚点比旧分散四锚点快，当前 `.py` 只保留该最快策略；旧分散四锚点只作为历史基线保留在文档。
- 2026-06-08 相邻双锚点对照：
  - 离线筛选脚本 `.codex/tests/carrot_single_companion_screen.py` 用当前 `8:44.832` 校准 5x5 companion 几何；静态相邻双锚点模型显示 Bush 命中率约 `31.9%`、环路距离 `2`、估算约 `8:09.480`，因此进入短窗实机。
  - 实机请求 `650` 只把锚点缩为 `(2,1)/(3,1)`，保留静态 Bush support、三桶优先补水和原 reroll 逻辑。
  - 请求 `650` 两轮 `15:02.899` / `15:02.968`，稳定均值 `15:02.934`，明显慢于当前 `8:44.832`。
  - 运行统计显示首轮完成时 `cycles=4546`、`harvest=1222`、`reroll=2504`，每 `10M` Carrot 约需 `90s` 左右；双锚点虽然降低移动和 blocked companion，但锚点太少，成熟等待和有效收割密度崩掉。
  - 结论：双锚点候选已从 `.py` 回退；后续不要再按“减少锚点换高命中率”的方向做静态实机，除非模型同时证明成熟等待不会上升。
- 2026-06-08 Grass-only 静态 support：
  - 改法：非锚点支撑从 `Bush` 改为 `Grass`，`roll_bush_companion()` 临时改为接受非锚点 `Grass` companion；四锚点、补水、路径和 reroll 结构不变。
  - 请求 `667` 两轮 `8:42.199` / `8:42.650`，短窗均值 `8:42.424`，看似快于当前完整均值 `8:44.832`，但差距很小。
  - 追加完整统计请求 `668`：`finished=true runs=14 average=8:44.187`，只快约 `0.645s`。
  - 再追加完整统计请求 `669`：`finished=true runs=14 average=8:45.337`，慢于当前完整均值。
  - 两次完整统计合并均值约 `8:44.762`，只比当前记录快约 `0.07s`，低于波动；不认定刷新。
  - 结论：Grass-only 静态 support 没有稳定刷新，已从 `.py` 回退；不要只把 Bush-only 换成 Grass-only。
- 2026-06-08 静态多类型 support 筛选：
  - `.codex/tests/carrot_single_static_type_screen.py` 固定当前四锚点和 5x5 wrap companion 半径 `3`，计算 21 个非锚点 support 对 `Grass/Bush/Tree` 的类型权重。
  - 结果：`bush_only_weight=84`、`best_static_weight=84`、`mixed_has_strict_advantage=False`；每个可命中 support 坐标对三种类型权重完全相同，因此静态多类型布局不会比 Bush-only 提高 companion 命中率。
  - 额外发现 `(0,4)` support 权重为 `0`；临时在 `init_anchors()` 跳过该格 Bush 初始化后，request `672` 三条有效 run 为 `8:54.687` / `8:42.343` / `8:46.048`，均值 `8:47.693`，慢于当前 `8:44.832`。
  - 结论：静态多类型 support 与跳过 unreachable support 都不保留；当前四锚点仍默认预置全部非锚点 Bush。
- 2026-06-08 same-drone 动态 support 预算复核：
  - `.codex/tests/carrot_single_companion_screen.py` 在当前 5x5 / 2x2 四锚点结构下，静态 Bush-only 基线为 `success=29.2%`、`path=4`、`ticks=1774.9`。
  - 该脚本筛出的 distance<=1 动态候选最好估算 `17:26.594`，distance<=2 最好估算 `8:48.797`。
  - 额外直接计算当前四锚点：distance<=1 动态只有 `usable=8`、`success=8.33%`、`ticks=5745.333`；distance<=2 动态为 `usable=52`、`success=54.17%`、`ticks=1899.282`，仍慢于静态 `1774.857`。
  - 结论：当前收割者自己去写相邻 / 近距离 support 没有实机价值；distance<=1 覆盖太窄，distance<=2 往返和改写成本已经超过 reroll 收益。
- 2026-06-09 mature-wait-aware 锚点筛选：
  - `.codex/tests/carrot_single_mature_wait_screen.py` 用 request `622` 当前四锚点 `8:44.832` 和 request `650` 双锚点 `15:02.934` 校准成熟等待惩罚；双锚点动作模型原本只比当前慢 `0.933x`，但实机慢到 `1.720x`，折算成熟等待倍数 `1.845x`。
  - 精确枚举 `2..6` 锚点、固定种子采样 `7..8` 锚点后，top candidates 全部是当前等价的相邻 `2x2` 四锚点：估算 `8:44.832`、`success=29.2%`、`path=4`，没有超过当前路线。
  - 结论：不再实机测试静态锚点数量或静态锚点形状变化；少锚点会重复 request `650` 的成熟等待失败，多锚点没有几何收益。下一条候选必须改变 claim / 动态承接机制，而不是只换锚点。
- 2026-06-09 低成本动态 claim 筛选：
  - `.codex/tests/carrot_single_low_cost_claim_screen.py` 保留当前静态 Bush 成功命中，再估算附近 `Grass / Tree` 废命中的动态承接；baseline 事件 `288`、静态命中 `84`、成功率 `29.17%`、估算 `1774.9t = 8:44.832`。
  - 最好 no-restore 下界 `hybrid d<=2 Grass+Tree` 估算 `8:06.162`，但它不恢复 Bush support，会污染后续静态 Bush 命中，不能直接实机。
  - 路径感知恢复后，`hybrid d<=1 Grass` / `Tree` 估算 `8:50.621`，比当前慢 `5.789s`；`anchor-sacrifice d<=1 Grass+Tree` 估算 `8:55.081`，比当前慢 `10.249s`。
  - 结论：当前四锚点下，“当前收割者临时改附近 Grass / Tree，再恢复 Bush”的低成本 claim 不进实机；恢复支撑和路径绕行成本已经吃掉 reroll 收益。
- 2026-06-09 adaptive support memory：
  - `.codex/tests/carrot_single_adaptive_support_memory_screen.py` 在低成本动态 claim 的 `no-restore` 上界基础上补 steady-state 模型：support 不恢复 Bush，而是保留最近一次请求类型；下一次同坐标类型匹配时直接接受，类型不匹配且距离 `<=2` 时当前 drone 改写为请求类型。
  - 离线筛选显示 `memory-only no rewrite` 与静态单类型等价，仍是 `8:44.832`；`rewrite mismatch d<=2` 估算 `8:06.162`，纸面快约 `38.670s`，达到短窗验证门槛；`d<=3` 因改写太多退到 `8:32.891`。
  - 临时实现保留 5x5 相邻 2x2 四锚点、三桶优先补水和 `10M` progress 日志；新增 `support_entity` 矩阵和 `static_hit/memory_hit/memory_rewrite/memory_far_reject/anchor_block` 计数。
  - 请求 `681` 短窗有效三轮：`8:36.362` / `8:35.664` / `8:40.898`，runner 稳定均值 `8:37.641`。
  - 请求 `682` 完整统计：`finished=true runs=14 average=8:37.719`；可见有效轮包括 `8:38.707`、`8:37.899`、`8:38.242`、`8:36.367`、`8:35.273`、`8:38.945`、`8:31.992`、`8:36.874`、`8:37.297`、`8:38.899`、`8:38.353`、`8:38.906`、`8:41.445`。
  - 统计规模：单轮约 `700~760` 次 `memory_rewrite`、`325~397` 次 `memory_hit`、`207~263` 次 `static_hit`，证明收益来自非 Bush support 记忆和近距离改写；但实机收益只有约 `7.1s`，远低于离线 `38s` 上界，说明改写 churn、地块状态和成熟等待仍吃掉大部分纸面收益。
  - 结论：保留为当前默认入口；后续不要把 `d<=3` 直接打开，模型已经显示改写过多会回吐收益。下一步若继续单机胡萝卜，应先压低 `memory_far_reject` 或减少 `memory_rewrite` 往返成本，而不是恢复 Bush 或只换静态 support 类型。
- 2026-06-10 删除 adaptive 统计计数候选：
  - 代码候选：删除 `cycle / harvest / reroll / static_hit / memory_hit / memory_rewrite / memory_far_reject / anchor_block` 计数、`10M` progress 日志和 done 统计字段；保留 `support_entity` 记忆、四锚点顺序、`d<=2` mismatch rewrite、三桶优先补水和起止 `quick_print`。
  - 这不改变 adaptive support memory 策略，只减少每个锚点 / reroll / support 命中路径上的观测计数和参数传递。
  - 验证：`python3 -m py_compile references/leaderboard_scripts/lb_carrots_single.py` 通过。
  - 真实游戏当前最近 request `730` 仍为 `game_tick=0` timeout，暂未能跑完成轮；文件头成绩不更新。
  - 风险：删除后无法直接从脚本输出看到 `static_hit / memory_hit / memory_rewrite / memory_far_reject` 分布；如果实机退化，只能先看总时间，再临时恢复统计探针定位。
- 2026-06-09 adaptive support memory `d<=1` 收窄对照：
  - 改法：只把 `roll_adaptive_companion()` 的 mismatch support 改写阈值从 `companion_distance <= 2` 收窄到 `<= 1`，其他锚点、补水、support memory 和计数器不变。
  - 请求 `683` 短窗两轮 `8:45.898` / `8:47.148`，稳定均值 `8:46.523`，明显慢于当前 `d<=2` 完整统计 `8:37.719`。
  - 结论：过度收窄改写半径会丢掉太多可兑现 companion；失败实现已从 `.py` 回退并重新同步 `gamesave/`。当前默认继续保留 `d<=2`，后续不要按 `d<=1` 降 churn 方向实机。
- 2026-06-09 selective adaptive support cell 筛选：
  - `.codex/tests/carrot_single_selective_adaptive_support_screen.py` 用当前 `d<=2` 成绩 `8:37.719` 校准，枚举只允许部分 support 坐标执行 mismatch rewrite 的策略，并单独筛“保留全量 `d<=2`、只额外开放少数 `d=3` support cell”。
  - 全量 `d<=2` 模型为 `success=65.28%`、`rewrite=36.11%`、`ticks=1644.1`；删掉任意一个低权重 support cell 的最好估算也只到 `8:37.868`，比当前慢约 `0.149s`。
  - selective `d=3` 最好是不额外开放；开放任意一个 `d=3` cell 至少退到 `8:38.899`，比当前慢约 `1.180s`。
  - 结论：不做实机；当前收益来自尽量多兑现 `d<=2` 内的非 Bush companion，选择性减少 support cell 只会损失成功率，额外打开 `d=3` 的 rewrite 成本又会吞掉新增命中。
- 2026-06-09 directional adaptive support 筛选：
  - `.codex/tests/carrot_single_directional_adaptive_support_screen.py` 继续沿用当前 `8:37.719` 校准，但把筛选粒度从 support 坐标改成锚点到 support 的相对 offset，枚举 `d<=2` 内 12 个相对方向是否允许 mismatch rewrite。
  - 全量 `d<=2` 仍是最优：`success=65.28%`、`rewrite=36.11%`、`rewrite_cost=629.8`、`ticks=1644.1`。删掉任意一个低权重方向后最好估算为 `8:38.177`，比当前慢约 `0.458s`。
  - 结论：不进实机；按方向过滤 rewrite 只是降低少量 churn，同时损失更多可兑现 companion。当前默认继续保留全量 `d<=2`。
- 2026-06-09 adaptive memory 锚点布局筛选：
  - `.codex/tests/carrot_single_adaptive_anchor_layout_screen.py` 用当前 `d<=2` adaptive memory 完整统计 `8:37.719` 校准，重新枚举 / 采样 5x5 内的锚点数量和形状。
  - 精确枚举 `2..6` 锚点，采样 `7/8` 锚点各 `40000` 个；top candidates 全部是当前等价的相邻 `2x2` 四锚点，估算 `8:37.719`、`success=65.3%`、`rewrite=36.1%`、`path=4`。
  - 结论：adaptive support memory 后，锚点数量 / 形状仍没有超过当前相邻 `2x2` 四锚点；不按 anchor layout 平替或加密进入实机。
- 2026-06-09 deferred far rewrite 筛选：
  - `.codex/tests/carrot_single_deferred_far_rewrite_screen.py` 检查 `memory_far_reject` 的 distance-3 mismatch support，是否可以不做当前锚点往返，而是在继续锚点循环时顺路改写，下圈再收割原锚点。
  - distance-3 非 Bush far event 共 `64` 个，没有任何一个在原始动作 tick 上快于直接 `harvest()+plant()` reroll；最佳 detour 也要 `4` 步，`best_deferred_ticks=1200`，而直接 reroll 只有 `401t`，且还没计入延迟一圈收割的机会成本。
  - 结论：不进入实机；当前锚点循环没有免费经过 support 的窗口，far support 仍需要绕行和延迟收割。后续不要按 deferred far rewrite 降 `memory_far_reject`，除非出现无需 detour 的支撑 writer 或通信结构。
- 2026-06-09 rewrite cooldown 筛选：
  - `.codex/tests/carrot_single_rewrite_cooldown_screen.py` 按当前四锚点顺序做 Monte Carlo，给每个 support cell 增加改写后冷却窗口，测试是否能避免刚改写后立刻被覆盖。
  - `cooldown=1` 只有约 `-0.297s` 模型收益，低于实机噪声和验证门槛；`cooldown>=2` 开始变慢，`cooldown=6` 已退化约 `4.097s`，原因是 `reroll/acc` 上升快于 `rewrite/acc` 下降。
  - 结论：不进入实机；rewrite cooldown 只是 selective rewrite 的时间版，不能有效压低 `memory_rewrite` 往返成本。
- 2026-06-09 type-filtered adaptive support 筛选：
  - `.codex/tests/carrot_single_type_filtered_adaptive_support_screen.py` 检查是否只对 `Grass / Bush / Tree` 中部分类型执行 `d<=2` mismatch rewrite。
  - 当前全类型 `d<=2` 仍是最优，估算 `8:37.719`；任意双类型组合估算 `8:45.239`，慢约 `7.520s`；任意单类型组合估算 `8:57.152`，慢约 `19.433s`。
  - 结论：当前收益来自全类型承接；按类型减少 rewrite churn 会损失更多可兑现 companion。默认继续保留 `Grass / Bush / Tree` 全类型 `d<=2` 改写。
- 2026-04-30 已知支撑记录复测
  - 在 `main4` 初始化时记录 5x5 每格实体；后续 `get_companion()` 命中已知 `Bush` 支撑格时直接接受
  - 请求 `400` 完成 `13` 轮，均值 `9:45.406`
  - 真实完成轮首两轮为 `9:41.814` / `9:49.399`，最终稳定均值略快于请求 `307` 的 `9:45.844`
  - 处理：保留实现为当前默认入口；这是小幅刷新，不代表路线已接近 #1
- 2026-05-02 移除静态支撑矩阵查询：
  - 改法：`main4` 不再创建和维护 `known_entity`；`roll_main4_bush_companion()` 遇到 `Entities.Bush` 且坐标不是四个胡萝卜锚点时直接接受。
  - 前提：`main4` 初始化后非锚点支撑格保持静态 `Bush`，运行中只会重种四个胡萝卜锚点，因此矩阵查询不会提供额外正确性。
  - 请求 `494` 完整结束 `finished=true runs=13 average=9:42.804`。
  - 复跑请求 `495` 完整结束 `finished=true runs=13 average=9:44.049`。
  - 结论：两次完整统计都快于旧可靠 `9:45.406`，删除静态支撑矩阵维护和成功命中查询后保留；当时 `lb_start.py` 记录更新为 `9:42.804`，当前记录以后续当前版本复跑为准。
- 2026-05-02 `main4` progress 日志阈值 `20M`：
  - 初次请求 `496` 误改到 `maybe_log_main2()`，默认 `main4` 日志频率未变；完整结束 `finished=true runs=13 average=9:46.007`，不作为该候选有效判断。
  - 修正后请求 `497` 完整结束 `finished=true runs=13 average=9:44.232`，`game_output_lines=79`，确实少于 10M 版本的约 `95~141` 行。
  - 结论：减少日志没有刷新 `9:42.804`，也没有明显优于 10M 复跑 `9:44.049`；代码已恢复 `10M` 日志阈值。
- 2026-05-02 信任锚点为 Carrot：
  - 改法：删除 `process_main4_anchor()` 开头的 `get_entity_type() == Entities.Carrot` 分支判断，直接按锚点已经是胡萝卜处理。
  - 请求 `498` 完整结束 `finished=true runs=13 average=9:44.376`。
  - 结论：没有刷新 `9:42.804`，也略慢于 no-known-entity 保留版复跑 `9:44.049`；锚点类型分支已恢复。
- 2026-05-02 静态 Tree-only support：
  - 改法：`main4` 非锚点支撑从 `Bush` 改为 `Tree`，companion rolling 只接受非锚点 `Tree`。
  - 请求 `511` 完整结束 `finished=true runs=13 average=9:45.182`。
  - 可见尾部有效轮包括 `9:41.599`、`9:41.985`、`9:46.699`、`9:47.688`、`9:49.335`。
  - 结论：预置 Tree support 没有刷新 `9:42.804`，尾部波动更差；代码已恢复静态 Bush-only support。
- 2026-05-02 静态 Bush/Tree 混合 support：
  - 改法：非锚点按坐标奇偶预置 `Bush / Tree`，companion rolling 只接受非锚点且类型匹配该坐标的预置支撑。
  - 请求 `514` 完整结束 `finished=true runs=13 average=9:51.414`。
  - 可见有效轮包括 `9:50.781`、`9:52.031`、`9:56.599`、`9:49.492`、`9:53.984`、`9:50.937`、`9:56.899`、`9:55.077`、`9:46.999`。
  - 结论：混合支撑明显慢于 Bush-only，也慢于 Tree-only；预置混合缩小了每种 companion 的可接受坐标集合，代码已恢复静态 Bush-only support。
- 2026-04-26 动态放开 `Tree` companion 复测
  - 在 4 锚点 `main4` 基础上允许 `Bush / Tree`，命中 `Tree` 后移动到伴生格补树
  - 请求 `318` 完成 `13` 轮，均值 `9:55.728`
  - 结果慢于静态 Bush-only 基线 `9:45.844`
  - 根因判断：小图里 Tree 确实会减少一部分拒绝，但补支撑移动和支撑替换成本抵消收益；Tree 动态接入不是当前 5x5 结构的净提升
  - 处理：失败实现已从 `.py` 删除；下一步如果继续用 Tree，应改为预置混合支撑，而不是命中后补种

## 失败对照

- “没伴生也能靠吞吐推进”的理解
  - 这条线当前应视为错误口径
  - 原因不是实现细节，而是 `160x` companion 才是主收益
- `Grass-only` 伴生路线
  - `Grass` 可种在 Soil，不能再按草地 / 耕地冲突判死
  - 但在静态单类型 support 模型下，Grass-only 与 Bush-only 只是同概率替换，不会天然提高 companion 命中率
  - 请求 `667/668/669` 已验证静态 Grass-only 没有稳定刷新；若没有额外低成本多类型承接结构，不再作为实机候选
- 需要真正淘汰的不是“所有 companion 路线”，而是“高冲突但低兑现率”以及“移动补种成本超过 reroll 成本”的 companion 分支
- 外部 `Save0/lb_carrot_single.py`
  - 原始入口指向 `carrot_single_pi`，但 `Save0` 中不存在这个目标文件
  - 按规则尝试改用唯一可疑替代 `Save0/carrot.py`，并内联 `utils.use_water()` / `utils.harvest_if_can()` / `utils.always_not()`
  - 真实请求 `243`：30 秒无 `output.txt` 完成轮，最终 `leaderboard finished without completed runs`
  - 同期 `item_snapshot` 显示 `carrot` 已从 `129,573,888` 增长到 `4,023,484,416`，但 leaderboard 没有记录 `run=`
  - 判断：这个脚本在单机榜语境下不是可直接迁入候选；问题不是产量不足，而是入口目标缺失、脚本无限运行且没有被 leaderboard 正确结算
- 2026-04-26 外部 `Save0/carrot.py` 修真实目标后单机复测：
  - 临时迁入为 `main3`，目标改为 `num_items(Items.Carrot) >= 100_000_000`
  - 请求 `287` 新增有效完成轮：`run=1 time=23:28.046`、`run=2 time=24:10.599`，稳定均值约 `23:49.323`
  - 结论：修目标后可结算，且明显优于旧记录 `7:02:50.195`；但仍远慢于 #1 `3:46.963`
  - 处理：已被 `main4` 替代，`.py` 不再保留该候选入口；后续继续围绕 companion 兑现率优化当前默认路线
- 13 锚点高密度静态 Bush 支撑：
  - 请求 `306` 有效完成 `11` 轮，均值 `11:20.339`
  - 比 4 锚点动态补支撑 `11:02.118` 和 4 锚点静态支撑 `9:45.844` 都慢
  - 根因：锚点变多后 `Bush` companion 落到目标胡萝卜格的废命中显著增加，reroll 从约 `3.1k` 上升到约 `6.6k`
  - 处理：失败实现已从 `.py` 删除，仅保留结论
- 相邻双锚点静态 Bush 支撑：
  - 请求 `650` 两轮 `15:02.899` / `15:02.968`，稳定均值 `15:02.934`，慢于当前 `8:44.832`。
  - 根因：理论筛选只捕捉到 Bush 命中率和移动环路收益，低估了锚点数量减少后的成熟等待；单机胡萝卜不能只靠两个锚点轮转。
  - 处理：失败实现已从 `.py` 回退，并重新同步正式四锚点版本到 `gamesave/`。
- 动态接受 `Tree` companion：
  - 请求 `318` `13` 轮均值 `9:55.728`
  - 慢于静态 Bush-only `9:45.844`
  - 结论：单机小图不适合命中后再补 Tree；可继续评估预置混合支撑，但不要把动态补 Tree 保留为候选实现
- 四桶优先补水：
  - 2026-05-02 请求 `471`：runner 先输出 `reached stable leaderboard runs 10 avg=9:49.161`，最终摘要给出 `leaderboard_average runs=11 average=9:49.546`。
  - 改法：`water_main4_anchor()` 从三桶优先改成四桶优先，并保留 `3` 桶 / `2` 桶 / `1` 桶 fallback。
  - 有效轮包括 `9:54.218`、`9:48.699`、`9:53.983`、`9:43.199`、`9:44.882`、`9:39.296`、`9:52.299`、`9:49.140`、`9:53.397`、`9:52.499`、`9:53.398`。
  - 取消摘要 `finished=false runs=12 average=9:05.041` 不作为刷新成绩。
  - 结论：没有刷新；四桶补水消耗更多水但没有压低成熟等待，代码已恢复三桶优先。
- 两桶优先补水：
  - 2026-05-02 请求 `484`：完整结束 `finished=true runs=13 average=9:44.716`，首跑快于当时可靠 `9:45.406`。
  - 2026-05-02 追加请求 `485`：完整结束 `finished=true runs=13 average=9:47.066`，复跑退化。
  - 两次合并约 `9:45.891`，慢于当时可靠基线 `9:45.406`。
  - 改法：`water_main4_anchor()` 改为两桶优先，有水量大于 `1` 时使用 `2` 桶，否则使用 `1` 桶。
  - 结论：首跑小幅刷新不稳定；两桶优先会放大成熟等待波动，代码已恢复三桶优先。

## 下一步优化方向

- 当前静态 Bush 支撑主线已补真实成绩；后续只在出现“不由当前收割者往返改写 support”的新结构时重开 companion 兑现率探针，不再重复静态平替或 same-drone 动态承接
- 重点看：
  - `Grass / Bush / Tree` 各自的真实兑现率和补支撑成本
  - 5x5 小图是否真的适合做 companion 链
  - `main1` 这类 claim 路线的问题到底是“冲突过高”，还是“claim 方式本身写得太笨”
- 已验证四桶优先补水慢于当前三桶优先，默认保留 `3` 桶 / `2` 桶 / `1` 桶 fallback。
- 已验证两桶优先补水首跑刷新不稳定，默认仍保留三桶优先。
- 已验证 `known_entity` 矩阵在静态 Bush 支撑版本中不是必要运行状态，默认直接按非锚点 Bush companion 接受。
- 已验证 `main4` progress 日志阈值 `20M` 没有带来净收益，默认保留 `10M`。
- 已验证删除锚点实体类型分支没有刷新，默认保留 `process_main4_anchor()` 的类型兜底。
- 已验证静态 Tree-only support 没有刷新，默认保留静态 Bush-only support；后续不要重复试“全 Tree 预置支撑”。
- 已验证静态 Bush/Tree 混合 support 没有刷新，默认保留静态 Bush-only support；后续不要再试坐标奇偶混合支撑。
- 已验证相邻双锚点明显慢于当前四锚点，默认保留 `(2,1)/(3,1)/(3,2)/(2,2)` 四锚点；后续静态锚点数量变化必须把成熟等待纳入筛选。
- 已验证静态 Grass-only support 没有稳定刷新，默认保留静态 Bush-only support；后续不要再做单类型 support 平替。
- 已通过静态多类型 support 筛选确认，当前四锚点几何下混合 `Grass/Bush/Tree` 不提高类型命中率；跳过 `(0,4)` 这个 unreachable support 也变慢，默认继续初始化全部非锚点 Bush。
- 已通过 same-drone 动态 support 预算确认，当前收割者自己写相邻 / 近距离 support 不值得进实机；后续动态承接必须避免当前 drone 往返改写成本。
- 已通过 mature-wait-aware 锚点筛选确认，当前相邻 `2x2` 四锚点是静态 Bush-only 锚点形状上界；不要继续只换锚点数量或形状。
- 已通过低成本动态 claim 筛选确认，当前 drone 附近临时改 `Grass / Tree` 再恢复 `Bush` 不值得进实机；但 no-restore support memory 经 request `682` 完整统计确认能小幅刷新，当前默认保留 adaptive support memory。
- 当前单机胡萝卜下一步不再是静态平替、恢复 Bush、锚点布局平替或按类型收窄 rewrite，而是围绕 adaptive support memory 继续压低 `memory_far_reject` / `memory_rewrite` 成本；`d<=1` 已实机变慢，selective support cell、directional rewrite filter、adaptive memory anchor layout、type-filtered rewrite、selective `d=3`、deferred far rewrite 和 rewrite cooldown 已模型判定无实机余量，`d<=3` 全开已在模型中显示改写过多，任何新增分支都必须先过 mature-wait-aware / support-memory 模型。
- 2026-06-10 已删除 adaptive 统计计数和 progress 日志作为管理成本候选；确认前不更新成绩注释。游戏恢复后必须短跑 `lb_carrots_single`，若无稳定刷新或需要重新观测 hit / rewrite 分布，则回退或临时恢复统计探针。

## 候选策略方向（猜测 / 待验证）

### 方向 1：保留小图，但重做 companion claim 规则（暂缓）

- 核心思路：不是放弃 claim，而是把 claim 规则重写成“只接受当前能低成本兑现的 companion”
- 主瓶颈：当前 `main1` 的问题更可能是冲突和错误接受，而不是“claim 这件事本身不该做”
- 可能更强的原因：如果能把 claim 的质量做高，单机胡萝卜才有机会真正吃到 `160x`
- 优先探针：
  - 不同 companion 类型的兑现率
  - 拒绝 `Grass` 后总冲突数是否明显下降
- 当前状态：静态 Bush-only 四锚点 claim 已验证明显超过 `main3()` 纯滚动基线；13 锚点高密度、相邻双锚点、静态单类型 / 多类型和低成本动态 claim 都已失败。adaptive support memory 已经刷新为当前默认；后续不能只重写接受顺序，必须先证明新 claim 模型能同时降低 reroll、成熟等待和 support 改写成本。

### 方向 2：围绕 `Bush / Tree` 做单机短链（当前暂缓）

- 核心思路：胡萝卜不会出现胡萝卜 companion，因此短链只能围绕可落地的 `Grass / Bush / Tree` support 做，而不是继续假设“胡萝卜 -> 胡萝卜”。
- 主瓶颈：当前主线只使用静态 `Bush`，没有评估 `Tree` companion 是否值得接入。
- 可能更强的原因：如果 `Tree` 的额外动作成本低于 reroll 掉它的成本，单机也可能进一步降低空转。
- 优先探针：
  - `Tree` companion 出现频率
  - 接受 `Tree` 后的 reroll 降幅是否超过补树动作成本
- 当前状态：动态补 Tree 已实机失败；恢复 Bush 的 same-drone 近距离动态 support 和低成本动态 claim 预算也慢于静态 Bush-only。no-restore adaptive support memory 证明有限距离改写有小幅收益；后续只在模型能优于当前 `8:37.719` 时再进实机。

### 方向 3：小图保留，但 support 服务于低成本可兑现伴生

- 核心思路：support 设计不再“什么伴生都接”，而是只服务于能低成本匹配实体的伴生
- 主瓶颈：小图 support 位有限，同一坐标不能同时放多种实体；混合 support 会缩小每种类型的可接受坐标集合
- 可能更强的原因：单机地图本来就小，support 必须极致聚焦，否则很快被无效格子拖死
- 优先探针：
  - 去掉 `Grass` 兼容后，support 冲突是否下降
  - 固定 support 与动态 support 哪种更适合单机胡萝卜
- 当前状态：静态 Grass-only、Tree-only、Bush/Tree 混合和静态多类型 support 都已失败；固定 support 已从 Bush-only 演进为 adaptive support memory。动态 support 必须限制 churn，不要恢复 Bush，也不要扩大到 `d<=3` 这种改写过多的路线。
