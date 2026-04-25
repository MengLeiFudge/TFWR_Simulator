# TFWR Oracle Workflow Workspace

这个仓库的主线是“真实游戏 oracle 工作流 + leaderboard 优化”，不是旧的本地 parity simulator。

如果你要在真实游戏里部署某个 `lb_*.py`、请求执行、读取结果、继续调榜，这里就是主入口。

## 仓库分工

- `references/leaderboard_scripts/`
  - `lb_*.py` 与同名 `lb_*.md` 的长期真源
- `references/unlocks/`
  - 从真实游戏资源和反编译逻辑生成的科技事实表
  - 打榜脚本的科技顺序、前置和成本判断优先参考这里
- `tfwr_orchestrator/`
  - Python 协调器
  - 负责路径解析、脚本部署、`lb_start.py` 生成、真实执行请求、双通道输出读取
- `oracle_runner_mod/`
  - Unity / BepInEx 模组
  - 负责轮询 `state.json` 并在游戏内执行 `lb_start`
- `gamesave/`
  - 指向本机验证用 `Save0` 的本地链接目录
  - 只作为部署目标，不是 git 真源

文档入口按层级分工：

- `README.md`
  - 仓库级入口
  - 承接第一次使用时的前期布置和最小工作流
- `tfwr_orchestrator/README.md`
  - Python 协调器细节
  - 承接 CLI、路径推导、双输出职责
- `oracle_runner_mod/README.md`
  - Unity / BepInEx 模组细节
  - 承接构建、安装、配置项、状态机协议
- `references/leaderboard_scripts/README.md`
  - 榜单脚本与策略文档的长期维护约定

## 使用前先明确的约定

1. 这个仓库默认面向“每个协作者都有自己的验证用存档和游戏安装目录”的工作流。
2. `references/leaderboard_scripts/` 才是 `lb_*.py` 的 git 真源；不要把 `gamesave/` 当成长久源码目录。
3. `lb_start.py` 是部署时生成的派生入口，不是手工维护的长期真源。
4. 真实结果优先级高于仓库推断；如果仓库逻辑和游戏实际输出冲突，应以真实结果为准。

## 第一次使用时的前期布置

### 1. 准备运行环境

- Python `>=3.11`
- The Farmer Was Replaced 本体
- 一个可用于验证的真实 `Save0`
- `BepInEx 6` Mono 版
- 如果你要自己编译模组，再准备可用的 `dotnet` SDK

### 2. 准备验证用 `Save0`

建议单独准备一个验证存档，不要直接拿你唯一在玩的正式存档做实验。

仓库默认假设：

- 你已经有一个可运行、可打榜的真实存档
- `.env` 会指向你自己的验证用 `Save0`
- 不同协作者可以各自指向不同的本地验证存档

### 3. 配置仓库根目录 `.env`

先复制：

```bash
cp .env.example .env
```

然后填写：

```env
TFWR_SAVE_ROOT=C:\Users\MLJ\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
```

说明：

- `TFWR_SAVE_ROOT`
  - 指向验证用 `Save0`
  - 用于重建 `gamesave/`
  - 也用于推导游戏 `output.txt`
- `TFWR_GAME_ROOT`
  - 指向游戏安装目录
  - 用于推导 `BepInEx/config/mlj.tfwr.oracle-runner.state.json`
  - 也用于推导 `BepInEx/LogOutput.log`

补充约定：

- `.env` 仅用于本地，不进 git
- 如果 shell 已设置同名环境变量，代码会优先使用环境变量
- 在 WSL 中运行时，可以直接保留 `C:\...` / `D:\...` 写法，Python 侧会自动转换为 `/mnt/c/...` / `/mnt/d/...`

### 4. 安装或更新 Unity / BepInEx 模组

先给游戏安装 `BepInEx 6` Mono 版。

如果需要自己编译模组：

```bash
dotnet build oracle_runner_mod/TFWROracleRunner.csproj
```

然后把生成的 `TFWROracleRunner.dll` 放到：

```text
<TFWR_GAME_ROOT>/BepInEx/plugins/TFWROracleRunner/
```

首次运行后，至少确认：

- `<TFWR_GAME_ROOT>/BepInEx/config/mlj.tfwr.oracle-runner.cfg` 已生成
- 关键配置仍指向 `lb_start`

模组的完整构建、安装、配置项和状态机说明统一放在 `oracle_runner_mod/README.md`。

### 5. 重建仓库里的 `gamesave/` 链接

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
```

执行后，仓库根目录的 `gamesave/` 应指向你在 `.env` 里配置的真实 `Save0`。

### 6. 做一次最小自检

先确认 CLI 能正常启动：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py --help
python3 tfwr_orchestrator/tools/run_real_game_script.py --help
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
```

如果这些帮助信息都能正常打印，说明 Python 侧入口至少已接好。  
更细的 CLI 职责与联调顺序统一放在 `tfwr_orchestrator/README.md`。

## 日常最小工作流

### 1. 部署单个榜单脚本

默认只部署一个目标脚本，同时生成派生入口 `lb_start.py`：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
```

只有显式传 `--all` 时才全量同步全部 `lb_*.py`：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --all
```

### 2. 请求真实游戏执行

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

协调器会启动或复用游戏进程、通过状态机写入请求，并在结束后回读本次新增输出。  
如果你要看参数说明、状态机细节和 CLI 分工，直接看 `tfwr_orchestrator/README.md`。

### 3. 区分两路输出

不要把输出混成一个“统一 output”概念：

- 游戏 `output.txt`
  - 承接脚本 `print(...)`
  - 承接 probe / 游戏原生文本
- `BepInEx/LogOutput.log`
  - 承接模组生命周期日志
  - 承接 leaderboard `start / run / summary`
  - 承接超时、取消、失败诊断

更细的读法见：

- `tfwr_orchestrator/README.md`
- `oracle_runner_mod/README.md`

## 常用命令

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
python3 tfwr_orchestrator/tools/extract_leaderboard_snapshot.py --help
```

刷新科技事实表：

```bash
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format json --output references/unlocks/unlock_snapshot.json
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format markdown --output references/unlocks/unlock_snapshot.md
```

## 测试

Python 主项目测试：

```bash
PYTHONPATH=tfwr_orchestrator/src python3 -m unittest discover -s tfwr_orchestrator/tests -p 'test_*.py' -v
```
