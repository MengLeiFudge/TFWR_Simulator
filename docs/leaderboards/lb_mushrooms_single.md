# 蘑菇·单机（`lb_mushrooms_single`）

## 当前策略与成绩

当前脚本：[lb_mushrooms_single.py](../../scripts/leaderboard/lb_mushrooms_single.py)。公开账号最高 **13:32.194（#5）**；已有最好本地模拟 **13:11.829**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444535/)，榜单抓取时间 `2026-11-11T09:12:45.338412+00:00`，账号查询时间 `2026-11-11T09:12:45.338412+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8六层场筛选，公开三格高度带和重力中转；只按实际颜色与高度作同色配对，遇非M接收柱不为固定同高关系额外下挖。顺次处理分区与层，保留采样柱，失败先收口再换场，目标30k Mushroom。

六层筛选三seed完整786.94773480/813.40401861/775.13565042秒，均791.82913461秒；seed2比同条件旧版慢4.255秒。旧版request473正式9轮812.194222222秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 双源确定配对队列 | 完整909.809017秒，move10176/dig3373/push3192 | 每对5.43move/1.80dig/1.70push，未兑现2move/1dig预算 | [20261109_rejected_mushroom_pair_queue_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_rejected_mushroom_pair_queue_v1.py) |
| 直接队列/全田就绪边/最高柱混合 | 完整941.855/944.217/1069.597秒 | 全田维护和开孔没有创造更多可兑现配对；最高柱代表API单独约583秒 | [20261108_rejected_mushroom_ready_edges_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_ready_edges_v1.py) |
| 双行输送/连续局部合并/三推定向滑块 | 1814.870/1481.578秒；三推预算到2617秒仅10768 | 搬运和全田规划太贵，失配材料与重复准备多 | [20261108_rejected_mushroom_routed_sliding_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_routed_sliding_v1.py) |
| 固定接收井/五格双向枢纽 | 完整1113.237/1563.424秒 | 局部颜色耗尽、频繁换片，平均动作预算未兑现 | [20261108_rejected_mushroom_bidirectional_hubs_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_bidirectional_hubs_v1.py) |
| 黑白格源接收/4格小田 | 完整2890.594/959.772秒 | 额外空巡和97次换片的准备抵消局部缩短 | [20261108_rejected_mushroom_small_world_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261108_rejected_mushroom_small_world_v1.py) |
| 十字自动揭盖/空接收柱 | 十字三seed828.444/843.154秒；空接收正式1344.643秒对1335.308秒 | 少挖损失配对机会，后者本地小收益未在正式样本确认 | [20261106_rejected_empty_receiver_26462009.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_rejected_empty_receiver_26462009.py) |
| 固定局部模板 | 完整953.632644秒 | 配对动作和供料利用率均未支持较小预算 | [20261109_rejected_mushroom_local_templates_v1.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_rejected_mushroom_local_templates_v1.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1335.308秒（构建26462009，6轮官方完整统计；请求349）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_22m15.308s_22bf18ce.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v01_22m15.308s_22bf18ce.py) |
| 2026-11-06 | 1164.739秒（构建26462009，7轮官方完整统计；请求378）。 | 蘑菇单机三格高度带完成整轮复验 | [20261106_v02_19m24.739s_af973d71.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v02_19m24.739s_af973d71.py) |
| 2026-11-09 | 13:32.194（2026-11-09，build26462009，官方完整9轮，request473）。 | 补齐蘑菇失败恢复并记录十二榜实机成绩 | [20261109_v03_13m32.194s_45bb4345.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_v03_13m32.194s_45bb4345.py) |

## 下一步优化方向

- 与多机共用配对逻辑的优化先核算每对真实动作与解释器，再完整30k目标确认；两榜只共用机制结论，不按机器数直接缩放成绩。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
