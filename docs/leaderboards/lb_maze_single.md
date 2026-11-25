# 迷宫·单机（`lb_maze_single`）

## 当前策略与成绩

当前脚本：[lb_maze_single.py](../../scripts/leaderboard/lb_maze_single.py)。公开账号最高 **2:06.355（#25）**；当前版本 7200s 全量随机本地模拟均值 **1:59.513（119.513s）**（较旧版模拟 `2:08.197` 快 **-8.684s / -6.8%**，较现行实机 `2:06.355` 快 **-6.842s / -5.4%**，距 `#1 1:35.630` 降至 **+25.0%**）。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17827402/)，榜单抓取时间 `2026-11-10T06:15:45.780308+00:00`，账号查询时间 `2026-11-10T06:15:45.780340+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

**核心策略（8×8 在线边探边收 + `in_d`/`sensed` 分离 + 增量纯 `D` 表 + 收益门限低频沿途探墙）**：
- 直接从 `(0,0)` 原地建宫（省去 `clear()` 与移至中心的空走步），从第 0 箱开始在线边探图边收宝，彻底消除旧版开局 126 步空 DFS 与全图 `build_all_routes` 串行停顿。
- **分离 `in_d[u]`（已入距离表）与 `sensed[u]`（已四向探邻）**：探到连通邻格或开墙露出未访叶格时立即纳入 `D` 表并加入 `frontier`，避免未访桥接叶格造成绕路长尾（曾使 seed 9 暴涨 20.7s）；全 64 格探毕后切入零 `sensed[]` 检查快路径。
- **增量纯 `D` 表（无 `H` 首步表）+ `(u, du)` 预打包 + 倒序 `range(cur_d, 0, -1)`**：实测纯 `D` 表比同步维护 `D+H` 快 1.0s 以上；在 `in_d_list` 预存 `(u, D[u])` 并用倒序 `range` 省去每步 `cur_d -= 1`，在 seed 1..12 上进一步节省 0.70s 解释器开销。
- **收益门限低频沿途探墙**：出发格按 `scan_gap=6` 复检闭墙，偶数箱（`path_scan_mod=2`）沿途复检闭墙，`relocations >= 255` 停止复检；发现新开墙仅在 `rem_boxes * (D[p][q] - 1) >= 150` 时执行增量 `add_edge_dist`。完整执行 300 次正常迁移与最后 1 次收割，目标 616,448 Gold。

