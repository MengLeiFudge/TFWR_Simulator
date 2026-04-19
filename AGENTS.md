# TFWR_Simulator 仓库约束

## 1. 项目目标

1. 第一阶段目标：把本仓库建设成独立的 Python parity simulator，使本地对 `simulate.py`、`test.py`、`lb_*.py` 这类脚本的执行语义尽量对齐真实游戏，作为后续优化工作的基础设施。
2. 第二阶段目标：在第一阶段 simulator 基石足够可靠之后，把本仓库发展为“直接产出榜单最优策略的优化器”，用于持续搜索、比较、验证 leaderboard 脚本策略，而不是停留在手工试脚本。
3. 第二阶段依赖第一阶段：如果 simulator parity 还不够，导致本地结果与真实游戏偏差明显，则应优先继续修 simulator，而不是过早把精力转到榜单优化策略本身。
4. 因此，凡是涉及 `leaderboard` / `simulate` 入口、脚本运行语义、资源初始状态、unlock 依赖、goal 判定、drone 行为、随机性或计时行为的任务，默认都应优先从“它是否会影响第二阶段优化器的可信度”这个角度评估优先级。

## 2. 仓库范围与路径

1. 这个仓库只承载独立的 Python parity simulator；真正的源码包是 `src/gamesimulator/`。
2. 仓库根目录下的 `runner.py` 只是薄入口，职责是把 `repo/src` 加入 `sys.path` 后转调 `gamesimulator.runner`。
3. `tests/` 存放 Python 测试；`src/gamesimulator/unlock_snapshot.py` 是仓库内的默认 unlock 快照；`.env.example` 是本地配置模板。
4. 旧 `GameSimulator` 根目录下其他 `.py` 文件不属于这个仓库；后续不要再把它们迁回这里。
5. 按当前用户要求，`src/` 只放工作区源码；其中 `src/gamesimulator/` 是包代码，仓库根 `leaderboard/` 是指向真实 `Save0` 的本地链接目录，仓库根 `references/` 是参考资料目录。

## 3. Save0 与配置

1. 真实 `Save0` 仍然是仓库外部内容，不进 git；仓库只允许在 `references/leaderboard_scripts/` 中保留 `lb_*.py` 参考副本。
2. 默认通过仓库根目录 `.env` 中的 `TFWR_SAVE_ROOT` 指向真实 `Save0`；`.env` 仅用于本地，不应提交。
3. 如果调用方显式传入 `save_root`，则以显式参数为准；否则再回退到 `.env` / 环境变量。
4. 路径与环境变量解析统一收口在 `src/gamesimulator/config.py`；不要在别的文件里重新发明一套路径推导逻辑。
5. 在 WSL 中运行时，允许把 `C:\...` 形式的 `TFWR_SAVE_ROOT` 自动转换为 `/mnt/c/...`；相关兼容逻辑也应只放在 `src/gamesimulator/config.py`。
6. `leaderboard/` 不由运行时自动修改；若 `.env` 改动，需要显式运行 `python tools/refresh_leaderboard_link.py` 来重建链接。
7. `references/leaderboard_scripts/` 与 `leaderboard/` 之间的同步必须显式运行 `python tools/sync_leaderboard_scripts.py cur2save` 或 `python tools/sync_leaderboard_scripts.py save2cur`；无论哪个方向都只允许影响 `lb_*.py`。
8. 当需要读取游戏侧输出时，不要写死 `C:\Users\...\output.txt` 这类路径；应从 `.env` / `TFWR_SAVE_ROOT` 推导到对应的游戏目录，再读取 `output.txt`。

## 4. 权威事实源

1. 做 simulator parity 时，事实优先级默认是：
   - 真实游戏运行产出
   - 游戏目录 `output.txt`
   - 外部 `Save0/__builtins__.py`
   - 外部 `Save0/lb_start.py`
   - 当前仓库实现
   - 旧实验结论或口头推断
2. 如果模拟器实现与真实游戏行为冲突，应优先修模拟器，不要拿当前实现反过来覆盖事实源。
3. `src/gamesimulator/unlock_snapshot.py` 只是仓库内快照，用于默认 unlock 推导；如果用户刷新了真实快照，再按用户要求同步更新对应 Python 常量。
4. 当前已确认的游戏事实：`clear()` 不会把地块含水量清零。若在同一地块上重复做树成长试验，前一轮浇过的水会保留下来，因此后续样本不能再被当成“干地”样本。
5. 当前已确认的游戏事实：水和化肥的自动补给速率与 `Unlocks.Watering` / `Unlocks.Fertilizer` 当前等级直接相关。验证自动补给时，必须先按当前等级换算理论值，再与日志对比。例如 `Watering=9` 时应为 `25.6/s`，`Fertilizer=4` 时应为 `0.8/s`，10 秒窗口内应分别增加 `256` 和 `8`。

