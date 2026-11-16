# 快速重置（`lb_fastest_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_reset.py](../../scripts/leaderboard/lb_fastest_reset.py)。公开账号最高 **41:47.696（#35）**；2026-11-16 request528 首轮41:41.503 后，第二轮 `directed_failed bone_incomplete_cycle` 中断使整场统计作废、未能上传。已有最好本地模拟 **41:11.034**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869903/)，榜单抓取时间 `2026-11-15T14:58:45.856608+00:00`，账号查询时间 `2026-11-15T14:58:45.856644+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

从原版1×1、零库存发展到伴生和8机。单机向日葵走最短环绕路径，收花后仅用现有Carrot补低于当前瓣档的新花；每批最多补size株、每株最多16次尝试，剩余少于10株时不补种，不追加筹资。boost_stock跨原料订单保留作物及支撑，蛇形往返生产；Trees5、Watering5和实际供电后提前筹最终迷宫Weird，用联产Wood支付Carrots5/6和Watering6。中期两座4×4、四座6×6独立宫筹第2/3次机，末段八座5×5/M4宫筹百万Gold。16×16、D4前三蛇255实体，末蛇按缺口取235，正常换帽共得2002400 Bone后支付解锁。

2026-11-15当前源完整seed1/2/3为2445.382402019/2471.831149448/2495.889700415秒，均2471.034417294秒；同批父版`5f34716`为2464.635501042/2479.786027471/2492.895979468秒，均2479.105835994秒，改善8.071418700秒（0.33%），seed3慢2.993720947秒。最终文件再次执行三例，逐项相同。历史request506前两轮短筛2504.565秒，正式三轮2498.140/2510.990/2513.958秒、均2507.696秒；本版尚未实机。

当前seed1累计边界：0→1158.85秒发展至Polyculture；1158.85→1217.14秒取得双机；1217.14→1308.96秒四机；1308.96→1517.61秒八机；1517.61→1935.38秒科技/原料投资包；1935.38→2094.92秒最终金币；2094.92→2445.382402秒完整恐龙结算和解锁。该段含混采与控制，不是各API纯耗时。

当前末段向日葵按花瓣整组达1600停止，骨头前最低400；本版三seed终点Wood18118～21676、Power90.012～142.658；历史实机末Power146.57～247.14。Watering6多余水来自后续自动积累，肥料287～291、Cactus19296、Bone2400、Gold40属于未回本投资或整批余量，不为清零额外做动作。

解锁Leaderboard实付2M Bone＋1M Gold；脚本unlock不检查UI父连线，但附加条件仍有效。骨头只允许一顶帽，其他机改高度会移除苹果，不安排并行农活。按每条(n²−1)²×2^(D−1)、真实苹果费用及整轮数比较D级数和地图，D5需要2592000 Cactus。已有“不值得只为少两条蛇买D5”的成本账限于当时8机/Cactus2的生产条件，不排除早期伴生3、16机、Cactus3一起改变回本条件。

### Josh 28:03视频：阶段目标与路线差异

