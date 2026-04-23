# TFWR Oracle Runner

基于 `BepInEx 6 + HarmonyX` 的常驻 Unity 权威执行器。

如果你只想知道“整个仓库第一次怎么配起来”，先看仓库根目录 `README.md`。  
这里专门说明模组本身的职责、安装方式、配置项和状态机协议。

## 模组职责

- 打开游戏后自动调用真实 `Menu.Play()`
- 常驻轮询 `mlj.tfwr.oracle-runner.state.json`
- 定位目标脚本窗口并直接调用真实 `MainSim.StartMainExecution(...)`
- 请求执行超时后自动 `StopMainExecution()`
- 新请求到来时自动覆盖旧请求
- 把结果回写成 `done / failed / superseded`
- 把生命周期日志和 leaderboard 输出写到 `BepInEx/LogOutput.log`

## 与 Python 协调器的配合关系

默认协作链路是：

1. `tfwr_orchestrator` 写入 `requested`
2. 模组读取 `target_script` 与 `timeout_seconds`
3. 模组在真实游戏内执行目标脚本窗口
4. 模组把终态写回 `done / failed / superseded`
5. `tfwr_orchestrator` 读取：
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`

默认目标脚本是 `lb_start`，不带 `.py`。

## 构建

```bash
dotnet build oracle_runner_mod/TFWROracleRunner.csproj
```

如果你的游戏安装目录不是默认的 `/mnt/d/Steam/steamapps/common/The Farmer Was Replaced`，可以显式传：

```bash
dotnet build oracle_runner_mod/TFWROracleRunner.csproj -p:TFWRGameRoot=/your/game/root
```

## 安装

1. 给游戏安装 `BepInEx 6` 的 Mono 版本。
2. 编译后把：

```text
oracle_runner_mod/bin/<Config>/netstandard2.1/TFWROracleRunner.dll
```

复制到：

```text
<TFWR_GAME_ROOT>/BepInEx/plugins/TFWROracleRunner/
```

3. 首次运行后检查配置文件：

```text
<TFWR_GAME_ROOT>/BepInEx/config/mlj.tfwr.oracle-runner.cfg
```

## 关键配置项

- `Enabled=true`
- `TargetScriptName=lb_start`
- `AutoPlayMainMenu=true`
- `DefaultRequestTimeoutSeconds=20`
- `RequestStopGracePeriodSeconds=3`

注意：

- `TargetScriptName` 不带 `.py`
- Python 协调器默认也按 `lb_start` 协作

## 状态机文件

状态文件路径固定为：

```text
<TFWR_GAME_ROOT>/BepInEx/config/mlj.tfwr.oracle-runner.state.json
```

最小示例：

```json
{
  "request_id": 1,
  "status": "requested",
  "target_script": "lb_start",
  "timeout_seconds": 20,
  "started_at": null,
  "finished_at": null,
  "last_error": null
}
```

状态流转：

- `idle`
- `requested`
- `running`
- `done`
- `failed`
- `superseded`

## 输出

模组侧输出主要落在：

```text
<TFWR_GAME_ROOT>/BepInEx/LogOutput.log
```

这里承接：

- 模组生命周期日志
- leaderboard `start / run / summary`
- 超时、取消、失败诊断
