# lb_hay

## 榜单目标

- 目标资源：`Items.Hay`
- 多无人机路线
- 当前脚本目标数量为 `2000000000`

## 收益机制说明

- 草是游戏最基础的资源，只能种在草地上。
- 这和胡萝卜正好相反：
  - 胡萝卜必须保持耕地 / Soil
  - 草则必须尽量保持所有目标地块都是草地
- 草的 companion 类型会从 `Bush / Carrot / Tree` 中选择；`Carrot` support 不是物理上永远无效，因为 companion 只要求目标坐标有对应实体。
- 当前把 Carrot 当弱候选处理，是因为由收割者自己往返改写 support 时，要额外切 Soil / Grassland，动作成本高于原地 reroll 收益。
- 另一个非常关键的事实是：
  - 草成熟非常快，基础只要 `0.5s = 200t`
  - 如果浇水，成熟时间甚至会压到几十 `t`
  - 但一次 `move()` 是固定 `200t`
  - 一次 `harvest()` 也是固定 `200t`
- 这会推出一个很硬的结论：
  - 草榜最应该省的是移动
  - 其次才是别的局部操作
- 但 `harvest()` 本身也要 `200t`，所以草榜不会是“见熟就收”的简单问题。
- 当前草榜打法的核心由此产生：
  - 原地赌伴生
  - 伴生正确才移动去处理另一格
- 另外，草的伴生一定不会是草本身。
  - 所以如果伴生落在另一个“目标草收获格”，那就一定是废伴生
  - 因为目标草格本来就必须保持为草，不可能改成别的作物来吃这个伴生
- 对 leaderboard 语境下的草来说，同样要把 `160x` 伴生视为主收益。
  - 多草如果不把伴生做进主路径，没有 `160x` 伴生，就基本没有意义

## 当前基线

- 当前默认入口：`main2()`
- 当前 repo 路线：32x32 世界，32 个分散双草伴生单元；每个单元预置 Bush 支撑位，只接受 `Bush` 且不落在另一目标草格的 companion
- 真实短窗口记录：
  - 旧 `main1`：`9:14.596`，45 秒窗口 5 轮平均
  - `main2` 初版 56 格方形支撑：`2:54.643`，45 秒窗口 10 轮平均
  - `main2` 当前 30 格曼哈顿支撑：`2:48.790`，45 秒窗口 10 轮平均
  - `main2` 有水即补水：`2:47.936`，45 秒窗口 10 轮平均
  - `main2` 优先双桶补水：`2:47.485`，45 秒窗口 10 轮平均
  - `main2` 优先三桶补水：`2:47.405`，45 秒窗口 9 轮平均
- 2026-05-30 当前版本复跑：请求 `610` 有效两轮 `2:48.124` / `2:47.599`，稳定均值 `2:47.861`；后续 `finished=false` 取消摘要不作为成绩。
- 当前仍慢于 #1 `1:47.733`，但已经把旧纯吞吐路线替换为 companion 主路径
- 证据来源：真实游戏 `run_real_game_script.py` 请求 `45`、`46`、`48`、`53`、`54`

## 通用注意事项下的榜单特化

- hay 的高收益核心来自 companion 命中后的 `160x` 收益，而不是单纯成熟就收
- `Carrot` 伴生不是物理无效，但 same-drone 往返改写 support 的成本太高；没有低等待 writer 前仍按弱候选处理
- 多机环境下当然不能无脑像单机那样频繁来回移动，但也不能退化成“没伴生也无所谓”的纯吞吐路线
- 这个榜单真正要平衡的是：
  - 伴生兑现率
  - 移动成本
  - 多机并行时的链路组织方式

## 当前版本结论

- `main1`
  - 逻辑是用棋盘布局把 Bush 稠密地放进 Grass 的邻域里，然后主要靠自然命中吃收益
  - 真实平均 `9:14.596`，已被 `main2` 淘汰
