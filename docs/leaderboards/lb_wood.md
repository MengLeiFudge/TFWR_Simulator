# 木头·多机（`lb_wood`）

## 当前策略与成绩

当前脚本：[lb_wood.py](../../scripts/leaderboard/lb_wood.py)。公开账号最高 **4:37.434（#38）**；已有最好本地模拟 **4:37.998**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869895/)，榜单抓取时间 `2026-11-10T06:15:47.926199+00:00`，账号查询时间 `2026-11-10T06:15:47.926228+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32机各巡4×8棋盘树区，非树格按动态伴生请求种Grass/Bush/Carrot。沿用上游跨区请求规则，本机字典不共享；跨区支撑实际失配时按真实低倍率收获计产。Carrot先核种子资金，不足走Bush退路；水位0.35、用水库存余量和全部句柄回收保留。来源enihsyou，MIT。

修正静态函数返回计费后的seed1完整277.998141690秒；2026-11-03 request261正式26轮均277.434038462秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 把动态请求严格限制在本区 | seed1完整308.66696001秒 | 高倍兑现更多但重抽、未熟移除和管理的总费用更高 | [20261028_rejected_github_multi_dynamic.py](../../references/leaderboard_history/lb_wood/20261028_rejected_github_multi_dynamic.py) |
| 固定棋盘永久支撑与四分之一树布局 | 2048株组件41.090936秒；含启动条件外推362.986578秒 | 接受率、成熟空访及支撑准备不能支持预算 | [20261024_rejected_quarter_component.py](../../references/leaderboard_history/lb_wood/20261024_rejected_quarter_component.py) |
| 32机冻结支撑批次 | 正式283.894731秒 | 全伴生正确性成立，但冻结/排队费用由当前巡田请求结构降低 | [旧版合集](../../references/leaderboard_history/lb_wood/)（多方向见版本表） |
| 保留Soil的旧动态支撑 | 三seed388.641082秒，对旧403.344651秒有收益 | 省翻地仍保留大量支撑往返与低倍率，已被后续结构替代 | [20261024_rejected_soil_preserve.py](../../references/leaderboard_history/lb_wood/20261024_rejected_soil_preserve.py) |
| 保护Bush、支撑补水、Tree-slot接力与helper | 历史support-lock约433.784秒；多个代理预算未回本 | 减少改写会损失覆盖率；树位改写/恢复及等待需要实际费用，支撑本身无需成熟 | [旧版合集](../../references/leaderboard_history/lb_wood/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_wood/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_wood/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 提升木头榜伴生路线 | [20260424_v03_ebfb10f3.py](../../references/leaderboard_history/lb_wood/20260424_v03_ebfb10f3.py) |
| 2026-04-25 | 未记录 | 迁入木头榜外部候选 | [20260425_v04_7ae1014e.py](../../references/leaderboard_history/lb_wood/20260425_v04_7ae1014e.py) |
| 2026-05-31 | 版本注记 10m22.851s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_10m22.851s_0224fb21.py](../../references/leaderboard_history/lb_wood/20260531_v05_10m22.851s_0224fb21.py) |
| 2026-06-08 | 版本注记 7m36.580s | 刷新木头榜 Grass support 接力策略 | [20260608_v06_7m36.580s_9f8142fa.py](../../references/leaderboard_history/lb_wood/20260608_v06_7m36.580s_9f8142fa.py) |
| 2026-06-08 | 版本注记 7m06.871s | 刷新木头榜 Grass Carrot support 策略 | [20260608_v07_7m06.871s_3b31b4e7.py](../../references/leaderboard_history/lb_wood/20260608_v07_7m06.871s_3b31b4e7.py) |
| 2026-06-08 | 版本注记 6m40.073s | 刷新木头榜未成熟 Bush 改写策略 | [20260608_v08_6m40.073s_4d4057a1.py](../../references/leaderboard_history/lb_wood/20260608_v08_6m40.073s_4d4057a1.py) |
| 2026-06-09 | 版本注记 6m40.073s | 减少木头目标检查频率 | [20260609_v09_6m40.073s_fcd6b90d.py](../../references/leaderboard_history/lb_wood/20260609_v09_6m40.073s_fcd6b90d.py) |
| 2026-06-09 | 版本注记 6m40.073s | 移除多机木头统计计数 | [20260609_v10_6m40.073s_ec6beb18.py](../../references/leaderboard_history/lb_wood/20260609_v10_6m40.073s_ec6beb18.py) |
| 2026-06-09 | 版本注记 6m40.073s | 缓存木头榜胡萝卜种植成本 | [20260609_v11_6m40.073s_76713914.py](../../references/leaderboard_history/lb_wood/20260609_v11_6m40.073s_76713914.py) |
| 2026-06-09 | 版本注记 6m40.073s | 减少木头榜地块复核读取 | [20260609_v12_6m40.073s_e87552f6.py](../../references/leaderboard_history/lb_wood/20260609_v12_6m40.073s_e87552f6.py) |
| 2026-10-27 | 4:43.895（2026-10-26，官方完整26轮，request 113）。 | 多机木头以独占支撑批次缩短至4分43秒 | [20261027_v13_4m43.895s_2cd0d665.py](../../references/leaderboard_history/lb_wood/20261027_v13_4m43.895s_2cd0d665.py) |

## 下一步优化方向

- 在不增加相邻树惩罚的前提下联合比较生产密度、请求归属和低成本支撑；核算实际倍率与种子净消耗。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
