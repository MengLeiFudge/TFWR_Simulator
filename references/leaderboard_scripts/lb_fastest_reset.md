# lb_fastest_reset

当前阶段（2026-10-24）：仅精简骨头固定绕环尾段的完整候选seed 0/1均正常结束并解锁Leaderboard；本地均值9912.481057游戏秒，比配对原版10007.049873秒省94.568816秒（0.945%）。两组首次bone_prep前79条日志完全一致。seed 0按已批准的75秒有限预算仅补跑一次，旧55秒停止报告保留；尚未部署此候选，短时实机和游戏打榜时间均未取得。预算以[缓存#10](leaderboard_targets.md)为准。
## 榜单目标

- 目标类型：`fastest_reset`
- 这不是单纯资源榜，而是“以最短时间完成一轮从开局到解锁排行榜 / reset 的完整流程”
- 当前脚本是明确的阶段式路线：前期解锁、能量阶段、奇异物质/金币阶段、后续扩张与排行榜解锁

## 目标判定与核心难点

- reset 榜的成功判定不是“攒够某类资源”，而是“真正解锁 `leaderboard`”。
- 反编译源码 `Core.decompiled.cs` 里，`LeaderboardType.reset` 的完成条件明确写成：
  - `sim.farm.IsUnlocked("leaderboard")`
- 你当前给出的已知门槛是：
  - `leaderboard` 科技需要 `2M bones`
  - `leaderboard` 科技需要 `1M gold`
- 这也是为什么这榜最难：
  - 目标本身很明确
  - 但路径实现方式极多
  - 真正决定成绩的不是“代码写得多花”，而是“节奏、阶段切换、资源与科技的取舍”
- 你当前的实跑观察也很关键：
  - `#1` 已经进入半小时以内
  - 但你自己二十多分钟时还只是运行到 `main2 -> main3` 这一带
  - 这说明榜前玩家大概率不是把相关科技全升满后才去开排行榜
  - 他们一定在“提前进入下一阶段”与“把当前科技继续升高来换效率”之间做了动态平衡

## 当前基线

- 当前默认入口：`main()`
- 当前实现已经完整覆盖：
  - `step1()`：从开局推进到解锁胡萝卜
  - `step2()`：混种并升级速度，直到积累 `1000 power`
  - `step3()`：刷奇异物质并解锁迷宫
  - `try_unlock_early_megafarm()`：用 `6x6` 小迷宫金币提前解锁 `Megafarm 1`
  - `step4()`：借助多无人机南瓜推进 `Expand 6`、仙人掌、恐龙和伴生
  - `step5()`：推进 `Megafarm 3`、`1M gold`、`2M bone` 并解锁排行榜
- 2026-05-30 当前版本复跑：请求 `620` 完整结算 `finished=true runs=1 average=168:48.299`。
- 证据来源：`lb_fastest_reset.py` 当前代码结构

## 通用注意事项下的榜单特化

- 这个榜单的主瓶颈是“解锁顺序、转阶段时机、资源门槛”和“哪些系统值得提前碰”
- 不能把资源榜的“稳定吞吐”模板直接套进来；这里更重要的是最短路径和避免过解锁
- 所有资源都应视作“为了推进下一门槛服务”，而不是单独追求储量
- 这榜最核心的不是“程序技巧”，而是流程取舍：
  - 科技先不开，意味着更早进入后续阶段，但短期效率更低
  - 科技开得更高，意味着前期牺牲时间，但后续效率更高
- 尤其是这几类科技最需要做平衡：
  - 无人机速度
  - 农场大小 / 扩张
  - 无人机数目 / 巨大农场
- 但按你当前给的执行策略，第一版先不讨论“科技不升满”的极限优化，而是先做出一条能稳定跑通的满科技解锁路线

## 当前版本结论

- 当前文件只有一条主线 `main()`
- 已知结论：
  - 早期草 -> 扩张 -> 种植 -> 灌木木头 -> 胡萝卜 是当前起手骨架
  - 中期通过混种和持续解锁推进到 `1000 power`
  - 后续走“南瓜扩张 -> 仙人掌 -> 恐龙 -> 迷宫金币 -> leaderboard”的完整路线
- 当前 `step4()` / `step5()` 已经不是空实现：
  - `step4()` 会解锁南瓜，把扩张推进到 `Expand 6`，再解锁仙人掌和恐龙
  - `step5()` 会先升 `Mazes 2`、凑第一档 `Megafarm`，再补 `1M gold` / `2M bone` 并尝试解锁 `Leaderboard`
- 这不是最终成绩路线；它是第一条可继续观测的完整候选路线。
- 2026-05-30 当前版本复跑已完整结算，当前记录为 `168:48.299`。
- 真实短窗口验证显示，“满扩张”不是合适第一版：
  - `Expand 5` 后下一级需要 `8,000 pumpkin`
  - `Expand 6` 后下一级需要 `64,000 pumpkin`
  - 再继续还要 `512,000 / 4,100,000 pumpkin`
  - 60 秒窗口里，满扩张路线主要时间会被南瓜阶段吞掉
- 因此当前默认路线先在 `Expand 6` 切走，不继续刷 `64,000+` 南瓜扩张。

## 2026-04-24 真实成本探针

- `get_cost(Unlocks.Pumpkins)`：`{Items.Wood:500, Items.Carrot:200}`
- `get_cost(Unlocks.Cactus)`：`{Items.Pumpkin:5000}`
- `get_cost(Unlocks.Dinosaurs)`：`{Items.Cactus:2000}`
- `get_cost(Unlocks.Leaderboard)`：`{Items.Bone:2000000, Items.Gold:1000000}`
- 实体种植成本：
  - `get_cost(Entities.Pumpkin)`：`{Items.Carrot:1}`
  - `get_cost(Entities.Cactus)`：`{Items.Pumpkin:2}`
- 多级科技关键成本：
  - `Expand 4 -> 5`：`1,000 pumpkin`
  - `Expand 5 -> 6`：`8,000 pumpkin`
  - `Expand 6 -> 7`：`64,000 pumpkin`
  - `Expand 7 -> 8`：`512,000 pumpkin`
  - `Expand 8 -> 9`：`4,100,000 pumpkin`
  - `Megafarm`：`2,000 / 8,000 / 32,000 / 128,000 / 512,000 gold`

## 2026-04-24 真实短窗口结论

- 命令：
  - `python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_fastest_reset`
  - `timeout 100s python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 45 --startup-timeout 20 --total-timeout 75 --poll-interval 0.5`
- 45 秒窗口结果：
  - 无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 但能稳定推进到南瓜扩张阶段
  - 一次记录到 `Expand 7 time=8779.61 pumpkin=80`
- 60 秒窗口结果：
  - 无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 在“跳过满扩张”的路线里，曾推进到 `step4 time=10226.29 size=16 cactus=172`
  - 随后进入 `step5` 的奇异物质准备阶段，记录到 `weird=3019 target=1149`
- 结论：
  - `step4()` / `step5()` 现在已经有可执行骨架
  - 当前短板仍是 `step2/step3` 的种子资源警告、南瓜扩张耗时，以及首轮金币阶段效率
  - 下一轮不应回到“满扩张”，应继续压缩 `Expand 7` 之前的南瓜成本，或更早切到恐龙 / 金币阶段

## 2026-04-25 真实短窗口结论

- 计时口径修正：
  - `1min` 是真实游戏 oracle 的外层墙钟保护，只用于避免迭代时误等完整 leaderboard。
  - `fastest_reset` 策略快慢必须按脚本输出的游戏内 `time=`、阶段切换日志和资源增量判断。
  - 多无人机路线可能让真实执行达不到 `200x` 加速；这不能直接当成策略慢的证据。
  - `simulate()` / `leaderboard_run()` 的速度参数只是上限；参数很大时会受机器性能和脚本计算量限制，高计算脚本出现现实 `1s` 只推进游戏内约 `10s` 属于正常现象。
  - 验证时应根据 `reset_stage ... time=` 动态决定是否提前停止：例如金币已达到 `1M`、骨头单轮收益已经可外推、或某条探针在游戏内阶段时间明显落后。
- 命令：
  - `python3 -m py_compile references/leaderboard_scripts/lb_fastest_reset.py`
  - `python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_fastest_reset`
  - `timeout 100s python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 60 --startup-timeout 20 --total-timeout 90 --poll-interval 0.5`
- `request_id=140`：
  - `Mazes 2` + 金币单批 `600` 可以在短窗口推进到 `gold=1000240`。
  - 迷宫金币阶段结束后进入恐龙升级，记录到 `dinosaurs 2 time=11060.65 cactus=15472`。
- `request_id=141`：
  - 金币单批改成 `300` 后，`gold=1000240` 变为 `time=11178.7`。
  - 对比 `600` 批量更慢，因此当前保留 `600`。
- `request_id=142`：
  - 继续升到 `Dinosaurs 4` 需要大量仙人掌，`dinosaurs 4 time=15131.87 cactus=9136`。
  - `Dinosaurs 4` 单轮骨头为 `161312`，但剩余仙人掌不足以持续支付苹果成本，后续出现 `Entities.Apple` 缺种子警告。
- `request_id=143` / `request_id=144`：
  - 把恐龙上限改为 `Dinosaurs 3`，并在每轮骨头前按 `get_cost(Entities.Apple)` 与恐龙等级补足苹果成本。
  - 这两轮只返回了外层 `lb_start` 的 `status=done`，没有 `game_output` 里的 `reset_stage done` 或 leaderboard 平均值证据。
  - 后续发现 `lb_fastest_reset.py` 里残留游戏脚本不支持的 `<<`，因此这两轮不能作为“榜单已完成”的证据。
- `request_id=149`：
  - 直接运行 `lb_fastest_reset` 可以解析并运行到 `reset_stage done`，证明 `<<` 修复后脚本语法路径不再阻塞。
  - 但直接运行继承当前存档资源，不等价于 `Fastest_Reset` 排行榜重置环境，不能作为排行榜完成证据。
- 当前结论：
  - 快速重置当前路线已推进过金币和骨头瓶颈，但真实排行榜完成仍需要新的有效证据。
  - `Expand 7`、`Megafarm 2+`、`Dinosaurs 4+` 都是已验证不适合当前默认路线的过度投资。
  - `Mazes 2` 仍保留，因为它减少金币阶段的宝箱迁移次数；金币单批 `600` 在 `300 / 600 / 1200` 中当前证据最好。
- 提交后继续 A/B：
  - `request_id=145`：外层 `lb_start` 墙钟约 `9.64s`，但因缺少榜单结果证据，不能视为完成成绩。
  - `request_id=146`：跳过 `Mazes 2` 外层墙钟约 `9.98s`，暂不采用。
  - `request_id=147`：只升到 `Dinosaurs 2` 外层墙钟约 `10.60s`，暂不采用。
  - `request_id=148`：金币单批 `450` 外层墙钟约 `10.62s`，暂不采用。
- `request_id=166`：
  - 这轮按游戏内 `time=` 重新评估，不再用外层 `60s` timeout 判定策略优劣。
  - `gold=1000560` 出现在 `time=10246.49`。
  - `Dinosaurs 2` 解锁出现在 `time=10246.58`。
  - 骨头阶段在 `time=10438.42` 达到 `bone=40328`，在 `time=11691.57` 达到 `bone=282296`。
  - 对比无恐龙升级路线同类窗口只到约 `bone=120984`，`Dinosaurs 2` 按游戏内时间是正收益。
- `request_id=167`：
  - `Dinosaurs 3` 解锁出现在 `time=11367.47`，比 `Dinosaurs 2` 多付出仙人掌准备时间。
  - 骨头阶段在 `time=11582.07` 达到 `bone=80656`，在 `time=14274.83` 达到 `bone=1129184`。
  - 按游戏内 `time=` 外推，`Dinosaurs 3` 的单轮骨头收益明显优于 `Dinosaurs 2`。
  - 该轮暴露了新问题：后续出现 `没有种植 Entities.Apple 所需的物品`，说明每轮恐龙前只补了一颗苹果成本，没有按整轮尾长预留苹果成本。
- `request_id=168`：
  - `Dinosaurs 3` 后不再出现 `Entities.Apple` 缺材料警告，说明按整轮尾长预留苹果材料是正确方向。
  - 骨头推进到 `time=13753.87 bone=887216` 后，开始反复小额补仙人掌；这暴露了“每轮补苹果材料”会把骨头阶段切碎。
- `request_id=169`：
  - 改为按剩余骨头轮数提前预留苹果材料，可以跑到 `reset_stage done time=17160.82`。
  - 但该版把苹果成本又按 `Dinosaurs 3` 乘了 `4`，最终剩余约 `92848 cactus`，属于明显过量预留。
- `request_id=170`：
  - 金币单机批量从 `600` 改为 `900` 后，`Megafarm 3 -> gold 1M` 净耗时约 `6995`。
  - 对照 `request_id=169` 同段约 `6865`，`900` 批量不采用，保留 `600`。
  - 2026-04-26 补充：这是旧前期结构下的结论；接入早期 `Megafarm 2` 和多无人机南瓜后，需要重新验证金币批次。
- `request_id=171`：
  - 打开现有多无人机金币实现后，到 `time=14005.09` 只有 `gold=230448`。
  - 同阶段单机迷宫金币已经能到 `1M`，因此当前这版多机金币不是正收益；问题在共享宝箱与重复补奇异物质，不是外层墙钟误判。
- `request_id=172`：
  - 增加 `plant_if_affordable(...)` 和施肥数量守卫后，前期胡萝卜 / 肥料 / 向日葵警告消失。
  - 该轮跑到 `reset_stage done time=17174.86`，说明警告清理不破坏主路线，但主要收益来自稳定性而不是总时间。
- `request_id=173`：
  - 移除苹果成本上的错误恐龙等级倍率后，`bone_prep` 只补到 `cactus=37360`，最终剩余 `cactus=9904`。
  - 无 `Entities.Apple` 警告，并跑到 `reset_stage done time=16479.57`。
  - 当前采用该路线：`Dinosaurs 3` + 按剩余骨头轮数预留苹果材料 + 苹果成本不乘恐龙等级。
- `request_id=174`：
  - 尝试在奇异物质阶段跳过自动草收割、直接覆种树，跑到 `reset_stage done time=16725.91`。
  - 相比 `request_id=173` 退步，说明当前真实行为下“先收割再种树”更稳；该 A/B 已回退。
- `request_id=175`：
  - 当前默认路线可跑到 `reset_stage done time=16512.99`。
  - 关键阶段：`step2 time=1312.43 power=1001.82`、`Megafarm 3 time=3777.95`、`gold 1M time=10452.55`。
  - 这轮确认 `Power` 在后段会归零，但没有主动补电。
- `request_id=177`：
  - 在 `Megafarm 3` 后主动补到 `3000 Power`，`power_start time=3808.26 power=0`，`power time=6003.77 power=3054.75`。
  - 单独补电净耗约 `2195` 游戏秒，`gold 1M time=11103.21`，比不补电更慢；该方向不采用。
- `request_id=179`：
  - 把 `step2` 的 `Power` 目标提高到 `3000`，`step2 time=1807.64 power=3011.09`，但到 `Megafarm 3` 后仍归零。
  - 后续 `gold 1M time=16525.87`，总完成 `reset_stage done time=22523.38`，明显退步；该方向已回退。
  - `apple_prep_start` 显示苹果成本只需要 `Cactus`，`hay_need/wood_need/carrot_need/pumpkin_need` 均为 `0`，所以骨头阶段不是后段割草根因。
- `request_id=180`：
  - 保持 `step2` 目标 `1000 Power`，在奇异物质阶段空闲格尝试顺手补太阳花。
  - 真实完成 `reset_stage done time=16365.53`，略优于 `request_id=173/175`；但 `Power` 仍在后段为 `0`，说明当前资源结构下没有足够胡萝卜支撑顺手补太阳花。
  - 当前采用：不再做后段清场补电，保留 `Power` / 苹果成本日志，避免再次误判“补电一定正收益”。
- `request_id=185` / `request_id=186`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 比较树、伴生树、南瓜获取 `Weird_Substance` 的效率。
  - 普通感染树 16 株平均约 `2940 weird / 1000 tick`，逐棵伴生树平均约 `2657 weird / 1000 tick`。
  - 普通 `8x8` 感染南瓜田只有约 `232 weird / 1000 tick`；修复死南瓜并形成完整巨型南瓜后，`6x6` 约 `832 weird / 1000 tick`、`8x8` 约 `806 weird / 1000 tick`。
  - 结论：南瓜确实能获取奇异物质，但即使满足 `>=6x6` 巨型南瓜条件，专门刷 `Weird_Substance` 仍明显慢于树；南瓜只适合在需要南瓜本体时顺带产出奇异物质。
- `request_id=187` / `request_id=188` / `request_id=189`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 专测批量伴生树，比较普通树、批量补 companion、种树后先施 1 次肥再批量补 companion、逐棵伴生等路线。
  - 测试前提后来确认是 `Polyculture 1`、`Trees 10`；因此这组结论只能排除低级伴生，不能外推到高等级伴生。
  - `request_id=189` 同场均值：`sequential_plain_8_sparse16` 约 `2951 weird / 1000 tick`，`batch_preinfect_8_sparse16` 约 `2965 weird / 1000 tick`，只高约 `0.5%`；同时平均 `conflict_companions=3.00`、`blocked_companions=0.75`，实现复杂度明显更高。
  - 大田结果反而退步：`plain_12_sparse36` 约 `3068 weird / 1000 tick`，`batch_preinfect_12_sparse36` 约 `2344 weird / 1000 tick`。
  - 未预感染的批量伴生树会因为补 companion 时间过长导致树自然成熟，后续无法用肥料感染，`batch_companion_12_sparse36` 的 `weird_delta=0`。
  - 结论修正：`Polyculture 1` 下批量伴生树没有形成稳定、明显的 `Weird_Substance` 效率优势；正式脚本是否要引入 companion 需要看更高伴生等级和解锁成本。
- `request_id=195`：
  - 固定 `Trees 10`，分别测试请求 `Polyculture 1/3/6`；真实输出显示请求 `6` 会钳到 `Polyculture 5`，因此满级应为 `5`。
  - `Polyculture 1`：`batch_preinfect_8_sparse16` 约 `2789 weird / 1000 tick`，`sequential_plain_8_sparse16` 约 `2796`，小图也没有优势；`12x12` 明显落后。
  - `Polyculture 3`：`batch_preinfect_8_sparse16` 约 `10967`，`sequential_plain_8_sparse16` 约 `9552`，小图约 `+14.8%`；`12x12` 约 `9788` vs `9755`，基本持平。
  - `Polyculture 5`：`batch_preinfect_8_sparse16` 约 `43677`，`sequential_plain_8_sparse16` 约 `36574`，小图约 `+19.4%`；`12x12` 约 `38933` vs `37449`，约 `+4.0%`。
  - 结论口径修正：快速重置看收益曲线，`Polyculture 3` 的普通树效率已经从 `Polyculture 1` 的约 `2796` 提到约 `9552`，约 `3.4x`；`Polyculture 5` 的普通树效率约 `36574`，约 `13.1x`。
  - 因此 `Polyculture` 本身应进入快速重置的高优先级科技，而不是只看批量伴生相对普通树的边际收益。
  - 批量预感染伴生树在伴生等级提高后继续提供额外收益，`Polyculture 3/5` 的 `8x8/16 株` 分别约 `+14.8%` / `+19.4%`；因此只要路线已经决定刷伴生科技，批量伴生策略也应作为默认 Weird 产线候选，而不是失败对照。
- `request_id=196`：
  - 成本 probe 显示 `Polyculture 0 -> 1` 成本是 `{Items.Pumpkin:3000}`。
  - `Polyculture 1 -> 2` 成本是 `{Items.Bone:10000}`，所以快速重置在骨头阶段前实际只能稳定使用 `Polyculture 1`。
  - 结论：先把 `Polyculture 1` 接入南瓜阶段；更高伴生等级无法提前服务金币前的 Weird 产线，除非路线结构发生大改。
- `request_id=197`：
  - 正式路线在 `step4()` 把南瓜目标从 `5000` 提到 `8000`，先解锁 `Cactus`，再用剩余南瓜解锁 `Polyculture 1`。
  - 真实输出 `polyculture 1 time=2729.52 pumpkin=784`，额外南瓜成本没有吞掉节奏。
  - 后续 `gold 1M time=8364.55`，明显优于之前 `request_id=190` 的 `gold 1M time=10437.83`。
  - 最终跑到 `reset_stage done time=14521.64`，优于此前 `request_id=180` 的 `done time=16365.53`；该改动保留。
- `request_id=198`：
  - 在 `Polyculture 1` 已接入后，临时把 `upgrade_mazes_for_gold()` 的目标从 `Mazes 3` 降到 `Mazes 2`。
  - 真实输出最终 `reset_stage done time=17331.81`，明显慢于 `request_id=197` 的 `14521.64`。
  - 结论：`Polyculture 1` 改善了 Weird 成本曲线，但还不足以让跳过 `Mazes 3` 变成正收益；正式路线继续保留 `Mazes 3`。
- `request_id=199`：
  - 在 `Polyculture 1` 正式路线基础上，`farm_weird_substance_worker()` 对树位调用 `get_companion()`，只在同一无人机列负责的奇偶空格补 companion。
  - 真实输出 `gold 1M time=7885.12`，`reset_stage done time=13944.29`。
  - 对比 `request_id=197` 的 `14521.64` 明显正收益；说明即使只有 `Polyculture 1`，正式全路线里显式补 companion 也值得保留。
- `request_id=200`：
  - 放宽 `request_id=199` 的列限制，允许跨列补 companion，但仍只补奇偶空格，避免覆盖树位。
  - 真实输出 `gold 1M time=7349.45`，`reset_stage done time=13409.57`，继续优于同列版 `13944.29`。
  - 当前保留跨列补 companion 版本；它提高了 Weird 产线，也顺带保留了更多 `Carrot`，没有引入新的缺材料警告。
- `request_id=201`：
  - 按“骨头阶段棋盘太小”的怀疑，临时改成 `gold 1M` 之后再补 `Expand 7`，希望用 `16x16` 恐龙棋盘减少骨头轮数。
  - 真实输出 `gold 1M time=7863.17`，随后在 `12x12` 上刷 `64000 Pumpkin`，到 `expand_bones 7 time=13758.78` 才完成。
  - 超时前只推进到 `dinosaurs 2 time=13758.87`，没有进入有效骨头循环；尾部持续南瓜/基础资源采集，被用户观察为“像无限收草”。
  - 结论：金币后补 `Expand 7` 仍被 `64000 Pumpkin` 成本吞掉，不能作为主线；如果要继续处理骨头瓶颈，优先测试更便宜的 `Dinosaurs 4`，而不是继续冲大地图。
- `request_id=202`：
  - 临时把骨头前恐龙科技目标从 `Dinosaurs 3` 提到 `Dinosaurs 4`。
  - 真实输出最终 `reset_stage done time=14979.76`，慢于 `request_id=200` 的 `13409.57`。
  - 结论：`Dinosaurs 4` 的 `432000 Cactus` 成本高于骨头轮数减半收益；正式路线继续停在 `Dinosaurs 3`。
- `request_id=203`：
  - 临时在金币迷宫每 300 次 Treasure 重定位后调用 `harvest_treasure_once()`，尝试补拿第 301 份最终宝箱收益。
  - 真实输出最终 `reset_stage done time=14051.74`，慢于 `request_id=200` 的 `13409.57`。
  - 结论：最终宝箱收益太小，额外寻路 / 收割 / 清场成本不值；已回退。
- `request_id=326`：
  - 参考单迷宫 `dfs_bfs` 的验证结论，临时禁用金币迷宫里的 `move_direct_toward_treasure()`，强制完整图 BFS 寻宝。
  - 真实输出 `gold 1M time=7849.40`，慢于当前正式基线 `request_id=200` 的 `gold 1M time=7349.45`。
  - 中途停止前骨头阶段推进到 `bone=1613120`，停止摘要 `finished=false runs=1 average=215:12.520`；该候选已回退。
  - 结论：单迷宫中直线贪心不占优，但快速重置金币阶段的 `12x12` 迷宫和墙消失收益不同，当前正式路线继续保留直线优先 + BFS 兜底。
- `request_id=329`：
  - 临时把 `STEP2_POWER_TARGET` 降为 `0`，同时新增 `step2_core_unlocks_ready()`，确保 `Speed 5 / Expand 4 / Trees / Watering / Fertilizer / Sunflowers` 仍解锁后才退出 `step2()`。
  - 真实输出 `step2 time=1211.21 power=112.36 size=6`，比正式基线 `step2 time=1312.43 power=1001.82` 早约 `101s`。
  - 但后续 `Megafarm 3 time=4628.30`，明显慢于正式基线 `Megafarm 3 time=3777.95`；该候选已回退。
  - 结论：不能简单取消 `1000 Power` 前置；前期少刷的 `Power` 会让 `step3/step4` 的南瓜、仙人掌和早期金币整体降速，省下的 `101s` 覆盖不了后续损失。
- `request_id=330`：
  - 在 `step3()` 后插入 `try_unlock_early_megafarm()`，用 `6x6` 小迷宫金币先刷到 `2000 gold`，提前解锁 `Megafarm 1`。
  - `farm_pumpkins_until()` 在 `max_drones() > 1`、地图 `>=6x6` 且缺口超过一整图时，改用多无人机按列并行种植、修补死南瓜和收割。
  - 真实输出 `early_megafarm 1 time=1646.66 gold=16 max_drones=2`，随后并行南瓜把 `expand 6 time=1994.53`，明显优于 `request_id=329` 的 `2557.62`。
  - 中段输出 `megafarm 3 time=3523.49`，优于正式基线 `3777.95`；`gold 1M time=7289.27`，略优于正式基线 `7349.45`。
  - 最终输出 `[lb_fastest_reset] finished=true runs=1 average=221:46.199`，同轮 `reset_stage done time=13306.14`，优于 `request_id=200` 的 `13409.57`。
  - 当前保留：早期 `Megafarm 1` + 多无人机南瓜是正收益；它主要压缩 `step4` 和 `Megafarm 3` 之前的节奏，不改变后段金币 / 骨头主结构。
- `request_id=331`：
  - 把 `try_unlock_early_megafarm()` 从只解锁 `Megafarm 1` 扩展到 `Megafarm 2`，继续用 `6x6` 小迷宫刷到第二级所需金币。
  - 真实输出 `early_megafarm 2 time=1765.06 gold=8 max_drones=4`；虽然额外金币投入约 `125s`，但后续 `step4 time=2547.29`，快于 `request_id=330` 的 `2605.77`。
  - 更关键的是 `Megafarm 3 time=3353.48`、`gold 1M time=6769.67`，分别优于 `request_id=330` 的 `3523.49` / `7289.27`。
  - 最终输出 `[lb_fastest_reset] finished=true runs=1 average=216:26.969`，同轮 `reset_stage done time=12986.9`，继续优于 `request_id=330` 的 `13306.14`。
  - 当前保留：早期推到 `Megafarm 2` 是明确正收益；它证明“先用小迷宫买更多无人机，再滚南瓜 / Weird / 金币”这条结构路线成立。
- `request_id=335/336`：
  - 在 `request_id=331` 路线基础上，把 `farm_gold_single_cycle()` 的批次上限从 `600` 提到 `900`，即每次 Weird 预采覆盖 `3` 个 300 次迷宫周期。
  - `request_id=335` 输出 `gold 1M time=6899.86`、`done time=12944.26`、`average=215:44.299`，刷新当前本地最好。
  - `request_id=336` 复跑输出 `gold 1M time=7013.02`、`done time=12997.38`、`average=216:37.399`；两轮差距约 `0.41%`，低于 `10%` 继续运行阈值。
  - 当前保留：在新前期结构下，`900` 批次虽然不稳定压低 `gold 1M`，但两轮均值约 `216:10.849`，仍优于旧 `216:26.969`；正式路线改为 `900`。
- `request_id=337/338`：
  - 临时把 `WEIRD_POWER_FLOOR` 从 `500` 提到 `1500`，目标是在 Weird 阶段顺手保留更多 `Power`，不单独清场补电。
  - `request_id=337` 完整结算，输出 `gold 1M time=6797.53`、`done time=12876.89`、`average=214:36.899`，单轮优于 `request_id=335`。
  - `request_id=338` 复跑在 `120s` 墙钟超时前仍未完成，输出 `gold 1M time=10083.89`，停止摘要 `[lb_fastest_reset] finished=false runs=1 average=241:14.740`。
  - 结论：`1500` 地板单轮有正向波动，但复跑超过 `10%` 退步且未完整结算，不满足两轮稳定采用规则；当前回退到 `WEIRD_POWER_FLOOR=500`，只保留证据，不刷新 `lb_start.py` 本地最好时间。
- `request_id=340`：
  - 临时把 `farm_gold_single_cycle()` 批次上限从 `900` 提到 `1200`，目标是减少金币阶段 Weird 补给批次数。
  - 真实输出 `gold 1M time=7687.93`，慢于 `request_id=335/336` 的 `6899.86` / `7013.02`。
  - 主动停止前摘要 `[lb_fastest_reset] finished=false runs=1 average=223:06.250`，骨头阶段仍未完成。
  - 结论：`1200` 批次会在 Megafarm 3 后过量预采 Weird，把金币阶段拖慢；当前回退并继续保留 `900`。
- `request_id=341/342`：
  - 临时把 `WEIRD_POWER_FLOOR` 从 `500` 提到 `1000`，目标是在 Weird 阶段顺手保留更多 `Power`，但不采用 `1500` 那种会显著拉长补给的地板。
  - `request_id=341` 完整结算，输出 `step2 time=1290.01`、`megafarm 3 time=3511.85`、`gold 1M time=6662.25`、`dinosaurs 3 time=7339.98`、`done time=12746.67`、`average=212:26.699`。
  - `request_id=342` 复跑完整结算，输出 `step2 time=1365.18`、`megafarm 3 time=3548.06`、`gold 1M time=6929.51`、`dinosaurs 3 time=7619.70`、`done time=13006.78`、`average=216:46.799`。
  - 两轮差距约 `2.0%`，低于 `10%` 继续采样阈值；两轮均值约 `214:36.749`，优于 `request_id=335/336` 的两轮均值约 `216:10.849`。
  - 当前保留：`WEIRD_POWER_FLOOR=1000` 是稳定正收益；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:32:26.699`。
- `request_id=349/350`：
  - 在 `WEIRD_POWER_FLOOR=1000` 的稳定路线基础上，把 Weird 阶段顺手补电地板继续提高到 `1250`，仍然不做单独清场补电。
  - `request_id=349` 完整结算，输出 `step2 time=1399.06`、`megafarm 3 time=3635.67`、`gold 1M time=6690.76`、`dinosaurs 3 time=7024.07`、`done time=12556.77`、`average=209:16.799`。
  - `request_id=350` 复跑完整结算，输出 `step2 time=1378.47`、`megafarm 3 time=3635.77`、`gold 1M time=6908.67`、`dinosaurs 3 time=7634.63`、`done time=12945.17`、`average=215:45.199`。
  - 两轮差距约 `3.1%`，低于 `10%` 继续采样阈值；两轮均值约 `212:30.999`，优于 `request_id=341/342` 的两轮均值约 `214:36.749`。
  - 当前保留：`WEIRD_POWER_FLOOR=1250` 是新的稳定最好；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:29:16.799`。
- `request_id=351/352`：
  - 在 `WEIRD_POWER_FLOOR=1250` 的稳定路线基础上，把 Weird 阶段顺手补电地板继续提高到 `1350`，仍然不做单独清场补电。
  - `request_id=351` 完整结算，输出 `early_megafarm 2 time=1791.76`、`expand 6 time=2123.77`、`step4 time=2575.03`、`mazes 3 time=3169.92`、`megafarm 3 time=3421.91`、`gold 1M time=6652.18`、`dinosaurs 3 time=7334.75`、`done time=12693.07`、`average=211:33.099`。
  - `request_id=352` 复跑完整结算，输出 `early_megafarm 2 time=2071.52`、`expand 6 time=2404.12`、`step4 time=2864.79`、`mazes 3 time=3447.02`、`megafarm 3 time=3697.21`、`gold 1M time=6771.83`、`dinosaurs 3 time=7195.97`、`done time=12639.57`、`average=210:39.599`。
  - 两轮差距约 `0.42%`，低于 `10%` 继续采样阈值；两轮均值约 `211:06.349`，优于 `request_id=349/350` 的两轮均值约 `212:30.999`。
  - 当前保留：`WEIRD_POWER_FLOOR=1350` 是新的稳定最好；但当前最好单轮仍是 `request_id=349` 的 `3:29:16.799`，所以不刷新 `lb_start.py` 本地实测时间。
- `request_id=357/358`：
  - 修复 `farm_gold_single_cycle()` 的批次循环边界：当 `remaining_paid_move_count` 刚好降到 `0` 时，不再额外 `clear()`、开迷宫、探图但执行 `0` 次 Treasure。
  - `request_id=357` 完整结算，输出 `step2 time=1330.70`、`early_megafarm 2 time=1916.13`、`step4 time=2720.55`、`mazes 3 time=3309.57`、`megafarm 3 time=3588.80`、`gold 1M time=6661.66`、`dinosaurs 3 time=7375.67`、`done time=12721.99`、`average=212:01.999`。
  - `request_id=358` 完整结算，输出 `step2 time=1305.69`、`early_megafarm 2 time=1764.25`、`step4 time=2558.85`、`mazes 3 time=3199.73`、`megafarm 3 time=3483.86`、`gold 1M time=6490.07`、`dinosaurs 3 time=7182.89`、`done time=12570.11`、`average=209:30.176`。
  - 两轮差距约 `1.19%`，低于 `10%` 继续采样阈值；两轮均值约 `210:46.087`，略优于 `request_id=351/352` 的 `211:06.349`。
  - 当前保留：金币批次 `0` 次额外迷宫确认为真实浪费，应删除；但当前最好单轮仍是 `request_id=349` 的 `3:29:16.799`，所以不刷新 `lb_start.py` 本地实测时间。
- `request_id=359/360`：
  - 修正 `farm_gold_single_cycle()` 的单次 Treasure 金币估算：每次付费重定位收益应为 `maze_size * maze_size * maze_multiplier`，不是只按 `maze_size * maze_size` 计算。
  - 直接效果是 12x12、`Mazes 3` 后的 Weird 目标从约 `10752/每 100 万金币批次` 降为实际需要的 `2736/早期 Megafarm 3`、`43344 + 40272/1M 金币两批`，避免按未乘迷宫倍率的错误值过量预采。
  - `request_id=359` 完整结算，输出 `step2 time=1346.18`、`early_megafarm 2 time=1834.58`、`step4 time=2621.97`、`mazes 3 time=3201.40`、`megafarm 3 time=3414.02`、`gold 1M time=6628.71`、`dinosaurs 3 time=6981.48`、`done time=12209.01`、`average=203:29.064`。
  - `request_id=360` 完整结算，输出 `step2 time=1403.93`、`early_megafarm 2 time=1957.28`、`step4 time=2736.60`、`mazes 3 time=3323.75`、`megafarm 3 time=3550.96`、`gold 1M time=6701.45`、`dinosaurs 3 time=7038.43`、`done time=12414.86`、`average=206:54.899`。
  - 两轮差距约 `1.67%`，低于 `10%` 继续采样阈值；两轮均值约 `205:11.982`，明显优于 `request_id=357/358` 的 `210:46.087`。
  - 当前保留：金币收益估算必须包含 `Mazes` 倍率；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:23:29.064`。
- `request_id=366/367`：
  - 在 `goto_treasure_with_graph()` 中取消每轮开头的整图 `refresh_maze_edges(graph, size)`，只保留直线试探时的局部边更新，以及图路径兜底。
  - 依据：迷宫墙只会消失，不会新增；旧图路径不会因为少刷边而失效，整图刷新会在每次 Treasure 寻路前重复做大量 `can_move()`。
  - `request_id=366` 完整结算，输出 `gold 1M time=6532.89`、`dinosaurs 3 time=6956.69`、`done time=12408.28`、`average=206:48.299`。
  - `request_id=367` 完整结算，输出 `step2 time=1424.01`、`early_megafarm 2 time=2017.73`、`step4 time=2773.68`、`mazes 3 time=3383.00`、`megafarm 3 time=3625.45`、`gold 1M time=6562.11`、`dinosaurs 3 time=6918.32`、`done time=12113.40`、`average=201:53.465`。
  - 两轮差距约 `2.41%`，低于 `10%` 继续采样阈值；两轮均值约 `204:20.882`，优于 `request_id=359/360` 的 `205:11.982`。
  - 当前保留：快速重置金币阶段同样不应每轮刷新整图墙；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:21:53.465`。
- `request_id=368/369`：
  - 将骨头阶段从固定蛇形全场扫描改为复用 `lb_dinosaur.py` 的“前期追苹果 + 后期安全路径”结构。
  - 依据：反编译 `DinosaurHat.OnMove()` 显示每吃一个苹果后移动成本降低 `3%`；越早吃到苹果，后续每一步都受益。固定蛇形平均吃苹果步数过高，没有利用早期苹果的复利收益。
  - `request_id=368` 完整结算，输出 `gold 1M time=6477.64`、`dinosaurs 3 time=6818.59`、`done time=9881.43`、`average=164:41.493`。
  - `request_id=369` 完整结算，输出 `gold 1M time=6143.85`、`dinosaurs 3 time=6826.62`、`done time=9985.42`、`average=166:25.484`。
  - 两轮差距约 `1.05%`，低于 `10%` 继续采样阈值；两轮均值约 `165:33.489`，明显优于 `request_id=366/367` 的 `204:20.882`。
  - 当前保留：骨头阶段必须利用恐龙榜的前期追苹果结构；`lb_start.py` 本地实测时间刷新为当前最好单轮 `2:44:41.493`。
- `request_id=370`：
  - 只把追苹果阈值从 `size * size / 3` 提到 `size * size / 2`，验证是否更长时间追苹果能继续加速。
  - 结果：完整结算 `gold 1M time=6846.93`、`dinosaurs 3 time=7190.25`、`done time=10275.23`、`average=171:15.290`，慢于 `request_id=368/369`。
  - 结论：阈值 `1/2` 不采用，当前回退并保留 `1/3`；追苹果过久会增加路径绕行和后期风险成本。
- `request_id=345/346`：
  - `request_id=345` 直接把 `STEP2_POWER_TARGET` 改为 `0`，导致 `step2()` 不执行，树等关键科技未解锁，脚本立即运行时报错；这是无效探针。
  - `request_id=346` 修正为“达到 `6x6` 和关键科技后退出 step2，不额外刷 `1000 Power`”。
  - 结果：`step2 time=1085.20`，确实比请求 `341/342` 的 `1290.01/1365.18` 少约 `205~280s`。
  - 但后续 `Megafarm 3 time=4839.46`，明显慢于请求 `341/342` 的 `3511.85/3548.06`。
  - 主动停止前 `weird_parallel` 已到 `time=5896.14`，仍在补 `43,344 Weird_Substance`，说明前置电力和伴随资源不足会被后段 Weird 产线放大偿还。
  - 结论：不采用取消前置电力；`STEP2_POWER_TARGET` 回退并继续保留 `1000`。

## 第二轮结构重写策略校正

- 已落地并保留：
  - `6x6` 小迷宫早期金币推进 `Megafarm 1`：请求 `330` 证明正收益。
  - `6x6` 小迷宫早期金币推进 `Megafarm 2`：请求 `331` 继续证明正收益。
  - `900` 金币批次：请求 `335/336` 两轮差异约 `0.41%`，优于旧批次。
  - `WEIRD_POWER_FLOOR=1350`：请求 `351/352` 两轮差异约 `0.42%`，刷新当前稳定最好。
- 已证伪，不应重复：
  - 取消前置 `1000 Power`：请求 `346` 证明后段 Weird / Megafarm 节奏明显变慢。
  - 早期小迷宫直接推到 `Megafarm 3`：请求 `332` 证明前置金币成本覆盖不了收益。
  - 金币阶段 BFS-only：请求 `326` 证明 `12x12` 金币阶段仍需要直线优先 + BFS 兜底。
  - `Mazes 2` 替代 `Mazes 3`：请求 `198` 证明金币阶段次数增加不值。
  - `Dinosaurs 4`、`Expand 7`、多无人机恐龙：请求 `202/192/201/191` 均已证伪。
- 仍可测的结构变量：
  - 金币阶段的轻量路径缓存：不能做完整全对路径表，应只缓存首步或最近 BFS 结果，避免 `Maze Single` 请求 `325` 的 `table_time` 问题在 `12x12` 上放大。
  - 金币阶段的 Treasure 延迟利用：当前直线优先能吃到墙消失收益，但仍需验证等待期间是否能做低成本刷新，而不是空等或重建全图。
  - Weird 产线的 companion 布局：`Polyculture 1` 与跨列补 companion 已是正收益，后续只测更低调度成本的布局，不再测试南瓜专职 Weird。
- `request_id=204`：
  - 回退 `Expand 7`、`Dinosaurs 4`、最终宝箱补收后，用当前保留版本复测。
  - 真实 `output.txt` 有完整 `reset_stage done time=14018.42`；`run_real_game_script.py` 本轮没有抓到 `game_output` 正文，但文件尾部证明脚本完成且状态已回到 `idle`。
  - 结论：当前代码没有残留失败候选；单轮随机波动下仍慢于 `request_id=200`，所以历史最佳证据继续看 `request_id=200`，代码结构保持同一版。
- `request_id=190`：
  - 当前 Expand 6 路线短跑到 `gold 1M time=10437.83`，随后骨头阶段在 75 秒墙钟窗口推进到 `bone=1371152` 后超时。
  - 这轮确认当前短窗口未完成的主因已经转向骨头循环；金币阶段仍是大段耗时，但不是本轮停止点。
- `request_id=191`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 测多无人机恐龙，单机 `12x12` 一轮为 `bone_delta=80656`、`bone_per_1000tick=116.11`。
  - 多机尝试直接报错：`恐龙帽只有一个，而且已在使用中。无法将其用于第二架无人机上。`
  - 结论：骨头阶段不能简单用多无人机并行恐龙；除非找到非恐龙帽的骨头路线，否则正式脚本继续单机恐龙。
- `request_id=192`：
  - 把 `step4()` 临时改为推进到 `Expand 7`，验证更大棋盘是否能抵消南瓜成本。
  - 结果到 `time=8649.02` 才刚 `expand 7`，期间 `64000` 南瓜成本吞掉大量时间并触发一次 `Entities.Carrot` 缺材料警告。
  - 对比 Expand 6 路线同窗口已进入金币 / 骨头阶段，Expand 7 明显退步；已回退到 `Expand 6`。
- `request_id=193` / `request_id=194`：
  - 尝试把骨头阶段改成“一次预留剩余轮数苹果成本后，连续跑完多轮恐龙”，减少重复换帽和循环检查。
  - 两次短跑都只输出到 `bone_prep cycles=25`，在 `125s` 请求窗口内没有产生 `bones_batch` 或完成输出，无法证明变快，且可观测性差。
  - 结论：该改法已回退；骨头阶段继续保持每轮恐龙后输出进度，便于短窗口动态判断。

## 失败对照

- 文件里已经保留了一段被注释掉的金币循环
- 原因很明确：会因为奇异物质不足而死循环
- 这说明 `fastest_reset` 里不能把“资源前提不满足的阶段跳转”直接当成理所当然
- “满扩张后再进后续阶段”
  - 真实短窗口显示这个方向会被 `512,000 / 4,100,000 pumpkin` 吞掉
  - 当前不再作为默认路线，只保留为失败对照
- “一开始就直接做科技取舍最优解”
  - 这条线当前不适合当第一版目标
  - 因为在还没有一条完整可跑通路线之前，先卷科技不升满只会把问题空间放大得过早
- “当前这版多无人机金币”
  - `request_id=171` 证明现有实现到 `time=14005.09` 只有 `gold=230448`
  - 不是因为真实墙钟慢，而是游戏内 `time=` 与资源增量都落后；除非重写为更少共享宝箱寻路 / 更少奇异物质补给，否则不作为默认路线
- “苹果成本按恐龙等级再乘一次”
  - `request_id=169` 能完成，但最终剩余约 `92848 cactus`
  - 真实每轮 D3 骨头只消耗约 `1144 cactus` 的苹果材料，额外乘 `4` 是过量预留
- “奇异物质阶段跳过自动草收割直接覆种树”
  - `request_id=174` 总时间退到 `16725.91`
  - 当前保留先收割再种树的实现
- “主动清场补 `Power`”
  - `request_id=177` 补到 `3000 Power` 净耗约 `2195` 游戏秒，金币阶段仍更慢
  - `request_id=179` 把前期目标提到 `3000 Power` 后总时间退到 `22523.38`
  - 当前结论：`Power` 归零是事实，但主动补电成本高于后段收益；后续只能考虑不触发额外草/胡萝卜链的顺手补电
- “专门用南瓜刷 `Weird_Substance`”
  - `request_id=185/186` 显示完整 `6x6/8x8` 感染南瓜田可以产出大量奇异物质，但单位 tick 效率只有树的约三成以内
  - 当前不把南瓜作为专职奇异物质来源；更值得继续测试的是批量伴生树，而不是继续优化南瓜 Weird 路线
  - 2026-04-25 补充结论：南瓜 Weird 路线到此先停止投入；下一轮只用 `gamesave/simulate.py` / `gamesave/test.py` 做批量伴生树 probe，确认“批量补 companion 后统一施肥收割”能否压过普通感染树，再决定是否改正式 `lb_fastest_reset.py`
- “批量伴生树刷 `Weird_Substance`”
  - `request_id=187/188/189` 只覆盖 `Polyculture 1`、`Trees 10`，原先“批量伴生树整体排除”的结论过强
  - `request_id=195` 显示 `Polyculture` 等级本身是主收益曲线：`Polyculture 3` 的普通树 Weird 效率约为 `Polyculture 1` 的 `3.4x`，`Polyculture 5` 约为 `13.1x`
  - 批量预感染伴生树在高伴生等级上还会进一步抬高收益：小图 `8x8/16 株` 在 `Polyculture 3/5` 分别约 `+14.8%` / `+19.4%`
  - `request_id=196/197` 已确认 `Polyculture 1` 可用 `3000 Pumpkin` 提前接入，并把完成时间压到 `14521.64`
  - 当前结论：`Polyculture 1` 保留为正式路线；高等级 `Polyculture` 虽然收益曲线很强，但 `2+` 级需要骨头，暂时不能服务前置 Weird / 金币阶段
- “多无人机恐龙骨头”
  - `request_id=191` 真实报错 `恐龙帽只有一个`，不能把恐龙帽同时给第二架无人机
  - 当前结论：骨头阶段不能按“无人机数 x N”直接并行
- “`Dinosaurs 4`”
  - `request_id=202` 完成时间退到 `14979.76`
  - 当前结论：`432000 Cactus` 成本不值，继续保留 `Dinosaurs 3`
- “Expand 7 换更大恐龙棋盘”
  - `request_id=192` 显示 `64000` 南瓜成本到 `time=8649.02` 才完成，远慢于 Expand 6 路线进入金币 / 骨头阶段
  - `request_id=201` 改成金币后再补 `Expand 7`，仍到 `time=13758.78` 才完成扩张，随后还没形成有效骨头收益
  - 当前结论：Expand 7 仍不回到默认路线；最大扩张更不应直接测试，除非先把南瓜收益曲线整体改掉
- “只升到 `Mazes 2`”
  - `request_id=198` 在 `Polyculture 1` 正式路线基础上完成时间退到 `17331.81`
  - 当前结论：`Mazes 3` 仍是金币阶段默认配置，不再把 `Mazes 2` 当成当前主线
- “金币迷宫 300 次后补收最终宝箱”
  - `request_id=203` 完成时间退到 `14051.74`
  - 当前结论：不补收最终宝箱，继续靠重定位金币推进
- “按迷宫等级倍率下调金币重定位次数估算”
  - `request_id=333` 先误把单次金币收益估成 `size * size * substance`，真实输出立刻证明早期 `6x6 / Mazes 1` 每次 Treasure 只涨 `36` 金币，而不是 `216`，该轮已手动停止。
  - `request_id=334` 改为 `size * size * 2^(Mazes-1)` 后完整结算，`gold 1M time=7378.28`、`done time=13347.51`、`average=222:27.573`，慢于当前最佳 `216:26.969`。
  - 当前结论：金币次数估算不能只看理论每次金币；较小 Weird 预采会增加拆批和重复清迷宫 / 探图成本，正式路线继续保留原来的 `size * size` 估算与 `600` 上限。
- “早期小迷宫直接推到 `Megafarm 3`”
  - `request_id=332` 临时把 `try_unlock_early_megafarm()` 从目标 `Megafarm 2` 提到 `Megafarm 3`。
  - 真实输出 `early_megafarm 3 time=2980.87`，但 `step4 time=3651.98`，明显慢于 `request_id=331` 的 `step4 time=2547.29`。
  - 后续即使省掉一次 `Megafarm 3` 升级，也无法覆盖前置 `6x6` 小迷宫刷 `32000 gold` 的成本；该请求已在证伪后停止并回退。
  - 当前结论：早期巨大农场的正收益上限暂定为 `Megafarm 2`；第三级必须等地图扩大、迷宫和资源结构更强后再做。
- “快速重置金币阶段禁用直线贪心”
  - `request_id=326` 的 `gold 1M time=7849.40` 慢于正式基线 `7349.45`
  - 当前结论：`12x12` 快速重置金币阶段继续保留直线优先；单迷宫的 BFS-only 结论不能直接迁移
- “单次帽子状态连续跑多轮恐龙”
  - `request_id=193/194` 没有在 `125s` 请求窗口内形成可用进度证据，且会让骨头阶段长时间无输出
  - 当前结论：不采用，保留每轮 `bones` 日志
- “外部 `Save0/fastest_reset.py` 复合候选”
  - 2026-04-25 读取当前文件后，将 `move_utils` / `math` / `fastest_reset_action` / `pumpkin3` 内联到既有 `lb_fastest_reset.py`，没有向存档新增依赖文件
  - 请求 `263` 能推进到阶段一完成，输出 `17 分 28.8 秒 完成了阶段一`，随后因内联 `back` 名称冲突在迷宫探图报错
  - 修正内联变量冲突后请求 `264` 仍 30 秒无完成轮，资源停在 `hay=171 wood=406 carrot=268 weird_substance=100 gold=7`
  - 2026-04-26 重新确认用户所指是存档根目录 `Save0/fastest_reset.py`，不是外部 `lb_fastest_reset.py` 包装入口
  - 请求 `280` 暴露后半段卡点：`item_snapshot` 中 `hay` 持续增长到 `682642`，`wood=429 carrot=50 pumpkin=80 cactus=0`，根因是补草/补木后地块残留草或灌木，胡萝卜没有覆盖种下
  - 修复 `farm_hay_until()` / `farm_wood_until()` / `farm_carrots_until()` 后，请求 `281` 能脱离割草卡点并推进到 `gold=345927`，但删掉外部 phase2 尾段后节奏偏慢
  - 恢复 `Save0/fastest_reset.py` 的 phase2 尾段，并加 `5000` 游戏秒保护；请求 `282` 在 `90s` 窗口内回到 `Expand 6 / Pumpkins 2 / 12x12` 节奏，`gold 345927 time=7578.41`
  - 请求 `283` 完整跑到 `reset_stage save0_fastreset_done time=22484.01`，但旧轮询仍因 `numLeaderboardRuns` 被游戏清零误判为 `leaderboard finished without completed runs`
  - 修改模组为 Harmony 捕获 `LeaderboardManager.StopLeaderboardRun(...)` 后，请求 `284` 完整结算：`[lb_fastest_reset] finished=true runs=1 average=376:11.397`，同轮 `reset_stage save0_fastreset_done time=22571.33`
  - 当前结论：外部 `Save0/fastest_reset.py` 已作为候选迁入并跑通；它比当前正式 `13409.57` 慢，不应替代正式最优路线，但 phase2 尾段“先 Megafarm，再 12x12 + Pumpkins 2”的节奏可继续作为前期参考

## 下一步优化方向

- 当前路线已经能完成一轮，下一步应围绕真实成绩继续压缩阶段耗时，而不是再追求“能跑通”。
- 必须补证据的关键点：
  - 每个解锁门槛前后的资源短板
  - 迷宫 / 金币 / 无人机阶段是否真的比继续滚基础资源更值
  - `step4()` / `step5()` 最短完成条件
- 下一轮优先级：
  - 骨头阶段现在仍耗时很长，但 `Expand 7` 和 `Dinosaurs 4` 都已被新证据排除；后续只能找更便宜的仙人掌准备方式或更短恐龙行走路径
  - 继续压缩 `Megafarm 3 -> gold 1M`，这是当前最大单段瓶颈
  - 只有重写宝箱分配 / 寻路 / 奇异物质补给后，才重新开启多无人机金币
  - 若继续处理 `Power`，只能在已有资源循环里搭便车；不要再单独清场种太阳花或抬高 `step2` 目标
  - 奇异物质来源已排除南瓜专职路线；`Polyculture 1` 已接入正式路线，跨列补 companion 已验证正收益，后续只在出现新 companion 排布策略时继续改 Weird 产线
  - `Dinosaurs 3` 当前优于 `Dinosaurs 2`，多无人机恐龙已被帽子唯一性排除，`Dinosaurs 4` 暂不回到默认路线，除非先找到更便宜的仙人掌准备方式

## 候选策略方向（猜测 / 待验证）

### 方向 1：第一版满科技基线路线

- 核心思路：先不碰“科技不升满”的取舍，按你给出的方向做一条完整基线：
  - 所有科技至少 `1` 级
  - 无人机速度、农场大小、无人机数目升满
  - 最后解锁 `leaderboard`
- 主瓶颈：当前路线已经能跑通，但不是满科技路线；继续升后几级科技会明显拖慢
- 可能更强的原因：先有完整可跑通路线，后续才有可靠基线可以做科技取舍优化
- 优先探针：
  - 这条满科技路线的真实总时间
  - 时间大头落在解锁、资源积累，还是最后排行榜门槛

### 方向 2：满科技基线完成后，再做“科技不升满”剪枝

- 核心思路：先记住“榜前玩家大概率不会全升满”，但把它放到第一版完成之后处理
- 主瓶颈：如果现在就开始同时优化流程和科技等级，问题空间会失控
- 可能更强的原因：有了满科技基线以后，才能逐项判断“哪个满级其实不值”
- 优先探针：
  - 把某一类科技从满级降到次满级后，总时间变化多少
  - 哪个科技的“最后几级”回报最差

### 方向 3：围绕阶段切换而不是代码结构做优化

- 核心思路：把思考重点放在“什么时候切到下一阶段”，而不是先在代码结构上做花样优化
- 主瓶颈：当前路线真正的损失很可能来自切阶段太早或太晚
- 可能更强的原因：对这榜来说，流程节奏的收益远大于局部代码层面的微修
- 优先探针：
  - `step1 -> step2 -> step3` 的切换时机是否已经合理
  - 满科技路线里，哪一段资源积累最可能被压缩

- `request_id=371`：
  - 临时新增金币迷宫首步查表：在 `build_maze_graph()` 后构建 `next_step[source][target]`，导航保留直线优先，失败时用首步表替代每次 BFS。
  - 真实输出在早期 `6x6` 金币阶段只到 `reset_stage gold_table time=1774.03 cost=4.26 size=6`，随后 `LogOutput.log` 中 `real_elapsed=9.0` 到 `31.0` 期间 `gold=0`、`weird_substance=1085` 基本不变，只自动增长水和肥料。
  - 该状态说明脚本卡在首步表导航循环内，没有形成 Treasure 使用；已写入 `stop_requested`，结果为 `oracle_error request_id=371 leaderboard cancelled: fastest_reset`。
  - 结论：首步查表候选不采用。原因不是表构建耗时（`6x6` 只耗 `4.26s` 游戏时间），而是固定首步表替换动态 BFS 后存在卡死风险；正式路线继续使用直线优先 + 动态 BFS 兜底。

- `request_id=372`：
  - 临时新增 `WEIRD_COMPANION_MAX_DISTANCE = 6`，对 Weird 阶段树伴生只保留跨边界曼哈顿距离 `<= 6` 的补位，目标是减少远距离 `goto_wrap()` 往返。
  - 真实输出 `step4 time=2811.81`、`mazes 3 time=3394.23`、`megafarm 3 time=3635.82`、`gold 1M time=6999.47`、`dinosaurs 3 time=7350.58`。
  - 对比当前最好请求 `368/369` 的 `gold 1M time=6477.64 / 6143.85`，阈值 6 明显拖慢金币阶段；主动停止前骨头阶段也落后，摘要为 `finished=false runs=1 average=155:21.292`。
  - 结论：伴生远距离补位不能简单按距离阈值裁剪。跨列伴生虽然有移动成本，但对 Weird / Power / 后续金币的综合收益仍覆盖了成本；当前回退为不限距离补 companion。

- `request_id=373`：
  - 临时禁用 Weird 阶段树施肥：新增 `WEIRD_FERTILIZER_ENABLED = False`，让 `farm_weird_substance_worker()` 不再调用 `use_item(Items.Fertilizer)`。
  - 真实输出只推进到 `step3 time=1736.87`、`gold time=1768.39`、`early_megafarm 1 time=1768.43`、`weird_parallel_start time=1768.51 weird=685 target=1338`。
  - 随后 `LogOutput.log` 中 `real_elapsed=9.0` 到 `29.0` 期间 `weird_substance=685`、`gold=16` 不再增长，只看到 `hay/wood/water/fertilizer` 持续增加，说明不施肥会让早期 Weird 产线卡住，连 `Megafarm 2` 都无法继续。
  - 结论：Weird 阶段施肥不是边际优化，而是当前早期树产线成立的必要加速；不采用禁用施肥，正式路线继续施肥。

- `request_id=374`：
  - 临时把 `step3()` 的 Weird 目标从 `2000` 降到 `1000`，验证是否只刷够 `Mazes 1` 就更快进入早期金币 / Megafarm。
  - 真实输出 `step2 time=1327.45`、`step3 time=1741.55 weird=8`、`early_megafarm 1 time=1815.54`、`early_megafarm 2 time=2076.65`、`step4 time=2880.09`、`mazes 3 time=3487.58`、`megafarm 3 time=3706.03`。
  - 对比近邻正式路线的早期阶段（例如请求 `371` 前一轮正式输出 `step3 time=1892.87`、`early_megafarm 2 time=2025.98`，以及请求 `370` 的 `step4 time=2795.85`），降低 step3 目标虽然让 `step3` 提前，但会把 Weird 缺口转移到 `try_unlock_early_megafarm()` 和后续阶段，`Megafarm 3` 前已经落后。
  - 结论：`step3` 的额外 Weird 不是纯浪费，它支撑早期 `Megafarm 2` 和后续节奏；不采用 `1000` 目标，回退到 `2000`。

- `request_id=375`：
  - 临时在 `step5()` 的 `Megafarm 3` 后追加 `upgrade_megafarm_for_final_push(4)`，验证中途花 `128000` 金币换 `16` 台无人机是否能加速后续 Weird 产线。
  - 真实输出 `megafarm 3 time=3600.27`、`gold time=4139.41 gold=128136 target=128000`、`megafarm 4 time=4139.48 gold=136 max_drones=16`，随后 `weird_parallel_start time=4139.63 weird=46 target=43344 drones=12`。
  - 结果 `gold 1M time=8362.31`、`dinosaurs 3 time=9043.48`、`done time=12228.41`，最终 `average=203:48.478`。对比当前最好请求 `368/369` 的 `gold 1M time=6477.64 / 6143.85` 和 `done time=9881.43 / 9985.42`，该路线明显退步。
  - 结论：`Megafarm 4` 的额外金币导航成本无法被 Weird 并行收益抵消；且实际 Weird worker 只显示 `drones=12`，没有吃满 `max_drones=16`。不采用中途升级 `Megafarm 4`，正式路线保持 `Megafarm 3` 后直接冲 `1M Gold`。

- `request_id=376/377`：
  - 临时加入 `dino_hat_apple_plant` 探针，验证 S4“单次换帽批量恐龙”的关键前提：戴 `Hats.Dinosaur_Hat` 时能否主动 `plant(Entities.Apple)`。
  - `request_id=376` 输出 `reset_probe dino_hat_apple_plant time=6722.56 can_pay=True before=Entities.Grass planted=False after=Entities.Apple cactus=16616`。该探针不充分，因为切换恐龙帽会在脚下自动生成苹果，`after=Entities.Apple` 不能证明 `plant()` 生效。
  - 修正后的 `request_id=377` 在切帽后先记录脚下自动苹果，再 `move(East)` 到邻格，收割后尝试主动种苹果。真实输出为 `reset_probe dino_hat_apple_plant time=7109.17 can_pay=True auto=Entities.Apple before=Entities.Grass after_harvest=Entities.Grass planted=False after=Entities.Grass cactus=16608`。
  - 结论：恐龙帽下即使材料足够，也不能主动种苹果；S4“保持恐龙帽、边跑边补苹果、减少换帽次数”的路线不成立。正式脚本回滚探针代码，骨头阶段继续使用每轮补苹果后切恐龙帽的现有路线。

- `request_id=378`：
  - 临时把 `STEP2_POWER_TARGET` 从 `1000` 降到 `200`，不改 `step2()` 的解锁逻辑，验证第三轮 S1 的“少刷 Power 是否能压缩前期”。
  - 真实输出 `step2 time=1320.03 power=203.04`、`step3 time=1761.30 weird=1043`、`early_megafarm 2 time=2064.53`、`expand 6 time=2475.18`、`step4 time=2904.60`、`mazes 3 time=3525.72`、`megafarm 3 time=3763.51`。
  - 对比 `request_id=377` 近邻正式路线的 `early_megafarm 2 time=1867.73`、`expand 6 time=2194.23`、`step4 time=2622.32`、`mazes 3 time=3216.66`、`megafarm 3 time=3460.74`，`200 Power` 路线在进入正式金币前已经落后约 `200~300s`。
  - 结论：`STEP2_POWER_TARGET=200` 不采用。Power 本身虽然会在后段归零，但前期多刷到 `1000` 对早期 Weird / 南瓜 / 仙人掌节奏有实际收益；正式脚本回退到 `STEP2_POWER_TARGET=1000`。

- `request_id=379/380`：
  - 临时让 `main()` 只跑 `fr_phase1()`，验证 S2 的早期确定性路线结束状态。`request_id=379` 因没有中间输出，只能从模组 `item_snapshot` 看到大约 `game_time=798` 时仍在推进，无法定位阶段；因此 `request_id=380` 追加 `s2_phase1_checkpoint` 输出后复跑。
  - `request_id=380` 最终输出 `reset_probe s2_phase1 time=1008.75 size=6 hay=163 wood=749 carrot=392 pumpkin=0 gold=0 weird=681 power=0 speed=5 expand=4 mazes=1 pumpkins=1 fertilizer=1 sunflowers=1 unlocks={Unlocks.Speed:5,Unlocks.Expand:4,Unlocks.Plant:1,Unlocks.Watering:3,Unlocks.Carrots:3,Unlocks.Trees:3,Unlocks.Grass:2,Unlocks.Fertilizer:1,Unlocks.Sunflowers:1,Unlocks.Pumpkins:1,Unlocks.Mazes:1}`。
  - 对比当前正式路线近邻 `request_id=376` 的 `step2 time=1309.41`、`step3 time=1589.31 weird=1032`、`early_megafarm 2 time=1736.87`，`fr_phase1` 以更早时间拿到 `Speed 5 / Expand 4 / Mazes 1 / Pumpkins 1`，但代价是没有 Power、Weird 只有 `681`，且尚未解锁 `Megafarm`。
  - 结论：`fr_phase1` 本身值得继续作为前期替代候选；下一步不直接替换全路线，而是验证 `fr_phase1 -> try_unlock_early_megafarm() -> step4() -> Megafarm 3` 的桥接时间是否优于正式路线的 `megafarm 3 time=3288.64~3460.74`。

- `request_id=381`：
  - 临时让 `main()` 执行 `fr_phase1() -> try_unlock_early_megafarm() -> step4() -> upgrade_mazes_for_gold() -> upgrade_megafarm_for_final_push(3)`，验证 S2 早期路线能否顺利桥接到正式金币阶段。
  - 真实输出 `early_megafarm 1 time=1074.45`、`early_megafarm 2 time=1717.70`、`s2_bridge_step4 time=3008.23`、`mazes 3 time=3617.62`、`s2_bridge_megafarm3 time=3833.84 max_drones=8`。
  - 对比近邻正式路线 `request_id=376/377` 的 `step4 time=2476.56 / 2622.32`、`megafarm 3 time=3288.64 / 3460.74`，桥接路线到 `Megafarm 3` 已经慢 `373~545s`；继续跑完整 `1M Gold` 没有采用价值。
  - 结论：`fr_phase1` 单看早期解锁更快，但缺 Power 与 Weird 储备会把成本转移到后续早期金币、南瓜和仙人掌阶段；不采用 `fr_phase1` 桥接正式路线。正式脚本回滚为 `main_current_route()`。

- `request_id=382`：
  - 临时跳过 `Polyculture 1`，把 `step4()` 中的南瓜目标从 `8000` 降到 `5000`，只解锁 `Cactus` 后进入 `Mazes 3 / Megafarm 3 / Gold`，验证科技最小化是否能抵消 Weird 伴生损失。
  - 真实输出 `skip_polyculture time=2323.11`、`step4 time=2453.59`、`mazes 3 time=3026.58`、`megafarm 3 time=3258.46`，前半段明显快于近邻正式路线。
  - 但无 `Polyculture` 后 Weird 产线退化：`weird_parallel_start time=3258.61 target=43344` 到 `weird_parallel time=5508.84 weird=43378`，单次大 Weird 预备耗约 `2250s`；随后 `gold time=7197.75 gold=518664 target=1000000`，已经慢于当前最好 `gold 1M time=6143.85~6477.64` 且只完成约一半金币。
  - 结论：`Polyculture 1` 不能跳过。它的 `3000` 南瓜成本能被 Weird 伴生产线收益覆盖；正式路线恢复 `farm_pumpkins_until(8000) -> unlock(Cactus) -> unlock(Polyculture)`。

- `request_id=383`：
  - 临时把 `farm_gold_single_cycle()` 的 `batch_paid_move_count` 上限从 `900` 提高到 `1800`，验证 `1M Gold` 阶段一次性预备更多 Weird、连续跑多个迷宫 cycle 是否能减少产线重建成本。
  - 真实输出 `step2 time=1384.54`、`step3 time=1798.33`、`early_megafarm 2 time=1956.24`、`polyculture1 time=2627.51`、`step4 time=2746.88`、`mazes 3 time=3355.62`、`megafarm 3 time=3572.59`。
  - 金币阶段输出 `weird_parallel_start target=83616 time=3572.74`、`weird_parallel time=5809.08 weird=83706`、`gold 1M time=7759.57`、`dinosaurs 3 time=8436.09`；后续手动停止时已有 `average=154:49.063`，并由模组记录 `oracle_error request_id=383 leaderboard cancelled`。
  - 对比当前最好 `gold 1M time=6143.85~6477.64`，一次性大 Weird 预备导致金币阶段明显变慢。
  - 结论：`batch_paid_move_count` 上限不提高到 `1800`；正式路线保持 `900`，分批 Weird 预备比一次性大批量更稳。

- `request_id=384`：
  - 临时新增 `SKIP_GRASS_UNLOCK_PROBE = True`，只跳过正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Grass)`，验证省掉 `Grass` 解锁成本是否能覆盖后续 Hay 产量损失。
  - 真实输出 `step3 time=1785.53`、`early_megafarm 2 time=1970.47`、`expand 6 time=2408.56`、`polyculture 1 time=2875.06`、`step4 time=2996.53`、`mazes 3 time=3592.67`。
  - 对比近邻正式路线 `request_id=383` 的 `step4 time=2746.88`、`mazes 3 time=3355.62`，以及 `request_id=377` 的 `step4 time=2622.32`、`mazes 3 time=3216.66`，跳过 `Grass` 在进入金币前已慢 `~237s` 以上。
  - 结论：`Grass` 不能跳过。虽然其直接成本不高，但后续南瓜 / 胡萝卜补料阶段出现额外 `carrots` 补给，Hay 产量下降会拖慢中段节奏；正式路线恢复 `unlock(Unlocks.Grass)`。

- `request_id=385`：
  - 临时新增 `WATERING_UNLOCK_CAP_PROBE = 3`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Watering)`，验证少升 Watering 是否能节省前期 Wood 投入。
  - 真实输出 `early_megafarm 2 time=1951.83`、`step4 time=2739.88`、`mazes 3 time=3323.21`、`megafarm 3 time=3568.90`、`gold 1M time=6233.89`、`dinosaurs 3 time=6804.14`、`done time=10031.76`、`average=167:11.799`。
  - 对比当前正式最好请求 `368/369` 的 `done time=9881.43 / 9985.42` 与 `average=164:41.493 / 166:25.484`，Watering 上限 `3` 虽然让金币阶段单轮接近最好，但总完成时间退步。
  - 结论：不限制 Watering 到 `3`。当前路线继续允许 `step2()` / `step3()` 自然升级 Watering；该投入对后续完整路线仍有净收益。

