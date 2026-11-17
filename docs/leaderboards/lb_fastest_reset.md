# 快速重置（`lb_fastest_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_reset.py](../../scripts/leaderboard/lb_fastest_reset.py)。公开账号最高 **41:47.696（#36）**；本轮已采用视频开局、提前伴生3及16机/Pumpkins6/Cactus3/D5，尚未实机。当前有效本地场均 **34:44.124**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869903/)，2026-11-16T16:08:17.450130+00:00刷新；账号核对时间16:08:17.450192+00:00。#1为22:47.800，本地均值距#1 **+52.4%**；#3、#10及账号来源见[进度总表](leaderboard_progress.md)和[公开快照](../../references/leaderboards/status_snapshot.md)。

`step1`先筹Expand/Plant，再按录屏的3×3草／灌木／胡萝卜布局及6×6棋盘树、胡萝卜配比推进；`opening_stock`保留长周期作物，用两格草短回访覆盖等待。供电后买首次伴生与双机，再补Trees3/Grass4。12×12先跑D2两条蛇，实际筹60000 Bone买伴生2/3；保留Trees5/Carrots6，利用Weird/Wood联产筹后续投资。C2先付M3，以合法小迷宫筹128000 Gold买16机；Pumpkins6供Cactus3，再全额支付M4/D5。末段16座4×4小迷宫正常筹百万Gold，两条D5蛇按骨头缺口结算；末蛇前按220 Power目标补电，不再补整田。最终实付2M Bone＋1M Gold。

2026-11-16采用源与改前冻结源按原版零库存重置目标比较，同用seed1..4、每批60墙钟秒、最多4进程，均累计超过7200游戏秒：

| 版本 | 完整轮数／累计游戏秒 | 均值／标准差／标准误（秒） | 逐轮游戏秒 |
| --- | --- | --- | --- |
| 改前8机/P1/C2/D4 | 4／9938.395685 | 2484.598921／29.514382／14.757191 | 2445.382402、2471.831149、2495.889700、2525.292433 |
| 当前视频开局＋P3/16机/P6/C3/D5 | 4／8336.497189 | 2084.124297／28.117375／14.058687 | 2117.298809、2106.540809、2058.985647、2053.671923 |

四轮均达原目标，平均省400.474624秒（16.1%）。最终正式路径另跑seed1，逐纳秒复现2117.298809458秒，只有主机、正常换回草帽。7200秒会话原报告为`.codex/reset-global-20261116/session-{ground-baseline,ground-final-80}.json`（原始材料已于 2026-11-17 清理），正式源单轮、源码/程序集/资源指纹与其他筛选回执见同目录`results.json`。本地seed随机源不同于正式榜加密随机源，不能当成已上传时间。ty仍有改前14处Measure相关类型错误；新增开局与投资代码无错误，未将既有诊断写成零错。

首seed阶段：Sunflowers解锁603.65秒；伴生1 901.93秒；双机984.83、四机1088.30；伴生2/3 1269.30／1323.36；八机1389.96、16机1636.11；投资完成1850.16；最终解锁2117.298809。末Bone906、Gold104、Power163.513，Wood161880/Cactus201560仍有联产和整田余量，尚未证明已最小。旧request528第二轮`bone_incomplete_cycle`使整场作废，公开记录仍为request506完整统计2507.696秒；本次4轮完成不代表已穷尽所有随机盘面。

### Josh 28:03视频：阶段目标与路线差异

