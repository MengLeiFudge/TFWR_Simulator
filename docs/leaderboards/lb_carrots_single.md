# 胡萝卜·单机（`lb_carrots_single`）

## 当前策略与成绩

当前脚本：[lb_carrots_single.py](../../scripts/leaderboard/lb_carrots_single.py)。公开账号最高 **4:10.642（#20）**；已有最好本地模拟 **4:11.840**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827400/)，榜单抓取时间 `2026-11-10T06:15:41.858180+00:00`，账号查询时间 `2026-11-10T06:15:41.858210+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8单机固定巡田环，位置请求字典决定本次种支撑还是Carrot，冲突请求重抽。比固定四/八锚点和冻结支撑批次少维护一层批次状态，并在巡回中共同服务生产与支撑。成熟收益按81920逐笔核对，提前移除及初始化独立计数；enihsyou来源及MIT许可保留。

seed1完整251.839966590秒；2026-11-03 request252正式29轮均251.449414秒。账号最高250.642秒属于之前动态请求版。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 短字符串替代坐标元组键 | 三seed模拟248.720717秒；正式29轮251.338345秒，父版250.641483秒 | 少解释器费用未转为正式整轮改善 | [20261029_rejected_string_keys.py](../../references/leaderboard_history/lb_carrots_single/20261029_rejected_string_keys.py) |
| 四锚点补水guard | 468.593641秒；八锚点同seed415.468726秒 | 少补水引入更多轮转与未熟访问，明显弱于后续布局 | [20261024_rejected_water_gate.py](../../references/leaderboard_history/lb_carrots_single/20261024_rejected_water_gate.py) |
| 固定Bush八锚点 | 三seed410.701895秒；正式403.330秒 | 固定类型接受率最多1/3，种收重抽动作已占主要预算 | [旧版合集](../../references/leaderboard_history/lb_carrots_single/)（多方向见版本表） |
| 32生产位冻结支撑批次 | 三seed316.270131秒；正式317.897696秒 | 正确保持支撑，但FIFO、冻结和完整巡回仍慢于当前动态请求 | [旧版合集](../../references/leaderboard_history/lb_carrots_single/)（多方向见版本表） |
| 旧四锚点无支撑保护 | 三seed521.692602秒，成熟失配约8.68%～10.23% | 接受时匹配不保证成熟收获时仍匹配；保护版480.091046秒解决后继续被更快结构替代 | [20261024_rejected_variant.py](../../references/leaderboard_history/lb_carrots_single/20261024_rejected_variant.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_carrots_single/20260418_v01_5bf0cea6.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_8deede45.py](../../references/leaderboard_history/lb_carrots_single/20260424_v02_8deede45.py) |
| 2026-04-26 | 未记录 | 完善真实打榜候选验证流程 | [20260426_v03_419d1416.py](../../references/leaderboard_history/lb_carrots_single/20260426_v03_419d1416.py) |
| 2026-04-26 | 未记录 | 优化胡萝卜榜伴生路线 | [20260426_v04_5451789b.py](../../references/leaderboard_history/lb_carrots_single/20260426_v04_5451789b.py) |
| 2026-05-01 | 未记录 | 测试榜单候选方向 | [20260501_v05_0235ef56.py](../../references/leaderboard_history/lb_carrots_single/20260501_v05_0235ef56.py) |
| 2026-05-31 | 版本注记 9m46.899s | 调整：收敛 leaderboard 脚本真源 | [20260531_v06_9m46.899s_0224fb21.py](../../references/leaderboard_history/lb_carrots_single/20260531_v06_9m46.899s_0224fb21.py) |
| 2026-05-31 | 版本注记 8m32.070s | 刷新胡萝卜单榜相邻锚点策略 | [20260531_v07_8m32.070s_7eadf136.py](../../references/leaderboard_history/lb_carrots_single/20260531_v07_8m32.070s_7eadf136.py) |
| 2026-06-09 | 版本注记 8m31.992s | 刷新单机胡萝卜伴生记忆 | [20260609_v08_8m31.992s_bc199704.py](../../references/leaderboard_history/lb_carrots_single/20260609_v08_8m31.992s_bc199704.py) |
| 2026-06-09 | 版本注记 8m31.992s | 移除单机胡萝卜统计计数 | [20260609_v09_8m31.992s_584172a5.py](../../references/leaderboard_history/lb_carrots_single/20260609_v09_8m31.992s_584172a5.py) |
| 2026-06-09 | 版本注记 8m31.992s | 缓存单机胡萝卜种植成本 | [20260609_v10_8m31.992s_e8747744.py](../../references/leaderboard_history/lb_carrots_single/20260609_v10_8m31.992s_e8747744.py) |
| 2026-06-09 | 版本注记 8m31.992s | 缓存资源榜补水库存读取 | [20260609_v11_8m31.992s_55e362fc.py](../../references/leaderboard_history/lb_carrots_single/20260609_v11_8m31.992s_55e362fc.py) |
| 2026-10-27 | 6:43.330（2026-10-26，官方完整18轮，request 82）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v12_6m43.330s_9d2d3c31.py](../../references/leaderboard_history/lb_carrots_single/20261027_v12_6m43.330s_9d2d3c31.py) |
| 2026-10-27 | 5:17.898（2026-10-26，官方完整23轮，request 106）。 | 冻结支撑批次将单机胡萝卜缩短至5分17秒 | [20261027_v13_5m17.898s_43f74d91.py](../../references/leaderboard_history/lb_carrots_single/20261027_v13_5m17.898s_43f74d91.py) |

## 下一步优化方向

- 按每圈实际有效收获数比较新的请求组织，计入支撑冲突和成熟空访；不能只用接受概率放大原吞吐。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
