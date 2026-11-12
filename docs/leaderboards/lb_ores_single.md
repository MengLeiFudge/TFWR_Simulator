# 石英矿·单机（`lb_ores_single`）

## 当前策略与成绩

当前脚本：[lb_ores_single.py](../../scripts/leaderboard/lb_ores_single.py)。公开账号最高 **8:54.068（#4）**；已有最好本地模拟 **9:32.569**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444637/)，榜单抓取时间 `2026-11-11T09:13:18.823086+00:00`，账号查询时间 `2026-11-11T09:13:18.823110+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

实采Coal，用煤方向探Iron，再用Iron支付Quartz距离。三个相邻锚点全部挖好后重读距离：第一点给球面，其余最近距离只排除球内候选，不能假定同一矿。按残差选下一钻孔、实际挖掘验证，失败有限回退沟网；目标4000 Quartz。

三seed完整538.47601803/626.64278013/552.58819794秒，均572.56899870秒；候选request423正式534.068秒，真源request436正式14轮548.380785714秒。公开账号最高534.068秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 强求三个最近距离球相交同一矿 | 首seed723.429秒 | 各次最近矿可能不同，频繁误定位/回退 | [20261107_rejected_prospect_funded.py](../../references/leaderboard_history/lb_ores_single/20261107_rejected_prospect_funded.py) |
| 全覆盖沟网 | 三seed694.006/745.302/683.232秒 | 单机全覆盖的开挖与移动多于付费信息收益 | [20261107_rejected_trench_sweep.py](../../references/leaderboard_history/lb_ores_single/20261107_rejected_trench_sweep.py) |
| 全田逐层剥离 | 7200秒仅3432/4000 Quartz | 大量无矿开挖及塌方损失，未完成目标 | [旧版合集](../../references/leaderboard_history/lb_ores_single/)（多方向见版本表） |
| 四口井 | 正式1069.625秒，初版1279.818秒 | 准备虽可摊销，仍没有消除无矿井搜索 | [旧版合集](../../references/leaderboard_history/lb_ores_single/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1279.818秒（构建26462009，6轮官方完整统计；请求347）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_21m19.818s_effd70d1.py](../../references/leaderboard_history/lb_ores_single/20261106_v01_21m19.818s_effd70d1.py) |
| 2026-11-06 | 1069.625秒（构建26462009，7轮官方完整统计；请求376）。 | 矿石单双机四井采样复用同片准备 | [20261106_v02_17m49.625s_7acb6913.py](../../references/leaderboard_history/lb_ores_single/20261106_v02_17m49.625s_7acb6913.py) |

## 下一步优化方向

- 压缩锚点准备并提高候选排除的信息量；每次开挖后重读实际高度/距离，保留有界错误回退。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
