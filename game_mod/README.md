# TFWR Oracle Runner

让外部 Python 工具、编辑器和自动化程序调用 The Farmer Was Replaced 的真实脚本执行入口，并收集执行状态、leaderboard 时间和资源快照。

模组通过 BepInEx 5 与 Harmony 接入游戏。Thunderstore 依赖为 `BepInEx-BepInExPack-5.4.2305`。它执行存档中已有的脚本窗口，不提供外部 Python 解释器。

客户端和本地模拟器从 GitHub 仓库取得，Thunderstore 包只安装游戏模组。后台控制接口需要支持协议2的DLL。

当前源码面向 Steam 构建26462009编译，原生输出使用当前`MainSim`的实例日志器。游戏的`Saver.Save(MainSim)`已改为返回`Task<bool>`；使用旧`bool`签名的DLL会报`MissingMethodException`，并阻断包括`prepare`在内的请求。`quit`等待保存成功后才发布完成状态，并在同一请求终态落盘后退出。需用当前游戏程序集重新编译并替换 DLL 后重启游戏加载；该修复已随 0.2.3 及之后的公开包发布。

## 后台控制

`prepare` 结束当前执行、确认已有结果页并进入工作区，返回 `workspace_ready=true`。普通脚本请求也会从主菜单自动进入工作区；已有脚本仍在执行时，普通请求继续等待，不主动中断。

`quit` 先停止执行，再调用游戏保存和退出入口；保存出现确认窗口时保留游戏并报告失败。模组先持久化请求终态再退出，客户端确认进程消失后返回 `game_exited=true`。任务结束且近期不再实机验证时调用它。

```bash
python3 game_control/tools/run_real_game_script.py --action prepare
python3 game_control/tools/run_real_game_script.py --action quit
```

有活动外部请求时，须显式加 `--replace`；已有终态须先收取结果。没有外部请求时保留手动游玩的主菜单和排行榜结果页。

## 版本历史

各版本变更见 [CHANGELOG.md](CHANGELOG.md)。

