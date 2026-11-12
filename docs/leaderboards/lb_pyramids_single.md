# 金字塔·单机（`lb_pyramids_single`）

## 当前策略与成绩

当前脚本：[lb_pyramids_single.py](../../scripts/leaderboard/lb_pyramids_single.py)。公开账号最高 **17:54.147（#5）**；已有最好本地模拟 **17:52.629**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21488443/)，榜单抓取时间 `2026-11-11T09:12:52.089424+00:00`，账号查询时间 `2026-11-11T09:12:52.089424+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

固定5×5专用田，角柱到Limestone读基座，蛇形清土保Sand；非中心柱最多两层，不穿基座时缺块可缓存。清到Limestone立即补底，其他角/侧柱先完成，中心单独重读并最后补尖；材料不足保留库存换片，目标30100 Power。

中心最后版三seed完整均1072.628647187秒；2026-11-09 request484正式7轮1074.146857143秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 通用足印彩块重建/逐层保沙 | 旧彩块seed1 3924.364秒，保沙4373.871秒，稀疏清单3974.134秒 | 通用单机巡层和重复高度读取吞掉少挖少放的收益；固定5×5才显著降低费用 | [20261106_rejected_sand_repair.py](../../references/leaderboard_history/lb_pyramids_single/20261106_rejected_sand_repair.py) |
| 角块最后、主机不在中心 | 三seed1064.878260秒，比中心版快约7.75秒 | 不符合最后补塔尖时主机在中心的要求，未采用 | [20261107_rejected_fixed_five_fill_base.py](../../references/leaderboard_history/lb_pyramids_single/20261107_rejected_fixed_five_fill_base.py) |
| 中心入口/更大7格足印等 | 已完成代表均未优于当时1064.878秒候选 | 减少入场几何不等于少挖覆盖土，须计整轮塔数与净Power | [20261107_rejected_seven_surface_first.py](../../references/leaderboard_history/lb_pyramids_single/20261107_rejected_seven_surface_first.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 4079.887秒（构建26462009，2轮官方完整统计；请求353）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_67m59.887s_6f2a77df.py](../../references/leaderboard_history/lb_pyramids_single/20261106_v01_67m59.887s_6f2a77df.py) |
| 2026-11-06 | 3647.784秒（构建26462009，2轮官方完整统计；请求386）。 | 金字塔单机列间折返减少重复移动 | [20261106_v02_60m47.784s_e845cd6b.py](../../references/leaderboard_history/lb_pyramids_single/20261106_v02_60m47.784s_e845cd6b.py) |
| 2026-11-07 | 1162.559秒（构建26462009，7轮官方完整统计；请求438）。 | 迁入地下五榜结构改进并完成实机复验 | [20261107_v03_19m22.559s_6bb1cb16.py](../../references/leaderboard_history/lb_pyramids_single/20261107_v03_19m22.559s_6bb1cb16.py) |

## 下一步优化方向

- 减少入口和覆盖层挖掘；固定几何已经很便宜，优先核算每塔必须开挖的体积和完成塔数。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
