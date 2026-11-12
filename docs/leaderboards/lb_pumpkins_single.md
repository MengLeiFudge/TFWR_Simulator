# 南瓜·单机（`lb_pumpkins_single`）

## 当前策略与成绩

当前脚本：[lb_pumpkins_single.py](../../scripts/leaderboard/lb_pumpkins_single.py)。公开账号最高 **7:32.911（#41）**；已有最好本地模拟 **7:20.873**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827408/)，榜单抓取时间 `2026-11-10T06:15:47.075827+00:00`，账号查询时间 `2026-11-10T06:15:47.075857+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

6×6整田种植、按原顺序巡查并用队列补死苗；成熟格与绕边对面具有同一非空合并编号时可以早停剩余巡查。保留0.65水位、真实水肥检查和完整36株收割，先固定90波再按1000万实际库存继续。来源enihsyou，MIT。

seed1完整440.872658460秒；2026-11-03 request260正式16轮455.8626875秒。账号最高452.911秒来自此前编号早停版。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 只把6×6改8×8 | 三seed473.751531秒，对照463.789004秒，慢2.15% | 虽少波次，move及use_item反增；单位面积倍率在6已封顶 | [20261024_rejected_variant.py](../../references/leaderboard_history/lb_pumpkins_single/20261024_rejected_variant.py) |
| 原pending顺序的最早成熟跳访 | 同轨迹54项资格超集，赠送收益包络23.921290秒 | 不足当时25.601365秒缺口，且大多数访问仍需施肥服务；这是冻结路径筛选 | [归档入口](../../references/leaderboard_history/lb_pumpkins_single/)（原记录未标独立源） |
| 尾部最近邻/重新排序 | 历史多轮退化为93波 | 省路程改变等待节奏与补种时点，实际没有收益 | [旧版合集](../../references/leaderboard_history/lb_pumpkins_single/)（多方向见版本表） |
| 过早施肥、极窄pending阈值、连续施肥 | 历史过早施肥595.157秒；多个阈值未优于483.280秒旧基线 | 肥料花在非真正尾格、感染与补种增加；具体旧政策关闭 | [旧版合集](../../references/leaderboard_history/lb_pumpkins_single/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_pumpkins_single/20260418_v01_5bf0cea6.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_8deede45.py](../../references/leaderboard_history/lb_pumpkins_single/20260424_v02_8deede45.py) |
| 2026-04-24 | 未记录 | 缩短单机南瓜收割路径 | [20260424_v03_4ada7948.py](../../references/leaderboard_history/lb_pumpkins_single/20260424_v03_4ada7948.py) |
| 2026-04-24 | 未记录 | 放宽单机南瓜尾部施肥 | [20260424_v04_10a5fe5c.py](../../references/leaderboard_history/lb_pumpkins_single/20260424_v04_10a5fe5c.py) |
| 2026-05-31 | 版本注记 7m52.654s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_7m52.654s_0224fb21.py](../../references/leaderboard_history/lb_pumpkins_single/20260531_v05_7m52.654s_0224fb21.py) |
| 2026-06-09 | 版本注记 7m40.295s | 压缩单南瓜波次路径 | [20260609_v06_7m40.295s_f15193f1.py](../../references/leaderboard_history/lb_pumpkins_single/20260609_v06_7m40.295s_f15193f1.py) |
| 2026-06-09 | 版本注记 7m38.450s | 刷新单南瓜尾部死点处理 | [20260609_v07_7m38.450s_1cff7a6b.py](../../references/leaderboard_history/lb_pumpkins_single/20260609_v07_7m38.450s_1cff7a6b.py) |

## 下一步优化方向

- 在当前队列中比较真正可取消的补种/确认访问，连同成熟时序与最终合并收益一起计价。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
