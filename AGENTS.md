# TFWR_Simulator 仓库约束

## 仓库范围

1. 这个仓库只承载独立的 Python parity simulator；真正的源码包是 `src/gamesimulator/`。
2. 仓库根目录下的 `runner.py` 只是薄入口，职责是把 `repo/src` 加入 `sys.path` 后转调 `gamesimulator.runner`。
3. `tests/` 存放 Python 测试；`src/gamesimulator/unlock_snapshot.py` 是仓库内的默认 unlock 快照；`.env.example` 是本地配置模板。
4. 旧 `GameSimulator` 根目录下其他 `.py` 文件不属于这个仓库；后续不要再把它们迁回这里。
5. 按当前用户要求，`src/` 只放工作区源码；其中 `src/gamesimulator/` 是包代码，仓库根 `leaderboard/` 是指向真实 `Save0` 的本地链接目录，仓库根 `references/` 是参考资料目录。

## 外部 Save0 与配置

1. 真实 `Save0` 仍然是仓库外部内容，不进 git；仓库只允许在 `references/leaderboard_scripts/` 中保留 `lb_*.py` 参考副本。
2. 默认通过仓库根目录 `.env` 中的 `TFWR_SAVE_ROOT` 指向真实 `Save0`；`.env` 仅用于本地，不应提交。
3. 如果调用方显式传入 `save_root`，则以显式参数为准；否则再回退到 `.env` / 环境变量。
4. 路径与环境变量解析统一收口在 `src/gamesimulator/config.py`；不要在别的文件里重新发明一套路径推导逻辑。
5. 在 WSL 中运行时，允许把 `C:\...` 形式的 `TFWR_SAVE_ROOT` 自动转换为 `/mnt/c/...`；相关兼容逻辑也应只放在 `src/gamesimulator/config.py`。
6. `leaderboard/` 不由运行时自动修改；若 `.env` 改动，需要显式运行 `python tools/refresh_leaderboard_link.py` 来重建链接。
7. `references/leaderboard_scripts/` 与 `leaderboard/` 之间的同步必须显式运行 `python tools/sync_leaderboard_scripts.py cur2save` 或 `python tools/sync_leaderboard_scripts.py save2cur`；无论哪个方向都只允许影响 `lb_*.py`。

## 代码边界

1. `src/gamesimulator/` 是完整 Python 代码，可以正常使用 Python 标准库；不要把它按“游戏脚本语法限制”来写。
2. 如果任务涉及外部 `Save0/test.py`、`Save0/simulate.py` 或 `Save0/__builtins__.py`，那是“游戏侧脚本 / 外部资源”修改，不属于本仓库内部源码；默认不要顺手改。
3. 只有在用户明确要求“同时修改游戏侧入口或探针脚本”时，才去改外部 `Save0`。
4. 根入口的使用体验要保持稳定：用户应能在仓库根目录直接运行 `py runner.py simulate.py` 这一类命令，不需要关心包目录。

## 权威事实源

1. 做 simulator parity 时，事实优先级默认是：
   - 真实游戏运行产出
   - 外部 `Save0/__builtins__.py`
   - 外部 `Save0/lb_start.py`
   - 当前仓库实现
   - 旧实验结论或口头推断
2. 如果模拟器实现与真实游戏行为冲突，应优先修模拟器，不要拿当前实现反过来覆盖事实源。
3. `src/gamesimulator/unlock_snapshot.py` 只是仓库内快照，用于默认 unlock 推导；如果用户刷新了真实快照，再按用户要求同步更新对应 Python 常量。

## 验证与回归

1. 改入口、配置或路径解析后，优先验证：
   - `python3 tools/refresh_leaderboard_link.py`
   - `python3 -m unittest tests.test_gamesimulator.RunnerTests`
   - `python3 runner.py simulate.py`
   - `python3 -m unittest tests.test_tooling`
2. 改 parser / execution / simulation 逻辑后，优先跑对应的 `unittest` 目标类或目标测试，而不是只做入口 smoke test。
3. 如果整份 `tests.test_gamesimulator` 仍有历史失败，必须明确区分“本次新增回归”和“迁移前就存在的问题”，不要混在一起汇报。

## Git 约束

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
