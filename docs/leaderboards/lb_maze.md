# 迷宫·多机（`lb_maze`）

## 当前策略与成绩

当前脚本：[lb_maze.py](../../scripts/leaderboard/lb_maze.py)。公开账号最高 **1:26.965（#10）**；已有最好本地模拟 **1:24.744**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869891/)，榜单抓取时间 `2026-11-10T06:15:46.008648+00:00`，账号查询时间 `2026-11-10T06:15:46.008677+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32机各管一座小迷宫：20座5×5、6座6×6、6座7×7，覆盖1010格。草感染/治愈的64份Weird消费作为到位屏障。每宫DFS建图，对称构建全点对首步/距离，只在出发点探新墙并增量更新；正常迁移300次后收最后一箱，再重建。全局Gold实际达标后由主机结束无收益尾段。上游zzlg-git固定commit e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629未附许可，仅作本地研究使用。

当前达标收尾版seed1完整84.744190980秒，尚无本版完整实机；前版2026-11-03 request257正式83轮86.964698795秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 32×32共宫唯一负责与动态驻点 | 唯一覆盖版正式127.169105秒；并行分枝代表115.858938秒 | 探索、布站、回应与归位的真实链仍慢于独立小宫 | [20261029_rejected_branch_team_team.py](../../references/leaderboard_history/lb_maze/20261029_rejected_branch_team_team.py) |
| 16宫双机持续巡逻/探索兑现分工 | 完整180.071982/198.939086秒 | 双份探索、导航与协调费用高于小宫单一写者 | [20261030_rejected_explorer_collector.py](../../references/leaderboard_history/lb_maze/20261030_rejected_explorer_collector.py) |
| 第二代按需BFS与反向目标缓存 | 完整90.232782/102.031204秒 | 反复重建及维护费用没有抵消全表收益 | [20261028_rejected_lazy_final_generation.py](../../references/leaderboard_history/lb_maze/20261028_rejected_lazy_final_generation.py) |
| 延迟探墙、沿途探墙 | 完整86.832763/89.726442秒，对照85.117033秒 | 少探墙多绕路，或少量省移动却大增规划 | [20261028_rejected_demand_scan.py](../../references/leaderboard_history/lb_maze/20261028_rejected_demand_scan.py) |
| 固定驻点/全局换中心几何 | 免费建图、规划和归位后，固定代表响应+兑现仍约47.74～59.52秒 | 只说明所测站位余量小；旧#10门槛不能证明其他布局不可行 | [20261026_rejected_parallel_stations.py](../../references/leaderboard_history/lb_maze/20261026_rejected_parallel_stations.py) |
| 纯轮询、漏格补图、容量回退串行等待 | 历史请求124/126/127/132分别中止或失败 | 漏节点与尚未派出区域的等待依赖不闭合；后用边界树补图修正 | [20261026_rejected_single_owner_root_overflow.py](../../references/leaderboard_history/lb_maze/20261026_rejected_single_owner_root_overflow.py) |
| 结算窗口重复收同一宝藏 | 不采用 | 违反项目预期玩法；每次正常迁移付200t，最后只收一次 | 机制判定，无候选代码 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 版本注记 21m12.142s | 导入 TFWR_Simulator | [20260418_v01_21m12.142s_5bf0cea6.py](../../references/leaderboard_history/lb_maze/20260418_v01_21m12.142s_5bf0cea6.py) |
| 2026-04-24 | 版本注记 21m12.142s | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_21m12.142s_8deede45.py](../../references/leaderboard_history/lb_maze/20260424_v02_21m12.142s_8deede45.py) |
| 2026-04-26 | 未记录 | 清理迷宫旧路线并刷新榜单记录 | [20260426_v03_8f27104f.py](../../references/leaderboard_history/lb_maze/20260426_v03_8f27104f.py) |
| 2026-04-26 | 未记录 | 杂项：记录多机迷宫阶段耗时探针 | [20260426_v04_0fb4b97b.py](../../references/leaderboard_history/lb_maze/20260426_v04_0fb4b97b.py) |
| 2026-04-26 | 未记录 | 减少多机迷宫动态墙刷新 | [20260426_v05_90daee2a.py](../../references/leaderboard_history/lb_maze/20260426_v05_90daee2a.py) |
| 2026-05-31 | 版本注记 1m49.837s | 调整：收敛 leaderboard 脚本真源 | [20260531_v06_1m49.837s_0224fb21.py](../../references/leaderboard_history/lb_maze/20260531_v06_1m49.837s_0224fb21.py) |
| 2026-06-08 | 版本注记 1m43.336s | 刷新迷宫动态负责区策略 | [20260608_v07_1m43.336s_64210144.py](../../references/leaderboard_history/lb_maze/20260608_v07_1m43.336s_64210144.py) |
| 2026-06-09 | 版本注记 1m43.336s | 移除多机迷宫诊断计数 | [20260609_v08_1m43.336s_c50bc4a4.py](../../references/leaderboard_history/lb_maze/20260609_v08_1m43.336s_c50bc4a4.py) |
| 2026-10-27 | 2:07.169（官方完整统计57轮）；本地seed1 122.617166秒，短时2轮124.6955秒。 | 迷宫完整覆盖与唯一取宝并完成官方统计 | [20261027_v09_2m07.169s_efc2b6b5.py](../../references/leaderboard_history/lb_maze/20261027_v09_2m07.169s_efc2b6b5.py) |
| 2026-10-29 | 1:27.674（官方完整统计83轮）；本地seed1 87.650051秒，短时2轮89.290秒。 | 采用独立小迷宫并按动态目标推进策略 | [20261029_v10_1m27.674s_ba9f99c1.py](../../references/leaderboard_history/lb_maze/20261029_v10_1m27.674s_ba9f99c1.py) |
| 2026-10-29 | 1:26.969（官方完整统计83轮，request155）；本地seed1 85.117033秒，短时8轮86.494625秒。 | 迷宫对称建表并迁入单机增量路由 | [20261029_v11_1m26.969s_997625ae.py](../../references/leaderboard_history/lb_maze/20261029_v11_1m26.969s_997625ae.py) |

## 下一步优化方向

- 比较宫数/边长/每宫机数的建图摊销和每箱净收益；新共宫策略须减少主要回应链，避免重做已失败的双份地图。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
