# lb_wood_single

## 榜单目标

- 目标资源：`Items.Wood`
- 单机路线
- 当前脚本默认目标数量为 `500000000`

## 收益机制说明

- 木头榜的主基调非常简单：
  - 主体一定是种树
  - 树之间不能相邻
- 因为树不能相邻，所以所有单机木头路线其实都在回答一个问题：
  - 怎么在“树不相邻”的前提下，把剩余格子变成最有价值的 support
- 这里最理想的伴生是灌木：
  - 它能作为树的理想 companion
  - 它自己还能继续产木头
- 所以木头榜里“最舒服”的状态就是：
  - 树位稳定
  - support 格尽量变灌木
- 这也是为什么木头榜和前面的胡萝卜、草在思维上是相通的：
  - 都是先明确主作物
  - 再明确哪些伴生最值
  - 最后围绕移动 / 冲突 / support 稳定性去做优化

## 当前基线

- 当前默认入口：`main11()`
- 当前基线记录：
  - 2026-05-30 当前版本复跑：请求 `613` 有效两轮 `5:36.679` / `5:40.624`，稳定均值 `5:38.652`；后续 `finished=false` 取消摘要不作为成绩
  - `main11` 游戏内实测：`5:40.868`
  - `main11` 已对齐模拟器口径下 5-seed 均值：约 `5:37.9`
  - `main11` 已对齐模拟器口径下 2h 均值：约 `5:39.0`
- 当前默认路线是 8x8 稀疏 tree/support 网络，挖掉 8 个分散树位，目标是降低 reroll 与 support 冲突
- 证据来源：`lb_wood_single.py` 顶部长篇版本结论与文件尾默认入口

## 通用注意事项下的榜单特化

- 这是当前仓库里策略演进最丰富的榜单之一
- 主瓶颈已经被定位得比较清楚：不是简单的“树长不熟”，而是 support 改写抖动、claim 冲突、无效 reroll
- 因此后续优化重点应放在 companion 接受 / 分配策略和 support 稳定性，而不是无脑加动作
- 但上层总纲必须保持简单：
  - 主基调是种树
  - support 最理想是灌木
  - 只要某条策略明显破坏“树不相邻 + support 走灌木”这条主脉，就该高度怀疑它

## 当前版本结论

- `main1` 到 `main3`
  - 3x3 时代路线，已经不是当前主线
- `main4` 到 `main8`
  - 8x8 checkerboard + active claim 主线逐步成形
  - 明确证伪了“全量常规浇水”和“永远拒绝 / 永远动态处理 Carrot”的一些简单想法
- `main9`
  - 允许树位被后段 companion 改写，但被明确认定会把活树数压得太低
- `main10`
  - 回到固定 tree/support 主路径，加入“便宜补水”
- `main11`
  - 当前主线；24 树 sparse checkerboard
  - 2026-05-30 当前版本复跑请求 `613` 稳定均值 `5:38.652`
  - 当前可以理解成：在“树不相邻”的约束下，努力让 support 系统尽量稳定
  - 2026-05-31 数学筛选：当前 8x8 / 24 树位布局中，companion 落到树位导致重 roll 的计数为 `128 / 576 = 22.22%`；对当前布局做一跳局部换位精确搜索，没有找到更低 invalid 的合法 24 树无相邻布局。短期不要只靠微调 `TREE_OFF` 期待大幅收益。
- `main12`
  - 条带型空洞布局，已明确慢于 `main11`
- `main13`
  - 非棋盘 20 树布局，当前主要保留为 probe
- `main14`
  - 24 树基线上开放少量 buffer tree slot
  - 2026-04-24 真实游戏复测中出现过单轮 `5:40.090`
  - 但完整 leaderboard 18 轮均值为 `6:20.046`，明显慢于 `main11` 的 `5:41.061` 级别均值；因此不作为默认入口
- `main15`
  - 4x4 checkerboard 小图路线，已明确慢于 `main11`

