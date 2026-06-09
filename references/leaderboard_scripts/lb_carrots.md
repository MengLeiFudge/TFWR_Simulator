# lb_carrots

## 榜单目标

- 目标资源：`Items.Carrot`
- 多无人机路线
- 当前脚本目标数量为 `2000000000`

## 收益机制说明

- 胡萝卜榜的关键不是“普通成熟后能不能收”，而是“收的时候有没有吃到伴生”。
- 你补充的当前关键事实是：
  - 胡萝卜伴生命中时，产出会直接放大到 `160` 倍
  - 因此对 leaderboard 语境下的胡萝卜来说，没伴生基本就等于没收益
- 这意味着胡萝卜不是纯吞吐榜，而是重 companion 兑现榜。
- 反编译源码 `Growable#ChooseCompanion()` 还有一个关键限制：
  - companion 类型会在 `grass / bush / carrot / tree` 中随机
  - 但如果随机出的类型等于当前作物本身，会重新随机
  - 因此“胡萝卜的 companion 是胡萝卜”这条链式假设不成立
  - 胡萝卜真实候选 companion 是 `Grass / Bush / Tree`
- 2026-05-31 纠偏：
  - `gamesave/__builtins__.py` 文档显示 `Entities.Grass` 可种在 `grassland or soil`
  - 所以旧结论“胡萝卜的 Grass companion 因地块冲突物理上无效”不成立
  - 真正的限制是：同一 support 坐标一次只能放一种实体；静态 `Grass-only`、`Bush-only`、`Tree-only` 都只是同概率替换
  - 要把成功率从单类型的约 `1/3` 提高到多类型，必须有低成本多类型承接或接力结构，而不是把 support 从 Bush 简单换成 Grass / Tree

## 当前基线

- 当前默认入口：`lb_carrots()`
- 当前 repo 路线：32x32 世界，32 个 `4x8` 周期 tile；每个 tile 用 1 台无人机维护 8 个折线胡萝卜锚点 `(0,0)..(0,4)` + `(1,4)..(1,6)`，其余 24 格为固定 `Bush` support，只接受 `Bush` 且拒绝落到任意胡萝卜锚点的 companion。
- 当前版本复跑时间：2026-06-08 请求 `649` 有效六轮 `4:32.943` / `4:34.843` / `4:36.712` / `4:34.296` / `4:33.507` / `4:33.581`，稳定均值 `4:34.314`；后续 `finished=false` 取消摘要不作为成绩。
- 旧八锚点竖列版本时间：2026-06-08 请求 `632` 有效两轮 `4:41.630` / `4:41.545`，稳定均值 `4:41.588`。
- 旧六锚点 tile 版本时间：2026-06-08 请求 `630` 有效两轮 `4:45.820` / `4:46.041`，稳定均值 `4:45.931`。
- 旧双锚点版本时间：2026-05-30 请求 `612` 有效两轮 `9:33.732` / `9:37.057`，稳定均值 `9:35.395`。
- 历史可靠真实时间：请求 `308` 有效两轮 `9:34.777` / `9:34.687`，均值 `9:34.732`。
- 旧 `main1()` 是 32 台线程每机一行、整图全种胡萝卜的纯吞吐路线；`main2()` 是 16 个低冲突单锚点伴生候选，已被 `main3()` 双胡萝卜单元替代。
- 2026-04-24 真实验证：当前 `main1` 纯吞吐路线 45 秒窗口无完成轮次，协调器返回 `leaderboard finished without completed runs`
- 证据来源：
  - `lb_carrots.py` 当前实现
  - 真实请求 `308`
  - 你本轮对收益机制的校正

## 通用注意事项下的榜单特化

- 胡萝卜榜必须把 companion 兑现率当成第一优先级，而不是把它当可有可无的附加收益
- 但 companion 不是“什么都接”：
  - `Grass / Bush / Tree` 都能落地，但静态 support 必须类型匹配
  - 只有当额外移动、改种、回程和 support 改写成本低于 reroll 成本时，放开多类型才值得
- 多机路线的关键不是简单扩格子，而是想办法用多机把 companion 链接起来，而不是让每台机都做孤立的单格循环

## 当前版本结论

- `main1`
  - 当前 repo 版本把多机胡萝卜写成了“满图纯吞吐”路线
  - 但按当前已确认机制，这条理解本身是不对的：胡萝卜必须尽量吃伴生，不能把“自然命中即赚到”当主思路
  - 2026-04-24 真实验证 45 秒窗口无完成轮次；它连可用短窗口基线都不能提供
- `main2`
  - 16 个低冲突单锚点 companion 候选
  - 采用局部 `Bush` support，不再逐格长距离回头补支撑
  - 方向正确，但锚点密度偏低，最终被 `main3()` 的 32 个双胡萝卜单元替代
- `main3`
  - 旧默认 companion 路线
  - 结构仿照草 / 木榜的伴生单元，但改为每个单元两个胡萝卜格共用一圈静态 `Bush` support
  - 两个胡萝卜位交替 reroll，减少单锚点成熟等待空档；水阈值提升到 `>512 / >256 / >128`，避免 32 线程低水量刷警告
  - 2026-05-30 当前版本复跑请求 `612` 有效两轮：`9:33.732` / `9:37.057`，稳定均值 `9:35.395`
  - 结论：稳定兑现 `Bush` companion 已能从“无可靠完成轮”推进到 10 分钟内，但已被 2026-06-08 的 `4x8` / 6 锚点周期 tile 路线替代