**完整验收指标（原版初始条件 + 默认 `game_leaderboard_random`，`--jobs 2`）**：
- 报告：`.codex/tmp/maze/final_lb_maze_single_7200s.json`（C# `--syntax-only` 通过，Python AST `2,493` 节点，SHA256 `6928483781529cddf912e25b0ad58dce7189f0a14eefe424fb100fbfae00bc86`）。
- 样本：**61/61 轮**，累计 **`7,290.275` 游戏秒**，**0 失败、0 警告、0 丢输出**；均值 **`1:59.513`（`119.513s`）**，SD **`10.991s`**，SE **`1.407s`**，标准 95% CI **`±2.815s`**，自适应 95%/99% CI **`±5.696s / ±6.355s`**，范围 **`100.992s (1:40.992) ~ 156.511s (2:36.511)`**。
- 配对固定 seed 1..12 均值 **`116.068s`**（均 `2,687.8` 步，`98.46s` 动作 + `17.60s` 解释器，12/12 全部快于旧版均 `124.554s` / `2,893.0` 步，净提速 **`-8.486s`**）。满足自动实机准入。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| DFS父指针替代图最短路 | 历史短筛277.846秒，对当时双向BFS184.233秒 | 省计算却走更长树路径，忽略后续开墙收益 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| 旧完整next-hop逐目标建表 | 历史短筛262.971秒，其中建表约14.14秒 | 旧构造过重；不等同于当前增量纯 `D` 表 | [旧版合集](../../references/leaderboard_history/lb_maze_single/)（多方向见版本表） |
| 按target懒缓存旧路径树（含 `single_v1` 新版） | 历史短筛226.522秒；新版 `single_v1` 181.4秒（65.5s 解释器） | 每次开墙失效大量缓存树，重建开销远高于增量 APSP | [旧版合集](../../references/leaderboard_history/lb_maze_single/) |
| A*或直线贪心（含 2-bucket 网格 A* 与混合乐观 A*） | 历史A*303.261秒；新版 2-bucket A* `151.0s`（2,784步/45s解释器）；未见目标乐观 A*+APSP `124.6~125.0s` | 每箱独立搜索的解释器开销为增量 `D` 表的 4× 以上；混合版仅省 ~23 步却增 +3.9s 解释器 | 同框架变体，由 `lb_maze_single.py` 可重建 |
| `D+H` 同步首步表（`single_v15`）与展开 `Q0..Q3` 邻接 | `single_v15` seed 1..12 均 `117.787s`（慢 `v14` `+1.015s`）；`Q0..Q3` 展开 `123.2s` 慢于 `adj` 元组解包 `121.4s` | `H` 表初始化与增量更新开销（+4.3s）超过省下的查邻开销（-3.3s）；多数组索引反贵于 2-元组解包 | 同框架变体，由 `lb_maze_single.py` 可重建 |
| 更密/更疏沿途探墙与仅出发点探墙扫描 | seed 1..12：`v16`（每箱探墙+剪枝）`119.488s`（仅省 18.5 步却增 +3.33s 解释器）；仅出发点探墙 `119.98~120.70s`；更疏 `m3/m4` `117.07~118.19s` | `scan_gap=6, prof_thresh=150, path_scan_mod=2, stop_scan=255` 为实测最优平衡点 | [20261028_rejected_path_scan_path_scan.py](../../references/leaderboard_history/lb_maze_single/20261028_rejected_path_scan_path_scan.py) |
| 缩小宫尺寸与开局中心度数重掷 | 8×8 唯一总动作最优（301×2048=616,448）；重掷中心 `deg=3` 仅降初始均距 `16.25→15.81`（概率 7.3%） | 更小宫总步数+迁移动作严格更多；重掷收益不足抵消开销 | 理论与离线抽样验证，无候选代码 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_maze_single/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_maze_single/20260422_v02_aa7209f3.py) |
| 2026-04-25 | 未记录 | 迁入单机迷宫外部候选 | [20260425_v03_61737dfd.py](../../references/leaderboard_history/lb_maze_single/20260425_v03_61737dfd.py) |
| 2026-04-26 | 未记录 | 优化单迷宫 DFS BFS 寻路 | [20260426_v04_f39a443c.py](../../references/leaderboard_history/lb_maze_single/20260426_v04_f39a443c.py) |
| 2026-04-26 | 未记录 | 复用单机迷宫寻路缓冲 | [20260426_v05_c9a03253.py](../../references/leaderboard_history/lb_maze_single/20260426_v05_c9a03253.py) |
| 2026-04-26 | 未记录 | 改进单机迷宫双向寻路 | [20260426_v06_e4daa3e8.py](../../references/leaderboard_history/lb_maze_single/20260426_v06_e4daa3e8.py) |
| 2026-05-31 | 版本注记 2m43.788s | 调整：收敛 leaderboard 脚本真源 | [20260531_v07_2m43.788s_0224fb21.py](../../references/leaderboard_history/lb_maze_single/20260531_v07_2m43.788s_0224fb21.py) |
| 2026-06-09 | 版本注记 2m43.788s | 减少单机迷宫路径检查 | [20260609_v08_2m43.788s_087d0ad9.py](../../references/leaderboard_history/lb_maze_single/20260609_v08_2m43.788s_087d0ad9.py) |
| 2026-06-09 | 版本注记 2m43.788s | 移除单机迷宫诊断计数 | [20260609_v09_2m43.788s_df88665c.py](../../references/leaderboard_history/lb_maze_single/20260609_v09_2m43.788s_df88665c.py) |
| 2026-10-27 | 2:25.112（2026-10-26，官方完整50轮，request 84）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v10_2m25.112s_9d2d3c31.py](../../references/leaderboard_history/lb_maze_single/20261027_v10_2m25.112s_9d2d3c31.py) |
| 2026-11-07 | 2:06.355（2026-11-03，官方完整57轮，request 258）；本地seed1 128.237s，seed 1..12 均 124.554s。 | 8×8整图DFS建表、出发点探墙与对称增量路由 | [20261107_v11_2m06.355s_d30b5f5.py](../../references/leaderboard_history/lb_maze_single/20261107_v11_2m06.355s_d30b5f5.py) |

## 下一步优化方向

- 拆账显示当前版本步数已距 8×8 全知神谕下界（约 `2,627` 步 / `96.4s` 纯动作）仅余 ~60 步（约 `2.0s`），主要余量在 `17.6s` 解释器开销（`add_edge_dist` `~5.5s`、沿路选邻 `~6.1s`、`add_node/init` `~2.9s`）。
- 后续冲 `#10 (1:52.1)` / `1:45` 方向：用代码生成/静态格点展开（参考[解释器计费笔记](interpreter_cost_notes.md#静态格点函数与策略应用)）替换 `for q, dr in adj[p]: if dg[q] < cur_d:` 动态查邻与 `D` 矩阵初始化，或探索低开销局部增量最短路结构进一步压缩这 `17.6s` 解释器成本。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