## 失败对照

- 2026-04-25 外部 `Save0/wood_single_pi.py` 候选：
  - 入口 `Save0/ld_wood_single.py` 指向 `wood_single_pi`
  - 请求 `250` 无任何 `run=`，最终 `leaderboard finished without completed runs`
  - 该文件只有 tick/排行榜显示时间探针，不是产木策略，不迁入
- 2026-04-25 外部 `Save0/wood_single.py` 候选：
  - 覆盖既有 `lb_wood_single.py` 验证，请求 `251` 只完成 1 轮
  - 成绩 `101:58.599`，且输出 `Items.Weird_Substance` 不足警告
  - 远慢于当前 `main11` 基线，不迁入
- `main9`
  - 树位降级过度，活树数下降明显
- `main12`
  - 条带型空洞布局，慢于 `main11`
- `main15`
  - 4x4 小图路线明显慢于 `main11`
- `main14`
  - 固定 buffer tree slot 能吃到部分 tree-slot claim，单轮能碰到 `5:40.090`
  - 但完整 leaderboard 均值劣化到 `6:20.046`，说明尾部波动和维护成本吞掉了收益
- `main11` 删除 support 预翻地
  - 2026-04-30 请求 `398` 验证。
  - 改法：`init_main11_support_soil()` 不再预翻 support 位；support 只有被 companion claim 时才按目标作物尝试种植，Carrot 按需补 `till()`。
  - 结果：runner 停表为 `reached stable leaderboard runs 8 avg=5:44.374`，慢于当时可靠基线 `5:40.868`。
  - 典型完成轮：`run=5 time=5:40.781`、`run=7 time=5:43.359`、`run=12 time=5:41.132`，但稳定均值仍未刷新。
  - 结论：省掉开局翻地成本后，后续 support 按需补地和改写抖动没有形成净收益；实现已从 `.py` 回退。
- `main11` 关闭周期 probe 输出
  - 2026-05-02 请求 `452` 验证。
  - 改法：跳过每轮 sweep 结束处的 `maybe_log_main11_probe(...)` 调用，保留布局、companion 接受策略、计数器更新、起止 `quick_print` 和默认入口不变。
  - 结果：runner 停表为 `reached stable leaderboard runs 7 avg=5:42.347`，慢于当时可靠基线 `5:40.868`。
  - 有效轮包括 `run=4 time=5:34.492`、`run=5 time=5:42.109`、`run=6 time=5:43.827`、`run=7 time=5:39.599`、`run=8 time=5:47.343`、`run=9 time=5:47.968`、`run=10 time=5:41.093`。
  - 取消摘要 `finished=false runs=11 average=5:16.555` 不作为刷新成绩。
  - 结论：没有刷新；周期 probe 输出不是当前主瓶颈，代码已恢复调用。
- `main11` 只接受 Bush companion
  - 2026-05-02 请求 `470`：runner 输出 `reached stable leaderboard runs 8 avg=7:51.324`。
  - 改法：`roll_main11_tree_companion()` 中除树位 target / support 冲突外，额外拒绝 `ct != Entities.Bush` 的 companion。
  - 有效轮包括 `8:01.367`、`8:18.359`、`7:37.099`、`7:50.099`、`7:43.124`、`7:43.163`、`7:39.648`、`7:57.730`。
  - probe 显示 `tree_reroll` 明显被放大，例如首轮收尾 `harvest=1201`、`tree_reroll=3714`，远高于可接受范围。
  - 取消摘要 `finished=false runs=9 average=7:41.550` 不作为刷新成绩。
  - 结论：没有刷新；Bush-only 过于严格，灌木稳定收益被 reroll 成本吞掉，代码已恢复原 companion 接受策略。
