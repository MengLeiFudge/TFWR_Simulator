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

`--help` 显示完整参数。默认窗口为30游戏秒、10墙钟秒、200万次内置调用和5000万个解释器节点。墙钟上限最多75秒，不随seed数相乘；优先从短窗口开始。父进程给报告回收保留最多1秒宽限，超过后终止自己的工作进程并报告 `hard_timeout`。每约2墙钟秒输出进度到stderr；stdout只输出JSON。

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

## 结构与来源

| 文件 | 职责 |
| --- | --- |
| `Native/*.cs` | 自动提取的原版机制、解释器与调度源码 |
| `UnityValues.cs`、`HeadlessHost.cs`、`HostUtilities.cs` | 无界面值类型、资源/日志/脚本宿主，隔离显示依赖 |
| `AssetLoader.cs`、`data/assets.json` | 202个原版资源，恢复对象引用、字段及OnEnable/Start生命周期 |
| `SimulationScenario.cs` | 科技、库存和原版排行榜场景 |
| `SimulationWorker.cs`、`SimulationMonitor.cs` | 执行、预算、进度、状态与轨迹 |
| `SimulationOptions.cs`、`SimulationSupervisor.cs`、`SimulatorCli.cs` | CLI、独立进程并行、硬超时及JSON报告 |
| `import_native.py`、`export_assets.py` | 开发时生成源码和资源，模拟运行时不调用 |
| `fixtures/`、`verify.py` | 归档实机脚本与观测重放，不启动真实游戏 |

源码来自本机原版构建26462009的Core.dll和Utils.dll。原作者代码保持其原有归属，生成文件不是重新编写的独立算法。二进制SHA256保存在资源快照的 `source_assemblies`，反编译文本SHA256在 `Native/source.json`。导入器和导出器锁定该版本；游戏更新时必须重新审查适配与重放结果，不能只换资源。

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