- `request_id=386/387`：
  - 临时新增 `FERTILIZER_UNLOCK_CAP_PROBE = 3`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Fertilizer)`，保留所有 `use_item(Items.Fertilizer)` 行为，避免重复 W4“禁用施肥”探针。
  - `request_id=386` 完整结算，输出 `step4 time=2774.12`、`mazes 3 time=3363.93`、`megafarm 3 time=3585.26`、`done time=9897.70`、`average=164:57.699`。
  - `request_id=387` 完整结算，输出 `step4 time=2704.41`、`mazes 3 time=3303.46`、`megafarm 3 time=3545.05`、`gold 1M time=6501.29`、`dinosaurs 3 time=6848.27`、`done time=9811.38`、`average=163:31.378`。
  - 两轮平均约 `164:14.539`，轮次差异约 `0.88%`，低于 `10%` 稳定阈值；对比当前正式最好 `request_id=368/369` 两轮平均约 `165:33.489`，该路线稳定刷新。
  - 结论：采用 Fertilizer 解锁上限 `3`。正式脚本使用 `FERTILIZER_UNLOCK_CAP = 3`，同时更新 `lb_start.py` 的 Fastest Reset 本地最好时间为 `2:43:31.378`。

- `request_id=388`：
  - 临时把已采用的 `FERTILIZER_UNLOCK_CAP = 3` 降到 `2`，验证是否还能继续减少前期 Wood 投入。
  - 真实输出 `step3 time=1836.91`、`early_megafarm 2 time=2067.64`、`polyculture 1 time=2739.94`、`step4 time=2866.61`、`mazes 3 time=3450.48`、`megafarm 3 time=3686.53`。
  - 对比 `request_id=386/387` 的 `step4 time=2774.12 / 2704.41`、`mazes 3 time=3363.93 / 3303.46`、`megafarm 3 time=3585.26 / 3545.05`，上限 `2` 在进入正式金币前已稳定慢 `~100s` 以上。
  - 结论：不采用 Fertilizer 上限 `2`；正式路线回到 `FERTILIZER_UNLOCK_CAP = 3`。

- `request_id=389`：
  - 临时把已采用的 `FERTILIZER_UNLOCK_CAP = 3` 提到 `4`，验证更多肥料等级是否能用前期加速覆盖额外 Wood 投入。
  - 真实输出 `step4 time=2666.57`、`mazes 3 time=3254.79`、`megafarm 3 time=3445.37`、`gold 1M time=6749.49`、`dinosaurs 3 time=7093.82`、`done time=10166.44`、`average=169:26.499`。
  - 对比已采用 `request_id=386/387` 的 `done time=9897.70 / 9811.38`、`average=164:57.699 / 163:31.378`，上限 `4` 虽然让 `step4/mazes 3/megafarm 3` 提前，但金币和骨头阶段回吐收益，完整结算慢约 `269s~355s`。
  - 结论：不采用 Fertilizer 上限 `4`；正式路线保持 `FERTILIZER_UNLOCK_CAP = 3`。

- `request_id=390`：
  - 临时新增 `WATERING_UNLOCK_CAP = 4`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Watering)`，验证自然升级 Watering 是否仍存在过度 Wood 投入。
  - 真实输出 `step4 time=2722.84`、`mazes 3 time=3328.55`、`megafarm 3 time=3546.10`、`gold 1M time=6636.10`、`dinosaurs 3 time=6993.16`、`done time=9983.75`、`average=166:23.749`。
  - 对比已采用 `request_id=386/387` 的 `done time=9897.70 / 9811.38`、`average=164:57.699 / 163:31.378`，Watering 上限 `4` 首轮完整结算已慢于两轮正式基线，也慢于最佳单轮 `request_id=387`。
  - 结论：不采用 Watering 上限 `4`；正式路线继续自然升级 Watering，只保留 `FERTILIZER_UNLOCK_CAP = 3`。

