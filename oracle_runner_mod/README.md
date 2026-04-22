# TFWR Oracle Runner

基于 `BepInEx 6 + HarmonyX` 的常驻 Unity 权威执行器。

## 目标

- 打开游戏后自动调用真实 `Menu.Play()`
- 常驻轮询 `mlj.tfwr.oracle-runner.state.json`
- 定位目标脚本窗口并直接调用真实 `MainSim.StartMainExecution(...)`
- 请求执行超时后自动 `StopMainExecution()`
- 新请求到来时自动覆盖旧请求
- 把结果回写成 `done / failed / superseded`

## 构建

```bash
dotnet build oracle_runner_mod/TFWROracleRunner.csproj
```

如果你的游戏安装目录不是默认的 `/mnt/d/Steam/steamapps/common/The Farmer Was Replaced`，可以显式传：

```bash
dotnet build oracle_runner_mod/TFWROracleRunner.csproj -p:TFWRGameRoot=/your/game/root
```

## 安装

1. 给游戏安装 `BepInEx 6` 的 Mono 版本
2. 编译后把 `oracle_runner_mod/bin/<Config>/netstandard2.1/TFWROracleRunner.dll` 复制到：

```text
BepInEx/plugins/TFWROracleRunner/
```

3. 首次运行后编辑配置文件：

```text
BepInEx/config/mlj.tfwr.oracle-runner.cfg
```

关键项：

- `Enabled=true`
- `TargetScriptName=lb_start`
- `AutoPlayMainMenu=true`
- `DefaultRequestTimeoutSeconds=20`
- `RequestStopGracePeriodSeconds=3`

注意：`TargetScriptName` 不带 `.py`。

## 状态机文件

状态文件路径固定为：

```text
BepInEx/config/mlj.tfwr.oracle-runner.state.json
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
