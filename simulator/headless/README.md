# C# 无界面脚本模拟器

这是游戏脚本的本地执行入口，旧Python模拟执行器已移除。运行时只需要.NET 10，不需要Python、Unity、Steam、BepInEx或真实存档。它直接使用原版语言解释器、调度器、农场和地下世界源码，配套原版资源快照。

## 构建与运行

在仓库根目录执行：

```bash
dotnet build simulator/headless/TFWRSimulator.csproj -c Release
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/functional/block.py --preset all --item Dynamite=2000 --seconds 60 --wall-seconds 10 --json block-report.json
```

WSL 中构建和执行使用 Windows `dotnet.exe`，例如 `"/mnt/c/Program Files/dotnet/dotnet.exe"`。从仓库根目录传相对路径，避免把 WSL 绝对路径传给 Windows 进程。

```bash
# 只检查入口及其全部静态导入，包括未执行分支中的导入。
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/functional/resources.py --syntax-only

# 独立进程并行；所有seed共享10秒墙钟预算。
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/leaderboard/lb_cactus_single.py --seeds 0,1,123 --jobs 3 --seconds 30 --wall-seconds 10

# 使用原版排行榜盘面、材料、科技、单机限制和地下特征配置。
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/leaderboard/lb_mushrooms_single.py --leaderboard mushrooms_single --seconds 30 --wall-seconds 10
```

`--help` 显示完整参数。默认窗口为30游戏秒、10墙钟秒、200万次内置调用和5000万个解释器节点。墙钟上限最多600秒，不随seed数相乘；优先从短窗口开始，只有单轮本身很长（重置榜）才抬高。父进程给报告回收保留最多1秒宽限，超过后终止自己的工作进程并报告 `hard_timeout`。每约2墙钟秒输出进度到stderr；stdout只输出JSON。

## 会话口径（与公开榜完整统计对齐）

公开榜只认游戏内满约7200秒（2小时）的完整统计会话成绩：会话内每轮从同一初始条件重新开始，上传分数是各轮时间的**均值**，且只在最后一轮成功时生效。本地因此统一用 [session.py](session.py) 跑满同样预算再比较，不拿单seed单轮数字当对照成绩：

```bash
python3 simulator/headless/session.py scripts/leaderboard/lb_maze.py --leaderboard maze --session-seconds 7200 --jobs 20

会话结论同时打印到标准输出；报告默认写 `.codex/tmp/sessions/<榜单>-session.json`，同一榜单重跑直接覆盖，加 `--no-output` 则只打印。
```

工具按批启动独立工作进程（`--jobs` 并行）累计各轮游戏时间，到预算即停；均分只算达成目标（`stop_reason=finished`）的轮，任一轮未达成目标就按 `StopLeaderboardRun` 规则判整场无效并立即停止。报告给出轮数、累计游戏秒、均值、标准差、标准误、最小／最大值和逐轮明细。

本机20核实测：迷宫每批20轮墙钟约7秒，满7200游戏秒的会话（84轮）约30秒、均分86.466秒±0.143（标准误）；快速重置单轮约2485游戏秒，4轮并行约9秒；地下蘑菇单机单轮约760游戏秒，12轮约4秒。全场均口径对任何榜都只是几十秒的计算预算，单seed单轮只保留作方向筛选。

`--preset max` 为基础游戏满科技，`all` 包含地下DLC，`reset` 为重置初始条件。满科技默认只有Pumpkin和Power各10亿，其余库存为0；具体实验应明确提供材料。`--scenario` 接受 `preset/items/unlocks/goal/leaderboard`；命令行 `--item`、`--unlock` 最后覆盖。`--save` 只读导入科技和库存，不恢复存档地形或运行状态；同一科技的多条等级记录取最高级。排行榜、preset与save作为初始条件来源不能混用，这也适用于场景JSON中的preset。

`items`和`unlocks`必须是对象。同一输入层中，`Coal`与`Items.Coal`等别名属于同一项，重复设置会报错；不同层之间仍允许覆盖。`--size 1..32`固定地图边长，默认0按Expand科技生成。使用排行榜场景时，显式材料、科技、目标或地图覆盖会令报告的 `leaderboard_has_overrides=true`；这类组件实验不能当作原始排行榜条件下的整轮成绩。

```json
{"preset":"all","items":{"Dynamite":2000},"unlocks":{},"goal":{"item":"Block","amount":1000000}}
```

目标只用于结束时报告，不会替脚本提前终止。连续脚本到窗口即停止；恐龙等批量结算仍须由脚本完成至少一轮后才能比较效率。部署准入继续遵守[脚本验证规则](../../docs/script-validation.md)，语法边界见[原版语言检查](syntax-validation.md)。

## 执行范围与边界

