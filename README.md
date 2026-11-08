# TFWR 脚本与模拟工具

本项目包含无需启动游戏的本地模拟器、连接真实游戏的控制工具与模组，以及功能脚本和排行榜脚本。本地模拟是脚本的主要验证方式；覆盖范围与误差须按具体机制确认。

工作流是：本地模型粗筛策略 → 真实游戏验证 → 记录账号最高成绩与策略证据。所有排行榜以当前公开#1为目标，#10或末名只作参照。先按距#1的倍率差距从大到小研究非快速重置榜，再将成熟方法迁入快速重置；已有较好时间仍超过2×#1时，优先重列策略方向和完整成本，不继续旧脚本的小修。只按游戏预期机制优化。模拟精度与范围见[验收说明](simulator/README.md#模拟精度与验收)；模型与ETA仍是预测，账号名次以公开记录为准。

## 仓库分工

| 目录 | 职责 |
| --- | --- |
| [simulator/](simulator/README.md) | 无需启动游戏的脚本模拟器，以及简化动作模型 |
| [game_control/](game_control/README.md) | 路径配置、脚本部署、请求控制、结果采集和公开排行榜缓存 |
| [game_mod/](game_mod/README.md) | BepInEx 模组，接收指令并在游戏内运行脚本 |
| [scripts/functional/](scripts/functional/README.md) | 全科技下持续生产资源，优先沿用已有功能脚本和成熟多机排行榜算法 |
| [scripts/leaderboard/](scripts/leaderboard/README.md) | `lb_*.py` 排行榜脚本真源 |
| [references/](references/README.md) | 游戏源码、资源与科技快照、公开成绩缓存等参考事实 |
| [docs/](docs/README.md) | 项目架构、共用研究方法、各榜策略与验证记录 |
| `gamesave/` | 指向本机真实 Save0 的链接，只是部署目标，不进 Git |