- `main11` 每棵树一次有限 Bush 优先 reroll
  - 2026-05-02 请求 `482`：完整结束 `finished=true runs=17 average=7:12.266`。
  - 改法：`roll_main11_tree_companion()` 中树位 target 和 support 冲突仍按原逻辑无限拒绝；第一次遇到合法但 `ct != Entities.Bush` 的 companion 时，额外 `harvest()` + `plant(Entities.Tree)` 重刷一次；第二次遇到合法 companion 时直接接受。
  - 可见有效轮包括 `7:24.179`、`7:15.699`、`7:31.599`、`7:14.726`、`7:09.648`、`7:06.523`、`7:10.820`、`7:11.445`、`7:05.099`、`7:22.539`、`6:59.531`、`7:03.945`、`7:12.099`、`7:06.992`。
  - probe 显示终局 `tree_reroll` 常见约 `2400~2700`，例如 run 15 为 `2503`、run 16 为 `2438`、最后未完成展示段为 `2479`。
  - 结论：没有刷新；即使每棵树只额外重刷一次 Bush，reroll 成本仍然压垮收益，代码已恢复原 companion 接受策略。
- `main11` 收割成熟 orphan Bush support
  - 2026-05-02 请求 `501`：完整结束 `finished=true runs=21 average=5:47.044`。
  - 改法：`process_main11_support_slot()` 中 `support_count[x][y] <= 0` 且 `entity == Entities.Bush and can_harvest()` 时额外 `harvest()`，其他 orphan 实体仍只计数。
  - 有效轮中有单轮 `5:40.820`，但完整均值明显慢于当前可靠 `5:40.868`；尾部还出现 `5:47~5:52` 多轮。
  - probe 尾部仍有大量 `orphan_support`，例如 run 20 收尾 `orphan_support=812`，说明额外收割没有降低结构抖动，反而增加动作成本。
  - 结论：没有刷新；orphan support 默认继续只计数不收割，代码已恢复。
- `main11` 收割成熟 claimed Bush support
  - 2026-06-08 请求 `651`：两轮 `5:51.036` / `5:50.742`，稳定均值 `5:50.889`，慢于当前 `5:38.652`。
  - 改法：`process_support_slot()` 中 `support_count[x][y] > 0` 且 `entity == ct == Entities.Bush and can_harvest()` 时额外 `harvest()` 并立刻 `plant(Entities.Bush)`；不改树位布局、claim、tree reroll、冻结、补水和日志。
  - 反编译 `Growable.HasCompanion()` 只检查 companion 坐标有实体且类型匹配，不检查成熟度；因此该候选没有从类型上破坏 companion，但每次成熟 Bush support 会多出 `harvest + plant` 两个动作。
  - 结论：Bush support 自身产木吃不回额外动作成本；claimed support 默认仍只 keep，不额外收割。
- `main11` claim/support 抖动探针
  - 2026-06-08 请求 `664`：探针版两轮 `5:42.890` / `5:39.287`，稳定均值 `5:41.088`，慢于当前 `5:38.652`；探针版不作为刷新成绩。
  - 2026-06-08 请求 `665`：用于保留输出细节，两轮 `5:41.638` / `5:45.976`，稳定均值 `5:43.807`。
  - 两轮分桶显示 `tree_reroll` 不是单一来源：`reroll_tree_slot=502/549`，`reroll_claim_conflict=613/647`，claim conflict 比 tree-slot invalid 还略高。
  - support 改写也不是单一作物问题：期望类型近似三等分，`support_expect_bush/grass/carrot=204/216/218` 与 `206/203/212`；旧实体也近似三等分，`support_old_bush/grass/carrot=193/197/203` 与 `191/190/195`，空位只有 `45/45`。
  - 结论：不要直接做 Bush 优先、冻结 support、额外收割 support 或单类型过滤；这会重新落回已失败路线。下一步如果继续单机木头，应先减少 claim overlap，而不是追某一种 support 类型。