- 原版Tokenizer、Parser、AST和内置函数：游戏语言、模块导入、作用域、容器、错误和操作计费。不会把游戏脚本交给CPython执行。
- 原版199t调度、纳秒事件、无人机状态及随机流；等待子机返回、取消子机和资源竞争沿用原版实现。
- 地上作物、伴生、水肥、南瓜合并、仙人掌、恐龙、迷宫；地下生成、开采、爆炸、塌方、矿物、蘑菇、金字塔、扫雷和藏宝图。
- 30个原版排行榜资源场景。正式排行榜使用加密随机源，本工具明确使用seed作本地筛选，报告标记 `seeded_leaderboard_screening`，不承诺预测正式打榜轨迹。
- 不模拟画面、音效、鼠标拾取或Steam成就到账。原版模拟内部的递归 `simulate/leaderboard_run` 保留警告行为；由CLI选择要模拟的脚本和场景。`tap` 保留模拟内计时，不发送外部点击。
- 警告和错误以原版消息键报告，不载入游戏的中文本地化资源。图形变换只服务不影响机制的显示调用；不支持的拾取/加权动画求值明确抛错。世界生成内部异常也会使运行失败，不静默产出有效报告。

实现完整性、方法覆盖与长期精度分开判断。直接采用原版源码并不等于所有参数组合都经过实机验证。已覆盖范围、误差和迁移状态见[验收记录](validation.md)。

## 报告

报告包含脚本与全部依赖SHA256、模拟程序集和资源SHA256、场景/存档输入SHA256、seed、实际初始科技/库存/地图、纳秒时间、净库存、调用数、API tick、无人机与表层格子状态、停止原因和脚本输出。`initial_state`来自原版Farm初始化后的有效状态，包含基础必有科技，并按当前场景过滤不可用DLC；`input_hashes`标识本次实际读取的JSON字节。`goal`记录显式目标，`leaderboard_goal`记录原版榜单目标。报告是观测摘要，不是可恢复整个世界的存档。

| 字段 | 含义 | 用途 |
| --- | --- | --- |
| `game_seconds` | 模拟世界推进的游戏时间 | 计算资源产出速率、游戏任务及成就窗口 |
| `efficiency.items.<资源>.net_change` | 本次实际入库净增长，消耗可以为负 | 扣除初始库存，保留运行材料消耗 |
| `efficiency.items.<资源>.net_per_game_second` | 净增长除以实际游戏秒 | 连续产出对照和重置路线计价 |
| 单seed报告的 `wall_seconds` | 工作进程开始到生成报告时的实际耗时，含资源加载、解析和模拟 | 观察执行器的本地计算开销 |
| 性能对照中的 `command_seconds` | 外部计时器测得整条命令从启动到退出的实际耗时，含进程启动、报告输出和回收 | 衡量用户等待时间，比较完整命令速度 |