## 2026-04-26 暂停点与后续方向

- 当前正式基线：保留 `FERTILIZER_UNLOCK_CAP = 3`，Watering 自然升级，`lb_start.py` 的本地最好时间保持 `2:43:31.378`。`request_id=386/387` 两轮平均约 `164:14.539`，轮次差异约 `0.88%`，可作为后续 A/B 对照。
- 暂停原因：`Watering 3/4`、`Fertilizer 2/4`、`STEP2_POWER_TARGET=200`、`step3 Weird 1000`、`Megafarm 4`、`Polyculture/Grass` 跳过、金币大批量、恐龙批量换帽等单变量都已证伪；继续在同类科技上限小变量里试探，边际收益很低。
- 后续优先方向 1：重写骨头阶段的苹果补给 / 仙人掌补给节奏。当前 `request_id=390` 从 `dinosaurs 3 time=6993.16` 到 `done time=9983.75` 仍约 `2990s`，且每轮都有 `apple_prep_start -> bone_prep -> bones`，应优先分析 `farm_bones_until()` 与 `farm_dinosaur_apple_cost()`，目标是减少每轮补给和切帽成本，而不是再调 `Dinosaurs` 等级。
- 后续优先方向 2：重新拆解金币阶段 Weird 产线。当前正式路线金币阶段仍在 `gold 1M time=6501.29~6636.10` 左右；`batch_paid_move_count=1800` 和 `Megafarm 4` 已证伪，但可以尝试按 `item_snapshot` 计算每 1000 游戏秒的 Weird 产出，先确认瓶颈是树成熟、伴生兑现、移动还是 Power 归零，再决定是否改 `farm_gold_single_cycle()` 或 Weird worker 布局。
- 后续优先方向 3：做阶段预算逆推，不再只比较完整平均值。下一轮探针应在 `step2/step3/step4/mazes3/megafarm3/gold1M/dinosaurs3/done` 全部输出后，计算每段耗时和相对基线差值；只有某段至少缩短 `>100s` 且后续不明显回吐，才值得完整跑完。
- 后续优先方向 4：若继续做科技最小化，只测“大结构”而不是等级微调。候选是 `Expand 5` 完整路线、`Mazes 2/3` 与更低棋盘尺寸联动、或前期 `fr_phase1` 的局部片段重用；不要重复已证伪的单独 `fr_phase1 -> step4` 桥接。
- 下一次执行规则：先写一个明确单变量探针，静态验证并同步后用 `--request-only` 投递；运行中只轮询三路输出，不前台长等。首轮若明显慢于 `164:14.539` 基线，立即回滚并只记录结论；只有首轮刷新或接近刷新，才按两轮稳定规则复跑。


