# 迷宫·多机（`lb_maze`）

## 当前策略与成绩

当前脚本：[lb_maze.py](../../scripts/leaderboard/lb_maze.py)。公开账号最高 **1:26.965（#14）**；当前版本 7200s 全量随机本地模拟均值 **0:38.823（38.823s）**（较现行实机暴降 **-48.142s / -55.4%**，大破第一阶段 2×#1 线 `0:59.072` 与第二阶段 +50% 线 `0:44.304`，快于公开 `#5 0:42.777`，距 `#1 0:29.536` 降至 **+31.4%**）。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869891/)，榜单抓取时间 `2026-11-15T14:58:45.796127+00:00`，账号查询时间 `2026-11-15T14:58:45.796160+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

**核心策略（32×32 合法流水线重建 + `d≤1` 高概率狙击，推翻旧“不再优化”结论）**：
- 基于 `World.cs` / `Execution.cs` 源码证实的纯合法预期机制：`HedgePlant.Harvest()` 立即清空整座迷宫（`t=0` 落为可直覆的 `Grass`），`plant(Entities.Bush)` 可直接覆盖 `Grass` 且对 `Hedge` 仅耗 1t 返回 `False`，`BushPlant.GenerateHedgeMaze(32)` 无成熟度要求且生成的 `Treasure` 立即 `Harvestable == true`（无 `RepositionTreasure` 的 200t 搬迁冷却），单座 32×32 仅耗 `1024` 份 `Weird_Substance`（初始库存 `1,000,000,000`，整轮 8,000+ 次重建仅用约 `0.8%`）。每座迷宫的宝藏至多通过正常 `harvest()` 收取一次，零重复收箱漏洞。
- 32 机角色分工（`P=9, H=9, F=5`，共驻守 23 个独立格点，距 `(0,0)` 环绕距离 `≤11` 压缩开局布阵）：
  - **9 种植机（role 0）+ 9 生成机（role 1）**：配对驻守 9 格（含 4 个 `sym(1,1)` 高叶概率格），以 `Weird_Substance` 全局递减步长同步轮转，`while not plant(Entities.Bush):` 1t 自旋衔接清场，`get_entity_type() == Entities.Bush` 立即 `use_item` 建新宫，空闲期兼顾本位 `d=0` 收宝。
  - **9 错失收割机（role 2）**：驻守 9 个内点，按步长接力读取 `measure() not in my_hit`（每机从 `hit_set` 移除自身坐标 `my_pos`，同时覆盖本位 `d=0` 收宝与未命中清场），4t 内清理错失迷宫。
  - **5 纯狙击机（role 3）**：零流水线冷却，驻守 4 个超高叶概率角格 `(0,0),(31,0),(0,31),(31,31)`（`GenerateHedgeMaze` 均匀抽 DFS 叶子令四角 `d=0` 概率高出均值 2.4×~4.6×，`d≤1` 达 3.8×~5.4×）与内点 `(4,4)`，覆盖 `d=0` 及开放 `d=1` 邻格（`return_home` 含 20 次撞墙 `harvest()` 防死锁兜底）。

