# 项目结构与边界

本项目以本地模拟作为脚本的主要验证方式，以真实游戏结果确认机制与成绩。脚本分为普通资源生产和排行榜优化两类，共用游戏机制知识，各自保留运行目标与验收条件。

| 目录 | 拥有的职责 | 入口 |
| --- | --- | --- |
| `simulator/` | 执行游戏脚本的本地模型、简化动作预算、随机数与时间对齐 | [模拟器](../simulator/README.md) |
| `game_control/` | 本机路径、脚本部署、模组请求、结果采集、公开数据工具 | [游戏控制](../game_control/README.md) |
| `game_mod/` | 游戏内请求状态机、脚本运行、窗口准备、成绩日志与退出 | [模组](../game_mod/README.md) |
| `scripts/functional/` | 持续生产资源，适配解锁与科技进度 | [运行约定](../scripts/functional/README.md) |
| `scripts/leaderboard/` | 对应榜单初始条件下的最快已确认策略 | [脚本约定](../scripts/leaderboard/README.md) |
| `references/` | 反编译源码、资源和解锁快照、外部来源及公开成绩缓存 | [参考资料](../references/README.md) |
| `docs/` | 架构、研究方法、策略结论和验证记录 | [文档索引](README.md) |

## 执行与数据流

本地路径是“脚本 → Python 模拟器 → 预计时间、库存与执行轨迹”，无需启动游戏。C# 简化模型另用于预算筛选，不执行脚本。覆盖范围、误差和未实现机制由模拟器文档记录。

实机路径是“脚本 → game_control 部署至已有存档文件 → 请求状态文件 → game_mod → 游戏执行 → 三份日志 → game_control 采集”。`gamesave/` 只是本机 Save0 链接，不是源码目录。运行期间冻结存档脚本，终态确认后才能再次部署。

路径统一由 `game_control/src/tfwr_orchestrator/config.py` 推导。排行榜同步读取 `scripts/leaderboard/`；公开成绩写入 `references/leaderboards/leaderboard_cache.json`；比较报告写入 `docs/leaderboards/leaderboard_targets.md`，仓库复跑成绩从 `scripts/leaderboard/lb_start.py` 读取。公开缓存和策略研究文档分别拥有来源事实与解释结论，不混作脚本依赖。

功能脚本按资源名或 `资源_机制.py` 命名，例如 `rice.py`、`bone_dinosaur.py`；排行榜脚本保留 `lb_` 前缀。当前功能目录只有正式约定，尚无可交付实现，也没有专门的功能脚本同步命令。

## 命名迁移

| 原目录 | 当前目录 |
| --- | --- |
| `mechanism_model/` | `simulator/` |
| `tfwr_orchestrator/` | `game_control/` |
| `oracle_runner_mod/` | `game_mod/` |
| `references/leaderboard_scripts/*.py` | `scripts/leaderboard/` |
| `references/leaderboard_scripts/*.md` | `docs/leaderboards/` |
| `references/leaderboard_scripts/leaderboard_cache.json` | `references/leaderboards/` |

使用当前目录中的命令与导入路径；Python 模拟入口为 `python3 -m simulator.local_simulator`。游戏控制内部 Python 包仍名为 `tfwr_orchestrator`，发行包与命令名保留。如果此前按旧目录做过可编辑安装，需要从仓库根目录执行 `python3 -m pip install -e game_control` 更新安装路径；直接运行 `game_control/tools/` 中的入口不需要这一步。C# 项目文件、程序集名和模组插件 ID 保留，避免目录调整影响已安装模组的身份与协议。

冻结的 `.codex/` 实验和历史附件保留原路径文本，需要复用时再迁移对应实验。既有测试文件随所属项目移动并保持内容不变；其中 `game_control/tests/test_config.py` 仍包含原目录与旧常量的断言，需要在获准维护测试时更新。