- `lb_carrots()` 4x8 六锚点周期 tile
  - 2026-06-08 的阶段性刷新路线，已被 8 锚点周期 tile 替代。
  - 结构：32 个 `4x8` tile，每个 tile 1 台无人机负责同一列的 6 个胡萝卜锚点；tile 内其余 26 格预置为 `Bush` support。
  - 仍然只兑现 `Bush` companion，不解决多类型 companion 约 `1/3` 命中率上限；收益来自把总胡萝卜锚点从 `64` 提高到 `192`，用更高锚点密度抵消单锚点成功率下降。
  - 离线筛选脚本 `.codex/tests/carrot_companion_layout_screen.py` 估算：周期可平铺 `4x8` / 6 锚点静态 Bush 候选的几何上限约为旧双锚点路线的 `2.57x`，估算 `3:44.307`，真实会被移动、成熟等待和 reroll 开销拉低。
  - 2026-06-08 请求 `630` 有效两轮：`4:45.820` / `4:46.041`，稳定均值 `4:45.931`；取消摘要 `[lb_carrots] finished=false runs=3 average=3:16.067` 不作为成绩。
  - 结论：真实刷新旧双锚点稳定均值 `9:35.395 -> 4:45.931`，但探针显示仍有约三成访问撞上未成熟，后续被 8 锚点周期 tile 替代。
- `lb_carrots()` 4x8 八锚点周期 tile
  - 当前默认路线为折线 8 锚点；旧竖列 8 锚点已被替代。
  - 结构：32 个 `4x8` tile，每个 tile 1 台无人机负责 8 个胡萝卜锚点；旧竖列版用第一列 8 格，当前折线版用 `(0,0)..(0,4)` + `(1,4)..(1,6)`；tile 内其余 24 格预置为 `Bush` support。
  - 离线几何估算：8 锚点平均可用 Bush 坐标约 `18/24`，Bush-only 成功率约 `25%`，但总胡萝卜锚点增加到 `256`，相对旧双锚点几何速率约 `3.13x`，估算 `3:03.807`。
  - 六锚点探针请求 `631` 显示首 tile 结束时每锚点约 `57~76` 次未成熟等待，说明继续增加锚点有理论依据。
  - 2026-06-08 请求 `632` 有效两轮：`4:41.630` / `4:41.545`，稳定均值 `4:41.588`；取消摘要 `[lb_carrots] finished=false runs=3 average=3:11.168` 不作为成绩。
  - 折线 8 锚点候选：仍为 `4x8` tile 和 `256` 总锚点，但锚点改为 `(0,0)..(0,4)` + `(1,4)..(1,6)`；离线几何筛选显示 Bush-only 成功率约 `26.4%`，相对旧双锚点几何速率约 `3.30x`，估算 `2:54.133`。
  - 2026-06-08 请求 `633` 有效两轮：`4:34.453` / `4:34.363`，稳定均值 `4:34.408`；取消摘要 `[lb_carrots] finished=false runs=3 average=3:06.889` 不作为成绩。
  - 2026-06-08 中等激进补水阈值候选：`water_carrot_anchor()` 从 `>512/>256/>128` 调整为 `>384/>192/>64`，不改锚点布局和 Bush-only companion 条件。请求 `648` 两轮 `4:34.492` / `4:34.218`，均值 `4:34.355`；因差距极小，追加请求 `649` 六轮 `4:32.943` / `4:34.843` / `4:36.712` / `4:34.296` / `4:33.507` / `4:33.581`，均值 `4:34.314`。
  - 结论：折线 8 锚点稳定刷新竖列 8 锚点 `4:41.588 -> 4:34.408`，中等激进补水阈值继续小幅推进到 `4:34.314`，保留为当前默认；收益来自减少 companion 落到锚点的 blocked 坐标并略压未成熟等待，仍未解决静态单类型 support 的 `Grass / Tree` 利用率问题。
- 2026-06-10 删除 progress / 统计计数候选：
  - 代码候选：删除 `harvest_count`、`reroll_count`、`last_log_carrots` 和 `100M` progress 输出；保留 `done` 输出、折线 8 锚点、静态 Bush support、Bush-only companion 接受条件和补水阈值。
  - 这不改变当前 Bush-only 伴生策略，只减少每次锚点收割 / reroll 路径上的观测计数和参数传递。
  - 验证：`python3 -m py_compile references/leaderboard_scripts/lb_carrots.py` 通过。
  - 真实游戏当前最近 request `730` 仍为 `game_tick=0` timeout，暂未能跑完成轮；文件头成绩不更新。
  - 风险：删除后不能从脚本 progress 输出直接看到 `harvest / reroll` 分布；若实机退化或需要继续分析瓶颈，需临时恢复统计探针。
