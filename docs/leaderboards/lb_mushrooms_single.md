# 蘑菇·单机（`lb_mushrooms_single`）

## 当前策略与成绩

当前脚本：[lb_mushrooms_single.py](../../scripts/leaderboard/lb_mushrooms_single.py)。公开账号最高 **12:37.850（#7）**（2026-11-16 request540 的 10 轮完整统计均值）；当前本地模拟 **5:22.248（7200游戏秒完整抽样 23 轮，累计 7411.705 游戏秒，默认游戏随机 `game_leaderboard_random`，标准差 6.848 秒、标准误 1.428 秒，95% 自适应置信区间 ±5.366 秒／常规 95% CI ±2.961 秒，范围 5:10.690～5:38.148，0 失败、0 警告、0 输出丢弃；尚无本版实机）**。

按当前公开榜基准对比：距 #1 **3:47.961（+41.4%）**、#3 **5:46.334（-7.0%）**、#10 **16:41.055（-67.8%）**；较旧版实机 12:37.850 / 旧版模拟 12:34.068 缩短 **57.3%～57.5%（2.35× 提速）**，已跨过阶段一 2×#1（7:35.922）与阶段二 +50%（5:41.942）两道门槛，并满足自动实机准入条件（待主线统一安排实机）。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444535/)，榜单抓取时间 `2026-11-25T10:38:16.211694+00:00`，账号查询时间 `2026-11-25T10:38:16.211729+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

**核心算法（2026-11-25 架构重写）**：
1. **机制纠偏**：C# 原版源码（`Simulation.cs:260-264`、`Farm.cs:1296-1304`、`Farm.cs:461-497`、`Farm.cs:1854-1923`、`World.cs:1844-1893`）证实单机 `6,075 t/s` 为 100% 动作/解释器受限而非等待受限；覆盖土/岩石具备 `autodestroyWhenDugBeside=1`，而蘑菇具备 `stability=3, autodestroyWhenDugBeside=0`；`push(200t)` 与 `move/measure/get_pos_z` 在 8×8 环面全向环绕且永不触发塌方，异色 `push` 为合法原地堆叠（不毁块）。
2. **多米诺塌方揭盖 + 5/6 层选场**：在 `(0,0)` 挖穿覆盖层后探测 `height >= 5`（接受 5 层和 6 层场，将拒场浪费减半）；随后沿 28 格连通支配脊线（`y=0,3,6` 及两处桥接）每格仅挖 1 块蘑菇（238t），利用覆盖层 `autodestroyWhenDugBeside=1` 一次性塌平全部 64 格覆盖层（无论覆盖层厚 1 层还是 10 层，均在 ~2.3 秒内 64/64 无损揭盖），并顺路单次读取全盘 64 格 `(z, color)`，0 额外移动。
3. **无损表面高度场 + 埋压栈缓存 + 原地异色堆叠蓄色**：揭盖后匹配阶段全程不调用 `dig()`（0 塌方失效），用定长 64 格数组维护 `(z_arr, c_arr, buried)`，每次 `push` 仅在埋压栈为空时做 1~2 次 1t `measure()`，全程 0 `get_pos_z()` / 0 `get_ground_type()`。热路径按开销递增依次执行：① 合并单次四邻检查 `d=0` 原地直推（200t）与 `d=1` 邻格反推（400t）；② `d=1` 邻格前推（400t）；③ 展开式两步过桥（600t）与双邻汇合（800t）；④ 弹出 LIFO 就绪边栈（距离 ≥3 时优先原地 0 移动异色堆叠蓄色暴露新色）；⑤ 就绪栈空时原地或 `O(1)` 环形游标高柱向低邻异色堆叠；剩余块数 `<= 96` 提前换场，避免低密度尾段空耗。
4. **解释器瘦身**：所有条件优先比较 `c_arr[nb] == cu`（83.3% 短路）；省略 `c_arr[a] >= 0` 冗余判断（空柱同在 `bottom` 使 `z_arr[a] > z_arr[b]` 自动为假）；原地连消延迟维护 `add_edges` 减少无效入栈；用 8 元素环面查表 `DX/STEP_D` 消除取模开销。

