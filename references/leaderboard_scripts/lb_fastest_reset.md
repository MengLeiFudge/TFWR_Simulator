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
  - 90 秒窗口和 60 秒窗口均返回 `status=done`，不再卡在迷宫金币或骨头阶段。
- 当前结论：
  - 快速重置当前已有可完成路线。
  - `Expand 7`、`Megafarm 2+`、`Dinosaurs 4+` 都是已验证不适合当前默认路线的过度投资。
  - `Mazes 2` 仍保留，因为它减少金币阶段的宝箱迁移次数；金币单批 `600` 在 `300 / 600 / 1200` 中当前证据最好。
- 提交后继续 A/B：
  - `request_id=145`：当前基线墙钟约 `9.64s`。
  - `request_id=146`：跳过 `Mazes 2` 仍能完成，但墙钟约 `9.98s`，暂不采用。
  - `request_id=147`：只升到 `Dinosaurs 2` 仍能完成，但墙钟约 `10.60s`，暂不采用。
  - `request_id=148`：金币单批 `450` 仍能完成，但墙钟约 `10.62s`，暂不采用。

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

## 下一步优化方向

- 当前路线已经能完成一轮，下一步应围绕真实成绩继续压缩阶段耗时，而不是再追求“能跑通”。
- 必须补证据的关键点：
  - 每个解锁门槛前后的资源短板
  - 迷宫 / 金币 / 无人机阶段是否真的比继续滚基础资源更值
  - `step4()` / `step5()` 最短完成条件
- 下一轮优先级：
  - 清理 `step2/step3` 的胡萝卜 / 肥料 / 向日葵资源警告
  - 评估 `Mazes 2` 是否在最终成绩上优于不升迷宫等级
  - 继续压缩 `farm_gold_single_cycle()` 的寻路与奇异物质补给节奏
  - 评估 `Dinosaurs 2` 与 `Dinosaurs 3` 的骨头总时间差

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