- `lb_carrots()` 4x8 十锚点 staircase
  - 离线几何筛选：`4x8` tile，锚点为 `(0,0),(0,1),(0,2),(1,2),(1,3),(1,4),(2,4),(2,5),(2,6),(3,6)`；总锚点 `320`，Bush-only 成功率约 `25.6%`，相对旧双锚点几何速率约 `4.00x`，估算 `2:23.849`。
  - 2026-06-08 请求 `634` 有效两轮：`4:40.347` / `4:41.281`，稳定均值 `4:40.814`；取消摘要 `[lb_carrots] finished=false runs=3 average=3:08.316` 不作为成绩。
  - 结论：慢于当前折线 8 锚点 `4:34.314`，失败实现不保留在 `.py`。十锚点虽然增加锚点数量，但更长路径、更多跨列移动和更低单锚点 Bush 成功率抵消了理论收益；后续不要只按静态几何上限继续加密锚点。
- 静态锚点路径筛选
  - 2026-06-08 `.codex/tests/carrot_static_path_screen.py` 在 4x8 tile 内枚举 8-10 锚点连通布局，并用当前 8 锚点 request `649` 与失败 10 锚点 request `634` 校准路径惩罚。
  - 筛选结果：最佳仍是一批与当前折线 8 锚点等价的 8 锚点布局，估算 `4:34.314`；第一个 9 锚点候选估算 `4:37.864`，已经慢于当前。
  - 结论：当前不继续做静态锚点加密或 8 锚点形状平替实机；除非新布局能同时降低成熟等待 / reroll，而不是只提高锚点数。
- 折线 8 锚点瓶颈探针
  - 2026-06-08 请求 `635` 探针版有效两轮：`4:34.687` / `4:35.182`，稳定均值 `4:34.935`；探针版不作为刷新成绩，代码已回退并重新同步正式版到 `gamesave/`。
  - 首轮首 tile：`ah=[97,104,99,104,103,100,97,102]`、`aw=[20,13,18,13,13,16,19,14]`、`ar=[210,284,242,292,299,258,197,263]`、`grass=901`、`tree=946`、`bush_ok=930`、`bush_blocked=198`。
  - 第二轮首 tile：`ah=[99,100,94,101,99,101,96,90]`、`aw=[12,11,17,10,12,10,15,20]`、`ar=[219,248,335,312,269,253,281,216]`、`grass=974`、`tree=959`、`bush_ok=886`、`bush_blocked=200`。
  - 聚合判断：非 Bush 请求占全部 companion 样本约 `62%~64%`；Bush-blocked 只占 Bush 请求约 `17.6%~18.4%`；未成熟等待约 `12%~13.5%`。下一轮不要继续加密静态锚点或只压 blocked，应优先评估低成本承接 `Grass / Tree` 的动态 helper / 接力结构。
- 动态 support 预算筛选
  - 2026-06-08 `.codex/tests/carrot_dynamic_helper_budget.py` 只做离线动作预算；成功 `move()` / `harvest()` / `plant()` 按 `200` ticks，`get_companion()` 按 `1` tick，support 类型不匹配时按往返、移除旧 support、种新 support 计算。
  - 周期跨 tile 理想动态承接 distance<=3 估算 `4:16.198`，但需要跨到邻居 tile 改写 support；这会破坏当前静态 Bush-only 能跨 tile 无冲突成立的前提，结果不可解释。
  - 安全的本 tile 内同无人机动态改写 distance<=3 估算 `5:32.201`，distance<=1 / <=2 更慢，均弱于当前折线 8 锚点 `4:34.314`。
  - helper relay 预算筛选：`.codex/tests/carrot_helper_relay_budget.py` 估算 16 个 anchor + 16 个 helper 的 current-shape relay 约 `2:44.975`，但跨 tile support 请求约 `46.7%`，忽略了真实成熟等待、请求顺序扰动和互相覆盖。
  - 2026-06-08 request `653/654` 临时实现 helper relay 后启动即失败；`output.txt` 报 `Error: get_drone_id 从未被定义。在使用变量之前必须先给它赋值。`，而当前真实 `Save0/__builtins__.py` 没有 `get_drone_id` / `send` / `receive` 定义。
  - 2026-06-09 API 复核：反编译 `Core.decompiled.cs` 中有 `Send()` / `Receive()` / `GetDroneId()` 方法体和 reset unlock 名称，但 `BuiltinFunctions.functionList` 只注册到 `spawn_drone` / `num_drones` / `max_drones` / `wait_for` / `has_finished`，没有把 `get_drone_id` / `send` / `receive` 放进当前脚本函数表；因此不能把隐藏方法体当作当前 Save0 可用 API。
  - 2026-06-08 非消息接力复核：反编译 `SpawnDrone` 会 `DeepCopy` 被启动函数和 `parentScope`，再给新 drone 建独立 `Scope`；因此脚本全局 `list` / `dict` 也不能作为 anchor/helper 间运行时共享队列。
  - 结论：当前游戏脚本可用 API 下，不能依赖无人机间消息通信或全局共享队列实现 helper relay；该失败候选已从 `.py` 回退并重新同步正式折线 8 锚点版本到 `gamesave/`。后续只有确认当前 Save0 暴露数字 drone id 与消息 API，或找到完全不需要运行时通信的同步接力结构，才重新评估动态 helper / 接力。
