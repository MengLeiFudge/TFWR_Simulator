# 干草·多机（`lb_hay`）

## 当前策略与成绩

当前脚本：[lb_hay.py](../../scripts/leaderboard/lb_hay.py)。公开账号最高 **1:51.991（#76）**；已有最好本地模拟 **1:52.697**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869890/)，榜单抓取时间 `2026-11-10T06:15:43.853910+00:00`，账号查询时间 `2026-11-10T06:15:43.853941+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32台无人机各服务一个双草单元，先铺30个曼哈顿半径3的Bush支撑格，只接受合法Bush伴生。草地收割会自动再生草并重抽伴生，失败分支只harvest，不再重复plant；主机原地派发，由工人自行到位。两草轮转、成熟判断、三桶优先及低库存补水共同决定有效周期。

seed1完整112.696615080秒；2026-11-03 request255正式65轮均112.014277秒。账号最高111.991秒来自此前版本。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 纯滚动收草 | 历史外部入口修正目标后仍明显慢于双草伴生 | 缺少160倍伴生，现实加速下的库存增长不能当游戏成绩 | [归档入口](../../references/leaderboard_history/lb_hay/)（原记录未标独立源） |
| 四生产位固定Bush异步队列 | 组件64.921855秒净551896064 Hay | 初始化、重抽和成熟轮转未形成比双草更好的吞吐 | [归档入口](../../references/leaderboard_history/lb_hay/)（原记录未标独立源） |
| 双机共用动态支撑、整代冻结 | 组件62.699949秒净187724800 Hay | 集中安装、派发和等待占掉接受率收益 | [归档入口](../../references/leaderboard_history/lb_hay/)（原记录未标独立源） |
| 同机追远点承接Tree/Carrot；实体邮箱与helper | 历史同机动态支撑及通信预算均未回本 | 往返、翻地、物理信号和减少常驻生产机的费用高于原地重抽；Carrot在机制上可作支撑 | [归档入口](../../references/leaderboard_history/lb_hay/)（原记录未标独立源） |
| GitHub错列分层派发 | seed1候选与父版均112.69529820秒 | 低倍率收获减少但整轮未加快，同效不替换 | [20261028_rejected_github.py](../../references/leaderboard_history/lb_hay/20261028_rejected_github.py) |
| 31单元、Tree-only、三桶-only补水 | 既有实机较慢 | 降低并行量或削弱低库存补水，均没有净收益 | [旧版合集](../../references/leaderboard_history/lb_hay/)（多方向见版本表） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_hay/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_hay/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 提升草榜伴生路线 | [20260424_v03_2160f4c6.py](../../references/leaderboard_history/lb_hay/20260424_v03_2160f4c6.py) |
| 2026-04-24 | 未记录 | 微调草榜补水阈值 | [20260424_v04_966327c5.py](../../references/leaderboard_history/lb_hay/20260424_v04_966327c5.py) |
| 2026-04-24 | 未记录 | 提高草榜补水强度 | [20260424_v05_f3edac6e.py](../../references/leaderboard_history/lb_hay/20260424_v05_f3edac6e.py) |
| 2026-04-25 | 未记录 | 提高多机草榜补水强度 | [20260425_v06_59977c47.py](../../references/leaderboard_history/lb_hay/20260425_v06_59977c47.py) |
| 2026-05-31 | 版本注记 2m48.124s | 调整：收敛 leaderboard 脚本真源 | [20260531_v07_2m48.124s_0224fb21.py](../../references/leaderboard_history/lb_hay/20260531_v07_2m48.124s_0224fb21.py) |
| 2026-06-09 | 版本注记 2m48.124s | 缓存资源榜补水库存读取 | [20260609_v08_2m48.124s_55e362fc.py](../../references/leaderboard_history/lb_hay/20260609_v08_2m48.124s_55e362fc.py) |

## 下一步优化方向

- 比较低移动、无阻塞的支撑承接与生产布局；先核算每次有效收获的重抽、等待和支撑费用。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