- `main2`
  - 32 个分散双草伴生单元
  - 初版按 7x8 方形支撑初始化，真实平均 `2:54.643`
  - 当前版只初始化 companion 曼哈顿半径 `3` 的 30 个支撑格，真实平均 `2:48.790`
  - 把补水阈值从库存 `>128` 降到 `>0` 后，真实平均 `2:47.936`
  - 补水改成库存足够时一次用 `2` 桶后，真实平均 `2:47.485`
  - 补水改成库存足够时一次用 `3` 桶后，真实平均 `2:47.405`
  - 2026-05-30 当前版本复跑请求 `610` 稳定均值 `2:47.861`
- 2026-04-30 companion 分布探针
  - 请求 `403` 两轮有效完成：`2:52.399` / `2:51.328`，均值 `2:51.864`
  - 探针本身有额外计数和输出开销，因此不作为速度候选保留
  - 首轮接近结束时首个单元统计：`bush=800`、`tree=790`、`carrot=786`、`other=0`、`effective=755`
  - 第二轮接近结束时首个单元统计：`bush=753`、`tree=782`、`carrot=802`、`other=0`、`effective=717`
  - 结论：companion 类型基本三等分；当前 Bush-only 结构只兑现约三分之一的 companion 机会，用户指出的“完全没管伴生会等于 0 收益”在方向上成立，但后续重写必须避免动态追 Tree / Carrot 的长距离移动成本
- 2026-05-02 当前默认入口复测
  - 请求 `407` 两轮有效完成：`run=1 time=2:48.720`、`run=2 time=2:49.129`。
  - 两轮均值 `2:48.925`，最近两轮差异 `0.2%`，满足 runner 稳定停表规则。
  - 结论：当前默认 `main2()` 仍稳定完成，但没有刷新 `2:47.405`；继续优化应按请求 `403` 的 companion 分布结论推进，而不是继续只调补水。

## 失败对照

- 2026-04-25 外部 `Save0/wheat.py` 候选：
  - 去掉 `utils.always_not` 依赖后覆盖既有 `lb_hay.py` 验证
  - 请求 `261` 只有 `[lb_hay] start`，30 秒无完成轮
  - `item_snapshot` 显示 Hay 增至约 `751757824` 仍未结算，不迁入
- 2026-04-26 修正 `Save0/wheat.py` 真实结算目标后复测
  - 临时迁入为 `main3`，把退出条件修成 `num_items(Items.Hay) >= 2_000_000_000`
  - 请求 `286` 完成 1 轮，`[lb_hay] finished=true runs=1 average=134:38.930`
  - 运行中 `item_snapshot` 显示 Hay 平稳增长，例如现实约 `102.2s` 时游戏时间 `8029.762`、`hay=1987840000`
  - 结论：修目标后可以结算，但游戏内时间远慢于当前 `main2` 的约 `2:47`；纯滚动收草不是草榜方向，不能迁入默认入口
- “没有 160x 伴生也能靠多机吞吐推进”的理解
  - 这条线当前应视为错误口径
  - 因为草榜的主收益同样来自伴生兑现，而不是普通收草
- `Carrot` 伴生路线
  - 这条线也应直接视为废路线
  - 原因不是收益排序，而是草地约束下根本不成立
- 当前仓库没有多机 hay 的成熟失败谱系，但单机 `hay_single` 已经证明：
  - 随便增加移动
  - 随便追无效伴生
  - 随便扩大无谓刷新
  都很容易直接退化
- `main2` 降到 20 个活跃双草单元
  - 真实平均 `4:24.106`
  - 结论：真实可用并行数高于 20，不能按 20 单元收缩
- 单草原地 companion 尝试
  - 45 秒窗口没有任何完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 结论：不移动会卡在成熟 / reroll 节奏上，不能直接替代双草轮转
- 动态兑现非阻塞 companion
  - 真实平均 `3:50.717`
  - 具体问题：为了兑现 Tree / Carrot companion 引入大量往返移动；Carrot support 还会快速耗尽种子并输出缺物品警告
  - 结论：在当前资源与移动成本下，不如固定 Bush support + 原地 reroll
