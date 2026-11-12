# 迷宫·单机（`lb_maze_single`）

## 当前策略与成绩

当前脚本：[lb_maze_single.py](../../scripts/leaderboard/lb_maze_single.py)。公开账号最高 **2:06.355（#25）**；已有最好本地模拟 **2:08.237**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827402/)，榜单抓取时间 `2026-11-10T06:15:45.780308+00:00`，账号查询时间 `2026-11-10T06:15:45.780340+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8单宫单机，DFS取得真实树图，对称构建首步与距离表；每次出发探墙，发现新边只传播严格改善的路径。完整执行300次正常迁移和最后一次收割，目标616448 Gold。来源与多机相同，zzlg-git未附许可，仅限本地研究。

seed1完整128.237280570秒；2026-11-03 request258正式57轮均126.355421053秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| DFS父指针替代图最短路 | 历史短筛277.846秒，对当时双向BFS184.233秒 | 省计算却走更长树路径，忽略后续开墙收益 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| 旧完整next-hop逐目标建表 | 历史短筛262.971秒，其中建表约14.14秒 | 旧构造过重；不等同于当前对称增量表 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| 按target懒缓存旧路径树 | 历史短筛226.522秒 | 动态图出现新路，旧树长尾抵消重复目标收益；按年龄重建也未过预算 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| A*或直线贪心 | 历史A*303.261秒，DFS+直线贪心195.393秒 | 大量管理或绕路不如图最短路 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| 沿途重复探墙 | 独立对照记录见归档 | 需要用实际move与更新成本比较，不能把少查询直接当完整收益 | [20261028_rejected_path_scan_path_scan.py](../../references/leaderboard_history/lb_maze_single/20261028_rejected_path_scan_path_scan.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_maze_single/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_maze_single/20260422_v02_aa7209f3.py) |
| 2026-04-25 | 未记录 | 迁入单机迷宫外部候选 | [20260425_v03_61737dfd.py](../../references/leaderboard_history/lb_maze_single/20260425_v03_61737dfd.py) |
| 2026-04-26 | 未记录 | 优化单迷宫 DFS BFS 寻路 | [20260426_v04_f39a443c.py](../../references/leaderboard_history/lb_maze_single/20260426_v04_f39a443c.py) |
| 2026-04-26 | 未记录 | 复用单机迷宫寻路缓冲 | [20260426_v05_c9a03253.py](../../references/leaderboard_history/lb_maze_single/20260426_v05_c9a03253.py) |
| 2026-04-26 | 未记录 | 改进单机迷宫双向寻路 | [20260426_v06_e4daa3e8.py](../../references/leaderboard_history/lb_maze_single/20260426_v06_e4daa3e8.py) |
| 2026-05-31 | 版本注记 2m43.788s | 调整：收敛 leaderboard 脚本真源 | [20260531_v07_2m43.788s_0224fb21.py](../../references/leaderboard_history/lb_maze_single/20260531_v07_2m43.788s_0224fb21.py) |
| 2026-06-09 | 版本注记 2m43.788s | 减少单机迷宫路径检查 | [20260609_v08_2m43.788s_087d0ad9.py](../../references/leaderboard_history/lb_maze_single/20260609_v08_2m43.788s_087d0ad9.py) |
| 2026-06-09 | 版本注记 2m43.788s | 移除单机迷宫诊断计数 | [20260609_v09_2m43.788s_df88665c.py](../../references/leaderboard_history/lb_maze_single/20260609_v09_2m43.788s_df88665c.py) |
| 2026-10-27 | 2:25.112（2026-10-26，官方完整50轮，request 84）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v10_2m25.112s_9d2d3c31.py](../../references/leaderboard_history/lb_maze_single/20261027_v10_2m25.112s_9d2d3c31.py) |

## 下一步优化方向

- 在当前动态图上比较更便宜的新边传播与首次探索回退，保持真实最短路和唯一正常结算。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
