# 金字塔·多机（`lb_pyramids`）

## 当前策略与成绩

当前脚本：[lb_pyramids.py](../../scripts/leaderboard/lb_pyramids.py)。公开账号最高 **20:14.332（#6）**，来自2026-11-16 request544 的6轮完整统计均值（最好19:14.006／最差21:15.506）；已有最好本地模拟 **11:29.578**（`game_leaderboard_random` 12轮完整验收均值 `689.578s`，SD `17.006s`，标准95% CI `±10.805s`，自适应95% CI `±17.676s`，99% CI `±22.326s`，范围 `658.776s ~ 723.364s`，累计 `8274.942s`，0失败、0警告、`leaderboard_has_overrides=false`）。较旧正式实机 `20:14.332` 快 **`8:44.754`（`-43.2%`）**，大破新 `#1 (7:32.273)` 的 `2×` 线（`15:04.5`）并大幅快于 `#3 (14:21.541)`（距新 `#1` 约 `+52.5%`）。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21488014/)，榜单抓取时间 `2026-11-19T06:32:20.575141+00:00`，账号查询时间 `2026-11-19T06:32:20.575141+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

核心机制与算法架构（全部遵守原版合法机制，无漏洞）：
1. **双 5×5 浅层快开 2× 加速**：开局用两座 5×5 `floor==-3` 多米诺快塔（约 `5.5s` 得 `~200 Power`），确保后续首座大塔全程满 2× 加速不断电。
2. **`set_world_size(30)` + 16 机竖井跨层选塔**：`set_world_size(30)` 既消除 `32×32` 下 `W=31` 溢出回退，又规避原版 `World.cs:TryPlaceRandomly` 在 `size2 == size` 时封死 `W=29` 的缺陷，完整解锁 `W=29`（`3,364 Power/塔`）。每跨过一个未中标 chunk，16 机在 `(14,14)` 并行竖井直挖至下一 chunk 顶部（约 `0.21s/chunk`，比 `clear()` 快约 `4.5×` 并顺带联产 `+16 Block`），每完成 20 座塔或深度达 `-2400` 时 `clear()` 一次控制地形深度。
3. **4 射线并行定位 + 阈值 `W_min = 21`**：4 架无人机沿东/西/南/北并行探查边界并由主机判定 `W >= 21`（单塔 `1,764 ~ 3,364 Power`）；不达标即继续竖井跨层。
4. **32 机八象限偶环多米诺清土 + 1t 内窥**：仅沿偶数环行走，利用 4 邻 `autodestroyWhenDugBeside` 自动清空奇数环覆土至完好沙顶（0 挖掘、0 移动），并以 1t 方向查询 `get_ground_type(dir)` 顺带侦测全部 3～6 根蚀损柱，跳过所有完好内格。
5. **缺柱单机防竞态并挖与 2-Lipschitz 坍塌锥并行重叠**：由固定 1 机/缺柱将 3～6 根蚀损柱挖至 `floor`（避免多机同柱竞态挖穿 `Limestone`），同时其他无人机根据已验证的 4 邻 Sand `stability=2` 规则精确解析计算坍塌后各格高度 `h_after(x,y) = min(H(x,y), min_{e in E} 2 * L1((x,y), e))`，彻底去除二次全塔稳定采样；若估算 `Block` 不足则按棋盘格非邻位并行补矿（避免 `autodestroy` 误吞 `Block` 掉落）。
6. **锥内等块权持久化并行修复**：按各坍塌锥所需 `Block` 权重比例分配全部 31 名工人，每名工人常驻单个锥内按连续等块权列段自底向上同步修补（基于 `Items.Block` 精确层阈值自旋同步，去除每层 `hover(1)` 与跨锥重派），全员回收后主机回 `(cx,cy)` 放塔尖 `Sand` 并收获，目标 `150,000 Power`。