来源：[Josh：WORLD RECORD FULL RESET (28:03)](https://www.youtube.com/watch?v=hdBSvuOim74)，发布于2025-11-09，2026-11-16读取说明、评论及相关作者回复，并按阶段查看41张真实1080p视频帧。终点日志是`Unlocks.Leaderboard 1 || Time: 28:3.13`；画面可见`simulate("Main2.0", {}, {}, {}, 83, 1)`，作为作者的一次路线展示，不写成当前公开榜成绩或本机完整统计。下表时间均取画面内游戏日志；YouTube播放位置通常晚约1.6～1.9秒。原始帧、公开回复、67项升级转录及校核在`.codex/sources/videos/youtube-hdBSvuOim74/`，以`frame-manifest.json`和`observations.json`定位。

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

**与本轮修改前路线比较。** 对照采用现存完整seed1报告`.codex/gemini-reset-maze-20261115/final-reset-seed1.json`（原始材料已于 2026-11-17 清理）（40:45.382，达到原目标）；其冻结源码与本轮改前源码的Python AST一致，差异为后续注释。视频seed83与本地seed1不是同条件因果实验，下表用于找路线分歧，不把时差直接承诺成可追回收益。

| 节点 | 视频游戏时间 | 改前seed1游戏时间 | 改前较晚 |
| --- | --- | --- | --- |
| Grass2 | 3:47.91 | 7:34.91 | 3:47.00 |
| Speed3 | 5:36.29 | 5:45.49 | 0:09.20 |
| Expand4（6×6） | 5:54.13 | 9:22.82 | 3:28.69 |
| Carrots3 | 7:01.77 | 12:48.29 | 5:46.52 |
| Sunflowers1 | 7:57.89 | 14:28.25 | 6:30.36 |
| Polyculture1 | 11:35.87 | 19:18.85 | 7:42.98 |
| 首次双机 | 12:34.61 | 20:17.14 | 7:42.53 |
| 八机 | 18:54.92 | 25:17.61 | 6:22.69 |
| Polyculture2/3 | 16:46.15／17:30.91 | 整轮未购买 | 改前仅伴生1 |
| 终盘生产包 | 16机／Cactus3／D5 | 8机／Cactus2／D4 | 需重新算完整投资回报 |

视频在第一次伴生之前已领先7:42.98，当时还没买Mazes；末段旧迷宫不能解释这一段。Speed3则只差9.20秒，不能继续笼统归因于“速度升级晚”。更具体的分歧是：视频先Grass2，再Trees2/Carrots2/6×6、水和Carrots3、首次供电；改前先推进Trees1、Expand3、Speed3，才买Grass2，又在供电前支付Trees3和Grass4。视频的Trees3、Grass4均在供电后。应比较前缀的完整资源账和供电时点，而非只交换一个升级后看瞬时领先。

中期另一项实质分歧是先跑D2恐龙，为Polyculture2/3支付共60000 Bone，再扩大生产。改前整轮停在伴生1。历史上确实试过D1筹骨买Poly2：2026-11-12三seed完整均2749.113418634秒，对同批采用版2751.645866159秒，平均快2.532447525秒；seed3慢18.739022583秒，因此当时未采用。生成脚本`.codex/reset-persistent-20261112/make_poly2.py`（原始材料已于 2026-11-17 清理）是在既有`staged_supply`前插入一条短蛇和一次伴生购买，后续等级／终盘包仍沿用原安排；三份`ground-funded-poly2-s*.json`保留完整结果。这个局部组合没有比较视频中的D2→Poly3及后续16机/C3/D5，不能据它选择整轮固定Poly1。按现行`5 << polyculture`，伴生1→3对命中收获的倍率由10升40，为原来的4倍；整轮还含未命中、种子、支撑、移动和筹骨成本。早期14000 Cactus的D1/2科技费、真实苹果费用、清场重建和后续Weird/Wood混采收益应作为同一条路线计价。

作者还确认了[草地自然产草以省plant](https://www.youtube.com/watch?v=hdBSvuOim74&lc=UgwbT_kL7TvliM9JDzt4AaABAg)、仙人掌cocktail sort、恐龙先搜索再带捷径的Hamiltonian回路。改前`tick_cell`已利用自然草地，不能把相同做法列为新收益；评论里未由作者确认的猜测不替代画面或源码。

此前遗漏的原因是把“有没有可直接迁入的公开代码”放在过高优先级，又因旧迷宫失效过早降低整条视频的研究优先级。对修改前脚本及旧成本记录的进一步核对表明，主要问题是把现行固定升级顺序和按笔供料当成研究边界，缺少以最终解锁时间比较整条路线的成本表：

- **供电排序没有先作交换计算。** 入口固定先买Trees3、Grass4等再解锁Sunflowers和补电；这些产量科技不直接提高向日葵产能，却把其后的工作留在无电状态。应先比较提前供电的投资与之后全部可加速工作的收益，再决定哪些科技确实有必要先买。
- **只试了高阶伴生的一种局部插入。** 上述Poly2结果没有支持继续固定Poly1，也没有覆盖Poly3、购买时点与新生产率下的其他升级。小幅均值改善且有单seed回退说明该实现需要进一步判断，不能关闭高阶伴生规划。
- **有混种，但缺少跨升级目标的种植和等待安排。** `basic(cost)`只收眼前这一笔科技所需的资源；`tick_cell`在仍缺Hay时不主动补Carrot，随后全田巡回。保留未熟作物并不等于已实现“多数格生长长周期作物，少数格短闭环收草”的调度；应按后续需求和成熟时刻规划配比、回访与购买。
- **组合粗算没有覆盖。** 现有D5理由按8机/C2估算额外仙人掌时间，历史16机负例属于另一固定科技顺序；两者都不是16机/C3/D5、高阶伴生组合的成本账。当时没有可出示的该组合完整粗算，记录为漏项，不能写成已研究后排除。按一阶吞吐估计，8→16机与C2→C3可令可并行仙人掌段的同量生产时间缩至约1/4，已足以要求把组合列入初筛，再计额外科技投资与串行成本。

共用的供电交换计算、逐级伴生、成熟等待重叠和组合成本表归[重置榜的科技路线计价](README.md#重置榜的科技路线计价)。这些要求此前已有方向性说明，实际执行没有给出覆盖这些决策的账表；问题不能归因于模拟复杂或算不动。后续粗算表须区分已计算、机制排除和未计算，完成后才选代表写脚本。研究录屏先记录阶段目标、升级时刻、地图/机数、关键库存和可见动作，再逐机制标注版本差异；只淘汰已证明失效的那一段。

### 开局种植与移动的复现

2026-11-16补看同一视频的68张真实相邻／阶段帧：3×3段取150～160播放秒、每0.5秒一帧，6×6段取420～426播放秒、每0.5秒一帧，另34张覆盖初始到首次供电。保存实际播放位置及SHA256，原图和索引在`.codex/reset-global-20261116/video/frames-{150,420,stages}.json`（原始材料已于 2026-11-17 清理）。以下坐标以左下为(0,0)，不是视频源码的转录；固定布局与移动由画面确认，未展示的调度条件仍须通过本地候选判断。

这次再次遗漏的原因是把“读到了升级节点”和“已经理解开局算法”混为一谈：此前41张疏采样画面没有还原完整巡回，又把现有`basic(cost)`的混采当作视频布局的等价实现。实际差异在固定格子的作物比例、草格访问频率及扩田后的配比切换；只交换科技顺序仍保留了原先的供料瓶颈。纠正方式是先保存相邻帧的格子／位置变化，能确认的直接写最小复现，再比较整轮；已合入[共用工作流](README.md#重置榜的科技路线计价)。

3×3混种画面对应草(0,0)/(0,1)，胡萝卜(1,0)/(1,1)/(2,2)，其余4格灌木。可见巡回按(0,1)→(1,1)→(1,2)→(1,0)→(2,0)→(2,1)→(2,2)→(0,2)回到草格，再在两格草往返；6×6按列向北、跨边界环绕继续下一列。当前候选的4秒草回访是有限实现选择，不能称为作者源码中的精确阈值。

| 地图／阶段 | 可见种植安排 | 移动与回访 |
| --- | --- | --- |
| 1×3、种植已解锁 | 先出现中间灌木和两端草；Speed1后可见下方两格灌木、上方草 | 竖直循环收补，草与木同时取得；Expand1与Plant1在41.02／41.65秒连续购买，实付30＋50 Hay，因此扩田前已筹齐两笔，不能照搬旧版扩田后巡回筹50草 |
| 3×3、Carrots1后 | 草(0,0)/(0,1)；胡萝卜(1,0)/(1,1)/(2,2)；灌木(0,2)/(1,2)/(2,0)/(2,1) | 连续帧可见中列和右列向北环绕收补，再经左上回到两格草，随后在两格草间短循环；不能只记“混采”而继续按自己的全田订单巡回 |
| 4×4、Expand3后 | 树／胡萝卜棋盘格，右列保留相邻草格 | 按列巡回，收草同时等待其他格；升级瞬间的新格自然草与之后完成布置分开记录 |
| 6×6、Carrots3前 | 树在奇数棋盘格；余格中x=0/3种胡萝卜，其余留草，即18树＋6胡萝卜＋12草 | 按列向北循环；不能将所有非树格都种胡萝卜，否则种子耗草挤掉后续增长 |
| 6×6、Carrots3后 | 仍保留奇数棋盘树；余格中x=0/3留草，其余改胡萝卜，即18树＋12胡萝卜＋6草 | 连续帧与前后画面共同确认配比变化；科技购买后的布局切换与成熟回访要一起复现 |

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| P3却缩减Trees/Carrots等级 | seed1完整2505.143632秒 | 基础产量被缩减后，后续Weird/Wood速率仍接近旧P1，高伴生投资没有兑现；只关闭此组合 | [缩减等级代表](../../references/leaderboard_history/lb_fastest_reset/20261116_rejected_poly3_reduced_yields.py) |
| 新前缀＋P1/16机/C3/D5 | 7200秒会话4轮均2336.066660秒，比2484.598921秒基线快 | 有效中间版，后被P3/P6及视频布局组合替代；证明旧8机/C2账不能排除D5 | [16机P1代表](../../references/leaderboard_history/lb_fastest_reset/20261116_rejected_poly1_16_c3_d5.py) |
| P3/16机/P6、仍用自己的开局巡回 | 7200秒会话4轮均2290.415902秒 | P6使额外仙人掌投资更便宜，但缺录屏的固定混种与回访；被当前2084.124297秒组合替代 | [尚未复现视频布局的组合](../../references/leaderboard_history/lb_fastest_reset/20261116_rejected_poly3_16_p6_without_video_layout.py) |
| 只提前双机，再补原科技 | 双机约883～902秒；三seed完整均2851.091秒，对当时2790.992秒 | 低产量/速度的筹资与后续补购回吐前缀领先 | [20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py) |
| 低科技先伴生、推迟首次供电 | 缺肥代表2217.230秒退出；先供电P1完整2948.098秒 | 只证明这些固定支付顺序无收益，不否定所有早并行 | [20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py) |
| 终点保留Mazes3、较早扩田或16机 | M3完整2877.175秒；历史16机包3081.834秒 | 少投资增加导航/重建，早买机增加Gold/Weird并挤掉供能 | [20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py) |
| 每单清场、整田批量备料 | 普通完整3504.220秒 | 丢掉未熟作物与自然伴生，已由保场订单替代 | [20261111_rejected_ground_bulk_basic.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_ground_bulk_basic.py) |
| 全科技向日葵批水/目标退出直接迁入 | 往返组合2752.542/2756.377秒，对当时采用2744.219秒 | 水库存竞争、低科技成本及完整时序不同；功能收益不能直接套整轮 | [20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py) |
| 统一四条250节 | seed1完整2511.468秒，对同前缀2501.429秒 | 每步计数开销抵消少吃果；只计末条缺口的235节版本才被采用 | [20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py) |
| 提早在水电前混采Weird | seed1完整2610.187秒，比同阶段父慢109.022秒 | 联产木头有用，但到货时点与当时速率不合适 | [20261112_rejected_followup_lb_fastest_reset-mixed-early.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-mixed-early.py) |
| 已有肥料催回访南瓜、购买F3催熟 | 三seed2522.040秒对2514.803秒；F3首seed2511.712秒慢10.546秒 | 催熟/感染/费用没有完整回本，只关闭所测政策 | [20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py) |
| 仙人掌窗口复用＋单调边界/仅缓存 | seed1完整2472.427480/2465.679293秒，对2464.635501秒 | measure少约43%仍未改善整轮，成熟与后续时序反馈须实测 | [20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py) |
| 单机太阳花仅改最短环绕 | 三seed完整均2476.690677629秒，对2479.105835994秒，省2.415秒 | 单项有效，现已被增加有限低瓣补种的2471.034秒组合替代 | 从`5f34716`的`solar_reserve`将原正向East/North到点循环替换为`go(x,y)`即可重建；原报告`.codex/gemini-reset-maze-20261115/reset-solar-shortest-seed*.json`（原始材料已于 2026-11-17 清理） |
| 同瓣最近邻贪心选点 | 三seed完整均2480.776315973秒，比共同父版慢1.670秒 | 单seed领先不足代表整轮平均收益；本实现不采用 | 在上行版本中，每瓣反复按环绕曼哈顿距离选最近点、`pop(best)`后`go`；原源`solar-nearest/lb_fastest_reset.py`与报告留同一`.codex`目录 |

2026-11-15这批比较均为原版重置初始条件和目标，每例15墙钟秒、最多两进程；原版Parser、正常终态、实际目标、依赖与程序集/资源指纹逐项核对。最终源仅剩主机，报告索引`.codex/gemini-reset-maze-20261115/results.json`（原始材料已于 2026-11-17 清理）。ty与冻结父版同为14处既有类型错误及15条提示，新增代码无诊断；没有将LSP写成零错。

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
| 2026-11-16 | 改前7200秒会话4轮均2484.598921秒，非新实机 | 冻结8机/P1/C2/D4正式源，供本轮同条件比较 | [本轮改前正式源](../../references/leaderboard_history/lb_fastest_reset/20261116_v30_sim_41m24.599s_3973de2.py) |

## 下一步优化方向

- 继续逐格复现视频开局，重点是3×3之前的草／灌木切换、Grass2筹资期间的真实巡回和成熟回访。当前短回访4秒是本轮有限代表，并非已还原作者源码的等待条件；不能只再调升级顺序。首seedSunflowers仍在603.65秒，视频为477.89秒，差距尚未解释完。
- 供电、伴生3、16机/P6/C3/D5已采用，不再写成未试。继续按实际新费率比较伴生4/5、基础产量和购买时点；一次P3缩减等级负例不能关闭高伴生方向。
- 终点Wood161880、Cactus201560仍需按少采与提前投资两路计价，区分混采副产物和整田零头。末段仅按需补电已验证，但清零不是独立目标。
- 当前均值距#1+52.4%，先查前期生产与组合投资；正式成绩需要新的完整游戏统计，本轮没有启动实机。地下榜只共享已验证的开局，终点仍按竹子／炸药另算。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