- spawn-on-demand helper 对照：
  - 机制依据：当前 `Save0/__builtins__.py` 虽然没有 `send / receive`，但有 `spawn_drone(task, *args)` 和 `wait_for(handle)`；因此可测试 16 个 anchor tile 留 16 个空 drone 位，每次 companion 请求临时 spawn helper 写 support，anchor 等待后收割。
  - 离线预算 `.codex/tests/carrot_spawn_helper_budget.py` 在计入 `SpawnDrone` `200t` 成本后，10-anchor `4x8` 纸面估算 `2:30.101`，看似明显快于当前 `4:34.314`。
  - 实机 request `670` 临时实现 16 tile / 10 anchor / spawn helper：两轮 `11:03.359` / `11:05.676`，稳定均值 `11:04.518`，明显慢于当前。
  - 运行统计显示 helper 机制本身可用但等待成本极高：第二轮 `helper_request=1951`、`helper_success=1951`、`helper_fail=0`、`helper_no_slot=0`。
  - 结论：按请求临时 spawn 并 `wait_for()` helper 会打穿并行吞吐；不再作为实机候选。后续 helper 必须是无需 anchor 阻塞等待、且无需不可用通信 API 的结构，否则继续暂缓。
- 物理 mailbox helper 预算：
  - 2026-06-09 `.codex/tests/carrot_physical_mailbox_budget.py` 检查不依赖 `send/receive` 的 world-state 信号方案：anchor 用实体格写请求，helper 解码后写 support，anchor 固定等待后收割。
  - 前提仍然需要把 32 个 active tile 降成 16 个 anchor tile + 16 个 helper 位；如果 helper 只盲扫 support 且 anchor 不等待，类型仍不同步，估算退到 `9:08.628`。
  - 如果 anchor 等待 helper 的类型轮换，2 类型 / 3 类型半周期等待估算约 `506` 分钟，完全不成立。
  - 即使给物理 mailbox 极乐观实现，1 个信号格、support 距离 1、只写 Grass 的固定等待上界也为 `30:18.593`，远慢于当前；更多信号格或更远 support 会继续恶化。
  - 结论：不实机物理 mailbox helper。没有真实消息 API 或共享状态时，用世界实体格编码请求 / 坐标 / 完成信号的动作和等待成本远高于 reroll。
- 非通信定时 helper 预算：
  - 2026-06-09 `.codex/tests/carrot_noncomm_schedule_budget.py` 检查“helper 不知道 anchor 当前 companion 请求，只周期性把 support 格轮换成 `Grass / Bush / Tree`”的剩余接力方向。
  - 在当前 `4x8` tile / 8 锚点 / 24 support 格下，nearest-neighbor support 循环需要 `26` 步移动；每轮改写全部 support 的下界约 `14800t`，三类型轮换周期约 `44400t`。
  - 如果 anchor 不等待，support 类型和随机 companion 请求独立，命中率仍接近静态单类型的 `1/3`；如果 anchor 等到目标类型，平均等待约 `22200t`，是当前 Bush-only 期望 reroll 成本 `800t` 的 `27.8x`。
  - 结论：不实机非通信定时 helper；真正候选仍必须有通信 / 共享状态，或 support writer 正好在请求格时能零等待承接。
- periodic same-drone dynamic support probe
  - 2026-06-08 临时在当前折线 8 锚点版本上实现同无人机动态承接：companion 坐标不是 carrot anchor 时，当前无人机移动到 companion 坐标，把 support 改成请求的 `Grass / Bush / Tree`，再回锚点收割；不使用通信 API，不使用 spawn helper，不改锚点和补水阈值。
  - request `674` 两轮 `5:51.064` / `5:50.618`，稳定均值 `5:50.841`，明显慢于当前 `4:34.314`。
  - probe 输出显示每轮 dynamic rewrite 约 `827 / 835` 次，dynamic fail 为 `1 / 0`；机制可运行，但大量跨 support 往返和改写动作把纸面收益吃掉。
  - 结论：当前 4x8 周期结构下，不再做“本机 periodic 动态改写 support”实机；后续若重开动态承接，必须先有无需长距离往返、无需阻塞等待、且能处理跨 tile support 归属的结构。
- adaptive no-restore support 筛选
  - 2026-06-09 `.codex/tests/carrot_adaptive_support_markov_screen.py` 检查“support 格保留最近一次被写入的 `Grass / Bush / Tree` 类型，不恢复 Bush”的剩余方向。
  - 只记忆不改写时，下一次 companion 请求类型仍独立随机；per-cell 类型命中率不会超过 `1/3`，不能提高当前静态单类型上限。
  - `wrap-tile rewrite mismatch` 估算 `4:16.111`，但该上界依赖当前无人机跨 tile 改写邻居 support，会破坏一 tile 一 owner 的约束，不进实机。
  - `own-tile rewrite mismatch` 是写入安全版本，估算 `5:32.087`，慢于当前 `4:34.314`；这也与 request `674` 同无人机动态改写实机 `5:50.841` 的方向一致。
  - 结论：不实机 adaptive no-restore support；后续不要再按“support 记忆最近类型 / 不恢复 Bush”推进，除非出现能安全跨 tile 写入且不破坏 owner 的同步结构。
