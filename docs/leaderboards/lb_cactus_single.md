# 仙人掌·单机（`lb_cactus_single`）

## 当前策略与成绩

当前脚本：[lb_cactus_single.py](../../scripts/leaderboard/lb_cactus_single.py)。公开账号最高 **0:15.518（#9）**；已有最好本地模拟 **0:15.936**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827398/)，榜单抓取时间 `2026-11-10T06:15:42.007715+00:00`，账号查询时间 `2026-11-10T06:15:42.007749+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8两轮分别种47、44株稀疏连通布局，最长西南偏序链5；按拓扑顺序种植并沿较大的西/南前驱插入。第二轮是第一轮子集，复用土壤；末株后等待1秒成熟界再收完整组。实际收益(47²+44²)×32=132640，超过131072目标。

三seed完整16.52404563/15.78297141/15.50033604秒，均15.93578436秒；2026-11-09 request454正式465轮均15.517909677秒。

2026-11-13固定代码生成原型，以现源SHA256 `e8027520c65b561ec4e16d4cf015c63871ba5673c9114f8f9230f98f8f18125c`冻结母版，使用原版`cactus_single`条件、预选seed0/1/123，60游戏秒／每组三seed共享10墙钟秒预算，每例均完整两批入库132640。

| 本地版本 | seed0游戏秒 | seed1游戏秒 | seed123游戏秒 | 均值游戏秒 | 每轮省tick |
| --- | ---: | ---: | ---: | ---: | ---: |
| 冻结原版 | 15.90132600 | 16.52404563 | 15.78675744 | 16.07070969 | 0 |
| A：展开两批，消除轮次分支 | 15.87103776 | 16.49375739 | 15.75646920 | 16.04042145 | 184 |
| B：另展开固定坐标，删除无引用布局表 | 15.84009108 | 16.46281071 | 15.72552252 | 16.00947477 | 372 |

A每例省0.03028824秒（均值时间-0.1885%），B每例省0.06123492秒（-0.3810%）。解释器实际扣费各省183／371tick，另省1tick的`range`内置调用；物理动作未减少。B产物670行，仍只维护107行原版及规则。9份原版/A/B轨迹（A/B共6组配对）的物理动作及非时间观测顺序、参数和返回值一致；统计修改前后、开关前后和无转换AST往返均保持原版时间、库存、状态、节点／API计数及输出。每份费用均对账，原版seed1的成熟轮询11890tick占解释器17724tick的大部分，不能将其全部视为可消除的计算时间。