## 5. 工作流分流（硬性）

### 5.1 情况一：优化模拟器

1. 适用条件：本地模拟器数值与游戏真实运行时间不一致，且差异已经超出随机数影响范围，例如游戏约 `5:40` 而模拟器约 `8:00`。
2. 在这种情况下，禁止去优化 `lb_*.py` 策略；应先修 simulator parity。
3. 在这种情况下，只允许修改 `leaderboard/test.py` 和 `leaderboard/simulate.py` 这两个存档侧入口文件，用于构造 probe。
4. 在这种情况下，禁止在 `leaderboard/` 内新增、删除、重命名任何文件；尤其禁止新增临时 probe 文件。只能改 `test.py` 和 `simulate.py`。
5. `simulate.py` 用于设定起始运行条件，例如科技情况、起始物品数目、入口参数。
6. `test.py` 用于设定测试逻辑。
7. 进入 simulator 排查时，应优先写一个尽量覆盖待测项目的综合脚本，并添加尽可能多的日志，目标是尽可能减少用户打开游戏运行脚本的次数；不要每次只验证一个很窄的小点。
8. 用户在游戏里运行后，会说“跑完了”；此时应去读取游戏目录的 `output.txt`，再在本地模拟器运行同一个 `simulate.py` / `test.py` 组合，对比输出是否一致。
9. 如果输出不一致，应修改模拟器源码（通常是 `src/gamesimulator/`），并在必要时继续改 `leaderboard/test.py` / `leaderboard/simulate.py` 做下一轮更完整验证。
10. 如果仍有疑点，可以重复“改 `simulate.py` / `test.py` -> 用户跑游戏 -> 读取 `output.txt` -> 本地重放 -> 修模拟器”的循环，直到输出口径对上。
11. 在这一阶段，随机性验证应优先看“分布、覆盖范围、均值、概率是否合理”，而不是追问“为什么这次正好是这个随机结果”。例如伴生验证应关注“是否覆盖所有合法候选且概率近似均匀”，而不是执着于某次具体结果。
12. 对于随机问题，应优先设计重复采样 probe，例如同一位置重复种植 `100` 次、`1000` 次，并用平均值和分布来判断 parity，而不是依赖单次样本。
13. 分析水与化肥的自动补给时，必须结合当前 `Unlocks.Watering` / `Unlocks.Fertilizer` 等级来计算期望速率，不要脱离等级只看绝对数值。用户给出当前等级时，应先按该等级换算每秒补给量，再与日志对比。
14. 本地运行 `simulate.py` / `test.py` 这类综合 probe 时，必须设置墙钟超时，防止脚本逻辑异常时让本地 runner 卡死。超时后应先检查已输出日志，再决定是否修改脚本或继续重跑。
15. 写树成长 probe 时，若想比较“干地 / 湿地 / 施肥”样本，不能只靠 `clear()` 重置场景；必须显式记录每轮 planting 前的 `get_water()`，并使用未浇过的新地块、或等待地块自然变干，否则样本会被持久化含水量污染。
16. 只有当 `simulate.py` / `test.py` 的输出与游戏 `output.txt` 对齐到可接受范围后，才允许进入打榜优化阶段。

### 5.2 情况二：打榜优化

1. 适用条件：模拟器时间与游戏真实时间已经对齐，可以认为“模拟器 = 真实游戏环境”。
2. 在这种情况下，才应该优化 `leaderboard/` 里的 `lb_*.py`。
3. 如果当前成绩与 `1#` 差距很大，说明策略方向本身大概率不对；此时应大胆尝试新的主策略，而不是执着于微调现有细节。
4. 只有在时间已经接近 `1#` 时，才优先考虑哪些细节没做好，并做局部微调。

## 6. 模拟器与原版差异