- zero-extra deferred support 筛选
  - 2026-06-09 `.codex/tests/carrot_deferred_zero_extra_support_screen.py` 检查“同无人机不阻塞 anchor、不通信，只在后续正常锚点路径自然经过 support 格时顺手改写，下一圈再兑现”的候选。
  - 当前锚点顺序的乐观上界：非 Bush 延迟命中只增加 `32` 个事件，success `26.3889% -> 31.9444%`，Monte Carlo 计入 support 当前类型与 pending 冲突后估算 `4:15.674`，不足以进入实机。
  - 同移动步数内最佳顺序为 `((0,0),(1,4),(1,5),(1,6),(0,4),(0,3),(0,2),(0,1))`，几何上界 success `26.3889% -> 42.0139%`；Monte Carlo 计入类型状态、pending 覆盖、重刷和改写成本后估算 `3:47.089`，略快于 `1.2x` 线 `3:48.797`。
  - 2026-06-09 续筛修正：原 `3:47.089` 来自周期 tile 折叠模型，隐含“跨 tile support 类型可预测”。真实 32 个 tile 独立随机运行时，一个 tile 改写 support 会破坏邻 tile 对跨 tile Bush support 的假设；若改为安全的 `own-tile only`，同移动步数最佳 Monte Carlo 退到 `5:56.246`。
  - 结论：不改 `lb_carrots.py`，也不在游戏恢复后短跑该候选。除非先证明跨 tile support 状态可预测 / 可同步，或者设计出不影响邻 tile 静态 Bush 成功率的零等待 writer，否则 Carrots 暂停继续实机。
- private writer / immutable Bush hybrid 筛选
  - 2026-06-10 `.codex/tests/carrot_hybrid_private_writer_screen.py` 复核上一条的中间模型：只允许本 tile 内、路线自然经过的 support 被当前无人机改写；跨 tile 只接受不可变 Bush support，不假设跨 tile support 状态可预测。
  - `timeout 60s python3 .codex/tests/carrot_hybrid_private_writer_screen.py` 约 `6.3s` 完成，`py_compile` 通过。
  - 解析模型里最佳同移动步数顺序仍是 `((0,0),(1,4),(1,5),(1,6),(0,4),(0,3),(0,2),(0,1))`，success `35.7639%`，估算 `3:57.786`，已经慢于 `1.2x` 线 `3:48.797`。
  - Monte Carlo 计入 support 当前类型、pending 冲突和路线移动后，当前顺序估算 `4:32.819`，最佳顺序只到 `4:25.877`；`deferred=39023`、`rewrites=34974`、`failed_pending=7933`，说明私有 writer 的状态冲突和改写 churn 仍吃掉收益。
  - 结论：不改 `lb_carrots.py`。当前 API 下，private writer 不足以压进 `1.2x`；多机胡萝卜后续只接受真正不破坏跨 tile Bush 成功率、且能低等待承接多类型 support 的新结构。
- 2026-05-31 多机胡萝卜理论复核：
  - 当前 `main3` 不是“没有伴生”的路线；按资源增量看，完成 `2,000,000,000` 胡萝卜约需要 `24414` 次满伴生收割，request `612` 的资源增长符合满伴生收割主导。
  - 当前 `32` 个双锚点单元的静态 Bush support，把 companion 类型成功率限制在约 `1/3`；双锚点 blocked 坐标后，理论失败重刷约 `2.13` 次 / 成功。
  - #1 `3:10.664` 相当于全局约 `128` 次满伴生收割 / 秒，当前 request `612` 约 `42.6` 次 / 秒，差距约 `3.0x`，几乎正好对应单类型 companion 概率损失。
  - 32x32 容量上，当前双锚点单元刚好是 `2` 胡萝卜 + `30` Bush support = `32` 格，`32` 个单元填满 `1024` 格。三锚点 L 至少 `36` 格、四锚点方块至少 `40` 格，不能无脑把单机相邻 2x2 结构搬到多机榜。
  - 动态接受近距离 `Grass / Tree` companion 的动作预算也不够大：在双锚点单元里，只接受距离 `<=1` 的非 Bush companion，理论只省约 `0.47` 个 `200t` 动作 / 成功；距离 `<=2` 约省 `0.39`，距离 `<=3` 反而亏。这个收益不足以解释 `3x` 差距。
  - 结论：后续多机胡萝卜不应继续做锚点数量或近距离动态补种微调；真正候选必须能低成本接近“全类型 companion 承接”，否则无法接近 #1。
- 2026-06-09 当前 `4x8` / 8 锚点 tile 静态混合 support 筛选：
  - `.codex/tests/carrot_tile_static_type_screen.py` 固定当前 `4x8` tile 和 8 个锚点，统计每个 support cell 对 `Grass / Bush / Tree` 请求的权重，比较 Bush-only 与最佳静态类型分配。
  - 结果：`support_cells=24`、`events=576`、`anchor_blocked=120`；`bush_hits=152`，`best_static_hits=152`，`bush_success=26.3889%`，`best_success=26.3889%`；`equal_cells=24`、`strict_best_cells=0`。
  - 结论：不进入实机；当前 tile 的每个 support cell 对三种类型权重完全相等，预置 Grass/Bush/Tree 混合支撑不能突破 Bush-only 静态上限。后续不要按“预置混合支撑”推进，除非同时引入低成本动态 writer。