来源：[Josh：WORLD RECORD FULL RESET (28:03)](https://www.youtube.com/watch?v=hdBSvuOim74)，发布于2025-11-09，2026-11-16读取说明、评论及相关作者回复，并按阶段查看41张真实1080p视频帧。终点日志是`Unlocks.Leaderboard 1 || Time: 28:3.13`；画面可见`simulate("Main2.0", {}, {}, {}, 83, 1)`，作为作者的一次路线展示，不写成当前公开榜成绩或本机完整统计。下表时间均取画面内游戏日志；YouTube播放位置通常晚约1.6～1.9秒。原始帧、公开回复、67项升级转录及校核在`.codex/youtube-reset-20261116/`，以`frame-manifest.json`和`observations.json`定位。

| 游戏时间段 | 阶段目标 | 画面与升级日志 |
| --- | --- | --- |
| 0:00→2:10.38 | 打开种植、速度和胡萝卜 | Expand1 0:41.02、Plant1 0:41.65、Speed1 1:03.47、Expand2 1:15.62、Speed2 1:33.08、Carrots1 2:10.38；由1×1扩到1×3、3×3 |
| 2:10.38→5:54.13 | 用低阶混采进入6×6 | 草、灌木、胡萝卜同时保留；先Grass2 3:47.91，再Trees1/2、Expand3、Carrots2、Speed3 5:36.29、Watering1、Expand4 5:54.13 |
| 5:54.13→7:57.89 | 先筹胡萝卜与首次供电条件 | Watering2 6:15.61、Carrots3 7:01.77、Grass3 7:35.37、Sunflowers1 7:57.89；尚未买Trees3/Grass4 |
| 7:57.89→10:20.63 | 供电后继续提速并筹南瓜种子 | 8:03.377时Power0，8:18.378时Power5，8:58.385时125；其间Fertilizer1 8:49.59、Speed4 8:55.49、Watering3 9:15.35，最后Pumpkins1/2 |
| 10:20.63→11:35.87 | 南瓜支付首次伴生 | 可见局部南瓜合并与坏苗；Polyculture1 11:35.87 |
| 11:35.87→12:34.61 | 补科技并取得第一台子机 | Trees3、Fertilizer2、Watering4、Speed5 12:08.32、Mazes1 12:13.51、Megafarm1 12:34.61 |
| 12:34.61→15:20.13 | 双机补产量并扩到12×12 | Expand5、Grass4、Trees4、Watering5、Fertilizer3、Carrots4、Pumpkins3、Expand6 15:16.84、Cactus1 15:20.13 |
| 15:20.13→16:16.89 | 第一批仙人掌开启D2恐龙 | Dinosaurs1/2分别在16:16.84/16:16.89购买 |
| 16:16.89→17:30.91 | 提前跑两条蛇供高阶伴生 | 12×12田上确实跑恐龙；Polyculture2 16:46.15、Polyculture3 17:30.91，随后Bone只剩500 |
| 17:30.91→20:48.60 | 高阶伴生与筹金交替，双机扩到16机 | Mazes2、Megafarm2 18:05.11、Megafarm3 18:54.92、Grass5、Trees5/6、Fertilizer4、Watering6/7、Mazes3 19:58.96、Megafarm4 20:48.60；17:38和17:58画面仍为12×12迷宫中正常行走 |
| 20:48.60→21:56.21 | 为更高恐龙产量建立生产包 | Carrots5/6、Pumpkins4/5/6、Expand7 21:26.21、Cactus2/3 21:56.17/.21；地图16×16、16机 |
| 21:56.21→24:28.40 | 集中仙人掌购买D5 | Dinosaurs3/4 24:09.62/.67、Dinosaurs5 24:28.40；视频确实为较高终盘产量支付了额外仙人掌投资 |
| 24:28.40→27:09.86 | 两条D5恐龙完成最终骨头 | 第一条后Bone约1.04M，第二条后约2.08M；接着买Mazes4 27:09.86，两个节点相隔2:41.46 |
| 27:09.86→28:03.13 | 末段筹百万金币并解锁 | 左下4×4密集驻机，其余地面自然长草；27:43.125时Gold577k、28:02.073时963k，最终Leaderboard1 28:03.13。此53.27秒包含已被修复的maze spam，不能直接迁入 |

**迷宫边界。** 用户指出的“4×4密集驻机刷金”与末段画面相符。[视频说明](https://www.youtube.com/watch?v=hdBSvuOim74)预告将修复maze spam；[作者回复](https://www.youtube.com/watch?v=hdBSvuOim74&lc=UgzetcKh1HkkEqg0ZJJ4AaABAg)写明“The only thing broken is the maze strat - it got patched out”，[另一回复](https://www.youtube.com/watch?v=hdBSvuOim74&lc=UgzJke5WrkVZIpDpBw14AaABAg)强调现在必须正常解迷宫。这条录像只买到Megafarm4即16机，没有确认“每格两机”的具体配置，也没有源码证明漏洞的调用顺序；不把这些推断记成事实。当前模拟器`Treasure`的`repositioning`防重入、移动期间不可收割及301次上限可静态核对，但不能仅凭这些反推旧版补丁的确切实现。前期正常走迷宫与末段spam分别判断。

**与当前路线比较。** 对照采用现存完整seed1报告`.codex/gemini-reset-maze-20261115/final-reset-seed1.json`（40:45.382，达到原目标）；其冻结源码与当前源码的Python AST一致，差异为后续注释。视频seed83与本地seed1不是同条件因果实验，下表用于找路线分歧，不把时差直接承诺成可追回收益。

| 节点 | 视频游戏时间 | 当前seed1游戏时间 | 当前较晚 |
| --- | --- | --- | --- |
| Grass2 | 3:47.91 | 7:34.91 | 3:47.00 |
| Speed3 | 5:36.29 | 5:45.49 | 0:09.20 |
| Expand4（6×6） | 5:54.13 | 9:22.82 | 3:28.69 |
| Carrots3 | 7:01.77 | 12:48.29 | 5:46.52 |
| Sunflowers1 | 7:57.89 | 14:28.25 | 6:30.36 |
| Polyculture1 | 11:35.87 | 19:18.85 | 7:42.98 |
| 首次双机 | 12:34.61 | 20:17.14 | 7:42.53 |
| 八机 | 18:54.92 | 25:17.61 | 6:22.69 |
| Polyculture2/3 | 16:46.15／17:30.91 | 整轮未购买 | 现行仅伴生1 |
| 终盘生产包 | 16机／Cactus3／D5 | 8机／Cactus2／D4 | 需重新算完整投资回报 |

视频在第一次伴生之前已领先7:42.98，当时还没买Mazes；末段旧迷宫不能解释这一段。Speed3则只差9.20秒，不能继续笼统归因于“速度升级晚”。更具体的分歧是：视频先Grass2，再Trees2/Carrots2/6×6、水和Carrots3、首次供电；当前先推进Trees1、Expand3、Speed3，才买Grass2，又在供电前支付Trees3和Grass4。视频的Trees3、Grass4均在供电后。应比较前缀的完整资源账和供电时点，而非只交换一个升级后看瞬时领先。

中期另一项实质分歧是先跑D2恐龙，为Polyculture2/3支付共60000 Bone，再扩大生产。当前整轮停在伴生1。历史上确实试过D1筹骨买Poly2：2026-11-12三seed完整均2749.113418634秒，对同批采用版2751.645866159秒，平均快2.532447525秒；seed3慢18.739022583秒，因此当时未采用。生成脚本`.codex/reset-persistent-20261112/make_poly2.py`是在既有`staged_supply`前插入一条短蛇和一次伴生购买，后续等级／终盘包仍沿用原安排；三份`ground-funded-poly2-s*.json`保留完整结果。这个局部组合没有比较视频中的D2→Poly3及后续16机/C3/D5，不能据它选择整轮固定Poly1。按现行`5 << polyculture`，伴生1→3对命中收获的倍率由10升40，为原来的4倍；整轮还含未命中、种子、支撑、移动和筹骨成本。早期14000 Cactus的D1/2科技费、真实苹果费用、清场重建和后续Weird/Wood混采收益应作为同一条路线计价。

作者还确认了[草地自然产草以省plant](https://www.youtube.com/watch?v=hdBSvuOim74&lc=UgwbT_kL7TvliM9JDzt4AaABAg)、仙人掌cocktail sort、恐龙先搜索再带捷径的Hamiltonian回路。当前`tick_cell`已利用自然草地，不能把相同做法列为新收益；评论里未由作者确认的猜测不替代画面或源码。

此前遗漏的原因是把“有没有可直接迁入的公开代码”放在过高优先级，又因旧迷宫失效过早降低整条视频的研究优先级。对当前脚本及旧成本记录的进一步核对表明，主要问题是把现行固定升级顺序和按笔供料当成研究边界，缺少以最终解锁时间比较整条路线的成本表：

- **供电排序没有先作交换计算。** 入口固定先买Trees3、Grass4等再解锁Sunflowers和补电；这些产量科技不直接提高向日葵产能，却把其后的工作留在无电状态。应先比较提前供电的投资与之后全部可加速工作的收益，再决定哪些科技确实有必要先买。
- **只试了高阶伴生的一种局部插入。** 上述Poly2结果没有支持继续固定Poly1，也没有覆盖Poly3、购买时点与新生产率下的其他升级。小幅均值改善且有单seed回退说明该实现需要进一步判断，不能关闭高阶伴生规划。
- **有混种，但缺少跨升级目标的种植和等待安排。** `basic(cost)`只收眼前这一笔科技所需的资源；`tick_cell`在仍缺Hay时不主动补Carrot，随后全田巡回。保留未熟作物并不等于已实现“多数格生长长周期作物，少数格短闭环收草”的调度；应按后续需求和成熟时刻规划配比、回访与购买。
- **组合粗算没有覆盖。** 现有D5理由按8机/C2估算额外仙人掌时间，历史16机负例属于另一固定科技顺序；两者都不是16机/C3/D5、高阶伴生组合的成本账。目前没有可出示的该组合完整粗算，记录为漏项，不能写成已研究后排除。按一阶吞吐估计，8→16机与C2→C3可令可并行仙人掌段的同量生产时间缩至约1/4，已足以要求把组合列入初筛，再计额外科技投资与串行成本。

共用的供电交换计算、逐级伴生、成熟等待重叠和组合成本表归[重置榜的科技路线计价](README.md#重置榜的科技路线计价)。这些要求此前已有方向性说明，实际执行没有给出覆盖这些决策的账表；问题不能归因于模拟复杂或算不动。后续粗算表须区分已计算、机制排除和未计算，完成后才选代表写脚本。研究录屏先记录阶段目标、升级时刻、地图/机数、关键库存和可见动作，再逐机制标注版本差异；只淘汰已证明失效的那一段。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 只提前双机，再补原科技 | 双机约883～902秒；三seed完整均2851.091秒，对当时2790.992秒 | 低产量/速度的筹资与后续补购回吐前缀领先 | [20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py) |
| 低科技先伴生、推迟首次供电 | 缺肥代表2217.230秒退出；先供电P1完整2948.098秒 | 只证明这些固定支付顺序无收益，不否定所有早并行 | [20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py) |
| 终点保留Mazes3、较早扩田或16机 | M3完整2877.175秒；历史16机包3081.834秒 | 少投资增加导航/重建，早买机增加Gold/Weird并挤掉供能 | [20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py) |
| 每单清场、整田批量备料 | 普通完整3504.220秒 | 丢掉未熟作物与自然伴生，已由保场订单替代 | [20261111_rejected_ground_bulk_basic.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_ground_bulk_basic.py) |
| 全科技向日葵批水/目标退出直接迁入 | 往返组合2752.542/2756.377秒，对当时采用2744.219秒 | 水库存竞争、低科技成本及完整时序不同；功能收益不能直接套整轮 | [20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py) |
| 统一四条250节 | seed1完整2511.468秒，对同前缀2501.429秒 | 每步计数开销抵消少吃果；只计末条缺口的235节版本才被采用 | [20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py) |
| 提早在水电前混采Weird | seed1完整2610.187秒，比同阶段父慢109.022秒 | 联产木头有用，但到货时点与当时速率不合适 | [20261112_rejected_followup_lb_fastest_reset-mixed-early.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-mixed-early.py) |
| 已有肥料催回访南瓜、购买F3催熟 | 三seed2522.040秒对2514.803秒；F3首seed2511.712秒慢10.546秒 | 催熟/感染/费用没有完整回本，只关闭所测政策 | [20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py) |
| 仙人掌窗口复用＋单调边界/仅缓存 | seed1完整2472.427480/2465.679293秒，对2464.635501秒 | measure少约43%仍未改善整轮，成熟与后续时序反馈须实测 | [20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py) |
| 单机太阳花仅改最短环绕 | 三seed完整均2476.690677629秒，对2479.105835994秒，省2.415秒 | 单项有效，现已被增加有限低瓣补种的2471.034秒组合替代 | 从`5f34716`的`solar_reserve`将原正向East/North到点循环替换为`go(x,y)`即可重建；原报告`.codex/gemini-reset-maze-20261115/reset-solar-shortest-seed*.json` |
| 同瓣最近邻贪心选点 | 三seed完整均2480.776315973秒，比共同父版慢1.670秒 | 单seed领先不足代表整轮平均收益；本实现不采用 | 在上行版本中，每瓣反复按环绕曼哈顿距离选最近点、`pop(best)`后`go`；原源`solar-nearest/lb_fastest_reset.py`与报告留同一`.codex`目录 |

本批均为原版重置初始条件和目标，每例15墙钟秒、最多两进程；原版Parser、正常终态、实际目标、依赖与程序集/资源指纹逐项核对。最终源仅剩主机，报告索引`.codex/gemini-reset-maze-20261115/results.json`。ty与冻结父版同为14处既有类型错误及15条提示，新增代码无诊断；没有将LSP写成零错。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_fastest_reset/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_fastest_reset/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 补齐最快重置候选路线 | [20260424_v03_24db7f57.py](../../references/leaderboard_history/lb_fastest_reset/20260424_v03_24db7f57.py) |
| 2026-04-25 | 未记录 | 跑通最快重置阶段路线 | [20260425_v04_d6dc2b6e.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v04_d6dc2b6e.py) |
| 2026-04-25 | 未记录 | 拦截最快重置误判与非法语法 | [20260425_v05_071c0e74.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v05_071c0e74.py) |
| 2026-04-25 | 未记录 | 推进快速重置榜单策略 | [20260425_v06_1fbc7898.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v06_1fbc7898.py) |
| 2026-04-25 | 未记录 | 改进快速重置伴生产线 | [20260425_v07_55c10ac1.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v07_55c10ac1.py) |
| 2026-04-26 | 未记录 | 迁入并验证外部最快重置候选 | [20260426_v08_1f586600.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v08_1f586600.py) |
| 2026-04-26 | 未记录 | 提前快速重置多机南瓜节奏 | [20260426_v09_c5cbe7b3.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v09_c5cbe7b3.py) |
| 2026-04-26 | 未记录 | 提前快速重置二级巨大农场 | [20260426_v10_6d9e7f57.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v10_6d9e7f57.py) |
| 2026-04-26 | 未记录 | 扩大快速重置金币批次 | [20260426_v11_da25aa36.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v11_da25aa36.py) |
| 2026-04-26 | 未记录 | 调整快速重置顺手补电地板 | [20260426_v12_b45afab6.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v12_b45afab6.py) |
| 2026-04-26 | 未记录 | 提高快速重置顺手补电阈值 | [20260426_v13_b0c7432f.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v13_b0c7432f.py) |
| 2026-04-26 | 未记录 | 提高快速重置补电稳定阈值 | [20260426_v14_56a1c015.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v14_56a1c015.py) |
| 2026-04-26 | 未记录 | 跳过快速重置金币空批次迷宫 | [20260426_v15_9a8cecf8.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v15_9a8cecf8.py) |
| 2026-04-26 | 未记录 | 修正快速重置金币收益估算 | [20260426_v16_e7b80a9f.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v16_e7b80a9f.py) |
| 2026-04-26 | 未记录 | 减少快速重置金币墙刷新 | [20260426_v17_61702cc1.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v17_61702cc1.py) |
| 2026-04-26 | 未记录 | 快速重置骨头阶段追苹果 | [20260426_v18_58c31f70.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v18_58c31f70.py) |
| 2026-04-26 | 未记录 | 采用快速重置肥料上限 | [20260426_v19_7f6fc675.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v19_7f6fc675.py) |
| 2026-05-31 | 版本注记 168m48.299s | 调整：收敛 leaderboard 脚本真源 | [20260531_v20_168m48.299s_0224fb21.py](../../references/leaderboard_history/lb_fastest_reset/20260531_v20_168m48.299s_0224fb21.py) |
| 2026-10-27 | 53:43.604（2026-10-26，官方完整3轮，request 94）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v21_53m43.604s_9d2d3c31.py](../../references/leaderboard_history/lb_fastest_reset/20261027_v21_53m43.604s_9d2d3c31.py) |
| 2026-10-27 | 52:15.911（2026-10-26，官方完整3轮，request 98）。 | 南瓜修补队列将快速重置缩短至52分15秒 | [20261027_v22_52m15.911s_ffe7fc79.py](../../references/leaderboard_history/lb_fastest_reset/20261027_v22_52m15.911s_ffe7fc79.py) |
| 2026-10-29 | 51:46.851（2026-10-28，官方完整3轮，request 182）。 | 快速重置骨头阶段迁入边界绕行 | [20261029_v23_51m46.851s_4ebac87d.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v23_51m46.851s_4ebac87d.py) |
| 2026-10-29 | 50:24.677（2026-10-28，官方完整3轮，request 185）。 | 快速重置提前补电覆盖南瓜与扩田供料 | [20261029_v24_50m24.677s_9bbe4daf.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v24_50m24.677s_9bbe4daf.py) |
| 2026-10-29 | 50:00.960（2026-10-28，官方完整3轮，request 188）。 | 快速重置仙人掌排序覆盖成熟等待 | [20261029_v25_50m00.960s_20f73959.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v25_50m00.960s_20f73959.py) |
| 2026-11-11 | 未取得；C#原目标3seed均值2790.992秒（2026-11-11，当前策略未实机）。 | 调整双重置迷宫筹资与矿物投资路线 | [20261111_v26_46m30.992s_8ec59b43.py](../../references/leaderboard_history/lb_fastest_reset/20261111_v26_46m30.992s_8ec59b43.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值2751.646秒（2026-11-12，当前策略未实机）。 | 重置榜按原料订单保留伴生产区 | [20261112_v27_45m51.646s_425a5024.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v27_45m51.646s_425a5024.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值2744.219秒（2026-11-12，当前策略未实机）。 | 迁入重置榜常驻采集与分区复用 | [20261112_v28_45m44.219s_5f25fe9a.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v28_45m44.219s_5f25fe9a.py) |
| 2026-11-12 | 2703.337666667秒（2026-11-12，实机完整3轮）；C#原目标3seed均值2682.885秒。 | 迁入恐龙递归追果并完成快速重置实机 | [20261112_v29_44m42.885s_56b4d84d.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v29_44m42.885s_56b4d84d.py) |

## 下一步优化方向

- **首先比较首次供电前缀。** 以Grass2先于高价供料、Watering2与Carrots3提前、Trees3/Grass4延后为一个明确候选；保留现有混采存量并计入下一阶段种子和电量。阶段检查取首次正Power、Polyculture1、双机与整轮，不能因前缀领先就采用。视频提供较强路线依据，当前版本收益尚未验证。
- **单独比较早期D2→Polyculture2/3。** 用12×12两条恐龙筹伴生升级，联算恐龙投资、苹果、清场与Weird/Wood后续混采回报。先作有限成本账再跑完整重置；不能用历史“低科技先伴生”负例替代本组合的验证。
- **重算16机/Cactus3/D5的完整包。** 同时比较8机/C2/D4、提高伴生但保留8机、16机/C3/D5；视频末段maze spam必须换成当前合法筹金方式。旧16机包负例与旧D5单项成本只关闭各自当时的条件。
- 向日葵有限低瓣补种已有完整对照；多机统一时钟、混采静态共享支撑仍可作为独立候选。地下榜同步研究共用前缀时，按竹子/炸药终点重新判断早期骨头和高阶伴生是否回本，不能照搬普通榜终盘。
- 末田仙人掌只调库存阈值仍需第8田；若研究部分连通收获，需同时覆盖苹果、科技付款和平方产量，不把余额直接当省时。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
