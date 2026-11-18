# 项目结构与边界

本项目以本地模拟作为脚本的主要验证方式，以真实游戏结果确认机制与成绩。脚本分为普通资源生产、排行榜优化和一次性成就任务三类，共用游戏机制知识，各自保留运行目标与验收条件。

| 目录 | 拥有的职责 | 入口 |
| --- | --- | --- |
| `simulator/` | 执行游戏脚本的本地模型、简化动作预算、随机数与时间对齐 | [模拟器](../simulator/README.md) |
| `game_control/` | 本机路径、脚本部署、模组请求、结果采集、公开数据工具 | [游戏控制](../game_control/README.md) |
| `game_mod/` | 游戏内请求状态机、脚本运行、窗口准备、成绩日志与退出 | [模组](../game_mod/README.md) |
| `scripts/functional/` | 全科技下持续生产资源，复用成熟功能与多机算法 | [运行约定](../scripts/functional/README.md) |
| `scripts/leaderboard/` | 对应榜单初始条件下的当前最好可执行策略，已接入者由母版生成 | [脚本约定](../scripts/leaderboard/README.md) |
| `scripts/achievement/` | 全科技下完成一次成就任务后退出 | [成就脚本](../scripts/achievement/README.md) |
| `references/` | 反编译／资源／解锁来源、公开缓存、外部来源与各榜历史代码 | [参考资料](../references/README.md) |
| `docs/` | 六份核心文档、30份单榜策略、共用方法与进度 | [文档索引](README.md) |

## 执行与数据流

本地默认路径是“脚本 → C#原版解释器/调度器/世界模型 → 游戏时间、净库存与执行轨迹”，无需启动游戏。`simulator/headless/` 的无界面宿主负责资源生命周期、场景、进程预算和报告；`Native/` 保留原版机制。C#简化动作模型另作预算筛选。覆盖与误差见[C#验收记录](../simulator/headless/validation.md)。

实机路径是“脚本 → game_control 部署至已有存档文件 → 请求状态文件 → game_mod → 游戏执行 → 三份日志 → game_control 采集”。`gamesave/` 只是本机 Save0 链接，不是源码目录。运行期间冻结存档脚本，终态确认后才能再次部署。

路径统一由`game_control/src/tfwr_orchestrator/config.py`推导。排行榜同步只读`scripts/leaderboard/`；公开成绩写`references/leaderboards/leaderboard_cache.json`，本地模拟及方向写`docs/leaderboards/leaderboard_progress.json`。`leaderboard_cache.py`读取两份JSON，生成七列进度总表和公开来源快照两份Markdown，离线保留原抓取时间。账号最高取公开查询，仓库`lb_start.py`只记历史正式复跑。

功能脚本按资源名或 `资源_机制.py` 命名，例如 `rice.py`、`bone_dinosaur.py`；排行榜脚本保留 `lb_` 前缀。功能初版以科技全解为前提，优先迁入用户已有功能脚本，没有对应实现时使用成熟多机排行榜算法。每个资源入口使用 `入口(target=-1)`：无参持续生产，有限目标由入口及子机按实际库存判断，正常结算后返回。`resources.py` 负责目标配置、材料补给和跨资源调用；`production.py` 提供库存判断与整次执行的Jump额度。保留原算法的并行、路径、同步与热路径。`mining.py` 只集中普通地形开采的共用函数。水、化肥自动获取，不设功能脚本。

功能脚本不导入排行榜文件，来源、许可、材料和地图前提见[功能脚本](../scripts/functional/README.md)。全部入口满足[脚本准入](script-validation.md)，算法、实际窗口和完整周期结论归[速率与成就](script-rate-validation.md)。初版不扩低科技，模拟器仍可配置科技供重置及指定场景。现有自动同步只处理排行榜，功能部署也须遵守已有存档边界。

接入固定生成的脚本，以`scripts/templates/leaderboard/`或`scripts/templates/functional/`中的可读母版作为人工策略源，正式转换规则归`simulator/optimizer/`，母版旁同名`*.codegen.json`保存当前选中参数及生成链指纹。母版、规则、配方及当前最好生成物一起入Git；可执行路径、游戏导入及部署入口保持现有结构，只手改母版及规则。未接入者直接维护现有脚本，目录按实际接入创建。完整步骤与重建要求归[母版与固定代码生成](leaderboards/interpreter_cost_notes.md#母版与固定代码生成)。

旧正式实现与未采用候选归`references/leaderboard_history/<lb_xxx>/`，`manifest.json`维护源码、原实验路径及提交映射。可从母版／转换器Git版本及参数复现的临时变体只保留淘汰结论，避免重复归档展开大文件；旧正式可执行版仍归档。归档不参与类型检查或部署扫描。同名单榜文档只保留当前策略、淘汰表、版本演进和下一步四节。公开缓存目录仅两份数据／快照，原始实验回执留`.codex/`，正式目录不新增阶段或日期过程文档。

## 命名迁移

| 原目录 | 当前目录 |
| --- | --- |
| `mechanism_model/` | `simulator/` |
| `tfwr_orchestrator/` | `game_control/` |
| `oracle_runner_mod/` | `game_mod/` |
| `references/leaderboard_scripts/*.py` | `scripts/leaderboard/` |
| `references/leaderboard_scripts/*.md` | `docs/leaderboards/` |
| `references/leaderboard_scripts/leaderboard_cache.json` | `references/leaderboards/` |

使用当前目录中的命令与导入路径；默认脚本入口为 `dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll`，首次先构建对应项目。游戏控制内部Python包仍名为 `tfwr_orchestrator`，发行包与命令名保留。如果此前按旧目录做过可编辑安装，需要从仓库根目录执行 `python3 -m pip install -e game_control` 更新安装路径；直接运行 `game_control/tools/` 中的入口不需要这一步。已有C#动作项目、模组程序集名和插件ID保留；完整模拟器为独立的 `TFWRSimulator` 程序集。

冻结的 `.codex/` 实验和历史附件保留原路径文本，需要复用时再迁移对应实验。项目不保留独立单元测试代码与测试项目；脚本主要通过本地模拟验证，机制与成绩按授权进行实机对照，工具代码变更使用静态检查及必要编译。