- 2026-04-26 动态放开 `Tree` companion 复测
  - 在 `main3` 基础上把可接受 companion 从 `Bush` 扩展为 `Bush / Tree`，命中后到伴生格种对应支撑
  - 请求 `317` 有效两轮：`10:11.835` / `10:13.866`
  - 结果慢于静态 Bush-only 基线 `9:34.732`
  - 根因判断：虽然减少了部分 reroll，但移动到 companion 格、替换支撑、再回目标格的动作成本更高；多机局部支撑结构也更容易被动态改写扰乱
  - 处理：失败实现已从 `.py` 删除；多机胡萝卜下一步不应简单“放开 Tree”，而应优先做预置混合支撑或更大单元布局
- 2026-04-26 四胡萝卜单元复测
  - 候选结构：16 个 `2x2` 胡萝卜单元，每单元 2 台无人机分别负责一列，四格共用一圈静态 `Bush` support
  - 请求 `321` 首轮 `9:47.460`
  - 结果慢于当前双胡萝卜单元基线 `9:34.732`
  - 根因判断：四格共享支撑没有带来足够 reroll 改善，反而引入更多 blocked carrot 位置、更多支撑初始化路径和更高的同单元竞争；收益曲线稳定落后
  - 处理：失败实现已从 `.py` 删除，存档入口已同步回稳定 `main3()`
- 2026-04-30 Grass/Bush support 复测
  - 候选结构：support 位不再开局全部改成 `Bush`，而是保留已知 `Grass / Bush`，reroll 时接受匹配的 `Grass / Bush` companion
  - 请求 `401` 两轮有效完成：`9:52.870` / `9:52.773`，均值 `9:52.822`
  - 结果慢于当前 Bush-only 双胡萝卜单元基线 `9:34.732`
  - 根因判断：省掉预置 Bush 的收益不足以抵消 Grass support 下的整体兑现节奏下降；至少在当前 32 个双胡萝卜单元结构中，保留自然 Grass 不是净收益
  - 处理：失败实现已从 `.py` 删除，存档入口已同步回稳定 `main3()`
- 2026-04-24 双胡萝卜 Bush companion 探针
  - 结构仿照草榜 `main2`：32 个分散双格单元，只接受 `Bush` companion，拒绝 `Grass` 和另一目标格
  - 真实 45 秒窗口无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 结论：直接照搬草榜双格结构不成立，胡萝卜成熟等待和 reroll 成本过高
- 2026-04-24 多机伴生支撑探针
  - 实现过 `main2`：每行无人机在胡萝卜格读取 `get_companion()`，遇到 `Bush / Tree` 时移动到 companion 坐标补支撑，再回原格等待收割
  - 真实 45 秒窗口无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 加入每 4 行循环一次的 `quick_print("main2 progress ...")` 后仍没有任何进度输出
  - 结论：按格子逐个回头补支撑的动作成本过高，且多机互相覆盖 support 的风险很高；该失败实现已从 `.py` 回退，只保留文档结论
- 2026-04-26 外部 `Save0/carrot.py` 修真实目标后多机复测
  - 将原始 `always_not` 无限运行改为 `num_items(Items.Carrot) >= 2_000_000_000`
  - 请求 `289` 在短窗内未产生可靠新增 `run=` 证据；取消时出现 `finished=false runs=1 average=52:17.769`，该行只能当取消摘要，不能当完成轮
  - 运行中 `progress_estimate` 显示后段预估约 `eta_game_time=2:59:04~3:04:00`，明显优于旧记录 `7:22:10.612`，但仍需用 `--request-only` 长流程跑出真实新增 `run=`
  - 水库存阈值变体请求 `290/291` 的预估约 `3:26:08~4:25:52`，慢于无阈值版本；不保留该变体
  - `--request-only` 长流程请求 `292` 证明这条估算误导：资源停在 `carrot=1,000,000,000`，同时 `hay=0 wood=0`，`output.txt` 大量输出“没有种植 Entities.Carrot 所需的物品”
  - 根因：纯滚动列收割把初始 Hay/Wood 全换成胡萝卜库存，但没有伴生倍率或补充材料，无法达到多机目标 `2,000,000,000`
  - 结论：该路线不是“慢但能跑通”，而是材料上限卡死；失败实现已从 `.py` 删除，只保留单机版 `main3`

## 失败对照

- “纯吞吐、不主动追 companion”的理解
  - 这条线当前应视为错误口径
  - 原因不是它一定完全跑不动，而是它忽略了胡萝卜 `160x` companion 才是主收益
  - 真实请求 `65` 无完成轮次，说明它在当前目标量下也不能作为短窗口迭代主线
- `Save0/carrot.py` 多机直接滚动列收割
  - 请求 `292` 卡在 `carrot=1,000,000,000` 且 `hay=0 wood=0`
  - 输出持续报“没有种植 Entities.Carrot 所需的物品”
  - 结论：多机目标下纯种植会被种子材料上限卡死，不能作为候选保留
- `Grass-only` 伴生路线
  - `Grass` 可种在 Soil，不能再按地块冲突判死
  - 但在静态单类型 support 模型下，它和 `Bush-only` 是同概率替换，不会天然提高 companion 命中率
  - 若只是把现有 Bush support 全换成 Grass，理论上主要变化是资源成本而不是 tick 结构；当前不作为优先实机候选