- `main11` TREE_OFF support overlap 离线筛选
  - 2026-06-08 `.codex/tests/wood_single_layout_overlap_screen.py` 用 8x8 wrap、companion 半径 `3`、24 个 active tree slot 评价布局。
  - 当前布局分数为 `invalid=128`、`overlap=4672`、`max_degree=12`、`shared_cells=40`；这与既有 `tree-slot invalid = 128 / 576` 结论一致。
  - 约 `488399` 个 swap / 随机候选检查后没有找到低于当前分数的布局。
  - 结论：短期不要只换 `TREE_OFF` 或做 8 个 off 位的局部平替；当前布局在 tree-slot invalid 与 support overlap 这两个指标上都已是强局部最优。
- `main11` 有限开放树位 buffer
  - 2026-06-08 `.codex/tests/wood_single_open_tree_budget.py` 枚举从当前 24 个 active tree slot 中开放 `1..4` 个作为 buffer support；乐观模型下开放 `(4,0)/(7,1)/(0,4)/(3,5)` 可把几何 invalid 从 `128` 降到 `80`。
  - 真实验证 request `671`：三条有效 run 为 `5:44.999` / `5:38.499` / `5:44.840`，稳定均值 `5:42.779`，慢于当前 `5:38.652`；后续 `finished=false runs=4 average=5:02.465` 是取消摘要，不作为成绩。
  - 结论：少量开放 active tree slot 虽能降低 tree-slot reroll，但活树数损失、support 改写和 sweep 扰动吃掉收益；不要继续做“开放 2 到 4 个树位”的实机微调。
- `main11` no-movement claim policy 筛选
  - 2026-06-09 `.codex/tests/wood_single_claim_policy_screen.py` 用当前 8x8 / 24 active tree slot 布局、同一 serpent sweep 和 3 类 companion 类型，模拟不移动、不减少树位的 claim 接受策略。
  - 当前 baseline：`reroll/accept=0.924`，其中 `tree_slot=0.429`、`conflict=0.496`、`same_type=0.245`、`avg_degree=11.363`。
  - `degree<=4..7` 的 unclaimed support 限流全部 stall，说明当前非树 support 格几乎都是高共享度格，不能靠低度 support 子集承接。
  - `free-bush-only` 和 `free-bush-or-degree<=4..6` 的总 reroll 约为 baseline `3.06x~3.16x`，即使同类型共享率提升到约 `0.43`，额外 policy reroll 和 tree-slot reroll 也会先压垮收益。
  - 结论：不要继续做“只改 companion 接受顺序 / 更严格保灌木 / 不加移动”的实机微调；它本质上重复 Bush-only / Bush 优先 reroll 的失败模式。
- `main11` delayed claim 单 owner 承接：
  - 2026-06-09 `.codex/tests/wood_single_delayed_claim_screen.py` 先筛 pending claim：当 support 当前只被单个旧 claim 占用，且旧 claim 会在当前 tree 下次收割前释放、support 格也会在那之前被扫到，就先挂 pending claim，等 support 格访问时激活。
  - 离线 count1 版本只处理 `support_count==1` 且 owner 已知、single pending reservation；10000 sweeps 显示 `reroll/accept` 从 baseline `0.922` 降到 `0.701`，`pending_loss=0`、`match_loss=0`，但 `replant/accept` 从 `0.502` 升到 `0.586`。
  - 临时实机 request `679` 两条有效 run 为 `5:43.281` / `5:45.735`，稳定均值 `5:44.508`，慢于当前 `5:38.652`。
  - 统计显示 delayed 机制确实触发，第二轮尾部附近 `delayed_accept=156`、`delayed_activate=155`、`delayed_drop=0`；但同时 `tree_reroll=922`、`support_replant=700`，收益没有转成成绩。
  - 结论：delayed pending claim 不保留；单机木头不要继续按“等旧 claim 释放后承接”的单 owner 状态机微调，除非新模型能同时压低 `support_replant` 并在实机短窗优于 `5:38.652`。