- 优先四桶补水
  - 2026-04-25 真实短窗口 9 轮平均 `2:47.567`
  - 慢于三桶补水 `2:47.405`，说明继续加大单次补水量会被库存消耗和随机波动吞掉
- 只在够三桶时补水
  - 2026-05-02 请求 `469`：runner 输出 `reached stable leaderboard runs 10 avg=2:47.503`。
  - 改法：`water_pair_slot()` 只保留 `num_items(Items.Water) > 2` 时 `use_item(Items.Water, 3)`，删除低库存 `2` 桶 / `1` 桶 fallback。
  - 有效轮为 `2:46.210`、`2:47.920`、`2:46.289`、`2:47.999`、`2:47.768`、`2:47.578`、`2:47.695`、`2:46.698`、`2:47.924`、`2:48.945`。
  - 取消摘要 `finished=false runs=11 average=2:36.800` 不作为刷新成绩。
  - 结论：没有刷新；低库存 fallback 仍有价值，代码已恢复 3 桶 / 2 桶 / 1 桶补水。
- `main2` 降到 31 个活跃双草单元
  - 2026-05-02 请求 `503`：runner 输出 `reached stable leaderboard runs 10 avg=2:52.719`。
  - 改法：`ACTIVE_PAIR_COUNT = 32` 改为 `31`，其余支撑布局、Bush-only companion 接受策略和三桶优先补水 fallback 不变。
  - 有效轮为 `2:53.229`、`2:50.585`、`2:52.341`、`2:52.812`、`2:52.799`、`2:51.929`、`2:53.788`、`2:52.734`、`2:52.599`、`2:54.374`。
  - 取消摘要 `finished=false runs=11 average=2:39.158` 不作为刷新成绩。
  - 结论：少一个双草单元明显慢于当前可靠 `2:47.405`；代码已恢复 `ACTIVE_PAIR_COUNT = 32`。
- Tree-only support 对照
  - 2026-05-02 请求 `508`：runner 输出 `reached stable leaderboard runs 10 avg=2:47.692`。
  - 改法：把支撑区实体从 `Entities.Bush` 改为 `Entities.Tree`，并只接受 `companion_entity == Entities.Tree`。
  - 有效轮为 `2:47.109`、`2:47.914`、`2:47.538`、`2:48.593`、`2:47.656`、`2:47.968`、`2:47.343`、`2:46.899`、`2:47.851`、`2:48.046`。
  - 取消摘要 `finished=false runs=11 average=2:34.343` 不作为刷新成绩。
  - 结论：同样低移动结构下 Tree-only 未刷新 `2:47.405`；代码已恢复 Bush-only support。
- Tree-only 动态接入探针
  - 2026-05-30 请求 `602`：60 秒窗口超时，状态 `failed`，`last_error=leaderboard cancelled: hay`。
  - 改法：保留 32 个双草单元和 Bush support；当 `get_companion()` 命中 `Tree` 且不在另一目标草格时，由当前 drone 往返到 companion 坐标种 Tree，再回原草格收割。
  - 有效完成轮为 `4:47.999`、`4:47.148`、`4:47.773`、`4:44.914`、`4:45.078`、`4:45.351`。
  - 取消摘要 `finished=false runs=7 average=4:21.905` 不作为刷新成绩。
  - 结论：在当前双草单元内由收草 drone 自己远距离接入 Tree，移动和建 Tree 成本远超 companion 收益；代码已恢复默认 `main2()`。
