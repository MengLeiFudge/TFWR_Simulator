# 仙人掌·多机（`lb_cactus`）

## 当前策略与成绩

当前脚本：[lb_cactus.py](../../scripts/leaderboard/lb_cactus.py)。公开账号最高 **0:34.634（#67）**；已有最好本地模拟 **0:34.753**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869881/)，榜单抓取时间 `2026-11-10T06:15:41.753120+00:00`，账号查询时间 `2026-11-10T06:15:41.753152+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32机树形派发行列任务，每条线单一写者。铺田顺路预交换左邻逆序，再用单向三格窗口双向收缩边界排序；全部行完成后排全列，最后确认成熟并唯一收获1024株，收益33554432 Cactus。行列屏障和末次收割都计时。

seed1完整34.753450860秒；2026-11-03 request249正式208轮均34.633932692秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 上下半田行列流水 | 完整40.351508秒，对照34.765467秒 | 局部列整理、最终合并、额外交换及派发抵消阶段重叠 | [20261029_rejected_band_pipeline_pipeline.py](../../references/leaderboard_history/lb_cactus/20261029_rejected_band_pipeline_pipeline.py) |
| 4×8块内Young插入后全局整理 | 完整40.799905秒 | 块内有序不足以完成全局偏序，多一轮整理增加总工作 | [20261029_rejected_tile_insertion_tiles.py](../../references/leaderboard_history/lb_cactus/20261029_rejected_tile_insertion_tiles.py) |
| 横纵局部违例轮流扫描 | 完整70.624933秒，少1251swap却多26710move | 15轮扫描和961次派发/等待过重 | [20261029_rejected_local_relaxation.py](../../references/leaderboard_history/lb_cactus/20261029_rejected_local_relaxation.py) |
| 活动边FIFO | 完整65.976511秒 | 避开空整趟扫描仍付大量定位、队列及邻边维护 | [20261030_rejected_active_edges.py](../../references/leaderboard_history/lb_cactus/20261030_rejected_active_edges.py) |
| 全局二维插入并按依赖层派发 | 规划52.909605秒；25层后121.899960秒未收获 | 9062交换、94层的在线规划及同步不支持预算 | [20261030_rejected_global_insertion.py](../../references/leaderboard_history/lb_cactus/20261030_rejected_global_insertion.py) |
| 两个半列专用合并 | 完整43.593666秒 | 中缝插入的往返和交换费用没有回本 | [20261030_rejected_seam_merge.py](../../references/leaderboard_history/lb_cactus/20261030_rejected_seam_merge.py) |
| enihsyou多机插入与KyleGough奇偶网络 | 前者完整39.799900秒；后者有条件必要动作账至少36.872640秒 | 前者移动高，后者同步比较网络加铺田已无明显预算；版本和许可见GitHub研究 | [20261028_rejected_github_algorithms_enihsyou.py](../../references/leaderboard_history/lb_cactus/20261028_rejected_github_algorithms_enihsyou.py) |
| 未成熟反复重种数字、跨田边swap | 机制不成立 | 数字缓存成熟后才刷新；swap不环绕，移动可环绕不改变该限制 | 机制判定，无候选代码 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_cactus/20260418_v01_5bf0cea6.py) |
| 2026-04-23 | 未记录 | 杂项：补齐打榜文档并整理各榜单说明 | [20260423_v02_54907897.py](../../references/leaderboard_history/lb_cactus/20260423_v02_54907897.py) |
| 2026-05-31 | 版本注记 37.265s | 调整：收敛 leaderboard 脚本真源 | [20260531_v03_37.265s_0224fb21.py](../../references/leaderboard_history/lb_cactus/20260531_v03_37.265s_0224fb21.py) |

## 下一步优化方向

- 按当前#1重算稀疏连通多轮收获与在线构盘，计入平方产量、访问与成熟；旧因#10门槛停止的方向不能当机制反证。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
