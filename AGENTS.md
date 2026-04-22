# TFWR Oracle Workflow 仓库约束

## 1. 项目目标

1. 本仓库当前主线是“真实游戏 oracle 工作流 + leaderboard 优化”，不是本地 parity simulator。
2. 真实执行环境由三部分组成：
   - `oracle_runner_mod/`：Unity / BepInEx 模组
   - `tfwr_orchestrator/`：Python 协调器
   - 真实游戏存档 `Save0`
3. 后续默认工作目标是：
   - 部署目标 `lb_*.py`
   - 生成派生入口 `lb_start.py`
   - 请求真实游戏执行
   - 读取双通道输出
   - 用真实结果迭代 leaderboard 脚本
4. 旧 simulator 资产已经从仓库主线清除；后续不要再把 parity simulator 当成默认开发方向。

## 2. 仓库范围与路径

1. Python 主项目路径固定为 `tfwr_orchestrator/`。
2. Python CLI 入口放在 `tfwr_orchestrator/tools/`；真实业务逻辑必须放在 `tfwr_orchestrator/src/tfwr_orchestrator/`。
3. `oracle_runner_mod/` 是 Unity/BepInEx 模组工程。
4. `references/leaderboard_scripts/` 是仓库内 `lb_*.py` 真源。
5. `gamesave/` 是指向真实 `Save0` 的本地链接目录，不进 git。
6. `references/DecompiledSource/` 是反编译参考目录。
7. 仓库内不再保留 `src/gamesimulator/` 这类旧 simulator 源码入口。

## 3. 配置与路径解析

1. 默认通过仓库根目录 `.env` 中的 `TFWR_SAVE_ROOT` 指向真实 `Save0`。
2. 默认通过仓库根目录 `.env` 中的 `TFWR_GAME_ROOT` 指向游戏安装目录。
3. `.env` 仅用于本地，不应提交。
4. 路径与环境变量解析统一收口在 `tfwr_orchestrator/src/tfwr_orchestrator/config.py`。
5. 在 WSL 中运行时，允许把 `C:\...` 自动转换成 `/mnt/c/...`；相关兼容逻辑也必须只放在 `config.py`。
6. 当前已确认的游戏安装目录（Windows 宿主机）是 `D:\Steam\steamapps\common\The Farmer Was Replaced`，在 WSL 中对应 `/mnt/d/Steam/steamapps/common/The Farmer Was Replaced`。
7. 需要读取游戏输出时：
   - 游戏 `output.txt` 由 `TFWR_SAVE_ROOT` 推导
   - 模组 `BepInEx/LogOutput.log` 由 `TFWR_GAME_ROOT` 推导
8. 不要在别的文件里写死 `C:\Users\...\output.txt` 或 `...\BepInEx\LogOutput.log`。

## 4. 权威事实源

1. oracle 工作流下，事实优先级默认是：
   - 真实游戏运行结果
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`
   - 真实 `Save0/__builtins__.py`
   - 真实 `Save0/lb_start.py`
   - 当前仓库实现
2. 如果仓库逻辑与真实游戏输出冲突，应优先修 Python 协调器或 Unity 模组，不要拿仓库实现反过来覆盖真实结果。

## 5. 默认工作流

### 5.1 部署

1. 每次验证默认只部署单个目标脚本，不再默认全量同步全部 `lb_*.py`。
2. 每次验证都应部署两份文件：
   - 派生入口 `lb_start.py`
   - 目标脚本 `lb_xxx.py`
3. `lb_start.py` 不再作为长期手工维护的真源提交；它应由工具在部署时生成。
4. `references/leaderboard_scripts/` 才是 `lb_*.py` 真源；不要直接把 `gamesave/` 当成 git 源码目录。
5. 只有显式传 `--all` 时，才允许全量同步全部 `lb_*.py`。

### 5.2 执行

1. 模组与 Python 协调器仍统一请求执行 `lb_start`，而不是直接请求 `lb_xxx`。
2. Python 协调器通过 `BepInEx/config/mlj.tfwr.oracle-runner.state.json` 写入请求、等待终态、最后重置回 `idle`。
3. `state.json` 只作为控制面，不应塞入机器消费的完整结果正文。

### 5.3 结果读取

1. Python 协调器必须同时读取两路输出：
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`
2. 两路输出职责必须分层：
   - `output.txt`：脚本 `print(...)`、probe 输出、游戏原生文本
   - `LogOutput.log`：模组生命周期日志、leaderboard 每轮时间、最终平均值、失败诊断
3. 不要把这两路输出混成一个“统一 output”概念。
4. 当 leaderboard 执行时，后续实现应优先从 `LogOutput.log` 读取：
   - `start`
   - 每轮时间
   - `pass/fail average`

## 6. 代码边界

1. Python 真实工作流代码必须放在：
   - `tfwr_orchestrator/src/tfwr_orchestrator/config.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/leaderboard_sync.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/output_capture.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/real_game_runner.py`
2. `tfwr_orchestrator/tools/*.py` 只应作为 CLI 入口，不应重复实现业务逻辑。
3. 如果任务涉及真实 `Save0/test.py`、`Save0/simulate.py` 或 `Save0/__builtins__.py`，那是外部游戏资源修改；默认不要顺手改。
4. `oracle_runner_mod/` 的修改应只围绕：
   - 状态机请求
   - 真实脚本窗口定位 / 打开
   - leaderboard 日志输出
   - 生命周期控制

## 7. 验证与回归

1. 改 Python 协调器或路径解析后，优先验证：
   - `PYTHONPATH=tfwr_orchestrator/src python3 -m unittest discover -s tfwr_orchestrator/tests -p 'test_*.py' -v`
   - `python3 tfwr_orchestrator/tools/run_real_game_script.py --help`
   - `python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py --help`
   - `python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help`
   - `python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help`
2. 改 `refresh_gamesave_link` 时，额外验证：
   - `python3 tfwr_orchestrator/tools/refresh_gamesave_link.py`
3. 改 Unity 模组时，优先验证：
   - `dotnet build oracle_runner_mod/TFWROracleRunner.csproj`
4. 如果没有新鲜验证证据，不要声称“已完成”“已修复”“可提交”。

## 8. Git 约束

1. 提交信息必须使用中文，不要用 `feat:`、`fix:`、`refactor:` 这类英文前缀。
2. 推荐前缀：
   - `功能：`
   - `修复：`
   - `重构：`
   - `杂项：`
3. 每个逻辑单元一个原子提交，不要把多个无关改动堆在一起。
4. 未经用户明确批准，严禁 `push`。
5. 所有 Git 操作都必须串行执行，禁止并发 `git add`、`git commit`、`git rebase`、`git stash`、`git checkout`、`git merge`。
