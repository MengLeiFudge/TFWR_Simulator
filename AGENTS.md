# TFWR Oracle Workflow 代理约束

## 目标与事实源

1. 主线是“本地模型筛选 → 真实游戏验证 → leaderboard 优化”。时间比较、效率预算和研究优先级统一以 #10 为基准；#1 仅供参考，不代表可达目标，#30/#100 用于了解成绩分布。模型与轮内 ETA 只代表预期，不能当作实测成绩或排名。Python脚本模拟器按单个seed、同脚本与初始条件尽量复刻游戏；时间精度门槛与覆盖口径见mechanism_model/README.md“模拟精度与验收”，未经新鲜对照不能声称通过。误差和未覆盖机制必须明示。
2. 真实游戏结果优先，其后是 `output.txt`、BepInEx `LogOutput.log`、真实 `Save0/__builtins__.py` / 部署入口，最后才是仓库推断。Unity `Player.log` 用于核对引擎错误。冲突时修认知或工具，不覆盖真实结果。
3. `references/leaderboard_scripts/lb_*.py` 及同名 `.md` 是策略真源；`gamesave/` 只是本机 Save0 链接。存档 `lb_start.py` 是部署生成物；仓库同名文件另作历史成绩索引。旧 `src/gamesimulator/` 不再是实现入口。
4. 使用说明见根 `README.md`；共用优化方法见 `references/leaderboard_scripts/README.md`，之后读对应榜单 `.md`。本文件只保存代理边界，不重复安装步骤。

## 路径、协议与代码边界

1. 路径、环境变量及 WSL 路径转换统一放在 `tfwr_orchestrator/src/tfwr_orchestrator/config.py`。`TFWR_SAVE_ROOT` 推导 `output.txt` 和 `Player.log`；`TFWR_GAME_ROOT` 定位游戏；`TFWR_BEPINEX_ROOT` / `--bepinex-root` 推导模组日志和状态文件，未设置时回退游戏目录/BepInEx。其他文件不得硬编码用户路径。
2. Python 执行工作流收口在 `config.py`、`leaderboard_sync.py`、`output_capture.py`、`real_game_runner.py`；公开排行榜抓取、缓存和成绩比较归 `leaderboard_cache.py`。`tools/*.py` 只接线。模组范围为请求状态机、窗口定位、leaderboard 日志与生命周期；本地动作模型归 `mechanism_model/`。
3. `state.json` 只承载控制面。读改写必须通过协调器接口持有同名 `.lock`；请求 ID 分配、取消、确认终态均核对当前请求，旧请求不得覆盖新请求。不按锁龄自动抢锁。
4. 输出保持独立：`output.txt` 是可清空重写的脚本输出；`LogOutput.log` 是追加式模组/成绩日志；`Player.log` 是 Unity 诊断。请求运行中不高频读 `output.txt`，结束后再回读；每次模组验证都检查后两份日志。

## 存档与部署

1. 默认只部署已有的目标 `lb_xxx.py` 和派生 `lb_start.py`，统一请求运行 `lb_start`；不默认全量同步。
2. 禁止向真实 Save0 / gamesave 添加或删除任何文件；用户明确要求恢复已删除的原有文件时例外。临时验证覆盖已有脚本前备份，结束后恢复；不得在 Save0 生成编译缓存。
3. 新的外部 `.py` 必须先读内容和依赖，确认运行方式；打榜适配到已有 `lb_start` / `lb_xxx`，探针适配到已有 `test.py`。不得把外部文件直接复制成存档新依赖。
4. `test.py`、`simulate.py`、`__builtins__.py` 属于外部游戏资源，默认不顺手修改。游戏会同步 `.env` 指向存档的外部修改，不无证据怀疑旧存档缓存。

## 策略研究与记录