## 提前 Polyculture 2 的本地基线

方案在 `step4()` 后、金币大生产前以最小骨头批次购买 `Polyculture 2`，保留 `Mazes 3`、`Megafarm 3` 和最终排行榜目标。科技快照确认升级需要 `10000 Bone`，父科技为 `Pumpkins`。回本要求是骨头、升级和补给投入小于 Weird 产线节省；有效吞吐倍率必须测量，不能直接假定为两倍。

场景为 `{"preset":"reset"}`，seed 为 `1`；API 上限 `500000`，脚本检查点上限 `5000000`，墙钟上限 `25s`。脚本 SHA256 为 `270c7b99a2762993fe3b2a91515085f318831ec64685eefe373a029808f335ba`。报告 `.codex/leaderboard-sol/reset/baseline-seed1.json` 记录模型预计 `26.215s` 时在第 `591` 行停止，错误为 `ValueError: 尚未解锁：Entities.Bush`，没有完成任何阶段。停止时 `Hay=50`，`Speed/Expand/Plant/Loops` 均为零。

首个可静态定位的分歧在 `step1()` 的 Speed 解锁：其父科技是 `loops`，裸 reset 预设却将其设为零。真实 `Core.decompiled.cs` 的 `BuiltinFunctions.resetUnlocks` 包含 `loops` 等基础能力，排行榜入口使用该集合。此前的 Speed 解锁失败又阻止 Expand 和 Plant，Bush 异常是后续症状。

