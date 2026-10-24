# TFWR Oracle Runner

让外部 Python 工具、编辑器和自动化程序调用 The Farmer Was Replaced 的真实脚本执行入口，并收集执行状态、leaderboard 时间和资源快照。

模组通过 BepInEx 5 与 Harmony 接入游戏。Thunderstore 依赖为 `BepInEx-BepInExPack-5.4.2305`。它执行存档中已有的脚本窗口，不提供外部 Python 解释器。

客户端和本地模拟器从 GitHub 仓库取得，Thunderstore 包只安装游戏模组。后台控制接口需要支持协议2的DLL。

## 后台控制

`prepare` 结束当前执行、确认已有结果页并进入工作区，返回 `workspace_ready=true`。普通脚本请求也会从主菜单自动进入工作区；已有脚本仍在执行时，普通请求继续等待，不主动中断。

`quit` 先停止执行，再调用游戏保存和退出入口；保存出现确认窗口时保留游戏并报告失败。模组先持久化请求终态再退出，客户端确认进程消失后返回 `game_exited=true`。任务结束且近期不再实机验证时调用它。

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --action prepare
python3 tfwr_orchestrator/tools/run_real_game_script.py --action quit
```

有活动外部请求时，须显式加 `--replace`；已有终态须先收取结果。没有外部请求时保留手动游玩的主菜单和排行榜结果页。

## 0.2.2 更新

- 新增 `prepare` 后台准备工作区和 `quit` 保存退出接口，客户端确认游戏退出后返回结果。
- 脚本请求可从主菜单直接进入工作区；无需模拟鼠标点击。
- 控制命令沿用请求 ID、文件锁与终态确认，活动外部请求须显式替换。
- 协议版本升级为2，原有脚本请求仍兼容；配套客户端从 GitHub 更新。

## 0.2.1 更新

- 修复停止后再次执行时的输出文件占用，以及短请求日志尚未落盘的问题。
- 启动等待期限按每个请求计时；替换和取消请求时重新核对状态，避免执行已过期请求。
- 手动运行保留排行榜结果页；外部请求开始前确认已有结果页，完成后只自动关闭所属结果页。
- 补记官方完整统计的最后完成轮，增加 Steam 初始化与榜单下载诊断。
- 配套客户端提供适合 AI 调用的 JSON 任务接口、幂等提交、增量监控和结果归档。

仓库中的本地模拟器只提供预测，精度与已验证范围见[模拟器验收与限制](https://github.com/MengLeiFudge/TFWR_Simulator/blob/master/mechanism_model/local_simulator/validation.md)。候选策略仍须真实游戏确认。

## 安装到 R2

1. 在 r2modman 的 TFWR profile 中安装上述 BepInExPack。
2. 在 R2 的在线模组列表中搜索 `TFWR_Oracle_Runner`，选择作者 `MengLei` 的包并安装。也可导入发布 ZIP。
3. 通过 R2 的模组启动入口打开游戏；外部请求负责进入工作区。
4. 在 profile 中检查 `BepInEx/config/mlj.tfwr.oracle-runner.cfg` 和 `BepInEx/LogOutput.log`。日志会输出实际 `state_file=` 路径。

新配置默认 `AutoPlayMainMenu=false`，没有外部请求时保留主菜单。设为 `true` 可在启动后直接进入工作区；已有配置保留原值。

手动安装时，使用游戏安装目录下的 `BepInEx` 目录。BepInEx 5 和 6 的插件入口不同，本版本须在 BepInEx 5 下加载；迁移时使用独立的 R2 profile，避免混放两套加载器的 core 文件。客户端与模组须一起更新，以共同遵守文件锁协议。

## 连接 Python 客户端

客户端来自 [TFWR_Simulator 仓库](https://github.com/MengLeiFudge/TFWR_Simulator)。需要 Python 3.11 或更新版本。从仓库根目录执行下面的命令；Windows 可将 `python3` 替换为 `python`。

在仓库 `.env` 中填写自己的路径：

```env
TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
TFWR_SAVE_ROOT=C:\Users\YourName\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
TFWR_BEPINEX_ROOT=C:\Users\YourName\AppData\Roaming\r2modmanPlus-local\TheFarmerWasReplaced\profiles\Default\BepInEx
```

`TFWR_BEPINEX_ROOT` 指向所选 profile 的 **BepInEx 目录**。可从 R2 打开 profile 文件夹后取得路径；不同安装方式可能使用不同位置。未设置时，客户端使用 `TFWR_GAME_ROOT/BepInEx`。也可通过 CLI 的 `--bepinex-root` 覆盖。WSL 支持上述 Windows 路径写法。

先通过 R2 启动该 profile 的游戏，再调用 `prepare` 或提交脚本。使用 R2 profile 时，客户端只连接已有游戏进程；不会自行启动缺少 profile 参数的游戏 EXE。

查询状态：

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --status-only
```