验证与 `--hot-spots` 归因证据：
- `--syntax-only` 通过（Python AST 7,288 节点，SHA256 `54cc8fedbfd8171348fe5c2435e061fd560eeed322259cec30d1b472f0232625`）。
- 固定 seed `1..3` 快筛：均值 `706.485s (11:46.485)`，SD `6.925s`（范围 `11:38.656 ~ 11:51.810`），3/3 成功、0 警告。
- `game_leaderboard_random` 12 轮完整验收：12/12 成功、0 警告、0 异常重试（每轮完成 `54 ~ 58` 座大塔），累计 `8274.942s`，均值 `689.578s (11:29.578)`，SD `17.006s`，标准 95% CI `±10.805s`，自适应 95% CI `±17.676s`，99% CI `±22.326s`，范围 `658.776s (10:58.776) ~ 723.364s (12:03.364)`；无新版实机。
- seed 1 `--hot-spots` 归因（前 `554.3s` / 44 塔窗口，默认 5000 万节点上限处截断）：全部 32 机均实际投入工作，工作机 `1..31` 平均 `api_ticks = 705,306`（范围 `415,946 ~ 1,798,213`）、平均 `wait_for` 仅 `3.59s`；主机（drone 0）`wait_for_latency_game_seconds = 297.19s`（占时钟 `53.6%`），主要来自锥内修复汇聚 `L306 wait_for(h_rep)` `127.8s`（~2.90s/塔）、4 射线定位 `L78 wait_for(h_e)` `103.6s`（~1.64s/次）、清土树汇聚 `L615` `54.6s` 及竖井跨层 `L338` `54.3s`，而缺柱挖掘 `L185 wait_for(h_dig)` 仅暴露 `8.1s`（`0.18s/塔`，几乎被锥计算完全隐藏）。全机 `api_ticks` 分布：`move` 52.5%、`dig` 29.5%、`place` 7.9%、`spawn_drone` 5.5%、层屏障 `num_items` 3.7%。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 32机各修独立塔、保留覆土直接完工、侧向dig | 机制不成立 | 世界/塌方共享且只同时修一塔；几何顶面须无遮挡；公开dig不接受方向参数 | 机制判定，无候选代码 |
| 把原塔挖掉重建彩块 | 初版正式5835.884秒，保沙后4738.376→1480.702秒 | 大幅增加自造缺口与全体块操作，天然支撑应尽量保留 | [旧版合集](../../references/leaderboard_history/lb_pyramids/)（多方向见版本表） |
| 沿边定尺寸后逐层全扫描 | 35现实秒时1157.270游戏秒仅49塔；每塔修补约13.014秒 | 几何定位可行，反复扫描完整层没有必要，未完成原目标 | [20261107_rejected_edge_direct.py](../../references/leaderboard_history/lb_pyramids/20261107_rejected_edge_direct.py) |
| 固定5×5、25机协修 | 62塔119.35秒净5648.42 Power，约47/s | 重生/派发摊销压过免定位收益，远低于当时两倍线119.3/s | [20261111_rejected_s_small.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_small.py) |
| 仅树形派发整列清理 | 完整1342.372秒，对1349.920秒 | 计数快但清理/修补变慢；首版遇Sand就停还留下超高柱 | [20261111_rejected_s_dispatch.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_dispatch.py) |
| 主机中心准备与外部清土重叠 | 末完整周期149232.86/1310.18秒，对同周期150901.01/1284.13秒 | 施工顺序改变增加实际缺口和损耗，没有整轮收益 | [20261111_rejected_s_overlap.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_overlap.py) |
| 区间端点累计层阈值 | 单seed1282.985秒，对1284.128秒，未采用 | 约1.143秒小样本优势未做完整组合确认，保留接近方案 | [20261111_rejected_s_interval.py](../../references/leaderboard_history/lb_pyramids/20261111_rejected_s_interval.py) |
| 八邻实际高度驱动局部修补 | 201.511秒repair_height失败，未达原目标 | 实时局部规则未维持完整支撑/高度恢复条件 | [20261107_rejected_edge_relax_local_support.py](../../references/leaderboard_history/lb_pyramids/20261107_rejected_edge_relax_local_support.py) |
| 清理期完全不补沙 | 15墙钟秒完成55塔，941.199892游戏秒、净Power93147.579，未达原目标；观察速率98.967/s | 去掉即时补沙也去掉临时支撑，后续实际缺口及维修链变长；不能假定所有提前放置都无益 | 从`0102d33`删除`pyramid_clean_fill`的补沙循环并返回0；冻结`pyramid-pure/lb_pyramids.py` |
| 列末记录高度、删除稳定采样 | 八邻闭包三seed首塔即与实测不符；按四邻、Sand稳定度2修正后，三seed共24座塔的预测缺口与稳定实测完全相同 | 别列后续挖掘会使快照失效；正确闭包仍须计算，整片两遍闭包平均约4.3秒/塔，慢于原稳定采样，未采用 | [四邻闭包执行代表](../../references/leaderboard_history/lb_pyramids/20261116_rejected_height_closure.py)；本轮 `make_pyramid.py` 的 `closure-check` 为失败八邻诊断，`closure4-check` 为正确诊断 |
| 西基边两机南北走端点 | seed1完整1310.944088712秒，对1285.509868964秒，慢25.434秒 | 少派机与少挖不等于更短关键路径，定位均时4.437→5.056秒，未采用 | `make_edge.py`从父版替换`pyramid_edge_bounds`，分别spawn/主机调用`pyramid_boundary((x0,y),floor,(0,±1))` |
| 塔外留一格隔离带、缺Block才并行采料 | seed1正常结算32塔，32订单库存均足，最低余量198；动作数量与父版相同，新增采料工人没有启动 | 本窗口没有单机采料瓶颈；不能从未触发分支宣称所有并行备料已验证或无用 | `make_materials.py`及`pyramid-materials-seed1.json`；双向边界完整85塔也无缺料订单，最小余量185 |
| `set_world_size(29)` 试图仅刷 29×29 | `W=29` 生成率 0% | `World.cs:5261` 中 `if (size2 == size)` 导致 29×29 地图无法放置 `W=29` 金字塔；改为 `set_world_size(30)` 后 `W=29` 恢复完整 1/13 概率 | 源码核实，已改用 `set_world_size(30)` |
| 逐层重派波次修复（`multi_v1`） | seed 1 完整 `1669.56s (27:49.6)`（修复占 `756s`） | 每层重新从 `(14,14)` 派发 16 机并跨坍塌锥轮转，移动与 `spawn_drone` 摊销过大 | 被锥内持久化修复取代，未归档 |
| 深柱独占 1 机导致浅边缘饿死（`multi_v4`） | seed 1 修复时间从 `412s` 退化至 `500s` | 为 `span >= 5` 深柱独占工人后，浅边缘锥只剩 4～6 机，长尾反而变慢 | 被按锥总块权比例分配取代，未归档 |
| `clear()` 重掷与不同 `W_min` 阈值扫描 | seed 1..3 均值：`clear`重掷 `W=23` `898.7s`、`W=25` `905.1s`；竖井跨层 `W=27` `863.4s`、`W=25` `722.8s`、`W=23` `711.4s`、`W=19` `715.7s`（均慢于 `W=21` `706.5s`） | 竖井跨层显著快于 `clear()`；`W_min` 过高增加跳层占比，过低增加小塔清土与定位摊销，当前实现以 `W_min=21` 最优 | 可通过调整当前 `lb_pyramids.py` 的 `w_min` 参数复现 |