1. 本仓库里的 simulator 目标是“可运行游戏内任意 py 脚本，并为 `simulate` / `leaderboard` 提供可重复、可验证的本地运行环境”，不是原版游戏那种带长期存档、持续推进和 UI 动画的完整运行时。
2. 默认使用方式应理解为“fresh run”：每次重点执行 `simulate.py`、`test.py`、`lb_*.py` 这类目标脚本，在确定的初始状态上复现结果，而不是把 simulator 当成一个会长期积累存档数据的沙盒。
3. simulator 默认不模拟原版的 UI、动画、成就、IPC、通知气泡、界面交互和长期存档累计；如果某个 builtin 在原版主要是 UI / meta 层行为，但脚本语言允许调用，则 simulator 仍必须接受这种写法，只是按脚本级语义处理最小必要效果。
4. 对这类 UI-only 或 meta-only builtin，若它们在游戏里主要效果只是消耗时间 / tick，则 simulator 应只推进对应的模拟时间，不产生额外 UI 副作用或持久化状态。例如 `do_a_flip()`、`pet_the_piggy()`、`tap()` 这类调用，在 simulator 里重点是保持 tick 语义，而不是还原界面表现。
5. `speedup` 参数在本仓库里只保留 CLI 形状兼容性，不应被理解为“控制本地模拟墙钟时间”的真实开关。simulator 的实际运行速度取决于本地电脑性能；脚本里的模拟时间推进由 tick / op 语义决定，而不是由 UI 动画速度决定。
6. 因为没有原版 UI 动画负担，`simulate` 和 `leaderboard` 在本地应始终以“尽可能快的计算速度”运行；是否达标、耗时多少，看的是模拟时间和脚本结果，而不是墙钟时间。

## 7. 第二阶段优化器关注点

1. 第二阶段默认研究“游戏本质收益结构”，不是只做语法级或局部代码级微调；应优先关注哪些机制真正决定 leaderboard 成绩。
2. 伴生收益通常极高；对依赖伴生的榜单，没吃到伴生通常就接近于没有有效收益。因此，布局、路径、回访节奏、support 格分配等设计，应优先服务于伴生命中率与伴生收益兑现。
3. 世界大小与版图布局通常是第二阶段的第一优先级决策变量。若不显式设置，则默认世界大小是 `32x32`；而 leaderboard 通常应主动选择更合适的大小，以利用穿越边界、伴生跨边界、回访周期压缩等收益。
4. tick 成本模型必须明确区分：大部分实际操作是 `200t`，而判断/读取类调用通常只有 `1t`。因此默认应优先“多判断、少操作”，先用便宜判断避免昂贵误操作；只有在主流程已经稳定、判断已不再显著减少操作时，才继续削减这些 `1t` 判断来进一步省 tick。
5. tick 优化不能无脑牺牲可读性。允许为了减少 tick 采用更激进写法，但前提是整体逻辑仍应可维护、可审计、可继续迭代验证。
6. 浇水、施肥等消耗品必须按真实初始数量和榜单机制精算使用，不能假设资源无限。目标通常不是直接灌到 `100%`，而是让作物在“下一次回到该格子时刚好成熟”；不同榜单对水和肥的依赖不同，必须区分处理。
7. 重种、reroll、support 改写、局部回访等行为都应按“期望收益 / tick 成本”评估，不要用大量动作换取极小改善。
8. 解锁顺序、扩张时机、资源转阶段时机是 `fastest_reset` 这类“初始科技为 0”的榜单核心优化对象；对其他起始科技已由 leaderboard metadata 给定的榜单，这些通常不是第一优先搜索维度，除非有新的事实证据证明它们同样关键。
9. 多无人机 leaderboard 默认应先假设“更多无人机通常更强”，因为并行天然有优势。同步、冲突、等待、抢格等协作开销可以作为次级修正项纳入评估，但不应默认先否定多机路线。
10. 不同 leaderboard 的目标函数和真实瓶颈不同，不能把同一套模板硬套到所有榜单。优化器应先识别榜单的主瓶颈，再决定搜索空间、评价指标和脚本结构。
11. 单次到格的“批处理能力”很关键。能在一次到访里顺手完成收、种、浇水、施肥、伴生处理和必要状态更新的策略，通常比把这些动作拆成多次回访更优。
12. 第二阶段的验证节奏应分层进行：每次脚本修改后先跑 1 次，与 `lb_start.py` 中当前 `#1` 基线比较；如果单次结果已经慢几十秒，通常没有必要继续跑完整长流程。只有当差距进入约 `10s` 以内时，才值得进一步跑完整 `2h` 流程看均值。
13. 任何魔法数字都必须带简体中文注释，说明来源。来源至少应指向以下之一：真实游戏常量、反编译源码、probe 实测结果、leaderboard 基线数据、或明确的成熟/回访节拍推导；禁止写“来路不明但看起来更快”的裸常量。

