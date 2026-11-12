# 快速重置（`lb_fastest_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_reset.py](../../scripts/leaderboard/lb_fastest_reset.py)。公开账号最高 **41:47.696（#35）**；已有最好本地模拟 **41:19.106**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869903/)，榜单抓取时间 `2026-11-12T15:58:46.358099+00:00`，账号查询时间 `2026-11-12T15:58:46.358123+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

从原版1×1、零库存发展到伴生和8机。boost_stock跨原料订单保留作物及支撑，蛇形往返生产；Trees5、Watering5和实际供电后提前筹最终迷宫Weird，用联产Wood支付Carrots5/6和Watering6。中期两座4×4、四座6×6独立宫筹第2/3次机，末段八座5×5/M4宫筹百万Gold。16×16、D4前三蛇255实体，末蛇按缺口取235，正常换帽共得2002400 Bone后支付解锁。

完整三seed2464.635501042/2479.786027471/2492.895979468秒，均2479.105835994秒；request506前两轮短筛2504.565秒，正式三轮2498.140/2510.990/2513.958秒、均2507.696秒。

seed1累计边界：0→1173.27秒发展至Polyculture；1173.27→1236.69秒取得双机；1236.69→1330.69秒四机；1330.69→1542.82秒八机；1542.82→1957.80秒科技/原料投资包；1957.80→2114.17秒最终金币；2114.17→2464.635501秒完整恐龙结算和解锁。该段含混采与控制，不是各API纯耗时。

当前末段向日葵按花瓣整组达1600停止，骨头前最低400；三seed终点Wood约20332～22027、Power188.936～303.150，实机末Power146.57～247.14。Watering6多余水来自后续自动积累，肥料约287～292、Cactus19296、Bone2400、Gold40属于未回本投资或整批余量，不为清零额外做动作。

