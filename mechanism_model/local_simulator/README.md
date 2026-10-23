# 农场 API 本地模拟

此入口执行受支持的游戏脚本，计算农田状态、资源和预计游戏时间，不需要打开游戏，只依赖 Python 3.11+ 标准库。已适配全部12种公开实体的主要机制，包括7种可种植作物、南瓜合并、恐龙和迷宫；范围与近似项见 [全作物机制](mechanisms.md)。[API覆盖记录](api-coverage.md) 保留49个公开函数的方法级对照。精度取舍遵循 [模拟精度与验收](../README.md#模拟精度与验收)，结果不能作为真实成绩或排名。

## 使用

在仓库根目录运行：

```bash
python3 -m mechanism_model.local_simulator references/leaderboard_scripts/lb_cactus_single.py --seed 1
```

保存报告和逐 API 轨迹：

```bash
python3 -m mechanism_model.local_simulator references/leaderboard_scripts/lb_cactus_single.py --seed 1 --output .codex/cactus-local.json --trace .codex/cactus-local.jsonl
```

`--output` / `--trace` 会覆盖指定文件，父目录须存在。命令不会访问真实存档、启动游戏或更新排行榜缓存。默认关闭逐API快照、JSON序列化和轨迹哈希；需要定位差异时再传 `--trace`。

同一脚本批量筛选多个seed：

```bash
python3 -m mechanism_model.local_simulator references/leaderboard_scripts/lb_cactus_single.py --seeds 0 1 123 --timeout 30 --output .codex/cactus-batch.json
```

`--seeds` 接受1～100个不重复的非负Int32，与 `--seed` 互斥。在一个隔离进程内依次运行，复用源代码编译结果，各seed重建独立世界。报告为 `kind=prediction_batch`，包含 `reports` 和 `completed_seeds`；每完成一个seed向stderr报告进度。若配置trace，分别写入 `名称.seed-N.扩展名`。

用 `--scenario scenario.json` 指定初始库存、科技及可选目标。将下列JSON保存为 `scenario.json` 后传入；省略项保留默认值：

```json
{"items":{"Hay":1000000,"Wood":1000000,"Carrot":1000000,"Cactus":1000000,"Water":100,"Fertilizer":100,"Weird_Substance":10000},"unlocks":{"Speed":4},"goal":{"item":"Cactus","amount":131072}}
```

默认 `preset=max`：科技全满、32×32草地、Pumpkin和Power各1e9，其他库存0。各榜脚本需要的资源应通过场景明确提供；单无人机榜的地图/无人机限制也应显式设置，例如 `Expand=5`、`Megafarm=0`。`preset=reset` 为除Grass等级1外科技全0、库存全0；两种预设都可覆盖。低级Expand的1×3农田已支持，但未验证完整Fastest Reset流程。

| 报告字段 | 含义 |
| --- | --- |
| `kind: prediction` | 本地预测 |
| `status` / `error` | 脚本完成或被停止，以及失败原因、行号 |
| `goal_reached` | 是否达到场景 `goal` 指定的物品数量；未配置目标时为null |
| `predicted_game_seconds` | API及循环估计成本推进的共享游戏秒，支持并行和中途变速；旧字段 `predicted_api_seconds` 保留为同值兼容字段 |
| `interpreter_ticks: null` | 尚未实现游戏解释器计时，不能解释成 0 |
| `api_calls` / `api_ticks_by_function` | 按 API 拆分的调用数与动作成本；各无人机成本相加，不等于共享时间 |
| `state` / `harvests` | 最终全实体/分组、库存和随机抽取次数；harvests记录普通作物收获，恐龙/迷宫收益体现在库存 |
| `estimated_loop_ticks` | 为循环推进计入的估计tick，与完整解释器耗时区分 |
| `script_steps` | CPython 行/函数调用事件数，仅用于执行上限 |
| `wall_seconds` | 本机计算时间，不是游戏时间；不含 CLI 子进程启动 |

JSONL 每行记录调用序号、无人机、API、参数、返回值、调用时刻的坐标/库存/当前格状态，以及预计可再次运行的 `ready_ns`。与单机按调用完成后记录的旧轨迹不同，它保留并发调用的时间顺序。报告附脚本哈希、seed和八流派生seed；只有开启trace才计算轨迹哈希，否则 `trace_sha256=null`。`warnings` 记录模拟内部启动入口被拒绝等情况。

## 机制与执行边界

作物参数来自当前原版资源快照，科技成本复用 `references/unlocks/unlock_snapshot.json`。全部作物、伴生、水肥/感染、南瓜合并、向日葵倍率、恐龙、迷宫和地图升级的实现与实机范围统一见 [全作物机制](mechanisms.md)。

脚本调用转为协程，在API和循环边界按可运行时间调度。每台无人机有独立位置、随机流和复制后的全局/闭包作用域，棋盘与资源共享；`wait_for`只阻塞调用者，返回值再次复制。清场取消其他无人机；等待已取消句柄会停止并报告原因，避免无界等待。

成功的普通移动/交换/种植/收获、翻地、清场和缩图计200t；失败动作和普通查询计1t。恐龙移动由400t起随吃苹果递减。时间查询与quick_print为0t；print、翻转和摸猪约1游戏秒。每次循环估计1t以推进忙等；CPython其他控制流及通用容器函数的游戏解释器成本未完整计入。

尚未全面对齐非整数range、所有类型/解锁门槛和完整游戏语言语义。不支持的语法或非法参数会停止，不返回固定成功值。`simulate` / `leaderboard_run`只复现模拟内部禁止递归启动的行为；外部游戏启动使用真实协调器。

水分采用概率期望，Power按各无人机动作连续扣除，未复刻原版0.2秒扣款批次。八流seed派生及各机制独立随机流已接入；various共享事件未逐个复现，同seed自然成熟时刻仍可能不同。完整解释器耗时和无人机竞争顺序也存在近似，不能把初始仙人掌约3%的历史误差推广到所有策略。

游戏没有int()/float()，运行器也不提供。输出与运行资源有限制；脚本仅适用于已记录的机制组合。

## 执行上限

默认每个seed限制 100000 次 API 调用、2000000 个脚本行/函数调用事件，可用 `--max-api-calls`、`--max-steps` 修改。`--timeout` 默认10秒、最多60秒；批量模式所有seed共享这一墙钟上限。纯计算循环也计步。CLI 使用独立进程，超时会终止并回收；失败返回非零退出码，已回传的seed报告及已经写出的轨迹可保留。

脚本执行器只用于已审阅的本地策略，不是运行不可信代码的安全沙箱。直接调用 Python `run_script()` 没有 CLI 的进程级兜底，日常筛选使用上述命令。

## 模拟开销

本地执行只推进虚拟游戏时间，没有UI帧率或时间倍率。当前减少的开销包括：关闭默认trace、只扫描活动无人机和未成熟作物、按需计算水分期望衰减、恐龙尾巴使用deque、移除已销毁迷宫、按源代码与路径缓存编译结果。已结束无人机的返回值由脚本持有的句柄保留，调度器不再扫描历史任务。

作物成熟仍保留既有时间推进和排序规则，没有引入完整事件队列，也没有跳过用户循环。脚本计步与进程墙钟限制保留。批量seed目前顺序执行，不是多核并行。当前优化只做静态检查与LSP诊断，未测量新版吞吐或重新运行机制对照，不提供加速倍数。

## 方法级验证

性能优化前的请求38/39/41/42累计635条离散观测一致；当时20项本地错误/限额检查通过。自然成熟和Power误差单独记录，完整证据见 [全作物机制](mechanisms.md) 与 [API覆盖记录](api-coverage.md)。这些是历史机制验证，不能当作当前优化版本重新通过实机对照的证明。

## 初始仙人掌版本的历史基线

请求 35，在真实游戏内分别运行未插桩策略函数、记录 API 返回值的版本和边界探针。显式传入满级科技、相同资源与 seed，避免 `simulate(Unlocks)` 捕获主农场的当前升级级别。

| seed | 一致的 API 返回值数 | 本地 API 秒 | 实机 tick 折算秒 | 低估比例 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1588 | 21.2261 | 21.8464 | 2.839% |
| 1 | 1606 | 21.3601 | 21.9996 | 2.907% |
| 123 | 1537 | 20.4971 | 21.1010 | 2.862% |
| 161803399 | 1618 | 21.3293 | 21.9629 | 2.885% |
| 20261022 | 1515 | 19.7073 | 20.2999 | 2.919% |
| 2147483647 | 1609 | 21.4261 | 22.0569 | 2.860% |

9473 个离散 API 返回值按顺序相同，六轮最终 Cactus 均为 131072，Pumpkin 均为 999995904；时间查询单独比较，不计入精确一致数量。54 条边界观测覆盖未成熟复种、越界交换、移动环绕、草交换失败、翻地缓存、交换、成熟后收获/复种和脚本随机数。正式 RNG 实现另通过既有独立 .NET 参考的 73728 个混合值对照。

时间列来自当时未插桩策略的get_tick_count()，包含验证入口额外函数定义、分支和末尾库存读取，不是官方榜单成绩。初始版本未添加经验倍率，约3%的偏差只描述该版本和场景；当时本地单轮计算约0.05～0.06秒。扩展版本按方法验证，未用这些历史数字冒充重新测量的整轮误差。

坏脚本的 API 上限、纯计算步数上限、墙钟终止、未知 API、Python 专有函数、额外导入和错误实体类型七项检查通过。Python 3.12 环境下 opcode 跟踪没有产生预期事件，因此计步采用行/函数调用事件。LSP 无诊断。

请求结束后已逐字节恢复真实 `test.py` / `simulate.py`；BepInEx 与 Unity 请求 35 期间的新增日志无 Error/Exception。原始输出、两份日志、逐 seed 报告、探针和首次差异比较器保存在本机 `.codex/tests/local-cactus/`。请求 34 曾因探针使用游戏不支持的 `int()` 失败，修正后请求 35 完整通过。后续方法级验证见 API 覆盖记录；显示刷新率异常的处理见 [模组运行排查](../../oracle_runner_mod/README.md#显示帧率与-vsync)。

事实源为当前安装资源 `FarmObjectSO(cactus)`、`LeaderboardSO(cactus_single)`，及反编译的 `Simulation`、`Growable`、`GridManager`、`Drone`、`Cactus`、`Execution.ApplySideEffect`。资源提取只是本次核对工具，模拟命令不依赖 UnityPy。

| 证据 | SHA256 |
| --- | --- |
| Core.dll | `b8ac8d22b614d9e48d3affa9a4de9c77e799b824ed8f50dc2e494cc2dd9f9082` |
| resources.assets | `a465a0e642a5e34687693fee927ef9343f4d2329e75f23a421c03a149d77b6e0` |
| lb_cactus_single.py | `a013b1fc641c0fa5e782fb0ad9946d7d7db55f11314f17d6ad410c4f9b9c7bfd` |
| 本次 game-output.txt | `6a214957427e87e9a321c6c6c228594f93e7e8ceeb37e4959c629bac5be42193` |
