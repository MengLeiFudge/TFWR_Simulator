# 蘑菇·单机（`lb_mushrooms_single`）

## 当前策略与成绩

当前脚本：[lb_mushrooms_single.py](../../scripts/leaderboard/lb_mushrooms_single.py)。公开账号最高 **12:37.850（#6）**，来自2026-11-16 request540 的10轮完整统计均值（最好12:02.373／最差13:04.472）；当前本地模拟 **12:39.361（7200游戏秒场均会话10轮，标准误5.74秒，seed1-10，全部达标）**，距当前 #1 **4:22.952（+188.5%）**；基准仍取更快的账号记录 12:37.850。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444535/)，榜单抓取时间 `2026-11-16T02:16:07.559763+00:00`，账号查询时间 `2026-11-16T02:16:07.559792+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8六层场筛选，公开高度和重力中转；只按实际颜色与高度同色配对，遇非M接收柱不为固定同高关系额外下挖。采用分区工人自己揭盖及一次预建蛇行路线／邻格表，层内下一格直接move；保留单机ceiling−6搜索下界、原颜色缓存及feed结果复用。目标仍30k Mushroom，所有选场和初始化计时。

2026-11-16最终生产源seed0/1/123完整771.89777172/754.46442045/749.26373211秒，均758.54197476秒；同条件0102d33原版805.17072024/786.94773480/781.11148725秒，均791.07664743秒，分别缩短4.13%/4.13%/4.08%。逐seed最终产量30848/30016/30064完全相同，六例均正常完成原目标、无覆盖初始条件、仅余主机；原版Parser执行通过，每例15墙钟秒预算，最长不足2秒。

原始回执和冻结指纹见 `.codex/five-structures-20261115/mushroom-single-final-seed{0,1,123}.json` 及 `lb_mushrooms_single-paired-base-seed{0,1,123}.json`。旧seed1/2/3完整均791.82913461秒属于不同seed组合，不与本轮均值冒充同一配对；request473正式9轮812.194222222秒仍为历史实机。

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
| 两趟扫描，先配对后削峰 | seed1首个完整场2352/81.11秒，对原版2240/54.92秒；合并局部揭盖80.73秒 | 材料保留增加112，重复巡视多约26秒，净速率更差，不采用 | 从 `0102d33:scripts/leaderboard/lb_mushrooms_single.py` 的work_layer增加外层两趟循环，仅第二趟执行 `count == 0` 的dig；多机同构[代表](../../references/leaderboard_history/lb_mushrooms/20261116_rejected_retain_first_pass.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1335.308秒（构建26462009，6轮官方完整统计；请求349）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_22m15.308s_22bf18ce.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v01_22m15.308s_22bf18ce.py) |
| 2026-11-06 | 1164.739秒（构建26462009，7轮官方完整统计；请求378）。 | 蘑菇单机三格高度带完成整轮复验 | [20261106_v02_19m24.739s_af973d71.py](../../references/leaderboard_history/lb_mushrooms_single/20261106_v02_19m24.739s_af973d71.py) |
| 2026-11-09 | 13:32.194（2026-11-09，build26462009，官方完整9轮，request473）。 | 补齐蘑菇失败恢复并记录十二榜实机成绩 | [20261109_v03_13m32.194s_45bb4345.py](../../references/leaderboard_history/lb_mushrooms_single/20261109_v03_13m32.194s_45bb4345.py) |
| 2026-11-15 | 旧seed1/2/3完整均791.82913461秒。 | 六层筛选、feed结果缓存；本轮替换前的冻结实现 | [20261115_baseline_0102d33.py](../../references/leaderboard_history/lb_mushrooms_single/20261115_baseline_0102d33.py) |

## 下一步优化方向

- 当前仍+188.5%；优先研究每对实际动作更少的配对结构，保留失配块不能以增加全田空巡为代价。本轮两趟代表已否定，不无界调整同一方案。
- 固定路线及邻格表已采用；继续压缩读数前须列清push、dig、塌方的失效范围。与多机只共用机制结论，不按机器数缩放成绩，单机仍用完整30k目标验收。
- 2026-11-16 同口径配对对照（seed1-3，完整30k目标）：配对搜索先挑候选再配对，752.4/777.6/740.9秒，原版754.5/779.8/743.0秒，三轮同向快约2.1秒、解释器节点降0.6%，已采用；把 `work_layer` 已读柱顶与颜色下传（含在 `work_layer` 为蘑菇柱预取 `measure()`）反而多读一次、整轮 767.0/767.9/759.1秒，已否定。7200游戏秒场均口径下现版10轮12:39.361、上一版12:41.481，差2.1秒但小于5.7秒标准误，所以本版按配对证据采纳，不宣称会话级显著。
- 2026-11-16 `--hot-spots`：单机版≈6.1e3 tick／游戏秒，属机制等待受限，压动作几乎不省时；30k目标＝1,875对、812秒意味着每对约0.43秒主要花在等成熟与等位。下一步先统计每对的等待时长与可并发覆盖的对数，再决定扩覆盖还是减空巡。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
