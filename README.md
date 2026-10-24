# TFWR Oracle Workflow Workspace

工作流是：本地模型粗筛策略 → 真实游戏验证候选 → 按完整轮成绩更新策略记录。时间比较和效率预算以第十名为基准，默认优先研究相对 #10 差距大的榜单。第一名仅供参考，不代表可达目标。模拟器尽量贴近游戏，但作为辅助工具不要求完全一致；默认按 API/方法及边界验证，记录误差和覆盖范围，具体见 [模拟精度与验收](mechanism_model/README.md#模拟精度与验收)。模型结果和轮内 ETA 都是预测，排名结论以真实游戏结算为准。

## 仓库分工

| 目录 | 职责 |
| --- | --- |
| `mechanism_model/` | 本地农场API脚本模拟；C#的Dinosaur、Cactus、Companion动作模型和随机序列对照 |
| `references/leaderboard_scripts/` | `lb_*.py` 策略真源，同名 `.md` 保存研究过程和实测证据 |
| `tfwr_orchestrator/` | Python 路径配置、脚本部署、请求控制、结果采集和公开排行榜缓存 |
| `oracle_runner_mod/` | BepInEx 模组，在真实游戏内执行脚本、记录完成轮和资源快照 |
| `references/unlocks/` | 游戏科技前置、成本和解锁事实表 |
| `gamesave/` | 指向本机真实 Save0 的链接，只是部署目标，不进 Git |

本地模拟通过CLI手动运行，尚未自动接在部署命令前。[脚本模拟入口](mechanism_model/local_simulator/README.md) 读取游戏脚本，输出预计游戏时间、库存和轨迹。目标是单seed执行与时间对齐，验收门槛见[模拟精度与验收](mechanism_model/README.md#模拟精度与验收)。脚本计时和事件改造尚待实机对照，历史662条离散观测不代表新版精度通过，详见[验收记录](mechanism_model/local_simulator/validation.md)。最终成绩仍由真实游戏验证。

## 首次配置

需要 Python 3.11+、游戏、可打榜的真实存档，以及 BepInEx 5 Mono。R2 对应依赖为 `BepInEx-BepInExPack-5.4.2305`。构建模组需要 Windows .NET SDK；动作模型使用 .NET 10。

从 `.env.example` 复制一份 `.env`，填写本机路径：

```env
TFWR_SAVE_ROOT=C:\Users\YourName\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
TFWR_BEPINEX_ROOT=C:\Users\YourName\AppData\Roaming\r2modmanPlus-local\TheFarmerWasReplaced\profiles\Default\BepInEx
```

`TFWR_BEPINEX_ROOT` 指向实际 profile 的 BepInEx 目录；手动安装可留空，回退到游戏目录下的 BepInEx。环境变量优先于 `.env`；WSL 支持上述 Windows 路径。

在 R2 安装 `MengLei / TFWR_Oracle_Runner`，通过所选 profile 启动游戏。客户端在 R2 模式只连接已启动的游戏；支持协议2的模组提供 `--action prepare` 准备工作区、`--action quit` 保存并退出，脚本请求也会自动进入工作区。构建、配置和手动安装见 [模组说明](oracle_runner_mod/README.md)。

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
python3 tfwr_orchestrator/tools/run_real_game_script.py --status-only
```

确认 `gamesave/` 指向正确 Save0，状态文件位于所选 profile，模组已加载。真实存档只能覆盖已有文件，不能通过部署新增或删除文件；临时验证覆盖前备份，验证后恢复。

## 日常优化流程

1. 阅读 [共用策略说明](references/leaderboard_scripts/README.md) 和目标榜单的同名 `.md`。刷新公开榜单后，按 [成绩与提升空间](references/leaderboard_scripts/leaderboard_targets.md) 中相对 #10 的差距选择研究对象并反推动作预算：

   ```bash
   python3 tfwr_orchestrator/tools/refresh_leaderboard_cache.py
   ```

   默认批量读取每榜前 100 名，报告展示 #1/#10/#30/#100、仓库复跑参考和大致位置。仅重算已有缓存用 `--offline`；代理和 Windows/WSL 用法见 [排行榜缓存](tfwr_orchestrator/README.md#排行榜缓存)。
2. 先用 [本地模型](mechanism_model/README.md) 筛选，例如：

   ```bash
   python3 -m mechanism_model.local_simulator references/leaderboard_scripts/lb_cactus_single.py --seed 1
   dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- cactus --size 32 --samples 100
   ```

   限制样本数、移动数和命令时间。模型比较的是动作成本、完成率或命中率，不能把动作下界直接写成真实成绩。
3. 候选接近预算后，部署单个目标脚本及派生入口：

   ```bash
   python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
   python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 60
   ```

   默认在至少两轮且最近两轮差异不超过 10% 后停止，适合方向筛选。确认接近候选谁更快时增加轮数；`--max-leaderboard-runs 0` 允许完整统计，另设足够的请求超时。完整统计累计约 **7200 游戏秒**，不是固定等待现实两小时。
4. 运行中查看资源百分比和预测，首轮结束后看完成轮均值：

   ```bash
   python3 tfwr_orchestrator/tools/run_real_game_script.py --status-only --status-lines 20
   ```

   `estimated_total_game_seconds` 是本轮预计总游戏时间；`eta_game_seconds` 是预计剩余时间。应以前者比较基线和 #10 参考时间。库存线性增长才能估算；Cactus/Dinosaur 等批量结算前可能长期 0%，需结合阶段日志，不能直接判为卡住。Fastest Reset 不使用资源比例估算。
5. 把预测、实测轮数/均值/波动、失败原因和下一步写回同名 `.md`；[Cactus 记录样本](references/leaderboard_scripts/lb_cactus.md#2026-10-22-研究记录样本) 展示完整口径。`.py` 只保留当前确认最快的实现。

`--request-only` 只投递请求，默认拒绝覆盖活动请求；明确替换须加 `--replace`，终态须先回收；它不负责持续监测或自动回收终态。长流程使用它时必须自行监看日志、按请求 ID 停止和确认终态，接口见 [协调器说明](tfwr_orchestrator/README.md)。常规等待命令会在超时或中断时请求停止当前任务。

## 三份输出

| 输出 | 内容与读取时机 |
| --- | --- |
| 游戏 `output.txt` | 脚本打印和游戏原生文本；每次执行会清空，结束后读取 |
| BepInEx `LogOutput.log` | 模组生命周期、每轮成绩、汇总、每秒资源快照；运行中主要观察来源 |
| Unity `Player.log` | 引擎错误和异常堆栈；与 BepInEx 日志一起排查故障 |

前两类游戏日志路径由 Save0 和 BepInEx 配置分别推导；`Player.log` 与 `output.txt` 位于同一游戏持久数据根目录。运行中默认跳过 `output.txt`，避免争用游戏写入句柄。状态文件只负责控制，不能作为策略仍有产出的证据。连续 30 秒没有模组日志应停止并诊断；心跳仍有输出也不代表资源在增长。

## 开发入口

- [Python 协调器](tfwr_orchestrator/README.md)：CLI、文件锁、取消与输出采集。
- [模组](oracle_runner_mod/README.md)：Windows 构建、R2 安装和协议。
- [动作模型](mechanism_model/README.md)：有界筛选命令及机制边界。
- `tfwr_orchestrator/tools/refresh_decompiled_sources.py --help`：刷新反编译事实源。
- `tfwr_orchestrator/tools/extract_unlock_snapshot.py --help`：提取科技事实表。

代理执行边界集中在 [AGENTS.md](AGENTS.md)。
