# 木头·单机（`lb_wood_single`）

## 当前策略与成绩

当前脚本：[lb_wood_single.py](../../scripts/leaderboard/lb_wood_single.py)。公开账号最高 **5:20.571（#28）**；已有最好本地模拟 **5:13.238**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827415/)，榜单抓取时间 `2026-11-10T06:15:50.052203+00:00`，账号查询时间 `2026-11-10T06:15:50.052237+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8单机棋盘树，巡田同时处理位置请求和Grass/Bush/Carrot支撑。删除独立筹首棵满倍率树的准备与冻结批次管理，开局种子不足时使用Bush退路；后续按真实种子费用和实际木材净增达标。保留0.16水位与固定巡回，来源enihsyou，MIT。

seed1完整313.237685880秒；2026-11-03 request262正式23轮均320.570869565秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 旧claim仅记期望、不确认种植成功 | 旧三seed含4/2/3次普通成熟Tree | 开局Carrot支撑可能欠料；支撑已登记不等于已安装 | [旧版合集](../../references/leaderboard_history/lb_wood_single/)（多方向见版本表） |
| 准备首树并核对真实支撑就绪 | seed1完整378.299953秒；后来冻结批次正式337.969682秒 | 正确性修正有效，但启动、引用和巡回维护费用较高，均被现源替代 | [20261024_rejected_readiness.py](../../references/leaderboard_history/lb_wood_single/20261024_rejected_readiness.py) |
| 24树成熟后逐株往返兑现 | 乐观动作账398.868962秒；再赠送支撑收益仍332.499782秒 | 平均往返距离与支撑改写费用过大；未进入运行 | 仅预算，未写候选 |
| 免往返缓存、不按类型调度 | 独立均匀请求假设下条件长期账318.107229秒，敏感性最低297.722126秒 | 命中率约1/3且命中时没有移除Bush副产；不能把命中收益与最高副产同时套用 | [归档入口](../../references/leaderboard_history/lb_wood_single/)（原记录未标独立源） |
| 支撑补水/等成熟、额外收割orphan或claimed Bush | 历史实机未刷新 | 伴生只看类型，等待与额外收种没有对应收益 | [旧版合集](../../references/leaderboard_history/lb_wood_single/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 版本注记 5m40.868s | 杂项：补齐打榜文档并整理各榜单说明 | [20260418_v01_5m40.868s_5bf0cea6.py](../../references/leaderboard_history/lb_wood_single/20260418_v01_5m40.868s_5bf0cea6.py) |
| 2026-04-24 | 版本注记 5m40.868s | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_5m40.868s_8deede45.py](../../references/leaderboard_history/lb_wood_single/20260424_v02_5m40.868s_8deede45.py) |
| 2026-05-31 | 版本注记 5m36.679s | 调整：收敛 leaderboard 脚本真源 | [20260531_v03_5m36.679s_0224fb21.py](../../references/leaderboard_history/lb_wood_single/20260531_v03_5m36.679s_0224fb21.py) |
| 2026-06-09 | 版本注记 5m36.679s | 移除单机木头探针计数 | [20260609_v04_5m36.679s_380649aa.py](../../references/leaderboard_history/lb_wood_single/20260609_v04_5m36.679s_380649aa.py) |
| 2026-10-27 | 5:37.970（2026-10-26，官方完整22轮，request 109）。 | 单机木头采用自付启动资金与冻结支撑批次 | [20261027_v05_5m37.970s_13b3f691.py](../../references/leaderboard_history/lb_wood_single/20261027_v05_5m37.970s_13b3f691.py) |

## 下一步优化方向

- 围绕真实请求冲突与巡回产量比较状态更少的承接方式；不要重复支撑成熟度或无类型缓存预算。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
