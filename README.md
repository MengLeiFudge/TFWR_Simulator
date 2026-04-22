# TFWR Oracle Workflow Workspace

这个仓库现在的主线不是本地 parity simulator，而是“真实游戏 oracle 工作流”：

- `oracle_runner_mod/`
  - Unity / BepInEx 模组
  - 常驻轮询 `BepInEx/config/mlj.tfwr.oracle-runner.state.json`
  - 在真实游戏里执行 `lb_start`
  - 把生命周期日志与 leaderboard 每轮/平均时间写到 `BepInEx/LogOutput.log`

- `python/tfwr_orchestrator/`
  - Python 子项目
  - 负责配置解析、脚本部署、`lb_start.py` 生成、状态机请求、双通道输出读取

- `references/leaderboard_scripts/`
  - 仓库内的 `lb_*.py` 真源

- `leaderboard/`
  - 指向真实 `Save0` 的本地链接目录

- `tools/`
  - 根目录薄包装器
  - 只负责把 `python/tfwr_orchestrator/src` 加入 `sys.path` 并转调新包

## 目录结构

```text
oracle_runner_mod/                 Unity / BepInEx 模组
python/
└── tfwr_orchestrator/             Python 主项目
references/
├── DecompiledSource/              反编译源码参考
└── leaderboard_scripts/           仓库内 lb_*.py 真源
tools/                             根目录薄包装器
leaderboard/                       指向真实 Save0 的链接目录
```

## 本地配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中设置：

```env
TFWR_SAVE_ROOT=C:\Users\MLJ\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
```

- `TFWR_SAVE_ROOT` 用于：
  - `leaderboard/` 链接重建
  - 游戏 `output.txt` 路径推导
- `TFWR_GAME_ROOT` 用于：
  - `state.json` 路径推导
  - `BepInEx/LogOutput.log` 路径推导
  - 反编译 / snapshot 提取

`.env` 不进 git；如果 shell 已经设置了 `TFWR_SAVE_ROOT` / `TFWR_GAME_ROOT`，代码会优先使用环境变量。

## 核心工作流

### 1. 重建 `leaderboard/` 链接

```bash
python3 tools/refresh_leaderboard_link.py
```

### 2. 把单个榜单脚本部署到真实 `Save0`

默认不再全量同步所有 `lb_*.py`。  
默认只同步单个目标脚本，并在目标存档里生成派生入口 `lb_start.py`。

```bash
python3 tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
```

显式全量同步时才使用 `--all`：

```bash
python3 tools/sync_leaderboard_scripts.py cur2save --all
```

### 3. 通过 Unity 模组请求真实游戏执行

```bash
python3 tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

Python 协调器会：

1. 启动或复用游戏进程
2. 等待 `state.json` 进入 `idle`
3. 记录两路输出的起始签名
4. 写入 `requested`
5. 等待 `done / failed / superseded`
6. 读取本次请求新增的两路输出

## 双通道输出

`python/tfwr_orchestrator` 现在会同时读取：

- 游戏 `output.txt`
  - 承接脚本 `print(...)`
  - 承接 probe / 游戏原生文本结果

- `BepInEx/LogOutput.log`
  - 承接模组生命周期日志
  - 承接 leaderboard `start / run / summary`
  - 承接超时、取消、失败诊断

不要再把这两路输出混成一个“统一 output”概念。

## 其他工具

```bash
python3 tools/refresh_decompiled_sources.py --help
python3 tools/extract_unlock_snapshot.py --help
python3 tools/extract_leaderboard_snapshot.py --help
```

这些根脚本也都只做薄包装，真实逻辑在 `python/tfwr_orchestrator/src/tfwr_orchestrator/`。

## 测试

Python 主项目测试：

```bash
PYTHONPATH=python/tfwr_orchestrator/src python3 -m unittest discover -s python/tfwr_orchestrator/tests -p 'test_*.py' -v
```

兼容入口：

```bash
python3 -m unittest tests.test_tooling -v
```
