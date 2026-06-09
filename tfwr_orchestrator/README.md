# tfwr_orchestrator

`tfwr_orchestrator` 是本仓库里负责真实游戏 oracle 工作流的 Python 子项目。

如果你只想知道“第一次怎么把整个仓库跑起来”，先看仓库根目录 `README.md`。  
如果你要继续看 Python 协调器到底负责什么、CLI 怎么分工、路径怎么推导，看这里。

## 子项目职责

它负责三类事情：

1. 解析 `.env` / `TFWR_SAVE_ROOT` / `TFWR_GAME_ROOT`
2. 部署 leaderboard 脚本，并在部署到真实存档时生成派生入口 `lb_start.py`
3. 通过 `state.json` 请求 Unity 模组执行脚本，并读取：
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`

## 目录约定

- `src/tfwr_orchestrator/`
  - 真实业务逻辑
- `tools/*.py`
  - CLI 入口
  - 只负责参数接线，不重复实现业务逻辑
- `tests/`
  - Python 测试

当前核心实现文件：

- `src/tfwr_orchestrator/config.py`
- `src/tfwr_orchestrator/leaderboard_sync.py`
- `src/tfwr_orchestrator/real_game_runner.py`
- `src/tfwr_orchestrator/output_capture.py`

## 配置输入与路径推导

配置默认来自仓库根目录 `.env`：

- `TFWR_SAVE_ROOT`
  - 指向真实 `Save0`
  - 用于推导 `gamesave/`
  - 用于推导游戏 `output.txt`
- `TFWR_GAME_ROOT`
  - 指向游戏安装目录
  - 用于推导 `BepInEx/config/mlj.tfwr.oracle-runner.state.json`
  - 用于推导 `BepInEx/LogOutput.log`

补充说明：

- 如果 shell 已设置同名环境变量，代码会优先使用环境变量
- 在 WSL 中运行时，可以直接保留 `C:\...` / `D:\...` 写法，`config.py` 会自动转换为 `/mnt/c/...` / `/mnt/d/...`
- 仓库根目录真实存档链接目录名固定为 `gamesave/`

## CLI 入口

### `refresh_gamesave_link.py`

重建仓库根目录 `gamesave/` 到真实 `Save0` 的链接：

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
```

### `sync_leaderboard_scripts.py`

同步榜单脚本。默认只同步单个目标脚本：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
```

当目标目录是 `gamesave/` 时，会额外生成：

- `lb_start.py`

只有显式传 `--all` 时，才全量同步全部 `lb_*.py`：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --all
```

### `run_real_game_script.py`

启动或复用真实游戏，通过状态机请求模组执行目标脚本：

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

默认流程：

1. 启动或复用游戏进程
2. 等待模组状态机进入可请求状态
3. 写入 `requested`
4. 运行中轮询 `LogOutput.log` 与状态机，避免高频读取游戏 `output.txt`
5. 等待 `done / failed / superseded`
6. 请求结束后回读本次新增的 `output.txt` 与 `LogOutput.log`

`--status-only` 在状态机仍是 `running` 时默认跳过游戏 `output.txt`，避免和游戏原生 Logger 的 `Clear` / `WriteLog` 抢文件句柄；需要强制读取时显式加 `--include-game-output`。

### 资源快照与反编译工具

```bash
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
python3 tfwr_orchestrator/tools/extract_leaderboard_snapshot.py --help
```

科技事实表默认固化到 `references/unlocks/`：

```bash
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format json --output references/unlocks/unlock_snapshot.json
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format markdown --output references/unlocks/unlock_snapshot.md
```

## 双通道输出职责

不要把两路输出混成一个“统一 output”概念：

- 游戏 `output.txt`
  - 承接脚本 `print(...)`
  - 承接 probe / 游戏原生文本
  - 请求运行中不要高频轮询，避免和游戏原生 Logger 写入冲突
- `BepInEx/LogOutput.log`
  - 承接模组生命周期日志
  - 承接 leaderboard `start / run / summary`
  - 承接运行中 `item_snapshot` 与停表判断
  - 承接超时、取消、失败诊断

## 最小联调顺序

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

## 验证

帮助命令：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py --help
python3 tfwr_orchestrator/tools/run_real_game_script.py --help
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
python3 tfwr_orchestrator/tools/extract_leaderboard_snapshot.py --help
```

开发期测试：

```bash
PYTHONPATH=tfwr_orchestrator/src python3 -m unittest discover -s tfwr_orchestrator/tests -p 'test_*.py' -v
```
