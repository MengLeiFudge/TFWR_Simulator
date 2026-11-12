# 炸药·单机（`lb_dynamite_single`）

## 当前策略与成绩

当前脚本：[lb_dynamite_single.py](../../scripts/leaderboard/lb_dynamite_single.py)。公开账号最高 **4:21.802（#8）**；已有最好本地模拟 **4:18.986**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444632/)，榜单抓取时间 `2026-11-11T09:12:48.693513+00:00`，账号查询时间 `2026-11-11T09:12:48.693513+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8单机缓存公开数字和活动约束，用全盘计数/包含关系推理并就近开确定安全格。覆盖层按实际开格才准备，推理停滞时按真实已完成围雷收益正常部分结算，再重生；不把SAFE当已挖格，每盘重建状态，目标100k Dynamite。

合法append初始化版三seed完整256.88164167/257.96066022/262.11541662秒，均258.98590617秒；2026-11-09 request467正式28轮261.801607143秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 增加邻格measure | 完整391.166秒 | 零扩张只清覆盖层，未开雷层不能读出额外煤灰数字 | [20261108_rejected_dynamite_sensors_v1.py](../../references/leaderboard_history/lb_dynamite_single/20261108_rejected_dynamite_sensors_v1.py) |
| 不实际开内部逻辑0格 | 完整396.117秒 | 失去自动清覆盖层，推理和后续准备费用增加 | [20261108_rejected_dynamite_interior_v1.py](../../references/leaderboard_history/lb_dynamite_single/20261108_rejected_dynamite_interior_v1.py) |
| 只换相邻访问路线 | 完整348.072秒 | 少移动未解决重复重建约束和结算返程 | [20261108_rejected_dynamite_routes_v1.py](../../references/leaderboard_history/lb_dynamite_single/20261108_rejected_dynamite_routes_v1.py) |
| 批次/并行规划与按区包装 | 约2692/4133秒；按区无改善 | 单机场景调度与全盘重建大于局部连续求解 | [20261106_rejected_dynamite_parallel_plan.py](../../references/leaderboard_history/lb_dynamite_single/20261106_rejected_dynamite_parallel_plan.py) |
| 旧子集枚举和猜测求解 | 旧正式880.591秒，初版1437.266秒 | 少量高收益盘没有抵偿枚举、猜测和准备；当前直接缓存约束更快 | [旧版合集](../../references/leaderboard_history/lb_dynamite_single/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1437.266秒（构建26462009，6轮官方完整统计；请求351）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_23m57.266s_6702ac6a.py](../../references/leaderboard_history/lb_dynamite_single/20261106_v01_23m57.266s_6702ac6a.py) |
| 2026-11-06 | 1266.656秒（构建26462009，6轮官方完整统计；请求381）。 | 单机炸药复用同盘求解状态并记录完整复验 | [20261106_v02_21m06.656s_4948b8b1.py](../../references/leaderboard_history/lb_dynamite_single/20261106_v02_21m06.656s_4948b8b1.py) |
| 2026-11-07 | 880.591秒（构建26462009，9轮官方完整统计；请求407）。 | 炸药单机按需准备开格覆盖层 | [20261107_v03_14m40.591s_b4936193.py](../../references/leaderboard_history/lb_dynamite_single/20261107_v03_14m40.591s_b4936193.py) |
| 2026-11-08 | 354.964秒（本地原目标三seed均值；当前增量求解版本未实机验证）。 | 迁入地下功能与榜单的高效结构并固化模拟证据 | [20261108_v04_5m54.964s_feca66ac.py](../../references/leaderboard_history/lb_dynamite_single/20261108_v04_5m54.964s_feca66ac.py) |
| 2026-11-09 | 未取得（缓存约束、就近开格与原地结算；本地原目标已通过）。 | 缓存扫雷约束并就近结算降低单机炸药耗时 | [20261109_v05_397be014.py](../../references/leaderboard_history/lb_dynamite_single/20261109_v05_397be014.py) |

## 下一步优化方向

- 按可完成围雷的实际平方收益选择安全任务；只为会改变选择的小约束支付精确推断成本。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
