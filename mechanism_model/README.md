# TFWR Mechanism Model

`mechanism_model/` 是正式的本地理论验证动作模型。

它和真实游戏 oracle workflow 分工不同：

- 这里只验证策略在简化机制下是否跑得通，以及大约需要多少动作。
- 它不模拟 Python 脚本解释时间、`1t` 判断真实耗时、Unity / BepInEx / leaderboard 停表。
- 随机种子不需要和真实游戏一致；重点是分布和约束接近真实机制。
- 真实排名结论仍以 `tfwr_orchestrator/` + `oracle_runner_mod/` 跑出来的游戏结果为准。

## 运行

当前项目使用本机可用的 .NET SDK，目标框架为 `net10.0`。

```bash
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- all
```

单独运行某个模型：

```bash
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 50
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --chase-limit-num 9 --chase-limit-den 25
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --extra-chase-limit-num 3 --extra-chase-limit-den 8 --extra-chase-min-apple-x 8
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --fill-step-num 1 --fill-step-den 2
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --phase-stats
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --cycle-adjacent-max-skip 16
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --use-move-result false --cycle-greedy-shortcut-max-skip 4
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --fill-step-num 14 --fill-step-den 15 --recover-detour
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --cycle-bfs-shortcut
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --check-tick-cost 1
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --use-move-result --check-tick-cost 1
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --use-move-result --cycle-wait-stats
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --cycle-entry-stats
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --chase-vertical-use-move-result
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --chase-skip-left-x 1
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --recover-west-stop-x 1
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --recover-bfs-to-origin
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --chase-limit-num 362 --chase-limit-den 1000 --recover-south-edge-probe
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --chase-limit-num 362 --chase-limit-den 1000 --recover-south-edge-cycle
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 100 --policy lb-current-game --recover-use-move-result
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- cactus --size 32 --samples 2000
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- companion --size 5 --crop grass --accept bush --target 4,3 --blocked 4,4
```

## 打榜筛选口径

使用本工具时，先把目标榜单的 `#1` 时间和当前复跑时间换算成机制预算，再看模型输出是否接近预算。

- 资源榜看每次有效收获周期、companion 命中率、reroll 次数和 support 维护动作。
- Dinosaur 看吃满 `1023` 个 apple 的总移动预算、分阶段 move/apple、动作 tick 和碰撞率。
- Cactus 看完成排序所需的 move、swap、measure 以及并行墙钟下界。
- 本工具默认不把 Python 解释、`1t` 判断、日志和本地搜索成本计入 `action_ticks`；Dinosaur 会额外报告 `can_move()` / `measure()` 计数，并可用 `--check-tick-cost` 折算成诊断预算。
- 只有动作结构接近 `#1` 预算或候选之间差距很小时，才优先做 `1t` 调用压缩；否则先改策略结构。

## 当前模型

### Dinosaur