**完整验收指标（原版初始条件 + 默认 `game_leaderboard_random`，`--jobs 2`）**：
- 报告：`.codex/tmp/maze/final_lb_maze_7200s.json`（C# `--syntax-only` 通过，Python AST `1,829` 节点，SHA256 `96820d8546d353adf5797a37f694a799c0b6e0f14a6a033d27f4bbf191349889`）。
- 样本：**186/186 轮**，累计 **`7,221.165` 游戏秒**，**0 失败、0 警告、0 丢输出**；均值 **`0:38.823`（`38.823s`）**，SD **`1.694s`**，SE **`0.124s`**，标准 95% CI **`±0.245s`**，自适应 95%/99% CI **`±0.551s / ±0.597s`**，范围 **`33.871s ~ 43.922s`**。
- 固定 seed 1..4 快筛均值 `38.066s`（`[39.32, 39.09, 36.41, 37.44]`）；seed 1 `--hot-spots` 约 8,414 次重建（约 27.66t/宫），全 32 机活跃。满足自动实机准入。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 32×32共宫唯一负责与动态驻点 | 唯一覆盖版正式127.169105秒；并行分枝代表115.858938秒 | 探索、布站、回应与归位的真实链仍慢于独立小宫 | [20261029_rejected_branch_team_team.py](../../references/leaderboard_history/lb_maze/20261029_rejected_branch_team_team.py) |
| 16宫双机持续巡逻/探索兑现分工 | 完整180.071982/198.939086秒 | 双份探索、导航与协调费用高于小宫单一写者 | [20261030_rejected_explorer_collector.py](../../references/leaderboard_history/lb_maze/20261030_rejected_explorer_collector.py) |
| 第二代按需BFS与反向目标缓存 | 完整90.232782/102.031204秒 | 反复重建及维护费用没有抵消全表收益 | [20261028_rejected_lazy_final_generation.py](../../references/leaderboard_history/lb_maze/20261028_rejected_lazy_final_generation.py) |
| 延迟探墙、沿途探墙 | 完整86.832763/89.726442秒，对照85.117033秒 | 少探墙多绕路，或少量省移动却大增规划 | [20261028_rejected_demand_scan.py](../../references/leaderboard_history/lb_maze/20261028_rejected_demand_scan.py) |
| 固定驻点/全局换中心几何与合作大宫神谕下界 | 免费建图/规划下 32×32 Voronoi 神谕 `53.5s`、`4×(16×16, 8机)` 神谕 `57.8s`；实作 `multi_race` 单次 1024 格 BFS 约 35k tick（~6s/次） | 即使零建图/零解释器开销，301 次搬迁合作大宫下界仍远逊于流水线重建（`38.8s`）；拆分为 `K` 座小宫流水线重建时命中×吞吐按 `1/K` 衰减 | [20261026_rejected_parallel_stations.py](../../references/leaderboard_history/lb_maze/20261026_rejected_parallel_stations.py) |
| 纯轮询、漏格补图、容量回退串行等待 | 历史请求124/126/127/132分别中止或失败 | 漏节点与尚未派出区域的等待依赖不闭合；后用边界树补图修正 | [20261026_rejected_single_owner_root_overflow.py](../../references/leaderboard_history/lb_maze/20261026_rejected_single_owner_root_overflow.py) |
| 结算窗口重复收同一宝藏 | 不采用 | 违反项目预期玩法；每座迷宫宝藏至多正常收取一次 | 机制判定，无候选代码 |
| brigante91单座32×32、32驻点、动态墙/根树（含16-pass降频） | 原文与16-pass变体均15墙钟秒到限未达标 | 空闲循环狂调 `measure()`（268万次），未获有效完整成绩 | 固定commit `0c48d1ba28758138b138ca407888589d68703288` 可重建 |
| 流水线重建配比扫描（`P=7..10`、`H_DO_D1=True`、`d=2`、先收草再种、work-stealing） | seed 1..4 均值：`P7_H7_F11` `39.97s`、`P8_H8_F8` `38.53s`、`P8_H9_F7` `38.54s`、`P9_H10_F4` `38.59s`、`P10_H10_F2` `40.49s`；`H_DO_D1=True` `41.93s`；work-stealing `v10` 同步失步触 `api_call_limit` | `P=9, H=9, F=5` 兼顾 9 路流水线吞吐与四角零冷却纯狙击；错失机做 `d=1` 触发 400t 冷却反慢 3.9s；`d=2` 探步约 726t/箱慢于重建；无锁偷任务易双种失步 | 同结构参数变体，由 `lb_maze.py` 改 `P/H/F` 可重建 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 版本注记 21m12.142s | 导入 TFWR_Simulator | [20260418_v01_21m12.142s_5bf0cea6.py](../../references/leaderboard_history/lb_maze/20260418_v01_21m12.142s_5bf0cea6.py) |
| 2026-04-24 | 版本注记 21m12.142s | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v02_21m12.142s_8deede45.py](../../references/leaderboard_history/lb_maze/20260424_v02_21m12.142s_8deede45.py) |
| 2026-04-26 | 未记录 | 清理迷宫旧路线并刷新榜单记录 | [20260426_v03_8f27104f.py](../../references/leaderboard_history/lb_maze/20260426_v03_8f27104f.py) |
| 2026-04-26 | 未记录 | 杂项：记录多机迷宫阶段耗时探针 | [20260426_v04_0fb4b97b.py](../../references/leaderboard_history/lb_maze/20260426_v04_0fb4b97b.py) |
| 2026-04-26 | 未记录 | 减少多机迷宫动态墙刷新 | [20260426_v05_90daee2a.py](../../references/leaderboard_history/lb_maze/20260426_v05_90daee2a.py) |
| 2026-05-31 | 版本注记 1m49.837s | 调整：收敛 leaderboard 脚本真源 | [20260531_v06_1m49.837s_0224fb21.py](../../references/leaderboard_history/lb_maze/20260531_v06_1m49.837s_0224fb21.py) |
| 2026-06-08 | 版本注记 1m43.336s | 刷新迷宫动态负责区策略 | [20260608_v07_1m43.336s_64210144.py](../../references/leaderboard_history/lb_maze/20260608_v07_1m43.336s_64210144.py) |
| 2026-06-09 | 版本注记 1m43.336s | 移除多机迷宫诊断计数 | [20260609_v08_1m43.336s_c50bc4a4.py](../../references/leaderboard_history/lb_maze/20260609_v08_1m43.336s_c50bc4a4.py) |
| 2026-10-27 | 2:07.169（官方完整统计57轮）；本地seed1 122.617166秒，短时2轮124.6955秒。 | 迷宫完整覆盖与唯一取宝并完成官方统计 | [20261027_v09_2m07.169s_efc2b6b5.py](../../references/leaderboard_history/lb_maze/20261027_v09_2m07.169s_efc2b6b5.py) |
| 2026-10-29 | 1:27.674（官方完整统计83轮）；本地seed1 87.650051秒，短时2轮89.290秒。 | 采用独立小迷宫并按动态目标推进策略 | [20261029_v10_1m27.674s_ba9f99c1.py](../../references/leaderboard_history/lb_maze/20261029_v10_1m27.674s_ba9f99c1.py) |
| 2026-10-29 | 1:26.969（官方完整统计83轮，request155）；本地seed1 85.117033秒，短时8轮86.494625秒。 | 迷宫对称建表并迁入单机增量路由 | [20261029_v11_1m26.969s_997625ae.py](../../references/leaderboard_history/lb_maze/20261029_v11_1m26.969s_997625ae.py) |
| 2026-11-09 | 1:26.965（前版实机83轮）；本版seed1模拟 1:24.744（三例均 1:26.387，seed 1..6 均 1:26.661）。 | 32座独立小宫对称建表 + 全局Gold达标收尾 | [20261109_v12_1m24.744s_45bb434.py](../../references/leaderboard_history/lb_maze/20261109_v12_1m24.744s_45bb434.py) |

## 下一步优化方向

- 优先安排当前 `0:38.823` 版本实机打榜验证（预计可冲进前 5，较旧实机 `1:26.965 (#14)` 快近 48 秒）。
- 理论余量拆账：`P=9` 无气泡下限为 `22.22t/宫`（约 `32.2s`），当前实测 `27.66t/宫`（`38.8s`），差值主要来自 `P/H` 驻点非本轮命中后的 200t 环阻塞（约 `~3.5~4.5s`）与纯狙击 `d=1` 移动 200t 冻结（约 `~1.1s`）。后续若冲 `#1 (0:29.536)`，可研究确定性无竞争的环位跳过/动态调度机制，以及核查更大覆盖数（如 24~26 站位）与高叶概率坐标精确分布的组合收益。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
