# 胡萝卜·多机（`lb_carrots`）

## 当前策略与成绩

当前脚本：[lb_carrots.py](../../scripts/leaderboard/lb_carrots.py)。公开账号最高 **3:51.310（#14）**；已有最好本地模拟 **3:51.900**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869887/)，榜单抓取时间 `2026-11-10T06:15:41.890847+00:00`，账号查询时间 `2026-11-10T06:15:41.890877+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32个4×8独占区域，每机沿闭环巡田，用本机位置请求字典安排Grass/Bush/Tree支撑，其余格种Carrot。请求越界或类型冲突时重抽，支撑与生产位置随请求变化，避免全场准备屏障和固定批次等待。水位阈值0.15，并为32机保留真实库存余量；来源为enihsyou的MIT实现。

修正静态函数返回计费后的seed1完整231.899769630秒；2026-11-03 request251正式32轮均231.428875秒。账号最高231.310秒是此前完整统计。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 无预约、自由跨区直接补伴生 | 503.663472秒仅739794432/2000000000 Carrot，触预算 | 支撑互相覆盖，高倍率成熟仅约24.3%；移动与未熟移除远高于现源 | [20261029_rejected_direct_companion_worker.py](../../references/leaderboard_history/lb_carrots/20261029_rejected_direct_companion_worker.py) |
| 4×8固定棋盘、冻结支撑批次 | 完整269.950359秒；当时两阶段父版277.755507秒 | 跨区拒绝、排队空访与20743次支撑改写限制吞吐，后由动态请求版替代 | [20261026_rejected_multi_cohort.py](../../references/leaderboard_history/lb_carrots/20261026_rejected_multi_cohort.py) |
| 全图无伴生纯种植 | 历史短窗无完成轮 | 种子消耗与低倍率吞吐均不支持目标 | [旧版合集](../../references/leaderboard_history/lb_carrots/)（多方向见版本表） |
| 两阶段全场Bush准备 | 正式276.794秒 | 解决启动支撑未就绪，但准备与静态接受率成本更高；作为正确性历史保留 | [旧版合集](../../references/leaderboard_history/lb_carrots/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_carrots/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_carrots/20260422_v02_aa7209f3.py) |
| 2026-04-26 | 未记录 | 优化胡萝卜榜伴生路线 | [20260426_v03_5451789b.py](../../references/leaderboard_history/lb_carrots/20260426_v03_5451789b.py) |
| 2026-05-31 | 版本注记 9m33.732s | 调整：收敛 leaderboard 脚本真源 | [20260531_v04_9m33.732s_0224fb21.py](../../references/leaderboard_history/lb_carrots/20260531_v04_9m33.732s_0224fb21.py) |
| 2026-06-08 | 版本注记 4m45.820s | 刷新胡萝卜六锚点布局 | [20260608_v05_4m45.820s_79f09ff3.py](../../references/leaderboard_history/lb_carrots/20260608_v05_4m45.820s_79f09ff3.py) |
| 2026-06-08 | 版本注记 4m41.545s | 刷新胡萝卜八锚点布局 | [20260608_v06_4m41.545s_2037d095.py](../../references/leaderboard_history/lb_carrots/20260608_v06_4m41.545s_2037d095.py) |
| 2026-06-08 | 版本注记 4m34.363s | 刷新胡萝卜折线锚点布局 | [20260608_v07_4m34.363s_88e63930.py](../../references/leaderboard_history/lb_carrots/20260608_v07_4m34.363s_88e63930.py) |
| 2026-06-08 | 版本注记 4m32.943s | 刷新胡萝卜补水阈值 | [20260608_v08_4m32.943s_964926a0.py](../../references/leaderboard_history/lb_carrots/20260608_v08_4m32.943s_964926a0.py) |
| 2026-06-09 | 版本注记 4m32.943s | 移除多机胡萝卜统计计数 | [20260609_v09_4m32.943s_1a010ab5.py](../../references/leaderboard_history/lb_carrots/20260609_v09_4m32.943s_1a010ab5.py) |
| 2026-06-09 | 版本注记 4m32.943s | 缓存资源榜补水库存读取 | [20260609_v10_4m32.943s_55e362fc.py](../../references/leaderboard_history/lb_carrots/20260609_v10_4m32.943s_55e362fc.py) |
| 2026-10-27 | 4:36.794（2026-10-26，官方完整27轮，request 86）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v11_4m36.794s_9d2d3c31.py](../../references/leaderboard_history/lb_carrots/20261027_v11_4m36.794s_9d2d3c31.py) |

## 下一步优化方向

- 比较区域内更便宜的多类型支撑承接；跨区方案须先给出写入归属和支撑保持方式。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
