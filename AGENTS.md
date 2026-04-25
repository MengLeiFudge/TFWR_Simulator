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
9. 游戏加载的就是 `.env` 指向的最新真实存档，不要再怀疑旧存档或缓存；游戏会自动同步外部文件内容修改。
10. 禁止向真实 `Save0` / `gamesave/` 添加或删除任何文件；除非用户明确要求恢复已删除的原有文件，否则只能修改存档内已有文件的内容。
11. 对任何新的外部 `.py` 文件，必须先读取内容并判断其运行方式；打榜文件要改造成能通过 `lb_start.py` 运行，测试文件要改造成能通过 `test.py` 运行。
12. 外部 `.py` 文件不得直接复制进真实存档作为新增依赖；需要运行时，应把确认后的逻辑适配进已有入口文件或仓库真源，再按单脚本部署规则同步。

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
5. leaderboard 脚本文件内部不要长期保留大量杂乱历史版本；只有带来明显策略改善、仍值得继续作为候选或对照的 `mainX` 才保留在 `.py` 中。像 `main14` 这类已验证失败的路线，应删除实现代码，只把失败结论、成绩和原因记录到对应 `lb_xxx.md`。
6. 持续推进榜单时，优先选择策略结构已经明确、实现尚未对齐的榜单；例如多无人机南瓜、单无人机南瓜这类机制和目标布局都比较清楚的榜单，应优先于继续在已接近局部最优但方向不清晰的榜单上微调。

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
4. 只有更新 Unity 模组 DLL 后，才允许代理自动结束现有 `TheFarmerWasReplaced.exe` 进程并重新启动游戏；这是让 BepInEx 加载新 DLL 的必要步骤。
5. 除更新 DLL 之外，任何情况都不能自动重启游戏；即使真实验证中游戏长时间无响应、`output.txt` 或 `BepInEx/LogOutput.log` 没有新增输出，也只能停止当前请求并通知用户处理游戏状态。
6. 真实 leaderboard 复测完成后，必须确认模组能自动关闭 leaderboard 结果页并回到 workspace；如果 `state.json` 长时间停在 `requested`，优先检查是否仍停留在结果页、游戏是否加载了旧 DLL、以及两类输出日志是否仍在刷新。

## 8. 长时间 leaderboard 迭代授权

1. 当用户明确进入长时间打榜迭代任务时，代理拥有当前仓库内最高可用权限，可持续修改、同步、验证 leaderboard 脚本，不需要每轮方案确认。
2. leaderboard 官方完整统计需要约 `2h`，但优化迭代阶段不等待完整打榜；请求启动后必须持续检查游戏 `output.txt`，如果连续 `30s` 没有新增输出，直接判定脚本卡住或明显低效并停止本次请求。
3. 迭代目标是优化脚本，不是实际刷满排行榜；每轮完成后 `output.txt` 必定有新增输出，优先使用新增输出里的 `average`、单轮时间和 probe 输出判断方向。
4. 运行任何 `lb_*.py` 真实验证时，`run_real_game_script.py` / `real_game_runner.py` 默认只跑到 `output.txt` 出现 2 条新增 `run=` 输出；两轮通常已经足够判断当前方向。只有这两轮成绩差异较大、无法判断均值稳定性，或要刷完整官方统计 / 专门观察长尾均值时，才显式传 `--max-leaderboard-runs 0` 或更大的轮次数继续运行。
5. 如果某个排行榜连续数次尝试没有进展，或者已经接近 `#1` 难以继续推进，应切换到其他更可能推进的排行榜，避免把时间耗在单一榜单上。
6. 切换榜单时，必须把当前榜单的尝试结果、失败原因和下一步判断记录到对应 `lb_xxx.md`，不要把失败实现长期留在 `.py`。
7. `BepInEx/LogOutput.log` 是第二优先级运行证据；模组应在请求运行中每秒输出 `item_snapshot`，包含当前所有物品数量，用于判断脚本是否仍在推进资源。
8. `state.json` 是最低优先级控制面；开始脚本前确认 `idle`，终止脚本后确认最终态即可，不得把状态机轮询当作脚本仍有进展的证据。

## 9. Git 约束

1. 提交信息必须使用中文，不要用 `feat:`、`fix:`、`refactor:` 这类英文前缀。
2. 推荐前缀：
   - `功能：`
   - `修复：`
   - `重构：`
   - `杂项：`
3. 每个逻辑单元一个原子提交，不要把多个无关改动堆在一起。
4. 未经用户明确批准，严禁 `push`。
5. 所有 Git 操作都必须串行执行，禁止并发 `git add`、`git commit`、`git rebase`、`git stash`、`git checkout`、`git merge`。