运行已有脚本 `my_script.py`，等待完成后打印结果：

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script my_script --request-timeout 20
```

只提交请求并立即退出：

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script my_script --request-timeout 60 --request-only
```

`--request-only` 默认拒绝覆盖活动请求；明确替换须加 `--replace`，终态须先回收。AI调用推荐 `--action submit/status/wait/cancel/result/health` 的JSON任务接口，支持幂等提交和结果留存，沿用当前DLL协议。常规文本等待模式先等待 `idle`。本仓库打榜使用 `lb_start` 派生入口；参数与任务生命周期见 [协调器说明](https://github.com/MengLeiFudge/TFWR_Simulator/blob/master/tfwr_orchestrator/README.md)。

## 榜单页面与 Steam 数据

手动运行结束后，结果页保留到用户按 OK 或 Esc。外部请求开始前会先确认已有结果页；外部请求产生的结果页由模组自动确认。`simulate()` 共用游戏运行浮层，但不会获得关闭之后手动结果页的权限。

结果页右侧的成绩列表由游戏向 Steam 获取，与模组的页面自动确认分别处理。日志中的 `steam_leaderboard load` 记录 Steam 初始化状态，`find` 记录榜单查询结果，`entries` 记录列表下载是否失败及条目数量。`initialized=False` 时，游戏不会发起查询；先检查 Steam 客户端与启动方式。

本机直接启动 EXE 时曾复现 Steam 未初始化、结果页列表空白。云同步恢复后，通过 Steam 启动同一份模组，已确认初始化成功、榜单查找成功并下载 300 条记录；手动结果页正常显示且持续保留。替换 DLL 后应通过正常 Steam/R2 启动路径打开游戏。Steam 云同步提示由用户处理，模组不代选存档。


## 配置

配置文件：`<BepInEx 根目录>/config/mlj.tfwr.oracle-runner.cfg`。

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `Enabled` | `true` | 启用执行器 |
| `TargetScriptName` | `lb_start` | 请求未指定目标时使用的脚本名 |
| `AutoPlayMainMenu` | `false` | 没有外部请求时是否自动进入工作区；请求准备不受此项限制 |
| `StartupPollIntervalMs` | `250` | 状态文件同步间隔，最小生效值为 50ms |
| `ScriptReadyTimeoutSeconds` | `30` | 每个请求等待工作区、空闲执行器及脚本窗口的期限 |
| `DefaultRequestTimeoutSeconds` | `20` | 请求未指定超时时使用的秒数 |
| `RequestStopGracePeriodSeconds` | `3` | 停止较慢时输出进度提示的等待时间 |

## 文件协议

状态文件位于 `<BepInEx 根目录>/config/mlj.tfwr.oracle-runner.state.json`，只承载控制状态。最小请求如下：

```json
{
  "request_id": 1,
  "status": "requested",
  "target_script": "my_script",
  "timeout_seconds": 20,
  "started_at": null,
  "finished_at": null,
  "last_error": null
}
```

- `request_id` 为递增的非负 32 位整数；分配新 ID 和提交必须在同一次锁内完成。
- `timeout_seconds` 为非负有限秒数；`0` 表示不限时，`null` 使用模组默认值。
- `command` 缺省或为 `run` 时执行脚本；`prepare` 与 `quit` 为独立控制请求，不读取 `target_script`。模组写回 `protocol_version=2` 表示支持这些命令。
- 脚本正常流转为 `idle → requested → running → done/failed → idle`；快速控制请求可直接从 `requested` 写回带起止时间的终态。
- `requested` 或 `running` 可写入同一请求的 `stop_requested`；停止完成后进入 `failed`，`last_error` 保存停止原因。
- 更大的请求 ID 替换旧请求。旧客户端观察到更大 ID 后按 `superseded` 结束，不再确认或清除新请求。
- 模组的状态修改先排队，在下一次同步时落盘；执行监控和 leaderboard 观察仍逐帧进行。

两端通过独占创建 `<状态文件>.lock` 来保护读改写：C# 使用 `FileMode.CreateNew`，Python 使用 `O_CREAT | O_EXCL`。持锁期间重新读取状态，写入同目录临时文件并原子替换，最后释放锁。模组遇到占用或 I/O 错误时等待下一次轮询，不在主线程 sleep；客户端进行有限重试。

自写客户端须遵守相同的锁协议；直接覆盖 JSON 不具备并发保护。取消和终态确认还必须核对当前请求 ID。可复用 Python 模块中的 `request_script_run`、`request_script_stop` 与 `acknowledge_terminal_state`。

如果进程异常退出并留下 `.lock`，先停止游戏和全部客户端，再移除该残留锁并重新启动。程序不会按锁龄自动抢锁。无效 JSON 或未知状态会报告错误，不会被当成新会话重置。

## 输出

- 游戏 `output.txt`：脚本打印和游戏原生输出；从 `TFWR_SAVE_ROOT` 推导。运行中默认不读取，避免抢占游戏写入句柄。
- `<BepInEx 根目录>/LogOutput.log`：模组生命周期、leaderboard 完成轮/汇总、每秒 `item_snapshot` 和失败诊断。模组在同步终态前刷新磁盘日志。
- Unity `Player.log`：引擎日志和异常堆栈；与游戏 `output.txt` 同处持久数据根目录，诊断时与 BepInEx 日志一起检查。

客户端按字节偏移读取新增完整日志行，保留跨次读取的半行；文件替换或缩短时重读。已启动请求的 `output.txt` 会被游戏清空，因此结束后从头读取；启动前失败只读追加诊断。最终在文件事务中回读三份输出并确认同一请求，防止新请求清空输出。

轮内百分比和 `estimated_total_game_seconds` 是库存净增长预测，不能代替 leaderboard 成绩。批量收获前可能无法估算；首轮完成后显示真实完成轮均值，取消摘要不混入成绩。

## 显示帧率与 VSync

如果 Unity `Player.log` 出现 `using refresh rate causes time drift` 或 `vsync is broken`，同时开启垂直同步后实际 FPS 仍高达数百，可在游戏内按 `Esc → 选项 → 图像 → 帧数`，改为固定 `60 fps`。返回工作区，确认画面上的 FPS 接近60，并继续检查 `Player.log` 与 BepInEx `LogOutput.log` 是否新增相同提示。

这是 Unity 显示计时的回退提示。固定帧率是本机已验证的处理方式，无需重启游戏或给模组增加全局图形补丁；实际设置由游戏保存到持久数据目录的 `options.txt`。显示帧率、现实计算速度与脚本游戏时间分别记录，不用 FPS 代替策略成绩。

## 构建与打包

使用 Windows .NET SDK，并通过属性指定游戏目录和 BepInEx 5 目录。BepInEx 目录可来自 R2 profile，也可来自解压后的 BepInExPack：

```powershell
dotnet build oracle_runner_mod/TFWROracleRunner.csproj -c Release -p:TFWRGameRoot="D:\Steam\steamapps\common\The Farmer Was Replaced" -p:TFWRBepInExRoot="C:\path\to\profile\BepInEx"
```

WSL 中使用 `dotnet.exe`，两个属性仍传 Windows 路径。MSBuild 也读取进程环境变量 `TFWR_GAME_ROOT` 与 `TFWR_BEPINEX_ROOT`，但不会读取仓库 `.env`。

生成 Thunderstore/R2 ZIP：

```powershell
dotnet build oracle_runner_mod/TFWROracleRunner.csproj -c Release -t:PackageThunderstore -p:TFWRGameRoot="D:\Steam\steamapps\common\The Farmer Was Replaced" -p:TFWRBepInExRoot="C:\path\to\profile\BepInEx"
```

输出位于 `oracle_runner_mod/bin/Release/netstandard2.1/`。ZIP 包含 manifest、README、MIT 许可证、图标与本模组 DLL；加载器由依赖包提供，游戏程序集仅用于编译引用。

## 许可证

本模组采用 MIT 许可证，完整条款见包内 `LICENSE`。BepInEx、Harmony 和游戏程序集的许可由各自权利人提供。