本批可复用机制：当前资源快照`DesignConstants.caveIn.neighborsInStabilityPropagation=0`对应four，Sand稳定度为2；挖掘后的稳定传播按四邻处理，而新放Sand另要求下层八邻Sand/Limestone（脚下Limestone为例外），`autodestroyWhenDugBeside=1`（Rock/Dirt/Limestone）可沿 4 邻自动连锁清覆土。依据为`simulator/headless/data/assets.json`、原版`Native/Design.cs`、`Native/World.cs`及`Native/Farm.cs`的`ClearGroundWithCaveins`/`ClearGroundInternal`/`isSandSupported`。模板原生蚀损为3～6整柱，且跨 chunk 下探时排行榜 `pretendedChunkDepth=48` 恒定不变。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 5835.884秒（构建26462009，2轮官方完整统计；请求352）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_97m15.884s_6f2a77df.py](../../references/leaderboard_history/lb_pyramids/20261106_v01_97m15.884s_6f2a77df.py) |
| 2026-11-06 | 4738.376秒（构建26462009，2轮官方完整统计；请求370）。 | 金字塔多机保留沙体并按层修补 | [20261106_v02_78m58.376s_ae02d7b6.py](../../references/leaderboard_history/lb_pyramids/20261106_v02_78m58.376s_ae02d7b6.py) |
| 2026-11-07 | 1480.702秒（构建26462009，5轮官方完整统计；请求440）。 | 迁入地下五榜结构改进并完成实机复验 | [20261107_v03_24m40.702s_6bb1cb16.py](../../references/leaderboard_history/lb_pyramids/20261107_v03_24m40.702s_6bb1cb16.py) |
| 2026-11-08 | 1338.123秒（本地原目标三seed均值；当前沿边补缺版本未实机验证）。 | 迁入地下功能与榜单的高效结构并固化模拟证据 | [20261108_v04_22m18.123s_feca66ac.py](../../references/leaderboard_history/lb_pyramids/20261108_v04_22m18.123s_feca66ac.py) |
| 2026-11-15 | 完整三seed均1274.445765901秒。 | 整列稳定采样与临时补沙；本轮替换前的冻结实现 | [20261115_baseline_0102d33.py](../../references/leaderboard_history/lb_pyramids/20261115_baseline_0102d33.py) |
| 2026-11-16 | 1214.332秒（2026-11-16 request544，6轮官方完整统计均值 20:14.332 #6；本地外推 1251.583秒）。 | 二维稳定采样（三列×三行段树形派发）与逐层同步维修 | [20261116_v05_20m14.332s_73ad1b7.py](../../references/leaderboard_history/lb_pyramids/20261116_v05_20m14.332s_73ad1b7.py) |

## 下一步优化方向

- 已满足实机验证自动准入（本地完整模拟 `11:29.578` 远低于新 `#1` 的 `2×` 线 `15:04.5` 且比账号最高 `20:14.332` 快 `8:44.8`），优先安排真实游戏完整打榜提交以刷新排名。
- 冲刺 `+50%` 线（`11:18.4`，目前仅差 `11.2s`）及更低时间的主要杠杆在 `hot-spots` 暴露出的两段关键路径：
  1. **降低 4 射线定位延迟**（当前占主机 `wait_for` `103.6s`）：评估多点并行稀疏格点一次定位中心与宽度的方案，并与首轮外环清土重叠；
  2. **进一步均衡锥内修复长尾**（当前占主机 `wait_for` `127.8s`）：按单层最大移动+放置耗时而非仅总块权切分大锥，并评估在保持每层支撑不变前提下减少层屏障 `num_items` 自旋节点数。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