#10 基准 `1966.927s` 与历史复跑 `10128.299s` 均非本轮实测。裸预设首差已通过下述场景配置继续核查；模拟器默认 reset 预设本身未修改。当前没有完整的 Weird 吞吐、提前骨头投入或回本预算；实机和双日志未验证。

## 当前规则下的部分基线与前期预算

补齐真实 `resetUnlocks` 对应的基础能力后，`.codex/leaderboard-sol/reset/scenario.json` 保持 Speed、Plant、Expand 为零、库存为零，只给 loops、debug、debug_2、timing、lists、dictionaries、costs、auto_unlock、operators、variables、senses、utilities、functions、import、simulation 各一级。不能改用满科技模拟 Reset。

报告 `.codex/leaderboard-sol/reset/baseline-with-initial-unlocks-seed1.json` 在 `3999.718561s`、500000 次 API 调用时达到上限，墙钟 `12.6745s`；这是预算停止，不是新的机制异常，也不是完整完成时间。已记录阶段：

| 阶段完成 | 累计本地游戏秒 |
| --- | ---: |
| step1 | 146.379194 |
| step2，Power 1000.077 | 1473.272143 |
| step3 | 1920.688543 |
| 早期 Megafarm 2 | 2089.608527 |
| step4，Polyculture 1 / Dinosaurs 1 | 2899.004323 |
| Mazes 3 | 3502.565466 |
| Megafarm 3 | 3743.639371 |