- 私有近距离 Tree support
  - 2026-06-08 `.codex/tests/hay_tree_companion_budget.py` 估算：只在每个双草单元的私有 support 格做 Tree/Bush 动态切换，distance<=2 理论约 `2:28.093`；该模型避免改写重叠 support 影响邻居单元。
  - 请求 `637` 实机验证私有近距离 Tree support：两轮 `2:59.687` / `3:00.156`，稳定均值 `2:59.922`，慢于当前 `2:47.861`。
  - 结论：预算低估了动态切换带来的成熟等待、support 改写和路径扰动；即使限制在私有近距离格，仍不如 Bush-only。代码已回退并重新同步正式版到 `gamesave/`。
- 2026-06-08 静态混合 support 暂缓复核
  - 机制证据：`Growable.ChooseCompanion()` 会从 `Grass / Bush / Carrot / Tree` 中随机选类型，并排除当前作物；因此草的 companion 类型近似三等分为 `Bush / Carrot / Tree`。
  - 静态混合 `Bush / Tree` support 不会把成功率提升到 `2/3`：同一 support 坐标只能放一种实体，Bush-only、Tree-only 或 Bush/Tree 混合都只是把同一批坐标分配给不同类型，不能同时承接两个类型。
  - Tree-only 已有请求 `508` 十轮均值 `2:47.692`，未刷新可靠基线 `2:47.405`；私有近距离 Tree 动态切换请求 `637` 均值 `2:59.922`，明显退化。
  - Carrot support 虽然会被 `ChooseCompanion()` 选中，但动态兑现非阻塞 companion 已验证会引入大量往返、耕地切换和缺种子警告；在草榜中继续追 Carrot 不进实机。
  - 结论：当前不再实机测试静态混合 support、Tree-only、Carrot support 或由收割 drone 自己追 Tree / Carrot。下一次只有出现“更近 drone 接力改写 support”或“同一局部低成本多类型承接”的新结构，才重新进入实机。
- 2026-06-10 same-drone 全类型 adaptive support 筛选：
  - 反编译 `Growable.HasCompanion()` 只检查 companion 坐标实体类型；Carrot support 在物理上不是无效，但需要把 support 格 `till()` 成 Soil 后再种 Carrot。Bush / Tree 与 Carrot 之间切换还要额外地块切换成本。
  - `.codex/tests/hay_adaptive_all_type_support_screen.py` 按“当前收割者自己往返改写 mismatch support，且不恢复”的上界估算：`lb_hay` 静态单类型 success `31.9%`、ticks `1054.3`；全类型 adaptive success `95.8%`，但 `rewrite_prob=0.67`、rewrite_ticks `993.2`、总 ticks `1210.7`，估算退到 `3:12.757`。
  - 结论：不改 `lb_hay.py`，不实机 same-drone 全类型承接。Carrot support 的正确口径是“可承接但改写成本高”，不是“永远物理无效”；hay 后续仍只接受已经在请求 support 格附近、能近零等待写入目标类型的 writer 结构。
- 2026-06-08 静态双草布局筛选
  - `.codex/tests/hay_pair_layout_budget.py` 枚举 4x8 周期 tile 内两目标草格，比较减少 blocked companion 与增加目标间移动的取舍。
  - 当前竖向相邻双草 `(0,0)/(0,1)` 估算仍是第一：Bush-only 成功率约 `31.9%`、目标间移动距离 `1`、估算 `2:47.861`。
  - 横向相邻双草估算约 `2:55.497`，更远目标格会因每轮移动距离增加退化到 `3:14.627` 或更慢。
  - 结论：不实机测试多机 hay 的静态目标格平替或拉开双草目标；当前结构已经是非通信 Bush-only 双草布局的低移动上界。
- 2026-06-08 spawn-on-demand Tree helper 筛选
  - 机制依据：当前 Save0 可用 `spawn_drone(task, *args)` / `wait_for(handle)`，因此理论上可把活跃双草单元从 32 降到 16，留下 helper 空位；Tree companion 出现时临时 spawn helper 写 Tree support，anchor 等待后继续。
  - `.codex/tests/hay_spawn_helper_budget.py` 的不安全上界显示，若只给 Tree 请求走 helper、Bush 仍直接接受，all-support distance<=3 估算 `2:33.767`；但这要求 Tree helper 写入后仍能无状态地信任 Bush support，实际不成立。
  - 保守正确模型需要 Bush/Tree 都经 helper 确认或重写 support；此时最好 all-support distance<=3 估算 `3:05.610`，慢于当前 `2:47.861`。
  - 结论：spawn-and-wait helper 不进入实机；减少活跃双草单元换 helper 空位会损失并行吞吐，且 support 类型被 Tree 改写后不能继续无条件接受 Bush companion。
