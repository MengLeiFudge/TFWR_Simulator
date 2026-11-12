# 藏宝图（`lb_treasure_map`）

## 当前策略与成绩

当前脚本：[lb_treasure_map.py](../../scripts/leaderboard/lb_treasure_map.py)。公开账号最高 **0:38.151（#9）**；已有最好本地模拟 **0:37.948**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21469574/)，榜单抓取时间 `2026-11-11T09:12:53.809850+00:00`，账号查询时间 `2026-11-11T09:12:53.809850+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8格世界逐图重生；先找Basalt取得地图位置，读取公开路径。按三维坐标保留最后出口，沿无环有效通路走到终点，保留每次下降；原路径索引严格递增，激活后不clear、不离开合法通路或破坏未来块。找图、解析与正常奖励全部计入115k Gold目标。

三seed完整34.58439639/42.40435905/36.85601439秒，均37.94825661秒；候选request421正式189轮38.151秒，真源request432正式189轮38.185497354秒。公开账号保留38.151秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 完整执行原路线，只做方向查表 | 三seed289.540321秒；正式274.988秒 | 减少分支只有小收益，没有消除大量合法回环 | [旧版合集](../../references/leaderboard_history/lb_treasure_map/)（多方向见版本表） |
| 同片继续找图、4/6格世界 | 同片三seed42.629秒，4/6格首seed57.566/40.381秒 | 找图与重生摊销不如8格逐图重生 | [20261107_rejected_last_exit_size4.py](../../references/leaderboard_history/lb_treasure_map/20261107_rejected_last_exit_size4.py) |
| 按原字符串长度筛图 | 三seed41.912秒且波动更大 | 原串长度不能代表去环后必要动作和净奖励 | [20261107_rejected_last_exit_select1000.py](../../references/leaderboard_history/lb_treasure_map/20261107_rejected_last_exit_select1000.py) |
| 逐层BFS | 首seed35.123秒，少移动但规划更贵 | 单seed费用不优于当前同seed34.584秒 | [20261107_rejected_layer_bfs_reset8.py](../../references/leaderboard_history/lb_treasure_map/20261107_rejected_layer_bfs_reset8.py) |
| 栈式一次去环 | 后续完整对照未改善 | 解析维护也计费，不能仅因渐近复杂度更低就采用 | [20261110_rejected_stack.py](../../references/leaderboard_history/lb_treasure_map/20261110_rejected_stack.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 277.200秒（构建26462009，26轮官方完整统计；请求354）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_4m37.200s_8b327985.py](../../references/leaderboard_history/lb_treasure_map/20261106_v01_4m37.200s_8b327985.py) |
| 2026-11-06 | 274.988秒（构建26462009，27轮官方完整统计；请求384）。 | 藏宝图逐字符方向查表并完成同种子实机对照 | [20261106_v02_4m34.988s_a76923e8.py](../../references/leaderboard_history/lb_treasure_map/20261106_v02_4m34.988s_a76923e8.py) |

## 下一步优化方向

- 按找图、解析、必要动作与奖励的联合费用选图；先比较一次解析的数据结构，避免重复原串长度筛选。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