解锁Leaderboard实付2M Bone＋1M Gold；脚本unlock不检查UI父连线，但附加条件仍有效。骨头只允许一顶帽，其他机改高度会移除苹果，不安排并行农活。按每条(n²−1)²×2^(D−1)、真实苹果费用及整轮数比较D级数和地图，D5需要2592000 Cactus，已有成本账不支持只为少两条蛇购买。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 只提前双机，再补原科技 | 双机约883～902秒；三seed完整均2851.091秒，对当时2790.992秒 | 低产量/速度的筹资与后续补购回吐前缀领先 | [20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m34.665s_ground_early_two_guarded.py) |
| 低科技先伴生、推迟首次供电 | 缺肥代表2217.230秒退出；先供电P1完整2948.098秒 | 只证明这些固定支付顺序无收益，不否定所有早并行 | [20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_49m08.098s_ground_powered_poly_p1_infected.py) |
| 终点保留Mazes3、较早扩田或16机 | M3完整2877.175秒；历史16机包3081.834秒 | 少投资增加导航/重建，早买机增加Gold/Weird并挤掉供能 | [20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_sim_47m57.175s_ground_terminal_maze3.py) |
| 每单清场、整田批量备料 | 普通完整3504.220秒 | 丢掉未熟作物与自然伴生，已由保场订单替代 | [20261111_rejected_ground_bulk_basic.py](../../references/leaderboard_history/lb_fastest_reset/20261111_rejected_ground_bulk_basic.py) |
| 全科技向日葵批水/目标退出直接迁入 | 往返组合2752.542/2756.377秒，对当时采用2744.219秒 | 水库存竞争、低科技成本及完整时序不同；功能收益不能直接套整轮 | [20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-snake-solar-goal-water.py) |
| 统一四条250节 | seed1完整2511.468秒，对同前缀2501.429秒 | 每步计数开销抵消少吃果；只计末条缺口的235节版本才被采用 | [20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-dino-inline-all250.py) |
| 提早在水电前混采Weird | seed1完整2610.187秒，比同阶段父慢109.022秒 | 联产木头有用，但到货时点与当时速率不合适 | [20261112_rejected_followup_lb_fastest_reset-mixed-early.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-mixed-early.py) |
| 已有肥料催回访南瓜、购买F3催熟 | 三seed2522.040秒对2514.803秒；F3首seed2511.712秒慢10.546秒 | 催熟/感染/费用没有完整回本，只关闭所测政策 | [20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_followup_lb_fastest_reset-fertilizer-use.py) |
| 仙人掌窗口复用＋单调边界/仅缓存 | seed1完整2472.427480/2465.679293秒，对2464.635501秒 | measure少约43%仍未改善整轮，成熟与后续时序反馈须实测 | [20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py](../../references/leaderboard_history/lb_fastest_reset/20261112_rejected_sim_41m12.427s_reset_cactus_transfer_sources_window.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_fastest_reset/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_fastest_reset/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 补齐最快重置候选路线 | [20260424_v03_24db7f57.py](../../references/leaderboard_history/lb_fastest_reset/20260424_v03_24db7f57.py) |
| 2026-04-25 | 未记录 | 跑通最快重置阶段路线 | [20260425_v04_d6dc2b6e.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v04_d6dc2b6e.py) |
| 2026-04-25 | 未记录 | 拦截最快重置误判与非法语法 | [20260425_v05_071c0e74.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v05_071c0e74.py) |
| 2026-04-25 | 未记录 | 推进快速重置榜单策略 | [20260425_v06_1fbc7898.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v06_1fbc7898.py) |
| 2026-04-25 | 未记录 | 改进快速重置伴生产线 | [20260425_v07_55c10ac1.py](../../references/leaderboard_history/lb_fastest_reset/20260425_v07_55c10ac1.py) |
| 2026-04-26 | 未记录 | 迁入并验证外部最快重置候选 | [20260426_v08_1f586600.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v08_1f586600.py) |
| 2026-04-26 | 未记录 | 提前快速重置多机南瓜节奏 | [20260426_v09_c5cbe7b3.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v09_c5cbe7b3.py) |
| 2026-04-26 | 未记录 | 提前快速重置二级巨大农场 | [20260426_v10_6d9e7f57.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v10_6d9e7f57.py) |
| 2026-04-26 | 未记录 | 扩大快速重置金币批次 | [20260426_v11_da25aa36.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v11_da25aa36.py) |
| 2026-04-26 | 未记录 | 调整快速重置顺手补电地板 | [20260426_v12_b45afab6.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v12_b45afab6.py) |
| 2026-04-26 | 未记录 | 提高快速重置顺手补电阈值 | [20260426_v13_b0c7432f.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v13_b0c7432f.py) |
| 2026-04-26 | 未记录 | 提高快速重置补电稳定阈值 | [20260426_v14_56a1c015.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v14_56a1c015.py) |
| 2026-04-26 | 未记录 | 跳过快速重置金币空批次迷宫 | [20260426_v15_9a8cecf8.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v15_9a8cecf8.py) |
| 2026-04-26 | 未记录 | 修正快速重置金币收益估算 | [20260426_v16_e7b80a9f.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v16_e7b80a9f.py) |
| 2026-04-26 | 未记录 | 减少快速重置金币墙刷新 | [20260426_v17_61702cc1.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v17_61702cc1.py) |
| 2026-04-26 | 未记录 | 快速重置骨头阶段追苹果 | [20260426_v18_58c31f70.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v18_58c31f70.py) |
| 2026-04-26 | 未记录 | 采用快速重置肥料上限 | [20260426_v19_7f6fc675.py](../../references/leaderboard_history/lb_fastest_reset/20260426_v19_7f6fc675.py) |
| 2026-05-31 | 版本注记 168m48.299s | 调整：收敛 leaderboard 脚本真源 | [20260531_v20_168m48.299s_0224fb21.py](../../references/leaderboard_history/lb_fastest_reset/20260531_v20_168m48.299s_0224fb21.py) |
| 2026-10-27 | 53:43.604（2026-10-26，官方完整3轮，request 94）。 | 迁入七项实机上榜策略并记录完整统计 | [20261027_v21_53m43.604s_9d2d3c31.py](../../references/leaderboard_history/lb_fastest_reset/20261027_v21_53m43.604s_9d2d3c31.py) |
| 2026-10-27 | 52:15.911（2026-10-26，官方完整3轮，request 98）。 | 南瓜修补队列将快速重置缩短至52分15秒 | [20261027_v22_52m15.911s_ffe7fc79.py](../../references/leaderboard_history/lb_fastest_reset/20261027_v22_52m15.911s_ffe7fc79.py) |
| 2026-10-29 | 51:46.851（2026-10-28，官方完整3轮，request 182）。 | 快速重置骨头阶段迁入边界绕行 | [20261029_v23_51m46.851s_4ebac87d.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v23_51m46.851s_4ebac87d.py) |
| 2026-10-29 | 50:24.677（2026-10-28，官方完整3轮，request 185）。 | 快速重置提前补电覆盖南瓜与扩田供料 | [20261029_v24_50m24.677s_9bbe4daf.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v24_50m24.677s_9bbe4daf.py) |
| 2026-10-29 | 50:00.960（2026-10-28，官方完整3轮，request 188）。 | 快速重置仙人掌排序覆盖成熟等待 | [20261029_v25_50m00.960s_20f73959.py](../../references/leaderboard_history/lb_fastest_reset/20261029_v25_50m00.960s_20f73959.py) |
| 2026-11-11 | 未取得；C#原目标3seed均值2790.992秒（2026-11-11，当前策略未实机）。 | 调整双重置迷宫筹资与矿物投资路线 | [20261111_v26_46m30.992s_8ec59b43.py](../../references/leaderboard_history/lb_fastest_reset/20261111_v26_46m30.992s_8ec59b43.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值2751.646秒（2026-11-12，当前策略未实机）。 | 重置榜按原料订单保留伴生产区 | [20261112_v27_45m51.646s_425a5024.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v27_45m51.646s_425a5024.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值2744.219秒（2026-11-12，当前策略未实机）。 | 迁入重置榜常驻采集与分区复用 | [20261112_v28_45m44.219s_5f25fe9a.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v28_45m44.219s_5f25fe9a.py) |
| 2026-11-12 | 2703.337666667秒（2026-11-12，实机完整3轮）；C#原目标3seed均值2682.885秒。 | 迁入恐龙递归追果并完成快速重置实机 | [20261112_v29_44m42.885s_56b4d84d.py](../../references/leaderboard_history/lb_fastest_reset/20261112_v29_44m42.885s_56b4d84d.py) |

## 下一步优化方向

- 优先重算单机至首次伴生/无人机的生产组织，比较提前投资、少采和混合获取三条完整路径，按当前时点真实速率计价。
- 末田仙人掌只调库存阈值仍需第8田；若研究部分连通收获，需同时覆盖苹果、科技付款和平方产量，不把余额直接当省时。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
