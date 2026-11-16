# 蘑菇·多机（`lb_mushrooms`）

## 当前策略与成绩

当前脚本：[lb_mushrooms.py](../../scripts/leaderboard/lb_mushrooms.py)。公开账号最高 **5:14.194（#8）**；当前本地模拟 **4:37.057（7200游戏秒场均会话26轮，标准误1.53秒，seed1-26，全部达标）**，距当前 #1 **1:34.538（+193.1%）**、#3 **2:18.040（+100.7%）**、#10 **7:15.755（-36.4%）**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444618/)，榜单抓取时间 `2026-11-16T02:16:07.500286+00:00`，账号查询时间 `2026-11-16T02:16:07.500314+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

公开柱顶测厚，仅在六层场工作；选场与废弃成本全部计时。每区工人只派发一次，先蛇行揭开本区覆盖土，再连续处理各层，不再等待全图揭盖后重派。固定路线及邻格表只建立一次，匹配动作返回当前格后，下一格直接走一步；每层仍重新读取实际柱顶、维护原颜色缓存，不以旧高度推断塌方后的状态。原直接推／三推／双邻喂料、ceiling−2共同floor和240k目标均保留。一次成功dig后实际可能因塌方下降多格，校验改为至少下降一格，避免把合法塌方误判成失败换场。全部回收后才能clear。

2026-11-16 改用公开榜同口径的7200游戏秒场均会话（`simulator/headless/session.py`）后，本版26轮均分277.057秒、标准误1.53秒；上一版同口径26轮均分287.620秒、标准误1.47秒，逐轮配对后本版每轮快8.9～12.4秒，均值改善**3.7%**，超出2倍标准误。改动只动解释器与读取：把 `work_layer` 已读到的柱顶与颜色直接传给 `carry_match`／`feed_column`／`push_match`，缓存只在本次真的变动过时刷新，配对搜索先挑候选再配对。同seed1-3对照：原版282.0/284.6/285.5秒、仅首轮复用282.1/284.6/286.5秒（无效）、仅条件刷新279.5/281.7/281.6秒、全部采用270.3/274.6/271.9秒。

2026-11-16同初始条件seed0/1/123各结算四个完整场次：原版141.86056878/143.63160777/143.39950767秒，收益116176/115952/115552；最终版131.57293761/132.24816783/133.19681526秒，收益116160/115952/115520，净速率提高7.80%/8.61%/7.63%，轻微产量损失已扣除。每例以 `240000 × 含选场初始化的实际时间 / 已结算净产量` 外推271.844912417/273.730166614/276.724685443秒，均274.099921491秒；不是240k完整轮成绩。原版Parser通过，六例都正常返回且仅余主机。

实际生产源另跑原240k目标：seed123完整286.53465168秒；seed0在15墙钟秒到限时已达目标但尚未正常收口，seed1到限时状态及效率无效，这两例不当作完整成绩，也不用于外推。每例预算固定15墙钟秒、最多同时两例，未放宽。原始报告、冻结源、重建器和指纹见 `.codex/five-structures-20261115/`；旧三seed九场外推299.947553105秒、较早完整320.579401620秒及request476正式23轮314.194217391秒均保留为历史。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 相邻双柱连续同色配对 | 8个完整场次29152/112.04秒，约260 Mushroom/s | 材料利用率远低于约16000/片预算，少移动未回本 | [20261111_rejected_s_pairs.py](../../references/leaderboard_history/lb_mushrooms/20261111_rejected_s_pairs.py) |
| 每机固定列、棋盘源/接收异步供料 | 前者16片12992/116.839秒；后者11片34192/119.294秒 | 快速挖掉尚可配对块，失配损失超过省下的搬运 | [20261109_rejected_mushroom_checkerboard_supply_v1.py](../../references/leaderboard_history/lb_mushrooms/20261109_rejected_mushroom_checkerboard_supply_v1.py) |
| 三格高度带与空接收组合 | 137.483秒仅70816/240000并报layer失败 | 跨层、分区和塌方的组合不满足共同高度不变量 | [20261106_rejected_band3.py](../../references/leaderboard_history/lb_mushrooms/20261106_rejected_band3.py) |
| 分区层间平移 | 补环绕保护后首seed579.165秒，对576.859秒 | 配对收益未增而解释器费用上升；无保护首版曾失败 | [20261106_rejected_shifted_partitions_wrap_guard.py](../../references/leaderboard_history/lb_mushrooms/20261106_rejected_shifted_partitions_wrap_guard.py) |
| 十字Rock自动揭盖 | 多机完整场次外推均315.485秒，对311.497秒 | 少挖也损失Mushroom，窗口较高库存没有稳定保留 | [20261108_rejected_mushroom_cross_cover_v2.py](../../references/leaderboard_history/lb_mushrooms/20261108_rejected_mushroom_cross_cover_v2.py) |
| 8×4转置分区候选 | 三seed完整301.098秒，对同批306.999秒；未采用 | 约1.92%单项收益尚未与当前六层选场作同条件完整组合，不能拼成更好当前值 | [20261110_rejected_blocks_4x8.py](../../references/leaderboard_history/lb_mushrooms/20261110_rejected_blocks_4x8.py) |
| 种子坑/长坑、地图贪心、坑边上坡巡走 | 局部组件分别停滞于22～23对、17对/26秒、7对/40秒 | 前者耗尽局部匹配，后两者地图维护或震荡移动过重；仅所测小区域，不是整榜上限 | [20261113_rejected_probe_grow.py](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_grow.py) |
| 平整层能推就推、精简判定删配对分支 | 8×8组件仅30对/约19秒；130秒多处理末层5582对，对现源6361对 | 降低节点同时损失配对密度，不能只看t/格 | [20261113_rejected_lb_mush_lean3.py](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_lb_mush_lean3.py) |
| 两趟扫描：首趟保留不匹配块、次趟才削峰 | seed1前两完整场62432/100.78秒，对原版58624/68.60秒；合并局部揭盖仍97.15秒 | 每场多产约6.5%，增加的巡视超过收益；未兑现所估40k/场，不采用 | [20261116_rejected_retain_first_pass.py](../../references/leaderboard_history/lb_mushrooms/20261116_rejected_retain_first_pass.py) |
| 仅合并局部揭盖；固定路线仍要求dig恰降一格 | seed1四场136.23秒，对原版143.63秒；加入路线后132.25秒；seed123旧严格高度判断发生drop误报 | 合并揭盖有用，最终同时采用预建路线与允许真实连带塌方；未删实际传感读数 | Git `0102d33` 对照本页最终实现；初筛报告 `lb_mushrooms-cover/route-seed1.json` 及 `lb_mushrooms-paired-route-seed123.json` |

