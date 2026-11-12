# 炸药·多机（`lb_dynamite`）

## 当前策略与成绩

当前脚本：[lb_dynamite.py](../../scripts/leaderboard/lb_dynamite.py)。公开账号最高 **14:34.708（#6）**；已有最好本地模拟 **13:41.035**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444631/)，榜单抓取时间 `2026-11-11T09:12:46.916920+00:00`，账号查询时间 `2026-11-11T09:12:46.916920+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

预建邻接表，32个区域独占开格，把局部确定推理和连续安全开挖都交给工人。相邻公开数字用剩余未知集合差推导SAFE/MINE，批末单调合并相容证明；全部工人回收后只正常结算一次。每盘重建事实，初始找层/覆盖准备及真实10M目标计时，不猜雷。

三seed固定30现实秒，共31盘正常结算，以初始化加已结算吞吐外推821.034545575秒；原10M未完整跑完。2026-11-09 request464正式9轮874.707888889秒。

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

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 6796.005秒（构建26462009，2轮官方完整统计；请求350）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_113m16.005s_6702ac6a.py](../../references/leaderboard_history/lb_dynamite/20261106_v01_113m16.005s_6702ac6a.py) |
| 2026-11-06 | 5561.376秒（构建26462009，2轮官方完整统计；请求367）。 | 炸药多机仅回访本列未知格并完成真源复验 | [20261106_v02_92m41.376s_3d9ced58.py](../../references/leaderboard_history/lb_dynamite/20261106_v02_92m41.376s_3d9ced58.py) |
| 2026-11-07 | 1093.692秒（本地原目标三seed均值；当前版本未实机验证）。 | 炸药多机分区推理并减少全局调度 | [20261107_v03_18m13.692s_2cb72225.py](../../references/leaderboard_history/lb_dynamite/20261107_v03_18m13.692s_2cb72225.py) |
| 2026-11-09 | 未取得（单调事实合并；本地固定窗口已验证）。 | 压缩炸药证明合并并记录非重置结构筛选 | [20261109_v04_d48ef4a7.py](../../references/leaderboard_history/lb_dynamite/20261109_v04_d48ef4a7.py) |

## 下一步优化方向

- 比较根据真实煤灰状态跨区读取的常驻协作，先计移动和确定信息的传播成本；更重闭包不能靠超过单盘奖励上限解决整轮。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
