# TFWR Oracle Workflow 代理约束

## 1. 文档职责边界

1. `README.md` 面向仓库使用者，承接环境准备、前期布置、首次自检和日常最小工作流。
2. 本文件只面向代理 / 自动化执行，承接代码边界、事实优先级、验证要求和 Git 约束。
3. 如果只是回答“怎么把仓库先跑起来”，优先参考 `README.md`；不要在这里重复写面向使用者的安装步骤。

## 2. 仓库主线与权威目录

1. 本仓库当前主线是“真实游戏 oracle 工作流 + leaderboard 优化”，不是本地 parity simulator。
2. 真实执行环境默认由三部分组成：
   - `oracle_runner_mod/`
   - `tfwr_orchestrator/`
   - 真实游戏存档 `Save0`
3. `references/leaderboard_scripts/` 是仓库内 `lb_*.py` 与同名 `lb_*.md` 的真源。
4. `gamesave/` 是指向真实 `Save0` 的本地链接目录，不进 git，也不是长期源码目录。
5. `lb_start.py` 是部署时生成的派生入口，不是长期手工维护的真源。
6. 仓库内不再保留 `src/gamesimulator/` 这类旧 simulator 主线入口；后续不要再按 simulator 心智组织新改动。

## 3. 路径解析与输出边界

1. 默认通过仓库根目录 `.env` 中的 `TFWR_SAVE_ROOT` 指向真实 `Save0`。
2. 默认通过仓库根目录 `.env` 中的 `TFWR_GAME_ROOT` 指向游戏安装目录。
3. 路径与环境变量解析统一收口在 `tfwr_orchestrator/src/tfwr_orchestrator/config.py`。
4. WSL 下的 `C:\...` / `D:\...` 到 `/mnt/c/...` / `/mnt/d/...` 转换逻辑，也只能放在 `config.py`。
5. 游戏 `output.txt` 必须由 `TFWR_SAVE_ROOT` 推导。
6. 模组 `BepInEx/LogOutput.log` 与 `state.json` 必须由 `TFWR_GAME_ROOT` 推导。
7. 不要在别的文件里写死 `C:\Users\...\output.txt`、`...\BepInEx\LogOutput.log` 或状态机文件路径。
8. 不要把游戏 `output.txt` 和 `BepInEx/LogOutput.log` 混成一个“统一 output”概念。

## 4. 默认工作流约束

1. 默认只部署单个目标脚本，不再默认全量同步全部 `lb_*.py`。
2. 每次真实验证都应部署两份文件：
   - 派生入口 `lb_start.py`
   - 目标脚本 `lb_xxx.py`
3. 模组与 Python 协调器统一请求执行 `lb_start`，不要直接把 `lb_xxx.py` 当作默认入口。
4. Python 协调器通过 `BepInEx/config/mlj.tfwr.oracle-runner.state.json` 写入请求、等待终态、最后重置回 `idle`。
5. `state.json` 只作为控制面，不应塞入机器消费的完整结果正文。
6. `output.txt` 负责脚本 `print(...)`、probe 输出和游戏原生文本。
7. `LogOutput.log` 负责模组生命周期日志、leaderboard 每轮时间、最终平均值和失败诊断。
8. `references/leaderboard_scripts/README.md` 是全榜单共用注意事项主文档；具体策略先看它，再看对应 `lb_xxx.md`。

## 5. 代码边界

1. Python 真实工作流代码必须放在：
   - `tfwr_orchestrator/src/tfwr_orchestrator/config.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/leaderboard_sync.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/output_capture.py`
   - `tfwr_orchestrator/src/tfwr_orchestrator/real_game_runner.py`
2. `tfwr_orchestrator/tools/*.py` 只应作为 CLI 入口，不应重复实现业务逻辑。
3. 如果任务涉及真实 `Save0/test.py`、`Save0/simulate.py` 或 `Save0/__builtins__.py`，那属于外部游戏资源修改；默认不要顺手改。
4. `oracle_runner_mod/` 的修改范围应收敛在：
   - 状态机请求
   - 真实脚本窗口定位 / 打开
   - leaderboard 日志输出
   - 生命周期控制

## 6. 权威事实源与完成标准

1. oracle 工作流下，事实优先级默认是：
   - 真实游戏运行结果
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`
   - 真实 `Save0/__builtins__.py`
   - 真实 `Save0/lb_start.py`
   - 当前仓库实现
2. 如果仓库逻辑与真实游戏输出冲突，应优先修 Python 协调器或 Unity 模组，不要拿仓库实现反过来覆盖真实结果。
3. 如果没有新鲜验证证据，不要声称“已完成”“已修复”“可提交”。

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