2026-11-25 配对对照（seed1-3 完整 30k 目标）：旧正式版 `c84ec62` 752.354 / 777.639 / 740.901 秒（均 756.965 秒），本版 308.0 / 319.4 / 323.4 秒（均 316.92 秒，缩短 58.1%）；`--syntax-only` 原版 Parser 通过，无警告。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 仅接受 6 层场（`H_MIN=6`）配本版表面场 | seed1-3 均 390.14 秒，对 `H_MIN=5` 373.77 秒（v2 口径） | 多米诺揭盖把单场揭盖压至 ~2.3 秒后，丢弃 5 层场的串行重掷成本高于 6 层多出的产量 | v2 消融验证（可由 `h_min=6` 重建） |
| 禁用异色堆叠（`max_idle=0`） | seed1-3 均 475.08 秒，对 `max_idle=10` 373.77 秒（v2 口径） | 无异色蓄色时中盘过早枯竭，换场次数从 39 暴增至 128 | v2 消融验证（可由 `max_idle=0` 重建） |
| 禁用本地过桥或 `d=1` 邻格前推 | 禁过桥 402.32 秒（+28.6s）；禁前推 324.71 秒对 318.33 秒（v5） | 8×8 环面上本地 1 步前推与 2 步过桥均显著减少跨盘移动与非匹配推送 | v2/v5 消融验证（可由参数重建） |
| `ready` 栈多槽前瞻（`PEEK_K=4/8`） | seed1-3 均 332.94 / 332.96 秒，对 `PEEK_K=0` 328.16 秒 | 额外弹出重插的解释器费用高于偶发减步收益 | v4 消融验证（可由参数重建） |
| 4 行加密脊线（`y=0,2,4,6`, 35 格）与隔格双挖 | 离线同口径 API 251.6s / 248.1s，对 28 格脊线 238.9s | 多挖 7+ 格的挖掘和失块成本超过初始多出的高度差边 | `.codex/tests/mushrooms/sim_lab4.py` 结论 |
| 覆盖厚度上限截断（`C_MAX=5/8`） | seed1-3 均 392.29 / 386.89 秒，对不截断 373.77 秒 | 多米诺揭盖使每场覆盖层仅在 `(0,0)` 挖一次，提前弃深场反而增加总重掷次数 | v2 消融验证（可由 `C_MAX` 重建） |
| 双源确定配对队列 | 完整909.809017秒，move10176/dig3373/push3192 | 每对5.43move/1.80dig/1.70push，未兑现2move/1dig预算 | [20261109_rejected_mushroom_pair_queue_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_rejected_mushroom_pair_queue_v1.py) |
| 直接队列/全田就绪边/最高柱混合 | 完整941.855/944.217/1069.597秒 | 全田维护和开孔没有创造更多可兑现配对；最高柱代表API单独约583秒 | [20261108_rejected_mushroom_ready_edges_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_ready_edges_v1.py) |
| 双行输送/连续局部合并/三推定向滑块 | 1814.870/1481.578秒；三推预算到2617秒仅10768 | 搬运和全田规划太贵，失配材料与重复准备多 | [20261108_rejected_mushroom_routed_sliding_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_routed_sliding_v1.py) |
| 固定接收井/五格双向枢纽 | 完整1113.237/1563.424秒 | 局部颜色耗尽、频繁换片，平均动作预算未兑现 | [20261108_rejected_mushroom_bidirectional_hubs_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_bidirectional_hubs_v1.py) |
| 黑白格源接收/4格小田 | 完整2890.594/959.772秒 | 额外空巡和97次换片的准备抵消局部缩短 | [20261108_rejected_mushroom_small_world_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_small_world_v1.py) |
| 十字自动揭盖/空接收柱 | 十字三seed828.444/843.154秒；空接收正式1344.643秒对1335.308秒 | 少挖损失配对机会，后者本地小收益未在正式样本确认 | [20261106_rejected_empty_receiver_26462009.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_rejected_empty_receiver_26462009.py) |
| 固定局部模板 | 完整953.632644秒 | 配对动作和供料利用率均未支持较小预算 | [20261109_rejected_mushroom_local_templates_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_rejected_mushroom_local_templates_v1.py) |
| 两趟扫描，先配对后削峰 | seed1首个完整场2352/81.11秒，对原版2240/54.92秒；合并局部揭盖80.73秒 | 材料保留增加112，重复巡视多约26秒，净速率更差，不采用 | 从 `0102d33:scripts/leaderboard/lb_mushrooms_single.py` 改造；多机同构[代表](../../references/leaderboard_history/lb_mushrooms/20261116_rejected_retain_first_pass.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1335.308秒（构建26462009，6轮官方完整统计；请求349）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_22m15.308s_22bf18ce.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v01_22m15.308s_22bf18ce.py) |
| 2026-11-06 | 1164.739秒（构建26462009，7轮官方完整统计；请求378）。 | 蘑菇单机三格高度带完成整轮复验 | [20261106_v02_19m24.739s_af973d71.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v02_19m24.739s_af973d71.py) |
| 2026-11-09 | 13:32.194（2026-11-09，build26462009，官方完整9轮，request473）。 | 补齐蘑菇失败恢复并记录十二榜实机成绩 | [20261109_v03_13m32.194s_45bb4345.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_v03_13m32.194s_45bb4345.py) |
| 2026-11-15 | 旧seed1/2/3完整均791.82913461秒。 | 六层筛选、feed结果缓存；上一轮替换前的冻结实现 | [20261115_baseline_0102d33.py](../../references/leaderboard_history/lb_mushrooms_single/20261115_baseline_0102d33.py) |
| 2026-11-16 | 12:37.850（#7，request540 10轮官方完整统计）；模拟 12:34.068（30轮）。 | 固定蛇行路线、先挑候选再配对、逐层扫描 | [20261116_v04_12m37.850s_c84ec62.py](../../references/leaderboard_history/lb_mushrooms_single/20261116_v04_12m37.850s_c84ec62.py) |
| 2026-11-25 | 5:22.248（本地7200游戏秒完整抽样23轮，游戏随机，SD=6.848s，95%自适应CI±5.366s；尚无实机）。 | 多米诺塌方揭盖 + 无损表面高度/埋压栈缓存 + 原地异色堆叠蓄色与过桥/汇合 | 当前 [lb_mushrooms_single.py](../../scripts/leaderboard/lb_mushrooms_single.py) |

## 下一步优化方向

- 本版已从 +230.8% 压至 +41.4%（超越公开 #3 `5:46.334`，满足阶段二 +50% 与自动实机准入），下一步优先安排实机完整打榜以刷新公开排名。
- 后续若继续向 #1（3:47.961，折合 738 t/对）冲击，当前约 1,045 t/对中 `move` 占 ~330t、`push` 占 ~300t、`dig`（探场+28格脊线）占 ~148t、解释器占 ~250t：可重点探索 ① 24~26 格更短连通支配脊线或在揭盖沿途顺手消除同色边；② 颜色导向的异色蓄色选向（优先推向同色最近邻而非最低邻，压低非匹配 push 比例）；③ 静态格点查表与热循环代码生成压缩剩余解释器费用。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
