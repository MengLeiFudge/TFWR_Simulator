# 恐龙（`lb_dinosaur`）

## 当前策略与成绩

当前脚本：[lb_dinosaur.py](../../scripts/leaderboard/lb_dinosaur.py)。账号公开纪录 **10:57.023（#20）**。2026-11-25 请求 `581` 的 11 轮完整统计均值 **10:57.023**，实际用时 333.2 秒。本地随机模拟均值 **10:37.741**。[进度总表](leaderboard_progress.md) · [公开快照](../../references/leaderboards/status_snapshot.md)

单机戴恐龙帽，前半程用交错网格追果，先走朝向目标的边，碰到蛇身或边界时转向。到 500 果后沿同一组边回到固定梳形环，再沿整行一次走完。整行固定移动由[母版及配方](../../scripts/templates/leaderboard/lb_dinosaur.codegen.json)生成。满盘换帽结算 33488928 Bone。

2026-11-25 原版初始场景，四批各 3 轮独立游戏随机，12/12 完整满盘、0 警告、0 丢输出，累计 7652.889 游戏秒。均值 637.741 秒，标准差 16.836 秒，95% 自适应置信区间半宽 17.498 秒，样本范围 609.318～678.678 秒。报告 `.codex/tmp/leaderboard-closeout/dinosaur-release-random-{1..4}.json`，源码 SHA256 `ad4d5538d67bfe46e14fa0f7c7b022a138f74318f9caacb5dd7bf78724660fd2`。

同条件固定 seed 1、2，存档原版本耗时 684.086／704.019 秒，改版 661.370／651.505 秒。旧版 seed 3 在 740.705 游戏秒触及 API 调用预算，新版 622.568 秒满盘。先前旧版随机抽样 11/12 完成，另有两次实机整场因一轮未完成而作废。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 多机同时戴恐龙帽/其他机铺作物约束苹果 | 机制不成立 | 第二顶有效帽报错；普通作物不排除苹果，改变同高连通区可能移除苹果 | 机制判定，无候选代码 |
| 两轮750或近满尾重开 | 两轮代表1564.522秒；旧256→769尾阶段477.347秒 | 平方收益损失和重复启动过重，主要费用发生在中段，免费末尾也不能补齐差距 | [20261108_rejected_partial_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_partial_v1.py) |
| 直段逐果更新目标 | 完整932.927998秒，对旧775.380425秒 | 少移动未覆盖解释器约309.406秒；未兑现原预算 | [20261108_rejected_event_segments_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_event_segments_v1.py) |
| 吃果立即结束后段直列、横向入场 | 前者800秒仍未结算；后者43.126秒仅11552 Bone | 身体/自由区没有持续恢复保证，局部move合法不能证明整轮 | [20261109_rejected_adaptive_fill_v1.py](../../references/leaderboard_history/lb_dinosaur/20261109_rejected_adaptive_fill_v1.py) |
| 固定行蛇形回路接入 | 71.377秒仅4608 Bone；干净起步66.940秒仅288 Bone | 闭环接入与当前身体冲突，不是有效完成时间 | [20261110_rejected_row_cycle.py](../../references/leaderboard_history/lb_dinosaur/20261110_rejected_row_cycle.py) |
| 动态安全Hamilton换边 | 121.675秒组件仅4果，父同窗52果 | 维护回路和搜索太贵，安全不等于快 | [20261030_rejected_dynamic_cycle.py](../../references/leaderboard_history/lb_dinosaur/20261030_rejected_dynamic_cycle.py) |
| 仅改真实半盘计数 | 完整778.249秒，对旧775.380秒 | 该seed观察计数与真实尾长一致，额外统计未带来路线收益 | [20261108_rejected_actual_half_v1.py](../../references/leaderboard_history/lb_dinosaur/20261108_rejected_actual_half_v1.py) |
| 递归追果延后到3/4盘 | seed1完整866.18325213秒、33488928 Bone，对同条件684.08607339秒 | 到切换点已794.37秒；原递归恢复费用上升，不能仅延后阈值 | 从Git `0102d33:scripts/leaderboard/lb_dinosaur.py`把 `turn_point = A // 2` 改为 `A * 3 // 4` 可重建 |
| 真实尾事件表＋后段向北短切 | seed1到1200.05秒仅697实体，换帽结算15545888 Bone；补跑原路线到15墙钟秒仍未达目标 | 包含1024步身体整形、真实尾跳跃和64格余量；1498次短切未兑现完整周期，不计模拟成绩 | [20261116_rejected_tail_shortcuts.py](../../references/leaderboard_history/lb_dinosaur/20261116_rejected_tail_shortcuts.py) |
| 交错网格 v3（整行展开，未合并前段连续直行） | seed 1～12 均满盘。v3 均值 661.981 秒，v4 652.732 秒 | v4 在 11/12 个配对种子上更快，平均节省 9.248 秒，配对标准误 3.592 秒。seed 5 的 v4 慢 28.719 秒 | `.codex/tmp/leaderboard-closeout/dinosaur-v{3,4}-seeds*.json` 与两份 seed 1～3 报告 |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_dinosaur/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_dinosaur/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v03_8deede45.py](../../references/leaderboard_history/lb_dinosaur/20260424_v03_8deede45.py) |
| 2026-04-25 | 未记录 | 迁入恐龙榜外部候选 | [20260425_v04_e295d1d9.py](../../references/leaderboard_history/lb_dinosaur/20260425_v04_e295d1d9.py) |
| 2026-05-31 | 版本注记 15m26.484s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_15m26.484s_0224fb21.py](../../references/leaderboard_history/lb_dinosaur/20260531_v05_15m26.484s_0224fb21.py) |
| 2026-06-09 | 版本注记 15m26.484s | 减少恐龙非目标格测量 | [20260609_v06_15m26.484s_4a0dfea6.py](../../references/leaderboard_history/lb_dinosaur/20260609_v06_15m26.484s_4a0dfea6.py) |
| 2026-06-09 | 版本注记 15m26.484s | 减少恐龙坐标回读 | [20260609_v07_15m26.484s_075dbef9.py](../../references/leaderboard_history/lb_dinosaur/20260609_v07_15m26.484s_075dbef9.py) |
| 2026-06-09 | 版本注记 15m26.484s | 压缩恐龙移动热路径 | [20260609_v08_15m26.484s_b7c81abc.py](../../references/leaderboard_history/lb_dinosaur/20260609_v08_15m26.484s_b7c81abc.py) |
| 2026-07-23 | 版本注记 15m26.484s | 恐龙榜算法更新 | [20260723_v09_15m26.484s_55514a27.py](../../references/leaderboard_history/lb_dinosaur/20260723_v09_15m26.484s_55514a27.py) |
| 2026-10-27 | 14:46.835（官方完整统计9轮）；本地seed1 902.299838秒，短时2轮872.558秒。 | 恐龙失败清理并完成官方打榜 | [20261027_v10_14m46.835s_9be4f1ce.py](../../references/leaderboard_history/lb_dinosaur/20261027_v10_14m46.835s_9be4f1ce.py) |
| 2026-10-29 | 13:38.714（官方完整9轮，request159）；本地三seed819.568663秒，短时2轮811.857秒。 | 采用恐龙边界绕行与后期填隙策略 | [20261029_v11_13m38.714s_0876dded.py](../../references/leaderboard_history/lb_dinosaur/20261029_v11_13m38.714s_0876dded.py) |
| 2026-10-30 | 13:20.066（2026-10-30，官方完整9轮，request226）；十果追果后西列整形交接。 | 恐龙短蛇追果与西列整形完成正式打榜 | [20261030_v12_13m20.066s_f66370a4.py](../../references/leaderboard_history/lb_dinosaur/20261030_v12_13m20.066s_f66370a4.py) |
| 2026-11-12 | 本版本尚未取得实机完整统计；仅有本地模拟对照。 | 迁入恐龙递归分区并提高骨头生产速率 | [20261112_v13_13bcd149.py](../../references/leaderboard_history/lb_dinosaur/20261112_v13_13bcd149.py) |
| 2026-11-12 | 同模型固定 seed 1、2 完成于 684.086／704.019 秒，seed 3 到 API 调用上限 | 递归矩形追果和后半盘固定回路 | [旧存档同版 ead31f5](../../references/leaderboard_history/lb_dinosaur/20261112_v14_ead31f5.py) |
| 2026-11-25 | 实机 10:57.023（11 轮，请求 581），模拟 10:37.741 | 交错网格追果与梳形回路 | 当前 [lb_dinosaur.py](../../scripts/leaderboard/lb_dinosaur.py) |