- 动态接受 `Tree` companion
  - 请求 `317` 两轮 `10:11.835` / `10:13.866`
  - 慢于静态 Bush-only `9:34.732`
  - 结论：动态补 Tree 不是低垂果实；若要利用 Tree，必须改成预置支撑或多格单元，而不是命中后长距离补种
- 四胡萝卜单元
  - 请求 `321` 首轮 `9:47.460`
  - 慢于双胡萝卜单元 `9:34.732`
  - 结论：不能只按“单元里胡萝卜更多”判断收益；blocked 目标格变多、支撑初始化和同单元竞争会抵消等待窗口收益
- 保留 Grass support、接受 Grass/Bush companion
  - 请求 `401` 两轮 `9:52.870` / `9:52.773`
  - 慢于 Bush-only 基线 `9:34.732`
  - 结论：用户指出的“赌 Grass 和赌 Bush 概率相同”在概率层面成立，但当前结构里省初始化成本没有转成总时间收益；短期不保留
- 需要避免的不是“所有 companion 行为”，而是“高冲突、低兑现率、以及用移动补种换不回 reroll 成本的 companion”
- 草榜式分散双格 Bush support
  - 真实请求 `55` 无完成轮次
  - 说明胡萝卜不能只靠“固定 Bush 支撑 + 双格轮转”解决，需要更短等待或更少 reroll 的链式结构
- 逐格读取 companion 后回头补 `Bush / Tree`
  - 真实请求 `84` / `85` 均无完成轮次
  - 请求 `84` 因水不足警告刷屏；去掉补水后，请求 `85` 仍无任何 `main2 progress` 输出
  - 说明这条线不是“缺水导致慢”，而是动作结构本身太重
- 32 个单胡萝卜锚点、原地 Bush reroll 探针：
  - 2026-05-30 请求 `603`：75 秒窗口超时，状态 `failed`，`last_error=leaderboard cancelled: carrots`。
  - 改法：32 个单锚点，每个锚点初始化自身曼哈顿半径 `3` 的 Bush support；循环中不再在两个胡萝卜格之间移动，只原地 reroll 到 `Bush` companion 后收割。
  - 进度输出：`100024320 time=61.48 harvest=40 reroll=82`、`200048640 time=114.48 harvest=78 reroll=157`、`300072960 time=167.28 harvest=116 reroll=236`。
  - 取消摘要 `[lb_carrots] finished=false runs=1 average=3:23.433` 不作为有效完成轮。
  - 结论：少一半目标锚点省下的移动远小于吞吐损失；这类简单分支后续应先按理论收割周期估算，不应直接进实机短窗。失败实现已从 `.py` 删除。
- 当前 Bush-only 双锚点结构上的 companion 统计探针：
  - 2026-06-08 请求 `623`：临时在 `roll_static_bush_companion()` 和 `harvest_pair_carrot()` 附近增加低频统计，不改变 Bush-only 成功条件；验证后已从 `.py` 回退，真源仍保留当前最快策略。
  - 有效完成两轮：`run=1 time=9:40.429`、`run=2 time=9:40.131`，稳定均值 `9:40.280`，慢于当前记录 `9:35.395`；取消摘要 `[lb_carrots] finished=false runs=3 average=6:31.408` 不作为有效成绩。
  - 第一轮结束探针：`samples=10965 grass=743 bush=9457 tree=765 bush_blocked=27 bush_ok=9430 non_bush_d1=264 non_bush_d2=766 non_bush_d3=1508 wait=8660 reroll=1535`。
  - 第二轮结束探针：`samples=10867 grass=788 bush=9243 tree=836 bush_blocked=34 bush_ok=9209 non_bush_d1=277 non_bush_d2=815 non_bush_d3=1624 wait=8444 reroll=1658`。
  - 结论：当前 32 个双锚点 Bush support 结构里，非 Bush 请求即使全部在半径 `3` 内，也只有约 `14%~15%` 探针样本；距离 `<=1` 的顺路机会约 `2.4%~2.5%`，距离 `<=2` 也只有约 `7%~7.5%`。在当前路线里继续做“顺路接一点 Grass / Tree”不可能解释 `3x` 差距，且单纯加统计已带来约 `5s` 退化。
  - 下一步不要在 `main3()` 上继续加轻量筛选或顺路补种；若要提高 companion 利用率，必须换成能结构性接近全类型承接的布局 / 接力机制，或者转去 `lb_wood` 做 Tree/Bush 收益拆分。

## 下一步优化方向

- 当前 `main3` 已补真实成绩；下一步不再证明伴生路线能否结算，而是压缩 companion reroll 和成熟等待成本
- 补探针，量化：
  - `Grass / Bush / Tree` 各自的真实命中率与兑现成本
  - 每条 companion 链最终兑现成多少次高收益 harvest
  - 多机协同时链式操作有没有明显减少空转
- 2026-05-31 理论复核后的优先级：
  - 不优先做三锚点 / 四锚点静态 Bush 单元；容量和动作期望都不支持它们形成数量级提升
  - 不优先做“命中后当前无人机走到 companion 格补种再回来”的近距离动态分支；距离阈值模型显示收益太小
  - 优先找能让 support 类型低成本随 companion 类型切换、或让别的无人机就地承接 support 改写的结构；目标是把单类型约 `1/3` 的类型命中率推向接近 `100%`