## 8. Leaderboard 本地验证

1. `leaderboard_run(...)` 在本地 simulator 中允许做面向离线验证的工程化调优，只要不破坏 seed 顺序和结果语义。当前默认允许并行预跑多轮、再按固定 seed 顺序消费结果，以降低本地验证成本。
2. `leaderboard_run(...)` 的输出格式应优先服务打榜迭代：每轮输出 `run / seed / time / total / progress`，结束时输出简洁的 `pass|fail average / min / max` 汇总，不要夹带原版 UI 才需要的噪声字段。
3. 本地 leaderboard 验证的目标是尽快判断脚本是否值得继续迭代，因此输出应优先保留与榜单成绩直接相关的信息，例如目标进度、单轮时间、均值、最小值、最大值；不要为了模仿 UI 而降低批量验证效率。
4. 只要不改变脚本语义，本地 leaderboard runner 应优先选择更适合离线优化的实现，例如无动画、可并行、固定 seed 顺序、精简日志。这类调优属于 simulator 的预期能力，不算“偏离原版游戏”。

## 9. 代码边界

1. `src/gamesimulator/` 是完整 Python 代码，可以正常使用 Python 标准库；不要把它按“游戏脚本语法限制”来写。
2. 如果任务涉及外部 `Save0/test.py`、`Save0/simulate.py` 或 `Save0/__builtins__.py`，那是“游戏侧脚本 / 外部资源”修改，不属于本仓库内部源码；默认不要顺手改。
3. 只有在用户明确要求“同时修改游戏侧入口或探针脚本”时，才去改外部 `Save0`。
4. 根入口的使用体验要保持稳定：用户应能在仓库根目录直接运行 `py runner.py simulate.py` 这一类命令，不需要关心包目录。

## 10. 验证与回归

1. 改入口、配置或路径解析后，优先验证：
   - `python3 tools/refresh_leaderboard_link.py`
   - `python3 -m unittest tests.test_gamesimulator.RunnerTests`
   - `python3 runner.py simulate.py`
   - `python3 -m unittest tests.test_tooling`
2. 改 parser / execution / simulation 逻辑后，优先跑对应的 `unittest` 目标类或目标测试，而不是只做入口 smoke test。
3. 如果整份 `tests.test_gamesimulator` 仍有历史失败，必须明确区分“本次新增回归”和“迁移前就存在的问题”，不要混在一起汇报。

## 11. Git 约束

1. 提交信息必须使用中文，不要用 `feat:`、`fix:`、`refactor:` 这类英文前缀。
2. 推荐使用中文分类前缀：`功能：`、`修复：`、`重构：`、`杂项：`。
3. 每个逻辑单元一个原子提交，不要把多个无关改动堆进同一个 commit。
4. 未经用户明确批准，严禁 `push`。

### 提交策略

1. 核心原则：不要积压一大堆未提交改动；完成一个清晰的逻辑单元并验证后，就应及时提交。
2. 如果当前任务跨多个明显独立的子改动，应拆成多个原子提交，而不是一个巨大的总提交。
3. 如果只是一次性初始化新仓库、导入现有结构或用户明确要求“提交当前工作区”，可以把当前工作区作为单个逻辑单元提交。

### Git 串行规则

1. 所有 Git 操作都必须串行执行，禁止并发 `git add`、`git commit`、`git rebase`、`git stash`、`git checkout`、`git merge` 等命令。
2. 即使作用文件完全不重叠，也必须等待前一个 Git 命令完成并确认仓库锁已释放后，才能启动下一个 Git 命令。
3. 如果遇到 `.git/index.lock`，优先按并发或锁残留问题处理，不要直接假设是内容冲突。

### commit 前验证

1. 改入口、配置或路径解析后，至少应先通过：
   - `python3 tools/refresh_leaderboard_link.py`
   - `python3 -m unittest tests.test_gamesimulator.RunnerTests`
   - `python3 runner.py`
   - `python3 -m unittest tests.test_tooling`
2. 改 parser / execution / simulation 逻辑后，应先跑对应的目标测试；若整份 `tests.test_gamesimulator` 仍有历史失败，需明确区分“历史失败”和“本次新增回归”。
3. 没有新鲜验证证据时，不要声称“已完成”“已修复”“可提交”。
