# lb_fastest_reset

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
- 当前实现只完整写到了：
  - `step1()`：从开局推进到解锁胡萝卜
  - `step2()`：混种并升级速度，直到积累 `1000 power`
  - `step3()`：刷奇异物质、解锁迷宫，并推进更多无人机相关资源
- `step4()` 和 `step5()` 目前还是空实现，因此当前脚本并不是完整可交付基线
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