局部对照代码：[平层扫推](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_sweepB.py)、[地图贪心](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_hunt.py)、[坑边巡走](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_walk.py)。这些是局部预算实验，没有完整榜单成绩。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-16 | 277.057秒（7200游戏秒场均会话26轮，标准误1.53秒；尚无本版实机） | 复用已读柱顶／颜色、缓存按需刷新、先挑候选再配对 | 当前 [lb_mushrooms.py](../../scripts/leaderboard/lb_mushrooms.py)，候选与回执留 `.codex/mush-opt/` |
| 2026-11-06 | 572.673秒（构建26462009，13轮官方完整统计；请求348）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_9m32.673s_22bf18ce.py](../../references/leaderboard_history/lb_mushrooms/20261106_v01_9m32.673s_22bf18ce.py) |
| 2026-11-06 | 557.267秒（构建26462009，13轮官方完整统计；请求357）。 | 蘑菇多机利用空接收柱并保留单机基线 | [20261106_v02_9m17.267s_1c3d2fc9.py](../../references/leaderboard_history/lb_mushrooms/20261106_v02_9m17.267s_1c3d2fc9.py) |
| 2026-11-09 | 未取得（当前算法仅完成本地效率验证）。 | 迁入蘑菇配对和迷宫达标收尾并同步存档 | [20261109_v03_45bb4345.py](../../references/leaderboard_history/lb_mushrooms/20261109_v03_45bb4345.py) |
| 2026-11-09 | 5:14.194（2026-11-09，build26462009，官方完整23轮，request476）。 | 补齐蘑菇失败恢复并记录十二榜实机成绩 | [20261109_v04_5m14.194s_bb379e4b.py](../../references/leaderboard_history/lb_mushrooms/20261109_v04_5m14.194s_bb379e4b.py) |
| 2026-11-15 | 九个完整场外推299.947553105秒；未取得新版完整实机。 | 六层筛选、单次派工、逐层推进；本轮替换前的冻结实现 | [20261115_baseline_0102d33.py](../../references/leaderboard_history/lb_mushrooms/20261115_baseline_0102d33.py) |

## 下一步优化方向

- 当前仍+193.1%，不是已突破两倍线。减少每对真实挖掘／推动／移动和筛场成本仍是主要方向；两趟扫描已实测，无需再靠相同代表调参。
- 59%解释器占比来自旧130秒诊断，不能直接当成本版账单，更不能据此认定删除所有四邻读数都安全。固定路线已落实；数组缓存下一代表须说明push、dig及跨区塌方后哪些格失效，再比较同完整场净速率。
- 人工放Mushroom、彩块push、榜内Jump均不成立。新跨层结构保留失配块须同时减少巡视；不能只以单场产量提高判断收益。
- 2026-11-16 `--hot-spots`：多机版总tick／游戏秒≈1.67e5，属动作受限；240k目标＝15,000对，满级合并奖励16。每对下限是1次push(200t)加到位移动，先按这条线算当前每对的实际tick，再决定减哪一段。
- 同日按整轮账单分配：seed1完整轮 move 18.90M、dig 8.84M、push 4.52M、解释器40.3M tick。把已读柱顶与颜色下传、缓存按需刷新、先挑候选再配对之后，解释器降到34.5M，整轮快4.1%；`--hot-spots` 164k tick／游戏秒里解释器已占25%。下一步的两块仍是解释器（`feed_column`／`carry_match` 的整列重扫）与 move（蛇行遍历本身约9.2万次移动，占move的绝大部分，push往返只占少部分）。
- 同日实测否定“一站多推”：站在同色较高邻柱上连续直推，seed1-3只有269.6→267.6k tick的移动减少、整轮反而282.0→285.8秒；说明每对之间很少能在同一邻柱连推两次，往返移动不是主成本，不再沿这条线调参。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