- 2026-06-09 非通信定时 Bush/Tree support 预算
  - `.codex/tests/hay_noncomm_schedule_budget.py` 检查 helper 不知道当前 companion 请求、只盲目周期轮换 support 为 `Bush / Tree` 的接力形态。
  - 当前 `4x8` 双草单元唯一 support 格为 `22` 个；nearest-neighbor support 循环移动 `28` 步；改写一轮 support 下界约 `14400t`，Bush/Tree 两类型周期约 `28800t`。
  - 如果 anchor 不等待，请求类型和 support 类型独立；在 `Carrot` 请求仍约占 `1/3` 的前提下，总成功率不会突破当前 Bush-only 的数量级。
  - 如果 anchor 等待目标类型，平均等待约 `14400t`，是当前 Bush-only 期望 reroll 成本 `854.3t` 的 `16.9x`。
  - 结论：不实机盲定时 support 轮换；hay 的 Tree 方向仍必须是请求感知的近场接力，而不是无通信周期改写。
- 2026-06-09 adaptive no-restore Bush/Tree support 筛选
  - `.codex/tests/hay_adaptive_support_memory_screen.py` 检查 support 格保留最近一次 `Bush / Tree` 类型、不恢复，只有当前请求类型不匹配时由收割 drone 往返改写。
  - 当前双草结构几何为 `support_events=46`、`total_positions=48`、平均距离 `2.39`；静态 Bush 成功率 `31.9%`，期望 `1054.3t`。
  - adaptive Bush/Tree 把类型成功率纸面提高到 `63.9%`，但约一半 useful accept 要改写 support，`rewrite_ticks=678.3`，总期望 `1104.9t`。
  - 估算从当前 `2:47.861` 退到 `2:55.919`；方向也和既有动态 Tree 实机退化一致。
  - 结论：不实机 adaptive no-restore support；没有 support writer 正好在请求格时，不要让当前收割 drone 往返改写 Bush/Tree support。
- 2026-06-09 物理接力 / mailbox helper 预算
  - `.codex/tests/hay_physical_relay_budget.py` 检查不使用 `send / receive`，改用世界实体格编码请求、helper 解码后写 support、anchor 固定等待的低带宽接力。
  - 多机 hay 如果从 32 个双草单元降为 16 个 anchor + 16 个 helper，零开销且 Bush/Tree 全承接的上界只是 `2:47.861`，等于当前；说明并行吞吐减半已经吃掉类型成功率翻倍。
  - 最小实体 mailbox `signal=1 dist=1` 也会退到 `12:40.454`；盲扫 support 不等待时因类型仍不同步退到 `5:35.722`，等待半周期退到 `114:43.910`。
  - 结论：不实机物理 mailbox / world-state relay；没有“无需 anchor 等待的完成信号”时，实体格编码和固定等待成本远高于当前 Bush-only reroll。
- 2026-06-10 目标检查间隔筛选
  - `.codex/tests/hay_goal_check_interval_screen.py` 检查减少 `num_items(Items.Hay)` 读取频率的管理成本候选；当前 `run_pair_cycle()` 每个双草 cycle 至少有循环头和两次 harvest 后检查。
  - 模型口径：当前 `2:47.861`、32 个 worker、每个 pair cycle 3 次查询；按 `cycles_per_worker_s=0.25..4.0`、`query_cost=0.0005..0.010`、`interval=1..64` 做敏感性筛选，并且偏向候选，只把尾巴算成发现达标的平均延迟，没有计入达标后的额外 reroll / 补水 / support 扰动。
  - 结果：只有当查询成本偏高或 pair cycle 很快时，`interval=2..8` 出现明显纸面收益；在低 cycle rate / 低查询成本下收益是噪声级或被退出尾巴吃掉。
  - 结论：不改 `lb_hay.py`，不实机目标检查间隔。Hay 当前主瓶颈仍是只兑现约三分之一 companion 类型；目标检查削减最多是实现成本小候选，且 tail / post-goal churn 风险没有真实验证支撑。