`efficiency.elapsed_game_seconds`与`game_seconds`相同，计入本次初始化、执行、移动、成熟和同步。状态快照完整且时间大于0时，`efficiency.valid=true`；错误、中途打断导致不完整状态或零时间时，速率为null。正常到达游戏窗口、或在调度步之间到达墙钟预算，可以报告已观测到的平均速率。该标记只说明速率可以计算，不证明批量生产已经结算，也不代表允许部署。运行中购买科技时，整段平均速率不能当作升级后稳定速率。重置路线的投资比较见[科技路线计价](../../docs/leaderboards/README.md#重置榜的科技路线计价)。

`command_seconds`由外部性能采样记录，不是单seed CLI的固定输出字段；多seed报告顶层的 `wall_seconds` 表示整批实际耗时，子报告仍表示各工作进程耗时。这些时间不相加。例如20游戏秒、1.391工作进程秒、1.706命令秒，表示约1.706秒现实时间算完20秒游戏过程；按命令计约11.7倍游戏速度。

- `finished`：脚本正常结束。`goal_reached` 另行判断库存/科技目标。
- `game_time_limit`、`wall_time_limit`、`api_call_limit`、`node_limit`：预算耗尽，不能标作完整任务成功。
- `error`、`hard_timeout`、`worker_error`：失败。没有完整快照时 `state_complete=false`，不能当效率证据。
- 最多保存10000条脚本输出，超出数量写入 `output_dropped`；不把截断输出称为完整输出。
- `--trace` 输出JSONL，记录内置调用的参数、应用时间和结果；`wait_for` 在子机完成时记录实际返回值。轨迹增加本地开销，不增加游戏tick。多seed自动生成带seed后缀的文件。
- `achievement_verification=not_recorded`：资源或脚本条件不等于Steam已解锁。

## 源码费用报告

添加`--hot-spots costs.json`，按模块路径、源码行、调用路径和无人机机位ID输出实际费用：

```bash
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/leaderboard/lb_cactus_single.py --leaderboard cactus_single --seed 1 --seconds 60 --wall-seconds 10 --hot-spots costs.json --json report.json
```

默认不采集。多seed会生成`costs.seed-<seed>.json`，与主报告中的seed及`hot_spots`路径对应；主报告保存场景、程序集和资源依据，费用文件保存依赖源码哈希，两者一起保留。输出不能覆盖脚本、场景、报告或轨迹，不与`--syntax-only`合用。采集会增加墙钟开销，不额外收游戏tick。

| 费用字段 | 口径 |
| --- | --- |
| `hot_spots[].interpreter_nodes` | 原版AST执行观察次数，不等于收费tick |
| `hot_spots[].interpreter_ticks` | 该行实际调用解释器扣费方法的独占费用，不重复累加到调用者 |
| `hot_spots[].api_calls`、`completed_api_calls` | 内置函数发起／完成次数；包含`range`、`get_time`等，不只包括游戏动作 |
| `hot_spots[].api_ticks` | 内置函数实际完成费用，与解释器费用分开；与主报告API账单对照 |
| `hot_spots[].call_path` | 模块名及函数名组成的调用路径；`<module>`表示模块初始化 |
| `drones[].wait_for_latency_game_seconds` | 该机位从发起`wait_for`到取得返回值的世界时延，含调度等待 |

`hot_spots`默认按解释器实际费用降序排列。同一源码行在不同机位或调用路径下分列；机位ID复用时合并累计。`pending_api_calls`、`state_complete`和`execution_finished`标明观测边界，窗口停止不等于完整任务账单。

总耗时始终取原版调度器推进的`game_seconds`／`nanoseconds`；机位费用与等待可能重叠，不求和推算世界时间。当前报告没有完整的Idle归因或关键路径图。2026-11-13单机仙人掌三seed的统计关闭／开启及修改前后时间、库存、状态和输出完全一致，8组既有实机归档重放通过；多机仙人掌seed1两次均34.75345086秒、覆盖32机位，API和节点计数对账一致，`wait_for`累计43.39909728秒。以上是定向本地证据，不代表新实机验收。转换流程与边界见[计费及代码生成](../../docs/leaderboards/interpreter_cost_notes.md#母版与固定代码生成)。

## 结构与来源

| 文件 | 职责 |
| --- | --- |
| `Native/*.cs` | 自动提取的原版机制、解释器与调度源码 |
| `UnityValues.cs`、`HeadlessHost.cs`、`HostUtilities.cs` | 无界面值类型、资源/日志/脚本宿主，隔离显示依赖 |
| `AssetLoader.cs`、`data/assets.json` | 202个原版资源，恢复对象引用、字段及OnEnable/Start生命周期 |
| `SimulationScenario.cs` | 科技、库存和原版排行榜场景 |
| `SimulationWorker.cs`、`SimulationMonitor.cs`、`ExecutionProfile.cs` | 执行、预算、进度、轨迹与可选源码实际费用 |
| `SimulationOptions.cs`、`SimulationSupervisor.cs`、`SimulatorCli.cs` | CLI、独立进程并行、硬超时及JSON报告 |
| `import_native.py`、`export_assets.py` | 开发时生成源码和资源，模拟运行时不调用 |
| `fixtures/`、`verify.py` | 归档实机脚本与观测重放，不启动真实游戏 |

源码来自本机原版Core.dll与Utils.dll的早期导入；2026-11-18按构建26732695重新核对并移植了会改变计费的差异（挖矿速度按实际50%重置为1.5^max(N-1,0)并统一除以初始1.5、列表解构计1 tick、别名导入按非静态每次扣费、免费调试函数非静态调用至少1 tick、set_world_size不缩到2格以下、排行榜脚本节点超10万即报错并取消该场），其余改动属界面与错误处理，不影响时间。原作者代码保持其原有归属，生成文件不是重新编写的独立算法。二进制SHA256保存在资源快照的 `source_assemblies`，反编译文本SHA256在 `Native/source.json`。导入器和导出器锁定该版本；游戏更新时必须重新审查适配与重放结果，不能只换资源。

生成源码的步骤是用ILSpy反编译上述两个程序集为 `Core.cs`、`Utils.cs`，然后运行：

```bash
python simulator/headless/import_native.py <反编译文本目录>
uv run --with UnityPy --with TypeTreeGeneratorAPI python simulator/headless/export_assets.py simulator/headless/data/assets.json
```

游戏路径统一由 `game_control` 的配置模块解析。生成步骤只读游戏安装文件，不读取或写入Save0。`Native/` 的修改必须通过导入器完成。适配点包括移除Unity帧等待、CLI的可重复seed模式、解释器观察钩子、资源生命周期和无界面诊断；机制算法不另写一套近似模型。

重新构建后可重放8组归档实机证据：

```bash
python simulator/headless/verify.py --output replay.json
```

WSL 另加 `--dotnet '/mnt/c/Program Files/dotnet/dotnet.exe'`。每例最多8墙钟秒，两个进程并行。当前构建的4组要求时间精确到纳秒且输出逐字相等；4组旧版机制归档要求输出逐字相等，单列版本，不能当作新版全覆盖。验证脚本只是开发工具，日常模拟直接运行C#程序集。
