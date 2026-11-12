# 蘑菇·多机（`lb_mushrooms`）

## 当前策略与成绩

当前脚本：[lb_mushrooms.py](../../scripts/leaderboard/lb_mushrooms.py)。公开账号最高 **5:14.194（#6）**；已有最好本地模拟 **4:59.948**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444618/)，榜单抓取时间 `2026-11-11T09:13:19.156940+00:00`，账号查询时间 `2026-11-11T09:13:19.156964+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

先以公开柱顶测厚，只在六层场揭开全田；选场与废弃成本计时。每区工人只派发一次，连续处理各层，缓存已公开顶面，用直接推、同层三推和双邻喂料配对；共同floor为ceiling−2。全部回收后换田，分区失败保留已有实际收益并重生，目标240k Mushroom。

三seed九个完整场次外推299.947553105秒，原240k未在该窗口跑完，seed3略慢；旧常驻版request476正式23轮314.194217391秒。较早完整目标三seed均320.579401620秒。

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

局部对照代码：[平层扫推](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_sweepB.py)、[地图贪心](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_hunt.py)、[坑边巡走](../../references/leaderboard_history/lb_mushrooms/20261113_rejected_probe_walk.py)。这些是局部预算实验，没有完整榜单成绩。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 572.673秒（构建26462009，13轮官方完整统计；请求348）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_9m32.673s_22bf18ce.py](../../references/leaderboard_history/lb_mushrooms/20261106_v01_9m32.673s_22bf18ce.py) |
| 2026-11-06 | 557.267秒（构建26462009，13轮官方完整统计；请求357）。 | 蘑菇多机利用空接收柱并保留单机基线 | [20261106_v02_9m17.267s_1c3d2fc9.py](../../references/leaderboard_history/lb_mushrooms/20261106_v02_9m17.267s_1c3d2fc9.py) |
| 2026-11-09 | 未取得（当前算法仅完成本地效率验证）。 | 迁入蘑菇配对和迷宫达标收尾并同步存档 | [20261109_v03_45bb4345.py](../../references/leaderboard_history/lb_mushrooms/20261109_v03_45bb4345.py) |
| 2026-11-09 | 5:14.194（2026-11-09，build26462009，官方完整23轮，request476）。 | 补齐蘑菇失败恢复并记录十二榜实机成绩 | [20261109_v04_5m14.194s_bb379e4b.py](../../references/leaderboard_history/lb_mushrooms/20261109_v04_5m14.194s_bb379e4b.py) |

## 下一步优化方向

- 现源130秒诊断每对约4900～5100t，解释器占约59%；比较保留直接推/三推/双邻喂料的判定压缩，先在同8×8区域验证t/对下降且配对密度不低于0.35/格。该方向置信度中低，不能从节点数单独外推整轮。
- 跨层新结构须保留失配块并降低每对move/dig；人工放Mushroom、彩块push、榜内Jump均不成立。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