- 2026-06-08 多锚点 Bush-only 轮转筛选
  - `.codex/tests/hay_multi_anchor_layout_budget.py` 用当前 `2:47.861` 校准，枚举单锚点、双锚点、三锚点、四锚点的 Bush-only 非通信结构，估算 Bush-only success、support 数量和最短闭环移动距离。
  - 单锚点纸面 `2:14.096`、success `33.3%`，但模型忽略成熟等待；历史多机单草原地 companion 已无完成轮，因此不按纸面结果进实机。
  - 当前竖向相邻双锚点 `((0,0),(0,1))` 仍是所有双锚点第一：估算 `2:47.861`、success `31.9%`、闭环移动距离 `2`。
  - 三锚点最好 `((0,0),(0,1),(0,2))`，估算 `3:04.419`；四锚点最好 `2x2`，估算 `3:13.060`。
  - 结论：当前双草相邻轮转仍是 Bush-only 非通信结构的上界；单草被成熟等待实机失败否定，三草 / 四草会因为 blocked anchor 增加和闭环移动变慢而退化，不进入实机。

## 下一步优化方向

- 继续量化：
  - 真正带来 `160x` 的伴生命中率
  - `Carrot` 未兑现请求出现频率
  - 多机为了吃伴生额外引入的移动 / 等待是否还能压住
  - 是否存在比 32 个双草单元更高的单位 drone 收益结构
- 请求 `403` 已确认 `Bush / Tree / Carrot` 出现近似三等分；下一轮应从“怎样低移动兑现非 Bush 类型，尤其是有没有近零等待 support writer”开始，而不是继续只微调 Bush-only 的补水或支撑半径
- 已验证三桶-only 补水慢于当前三桶优先 + 低库存 fallback，默认保留 fallback。
- 已验证 31 个活跃双草单元明显慢于 32 个，默认保留 32 个单元。
- 已验证 Tree-only support 慢于 Bush-only，默认保留 Bush-only support。
- 已验证当前双草单元里“命中 Tree 后自己远距离补 Tree”明显慢于 Bush-only 默认路线；后续 Tree 方向必须控制在近距离支撑或交给更近 drone 接力，不能让收割 drone 自己追远点。
- 已验证静态混合 support 只是重新分配单类型坐标，不能突破类型上限；后续不做无新结构的 Bush/Tree 混合实机。
- 已通过 2026-06-10 same-drone 全类型 adaptive support 筛选确认，Carrot support 可作为 companion 类型承接，但由当前收割者往返改写 Bush/Tree/Carrot support 会比原地 reroll 更慢；后续不要把“全类型承接”写成 same-drone support 改写，除非有近零等待 writer。
- 已验证静态双草布局筛选里，当前竖向相邻双草是低移动上界；后续不要只换双草目标位置或拉开目标间距。
- 已验证 spawn-on-demand helper 预算不过线；后续不要用“减少活跃单元腾 helper 位 + anchor wait_for”来追 Tree companion。
- 已验证非通信定时 Bush/Tree support 轮换预算不过线；没有请求感知时类型仍不同步，等待正确类型比当前 reroll 贵一个数量级。
- 已验证 adaptive no-restore Bush/Tree support 预算不过线；当前收割 drone 往返改写 support 的成本高于省掉的 reroll。
- 已验证物理 mailbox / world-state relay 预算不过线；即使 helper 全承接 Bush/Tree，16 helper 结构也只追平当前，任何实体格编码和固定等待都会明显变慢。
- 已验证多锚点 Bush-only 轮转筛选里，单草纸面收益不可信，三草 / 四草估算慢于当前双草相邻轮转；后续不要只按单锚点、三锚点或四锚点 Bush-only 轮转继续实机。
- 已通过目标检查间隔筛选确认，少查 `num_items(Items.Hay)` 只有管理成本小空间，且模型偏向候选；没有真实游戏验证前不改默认检查频率。