原型位置为本机`.codex/tests/tick-optimizer-cactus-20261113/`：`experiment.py`保存生成／执行规则，`generation.json`保存指纹，`comparison.json`保存配对汇总，`profile_*.json`、`*.hot-spots.seed-*.json`及`*.trace.seed-*.jsonl`保留原始报告；`analyze.py`复核费用守恒及轨迹。18份单机完整报告、单机种子批次最长单例0.470墙钟秒；8组既有实机归档重放通过。当前未修改正式脚本或存档，未实机，原型不与上方不同seed组的历史均值混算或替代主表结果。生成与费用规范见[解释器费用](interpreter_cost_notes.md#母版与固定代码生成)。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 满田Morton插入 | 三seed19.106118秒 | 取消选点扫描有收益，但完整偏序与交换仍多，由稀疏两轮替代 | [20261108_rejected_cactus_morton_v1.py](../../references/leaderboard_history/lb_cactus_single/20261108_rejected_cactus_morton_v1.py) |
| 按小值桶接入西南前沿 | 完整27.120秒、161swap | 未兑现60～90交换预算，运输与表维护较贵 | [20261108_rejected_cactus_bucket_frontier_v1.py](../../references/leaderboard_history/lb_cactus_single/20261108_rejected_cactus_bucket_frontier_v1.py) |
| Young交换依赖图重排 | 端点就绪版20.649秒、189move、166swap | 解释器约4.583秒，少巡航未覆盖规划成本 | [20261108_rejected_cactus_young_dag_v1.py](../../references/leaderboard_history/lb_cactus_single/20261108_rejected_cactus_young_dag_v1.py) |
| 增量逆序边消解 | 完整24.766秒、183swap、190move | 状态维护约8.162秒，没有降低足够的实际交换 | [20261108_rejected_cactus_local_edges_v1.py](../../references/leaderboard_history/lb_cactus_single/20261108_rejected_cactus_local_edges_v1.py) |
| 按行Young插入只检查收割起点成熟 | 部分seed仅连锁60株；补成熟保护后三seed21.900098秒 | 局部成熟不保证全组成熟；修正后也未优于父版 | [20261028_rejected_mature_insertion.py](../../references/leaderboard_history/lb_cactus_single/20261028_rejected_mature_insertion.py) |
| 放大世界做稀疏田、感染翻倍、环绕交换、未成熟重种 | 机制不成立 | 单机榜禁Expand升级，感染减半Cactus转Weird，swap不环绕且数字缓存未刷新 | 机制判定，无候选代码 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_cactus_single/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_cactus_single/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 改进单机仙人掌成盘策略 | [20260424_v03_6e11b25c.py](../../references/leaderboard_history/lb_cactus_single/20260424_v03_6e11b25c.py) |
| 2026-05-01 | 未记录 | 测试榜单候选方向 | [20260501_v04_0235ef56.py](../../references/leaderboard_history/lb_cactus_single/20260501_v04_0235ef56.py) |
| 2026-05-31 | 版本注记 21.199s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_21.199s_0224fb21.py](../../references/leaderboard_history/lb_cactus_single/20260531_v05_21.199s_0224fb21.py) |
| 2026-10-29 | 0:20.308（2026-10-28，官方完整355轮，request179）。 | 单机仙人掌采用反对角线插入与成熟收口 | [20261029_v06_20.308s_7b994a31.py](../../references/leaderboard_history/lb_cactus_single/20261029_v06_20.308s_7b994a31.py) |
| 2026-10-30 | 0:20.056（2026-10-30，官方完整359轮，request216）。 | 单机仙人掌环绕选点完成20.056秒打榜 | [20261030_v07_20.056s_6f9000de.py](../../references/leaderboard_history/lb_cactus_single/20261030_v07_20.056s_6f9000de.py) |
| 2026-11-09 | 未取得（Morton顺序西南插入；本地完整目标已验证）。 | 迁入炸药差集推理与仙人掌局部巡航并记录结构筛选 | [20261109_v08_4f99c999.py](../../references/leaderboard_history/lb_cactus_single/20261109_v08_4f99c999.py) |

## 下一步优化方向

- 2026-11-19实测分解（seed1完整16.52秒）：第0批47株8.37秒（含47次till）、成熟等待1.0秒、第1批44株6.03秒、等待与收获1.06秒。每株约4.3个动作＝移动1.3＋种植1＋排序2.3（约0.63次交换×3.65个动作）。
- 世界大小锁死：`set_world_size(16)`/`(32)`在该榜是空操作（返回None，`get_world_size()`始终8），只能8×8共64格，因此“换大田放稀疏长链”不可行。
- 满田一轮实测更慢：目标131072＝32×64²只要64株一轮，但8×8满田一轮实测21.12秒（当前47+44两轮16.52秒）。满田每格有2个西/南前驱，交换约1.5次/格，排序代价翻三倍，省下的一轮抵不过。前驱数才是排序代价的旋钮。
- 排序代价有硬下界：收获要求逐格四邻居有序（`World.cs` `IsSorted`→`AreSorted`，W/S≤本格≤E/N），每条相邻边是逆序的概率约0.5，所以交换次数不可能低于“边数×0.5”。当前91株两轮已是株数最小值（2×46²=4232≥4096），交换也已在逆序下界上，故每株排序不可能低于约1.5个动作。0:10.703反推每株2.9个动作、排序仅0.4个动作，低于该下界，说明前几名不是靠布局或排序实现，差别在产量/成熟/收获触发这一侧。
- 固定展开原型已有小幅稳定收益；下一步在原版计费依据下比较已知坐标的静态前驱与状态访问，计入生成体积和初始化；不把成熟轮询节点当作可直接删掉的时间。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