按原报告 `harvests.at_ns` 与阶段时间筛选，step2 净耗 `1326.892950s`，期间向日葵收获676次，其中594次得到1 Power、82次得到8 Power，毛产量1250。首次向日葵收获为 `1170.599476s`，不能把它当作解锁时刻。低倍率确有损失，但前期尚未产电的时间更长；单独优化末尾补电不足以解决与#10的差距。

当前 `step2()` 每列先尝试 Speed，再到最后尝试 Sunflowers；当前成本中 Speed 4 与 Sunflowers 1 都需要500 Carrot。可筛选一个局部顺序候选：仅将原有 Sunflowers 解锁及成功标记块移到 Speed 尝试前，保留其余升级、混种、Power 100/1000 阈值和后续路线。Speed 3有Power时动作速率倍率约6.75，高于Speed 4无Power时的5.0625；这只是产电后动作吞吐的理论理由，成熟、种植、补料和推迟速度升级的代价仍须完整计入。

先用当前正式脚本补完整seed 1基线，有限提高API/语句预算、墙钟仍不超过60秒并保持进度；达标后同场景比较候选。只在解锁成功和已有阶段边界输出科技、库存与时间，不逐格输出。至少对照seed 0/1/123的完整时间及step2、Megafarm 3、最终金币/骨头阶段；若前期收益被后续回吐，停止候选，不继续枚举Power阈值。早期骨头购买Polyculture 2另作独立候选，不能与解锁顺序合并后归因。

## 2026-10-24：完整首配对与有界筛选结论

沿用补齐15项基础能力的reset场景，不添加库存或生产科技；正常结束且 `state.unlocks.leaderboard > 0` 才算完成。场景未配置物品goal，故 `goal_reached=null`。原版SHA256为 `270c7b99a2762993fe3b2a91515085f318831ec64685eefe373a029808f335ba`；候选为 `fb90c19851688da14952911c3d148bd335cf0fe12e73ef8d44dae0a3f3dc3dda`，仅把step2原Sunflowers解锁及成功标记块移到Speed之前。

| 样本 | 完整本地游戏秒 | 最终Leaderboard解锁 |
| --- | ---: | --- |
| 原版seed 0 | 9899.899869 | 是 |
| 原版seed 1 | 10114.199878 | 是 |
| 提前Sunflowers候选seed 1 | 10286.981630 | 是 |
| 原版seed 123 | 未取得 | 有界停止时否 |

seed 1候选step2累计从1473.272143降到1465.716942秒，只省7.555201秒；step4从2899.004323降到2838.356596秒，省60.647728秒；整轮却慢172.781752秒。不同后续随机轨迹和资源阶段会改变耗时，不能把这一负收益外推为所有seed的严格劣势，也不能混合未配对样本计算收益。3seed筛选未完成，停止该候选实机安排，不继续枚举Power阈值。

各次设置API上限300万、检查点1500万、总墙钟55秒，并每5墙钟秒报告实际API和游戏时间。原版seed 123初次CLI超时只保留99字节摘要；用正式run_script入口补取详细停止报告，55秒时为6501.544529游戏秒、2590308次API、Leaderboard仍为0，停在第二次大批Weird生产。该部分时间不计入完整预测。

Astra修复CLI父子报告截止竞争（0352baa）后，用原55秒场景复核，已收到BudgetExceeded、line 1637、完整state/output/API：5772.367003游戏秒、2297486次API，无BrokenPipe。回传预留使实际工作预算短于总硬预算，游戏机制和计费不变；报告竞争已解除，seed 123完整执行仍未覆盖。

| 时间名称 | 本次候选值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 10286.981630 | 仅seed 1一次完整完成，配对原版10114.199878，3seed不足 |
| 短时打榜测试时间 | 未取得 | 首配对无净收益且3seed不齐；实机准备79仍阻塞 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据位于 `.codex/leaderboard-sol/reset/`：`full-baseline-seed0.json`、`full-baseline-seed1.json`、`early-sunflowers/seed1.json`、`early-sunflowers/comparison.json`、`full-baseline-seed123-bounded-detail.json`、`cli-budget-recheck-seed123.json`及`three-times.json`。游戏指纹见[当前规则](current_game_rules.md)。正式py未改、Save0未部署Reset，未进行本候选实机或同seed精度验收；提前Polyculture 2未与本候选混合。

## 提前Polyculture 2：按完整报告核算阶段回本

当前源码Growable.GetYield在伴生倍率之后将感染产量的一半转为Weird。原版两次大批Weird生产期间Trees 4、Polyculture 1不变，树的Wood收益40/400分别为普通/伴生成熟收获，20/200分别为感染普通/感染伴生；后两类产生等量Weird。按既有完整报告的harvests.at_ns切阶段求和，所得Weird与阶段库存增量一致，无须重新运行基线。

| seed | 两次大批Weird净耗秒 | Weird增量 | 其中来自伴生 | 伴生产量占比 | 固定收获速率下的节时预算 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 1319.539994 | 83620 | 66800 | 79.89% | 584.716761秒 |
| 1 | 1011.016251 | 83680 | 68200 | 81.50% | 453.083531秒 |

每批独立按T×f/(1+f)计算最后一列，f是该批Weird中伴生产量占比；Polyculture 2将命中倍率10→20，只增加原命中部分的产量。这假定收获速率和命中结构不变，不是完整时间预测，也不是严格上界。提前结束Weird会减少顺手产电及被动肥料积累，随后金币或骨头可能变慢；初始化、成熟与改写支撑也不会按比例消失。

当前解锁成本为10000 Bone。已有Dinosaurs 1且12×12时，理论完整143尾的一轮兑现20449 Bone，足够购买；苹果每个2 Cactus，完整一轮143个共286，须按实际库存核对并保留已有补给。DinosaurHat的移动ops从400逐苹果递减，与恐龙科技等级无关；等级影响苹果价格和骨头倍率。现有seed 0/1最终Dinosaurs 3的12×12单轮日志可作成本量级参考，但不能当提前Dinosaurs 1的预测。

独立候选采用正式原版SHA270c7b99，而非提前Sunflowers失败版。在step5完成Mazes 3和Megafarm 3后、farm_gold_until(1000000)前，仅插入一次Polyculture 2准备：读当前等级和实际cost，调用已有farm_bones_until满足Bone成本，再unlock并确认等级达到2。保持世界尺寸、全部Power/Weird阈值、金币批次和最终Dinosaurs 3路线。借用现有完整绕环，允许骨头超额并保留余量计入最终目标，不另写刚好100尾截断算法。原有清场/补给成本必须进入记录。

此处原先安排的候选筛选已暂缓。下节整轮预算发现Weird阶段还输出大量Power，仅有Weird局部收益不足以支持执行。先核算联产资源回吐；已启动的有界单次只保留诊断，不自动扩seed或进入实机。

本节保留为局部预算来源，不再作为候选准入结论。整轮决策以下节为准；不枚举骨头数量、Power阈值或Polyculture等级。

## 整轮时间切片与候选准入（2026-10-24）

研究先回答“增加A1后，B/C真正能省多少”，再写候选。以下直接解析当前正式脚本seed 0/1的完整本地报告，不重跑；它们是模拟结果，未经本版本完整实机校准。两样本均解锁Leaderboard，整轮9899.900/10114.200秒，均值10007.050秒；样本范围不是统计置信区间。分析脚本与结构化账在 `.codex/leaderboard-astra/summarize_reset_budget.py`、`reset-time-budget.json`，输入SHA与来源随账保存。

### 当前时间花在哪里

阶段按既有日志相减，合计与报告完整时间一致；表中的金币段已扣除两次Weird，不能重复相加。骨头段含每轮轻量补给检查及最终解锁，尚未拆成精确追击/固定绕环两段。

| 阶段 | seed 0秒 | seed 1秒 | 均值秒 | 整轮占比 |
| --- | ---: | ---: | ---: | ---: |
| 初始能力 | 146.039 | 146.379 | 146.209 | 1.46% |
| 前期资源与1000 Power | 1297.745 | 1326.893 | 1312.319 | 13.11% |
| 首次Weird与迷宫解锁 | 436.596 | 447.416 | 442.006 | 4.42% |
| 首个并行解锁 | 25.873 | 35.170 | 30.521 | 0.30% |
| 升至4机 | 104.476 | 133.750 | 119.113 | 1.19% |
| 扩田与一级恐龙 | 794.662 | 809.396 | 802.029 | 8.01% |
| 升至Mazes 3 | 596.074 | 603.561 | 599.817 | 5.99% |
| 升至8机 | 203.918 | 241.074 | 222.496 | 2.22% |
| 两批大规模Weird | 1319.540 | 1011.016 | 1165.278 | 11.64% |
| 1M金币导航及衔接 | 1727.921 | 1930.922 | 1829.422 | 18.28% |
| Dino 3升级及首轮苹果准备 | 419.488 | 417.589 | 418.539 | 4.18% |
| 25轮骨头及最终解锁 | 2827.568 | 3011.033 | 2919.301 | 29.17% |

粗分A为准备到8机（均值3674.511秒），B为Weird与1M金币（2994.700秒），C为恐龙准备与骨头（3337.840秒）。只在A之后插入升级，不能让不变的A低于#10整轮1966.927秒；骨头段本身也超过#10。后期改进只能是增量收益，不能宣称单项能达到前十。

### 科技效果只能作用于受影响部分

每个候选先列新增步骤时间/资源、各后续阶段可受益的比例、其他产物变化及有效并行数。阶段内部动作、生长和补给可能重叠，不能把它们当独立耗时相加；没有计数支持时把比例标为未知。

`整轮净节时 = 各阶段直接节时之和 − 新增准备/升级/恢复时间 − 后续资源缺口造成的额外时间`

对已识别的受益比例a和有效加速r，可暂用 `T′ = T × (1−a+a/r)`；只有机制和阶段数据支持a、r时才代数值。收获倍率先换算所需收获次数并取整，不能直接除整个阶段。已知误差、种子波动与结构假设分开记录。

| 改动 | 必须计入的成本 | 可受影响部分 | 当前判断 |
| --- | --- | --- | --- |
| 提前Polyculture 2 | 10000 Bone；额外恐龙、清场、补给 | 伴生命中的产量，当前占Weird约80%；不直接加速金币移动或骨头 | 缺联产Power保持率，暂缓 |
| Trees 4→5 | 19200 Hay及购买时的补料；不能拿期末库存当当时可用库存 | 所有Tree产量，可能减少Weird生产周期 | 同样可能少产Power；先补资源账，不直接试完整路线 |
| Megafarm 3→4 | 128000 Gold及其Weird/导航成本 | 当前按列产线受12列限制，8→最多12有效工人；不加速单机迷宫和恐龙 | 即使全部Weird可并行，局部节时上界约388秒；已有失败记录，不重试 |
| Mazes 3→4 | 432000 Cactus及基础补料 | 单次金币翻倍，所需迁移近半；每次Weird成本也翻倍，单位Gold所需Weird不因等级下降 | 不把Weird和导航同时减半；先过仙人掌准备预算 |
| Dinosaurs 3→4 | 432000 Cactus及补料 | 12×12完整轮产量81796→163592，25轮→13轮；每个苹果价格同时翻倍 | 只可削掉约12轮，准备成本须抵扣；历史失败，不重试 |
| Expand 6→7 | 64000 Pumpkin和整条补料链 | 改变南瓜/仙人掌产量、迷宫规模及恐龙尾长，也改变移动与排序 | 不能只按骨头倍率算收益；历史扩田成本失败仍有效 |

### Power是Weird阶段的联产收益

源码Execution以累计操作数/6000计Power消耗，Farm.MaxSpeedFactor在有Power时将动作速度翻倍。Speed 5下，一份Power对随后串行动作的节时折算约 `6000×0.0025/(1.5^5×2)=0.987654秒`，有扣款批次边界；不能直接套到多机并行时间或自然生长。