## 候选策略方向（猜测 / 待验证）

### 方向 1：多机也改成“原地赌伴生，命中再移动”（已收窄）

- 核心思路：把单草“原地赌伴生，伴生正确才移动”的思想改造成多机版本，而不是每机固定扫行收草
- 主瓶颈：当前 repo 多机路线移动虽然少，但伴生兑现率太低
- 可能更强的原因：如果多机也能把移动集中在“伴生命中之后”，就能同时保住低移动和高倍率
- 优先探针：
  - 多机版原地赌伴生后，单位时间 `160x` 收割次数是否明显上升
  - 为了命中伴生新增的移动量是否还能接受
- 当前状态：当前 `main2` 本质已经是相邻双草 Bush-only 命中后移动；单锚点和多锚点 Bush-only 已被预算 / 实机筛掉。后续不再只改活跃草数量或锚点数量，必须有新的低等待承接机制。

### 方向 2：低等待全类型 support writer（已收窄）

- 核心思路：不再把 `Carrot` 物理判死，而是只在 support writer 已经接近请求格、且不需要 anchor 长等时承接 `Bush / Tree / Carrot`
- 主瓶颈：当前 Bush-only 只兑现约三分之一类型；但 same-drone 全类型改写要为 2/3 有效请求付往返和地块切换成本
- 可能更强的原因：如果 writer 正好在请求 support 附近，才能把全类型高命中率兑现出来
- 优先探针：
  - `Carrot / Tree` 未兑现请求的空间分布
  - writer 是否能在不等待 anchor 的情况下到达请求 support
- 当前状态：same-drone 全类型 adaptive support 已筛掉；静态混合、Tree-only、adaptive no-restore 和非通信定时轮换都不能突破类型命中上限或动作成本。后续只接受请求感知且低等待的全类型承接。

### 方向 3：多机链式伴生接力（暂缓）

- 核心思路：一台机原地赌到有效伴生后，不一定自己去追，而是把机会交给更近的另一台机去接
- 主瓶颈：单台机自己追伴生，容易把移动成本拉高
- 可能更强的原因：多机接力可能把“低移动”和“高伴生兑现率”同时保住
- 优先探针：
  - 接力前后单位时间 `160x` 收割次数变化
  - 无人机之间的等待 / 抢格 / 同步成本是否过高
- 当前状态：当前 Save0 没有消息 API；`spawn_drone() + wait_for()`、非通信定时 helper、world-state mailbox / physical relay 都已筛掉。没有无需 anchor 等待的完成信号或真正通信 API 前，不进实机。

### 方向 4：草地全图不变，但用补水压缩“赌伴生等待窗”（已收窄）

- 核心思路：补水不是为了单纯加快成熟，而是为了让“原地赌伴生”的等待时间更短
- 主瓶颈：草长得快，但如果还要等伴生窗口，少量等待也会被 `200t` 移动/收割成本放大
- 可能更强的原因：如果几十 `t` 的补水能换掉一次 `200t` 的空移动，它就非常值
- 优先探针：
  - 补水后有效伴生命中前的等待时长变化
  - 补水成本是否远小于省掉的移动 / 收割成本
- 当前状态：三桶优先 + 低库存 fallback 是当前默认；四桶、三桶-only、减少活跃单元和 support 改写后补水类方向都没有刷新。后续只有明确减少无效 harvest-reroll 或 support 成熟等待的补水模型才重开。
