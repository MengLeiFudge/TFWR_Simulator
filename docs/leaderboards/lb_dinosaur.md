# 恐龙（`lb_dinosaur`）

## 当前策略与成绩

当前脚本：[lb_dinosaur.py](../../scripts/leaderboard/lb_dinosaur.py)。公开账号最高 **13:20.066（#79）**；已有最好本地模拟 **11:24.086**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869889/)，榜单抓取时间 `2026-11-12T08:37:06.266530+00:00`，账号查询时间 `2026-11-12T08:37:06.266561+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

单机戴唯一恐龙帽，递归矩形区域追果，退出时恢复父区域；半盘后切预建主回路并分段前进。延迟子区域计算、复用主区域、按需读取坐标降低规划费用，实际移动方向与迁入版相同。32×32完整换帽结算33488928 Bone；来源lywlucas固定版本，MIT，详见B站来源研究。

原生榜三个seed完整687.88971666/684.08607339/704.01886290秒，主表采用已有最好684.08607339秒；当前版本未实机。旧版request226正式9轮800.065777778秒及后续809.907秒复验属于历史。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 多机同时戴恐龙帽/其他机铺作物约束苹果 | 机制不成立 | 第二顶有效帽报错；普通作物不排除苹果，改变同高连通区可能移除苹果 | 机制判定，无候选代码 |
| 两轮750或近满尾重开 | 两轮代表1564.522秒；旧256→769尾阶段477.347秒 | 平方收益损失和重复启动过重，主要费用发生在中段，免费末尾也不能补齐差距 | [20261108_rejected_partial_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_partial_v1.py) |
| 直段逐果更新目标 | 完整932.927998秒，对旧775.380425秒 | 少移动未覆盖解释器约309.406秒；未兑现原预算 | [20261108_rejected_event_segments_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_event_segments_v1.py) |
| 吃果立即结束后段直列、横向入场 | 前者800秒仍未结算；后者43.126秒仅11552 Bone | 身体/自由区没有持续恢复保证，局部move合法不能证明整轮 | [20261109_rejected_adaptive_fill_v1.py](../../references/leaderboard_history/lb_dinosaur/20261109_rejected_adaptive_fill_v1.py) |
| 固定行蛇形回路接入 | 71.377秒仅4608 Bone；干净起步66.940秒仅288 Bone | 闭环接入与当前身体冲突，不是有效完成时间 | [20261110_rejected_row_cycle.py](../../references/leaderboard_history/lb_dinosaur/20261110_rejected_row_cycle.py) |
| 动态安全Hamilton换边 | 121.675秒组件仅4果，父同窗52果 | 维护回路和搜索太贵，安全不等于快 | [20261030_rejected_dynamic_cycle.py](../../references/leaderboard_history/lb_dinosaur/20261030_rejected_dynamic_cycle.py) |
| 仅改真实半盘计数 | 完整778.249秒，对旧775.380秒 | 该seed观察计数与真实尾长一致，额外统计未带来路线收益 | [20261108_rejected_actual_half_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_actual_half_v1.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_dinosaur/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_dinosaur/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v03_8deede45.py](../../references/leaderboard_history/lb_dinosaur/20260424_v03_8deede45.py) |
| 2026-04-25 | 未记录 | 迁入恐龙榜外部候选 | [20260425_v04_e295d1d9.py](../../references/leaderboard_history/lb_dinosaur/20260425_v04_e295d1d9.py) |
| 2026-05-31 | 版本注记 15m26.484s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_15m26.484s_0224fb21.py](../../references/leaderboard_history/lb_dinosaur/20260531_v05_15m26.484s_0224fb21.py) |
| 2026-06-09 | 版本注记 15m26.484s | 减少恐龙非目标格测量 | [20260609_v06_15m26.484s_4a0dfea6.py](../../references/leaderboard_history/lb_dinosaur/20260609_v06_15m26.484s_4a0dfea6.py) |
| 2026-06-09 | 版本注记 15m26.484s | 减少恐龙坐标回读 | [20260609_v07_15m26.484s_075dbef9.py](../../references/leaderboard_history/lb_dinosaur/20260609_v07_15m26.484s_075dbef9.py) |
| 2026-06-09 | 版本注记 15m26.484s | 压缩恐龙移动热路径 | [20260609_v08_15m26.484s_b7c81abc.py](../../references/leaderboard_history/lb_dinosaur/20260609_v08_15m26.484s_b7c81abc.py) |
| 2026-07-23 | 版本注记 15m26.484s | 恐龙榜算法更新 | [20260723_v09_15m26.484s_55514a27.py](../../references/leaderboard_history/lb_dinosaur/20260723_v09_15m26.484s_55514a27.py) |
| 2026-10-27 | 14:46.835（官方完整统计9轮）；本地seed1 902.299838秒，短时2轮872.558秒。 | 恐龙失败清理并完成官方打榜 | [20261027_v10_14m46.835s_9be4f1ce.py](../../references/leaderboard_history/lb_dinosaur/20261027_v10_14m46.835s_9be4f1ce.py) |
| 2026-10-29 | 13:38.714（官方完整9轮，request159）；本地三seed819.568663秒，短时2轮811.857秒。 | 采用恐龙边界绕行与后期填隙策略 | [20261029_v11_13m38.714s_0876dded.py](../../references/leaderboard_history/lb_dinosaur/20261029_v11_13m38.714s_0876dded.py) |
| 2026-10-30 | 13:20.066（2026-10-30，官方完整9轮，request226）；十果追果后西列整形交接。 | 恐龙短蛇追果与西列整形完成正式打榜 | [20261030_v12_13m20.066s_f66370a4.py](../../references/leaderboard_history/lb_dinosaur/20261030_v12_13m20.066s_f66370a4.py) |
| 2026-11-12 | 本版本尚未取得实机完整统计；仅有本地模拟对照。 | 迁入恐龙递归分区并提高骨头生产速率 | [20261112_v13_13bcd149.py](../../references/leaderboard_history/lb_dinosaur/20261112_v13_13bcd149.py) |

## 下一步优化方向

- 为当前递归身体推导可恢复的区域退出短切与后半安全路径，先算必要恢复路程；迁入前版本移动约占88%，计算优化不能代替路线减少。
- 外部检索按状态表示、允许变形和恢复条件区分算法；旧静态四象限回路未覆盖可恢复矩形，不能因名称相似判已试过。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