1. 优化前用 `refresh_leaderboard_cache.py` 更新公开成绩缓存，读取生成的 `references/leaderboard_scripts/leaderboard_targets.md`，按 #10 时间反推预算；缺少 #10 时不计算差距，不回退到 #1。默认每榜前 100 名，展示 #1/#10/#30/#100；缓存带来源和抓取时间。离线报告保留原抓取时间，不把历史 #1 当作当前成绩。
2. 预算落到主机制：伴生有效收获周期、reroll/support 成本、Dinosaur move/apple、Cactus move/swap/measure、Maze 节点/宝藏路径。伴生收益按真实 YieldFactor 和 companion 倍率计算，明显超预算的候选不进实机。
3. 已有正式模型时先用 `mechanism_model/`，无模型才写有界探针。默认按游戏 API/方法及边界做对照，不为验收模拟器逐榜运行完整策略；记录返回值、状态/资源变化、随机数与时间误差。方法覆盖与组合机制覆盖分别报告，未实现接口不能标为通过；方法级通过不能代替单seed长程精度对照；候选差距接近误差时交给实机判定。具体口径见 `mechanism_model/README.md`。
4. 理论计算先用闭式估算、少量候选和剪枝；禁止无界全组合搜索。探针写成 `.codex/tests/*.py` 或正式脚本，设置输入/时间/移动上限和早停条件。预计超过 60 秒必须有进度；连续 30 秒无有效输出则停止并缩小输入。
5. 探索脚本记录初始化、support 准备、reroll、成熟等待、移动补种、收割和资源补给等阶段，使用 `quick_print()`（0t）。`print()` 消耗约1游戏秒，不用于频繁阶段日志；先改善策略结构，接近目标或候选接近时再压缩廉价判断和调用开销。
6. 具体 `lb_xxx.py` 只保留当前确认最快的实现。固定结构：首行 `from __builtins__ import *`，紧接完整轮时间注释，第一个函数与文件同名，随后辅助方法，末尾 `if __name__ == "__main__":` 调用同名入口。
7. 历史版本、失败原因、接近候选、预测和实测分别写入同名 `.md`，使用共用 README 模板。足够轮数的当前版本复跑同时更新仓库 `lb_start.py` 的右侧成绩列，随后离线重建排行榜报告；参考成绩不等于已提交排名。更快候选须说明机制原因，迁入真源后重新部署验证；可迁移结论同步共用文档。
8. 默认按“本地复跑时间 ÷ #10 时间”从大到小选择研究对象，差距越大越优先分析提升空间；大差距本身不能证明候选有效，仍先做机制预算。连续无进展则记录结论后换榜。缓存外的本地成绩只标为前 N 名之后，不外推精确位置。

## 实机验证与生命周期

1. 测试、游戏启动和本地探针按用户当前授权执行；默认静态自审及必要编译/LSP。无新鲜证据不得声称已修复或可发布。Windows/WSL 构建 C# 使用 Windows `dotnet.exe`。
2. 只有更新 DLL 后才允许自动结束游戏并重启以加载新 DLL。其他原因无论无响应或日志停止，都只停止请求并通知用户处理游戏状态；R2 模式正常运行只连接用户启动的 profile。
3. 外部请求运行前确认 idle，并确认已有 leaderboard 结果页以返回 workspace；结束后确认终态、按同一 ID 回到 idle，核对本次外部请求的结果页自动关闭。手动运行的结果页必须保留，simulate 不得留下自动关闭权限。长停 requested 时检查结果页、DLL 版本和日志。
4. 官方完整统计累计约 7200 游戏秒，现实耗时取决于加速与计算负载。方向筛选可观察至少两轮，最近两轮差异超过 10% 则增加轮次；确认最快或接近候选必须完整统计或足够多轮，禁止两轮定胜负。
5. 首轮未完成时，按 `item_snapshot` 的目标库存比例显示百分比和线性预测。用 `estimated_total_game_seconds` 对比成绩；`eta_game_seconds` 是剩余时间，`eta_real_seconds` 只用于安排电脑占用。首轮完成后以完成轮均值为主。
6. 批量收获、资源消耗和阶段切换会使库存 ETA 无效；无增长不能单独证明卡住。Fastest Reset 不套资源比例。弱候选结合阶段时间/吞吐和预算提前停止，写明依据，不机械等待完整统计。
7. 持续观察 BepInEx 日志；连续 30 秒无新增日志时停止请求并诊断，不能直接断言策略低效。每秒快照/心跳证明模组仍响应，不证明策略有产出。取消摘要 `finished=false` 可能含未完成轮，成绩只计真实 `run=`。
8. `--request-only` 不带监控与自动确认，调用者负责有界监测、停止和终态回收。常规等待模式超时/中断会请求停止当前任务。收口用 `--status-only` / `ps` 确认无本仓库残留高 CPU 进程。
9. 用户明确进入长时间打榜迭代时，可在该范围内持续修改、同步和验证，无需逐轮确认；不扩大到自动发布或无关存档修改。

## Git 与发布

1. 保留无关 dirty；每个逻辑单元一个原子提交，提交信息用中文（如 `修复：`），Git 写操作串行。
2. 未经明确批准不 push、不发布 Thunderstore/R2。仅本地替换 DLL 的任务不得顺带上传包。