- 2026-06-08 探针后的收敛：
  - 当前双锚点 `main3()` 的顺路非 Bush 承接空间太小，不能再作为下一轮主线。
  - `4x8` / 8 锚点周期 tile 已验证能继续提高总 companion 兑现次数，折线布局还能降低 blocked 锚点概率，但它仍是 Bush-only 静态支撑。
  - 4x8 静态锚点路径筛选已经排除继续加密锚点；后续不要再只换 8 锚点等价形状或 9/10 锚点静态布局。
  - 4x8 静态混合 support 类型筛选已经确认每个 support cell 的三类型权重完全相等；后续不要再按预置 Grass/Bush/Tree 混合支撑推进。
  - 非通信定时 helper 已被预算筛掉；没有通信 / 共享状态时，support 类型轮换无法和随机 companion 请求同步，只会保持 `1/3` 命中或引入远高于 reroll 的等待。
  - 物理 mailbox helper 也已被预算筛掉；世界实体格可以当低带宽信号，但编码请求、坐标和完成确认的动作 / 等待成本太高。
  - 2026-06-10 已删除 progress / 统计计数作为管理成本候选；确认前不更新成绩注释。游戏恢复后必须短跑 `lb_carrots`，若无稳定刷新或需要重新观测 harvest / reroll 分布，则回退或临时恢复统计探针。
  - 下一轮若继续多机胡萝卜，应优先在当前折线 8 锚点 tile 上量化瓶颈：每 tile 成熟等待、reroll 次数、移动环路成本、水 / 肥消耗，以及是否存在低成本动态 helper 承接 `Grass / Tree`。
- 简单策略先做数学门槛，不直接实机：
  - 先按榜一时间反推“如果每次收割都带 companion，需要多短的单次有效收割周期”
  - 再按动作成本估算原地 reroll、走到 companion 格补种、回原格等路径的期望时间
  - 只有理论周期接近或优于目标周期的方案，才进入真实游戏验证

## 候选策略方向（猜测 / 待验证）

### 方向 1：多机链式胡萝卜操作

- 核心思路：按你给出的路线做链式操作，例如：
  - 先种胡萝卜 `a`
  - 如果 `a` 的伴生是 `Grass / Bush / Tree`，不要单机长距离回头补
  - 改为让局部固定 support 区预先承接可落地类型
  - 胡萝卜机只负责挑选 companion 落在 support 区附近的格子
- 主瓶颈：当前 repo 路线把每格都当独立循环，没把 companion 机会串起来
- 可能更强的原因：减少“读 companion -> 长距离补支撑 -> 回原格”的往返动作，才可能把 `160x` 兑现率转成收益
- 优先探针：
  - support 区固定后，单位时间高倍收割次数是否明显上升
  - companion 坐标落入局部 support 区的命中率
- 当前状态：已演进为 `4x8` / 折线 8 锚点静态 Bush support；静态锚点加密、8 锚点形状平替、9/10 锚点、静态混合 support、同无人机顺路改写、spawn-on-demand helper、非通信定时 helper、physical mailbox 和 adaptive no-restore support 都已筛掉。后续不再直接按“链式胡萝卜”实机，除非先证明新的链路不需要 anchor 阻塞等待、不依赖当前缺失的通信 API，且不会破坏 tile owner。

### 方向 2：围绕多类型 companion 建低成本承接结构

- 核心思路：承认 `Grass / Bush / Tree` 都可落地，但必须避免“命中后长距离补种再回原格”的高动作成本
- 主瓶颈：静态单类型 support 只能吃约 `1/3` 类型概率；动态补种又容易被移动和改写成本压垮
- 可能更强的原因：如果能让同一局部 support 区低成本承接多类型，伴生命中率才可能真正提高
- 优先探针：
  - 三种可落地 companion 的出现频率与目标格冲突率
  - 多类型承接比单类型 reroll 少掉的失败重刷，是否超过移动 / 改种成本
- 当前状态：`carrot_tile_static_type_screen.py` 已确认预置静态混合 support 不优于 Bush-only；`carrot_adaptive_support_markov_screen.py` 已确认只记忆 support 最近类型不会突破 `1/3` 类型命中；写入安全的 own-tile mismatch rewrite 估算 `5:32.087`，慢于当前 `4:34.314`，且 request `674` 的 same-drone dynamic 实机也慢到 `5:50.841`。多类型承接只有在能安全跨 tile 写入、或 support writer 正好在请求格且无等待时才重开。

### 方向 3：让不同无人机承接同一条 companion 链

- 核心思路：不是让一台机单独把整条链跑完，而是让相邻无人机接力承接 companion 引出的下一格
- 主瓶颈：单机链式操作会增加回头路；多机如果不协同，链还是会断
- 可能更强的原因：多机接力可能把“链式收益”和“并行吞吐”两边都保住
- 优先探针：
  - 接力链相对单机链的回头路减少量
  - 无人机间协同时序是否会引入新的阻塞
- 当前状态：当前 Save0 没有 `send` / `receive`，`spawn_drone()` 会复制 parent scope，不能共享运行时队列；`spawn_drone() + wait_for()` 已被 request `670` 证伪，physical mailbox / world-state relay 预算也不过线。不同无人机接力暂缓到有真正通信 API、远程请求可见性，或无需完成信号的同步结构出现。
