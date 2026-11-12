# 向日葵·单机（`lb_sunflowers_single`）

## 当前策略与成绩

当前脚本：[lb_sunflowers_single.py](../../scripts/leaderboard/lb_sunflowers_single.py)。公开账号最高 **4:55.371（#10）**；已有最好本地模拟 **4:54.007**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827413/)，榜单抓取时间 `2026-11-10T06:15:47.825548+00:00`，账号查询时间 `2026-11-10T06:15:47.825577+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8按花瓣降序分桶巡收，延后未熟位置，使用真实可用水肥并在施肥后重新检查成熟。自然保留最低九株，使最后生产花仍满足至少十株的8倍条件；整批不提前重种高瓣。选择同瓣目标使用与移动一致的8格环绕距离查表。来源enihsyou，MIT。

当前模型seed1完整294.007406975秒；2026-11-09 request452正式25轮均295.370520秒，显示295.371秒。修正前模型293.356868255秒已撤回。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 全局最大值高频sweep或max-only/高瓣跳收 | 历史阈值候选约27～28分钟，慢于盲收10:23 | 收获密度崩溃，查询和等稀疏高瓣过贵；旧惩罚链解释已撤回 | [旧版合集](../../references/leaderboard_history/lb_sunflowers_single/)（多方向见版本表） |
| 固定九株7瓣永久支撑 | 正式338.927秒，后自然九株333.201秒 | 重抽支撑和固定生产位较贵，后由自然分桶方案替代 | [旧版合集](../../references/leaderboard_history/lb_sunflowers_single/)（多方向见版本表） |
| 只缩田到6×6 | 独立筛选见归档 | 减少移动同时减少有效生产格，须连同成熟与种收密度比较 | [20261024_rejected_size6.py](../../references/leaderboard_history/lb_sunflowers_single/20261024_rejected_size6.py) |
| 普通曼哈顿选花 | seed1 305.075783秒；环绕选点300.820286秒、查表更快 | 选点距离与真实环绕移动不一致，已由当前查表替代 | [20261028_rejected_wrap_choice.py](../../references/leaderboard_history/lb_sunflowers_single/20261028_rejected_wrap_choice.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_sunflowers_single/20260418_v01_5bf0cea6.py) |
| 2026-04-25 | 未记录 | 迁入单机向日葵外部候选 | [20260425_v02_c4a691e2.py](../../references/leaderboard_history/lb_sunflowers_single/20260425_v02_c4a691e2.py) |
| 2026-04-26 | 未记录 | 优化单向日葵高吞吐路线 | [20260426_v03_d27deec7.py](../../references/leaderboard_history/lb_sunflowers_single/20260426_v03_d27deec7.py) |
| 2026-05-31 | 版本注记 10m35.599s | 调整：收敛 leaderboard 脚本真源 | [20260531_v04_10m35.599s_0224fb21.py](../../references/leaderboard_history/lb_sunflowers_single/20260531_v04_10m35.599s_0224fb21.py) |
| 2026-06-09 | 版本注记 10m35.599s | 复用单机向日葵能量查询 | [20260609_v05_10m35.599s_d6152c1b.py](../../references/leaderboard_history/lb_sunflowers_single/20260609_v05_10m35.599s_d6152c1b.py) |
| 2026-06-09 | 版本注记 10m35.599s | 移除单机向日葵统计计数 | [20260609_v06_10m35.599s_dcc8a765.py](../../references/leaderboard_history/lb_sunflowers_single/20260609_v06_10m35.599s_dcc8a765.py) |
| 2026-10-24 | 版本注记 5m38.927s | 向日葵单机采用最低瓣支撑并记录完整打榜成绩 | [20261024_v07_5m38.927s_6995176d.py](../../references/leaderboard_history/lb_sunflowers_single/20261024_v07_5m38.927s_6995176d.py) |
| 2026-10-27 | 5:33.201（2026-10-26，官方完整22轮，request 83）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v08_5m33.201s_9d2d3c31.py](../../references/leaderboard_history/lb_sunflowers_single/20261027_v08_5m33.201s_9d2d3c31.py) |
| 2026-10-29 | 5:06.334（官方完整24轮，request168）；本地三seed306.495105秒，短时11轮306.156秒。 | 单机向日葵分瓣用水并修正分桶巡收 | [20261029_v09_5m06.334s_ed91277c.py](../../references/leaderboard_history/lb_sunflowers_single/20261029_v09_5m06.334s_ed91277c.py) |

## 下一步优化方向

- 比较分批布局与成熟回访，保持每次实际最大瓣、至少十株及净Power收益；避免恢复已失败的跳过低瓣政策。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