- `main11` orphan support 实体记忆过滤：
  - 2026-06-09 `.codex/tests/wood_single_orphan_memory_policy_screen.py` 筛选：当 `support_count==0` 且本地记得孤儿 support 实体类型时，只在孤儿实体与新 companion 类型匹配时接受，否则 reroll，目标是减少后续 `support_replant`。
  - 模型结果：baseline `reroll/accept=0.922`、`replant/accept=0.502`；`strict-orphan-match` 把 `replant/accept` 降到 `0`，但 `reroll/accept` 暴涨到 `2.862`，估算退化约 `342s`；`bush-or-orphan-match` 类似退化约 `340s`。
  - 结论：不实机、不改 `.py`。orphan 记忆过滤只是把 support replant 换成更多 tree reroll，明显重复“更严格接受顺序 / Bush 优先”类失败模式。
- `main11` Carrot companion 材料 guard
  - 2026-06-08 请求 `665` 的探针输出里，开局出现 `Warning: 没有种植 Entities.Carrot 所需的物品。`，说明部分 Carrot support claim 接受后暂时落不了地。
  - 候选改法：`roll_tree_companion()` 遇到 `ct == Entities.Carrot` 且当前不能支付 `plant(Entities.Carrot)` 成本时，直接 reroll，不占用 support claim。
  - 2026-06-08 请求 `666` 两轮 `5:51.288` / `5:47.929`，稳定均值 `5:49.609`，慢于当前 `5:38.652`。
  - 结论：缺材料 Carrot claim 的负面影响小于额外 reroll 成本；不要按“当前付不起就拒绝 Carrot companion”的方向继续。
- `main11` 释放 Bush support 后冻结：
  - 2026-05-02 请求 `512`：runner 输出 `reached stable leaderboard runs 8 avg=7:39.980`。
  - 改法：`release_main10_tree_claim()` 在 `support_count` 降到 0 时保留 `Entities.Bush` 标记；`roll_main11_tree_companion()` 拒绝把空闲但 Bush-frozen 的 support 改成非 Bush。
  - 可见有效轮包括 `7:44.999`、`7:33.632`、`7:40.199`、`8:01.289`、`7:22.382`、`7:40.039`、`7:43.860`。
  - probe 显示 `tree_reroll` 被放大到每轮约 `3.2k+`，例如 run 1 收尾 `tree_reroll=3253`，run 2 收尾 `tree_reroll=3257`，run 3 收尾 `tree_reroll=3335`。
  - 结论：没有刷新；冻结确实限制了 support 改写，但代价接近 Bush-only 过滤，重刷成本压垮收益，代码已恢复原释放逻辑。
- 文件还明确把以下现象视为失败信号：
  - `tree_reroll` 与 `harvest` 同量级增长
  - `support_replant` 与 `harvest` 同量级增长
- 这些失败信号本质上都在说明同一件事：
  - 你为了追伴生，已经开始破坏“树位稳定 + 灌木 support”的主结构了

## 下一步优化方向

- 继续以 `main11` 为主线
- 优先做：
  - 只在新模型能同时降低 reroll 与 support replant 时，才继续 companion 接受 / 分配策略
  - 只在能证明不增加 support 改写抖动时，才调整 support 状态机
  - 少量 layout 变体验证已被开放树位和 overlap 筛选压窄，不能再直接实机微调
- 当前默认判断是：sparse layout 本身已经接近局部最优，主矛盾更多在 companion 侧；但普通接受顺序、Bush 冻结、no-movement claim、delayed claim 和开放少量树位都已失败，后续需要新的状态信息或低成本承接结构
- 2026-05-31 布局筛选进一步支持这个判断：当前布局的 tree-slot invalid 一跳邻域没有更优解，后续应优先看 claim 冲突、support 改写、成熟等待和补水，而不是只换树位空洞。
- 这也可以翻译成一句更直接的话：
  - 现在不是继续发明新主题的时候
  - 但也不能继续重复“树位稳定、灌木 support 稳定”的普通微调
  - 下一次必须先拿离线模型证明 reroll 降幅不会被 support replant 或成熟等待吃掉
