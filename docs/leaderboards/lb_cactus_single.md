# 仙人掌·单机（`lb_cactus_single`）

## 当前策略与成绩

当前脚本：[lb_cactus_single.py](../../scripts/leaderboard/lb_cactus_single.py)。公开账号最高 **0:15.518（#9）**；已有最好本地模拟 **0:15.936**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827398/)，榜单抓取时间 `2026-11-10T06:15:42.007715+00:00`，账号查询时间 `2026-11-10T06:15:42.007749+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8两轮分别种47、44株稀疏连通布局，最长西南偏序链5；按拓扑顺序种植并沿较大的西/南前驱插入。第二轮是第一轮子集，复用土壤；末株后等待1秒成熟界再收完整组。实际收益(47²+44²)×32=132640，超过131072目标。

三seed完整16.52404563/15.78297141/15.50033604秒，均15.93578436秒；2026-11-09 request454正式465轮均15.517909677秒。

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

- 比较更短偏序链且走路更少的连通布局和成熟收尾；按多轮株数平方收益核算完整目标。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