本地模拟通过CLI手动运行，尚未自动接在部署命令前。[脚本模拟入口](simulator/local_simulator/README.md) 读取游戏脚本，输出预计游戏时间、库存和轨迹。目标是单seed执行与时间对齐，验收门槛见[模拟精度与验收](simulator/README.md#模拟精度与验收)。约900游戏秒场景的通过记录对应旧版；新版已按源码迁移机制，尚待实机精度验收，见[更新影响](simulator/local_simulator/game-update-26385848.md)和[验收记录](simulator/local_simulator/validation.md)。最终成绩仍由真实游戏验证。

所有准备在游戏内执行的脚本，必须先通过本地模拟的正确性与效率验证。只有同条件下效率严格高于当前存档版本，才允许覆盖已有对应文件。功能初版按科技全解，Fastest Reset按原版重置条件；详细要求见[脚本验证与替换准入](docs/script-validation.md)，本轮功能脚本的来源、实际增长率与完整周期结果见[功能效率对照](docs/functional-validation.md)。

## 首次配置

本地 Python 模拟仅需 Python 3.11+，无需打开游戏或配置真实存档。运行方式见 [模拟器说明](simulator/README.md)。C# 动作模型使用 .NET 10。

以下配置用于真实游戏执行：需要游戏、真实存档和 BepInEx 5 Mono；排行榜任务还需要存档已解锁对应榜单。R2 对应依赖为 `BepInEx-BepInExPack-5.4.2305`。构建模组需要 Windows .NET SDK。

从 `.env.example` 复制一份 `.env`，填写本机路径：

```env
TFWR_SAVE_ROOT=C:\Users\YourName\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
TFWR_BEPINEX_ROOT=C:\Users\YourName\AppData\Roaming\r2modmanPlus-local\TheFarmerWasReplaced\profiles\Default\BepInEx
```

`TFWR_BEPINEX_ROOT` 指向实际 profile 的 BepInEx 目录；手动安装可留空，回退到游戏目录下的 BepInEx。环境变量优先于 `.env`；WSL 支持上述 Windows 路径。

在 R2 安装 `MengLei / TFWR_Oracle_Runner`，通过所选 profile 启动游戏。客户端在 R2 模式只连接已启动的游戏；支持协议2的模组提供 `--action prepare` 准备工作区、`--action quit` 保存并退出，脚本请求也会自动进入工作区。构建、配置和手动安装见 [模组说明](game_mod/README.md)。

```bash
python3 game_control/tools/refresh_gamesave_link.py
python3 game_control/tools/run_real_game_script.py --status-only
```

确认 `gamesave/` 指向正确 Save0，状态文件位于所选 profile，模组已加载。真实存档只能覆盖已有文件，不能通过部署新增或删除文件；临时验证覆盖前备份，验证后恢复。

## 日常优化流程

1. 阅读[共用策略说明](docs/leaderboards/README.md)和目标榜单同名`.md`。先列策略方向并按机制淘汰，再估算完整成本。用项目内`refresh_leaderboard_cache.py --script lb_xxx`刷新当前研究榜的#1及账号最高记录，以#1为目标制定预算。用户查询全榜时省略`--script`，刷新常规及地下全部30榜。更新本地研究JSON后离线重建进度：

   ```bash
   python3 game_control/tools/refresh_leaderboard_cache.py --offline
   ```

   默认每榜前100名；统一生成“排行榜、#1、#10、实机、模拟、比例、改进方向”七列，实机为账号最高并附排名。公开事实与本地研究状态分别保存为JSON；进度、targets和来源快照同步生成。命令及Windows/WSL代理用法见[排行榜缓存](game_control/README.md#排行榜缓存)。
2. 先用 [本地模型](simulator/README.md) 筛选，例如：

   ```bash
   python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seed 1
   dotnet run --project simulator/TFWRMechanismModel.csproj -- cactus --size 32 --samples 100
   ```

   限制样本数、移动数和命令时间。模型比较的是动作成本、完成率或命中率，不能把动作下界直接写成真实成绩。
3. 按[脚本验证与替换准入](docs/script-validation.md)准备脚本。排行榜进入实机满足任一条件：用户明确授权该实机任务；或有效模拟预估时间≤当前公开#1的2倍，且严格快于当前账号公开最高记录。模拟可采用有依据的短程预估，不要求完整跑完目标。随后部署单个目标脚本及派生入口；具体证据与缺失口径见[共用策略说明](docs/leaderboards/README.md#固定效率闭环)：

   ```bash
   python3 game_control/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
   python3 game_control/tools/run_real_game_script.py --target-script lb_start --request-timeout 60
   ```

   默认在至少两轮且最近两轮差异不超过 10% 后停止，适合方向筛选。确认接近候选谁更快时增加轮数；`--max-leaderboard-runs 0` 允许完整统计，另设足够的请求超时。完整统计累计约 **7200 游戏秒**，不是固定等待现实两小时。
4. 运行中查看资源百分比和预测，首轮结束后看完成轮均值：

   ```bash
   python3 game_control/tools/run_real_game_script.py --status-only --status-lines 20
   ```

   `estimated_total_game_seconds`是本轮预计总游戏时间；`eta_game_seconds`是预计剩余时间。用前者对照#1目标和当前账号记录；它仍是预测。库存线性增长时才能按库存估算，Cactus/Dinosaur等批量结算前可能长期0%，须看阶段进度和完整生产周期。Fastest Reset按阶段预算推算，不套资源比例。
5. 把预测、实测轮数/均值/波动、失败原因和下一步写回同名 `.md`；[Cactus 记录样本](docs/leaderboards/lb_cactus.md#2026-10-22-研究记录样本) 展示完整口径。`.py` 只保留当前确认最快的实现。

`--request-only` 只投递请求，默认拒绝覆盖活动请求；明确替换须加 `--replace`，终态须先回收；它不负责持续监测或自动回收终态。长流程使用它时必须自行监看日志、按请求 ID 停止和确认终态，接口见 [协调器说明](game_control/README.md)。常规等待命令会在超时或中断时请求停止当前任务。

## 三份输出

| 输出 | 内容与读取时机 |
| --- | --- |
| 游戏 `output.txt` | 脚本打印和游戏原生文本；每次执行会清空，结束后读取 |
| BepInEx `LogOutput.log` | 模组生命周期、每轮成绩、汇总、每秒资源快照；运行中主要观察来源 |
| Unity `Player.log` | 引擎错误和异常堆栈；与 BepInEx 日志一起排查故障 |

前两类游戏日志路径由 Save0 和 BepInEx 配置分别推导；`Player.log` 与 `output.txt` 位于同一游戏持久数据根目录。运行中默认跳过 `output.txt`，避免争用游戏写入句柄。状态文件只负责控制，不能作为策略仍有产出的证据。连续 30 秒没有模组日志应停止并诊断；心跳仍有输出也不代表资源在增长。

## 开发入口

- [项目结构与边界](docs/architecture.md)：各模块职责、脚本分类和数据流。
- [Python 游戏控制](game_control/README.md)：CLI、文件锁、取消与输出采集。
- [模组](game_mod/README.md)：Windows 构建、R2 安装和协议。
- [动作模型](simulator/README.md)：有界筛选命令及机制边界。
- [游戏脚本类型检查](typings/README.md)：仓库类型声明、ty/LSP配置和游戏语言的静态边界。
- `game_control/tools/refresh_decompiled_sources.py --help`：刷新反编译事实源。
- `game_control/tools/extract_unlock_snapshot.py --help`：提取科技事实表。

XERJ 项目索引范围由 [.xerjignore](.xerjignore) 限定。`docs/*-validation.json` 自动生成报告由对应Markdown说明承载检索，图标和.NET框架反编译产物也排除；游戏源码、项目实现和模型资源JSON保留。进入仓库后运行 `xerj-project index` 增量更新，使用 `xerj-project search "查询"` 或 `xerj-project def 符号` 定位。

若新增结构文件报 `no frozen dataset accepts family`，表示旧索引的字段或格式集合已冻结。不要改写源JSON迎合缓存，也不要用 `--fresh` 清除旧记录；备份本项目的索引记录和journal后，仅重建本项目对应prefix的缓存，保留其他项目。重建后再运行普通增量命令，确认退出码为0且检索命中当前源码。

代理执行边界集中在 [AGENTS.md](AGENTS.md)。
