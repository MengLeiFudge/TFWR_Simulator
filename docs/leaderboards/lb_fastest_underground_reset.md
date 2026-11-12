# 地下重置（`lb_fastest_underground_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_underground_reset.py](../../scripts/leaderboard/lb_fastest_underground_reset.py)。公开账号最高 **54:39.570（#5）**；已有最好本地模拟 **50:26.822**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444633/)，榜单抓取时间 `2026-11-12T15:58:46.356414+00:00`，账号查询时间 `2026-11-12T15:58:46.356442+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

从原版1×1零库存发展到供电、伴生与4机，再按真实get_cost支付矿业链。跨订单保场供料，Iron4、Quartz3、Ore_Boost1、Mining8、Dynamite4、Bamboo4；煤方向追铁，石英用付费最近距离选孔并追可见邻矿。蘑菇分区工人常驻、扫雷邻接和几何并行初始化，数字/约束每盘重建；最终12格田筹200k Bamboo及20k Dynamite并实付解锁。

采用源八seed完整均3034.092696秒；主表更快有效候选“小宫＋80层＋32次扑空容错”八seed均3026.821846秒，有明显seed回退而未采用。当前采用源未实机；历史request497正式三轮3279.570秒。

最终Underground_Leaderboard只收20000 Dynamite＋200000 Bamboo。正常链Dynamite1需80 Mushroom＋4000 Gold并要求Expand4；Mushrooms1需60 Quartz＋100 Pumpkin；Quartz1需50 Iron。Mining7的90 Quartz、Mining8的250 Mushroom以及Dynamite2/3/4、矿物增产属于可选投资。路线必须从最终需求倒推，不能将普通Reset的金币/骨头目标当作地下前置。

当前找扫雷层上限208，仅适用于本路线Quartz已解锁、chunk循环长7、白名单[3,5]：候选块3/5/10/12对应48～63、80～95、160～175、192～207层，208～255无候选。仍保留连续8次扑空退出；最终解锁前供电目标降500，前段保持1000。共同八seed均从3061.424417降至3034.092696秒，8/8更快，末Power17.431～60.590。

Block8633～11928多来自矿采/蘑菇/扫雷联产，末Rice约4150及Pumpkin1436是种子预留与整田零头；删除生产要扣掉其副产物。Special_Soils实际只加成种在对应地块上的作物：Loam对Carrot/Sunflower、Perlite对Bamboo/Tree/Bush/Cactus各2倍，不是全局增产。挖到特殊土、整地、成熟、塌方和回程都计价；Jump榜内禁用，爆破钻需12M Dynamite远超终点20k，直接排除该投资。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
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

## 下一步优化方向

- 优先压缩地上启动与矿物投资链。按资源到货时点、速率和主依赖比较保场混合获取与阶段重叠，clear前必须回收所有写者。
- 保留3026.821846秒完整八seed候选和其波动；原cap80版seed7失败，与加容错版本区分，旧前三seed2938.444秒不再充作当前均值。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