两个大批Weird结束时，seed 0输出870.532与1381.749 Power，seed 1输出660.904与1371.934 Power。第一次的库存随后在金币段用尽，第二次的库存继续支持金币、仙人掌和骨头，最终也耗尽。减少其中任一批Power都会影响后续；只看1M金币结束时剩余的589.610/450.880，会漏掉金币过程中已经消耗的Power。

用120秒作为额外骨头步骤的敏感性参数：现有无Power的12×12、Dino 3单轮共46个样本，范围109.896～133.280秒，中位数约118～119秒；等级不改变移动ops，但该量级不是提前Dino 1的实测，额外恢复成本也未确认。下表没有概率含义，只检验局部预算对Power损失的敏感程度；正数为省时，负数为退步。

| 两批留给后续的Power减少比例 | seed 0净节时秒 | seed 1净节时秒 |
| --- | ---: | ---: |
| 0% | +464.717 | +333.084 |
| 25% | −91.402 | −168.852 |
| 50% | −647.521 | −670.787 |

所以“额外一轮骨头约120秒，小于Weird省453～585秒”还不够。该参数下，两seed最多容忍损失约471/337 Power，即原后续可用量的20.9%/16.6%；其余成本会继续压低容忍值。现在没有证据保证能保留所需Power，提前Poly 2尚不具备保守净收益依据。科技提升可能改变命中、成熟和产电速率，不能用固定速率表当作真实结果。

### 下一步先获取最有价值的局部证据

优先看占29.17%的骨头段中不需要新资源的成本。当前run_dinosaur_chase_loop在退出追击后，固定绕环仍调用完整update_and_move，每步执行measure并维护step、苹果目标和length；这些值在固定绕环结束后不再读取。候选仅简化这一尾段，保持追击、路径、can_move失败退出、实际move与坐标更新不变。它没有升级或清场投资，也不压缩前面的Weird产电阶段，跨阶段副作用较少。

先由Sol抽取现有12×12绕环作有界局部对照，使用当前Reset科技、Dino 3、Power=0、足够但固定的苹果材料、单机，比较相同seed 0/1/123的原版与仅尾段简化版。确认骨头产量、move次数/动作tick和随机抽样一致，记录完整单轮时间、measure调用与解释器tick。每少10000次measure，单此API在Speed 5下约省1.646～3.292秒，另计被删维护语句；不能在没有尾段计数时给整轮百分比。

用局部每轮差额乘现有25轮，再按有/无Power分段修正，得到整轮回本预算；稳定改善才迁入完整Reset候选并作配对验证。局部结果不填“完整本地预估时间”，也不进实机。若所得收益很小，保留结论后转向A段的资源/科技依赖路径预算，不围绕尾段做参数枚举。

候选准入要同时满足：当前规则可执行；新增成本有来源；主要联产资源与后续时间已纳入；在明确的保守假设下仍有净收益。未知项可能改变正负号时，先做针对该未知项的有界局部检查。只有两个完整seed时，不给95%置信度之类结论；最终仍以同版本实机和完整官方统计确认。

### 已启动的Poly 2单次诊断：局部收益确实发生后续回吐

暂停通知到达前已启动的一次seed 1本地运行完成，未扩样本。候选SHA `7de63e5635c1e607c0d1838077d3f0961b14e020f4e8b3b65ca73dafffde8d95`，正常解锁Leaderboard并确认Poly 2，完整11258.980534秒；既有原版10114.199878秒，慢1144.780657秒。新增helper定义多1t，使start从0.2800变为0.2825秒，前期轨迹已经分歧；这是完整诊断，不能把所有差异严格归因于升级。

| 时间切片 | 候选减原版（秒） |
| --- | ---: |
| 升到8机前的前缀 | −49.368 |
| 新增骨头与Poly 2升级 | +126.234 |
| 两批Weird | −939.089 |
| 两批Weird之后的金币导航 | +1557.007 |
| 1M金币之后的准备与骨头 | +449.990 |
| 其他边界语句 | +0.006 |
| 合计 | +1144.781 |

Weird从1011.016秒降到71.928秒，但其后可用Power从两批合计2032.838降到5.042。减少2027.796 Power的串行动作折算约2002.762秒，实际金币及后续合计多2006.998秒，量级接近，支持把联产Power纳入预算；它不证明全部差值只来自Power。原版两批Weird结束Fertilizer均为8，候选为173/392，显示资源短缺边界也发生变化；之前固定收获速率只预测省453秒，不能表达这种跨阈值变化。

本候选三类时间：完整本地预估11258.980534秒（仅1seed诊断）；短时实机未取得；完整游戏打榜未取得。不扩seed或实机。原始报告及三值在 `.codex/leaderboard-sol/reset/early-poly2/`；相加闭合的时间差账在 `.codex/leaderboard-astra/reset-poly2-accounting.json`。后续预算必须同时检查资源等待阈值与联产资源，不能仅由科技倍率线性外推。

## 骨头固定绕环尾段：3seed组件对照与25轮预算

本次仅抽取当前正式脚本的build_dinosaur_path和run_dinosaur_chase_loop，来源SHA256为270c7b99。共同入口只执行12×12缩图、清场、戴恐龙帽、单轮绕环和换草帽结算，不包含升级或材料准备。科技复制既有Reset完整seed 1最终快照，保留Speed 5、Expand 6、Dinosaurs 3等当前等级，仅将Megafarm置0限定单机、Leaderboard置0避免预先达标。12种初始库存归零，仅固定Cactus 1000000，Power始终0；目标81796 Bone。

原组件SHA256为 `627abf5291fc842884cbb8554f0157d64cce9e6056beecb74bcfb8312e80daac`，精简组件为 `fc42d5f701e87602a234c40c5ced609abe7d019a8ff8bd7357d729c0db0fdf97`。只把固定绕环尾段内联为方向有效性检查、can_move失败退出、move及原get_pos_x/y坐标更新；追击和path不变，删除此后无人读取的step、measure、目标和length维护。两版函数定义数相同，没有单方新增helper产生的开局tick。

| seed | 原组件游戏秒 | 精简组件游戏秒 | 单轮省秒 | 相同move数 / 动作tick | measure原→新 | 解释器tick原→新 | 相同snake抽样数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 119.799831 | 115.789285 | 4.010546 | 2870 / 306727 | 2871→949 | 44494→34226 | 2048 |
| 1 | 126.165939 | 122.399674 | 3.766265 | 2932 / 324665 | 2933→1139 | 45650→36036 | 3062 |
| 123 | 122.599839 | 118.699910 | 3.899928 | 2825 / 316316 | 2826→961 | 43809→33819 | 2358 |

六次运行均完整达标，每轮Bone 81796、Cactus消耗1144，配对can_move调用也一致。原组件均值122.855203秒，精简组件118.962956秒，单轮省3.892246秒；measure少1922/1794/1865次，解释器tick少10268/9614/9990。模型570dbb2，每seed上限50万API/200万检查点，每版三seed批次共享25秒墙钟。

随机数按机制区分：全部非various流的抽样数及流seed配对一致，特别是snake流不变。various流因世界时长缩短而少抽5760/5472/5616次，逐seed恰等于少经历的0.1秒水分衰减次数×144格；不能强称全部八流抽样一致，也不把这种计时变化当作骨头路径失效。

按现有25轮预算：若全程无Power，三seed局部差额线性换算约94.157～100.264秒，均值97.306秒；若25轮始终有Power且路径与其他条件相同，动作tick约减半，对应约47.078～50.132秒，均值48.653秒。这是情景预算，不是完整Reset预测、严格上下界或统计置信区间。

既有完整seed 0/1分别有22/24轮在Power=0时开始，其余3/1轮可能只部分有Power。把这些不确定轮的收益系数放在0.5～1，结合当前组件样本差额得到约88.507～100.264秒、92.274～100.264秒的敏感性范围；不假设这三个局部seed覆盖所有25轮苹果轨迹。减少时间也使组件期末被动Fertilizer少1/2/2份、Water少3/3/4份；如果完整路线依赖这些补给而发生额外等待，仍须抵扣回吐。Cactus、move和当前骨头收益未增加资源需求，但不能据此保证整轮反馈为零。

| 时间名称 | 当前值 | 依据 |
| --- | --- | --- |
| 完整本地模拟预估时间 | 未取得 | 只做组件，122.855/118.963秒不代填完整Reset |
| 短时打榜测试时间 | 未取得 | 未部署组件或完整候选 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

原始证据在 `.codex/leaderboard-sol/reset/bone-tail/` 的 `source-manifest.json`、`scenario.json`、`baseline/seeds0-1-123.json`、`candidate/seeds0-1-123.json`、`comparison.json`及`three-times.json`。此处组件结果只作预算输入；后续完整本地候选见末节，正式py和Save0仍未修改，未进行实机或同seed精度验收。后续是否推进由整轮成本与补给边界决定，不继续围绕尾段枚举参数。

### 整轮准入：水肥减少在当前两基线没有后续消费路径

Astra核对正式step5调用链：金币与Dinosaurs 3升级完成后调用farm_bones_until，结束后只解锁Leaderboard并输出；解锁成本仅1000000 Gold与2000000 Bone。骨头循环自身不使用Water或Fertilizer，只有苹果材料不足时才可能转回生产。

两个完整基线首轮bone_prep均为37360 Cactus，25轮每轮消耗1144，总共28600，余8760。逐一核对两份报告的全部25条bone_prep，当前库存减剩余轮数×1144的余量始终8760。因此只要完整候选保持相同骨头路径与产量，骨头开始后不会再次触发种植补料；少积累的水/肥没有当前流程的消费方，不应凭这一库存差单独扣减预算。此结论限于这些初始库存和路线，不泛化到缺材料场景。

组件SHA、复制函数AST、六份达标终态已复核。various抽样差由时长减少的水衰减解释，snake及其余流计数保持一致；完整连续25轮仍需检查苹果路径、供料、Power转折和成功条件，组件不能代替整轮验证。

准入结论：值得进入完整本地对照。由正式原版复制候选，只替换已核对的固定绕环尾段，不增加函数定义、不改变顶部语句或日志，不并入其他候选。先运行seed 0/1，复用同版本已完成的原版；每次仍55秒墙钟、300万API、1500万检查点并输出进度。先核对start、step1～4、Megafarm 3、1M Gold、首轮bone_prep的时间和库存；改动执行前如已分歧，先定位，不将整轮差额归因为尾段。

两seed完整成功且净收益稳定后，再决定额外seed和实机队列。seed 123原版已在同预算停止，不机械重跑；预算停止仍记为未完成。保留全部25轮Bone/Cactus/Power阶段、末态Leaderboard、随机流与三类独立时间；若新增补料或动作路径改变则重新核算。预计约90～100秒仅是约0.9%～1.0%的增量收益，不代表接近#10，完成该项后回到A段资源/科技依赖的结构预算。

## 首轮55秒预算记录：完整尾段候选seed 0/1配对（历史）

候选 `.codex/leaderboard-sol/reset/bone-tail/full/lb_fastest_reset.py` 的SHA256为 `acb8130f570ba12592fb69c534f5ff11796fe2c3dda3263424f38185f3bcb153`。由正式原版270c7b99直接复制，只替换已验证尾段；run_dinosaur_chase_loop的追击前缀及其他全部模块AST节点保持一致，不新增函数、顶部语句或日志，不混入其他候选。场景仍是补齐15项初始基础能力的reset，原版复用既有完整seed 0/1报告，未重跑原版或seed 123。模型570dbb2；每次总墙钟55秒、API上限300万、检查点1500万，保留5秒进度。

| seed | 原版完整游戏秒 | 候选完整游戏秒 | 完整净收益 | 候选骨头完成轮数 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 9899.899869 | 未取得 | 未取得 | 10/25，有界停止 |
| 1 | 10114.199878 | 10021.383165 | 省92.816713秒，0.918% | 25/25，Leaderboard已解锁 |

两seed从start、step1～4、Megafarm 3、1M Gold直到首次bone_prep的79条日志均与各自原版逐条相同，包含时间和库存；没有新增helper定义造成的开局tick或改动前轨迹分歧。两版对照按相同完整脚本场景进行，局部修改生效前的前缀已核对。

seed 1全部25轮每轮产出81796 Bone，bone_prep的Cactus余量恒8760，整轮move均342942次、move动作tick均62277474，can_move/get_pos_x/get_pos_y/plant/use_item/harvest调用数相同。snake抽样均53558，其他非various流计数亦相同；various少133632次，恰对应12×12少经历928次0.1秒水衰减。measure从90192降到45917，解释器tick从8306842降到8069024；没有靠改移动路径或补料取得收益。

seed 1各轮开始时只有第1轮Power为正，两版标记一致，末态Power均0。末态Leaderboard科技一致，Bone44900、Gold200、Cactus8760、Pumpkin496及其余生产库存一致；仅被动Fertilizer从1743降到1706、Water从6883降到6809。没有新增plant/use_item调用，符合骨头后无水肥消费方的准入分析。未逐API采样轮内Power精确归零时刻，不宣称该时刻完全相同。

seed 0工作进程在53.763秒触预算，总命令仍受55秒限制，报告8131.868406游戏秒、Bone817960；完成10轮并正在第11轮。已完成10轮的Bone/Cactus/剩余轮数均与原版一致，第10轮结束累计省38.921587秒；各轮开始时Power为正的仍为第1～3轮。该部分进度不计入完整候选时间，也不与seed 1混成两seed均值。未放宽预算或机械重跑失败样本，issue #56记录完整两seed验证仍受计算预算阻塞。

| 时间名称 | 当前完整尾段候选值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 10021.383165 | 仅seed 1一次完整正常结束；同seed原版10114.199878，两seed筛选未齐 |
| 短时打榜测试时间 | 未取得 | 完整两seed确认不足；游戏重开尚待授权 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据在 `.codex/leaderboard-sol/reset/bone-tail/full/`：`source-manifest.json`、`seed0.json`、`seed1.json`、`comparison.json`和`three-times.json`。组件与完整候选的三类时间分别保存，不互相覆盖。正式py和Save0未修改，未运行实机或同seed模型精度验收；单个完整样本只能支持该次净收益，不宣称两seed稳定刷新或统计置信度。

## 75秒单次补齐：完整seed 0/1均通过本地筛选

Astra按旧报告末段仍持续推进、估计尚需约5秒墙钟的证据，批准仅seed 0一次新的75秒总墙钟方案。runner提交7b63d27使CLI校验、帮助和文档支持此有限预算，默认10秒、父子绝对截止、最多1秒报告余量和5秒进度保持；脚本SHA acb8130f、场景、300万API和1500万检查点均不变。seed 1与两份原版复用，不重跑seed 1/123；旧55秒JSON及进度均未覆盖。

seed 0本次工作进程54.803秒正常结束，Leaderboard已解锁。旧55秒停止报告全部输出是本次完整输出的精确前缀；两seed从start到首轮bone_prep的79条日志仍与各自原版逐条相同。预算变化只允许执行完成，不改变模型机制或候选逻辑。