仓库中的本地模拟器只提供预测，精度与已验证范围见[模拟器验收与限制](https://github.com/MengLeiFudge/TFWR_Simulator/blob/master/simulator/headless/validation.md)。候选策略仍须真实游戏确认。

## 安装到 R2

1. 在 r2modman 的 TFWR profile 中安装上述 BepInExPack。
2. 在 R2 的在线模组列表中搜索 `TFWR_Oracle_Runner`，选择作者 `MengLei` 的包并安装。也可导入发布 ZIP。
3. 通过 R2 的模组启动入口打开游戏，或按下述 INI 配置经 Steam 启动；外部请求负责进入工作区。
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

先加载该 profile 的游戏，再调用 `prepare` 或提交脚本。使用 R2 profile 时，Python 客户端只连接已有游戏进程；代理可按实机任务授权执行以下启动步骤。

经 Steam 使用 R2 已安装的模组时：

1. 在游戏关闭时备份游戏目录的 `doorstop_config.ini`。
2. 保持 `enabled = true`，将 `target_assembly` 改为所选 `TFWR_BEPINEX_ROOT` 下 `core\BepInEx.Preloader.dll` 的 Windows 绝对路径，并确认 DLL 存在。目标是 BepInEx Preloader，不是 Oracle 插件 DLL。
3. 通过 Steam 库启动游戏，或打开 `steam://rungameid/2060160`。
4. 检查所选 profile 的新 `LogOutput.log`，确认 Oracle 已加载、`state_file` 路径正确；榜单运行后另核对 Steam 初始化与提交结果。
5. 任务结束使用 `--action quit` 保存并正常退出。云存档冲突由用户选择，不代选。

查询状态：

```bash
python3 game_control/tools/run_real_game_script.py --status-only
```

运行已有脚本 `my_script.py`，等待完成后打印结果：

```bash
python3 game_control/tools/run_real_game_script.py --target-script my_script --total-timeout 600
```

只提交请求并立即退出：

```bash
python3 game_control/tools/run_real_game_script.py --target-script my_script --total-timeout 60 --request-only
```

`--request-only` 默认拒绝覆盖活动请求；明确替换须加 `--replace`。终态 `done`/`failed`/`superseded` 不是活动请求，可直接被新请求覆盖。AI调用推荐 `--action submit/status/wait/cancel/result/health` 的JSON任务接口，支持幂等提交和结果留存，沿用当前DLL协议。常规文本等待模式先等待 `idle`。本仓库打榜使用 `lb_start` 派生入口；参数与任务生命周期见 [协调器说明](https://github.com/MengLeiFudge/TFWR_Simulator/blob/master/game_control/README.md)。

## 榜单页面与 Steam 数据

手动运行结束后，结果页保留到用户按 OK 或 Esc。外部请求开始前会先确认已有结果页；外部请求产生的结果页由模组自动确认。`simulate()` 共用游戏运行浮层，但不会获得关闭之后手动结果页的权限。

结果页右侧的成绩列表由游戏向 Steam 获取，与模组的页面自动确认分别处理。日志中的 `steam_leaderboard load` 记录 Steam 初始化状态，`find` 记录榜单查询结果，`entries` 记录列表下载是否失败及条目数量。`initialized=False` 时，游戏不会发起查询；先检查 Steam 客户端与启动方式。

本机直接启动 EXE 时曾复现 Steam 未初始化、结果页列表空白。云同步恢复后，通过 Steam 启动同一份模组，已确认初始化成功、榜单查找成功并下载 300 条记录；手动结果页正常显示且持续保留。替换 DLL 后应通过正常 Steam/R2 启动路径打开游戏。Steam 云同步提示由用户处理，模组不代选存档。


## 配置

配置文件：`<BepInEx 根目录>/config/mlj.tfwr.oracle-runner.cfg`。

`General` 段是日常会动的开关，`Advanced` 段是执行器内部时序，一般不用改。

| 段 | 配置项 | 默认值 | 用途 |
| --- | --- | --- | --- |
| General | `Enabled` | `true` | 启用执行器 |
| General | `AutoPlayMainMenu` | `false` | 没有外部请求时是否自动进入工作区；请求准备不受此项限制 |
| General | `AutoOkLeaderboardResult` | `false` | 排行榜结果页一出现就按 OK，供等"运行结束"的外部队列使用 |
| Advanced | `DefaultTargetScript` | `lb_start` | 请求未给 `target_script` 时使用的脚本窗口 |
| Advanced | `StartupPollIntervalMs` | `250` | 状态文件同步间隔，最小生效值 50ms |
| Advanced | `ScriptReadyTimeoutSeconds` | `0` | 等待工作区、空闲执行器或停止生效的现实秒上限，范围0～3600；0表示不限时，请求保持 `requested` |
| Advanced | `MaxRunSeconds` | `0` | 单次 `run` 无条件生效的现实秒上限，范围0～86400；0表示不限时。按运行时长判断，不检测客户端存活 |
| Advanced | `SaveTimeoutSeconds` | `10` | 保存等待上限，范围0～60秒；0表示不限时 |
| Advanced | `RequestStopGracePeriodSeconds` | `3` | 停止后等待 `StopMainExecution()` 生效的观察窗口 |

## 文件协议

状态文件位于 `<BepInEx 根目录>/config/mlj.tfwr.oracle-runner.state.json`，只承载控制状态。最小请求如下：

```json
{
  "request_id": 1,
  "status": "requested",
  "target_script": "my_script",
  "started_at": null,
  "finished_at": null,
  "last_error": null
}
```

- `request_id` 为递增的非负 32 位整数；分配新 ID 和提交必须在同一次锁内完成。
- `run` 没有时间参数：模组启动脚本后一直观察到它自然结束，再写 `done`；客户端要停止就写同请求的 `stop_requested`。防止客户端掉线后无限运行只用配置 `Advanced.MaxRunSeconds`，默认0表示不限。
- `command` 缺省或为 `run` 时执行脚本。控制命令：`prepare`（停在空闲工作区）、`save`（只存档，游戏继续）、`quit`（存档确认后退出，等于 `save` 加退出）、`play`、`stop`、`ok`、`open`、`close`、`minimize`、`unminimize`、`dock`、`arrange`、`list`。模组写回 `protocol_version=4`。
- `minimize`/`unminimize` 收放单个窗口；`dock` 只把 `target_script` 挂到 `second_script` 链尾；`arrange` 把所有窗口按名字排序挂成一列，锚点取 `target_script`（缺省 `stand`）。
- 即时命令 `play`、`stop`、`ok`、`list`、`minimize`、`unminimize` 不等待空闲，收到请求的当帧完成并写回终态；其中 `stop` 主动停止当前程序。
- `save`、`quit` 与 `open`、`close`、`dock`、`arrange` 共用异步保存流程，等保存确认后才写终态；保存等待只使用 `Advanced.SaveTimeoutSeconds`。超时、保存未确认或警告弹窗未关闭时记为失败并保留现场；后台保存可能继续完成。取消或被新请求替换后不再退出游戏，不回滚已经开始的磁盘保存。保存期间状态文件丢失会记录警告并撤销退出；状态读取失败时保留等待句柄并定期警告，待恢复读取后继续处理。
- `open` 读取 `code_file` 指定的源码（超过 1 MB 拒绝），按 `second_script`（缺省 `stand`）停靠；`open/close/minimize/unminimize/dock` 必须指定 `target_script`，`dock` 另需 `second_script`。`arrange` 用 `target_script`（缺省 `stand`）作首窗口，先解除其停靠再排列；`list` 把窗口清单写进 `result_text`。
- `protocol_version` 只由模组发布，客户端只读；请求里带不带都不影响执行。模组收到不认识的 `command` 时写 `failed`，旧DLL遇到新命令同样报未知命令，所以不需要客户端先声明版本。
- 重复或落后的 `request_id` 不再静默丢弃：模组写 `failed`，`last_error` 说明当前已处理到哪个编号，客户端应改用更大的ID。
- 工作区已就绪却没有目标窗口时立即 `failed`；其余等待（未进工作区、别的脚本在跑、确认弹窗未关闭）持续保持 `requested`，要兜底就把 `ScriptReadyTimeoutSeconds` 设为正数。
- 终态 `done`/`failed`/`superseded` 不是活动请求，可直接被更大的新请求覆盖；`requested`/`running`/`stop_requested` 才是活动请求。模组不会自动归档旧结果，本仓库客户端在覆盖前要求旧结果已归档（见 [协调器说明](https://github.com/MengLeiFudge/TFWR_Simulator/blob/master/game_control/README.md)）。
- 实时字段 `executing`、`leaderboard_running`、`leaderboard_screen`、`saving`、`busy_windows` 每轮刷新，与请求字段互不覆盖；`saving` 直接取原版 `Saver.IsSaving`，请求超时或取消后仍反映后台写盘，改写存档前必须等它为 `false`；`busy_windows` 只报模组已知的运行窗口，手工运行其它窗口时可能为空。
- 配置 `AutoOkLeaderboardResult=true` 时，结果页一出现就按 OK，供等“运行结束”的外部脚本使用；不开启时仍只关闭属于本模组请求的结果页。
- 脚本正常流转为 `idle → requested → running → done/failed`；回到 `idle` 是客户端为了让状态文件可读的自选动作，模组不强制。快速控制请求可直接从 `requested` 写回带起止时间的终态。
- `requested` 或 `running` 可写入同一请求的 `stop_requested`；停止完成后进入 `failed`，`last_error` 保存停止原因。
- 更大的请求 ID 替换旧请求；模组本身不写 `superseded`，由客户端观察到更大 ID 后自行判定，不再确认或清除新请求。
- 模组的状态修改先排队，下一次同步将请求快照与实时字段合并后一次原子落盘；写入失败保留快照重试。执行监控和 leaderboard 观察仍逐帧进行。

两端通过独占创建 `<状态文件>.lock` 来保护读改写：C# 使用 `FileMode.CreateNew`，Python 使用 `O_CREAT | O_EXCL`。持锁期间重新读取状态，写入同目录临时文件并原子替换，最后释放锁。模组遇到占用或 I/O 错误时等待下一次轮询，不在主线程 sleep；客户端进行有限重试。

自写客户端须遵守相同的锁协议；直接覆盖 JSON 不具备并发保护。取消和终态确认还必须核对当前请求 ID。可复用 Python 模块中的 `request_script_run`、`request_script_stop` 与 `acknowledge_terminal_state`。

如果进程异常退出并留下 `.lock`，先停止游戏和全部客户端，再移除该残留锁并重新启动。程序不会按锁龄自动抢锁。无效 JSON 或未知状态会报告错误，不会被当成新会话重置。

## 为什么这样设计

游戏实例和本地模拟器不是同一种东西，协议按这个区别定形：

- **单实例、串行**：同一时刻只有一个脚本在跑，进工作区、结果页、存档都耦合在同一时间线上；本地模拟可以多核铺满、几分钟出一个榜，游戏里同一件事可能两小时。所以游戏侧只给异步命令——投递即返回，客户端按ID轮询，想什么时候回来读都行。
- **游戏秒与现实秒**：成绩口径只有游戏秒（排行榜一轮 7200 游戏秒），加速只改变现实秒。运行本身因此没有"时间上限"语义，脚本自己决定何时结束。现实秒只出现在三个兜底配置里（`SaveTimeoutSeconds`、`ScriptReadyTimeoutSeconds`、`MaxRunSeconds`），默认都设为不限时。
- **强终不产生成绩**：被外部时钟掐掉的运行是未完成，写 `failed`；只有脚本自然结束才写 `done` 并被客户端当成结果。
- **失败代价不对称**：本地一次失败几分钟，改参数重跑即可；游戏一次失败废掉一轮两小时，还可能污染榜单成绩。所以请求ID递增、终态只由模组写、结果与终态分开保存，都是为了事后能核对到底发生了什么。
- **墙钟只防跑飞**：只有客户端掉线、脚本死循环这类异常才需要外部时钟介入，因此这些上限默认关闭或给足余量，不参与成绩语义。

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
dotnet build game_mod/TFWROracleRunner.csproj -c Release -p:TFWRGameRoot="D:\Steam\steamapps\common\The Farmer Was Replaced" -p:TFWRBepInExRoot="C:\path\to\profile\BepInEx"
```

WSL 中使用 `dotnet.exe`，两个属性仍传 Windows 路径。MSBuild 也读取进程环境变量 `TFWR_GAME_ROOT` 与 `TFWR_BEPINEX_ROOT`，但不会读取仓库 `.env`。

也可在 Windows 执行 `scripts\packaging\build_mod.cmd`，入口通过 Python 协调器读取仓库 `.env` 和现有环境变量，定位仓库、游戏与BepInEx；需要Windows Python 3（`py -3`）及PATH中的 `dotnet.exe`。额外MSBuild参数可跟在命令后面。

生成 Thunderstore/R2 ZIP：

```powershell
dotnet build game_mod/TFWROracleRunner.csproj -c Release -t:PackageThunderstore -p:TFWRGameRoot="D:\Steam\steamapps\common\The Farmer Was Replaced" -p:TFWRBepInExRoot="C:\path\to\profile\BepInEx"
```

输出位于 `game_mod/bin/Release/netstandard2.1/`。ZIP 包含 manifest、README、MIT 许可证、图标与本模组 DLL；加载器由依赖包提供，游戏程序集仅用于编译引用。

发布用 `scripts\packaging\publish_mod.ps1`：默认 `-Check` 核对版本号四处一致与包内文件字节一致，`-Publish` 上传并核对远端结果，`-Verify` 只核对已发布版本。激活状态以包接口的 `latest` 为准，版本接口发布后有几秒到几分钟缓存延迟；等待总时长由 `-WaitSeconds` 限制（默认 30）。

## 许可证

本模组采用 MIT 许可证，完整条款见包内 `LICENSE`。BepInEx、Harmony 和游戏程序集的许可由各自权利人提供。
