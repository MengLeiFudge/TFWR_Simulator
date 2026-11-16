# 地下重置（`lb_fastest_underground_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_underground_reset.py](../../scripts/leaderboard/lb_fastest_underground_reset.py)。公开账号最高 **51:58.780（#5）**，来自2026-11-16 request550的3轮官方完整统计；本轮采用视频前期种植和移动的新开局，尚未实机。本地7200秒会话均值 **45:24.105**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444633/)，2026-11-16T16:08:20.188468+00:00刷新，账号核对16:08:20.188505+00:00。#1为21:25.151，本地均值距#1 **+112.0%**，仍需继续研究。其余名次及来源见[进度总表](leaderboard_progress.md)和[公开快照](../../references/leaderboards/status_snapshot.md)。

`ur_s_step1`复现3×3固定草／灌木／胡萝卜混种与两格草短回访，6×6按胡萝卜等级切换作物配比，先供电再推进伴生和四机；相关画面与未还原的条件见[普通重置的逐格复现](lb_fastest_reset.md#开局种植与移动的复现)。地下保留自己的4机终盘和真实矿物科技链，没有迁入普通榜的恐龙、P3或16机投资。煤追铁、付费勘探石英、Mining8/Dynamite4/Bamboo4，最终12格田真实筹200000 Bamboo＋20000 Dynamite并支付解锁。

2026-11-16同用原版零库存地下重置目标、seed1..3、每批60墙钟秒和最多3进程，两版累计均超过7200游戏秒：

| 版本 | 完整轮数／累计游戏秒 | 均值／标准差／标准误（秒） | 逐轮游戏秒 |
| --- | --- | --- | --- |
| 改前固定前缀 | 3／8974.822485 | 2991.607495／14.750000／8.515917 | 2977.840089、2984.919622、3012.062773 |
| 当前视频混种与路径 | 3／8172.315941 | 2724.105314／89.800648／51.846428 | 2812.473612、2600.930548、2758.911782 |

3/3达成原目标、逐轮更快，平均省267.502181秒（8.9%）；均值不与旧八seed3026.821846秒候选混比。首seed正式路径另跑逐纳秒复现2812.473612011秒，正常解锁、只剩主机。原会话`session-under-{baseline,final}.json`、正式源单轮及全部指纹索引在`.codex/reset-global-20261116/results.json`。本地seed不是正式榜加密随机轨迹，尚无新实机成绩；既有找蘑菇层8次扑空退出仍存在，不能将三个seed通过写成已解决request542的失败机制。

首seedSunflowers解锁602.54秒，双机996.95、四机并进入地下链1138.05秒（改前1483.03）。终点仍只收竹子／炸药，Mining7的90 Quartz、Mining8的250 Mushroom和各增产等级均属投资。扫雷查层上限208来自Quartz已解锁后的7块循环白名单[3,5]，维持8次扑空退出；最终付款前补电目标500，其余链为1000。首seed末Power321.743、Block10449、Rice4187、Quartz344和Dynamite2588，副产物、种子与整盘余量没有最小化，不用末库存倒算前期缺口。

Special_Soils只加成种在对应地块上的作物：Loam对Carrot/Sunflower、Perlite对Bamboo/Tree/Bush/Cactus各2倍，须计挖土、整地和回程。Jump榜内禁用，爆破钻需12M Dynamite远超终点20k，仍排除该投资。历史request542首轮找层失败整场作废，request550完整均值3118.780秒才是已上传记录。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 只加胡萝卜一田预备与提前供电 | 7200秒会话3轮均3057.933735秒，对同批2991.607495秒 | 首seed四机前缀1424.16秒虽比1483.03早，整轮反慢66.326秒；不采用，不能否定视频固定布局与路径 | [前缀候选](../../references/leaderboard_history/lb_fastest_underground_reset/20261116_rejected_carrot_forecast_prefix.py) |
| 轻量Mining6/D3/B3或M7/D3/B4 | 完整3941.048～4334.263秒及4002.216秒 | 少科技费没有抵消慢矿采、蘑菇与更多扫雷盘 | [20261111_rejected_sim_72m14.263s_package_m6_d3_b3_funded.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_72m14.263s_package_m6_d3_b3_funded.py) |
| Mining7/D4/B4及中档矿物等级 | 合并供料三seed3309.435秒；Iron4/Quartz2首seed3249.595秒 | 少90石英或低一级增产的整条成本仍高于当时3182.025秒 | [20261111_rejected_sim_54m09.595s_balanced_ore_i4_q2.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_54m09.595s_balanced_ore_i4_q2.py) |
| 单机早下地、藏宝图筹Gold后买机 | 首双机2068.51秒，完整4783.336秒；旧早下地7000秒未完成 | 较短地上前缀被串行矿采和筹Gold回吐，只关闭所测组合 | [20261111_rejected_sim_79m43.336s_minimal_treasure_light_ore_complete.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_79m43.336s_minimal_treasure_light_ore_complete.py) |
| 无电感染先四机/不买伴生 | 完整3644.515/3750.546秒 | 缺电且推迟提速/增产，四机1619.88秒仍晚，不能否定有电早并行 | [20261111_rejected_infected_lean.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_infected_lean.py) |
| 独占列并行采铁、额外备煤 | 采铁代表3503.526秒；备煤共同八seed均3136.516秒 | 阶段备煤虽省约27.5秒，地形/供料及后续费用回吐 | [20261111_rejected_parallel_iron.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_parallel_iron.py) |
| 所有筹金小宫、蘑菇查层48/80 | 中期小宫三seed3024.479秒对3006.673秒；查层八seed3142.196/3075.309秒 | 单项均未改善；部分组合有失败seed，不能删坏样本报均值 | [20261112_rejected_followup_under-seg80.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_under-seg80.py) |
| Rice6/Bamboo5及米预留减半 | 八seed3072.353/3147.393秒；米减半组seed8找层失败 | 升级未回本、减少种子储备后完整组合未通过，保留联产时点账 | [20261112_rejected_followup_rice6-late.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_rice6-late.py) |
| 全程减供电/末段仅300 | 前者途中断电，后者又补一整批 | 需区分前期工作量和末段余额；末段500才有同条件完整收益 | [20261112_rejected_followup_power-late300.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_power-late300.py) |
| 常规蘑菇按片路线复用迁入 | 八seed3052.779018秒，对3034.092696秒，仅3/8更快 | 全科技局部收益不等于低科技整轮收益；只缓存或其他派发仍开放 | [20261112_rejected_followup_mushroom-route.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_mushroom-route.py) |
| 竹子完整功能版迁入 | 末段20万组件三seed87.543秒，对现源63.877秒 | 500M重派收益不在该目标触发，筛种和升降增加成本 | [20261112_rejected_followup_bamboo-retained-stumps.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_bamboo-retained-stumps.py) |
| 早Special_Soils、Treasure_Map3、Petrified_Pumpkins4 | 历史晚土组合六seed10172.228秒，其他代表更慢 | 局部2倍增产不足以抵偿整链投资/访问，历史结果不能套到当前路线 | [归档入口](../../references/leaderboard_history/lb_fastest_underground_reset/)（原记录未标独立源） |
| 稻米同田连续找Clay、三趟种收 | 2026-11-15共同seed1/2/3完整均3028.405526312秒，对父版2991.607494878秒，慢36.798秒 | 普通地层的深挖、成熟、塌方和供料全部计入；专用稻米榜的收益不能直接迁移，关闭这一实现 | [深挖模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_deep_rice.py)，原报告`under-rice-seed*.json` |
| 竹子每机单井闭环、首花及次花全筛 | 早期200目标seed1耗尽Rice、Bamboo0；仅末段启用仍在126605/200000时耗尽Rice | 旧6112米储备不能支付140株完整花节筛选；禁止补虚拟种子或将提前退出当完成 | [全筛模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_closed_bamboo_full.py)，原报告`under-bamboo[-late]-seed1.json` |
| 竹子闭环仅筛首花、保留竹桩 | 共同三seed完整均3045.906270510秒，对2991.607494878秒，慢54.299秒 | 能完成目标；省去二次筛选后整轮仍无改善，不替换现源 | [首花模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_closed_bamboo_first.py)，原报告`under-bamboo-first-seed*.json` |
| 后期供电复用四机分瓣生产、达标免收余档 | 共同三seed完整均3028.261093838秒，对2991.607494878秒，慢36.654秒 | 补电局部缩短但整轮未改善；真实Carrot、水、成熟及后续生产均计入，未实现统一时钟 | 从`5f34716`重建：`ur_s_parallel_solar_reserve(size,target=0)`每瓣前检查目标；`ur_power_stock`保留实际筹种和clear，后接该调用，替代原串行种收；原源`under-power/lb_fastest_underground_reset.py` |

本批原源、完整报告和指纹索引留`.codex/gemini-reset-maze-20261115/results.json`。稻米和竹子模块重建时分别复制为`deep_rice.py`、`closed_bamboo.py`，取`5f34716`入口，在末尾main之前静态导入`reset_rice_stock`或`reset_bamboo_stock`，以同名`ur_rice_stock`或`ur_bamboo_stock`返回其结果。末段竹子代表将原`ur_bamboo_stock`改名`ur_bamboo_stock_original`，新入口对goal<10000沿用原版，其余调用模块；`ur_need`的实际稻米预算保持不变。归档及原路径/SHA256映射见[manifest](../../references/leaderboard_history/manifest.json)。

2026-11-15这批完整比较均为原版零库存重置场景、同一seed、原目标，每例15墙钟秒，最多两进程；三个新整轮代表均正常完成、目标达成、状态完整、效率有效并回收全部工人。因初筛均值已退步，没有选择性扩seed或与旧八seed均值混比，也没有撤回八seed3026.821846秒的有效旧候选。这里只关闭已测的低科技组合，不否定同田、闭环或并行供电的全部构造。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 31535.109秒（构建26462009，1轮官方完整统计；请求355）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_525m35.109s_87447cee.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v01_525m35.109s_87447cee.py) |
| 2026-11-06 | 29133.641秒（构建26462009，1轮官方完整统计；请求366）。 | 地下重置提前准备补给科技与满级速度 | [20261106_v02_485m33.641s_5200e71b.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v02_485m33.641s_5200e71b.py) |
| 2026-11-06 | 25147.408秒（构建26462009，1轮官方完整统计；请求371）。 | 地下重置支付资源升级Mining8缩短末段挖掘 | [20261106_v03_419m07.408s_05774719.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v03_419m07.408s_05774719.py) |
| 2026-11-06 | 22699.482秒（构建26462009，1轮官方完整统计；请求391）。 | 地下重置提前投资煤铁产量并复用扫雷状态 | [20261106_v04_378m19.482s_34edeb18.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v04_378m19.482s_34edeb18.py) |
| 2026-11-06 | 22108.401秒（构建26462009，1轮官方完整统计；请求394）。 | 地下重置用公开石英距离定位并全额计入勘探成本 | [20261106_v05_368m28.401s_95e81154.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v05_368m28.401s_95e81154.py) |
| 2026-11-07 | 18140.125秒（构建26462009，1轮官方完整统计；请求401）。 | 地下重置通过付费勘探减少采铁开挖 | [20261107_v06_302m20.125s_f9c155a2.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v06_302m20.125s_f9c155a2.py) |
| 2026-11-07 | 16670.354秒（构建26462009，1轮官方完整统计；请求404）。 | 地下重置扫雷按需清理覆盖层 | [20261107_v07_277m50.354s_5167e0ae.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v07_277m50.354s_5167e0ae.py) |
| 2026-11-07 | 15440.645秒（构建26462009，1轮官方完整统计；请求411）。 | 地下重置在大田与Mining5后升级Coal3 | [20261107_v08_257m20.645s_20d5421c.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v08_257m20.645s_20d5421c.py) |
| 2026-11-07 | 15255.250秒（构建26462009，1轮官方完整统计；请求415）。 | 地下重置用前置采矿库存升级Rice5 | [20261107_v09_254m15.250s_9d317937.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v09_254m15.250s_9d317937.py) |
| 2026-11-07 | 13559.391秒（构建26462009，1轮官方完整统计；请求418）。 | 地下重置采完首段煤后重生 | [20261107_v10_225m59.391s_b4d62610.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v10_225m59.391s_b4d62610.py) |
| 2026-11-08 | 11912.122秒（本地原目标三seed均值；当前供能与增量扫雷版本未实机验证）。 | 迁入地下功能与榜单的高效结构并固化模拟证据 | [20261108_v11_198m32.122s_feca66ac.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261108_v11_198m32.122s_feca66ac.py) |
| 2026-11-10 | 11067.625秒（本地原目标三seed均值；Dynamite3后Expand5版本未实机验证）。 | 地下Reset末段提前纳入Expand5 | [20261110_v12_184m27.625s_59c3edc1.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261110_v12_184m27.625s_59c3edc1.py) |
| 2026-11-11 | 54:39.570（2026-11-11官方完整3轮，request497）；C#原目标3seed均值3390.747秒。 | 地下重置打榜压缩至一小时以内 | [20261111_v13_54m39.570s_05212f0a.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_v13_54m39.570s_05212f0a.py) |
| 2026-11-11 | 未取得；C#原目标3seed均值3182.025秒（2026-11-11，当前策略未实机）。 | 调整双重置迷宫筹资与矿物投资路线 | [20261111_v14_53m02.025s_8ec59b43.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_v14_53m02.025s_8ec59b43.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值3067.141秒（2026-11-12，当前策略未实机）。 | 重置榜按原料订单保留伴生产区 | [20261112_v15_51m07.141s_425a5024.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_v15_51m07.141s_425a5024.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值3006.673秒（2026-11-12，当前策略未实机）。 | 迁入重置榜常驻采集与分区复用 | [20261112_v16_50m06.673s_5f25fe9a.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_v16_50m06.673s_5f25fe9a.py) |
| 2026-11-16 | 改前7200秒会话3轮均2991.607495秒，非新实机 | 冻结旧固定前缀，作为视频混种与路径的共同对照 | [本轮改前正式源](../../references/leaderboard_history/lb_fastest_underground_reset/20261116_v17_sim_49m51.607s_3973de2.py) |

## 下一步优化方向

- 当前仍距#1+112.0%，从终点与资源来源重列路线，继续拆视频真实开局路径、混种比例与成熟回访，不将现行4机/伴生前缀当必需条件。已采用的视频开局平均省267.502秒，尚未把10分钟前的布局与等待完全还原。
- 矿物投资与供料仍按新前缀实际速率重新计价，比较更早采矿、并行备料和减少选定科技的完整成本；历史八seed候选及其波动保留为旧条件证据，不充作当前会话均值。
- 新藏宝图坍塌隧道筹金尚未在重置初始科技下完成对照；先计入Mining/Treasure_Map解锁和实际小目标，不能用全科技榜22.6%的组件改善代替整轮收益。共享支撑和统一时钟也仍是待验证的不同构造。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
