# 南瓜·多机（`lb_pumpkins`）

## 当前策略与成绩

当前脚本：[lb_pumpkins.py](../../scripts/leaderboard/lb_pumpkins.py)。公开账号最高 **6:14.128（#26）**；已有最好本地模拟 **6:13.170**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869892/)，榜单抓取时间 `2026-11-10T06:15:45.988019+00:00`，账号查询时间 `2026-11-10T06:15:45.988053+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

16个互不重叠的6×6、7×7、8×8区域覆盖824格，每区两机维护修补队列。健康成熟格退出待办，死苗补种；邻格共享非空合并编号可跳过部分访问，等待两半完成后由区域负责人收整块。15次树形派发加16助手最多32机，W=0.80、施肥间隔5.5秒；来源enihsyou，MIT。

修正模型后的seed1完整373.169717730秒，与同seed原生simulate纳秒一致；2026-11-03 request259正式20轮均374.127700秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 四个15×15大区、每区八机 | 468.942614秒仅达95.53%原2亿目标，触预算 | 更多往返和全区收尾等待抵消较大方阵收益 | [20261029_rejected_eight_worker.py](../../references/leaderboard_history/lb_pumpkins/20261029_rejected_eight_worker.py) |
| 全场1024格就绪后唯一收割 | 四波47.304634秒，条件外推809.728936秒 | 每波重派、补死苗和最慢成熟尾部过重；组件正确不代表整轮快 | [20261025_rejected_full_cover_component.py](../../references/leaderboard_history/lb_pumpkins/20261025_rejected_full_cover_component.py) |
| 成熟小块立即收 | 62.833612秒组件净12507136 | 大量仅1株或4株收获，丢失大方阵倍率 | [20261030_rejected_partial.py](../../references/leaderboard_history/lb_pumpkins/20261030_rejected_partial.py) |
| 缓存已合并成熟矩形 | 模型374.843637秒；正式374.957900秒，对父正式374.308350秒 | 省2056步但正式完整统计未确认收益 | [20261028_rejected_merged_bounds.py](../../references/leaderboard_history/lb_pumpkins/20261028_rejected_merged_bounds.py) |
| 初种后额外补水 | seed1完整383.164014秒，对父375.234256秒 | 水费和后续补种/成熟反馈没有回本 | [20261028_rejected_seed_water.py](../../references/leaderboard_history/lb_pumpkins/20261028_rejected_seed_water.py) |
| 固定正反交替修补 | 冻结轨迹条件省约5.995%该段移动当量，未运行新候选 | 角测列改变缺等价保证，立即折返也改变死苗/成熟时序；不据几何省步放行 | 仅预算，未写候选 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_pumpkins/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_pumpkins/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v03_8deede45.py](../../references/leaderboard_history/lb_pumpkins/20260424_v03_8deede45.py) |
| 2026-04-24 | 未记录 | 缩短多机南瓜收割路径 | [20260424_v04_6f979a94.py](../../references/leaderboard_history/lb_pumpkins/20260424_v04_6f979a94.py) |
| 2026-04-24 | 未记录 | 实现多机南瓜助手协作 | [20260424_v05_62b17ecf.py](../../references/leaderboard_history/lb_pumpkins/20260424_v05_62b17ecf.py) |
| 2026-04-25 | 未记录 | 提高多机南瓜补水效率 | [20260425_v06_88a6ac4f.py](../../references/leaderboard_history/lb_pumpkins/20260425_v06_88a6ac4f.py) |
| 2026-04-25 | 未记录 | 迁入南瓜榜外部候选 | [20260425_v07_6a12900b.py](../../references/leaderboard_history/lb_pumpkins/20260425_v07_6a12900b.py) |
| 2026-05-31 | 版本注记 6m40.273s | 调整：收敛 leaderboard 脚本真源 | [20260531_v08_6m40.273s_0224fb21.py](../../references/leaderboard_history/lb_pumpkins/20260531_v08_6m40.273s_0224fb21.py) |

## 下一步优化方向

- 比较能减少死苗长尾及最慢区域等待的分工；全覆盖新方案先解决真实跨块合并、收割归属和旧状态失效。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
