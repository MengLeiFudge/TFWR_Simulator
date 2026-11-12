# 金字塔·多机（`lb_pyramids`）

## 当前策略与成绩

当前脚本：[lb_pyramids.py](../../scripts/leaderboard/lb_pyramids.py)。公开账号最高 **22:43.254（#5）**；已有最好本地模拟 **21:14.446**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21488014/)，榜单抓取时间 `2026-11-11T09:58:52.452062+00:00`，账号查询时间 `2026-11-11T09:58:52.452086+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

同一时间只修一座原生塔。沿保沙路径定位边界与基座，并行探西基边；每柱只清覆盖土及高于几何面的块，尝试就地补缺。清理结束后用中列加邻格采样取得三列实际高度，依八邻下层支撑修剩余缺块。最多31工人树形派发，Block精确消耗阈值逐层同步；主机提前到中心，全体回收后最后补尖收能量，目标150100。

三seed完整1285.509868964/1241.532496481/1296.294932258秒，均1274.445765901秒；当前版本未实机。上版2026-11-09 request482正式6轮1363.254秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 32机各修独立塔、保留覆土直接完工、侧向dig | 机制不成立 | 世界/塌方共享且只同时修一塔；几何顶面须无遮挡；公开dig不接受方向参数 | 机制判定，无候选代码 |
| 把原塔挖掉重建彩块 | 初版正式5835.884秒，保沙后4738.376→1480.702秒 | 大幅增加自造缺口与全体块操作，天然支撑应尽量保留 | [旧版合集](../../references/leaderboard_history/lb_pyramids/)（多方向见版本表） |
| 沿边定尺寸后逐层全扫描 | 35现实秒时1157.270游戏秒仅49塔；每塔修补约13.014秒 | 几何定位可行，反复扫描完整层没有必要，未完成原目标 | [20261107_rejected_edge_direct.py](../../references/leaderboard_history/lb_pyramids/20261107_rejected_edge_direct.py) |
| 固定5×5、25机协修 | 62塔119.35秒净5648.42 Power，约47/s | 重生/派发摊销压过免定位收益，远低于两倍线119.3/s | [20261111_rejected_s_small.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_small.py) |
| 仅树形派发整列清理 | 完整1342.372秒，对1349.920秒 | 计数快但清理/修补变慢；首版遇Sand就停还留下超高柱 | [20261111_rejected_s_dispatch.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_dispatch.py) |
| 主机中心准备与外部清土重叠 | 末完整周期149232.86/1310.18秒，对同周期150901.01/1284.13秒 | 施工顺序改变增加实际缺口和损耗，没有整轮收益 | [20261111_rejected_s_overlap.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_overlap.py) |
| 区间端点累计层阈值 | 单seed1282.985秒，对1284.128秒，未采用 | 约1.143秒小样本优势未做完整组合确认，保留接近方案 | [20261111_rejected_s_interval.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_interval.py) |
| 八邻实际高度驱动局部修补 | 201.511秒repair_height失败，未达原目标 | 实时局部规则未维持完整支撑/高度恢复条件 | [20261107_rejected_edge_relax_local_support.py](../../references/leaderboard_history/lb_pyramids/20261107_rejected_edge_relax_local_support.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 5835.884秒（构建26462009，2轮官方完整统计；请求352）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_97m15.884s_6f2a77df.py](../../references/leaderboard_history/lb_pyramids/20261106_v01_97m15.884s_6f2a77df.py) |
| 2026-11-06 | 4738.376秒（构建26462009，2轮官方完整统计；请求370）。 | 金字塔多机保留沙体并按层修补 | [20261106_v02_78m58.376s_ae02d7b6.py](../../references/leaderboard_history/lb_pyramids/20261106_v02_78m58.376s_ae02d7b6.py) |
| 2026-11-07 | 1480.702秒（构建26462009，5轮官方完整统计；请求440）。 | 迁入地下五榜结构改进并完成实机复验 | [20261107_v03_24m40.702s_6bb1cb16.py](../../references/leaderboard_history/lb_pyramids/20261107_v03_24m40.702s_6bb1cb16.py) |
| 2026-11-08 | 1338.123秒（本地原目标三seed均值；当前沿边补缺版本未实机验证）。 | 迁入地下功能与榜单的高效结构并固化模拟证据 | [20261108_v04_22m18.123s_feca66ac.py](../../references/leaderboard_history/lb_pyramids/20261108_v04_22m18.123s_feca66ac.py) |

## 下一步优化方向

- 比较清理与修补的依赖次序，按真实缺口体积及最长施工链计价；生成器天然挖空3～6整柱，不能把所有后续缺块都算天然侵蚀。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