- 已验证关闭 `main11` 周期 probe 输出没有刷新，默认保留 probe 以便继续观察 reroll / replant 抖动。
- 已验证只接受 Bush companion 明显退化，默认继续接受非冲突 companion，不把灌木优先写成硬过滤。
- 已验证有限 Bush 优先 reroll 仍明显退化；后续不要继续用“主动增加 tree reroll”追灌木比例，除非先找到能同时压低 reroll 的支持位冻结机制。
- 已验证收割成熟 orphan Bush support 没有刷新，默认 orphan support 只计数不收割。
- 已验证收割成熟 claimed Bush support 没有刷新，默认 claimed support 只 keep，不额外收割重种。
- 已验证释放后冻结 Bush support 明显退化；不要用“空闲 Bush 位拒绝非 Bush”这种方式做冻结，因为它会把 `tree_reroll` 推到不可接受范围。
- 已通过 claim/support 抖动探针确认，当前 `tree_reroll` 里 claim conflict 不低于 tree-slot invalid；但 support 期望类型和旧实体都近似三等分，不能用单类型优先规则直接解决。
- 已通过 TREE_OFF overlap 筛选确认，当前 8 个 off 位没有容易替换的局部布局；不要只做 tree slot 空洞微调。
- 已验证 Carrot companion 材料 guard 变慢；不要因为开局缺材料 warning 就提前拒绝 Carrot companion。
- 已验证开放少量 active tree slot 变慢；不要用“少 2 到 4 棵树换更低 tree-slot reroll”的方式继续微调。
- 已通过 no-movement claim policy 筛选确认，单纯更严格地挑 support 坐标或优先 Bush 会把总 reroll 放大到 baseline 约 `3x` 或直接 stall；不要按“只改接受顺序但不移动 / 不加状态”的方向实机。
- 已验证 delayed claim 单 owner 承接变慢；pending 能降低一部分 reroll，但会提高 support replant / 运行节奏成本，不要继续按单 owner pending 状态机微调。
- 已通过 orphan support 实体记忆过滤筛选确认，严格匹配孤儿实体虽然能压掉 support replant，但会把 reroll 放大到 baseline 约 `3x`；不要按“记住孤儿实体后拒绝不匹配类型”的方向实机。

## 候选策略方向（猜测 / 待验证）

### 方向 1：`main11` 上继续强化“灌木优先”的 support 冻结

- 当前结论：普通冻结、Bush-only、有限 Bush 优先 reroll、no-movement claim policy 和 delayed claim 单 owner 承接都已失败；除非能同时降低 reroll 与 support replant，否则不要继续把“灌木优先”写成更复杂的接受 / pending 状态规则。

### 方向 2：`main11` 上做更激进的“树位有限开放”（已降级）

- 核心思路：不像 `main9` 那样开放整片树位，而是只对极少数后段树位开放 companion 占用
- 主瓶颈：当前仍有不少 target 落在树位上的无谓 reroll
- 可能更强的原因：有限开放如果只是为了减少无效 reroll，而不是为了引入更花哨的伴生，就还有机会不伤主结构
- 优先探针：
  - 哪些树位最常成为无效 target
  - 开放 2 到 4 个树位后的活树数变化
- 当前结论：2026-06-08 有限开放树位预算和 request `671` 已证明开放 2 到 4 个 active tree slot 会变慢；后续不要继续做树位开放微调，除非新模型能同时保住活树数、support 恢复和 sweep 节奏。

### 方向 3：维持 `main11` 布局，但把“灌木最理想”写进更严格的 companion 接受顺序

- 当前结论：2026-06-09 no-movement claim policy 筛选已把这条路线降级为失败方向；更严格的接受顺序会先增加 reroll，不形成实机候选。