| seed | 原版完整游戏秒 | 候选完整游戏秒 | 省游戏秒 | 改善 | 完成情况 |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 9899.899869 | 9803.578949 | 96.320920 | 0.973% | 25/25骨头轮，Leaderboard 1 |
| 1 | 10114.199878 | 10021.383165 | 92.816713 | 0.918% | 25/25骨头轮，Leaderboard 1 |
| 两seed均值 | 10007.049873 | 9912.481057 | 94.568816 | 0.945% | 两个完整候选样本 |

两组25轮每轮均产81796 Bone，Cactus每轮消耗1144，prep库存扣除全部剩余轮需求后始终余8760。完整API计数只有measure减少，其他调用全部一致；seed 0/1整轮move分别398579/342942，move动作tick分别73163911/62277474，均与配对原版一致。没有新增材料生产、移动或水肥使用。

seed 0的measure从90885降到44847，解释器tick从9173925降到8927257；seed 1分别从90192降到45917、从8306842降到8069024。snake抽样分别57062/53558，所有非various流计数配对一致。various分别少138672/133632次，恰等于少经历963/928次0.1秒水分衰减×144格；不宣称全部随机流完全相同。

两版轮开始Power为正的标记一致：seed 0为第1～3轮，seed 1仅第1轮；末态Power均0。两组末态解锁与所有生产库存均相同，包括Bone44900、Gold200、Cactus8760、Pumpkin496。只有被动积累库存减少：seed 0的Fertilizer 1619→1581、Water 6740→6663；seed 1为1743→1706、6883→6809。当前流程没有这些水肥的后续消费方。未逐API采样轮内Power归零时刻，不宣称其时间完全一致。

| 时间名称 | 本候选当前值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 9912.481057 | 同脚本、同场景完整seed 0/1均值；配对原版10007.049873 |
| 短时打榜测试时间 | 未取得 | 本候选尚未部署实机；游戏正常重开待授权，79/Save0仍冻结 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

新证据在 `.codex/leaderboard-sol/reset/bone-tail/full/` 的 `seed0-budget75.json`、`seed0-budget75.progress`、`seed0-budget75.client.json`、`comparison-budget75.json`及`three-times-budget75.json`；原55秒的`seed0.json`、`seed0.progress`、`comparison.json`和`three-times.json`作为历史保留。正式py和Save0未修改；组件三值也单独保留。两seed均支持该项约0.9%的完整本地净收益，不构成统计置信区间、实机成绩、排名或同seed模型精度验收。结果交Astra判断实机队列；后续回到A段资源/科技依赖的结构预算，不继续围绕尾段枚举。

## Reset A段观测：seed 1科技、产电与动作成本账

本项只观测当前正式原版270c7b99。副本SHA `6d4e776ff5ac90e7fb585205a04c62ba78c00d1b3382b1078018ae683e58e22d`，仅在入口原step2日志后插入return；移除此Return后全模块AST与原版相同，其余函数、顶部语句和日志均保留。沿原reset场景只运行seed 1一次，55秒总墙钟、30万API、300万检查点；CLI保留5秒进度和30秒无进度停止约束，子进程继承256MiB的RLIMIT_FSIZE硬上限。工作进程3.785秒正常完成，轨迹75111条、16750256字节（15.975MiB），未触任何预算。

前三条输出与既有完整seed 1基线逐字相同。step1原日志146.379193764秒，step2原日志1473.272143310秒，区间为1326.892949546秒。此前预算1312.318851278秒是原seed 0/1的step2均值，其中seed 0为1297.744753009秒；本项不将均值当seed 1。报告末态1473.299962400秒包含新增return及调度收尾，超出原日志边界的0.027819090秒不计A段。

库存按原API副作用时刻记录，成功升级列出立即支付后的余额；预计返回时刻另列。step1/step2显示原日志get_time，库存查询和quick_print可稍晚。非Power库存由既有收获、成功种植、升级、用料及原补给时序推导；20546条num_items读数和全部非Power末态逐一相符。伴生额外收益由实际收获记录纳入，未假设Polyculture 0时所有收获均只有基础产量。Power只用同一0.2秒结算周期内的既有读数和收获增量还原，不跨周期外推扣款。

| 边界 | 游戏秒 | Hay | Wood | Carrot | Power | Water / Fertilizer / Weird |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| step1原日志 | 146.379194 | 21 | 1 | 0 | 0.000000 | 0 / 0 / 0 |
| Sunflowers 1支付后 | 1156.740193 | 233 | 355 | 1 | 0.000000 | 30 / 0 / 72 |
| Speed 5支付后 | 1337.895069 | 94 | 412 | 22 | 105.108833 | 39 / 0 / 134 |
| 达到1000Power后的step2原日志 | 1473.272143 | 4 | 960 | 3 | 1000.076667 | 40 / 0 / 170 |

三个子区间分别为1010.360999、181.154876、135.377075秒：step1→Sunflowers、Sunflowers→Speed 5、Speed 5→step2原日志。Sunflowers在Speed 4之后、Speed 5之前解锁；首次向日葵成熟收获发生在1170.599476秒，距解锁应用13.859283秒。升级成本在应用时刻支付，不等于API返回时间；下表覆盖这次前缀内全部19次成功升级。

| 科技 | 新等级 | 应用游戏秒 | 预计返回游戏秒 | 实际支付成本 |
| --- | ---: | ---: | ---: | --- |
| Speed | 1 | 10.892500 | 11.225833 | 20 Hay |
| Expand | 1 | 26.167503 | 26.500836 | 30 Hay |
| Plant | 1 | 51.669175 | 52.002508 | 50 Hay |
| Expand | 2 | 85.280848 | 85.614182 | 20 Wood |
| Carrots | 1 | 146.045860 | 146.379194 | 50 Wood |
| Speed | 2 | 444.289253 | 444.511476 | 20 Wood |
| Expand | 3 | 474.770389 | 474.992611 | 20 Carrot + 30 Wood |
| Speed | 3 | 582.649364 | 582.797512 | 50 Carrot + 50 Wood |
| Trees | 1 | 665.719023 | 665.867171 | 70 Carrot + 50 Wood |
| Watering | 1 | 695.159774 | 695.307922 | 50 Wood |
| Expand | 4 | 744.073865 | 744.222013 | 50 Carrot + 100 Wood |
| Watering | 2 | 790.093881 | 790.242029 | 200 Wood |
| Carrots | 2 | 830.179821 | 830.327969 | 250 Wood |
| Fertilizer | 1 | 946.775417 | 946.923566 | 500 Wood |
| Speed | 4 | 966.073202 | 966.171968 | 500 Carrot |
| Watering | 3 | 1098.980588 | 1099.079354 | 800 Wood |
| Sunflowers | 1 | 1156.740193 | 1156.838958 | 500 Carrot |
| Carrots | 3 | 1280.385588 | 1280.434971 | 1250 Wood |
| Speed | 5 | 1337.895069 | 1337.927991 | 1000 Carrot |

整个step1+step2前缀成功升级共支付100 Hay、3370 Wood、2190 Carrot；其中step2为3300 Wood、2190 Carrot。全部成功种植另支付1441 Hay、1441 Wood、688 Carrot；不能把向日葵解锁的500 Carrot当作全部产电投入。水/肥实际使用180/52份，被动收到220/52份，期末40/0。此账只列实际支出，不将生产这些材料的所有时间直接归因给某一科技。

### 向日葵毛收入、耗电与期末库存

成功种植688株，成熟收获676株：594次×1 Power、82次×8 Power，共1250 Power；结束尚有12株未收。期末净库存1000.076667，收入减库存为249.923333，表示期间已结算的Power支出；未在此虚构未结算used_power。Speed 5支付时累计毛收入218、净库存105.108833；其后再产1032，库存净增加894.967833。

已收676株从种下到收获的平均年龄5.364984秒。按每株最后未成熟与首次已成熟快照，平均成熟年龄只能约束在1.210758～5.215571秒，成熟后未收平均区间为0.149412～4.154226秒。这些是每株的观测区间，时间彼此重叠，不能相加成全局等待秒或当作已知成熟事件时刻。

### 能辨明的step2时间占用

单机副作用API的[api_time_ns, ready_ns)区间已逐段核对不重叠，并裁剪至两个原日志get_time边界。以下按实际时间累加，包含当时Speed与Power变化；random、解释器、分支和调度无法由现有轨迹单独拆开，保留余项。

| 占用 | 游戏秒 | 占step2 |
| --- | ---: | ---: |
| 种植API | 350.362656 | 26.405% |
| 收获API | 338.224482 | 25.490% |
| 移动API | 491.432722 | 37.036% |
| 翻土API | 11.888894 | 0.896% |
| 使用水肥API | 15.687274 | 1.182% |
| 升级尝试API（成功和失败） | 5.435581 | 0.410% |
| 其余已分离API | 17.654495 | 1.331% |
| 解释器、random与调度余项 | 96.206845 | 7.251% |
| 合计 | 1326.892950 | 100.000% |

can_harvest=false本身的API时间仅0.492120秒，已经包含在上表，不能另加。识别到718次判熟失败后未收割、未种植或施肥便移走的访问，从失败查询到移动返回合计52.744129秒（3.975%，也已包含在上表）；这是巡视与判断区间，不是纯等待。step2没有连续两次false can_harvest形成的纯轮询序列。成熟与其他格生产重叠，纯成熟等待的全局墙钟占比仍为未知，不将全部false查询或株秒归为等待。

原始数据及推导代码在 `.codex/leaderboard-sol/reset/a-stage/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.jsonl`、`seed1.client.json`、`analyze.py`、`accounting.json`和`sunflower-lifetimes.json`。轨迹SHA `312baf8f44943c05288dcb5a792d48d6e9601e9fe82418dcc1efa16bfeeed2b7`与模拟报告一致。

本项为单seed前缀观测，不是新优化算法。该副本的完整Reset本地模拟预估时间、短时打榜测试时间和游戏打榜时间均为未取得/null，1473秒前缀或1327秒step2不代填完整时间；此前骨头尾段候选三值独立保留。正式py与真实Save0均未修改，未开展实机或同seed模型精度验收。观测交Astra结合静态科技成本选择一个结构方向，不重跑已失败的提前Sunflowers，不扩seed或枚举cap。

## 提前Speed 2：集中补20 Wood的单次A段筛选

候选SHA `bdf14ca61eedefdb1fdf4594ce6f2baafff4ebd3b8121ecb0e9de59296d04ad5`，从前述A段原版观测副本复制，只在原step1日志后、step2前增加farm_wood_until(20)和unlock(Unlocks.Speed)。复用既有helper，保留step2原日志后return；无新增函数定义，其余模块AST与观测原版一致，不混入骨头尾段、向日葵结构或科技cap候选。沿同reset场景只运行seed 1一次，仍为55秒总墙钟、30万API、300万检查点、trace256MiB硬限；工作4.129秒正常结束，78718次API、194084检查点，轨迹17560034字节，未触预算。

原start/step1两条日志逐字相同，完整基线复用前述观测，不重跑原版或其他seed。Wood初始1，helper首次检查146.384193765秒，到175.554199599秒首次读到20，观察跨度29.170006秒；包含最终查询返回为29.171673秒。Speed 2应用175.557532933秒、返回175.779755333秒，花20 Wood；从原step1日志到升级返回共29.400562秒。以下净收益已经包含补木及升级，不把这段准备排除。

| Speed新等级 | 原版应用游戏秒 | 候选应用游戏秒 | 候选预计返回游戏秒 | 提前游戏秒 |
| --- | ---: | ---: | ---: | ---: |
| 2 | 444.289253 | 175.557533 | 175.779755 | 268.731720 |
| 3 | 582.649364 | 413.285501 | 413.433649 | 169.363863 |
| 4 | 966.073202 | 806.024157 | 806.122922 | 160.049045 |
| 5 | 1337.895069 | 1200.851989 | 1200.884911 | 137.043080 |

| 时间边界 | 原版游戏秒 | 候选游戏秒 |
| --- | ---: | ---: |
| step1原日志 | 146.379194 | 146.379194 |
| step2原日志 | 1473.272143 | 1350.878036 |
| step1→step2日志区间，候选包含准备 | 1326.892950 | 1204.498843 |

含准备的A段净省122.394107秒（9.224%）。候选首个step2 Power循环API发生于175.779755333秒，从该点到step2日志为1175.098281秒；这只是函数内观察区间，不能用它排除补木投资后再与原版总阶段比较。应用Sunflowers从1156.740193提前至998.754361秒，首次成熟收花从1170.599476提前至1012.598829秒。

### 期末科技相同，资源差额先列后段负债

两版全部科技字典相同：Speed 5、Expand 4、Carrots 3、Trees 1、Grass 1、Watering 3、Fertilizer 1、Sunflowers 1、Plant 1；原有15项基础能力保留，其他科技仍0。完整科技字典和全部12项库存均保存在comparison.json，不以节时替代资源验收。

| 库存 | 原版 | 候选 | 候选减原版 |
| --- | ---: | ---: | ---: |
| Bone | 0 | 0 | 0 |
| Cactus | 0 | 0 | 0 |
| Carrot | 3 | 0 | -3 |
| Fertilizer | 0 | 0 | 0 |
| Gold | 0 | 0 | 0 |
| Hay | 4 | 5 | 1 |
| Piggy | 0 | 0 | 0 |
| Power | 1000.076667 | 1001.098333 | 1.021667 |
| Pumpkin | 0 | 0 | 0 |
| Water | 40 | 42 | 2 |
| Weird_Substance | 170 | 120 | -50 |
| Wood | 960 | 1302 | 342 |

Carrot少3、Weird少50是待核算的后段负债，不能直接折成整轮净收益。Wood多342、Hay多1、Water多2、Power多1.021667，Fertilizer期末仍0。两版成功升级总支出相同，候选未跳过科技换取节时；种植支出则由1441 Hay/1441 Wood/688 Carrot变为1460/1460/718。候选用水199份、用肥58份（原180/52），被动供水241份、供肥58份（原220/52）；更早的解锁时刻会改变补给时序，不能只按总时长推断末态。

### Power毛净账

| 产电项目 | 原版 | 候选 |
| --- | ---: | ---: |
| 成功种花 | 688 | 718 |
| 成熟收花 | 676 | 706 |
| 一倍 / 八倍收获次数 | 594 / 82 | 624 / 82 |
| 毛Power | 1250 | 1280 |
| 期末净Power | 1000.076667 | 1001.098333 |
| 已结算Power支出 | 249.923333 | 278.901667 |
| 期末未收花 | 12 | 12 |

候选21922条非Power库存读数与推导账相符，所有非Power末态一致于账本，轨迹SHA与报告一致。插入准备后动作量和随机轨迹已改变；不能把122秒全部归因为基线同动作加速的91秒预算。现有轨迹仍不能单独确定纯成熟等待的全局占比。

证据在 `.codex/leaderboard-sol/reset/early-speed2/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.jsonl`、`seed1.client.json`、`accounting.json`、`comparison.json`、`three-times.json`及推导代码`analyze.py`。该副本尚未完成完整Reset，本地模拟预估时间、短时打榜测试时间和游戏打榜时间均为null；原骨头尾段三值独立保留。

按准入停止条件，现交Astra核算Carrot/Weird及供给时序的后段影响，再决定是否推进step3或完整Reset；当前不扩seed、不继续完整候选或实机。正式py及真实Save0未修改。
