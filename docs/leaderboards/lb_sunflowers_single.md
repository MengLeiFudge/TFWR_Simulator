# 向日葵·单机（`lb_sunflowers_single`）

## 当前策略与成绩

当前脚本：[lb_sunflowers_single.py](../../scripts/leaderboard/lb_sunflowers_single.py)，人工维护[母版](../../scripts/templates/leaderboard/lb_sunflowers_single.py)及[配方](../../scripts/templates/leaderboard/lb_sunflowers_single.codegen.json)。公开账号最高 **4:32.418（#10）**，来自2026-11-16 request539 的27轮完整统计均值（最好4:26.553／最差4:35.381）；本版三seed原目标完整模拟均值 **4:32.152**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827413/)，榜单抓取时间`2026-11-15T10:09:43.888996+00:00`，账号查询时间`2026-11-15T10:09:43.889025+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)。

8×8按瓣数分桶，场上剩余最高瓣至少12时，收割处立即补种低于当前最高瓣的新苗，让成熟与后续收割重叠；首轮尾部避免15瓣晚苗拖慢，附近最高瓣成熟时先取得启动能量。桶元素用尾部交换删除，选点兼顾环绕距离和预计成熟，实际仍以`can_harvest()`确认。位置编码为`16*y+x`，距离与路径固定生成；低于十株时重填。本轮参考公开机制独立实现，早期enihsyou／MIT版本保留在历史记录。

2026-11-15，冻结`fa567eb`基线，原版10k Power目标，seed0/1/123完整对照：

| seed | 基线／秒 | 本版／秒 |
| --- | ---: | ---: |
| 0 | 294.691196906 | 274.942144541 |
| 1 | 294.007406975 | 271.259655322 |
| 123 | 294.255639064 | 270.254542906 |

均值294.318080982→272.152114256秒，用时减少7.53%。每例15墙钟秒，全部正常结束、目标达成、状态完整，母版和产物均经原版Parser执行。费用报告定位到旧二维动态距离计算43895t、成熟选择60959t及反复距离表构造10288t；整数相对位置表消除重复几何计算后，未预生成母版三seed280.691306791/273.444023412/272.665249746秒，预生成再省5.749/2.184/2.411秒。成熟与随机调用随初始化时间变化，不能把全部差异说成相同动作下的纯tick差。

报告、费用与源码指纹留`.codex/gemini-directions-20261115/`：`sun-single-base`、`sun-single-v2-costs.json`、`sun-tables-mother-final`（seed0/123）、`sun-single-tables-template`（seed1）及`final-sunflowers_single`。生成及逐字节核对见[工具说明](../../simulator/optimizer/README.md)，固定来源见[来源记录](github_strategy_research.md#gemini交接的公开机制)。旧版request452正式均295.370520秒仍是公开成绩来源。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 全局最大值高频sweep或max-only/高瓣跳收 | 历史阈值候选约27～28分钟，慢于盲收10:23 | 收获密度崩溃，查询和等稀疏高瓣过贵；旧惩罚链解释已撤回 | [旧版合集](../../references/leaderboard_history/lb_sunflowers_single/)（多方向见版本表） |
| 固定九株7瓣永久支撑 | 正式338.927秒，后自然九株333.201秒 | 重抽支撑和固定生产位较贵，后由自然分桶方案替代 | [旧版合集](../../references/leaderboard_history/lb_sunflowers_single/)（多方向见版本表） |
| 只缩田到6×6 | 独立筛选见归档 | 减少移动同时减少有效生产格，须连同成熟与种收密度比较 | [20261024_rejected_size6.py](../../references/leaderboard_history/lb_sunflowers_single/20261024_rejected_size6.py) |
| 普通曼哈顿选花 | seed1 305.075783秒；环绕选点300.820286秒、查表更快 | 选点距离与真实环绕移动不一致，后由环绕查表替代 | [20261028_rejected_wrap_choice.py](../../references/leaderboard_history/lb_sunflowers_single/20261028_rejected_wrap_choice.py) |
| 直接滚动补种首代表 | seed1 294.617935504秒，对同批294.007406975秒，退步 | 补种本身不足以回本；后续加入晚苗筛选、启动供电、按瓣补水与整数几何才获益 | 本轮`sunflower-rolling`；重建时从当前母版撤去首轮晚15瓣重抽、启动收割、次高瓣0.85水位并恢复动态二维距离 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_sunflowers_single/20260418_v01_5bf0cea6.py) |
| 2026-04-25 | 未记录 | 迁入单机向日葵外部候选 | [20260425_v02_c4a691e2.py](../../references/leaderboard_history/lb_sunflowers_single/20260425_v02_c4a691e2.py) |
| 2026-04-26 | 未记录 | 优化单向日葵高吞吐路线 | [20260426_v03_d27deec7.py](../../references/leaderboard_history/lb_sunflowers_single/20260426_v03_d27deec7.py) |
| 2026-05-31 | 版本注记 10m35.599s | 调整：收敛 leaderboard 脚本真源 | [20260531_v04_10m35.599s_0224fb21.py](../../references/leaderboard_history/lb_sunflowers_single/20260531_v04_10m35.599s_0224fb21.py) |
| 2026-06-09 | 版本注记 10m35.599s | 复用单机向日葵能量查询 | [20260609_v05_10m35.599s_d6152c1b.py](../../references/leaderboard_history/lb_sunflowers_single/20260609_v05_10m35.599s_d6152c1b.py) |
| 2026-06-09 | 版本注记 10m35.599s | 移除单机向日葵统计计数 | [20260609_v06_10m35.599s_dcc8a765.py](../../references/leaderboard_history/lb_sunflowers_single/20260609_v06_10m35.599s_dcc8a765.py) |
| 2026-10-24 | 版本注记 5m38.927s | 向日葵单机采用最低瓣支撑并记录完整打榜成绩 | [20261024_v07_5m38.927s_6995176d.py](../../references/leaderboard_history/lb_sunflowers_single/20261024_v07_5m38.927s_6995176d.py) |
| 2026-10-27 | 5:33.201（2026-10-26，官方完整22轮，request 83）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v08_5m33.201s_9d2d3c31.py](../../references/leaderboard_history/lb_sunflowers_single/20261027_v08_5m33.201s_9d2d3c31.py) |
| 2026-10-29 | 5:06.334（官方完整24轮，request168）；本地三seed306.495105秒，短时11轮306.156秒。 | 单机向日葵分瓣用水并修正分桶巡收 | [20261029_v09_5m06.334s_ed91277c.py](../../references/leaderboard_history/lb_sunflowers_single/20261029_v09_5m06.334s_ed91277c.py) |

## 下一步优化方向

- 较低瓣滚动补种、尾部删除和预生成环绕表均已采用。下一步只比较达标前少填剩余空格、按瓣选择成熟检查等有明确费用依据的改动；收益把握中等，预选seed0/1/123和每例15墙钟秒，仍须完整10k目标。新增高瓣不得破坏当前最大瓣条件，少移动不能代替净Power兑现。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
