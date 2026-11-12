# 干草·单机（`lb_hay_single`）

## 当前策略与成绩

当前脚本：[lb_hay_single.py](../../scripts/leaderboard/lb_hay_single.py)。公开账号最高 **2:51.998（#80）**；已有最好本地模拟 **2:58.350**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827401/)，榜单抓取时间 `2026-11-10T06:15:43.808084+00:00`，账号查询时间 `2026-11-10T06:15:43.808116+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

5×5田保留21株有效Bush，两个相邻草格轮转。合法伴生才进入生产收割；原地harvest重抽利用自动再生，循环条件直接判伴生。补水后用0.5游戏秒的有限成熟检查避免提前收掉有效草，匹配但未成熟的访问不计产出。

seed1完整178.349667480秒；2026-11-03 request256正式42轮均172.448643秒。此前成熟等待版正式171.998秒仍是账号最高。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 原地单草、4×4及同机动态改支撑 | 历史单草窗口无完成轮；部分布局明显慢于双草 | 成熟/重抽空档或额外支撑往返无法摊销 | [旧版合集](../../references/leaderboard_history/lb_hay_single/)（多方向见版本表） |
| 删除开局水、双桶及改横向草位 | 历史实机均未优于约172秒基线 | 开局成熟与两点访问节奏被打乱 | [旧版合集](../../references/leaderboard_history/lb_hay_single/)（多方向见版本表） |
| GitHub高水位与近终点计数 | seed1 175.42965069秒，对照175.15623348秒 | 新增计数和水策略未形成完整收益 | [20261028_rejected_github_hay.py](../../references/leaderboard_history/lb_hay_single/20261028_rejected_github_hay.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_hay_single/20260418_v01_5bf0cea6.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_8deede45.py](../../references/leaderboard_history/lb_hay_single/20260424_v02_8deede45.py) |
| 2026-05-31 | 版本注记 2m58.741s | 调整：收敛 leaderboard 脚本真源 | [20260531_v03_2m58.741s_0224fb21.py](../../references/leaderboard_history/lb_hay_single/20260531_v03_2m58.741s_0224fb21.py) |

## 下一步优化方向

- 只比较能减少重抽或未熟空访的结构；固定支撑混色不能突破每格仅匹配一种请求的概率。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