- `lb-current-game` 按当前 `lb_dinosaur.py` 的前期追 apple + 后期固定回路流程，复刻 `Apple.Measure()` / `Apple.ChooseTarget()` / `DinosaurHat.OnMove()` 的一拍延迟机制；它是 Dinosaur 本地筛选的默认可信基线。
- 当前默认 Dinosaur 选项对齐仓库内 `lb_dinosaur.py`：`chase_limit=9/25`、`fill_step=15/16`、恢复段沿 Hamilton 路径绕行、并使用 `move()` 返回值替代移动前预检查。要复现旧基线时应显式传 `--chase-limit-num 1 --chase-limit-den 3 --fill-step-num 1 --fill-step-den 1 --recover-detour-max-steps 0 --use-move-result false`。
- 其他 Dinosaur policy 仍是抽象蛇身模型，只用于粗筛 GIF / Hamilton 短切方向，不能直接当成真实脚本可迁入结论。
- 默认输出 `lb-current-game`、`cycle`、`gif-safe-chase`、`gif-bfs-safe-chase` 和 `hamilton-shortcut-probe`。
- `gif-safe-chase` 是轻量邻格规则：只沿 Hamilton 序前进，并且不越过真实尾巴窗口。
- `gif-bfs-safe-chase` 是更接近 GIF 的本地理论候选：用 BFS 找 Hamilton 序单调、安全窗口内的 apple 短路径；它只证明动作模型方向，暂未压缩成游戏脚本可承受的调用结构。
- `hamilton-shortcut-probe` 是筛选器，不代表已确认安全；如果碰撞率不为 `0`，说明这个短切规则破坏了后续恢复结构。
- `--policy <name>` 可只跑一个 Dinosaur policy，避免把昂贵候选一起跑起来。
- `--chase-limit-num` / `--chase-limit-den` 只作用于 `lb-current-game`，用于本地筛 `length < size*size*num/den` 的前期追 apple 阈值；模型用乘法比较，避免整数除法提前截断 Python 脚本里的浮点阈值。
- `--extra-chase-limit-num` / `--extra-chase-limit-den` 只作用于 `lb-current-game`，用于本地筛“超过基础 `chase_limit` 后只追门控 apple”的额外追踪窗口；默认 `0/1` 禁用。
- `--extra-chase-min-apple-x` 只作用于额外追踪窗口，用于要求额外阶段只追 X 足够靠右的 apple，避免重复低 X apple 破坏左下角恢复形状。
- `--extra-chase-fill-step-num` / `--extra-chase-fill-step-den` 只作用于额外追踪窗口，用于试探额外阶段是否能少走 `chase_fill` 释放步数；默认 `-1/1` 表示沿用基础 `fill_step`。当前筛选显示少走释放步数会严重撞击，不支持迁入脚本。
- `--fill-step-num` / `--fill-step-den` 只作用于 `lb-current-game`，用于本地筛每轮 `chase_fill` 先沿安全回路走多少个 `length` 比例步；当前默认 `15/16` 对齐正式脚本。
- `--chase-vertical-use-move-result` 是本地负例探针：在追 apple 的纵向调整里，先尝试 `move(North/South)`，失败再退回 `West`。模型显示检测次数下降，但真实 request `749` 在 `300s` 内没有完成任何 leaderboard run，不支持迁入脚本。
- `--chase-skip-left-x` 是本地负例探针：当目标 apple 的 X 小于该值时跳过本轮追踪。它会导致早期低 X apple 被长期跳过并进入空转，不属于当前脚本口径。
- `--phase-stats` 会输出 `lb-current-game` 每个阶段的平均 move、action tick、apple 数和 tick 占比，用于定位下一轮策略优化应优先碰哪一段。
- `--cycle-adjacent-max-skip` 只作用于 `lb-current-game` 的 `cycle_finish`，用于筛“已知 apple 正好相邻且处在 Hamilton 前方窗口内时直接踏入”的 O(4) 短切；默认 `0` 禁用。
- `--cycle-greedy-shortcut-max-skip` 是本地负例探针：假设 `cycle_finish` 能持续知道下一颗 apple，用 O(4) 邻格检查选择 Hamilton 前方窗口内更靠近 apple 的方向。当前筛选显示它会显著增加等待步数和检测量，窗口越大越差，不支持迁入脚本。
- `--recover-detour` 只作用于 `lb-current-game` 的 `recover_west` / `recover_south`，是旧的一步绕行别名；当前正式脚本口径默认等价于 `--recover-detour-max-steps <size*size>`。
- `--recover-detour-max-steps` 只作用于 `lb-current-game` 的恢复段，表示原方向被挡后最多沿 Hamilton 路径绕行多少步。
- `--recover-west-stop-x` 是本地负例探针：恢复西移阶段停在指定列后直接恢复南移。它会破坏下一轮 `chase_fill` 的左下角形状，当前筛选结果不支持迁入脚本。
- `--recover-bfs-to-origin` 是本地负例上界探针：每轮追 apple 后尝试用有限 BFS 回到 `(0,0)`，并用虚拟执行确认进入原点后下一步 Hamilton 出口仍可走。它只用于证明“直接找回原点路线”是否有结构收益，当前筛选结果不支持迁入脚本。
- `--recover-bfs-max-depth` / `--recover-bfs-max-nodes` 限制 `--recover-bfs-to-origin` 的搜索规模；默认分别为 `64` 和 `size*size`。
- `--recover-south-edge-probe` 是本地负例探针：当 `recover_south` 在 `x=0` 且 South 被挡时尝试简单逃逸方向。它不属于当前脚本口径，只有模型筛选需要时才启用。
- `--recover-south-edge-cycle` 是本地负例探针：当 `recover_south` 在 `x=0` 且 South 被挡时沿 Hamilton 路径绕回左边界后继续向南。它不属于当前脚本口径，只有模型筛选需要时才启用。
- `--recover-use-move-result` 是本地负例探针：恢复段直接尝试 `move(West/South)` 来替代 `can_move()` 预检查。失败 `move()` 会消耗 `1` tick 并改变尾巴释放时序，当前筛选结果不支持迁入脚本。
- `--cycle-bfs-shortcut` 是本地上界探针：假设 `cycle_finish` 能持续知道下一颗 apple，并复用 Hamilton 单调小窗口 BFS 尝试短切。它不代表可直接迁入游戏脚本，迁入前必须另算 `measure()` 和搜索成本。
- `--check-tick-cost` 只用于诊断，把脚本侧 `can_move()` / `measure()` 次数按指定 tick 成本折入 `avg_total_ticks_with_checks`；默认 `0`，不改变 `action_ticks`。
- `--cycle-use-move-result` 只作用于固定 `cycle_finish`，用 `move()` 返回值替代 `can_move()` 预检查，用于评估后半段 `1t` 检测压缩。
- `--use-move-result` 作用于 `lb-current-game` 的 `update_and_move()` 与固定 `cycle_finish`，用 `move()` 返回值替代移动前预检查；外层需要分支决策的 `can_move(North/South)` 仍会计入检测次数。
- `--cycle-wait-stats` 输出 `cycle_finish` 的 apple 等待分布：每颗 apple 平均等待移动数、当前 head 到 apple 的 Hamilton 前向距离分布和曼哈顿邻域命中率，用来判断局部短切是否有足够机会密度。
- `--cycle-entry-stats` 输出进入 `cycle_finish` 时的平均脚本长度、grid dinosaur 数、剩余 apple、前期 moves / action ticks / 检测次数，用来判断前期改动是否只是把成本从后半段转移到前半段。
- `--include-heavy` 会额外运行更重的本地探针；它不属于默认验证入口。
- `action_ticks` 只统计 `move()` 动作耗时。
- apple `measure()`、本地寻路搜索和其他廉价检测不计入 `action_ticks`；`can_move()` / `measure()` 会作为脚本检测次数单独输出。
- `--max-moves` 是本地防卡死上限，不是游戏机制；32x32 纯回路吃满可能需要几十万次移动，默认值刻意高于这个量级。
- 默认 `--runs` 偏小，目的是快速筛选；要比较接近候选时再显式增加样本数。