## 下一步优化方向

- 后续短切必须记录真实身体顺序。走过捷径后，身体的回路编号有空洞，不能用 `tail = head - length` 代替真实尾位置；苹果也可能出现在这些空洞中。局部不撞身不能证明最终能填满。
- 递归直出需证明直出路径、父区域恢复和未来目标均可达；所提 `id-(x+y) >= id-cnt` 只化为 `cnt >= x+y`，没有编码实际身体占格，不能直接作为安全上界。先用真实身体轨迹核对一条可恢复的退出代表，再写候选，不盲改判断。
- 外部检索按状态表示、允许变形和恢复条件区分算法；本轮只否定上述两个具体实现，未否定可恢复区域短切这一类方向。原始回执及重建器在 `.codex/five-structures-20261115/`（原始材料已于 2026-11-17 清理），所有候选每例15墙钟秒，不放宽预算。
- 满速有电的单机每 tick 约 0.165 ms，理论上限约 6075 t/s。用动作费用、有效工时和移动轨迹拆分热点。源码见 `Native/Simulation.cs` 的 `ChangeExecutionSpeed` 与 `Native/Farm.cs` 的 `MaxSpeedFactor`。
- `Dinosaur.OnMove` 每吃一个苹果降低移动单价，整数截断后最低 33t。后半盘重点削减每果走过的格数，并验证修改后还能回到可填满的回路。
- 正式资源榜的 `randomSnake` 使用 `BufferedCryptoRandom`，按 `TryChooseTarget` 从可选空格抽取。固定 seed 用于本地配对，正式策略只能根据当前苹果和蛇身走位。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
