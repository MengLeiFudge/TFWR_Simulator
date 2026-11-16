# 炸药·多机（`lb_dynamite`）

## 当前策略与成绩

当前脚本：[lb_dynamite.py](../../scripts/leaderboard/lb_dynamite.py)。公开账号最高 **14:21.783（#6）**，来自2026-11-16 request543 的9轮完整统计均值（最好13:44.353／最差15:12.719）；已有最好本地模拟 **13:41.035（完整盘吞吐外推）**，距当前 #1 **5:35.314（+144.9%）**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444631/)，榜单抓取时间 `2026-11-16T02:16:07.616607+00:00`，账号查询时间 `2026-11-16T02:16:07.616642+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

预建邻接表，32个区域独占开格，把局部确定推理和连续安全开挖都交给工人。相邻公开数字用剩余未知集合差推导SAFE/MINE，批末单调合并相容证明；全部工人回收后只正常结算一次。每盘重建事实，初始找层/覆盖准备及真实10M目标计时，不猜雷。

三seed固定30现实秒，共31盘正常结算，以初始化加已结算吞吐外推821.034545575秒；原10M未完整跑完。2026-11-09 request464正式9轮874.707888889秒。2026-11-16本轮原生对照均采用更紧的每例15墙钟秒预算，没有重跑或放宽旧30秒窗口。

当前工人已在本批安全队列耗尽后立即再次propagate，未等待下一次全局派机才推理；非零数字逐格唤醒是可比较的更激进代表，不能把已有区内循环误诊为缺失。原生模型 `Native/World.cs` 的GeneratePuzzle排除首挖周围3×3布雷，seed1前三盘首数字也均为0；零区传播清覆盖层，不能把尚未实际开挖的邻格一律视为已公开数字。跨区协作必须读取真正的煤灰数字，不取私有雷阵。

本轮公共煤灰常驻代表只读本区及两格边界的真实高度、地面和measure；空闲最多八趟巡检且设4游戏秒等待，所有外层循环有上限。seed1首盘同得318880，派机批数6→3，但正常结算32.89→71.92秒；100游戏秒基线已结算三盘879616，常驻只结算一盘318880。单纯消除屏障没有覆盖巡检成本，不采用。回执、冻结源和重建器见 `.codex/five-structures-20261115/`，不是全10M新成绩。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 中心放射等面积分区 | 相同前三盘879616，95.90秒对82.99秒，批数9/9/10对6/6/8 | 细长区域增加跨区信息交接，没有减少关键批次 | [20261111_rejected_s_radial.py](../../references/leaderboard_history/lb_dynamite/20261111_rejected_s_radial.py) |
| 物理雷标记常驻轮询 | 修正版80秒净167632、四盘完整结算 | 标记准备和外区实际读数费用过重；天然Rock与标记混淆的首版无效 | [20261108_rejected_persistent_state_v4.py](../../references/leaderboard_history/lb_dynamite/20261108_rejected_persistent_state_v4.py) |
| 主机前沿派发/集中缓存按列开格 | 120秒825984/562960；前沿前三盘100.481秒对92.550秒 | 减少派机被主机传播和重复批次抵消 | [20261108_rejected_active_frontier_v1.py](../../references/leaderboard_history/lb_dynamite/20261108_rejected_active_frontier_v1.py) |
| 树形归并、工人缓存 | 相同四盘118.225/116.422秒，对单调115.057秒 | 旧数字重发首版不收敛；修正后仍未减少足够费用 | [20261108_rejected_worker_cached_v2.py](../../references/leaderboard_history/lb_dynamite/20261108_rejected_worker_cached_v2.py) |
| 就地读邻煤灰、已开零区省略 | 前三盘90.149秒对83.024秒；零区四盘116.673秒对112.030秒 | 零扩张只清覆盖层，未自动公开邻格数字；省略没有减少同步批数 | [20261109_rejected_connected_zero_v2.py](../../references/leaderboard_history/lb_dynamite/20261109_rejected_connected_zero_v2.py) |
| 证明138雷后全局补SAFE | 相同四盘116.354秒对112.030秒，触发两次新增SAFE为0 | 全局集合维护无收益；单盘上限318880也限制纯增产路线 | [20261108_rejected_global_cap_v1.py](../../references/leaderboard_history/lb_dynamite/20261108_rejected_global_cap_v1.py) |
| 矩形转置、16工人、固定提前结算 | 转置共同20盘均慢1.26%；前三盘最佳保守收益约10.8k～13.3k/s | 降低并行或提前丢掉平方围雷收益，未达两倍线约14.9k/s | [20261110_rejected_regions_8x4.py](../../references/leaderboard_history/lb_dynamite/20261110_rejected_regions_8x4.py) |
| 无雷标的公共煤灰常驻巡检 | seed1首盘318880，71.92秒对32.89秒；100秒只结算一盘，对基线三盘 | 派机批数确实减少，未知边界反复走读增大关键路径；仅否定这个有限巡检代表 | [20261116_rejected_public_persistent.py](../../references/leaderboard_history/lb_dynamite/20261116_rejected_public_persistent.py) |
| 每个新非零数字后立即propagate并补安全队列 | seed1相同前两盘590896，65.31秒对54.55秒；首盘批数仍6 | 重复传播与队列维护费用增加，未减少全局批数 | 从Git `0102d33:scripts/leaderboard/lb_dynamite.py` 在 `clues.add(cell)` 后立即传播、枚举owned补SAFE，set去重；原始 `make_dynamite_immediate.py` 与回执在本轮.codex目录 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 6796.005秒（构建26462009，2轮官方完整统计；请求350）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_113m16.005s_6702ac6a.py](../../references/leaderboard_history/lb_dynamite/20261106_v01_113m16.005s_6702ac6a.py) |
| 2026-11-06 | 5561.376秒（构建26462009，2轮官方完整统计；请求367）。 | 炸药多机仅回访本列未知格并完成真源复验 | [20261106_v02_92m41.376s_3d9ced58.py](../../references/leaderboard_history/lb_dynamite/20261106_v02_92m41.376s_3d9ced58.py) |
| 2026-11-07 | 1093.692秒（本地原目标三seed均值；当前版本未实机验证）。 | 炸药多机分区推理并减少全局调度 | [20261107_v03_18m13.692s_2cb72225.py](../../references/leaderboard_history/lb_dynamite/20261107_v03_18m13.692s_2cb72225.py) |
| 2026-11-09 | 未取得（单调事实合并；本地固定窗口已验证）。 | 压缩炸药证明合并并记录非重置结构筛选 | [20261109_v04_d48ef4a7.py](../../references/leaderboard_history/lb_dynamite/20261109_v04_d48ef4a7.py) |

## 下一步优化方向

- 当前仍+144.9%。下一个跨区代表须先量出每次巡检拿到的新事实数、为一个新事实走的步数，避免再次用盲轮询换掉屏障；优先比较前沿触发的少量边界读取，而不是仅减少spawn次数。
- 保留原本已有效的局部连续推理；逐格即时传播的代表已关闭。新结构按相同完整盘净收益比较，不把本轮负例推成所有常驻协作不可能，也不靠超过单盘奖励上限的估产翻盘。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