模型依据：

- `references/DecompiledSource/Core/Core.decompiled.cs` 中 `Apple.ChooseTarget()` 会在非 Dinosaur / Apple 的位置里选下一个 apple 目标。
- `Apple.Measure()` 返回当前 apple 预先选好的 `nextPos`；当前脚本走到 apple 格时读取的是下一颗 apple 坐标。
- `DinosaurHat.OnMove()` 在离开当前 apple 格时才吃 apple、生成下一颗 apple，并执行 `ops -= floor(ops * 0.03)`。
- `DinosaurHat.OnMove()` 每步末尾会检查 `target.nextPos == oldPos` 并重新 `ChooseTarget()`，本地模型也必须模拟这个重投，否则会过早出现不可生成 apple 的假失败。
- `DinosaurHat.BoneCount()` 数的是 grid 上的 `Dinosaur` 实体数量；模型完成口径使用 grid dinosaur count，而不是内部 tail 链表长度。
- `Drone.Move()` 会返回布尔值；不能移动时直接返回 `false`，不调用 `DinosaurHat.OnMove()`，不改无人机位置，调度层失败成本为 `1` tick。因此 `lb_dinosaur.py` 可以在不改变路径的情况下用 `move(dir)` 返回值替代部分 `can_move(dir)` 预检查。

### Cactus

- 模拟 cactus 值 `0..9` 的随机分布。
- 使用当前 `lb_cactus.py` 的 window3 鸡尾酒式单线排序代理。
- 先排序所有行，再排序所有列。
- `action_ticks` 只统计 `move()+swap()`。
- `measure()` 数量单独输出，不并入动作 tick。

模型依据：

- `references/DecompiledSource/Core/Core.decompiled.cs` 中 `Cactus.OnRestart()` 使用 `randomCactus.Next(10)`。
- `references/leaderboard_scripts/lb_cactus.py` 当前主线为行排序后列排序。

### Companion

- 模拟 `Growable.ChooseCompanion()` 的类型和位置分布。
- 默认场景对应单草 / 双草讨论常用的 Bush-only 检查：
  - world size `5`
  - target `(4,3)`
  - blocked `(4,4)`
  - crop `grass`
  - accept `bush`
- 支持通过 `--support x,y;x,y` 指定可承接 companion 的 support 集合。
- 在 shell 中传多个点位时需要加引号，例如 `--support '1,2;2,2'`。
- 未指定 support 时，默认把目标曼哈顿半径 `3` 内、排除 target 和 blocked 的格子视为可承接 support。

模型依据：

- `Growable.ChooseCompanion()` 在 `[-3,3]` 偏移里重抽，要求曼哈顿距离不超过 `3` 且不是当前格。
- companion 类型从 `grass / bush / carrot / tree` 抽取，并重抽到不等于当前作物。

## 口径

- 这个工具适合筛掉理论上明显不成立的路线。
- 如果某个候选在这里表现接近或更好，再迁移到 `references/leaderboard_scripts/lb_*.py` 做真实游戏验证。
- 如果真实游戏结果和本模型冲突，以真实游戏为准，并回头修正模型口径。
