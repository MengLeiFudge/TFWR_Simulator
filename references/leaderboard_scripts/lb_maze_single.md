# lb_maze_single

## 2026-10-28：迁入增量全点对路由，官方57轮126.703281秒

当前版把已在多机独立小迷宫中验证的树形建图、对称全点对表和新边增量更新迁到单机8×8。旧版每次宝藏重新双向搜索，并沿途探查闭墙；新版建表后直接走路，只在上一宝藏位置出发前检查新通路。不同探墙时机可能增加移动，完整计费包含该代价，没有把旧版较短路线与新版较低规划费拼接。

三类时间：完整本地seed0/1/123为107.343662、128.242054、133.398298秒，均值122.994672秒；request156短筛终态实际17轮124.339412秒；request157官方完整57轮126.703281秒，范围105.937–160.429秒。较上一正式145.112秒缩短18.408719秒、12.6859%。单轮拓扑波动较大，保留完整统计而不以最好一轮为成绩。

固定seed1当前旧版完整151.288936秒，新版128.242054秒；新版3097次move、531次can_move、97337解释器tick。三seed均完成616448 Gold，包含300次正常搬迁和最终一次harvest，未利用200tick内重复领奖。实机完整终态、双日志和结果页自动关闭均正常，临时覆盖的两份存档在idle157恢复。公开账号新分数/名次尚未独立确认。

算法来源：[zzlg-git/TheFarmerWasReplaced_Maze_1min28s](https://github.com/zzlg-git/TheFarmerWasReplaced_Maze_1min28s/tree/e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629)，本仓库在该多机算法基础上改为单机入口并对称建表。上游树未附许可证，保留来源，本轮仅本地使用、未push或发布。执行源SHA256 `8fea560d319579ede8d7af63e502c1587cad293af2fe8776fb42db20aaaa84e4`；正式文件只调整注释，执行AST一致。工具LSP与实际游戏编译/完整运行结果见`acceptance.json`。

证据目录`.codex/leaderboard-astra/maze-single-incremental-routes/`保存构建器、原版快照、场景、模型与原始实机结果、来源哈希和恢复记录。首个场景误用了不支持的`world_size`字段，解析器执行前拒绝；修正为Expand5/Megafarm0推导8×8后才运行，失败报告仍保留，未计入时间均值。后续优先比较出发点探墙与沿途探墙的实际净收益，或减少首次探索回退；尚无新候选成绩。

## 2026-10-26：闭墙刷新版完成官方统计并上榜

当前正式版采用闭墙刷新候选，保持真实移动、探测和每次宝藏结算。request 84正常完成50轮，官方均值145.112秒；Steam账号成绩查询在17:35 UTC确认第60名、145112ms。相比旧历史实测183.020秒缩短37.908秒。未使用200tick窗口重复收取同一宝藏的漏洞，比较基准仍为#10。

三类时间：本地完整三seed均值141.640540秒；正式版短时复核request 91实际完成3轮、均值146.796333秒；官方完整统计145.112秒。短复核停止阈值为至少两轮，终态包含3个真实run，按终态统计。

完整统计执行源SHA256为`ddcd6d961b3a62995b8a6df858992588310707a439037a7896b3aea68a5a7ab2`；正式版仅规范时间注释、AST相同，源`a0029113f6e18073b8df1d524aebe62e54adeb8114a7ba90be76106c4d1ef965`已重新部署实机复核。两次运行无水不足警告；短复核sample_limit停止不作为完整成绩。

证据保存在`.codex/leaderboard-astra/real-20261026/`的`request84-full.json`、`request91-full.json`、`promotion-manifest.json`及公开账号查询记录。临时存档已恢复，游戏正常退出。

## 此前阶段记录

当前阶段（2026-10-24）：闭墙刷新候选完成seed0/1/123完整本地配对，均值179.469674→141.640540游戏秒，净省37.829134秒（21.078%）。逐seed完整移动序列、新边发现次序、最终有序图和maze随机流均保持。三值为141.640540 / 未取得 / 未取得；进入待实机队列，正式脚本未迁入。

## 2026-10-24：模型作用域首差与完整原版基线

当前源码SHA256为 `6390ba256e4546be77b725ee607f071d78078a915d0484d2fb4e12da0354ed8c`。首次本地观测在5.954108秒、首次BFS的 `bfs_stamp` 读取处报NameError，目标未完成。游戏 `global` 跳过当前函数、沿父作用域寻找绑定，而原模型直接沿用Python模块global，错误跳过外层入口的局部计数器；这是模型语义差异，未修改正式策略绕过。

模型提交 `8f68152` 按Core的Parser与Scope规则修正嵌套绑定、静态调用标记和闭包副本的共享绑定。Python编译、两文件ty零诊断及16个正式榜单脚本的模型编译通过。修正后仅重跑同SHA的seed1一次，原失败报告保留。显式满级8×8、Expand5/Megafarm0，初始仅Power/Weird各十亿，目标616448 Gold；30秒、50万API、300万检查点、64MiB轨迹限额。

完整结果191.299865秒，工作2.737秒，483070解释器tick；move2997、can_move10697、use_item302。DFS日志5.454352秒，最终Gold616448，库存非负。轨迹22125条、4704294字节，原失败轨迹为新轨迹的精确前缀。此结果证明原脚本在本地越过了作用域阻塞，不构成新的实机精度验收。

证据目录 `.codex/leaderboard-sol/maze-single/refresh-cost/`：原 `baseline-seed1.json` 保留失败现场，当前完整基线为 `baseline-fixed-seed1.json`，配套 `fixed-manifest.json` 和 `analysis-fixed.json`。已有API轨迹重建出2863次路径后刷新、7083次已知通路重复查询和14166次重复加边调用；后续候选须计入闭墙列表构造/维护，并核对实际移动序列与图边顺序，不把删查询数量直接当作净节时。

## 2026-10-24：闭墙刷新候选首seed完整配对

候选SHA256为 `ddcd6d961b3a62995b8a6df858992588310707a439037a7896b3aea68a5a7ab2`，基线为上述正式原版，模型采用8f68152作用域修正。DFS完成后按原East/North/West/South顺序建立各格尚未确认开放的邻边列表；仍在每次路径移动后刷新当前位置，只查询待查边。发现新开边时向图两端追加，并从两端待查列表移除，保持其余顺序。DFS、双向BFS、寻宝与失败处理保持。

保守净预算9.441865秒先过准入门槛后，使用同场景和30秒/50万API/300万检查点/64MiB轨迹预算，仅运行候选seed1一次；原版完整报告直接复用。

| 项目 | 原版 | 候选 |
| --- | ---: | ---: |
| 完整本地游戏秒 | 191.299865 | 151.288936 |
| move调用 | 2997 | 2997 |
| can_move调用 | 10697 | 3614 |
| 解释器tick | 483070 | 247004 |
| 最终Gold | 616448 | 616448 |

15项门槛全部通过。两份完整轨迹的2997次move方向、返回值及坐标逐项一致；DFS前缀相同，15条新边首次发现的move序号、方向和插入次序相同，最终有序邻接图相同。maze抽样均39532次；其余全部API计数不变。少7083次已知通路查询、少236066解释器tick，与静态推导精确吻合。构造5890t及列表维护已计入；实际节时40.010930秒，与精确预算40.024757秒相差−0.013827秒。

候选本地计算1.150秒，轨迹3168549字节，未触限、库存非负。被动水肥和Power消耗随世界时间缩短而变化，差额单列；不声称所有随机流均保持。当前预测为#10的约1.350倍，仅单seed，不外推排名。

首seed三类时间：**151.288936 / 未取得 / 未取得**。证据 `.codex/leaderboard-sol/maze-single/closed-refresh/{comparison.json,three-times.json,research-note.md}`。此后按同SHA seed0→123顺序完成配对，结果见下节；保留本节单seed历史口径。

## 2026-10-24：闭墙刷新三seed确认与待实机队列

复用seed1未重跑，seed0原版与候选各一次且全部门槛通过后，才补seed123同样配对。候选SHA保持 `ddcd6d96`，场景、模型语义和各次30秒/50万API/300万检查点/64MiB轨迹限额不变。

| seed | 原版完整本地秒 | 候选完整本地秒 | 净省秒 | 节时预算误差秒 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 159.374908 | 124.960883 | 34.414025 | 0.009547 |
| 1 | 191.299865 | 151.288936 | 40.010930 | -0.013827 |
| 123 | 187.734248 | 148.671801 | 39.062447 | 0.021235 |
| 均值 | 179.469674 | 141.640540 | 37.829134 | — |

三个seed均完成616448 Gold。完整移动方向、结果和坐标逐项相同（2341/2997/2875次），新边首次发现move序号与插入次序相同（26/15/20条），DFS前缀、最终有序图及maze随机流保持。can_move分别减少6166/7083/6878次，解释器少202840/236066/230296t，与含构造和维护成本的预算精确对应；最大节时预算误差0.021235秒。这是本地原版与候选的费用核算，不是模拟器对实机的精度证据。

当前三类时间：**141.640540 / 未取得 / 未取得**，约为缓存#10（112.091秒）的1.264倍。样本范围124.961–151.289秒，后续实机先比较同版本样本分布；若明显偏离，再做同seed对照，不能把跨seed波动直接归为模型误差。

候选进入待实机队列，顺序为Hay→Carrots Single→Dinosaur→Sunflowers Single自然保留→Maze Single闭墙→Reset组合。请求79收口和Save0冻结边界保持；本轮不继续扩seed或改正式脚本，Sol接续胡萝卜单机八锚点及木头/南瓜基线补齐。

证据 `.codex/leaderboard-sol/maze-single/closed-refresh/{comparison-seeds0-1-123.json,three-times-seeds0-1-123.json,research-note-seeds0-1-123.md}`；原版三seed独立保存在 `refresh-cost/three-times-fixed-seeds0-1-123.json`，单seed历史均保留。

## 榜单目标

- 目标资源：`Items.Gold`
- 单机路线
- 当前脚本目标数量为 `616448`

## 结算机制说明

- 迷宫单榜和多榜的底层规则一致：
  - 生成一个 `n x n` 迷宫后，单次 Treasure 收益是 `n * n * 32`
  - Treasure 最多可以被重新定位 `300` 次
  - 所以完整做满时，总量级是 `n * n * 301 * 32`
- 套回单榜目标：
  - `8x8` 面积是 `64`
  - `64 * 301 * 32 = 616448`
- 这意味着单机迷宫榜的目标值正好对应“一次完整的 `8x8` 迷宫重定位流程”
- 也就是说，单榜迷宫当前也更像“一次到位问题”，而不是随便选小图多刷很多轮的问题

- 另外，反编译源码 `Treasure.RepositionTreasure(...)` 还能确认一个当前版本很关键的事实：
  - 对 Treasure 使用 `Weird_Substance` 后，新宝藏不是立刻出现
  - 而是通过 `StartTimer(CompleteRepositioning, sim.OpDuration * 200.0)` 延迟完成换位
- 这条时序事实不只影响多榜，同样会影响单榜里“什么时候该继续 use、什么时候该收”的判断

## 当前基线

- 当前默认入口：`lb_maze_single()`，DFS全探图后以复用缓冲区的双向BFS寻宝。
- 当前路线：8×8单机一次DFS建图；每次measure后用双向BFS走到Treasure，逐步刷新新打开的通路，再用Weird_Substance重定位，直到收获达标。
- 2026-04-25 真实请求 `217`：当前 `main1()` 连续 `30s` 没有任何 `run=` 输出，按 `output stall` 规则停止；因此当前默认基线在真实短窗里不可作为有效主线。
- 2026-04-25 外部 `Save0/maze_astar.py` 候选：通过覆盖既有 `gamesave/lb_maze_single.py` 验证，没有向真实存档新增依赖文件；请求 `216` 两轮停表，`run=1 time=5:03.828`、`run=2 time=5:02.695`、`finished=false runs=2 average=5:03.261`。
- 重新读取当前 `Save0/maze_astar.py` 后再测：请求 `244` 两轮停表，`run=1 time=5:06.562`、`run=2 time=4:28.164`、`finished=false runs=2 average=4:47.363`。
- 真源同步后复验：请求 `245` 两轮停表，`run=1 time=5:35.663`、`run=2 time=4:31.171`、`finished=false runs=2 average=5:03.417`。
- 结论：当前 `maze_astar` 版本能稳定完成并明显优于旧 `main1()`，迁入为当前默认；它的文件头作者注释提到“有些地方效率不高”，但这是后续优化方向，不是拒绝迁入的理由。
- 2026-04-26 DFS + 直线贪心 + BFS 候选：请求 `323`，`run=1 time=3:16.699`、`run=2 time=3:03.899`、`run=3 time=3:20.117`、`run=4 time=3:12.148`，停止摘要 `finished=false runs=9 average=3:15.393`。
- 2026-04-26 DFS + BFS-only 候选：请求 `324`，停止摘要 `finished=false runs=14 average=3:15.310`，刷新当时本地最好成绩。探针显示 `explore_time≈5.47s`、`steps=126`、每轮 `bfs=301`，说明一次全探图成本很低，主要剩余成本在 301 次重定位延迟与实际移动。
- 2026-04-26 BFS 缓冲复用候选：请求 `361`，把每次 BFS 的 `previous` / `queue` / `path` 临时列表改为固定缓冲区 + `stamp` 标记，避免 301 次寻宝重复分配列表；主动停止摘要 `finished=false runs=25 average=3:05.876 stable=true`，优于 `3:15.310`。
- 2026-04-26 双向 BFS 候选：请求 `362`，在缓冲复用基础上从当前位置和 Treasure 双端扩展；主动停止摘要 `finished=false runs=31 average=3:04.233`。单轮 `nodes` 大多降到 `4,700~7,100`，低于单向 BFS 复用版的约 `7,700~9,300`，但总时间只小幅提升，说明剩余瓶颈主要是移动和重定位。
- 2026-05-02 当前默认双向 BFS 复测：请求 `422` 在 16 轮时达到 runner 稳定停表，均值 `2:59.520`，刷新当前本地最好记录；有效轮包括 `2:46.699`、`2:42.148`、`2:50.781`、`3:27.999`、`2:50.699`、`2:53.599`、`3:23.359`、`2:57.656`、`3:07.799`、`3:10.234`、`2:44.335`、`3:26.367`、`2:59.335`、`2:59.296`、`2:49.599`、`2:42.421`。`finished=false runs=17 average=2:56.975` 是外部停表取消摘要，不作为完整统计结果。
- 2026-05-02 East-first 方向优先级：请求 `424` 在 3 轮时达到 runner 稳定停表，均值 `2:46.640`；追加请求 `425` 在 4 轮时达到稳定停表，均值 `2:49.743`。改法只把 `directions` 从 `[North, East, South, West]` 改成 `[East, North, West, South]`，双向 BFS 与寻宝时序不变。两次都快于 `2:59.520`，保留为当前默认实现，并同步更新 `lb_start.py`。
- 2026-05-30 当前版本复跑：请求 `618` 有效六轮 `2:43.788` / `3:02.773` / `3:21.289` / `2:41.796` / `3:08.007` / `3:20.468`，稳定均值 `3:03.020`；后续 `finished=false` 取消摘要不作为成绩。
- 2026-04-26 DFS + next-hop 全对查表候选：请求 `325`，停止摘要 `finished=false runs=12 average=4:22.971`，明显慢于 BFS-only；探针显示每轮 `table_time=14.14`、`table_nodes=4096`，说明当前脚本环境下全对预计算的列表构建成本不能抵消单源 BFS 成本。
- 同步工具对 `lb_maze_single` 生成 `lb_start.py` 时使用外部入口验证过的 `1000` 模拟速度。

## 第二轮结构重写策略校正

- DFS全探图已是当前实现；寻宝已从早期单源BFS演进为双向BFS，不再作为待实现P0。
- “DFS 全探图 + 全对最短路 / next-hop 查表”已经由请求 `325` 证伪：
  - `8x8` 只有 `64` 格，但当前脚本环境里 `table_time=14.14` 仍过高。
  - 均值从 BFS-only 的 `3:15.310` 退到 `4:22.971`。
- 后续不要重复实现完整全对查表；如果继续做路径缓存，只能测更轻量的候选：
  - 缓存最近一次 BFS 的父指针或首步，不构建完整 `64x64` 表。
  - 只在墙消失后做局部刷新，避免每次重定位重建全局数据。
- 当前未解决的结构瓶颈不是“是否 DFS”，而是：
  - 301 次 Treasure 重定位延迟。
  - 每次寻宝的真实移动步数。
  - 墙消失后能否低成本吃到直线路径收益。

## 通用注意事项下的榜单特化

- 单机 maze 不该再被理解成“随便找个小图高频 use_item 就行”
- 因为按目标值反推，`8x8` 才是和当前单榜完全对齐的一次到位面积
- 当前单榜真正要解决的是：
  - Treasure 延迟换位后的正确 use / harvest 节奏
  - `8x8` 迷宫是否能靠信息与路径策略压到可接受时间

## 当前版本结论

- `main1`
  - 2x2 mini-maze 基线
  - 设计重点是把每轮逻辑压到尽可能稳定和简单
  - 真实短窗 30 秒无完成轮，已不再作为默认入口
- `maze_astar`
  - 旧默认路线
  - 使用单机 A* 在已探明墙信息上寻路，每次移动后刷新墙体置信信息
  - 请求 `244` 两轮均值 `4:47.363`
  - 请求 `245` 真源同步后两轮均值 `5:03.417`
  - 相比 2x2 基线，优势来自直接匹配 8x8 一次到位目标，而不是小迷宫多轮堆收益
- `dfs_bfs`
  - 当前默认路线
  - 一次 DFS 全探图后，每次 Treasure 重定位只做单源 BFS，不再维护 A* 的 open_set、f_value 和路径深拷贝
  - 请求 `324` 停止摘要 `finished=false runs=14 average=3:15.310`
  - 相比 `maze_astar` 的 `4:47.363`，约提升 `32%`
- `dfs_bfs_reuse_buffers`
  - 已被双向 BFS 替代
  - 保留 DFS+BFS 的寻路结构，只把单源 BFS 的 `previous`、`queue`、`path` 改成固定缓冲区复用
  - 请求 `361` 主动停止摘要 `finished=false runs=25 average=3:05.876 stable=true`
  - 相比 `dfs_bfs` 的 `3:15.310`，约提升 `4.8%`；这说明单机迷宫的脚本分配开销仍然值得压缩
- `dfs_bidirectional_bfs`
  - 当前默认路线
  - 在固定缓冲区基础上改为双向 BFS，仍然保持最短路，不退回 DFS 树路径
  - 请求 `362` 主动停止摘要 `finished=false runs=31 average=3:04.233`
  - 相比 `dfs_bfs_reuse_buffers` 的 `3:05.876` 只提升约 `0.9%`；可保留，但后续继续压 BFS 计算的收益已经很小
  - 2026-05-30 当前版本复跑请求 `618` 波动较大，六轮稳定均值 `3:03.020`

## 失败对照

- “2x2 多轮堆起来也许就够快”的理解
  - 这条线当前应视为偏弱口径
  - 因为按目标值反推，`8x8` 才是与单榜完全对齐的一次到位面积
- 未验证当前文件就沿用旧“寻路成本高”的判断
  - 当前应视为流程错误
  - 正确做法是先读取当前外部文件，再用真实游戏两轮验证
  - 请求 `244` 证明当前版本至少已经优于仓库默认基线
- 旧版里若默认 Treasure 立刻换位的逻辑
  - 在当前版本里同样是危险时序假设
- `dfs + next-hop 全对查表`
  - 请求 `325` 停止摘要 `finished=false runs=12 average=4:22.971`
  - 失败原因：`table_time=14.14` 的预计算开销过高，且路径执行没有比单源 BFS 明显省掉足够游戏时间
- `dfs + 直线贪心 + BFS`
  - 请求 `323` 停止摘要 `finished=false runs=9 average=3:15.393`
  - 结论：能刷新旧 A*，但不优于 BFS-only；直线贪心会绕开最短树路径，保留价值不大
- `measure()==None` 原地等待探针
  - 请求 `348` 临时在 `goto_treasure()` 的 `measure()==None` 分支中加入最多 `2s` 原地等待，并打印 `measure_waits` / `wait_time`。
  - 结果：停止前 `27` 轮均输出 `measure_waits=0 wait_time=0`，说明当前 DFS+BFS 主流程里没有走到该分支。
  - 停止摘要 `finished=false runs=27 average=3:12.886` 属于随机波动，不能归因于等待策略；候选已从 `.py` 回退，只保留本探针结论。
- `DFS 树父指针路径缓存`
  - 请求 `356` 在一次 DFS 全探图后缓存 DFS 树父指针，并用树路径替代每次单源 BFS。
  - 真实完成多轮：`run=1 5:09.609`、`run=2 4:50.039`、`run=3 4:22.929`、`run=4 4:18.671`、`run=5 5:04.062`、`run=10 4:09.296`。
  - 停止摘要 `finished=false runs=10 average=4:37.846 stable=true`，明显慢于当前 `dfs_bidirectional_bfs` 基线 `3:04.233`。
  - 失败原因：DFS 树路径不等于迷宫图最短路，省掉 BFS 计算后增加的移动步数远大于脚本计算收益；候选已从 `.py` 回退。
- 去中心开局 + 探图遇宝即 use + 换位后首段路径探针
  - 2026-04-30 请求 `394` 验证。
  - 改法：删除开局移动到中心；DFS 探图到达 Treasure 时立即 `use_item(Items.Weird_Substance, substance)`；每 50 次重定位记录下一次 BFS 的 `nodes` / `steps`。
  - 结果：runner 停表为 `reached stable leaderboard runs 12 avg=3:09.430`，慢于当前基线 `3:04.233`，不保留。
  - 典型完成轮：`run=6 time=3:01.992`、`run=8 time=2:59.335`、`run=10 time=2:57.656` 有较快单轮，但 `run=4 time=3:27.968`、`run=9 time=3:32.499` 拉高均值。
  - 探针结论：换位后的下一次 BFS 路径成本波动很大，例如第 4 轮 `count=300 nodes=48 steps=13`、第 8 轮 `count=300 nodes=22 steps=8`，说明用户指出的“换位后首次寻路”确实是长尾来源；但单纯去中心和探图遇宝即 use 没形成稳定收益。
- 只删除开局中心移动
  - 2026-05-02 请求 `509`：runner 输出 `reached stable leaderboard runs 6 avg=3:15.434`。
  - 改法：只删除 `clear()` 后移动到中心的 `for _ in range(size // 2): move(North); move(East)`；保留 East-first、双向 BFS、逐步刷新和诊断输出。
  - 有效轮包括 `3:55.499`、`3:16.523`、`3:11.171`、`3:05.937`、`3:05.781`、`2:57.695`、`2:57.499`。
  - 停表后取消摘要 `finished=false runs=9 average=2:49.358` 不作为刷新成绩。
  - 结论：不居中会引入很重的前几轮长尾；代码已恢复开局中心移动。
- 直线可走时跳过 BFS
  - 2026-05-02 请求 `423`：runner 在 14 轮时输出 `reached stable leaderboard runs 14 avg=3:19.134`。
  - 改法：在 `goto_treasure()` 中先朝 Treasure 的横向或纵向方向尝试直走 1 步，只有直线单步不能推进时才调用双向 BFS。
  - 典型输出：`bfs` 从默认每轮 `301` 降到约 `200~241`，`nodes` 降到约 `3394~5831`，但有效轮时间包括 `3:42.399`、`3:31.484`、`3:47.031`，明显拉高均值。
  - 结论：直线单步减少了 BFS 计算次数，但会增加迷宫绕路和长尾；慢于当前 `2:59.520`，实现已回退。
- East-South 方向优先级
  - 2026-05-02 请求 `426`：runner 在 3 轮时输出 `reached stable leaderboard runs 3 avg=3:11.164`。
  - 改法：将方向顺序从当前有效的 `[East, North, West, South]` 改成 `[East, South, West, North]`。
  - 有效轮为 `3:27.399`、`3:03.476`、`3:02.617`，明显慢于 `2:46.640`。
  - 结论：East-first 的收益不能简单归因于横向优先，第二优先方向选 South 会放大长尾；实现已回退为 East-North。
- East-North-South 尾部顺序
  - 2026-05-02 请求 `427`：runner 输出 `reached stable leaderboard runs 2 avg=2:53.367`。
  - 改法：保留 East / North 前两优先级，只把尾部从 `[West, South]` 改成 `[South, West]`。
  - 可见完成轮为 `3:00.234`、`2:46.499`，未刷新 `2:46.640`。
  - 结论：尾部方向也影响 tie-break；当前仍保留 `[East, North, West, South]`。
- West-first 对称方向
  - 2026-05-02 请求 `428`：runner 输出 `reached stable leaderboard runs 3 avg=3:00.286`。
  - 改法：将方向顺序改成 `[West, North, East, South]`，用于对照 East-first 是否只是横向优先收益。
  - 可见完成轮为 `3:06.171`、`2:56.601`、`2:58.085`，未刷新 `2:46.640`。
  - 结论：当前迷宫 tie-break 明确偏向 East-first，不是任意横向优先都有效；实现已回退。
- East-West 方向优先级
  - 2026-05-02 请求 `430`：runner 输出 `reached stable leaderboard runs 4 avg=2:56.777`。
  - 改法：将方向顺序改成 `[East, West, North, South]`，用于确认 East-first 下第二优先级是否应继续偏横向。
  - 有效轮为 `2:44.687`、`2:58.398`、`3:07.382`、`2:56.640`，未刷新 `2:46.640`。
  - 结论：East 后第二优先级必须保留 North；实现已回退。
- North-West 方向优先级
  - 2026-05-02 请求 `431`：runner 输出 `reached stable leaderboard runs 3 avg=2:58.135`。
  - 改法：将方向顺序改成 `[North, West, East, South]`，用于测试 North-first 下的另一个 tie-break。
  - 可见完成轮为 `2:33.867`、`3:10.702`、`3:09.837`，出现快单轮但长尾很重，未刷新 `2:46.640`。
  - 结论：North-first 仍不稳定；实现已回退。
- South-first 方向优先级
  - 2026-05-02 请求 `432`：runner 输出 `reached stable leaderboard runs 3 avg=3:03.089`。
  - 改法：将方向顺序改成 `[South, East, North, West]`，用于覆盖 South-first 首方向。
  - 有效轮为 `3:05.580`、`2:56.499`、`3:07.187`，未刷新 `2:46.640`。
  - 结论：South-first 明显偏慢；实现已回退。
- 只让 BFS 使用 East-first
  - 2026-05-02 请求 `434`：runner 输出 `reached stable leaderboard runs 12 avg=3:53.007`。
  - 改法：DFS 探图和边刷新恢复 `[North, East, South, West]`，只在 `move_with_bfs()` 内按 `[East, North, West, South]` 查找边。
  - 结果：有效轮多数落在 `3:28~4:26`，明显慢于 `2:46.640`。
  - 结论：East-first 收益不是单独替换 BFS 邻居顺序即可得到；拆分后的边查找成本和探图顺序退化都很重，已回退为全局 East-first。
- 删除内部诊断 `quick_print`
  - 2026-05-02 请求 `450`：runner 输出 `reached stable leaderboard runs 11 avg=3:10.059`。
  - 改法：删除 DFS 探图后的 `explore_time` 诊断输出，以及完成寻宝循环后的 `total_time / bfs / nodes` 诊断输出；迷宫策略、方向顺序和双向 BFS 不变。
  - 有效轮包括 `3:01.249`、`2:47.099`、`3:29.899`、`3:32.599`、`3:02.109`、`3:26.874`、`2:54.062`、`3:11.132`、`3:14.799`、`3:07.031`、`3:03.799`。
  - 取消摘要 `finished=false runs=13 average=3:00.462` 不作为刷新成绩。
  - 结论：没有刷新；诊断输出不是当前主瓶颈，代码已恢复两条 `quick_print`，保留后续判断 BFS 节点数和探图成本的观测能力。
- 删除 BFS / 探图诊断计数维护
  - 2026-06-10 代码候选：删除只服务最终诊断的 `explore_steps`、`bfs_count`、`bfs_nodes` 及输出中的 `steps= / bfs= / nodes=` 字段；保留 `explore_time / total_time` 两条阶段时间输出。
  - 这不同于请求 `450` 的“删除 quick_print”：本候选移除的是 DFS 每步计数和 BFS 每个扩展节点的循环内计数维护，East-first、双向 BFS、逐步刷新动态边、寻宝和收割策略都不变。
  - 验证：`python3 -m py_compile references/leaderboard_scripts/lb_maze_single.py` 通过。真实游戏当前仍为 `game_tick=0`，暂未能跑完成轮；文件头成绩不更新。
  - 结论：这是单机迷宫主结构内的管理成本候选。游戏恢复后短跑确认；若无稳定刷新或需要重新定位 BFS 长尾，则回退或临时恢复诊断计数。
- East-first 单源 BFS
  - 2026-05-02 请求 `451`：runner 输出 `reached stable leaderboard runs 11 avg=3:17.658`。
  - 改法：保留 `[East, North, West, South]` 方向顺序，但把 `move_with_bfs()` 从双向 BFS 改回单源 BFS 固定缓冲区。
  - 有效轮为 `3:31.054`、`3:26.399`、`3:20.464`、`3:17.695`、`3:02.851`、`3:25.546`、`3:40.781`、`2:54.296`、`3:15.390`、`3:12.493`、`3:07.264`。
  - 探针显示每轮 `nodes` 回到约 `7837~9086`，高于当前双向 BFS 常见的 `4700~7100` 区间。
  - 取消摘要 `finished=false runs=12 average=3:05.892` 不作为刷新成绩。
  - 结论：没有刷新；East-first 下双向 BFS 仍然必要，代码已回退为双向 BFS。
- BFS 成功移动后不逐步刷新动态边
  - 2026-05-02 请求 `481`：runner 输出 `reached stable leaderboard runs 15 avg=3:46.095`。
  - 改法：在 `move_with_bfs()` 中保留 `can_move(direction)` 阻塞检查；遇到阻塞仍调用 `refresh_current_edges(graph)`，但成功 `move(direction)` 后不再逐步刷新当前格边。
  - 有效轮为 `3:29.648`、`3:51.484`、`3:29.099`、`3:55.934`、`3:38.828`、`3:42.652`、`3:52.499`、`3:38.281`、`4:18.281`、`3:42.851`、`3:35.781`、`4:03.984`、`3:52.460`、`3:41.484`、`3:38.164`。
  - 探针显示每轮 `nodes` 约 `8135~9922`，高于当前逐步刷新双向 BFS 常见的 `4700~7100` 区间。
  - 结论：成功移动后的逐步 `refresh_current_edges(graph)` 能吃到动态开放边，是必要优化；候选已回退。
- BFS 路径长度与失败来源 probe：
  - 2026-05-02 请求 `553`：probe 完整结束 `finished=true runs=39 average=3:08.111`；probe 只追加每轮诊断字段，成绩不作为刷新候选。
  - 可见 38 轮带 probe 字段的汇总：每轮固定 `301` 次 BFS，平均 `nodes≈6002`，平均路径步数 `≈2704`，单次最大路径 `50`。
  - `no_path=0`、`blocked=0`，说明当前稳定路线里双向 BFS 都能找到路径，执行路径时也没有动态边阻塞失败。
  - 结论：长尾不是动态边失败或无路重试，而是 Treasure 重定位后的真实路径长度与 BFS 节点数波动；下一步不要优先做失败兜底，应看是否能减少 BFS 调用次数或用安全局部路径缓存降低节点扫描。
- `(start, target)` 完整 pair 重复率 probe：
  - 2026-05-02 请求 `554`：probe 完整结束 `finished=true runs=39 average=3:05.448`；probe 只追加每轮诊断字段，成绩不作为刷新候选。
  - 可见 38 轮带 probe 字段的汇总：总 `bfs=11437`，`pair_unique=11058`，`pair_repeat=379`，重复率约 `3.31%`；平均每轮 `pair_unique=291.00`、`pair_repeat=9.97`。
  - 单轮 `pair_repeat` 只在 `4~17` 之间，大多数 `(当前位置, Treasure目标)` 都是首次出现。
  - 结论：不要继续写完整 `(start, target)` 路径缓存或 next-hop 缓存；命中率过低，缓存维护成本大概率吃不回。后续若做缓存，应优先考虑按目标格或局部距离层的轻量结构，而不是完整 pair 缓存。
- Treasure 目标格重复率 probe：
  - 2026-05-02 请求 `555`：probe 完整结束 `finished=true runs=40 average=3:03.241`；probe 只追加每轮诊断字段，成绩不作为刷新候选。
  - 可见 38 轮带 probe 字段的汇总：总 `bfs=11438`，`target_unique=2416`，`target_repeat=9022`，目标格重复率约 `78.88%`；平均每轮 `target_unique=63.58`、`target_repeat=237.42`。
  - 单轮基本会覆盖 `62~64` 个目标格，随后大量重复目标。
  - 结论：完整 pair 缓存不值得，但“按目标格懒缓存 BFS 树”有命中基础；下一步应只测懒 target-cache，并保留失败后回退的边界。
- 按 Treasure 目标懒缓存 BFS 树：
  - 2026-05-02 请求 `556`：候选完整结束 `finished=true runs=32 average=3:46.522`，明显慢于当前可靠 `2:46.640`。
  - 改法：首次遇到某个目标格时从目标反向 BFS 一次，缓存每个 source 到该 target 的下一步方向；后续同目标直接按缓存方向移动，路径缺失或阻塞时 fallback 到原双向 BFS。
  - 可见 32 轮 cache 指标汇总：`bfs=0`、`nodes=0`、`cache_hits=7595`、`cache_misses=2037`、`cache_invalid=0`、`cache_nodes=130368`；平均每轮 `cache_hits=237.34`、`cache_misses=63.66`、`cache_nodes=4074.0`。
  - 结论：命中率足够，问题不是缓存未命中，而是缓存树固定在较早图状态，无法吃到后续动态开墙带来的短路收益，实际移动路径显著变长；实现已回退。
- target-cache 周期重建离线筛选
  - 2026-06-10 `.codex/tests/maze_single_target_cache_rebuild_screen.py` 用 `8x8` 随机 DFS 迷宫树和低概率动态开墙模型，比较 fresh BFS 与“按目标格缓存 BFS 树并按使用次数 / 年龄重建”的策略；模型成本为 `route_steps * 1.0 + bfs_nodes * 0.08`。
  - 命令：`timeout 60s python3 .codex/tests/maze_single_target_cache_rebuild_screen.py`，约 `16.5s` 完成。模型偏向缓存：没有脚本字典开销，也不模拟真实路径执行中的额外分支。
  - 结果：所有缓存重建策略都慢于 fresh BFS。`never_rebuild cost_ratio=1.204 route_ratio=1.408`，复现旧图 stale path；`uses_1 cost_ratio=1.322 bfs_ratio=2.414`，重建过密；相对最好的 `uses_2 cost_ratio=1.139` 仍显著慢于 fresh BFS；`age_32 cost_ratio=1.166` 也不过线。
  - 结论：不改 `lb_maze_single.py`，不进入实机。target-cache 的两难很明确：不重建会走旧图长路，频繁重建又比双向 fresh BFS 节点成本更高。后续不要再做按目标格缓存路径树；若继续缓存，只能缓存极轻量统计或 tie-break 启发，不能直接复用旧路径。
- 路径执行前 `can_move()` 削减候选
  - 2026-06-10 代码候选：`move_with_bfs()` 的路径来自 `graph` 中已经确认可走的边；反编译 `Treasure.CompleteRepositioning()` 只会随机打开墙，不会关闭旧通路。request `553` probe 也已确认当前稳定路线 `no_path=0` / `blocked=0`。
  - 改法：保留成功 `move()` 后的逐步 `refresh_current_edges(graph)`，继续吃后续动态开墙收益；只删除执行 BFS 路径前每一步额外的 `can_move(direction)` 防守检查。
  - 验证：`python3 -m py_compile references/leaderboard_scripts/lb_maze_single.py` 通过。真实游戏当前仍为 `game_tick=0`，暂未能跑完成轮；文件头成绩不更新。
  - 风险：如果未来游戏机制改为会关闭旧墙，这个优化会失去防守；当前反编译和 request `553` 都支持旧边不会失效。游戏恢复后优先短跑确认。
- BFS / 探图诊断计数删除候选：
  - 2026-06-10 代码候选：删除 `explore_steps`、`bfs_count`、`bfs_nodes` 以及对应输出字段，只保留 `explore_time` / `total_time` 阶段时间。
  - 这不同于 request `450` 的“只删除 quick_print”：本候选移除的是 DFS 每步计数和 BFS 每次扩展节点计数，路径、双向 BFS、逐步 `refresh_current_edges(graph)`、East-first 顺序和目标处理都不改变。
  - 验证：`python3 -m py_compile references/leaderboard_scripts/lb_maze_single.py` 通过；`rg` 确认脚本内无 `explore_steps / bfs_count / bfs_nodes / steps= / bfs= / nodes=` 残留。真实游戏当前仍为 `game_tick=0`，暂未能跑完成轮；文件头成绩不更新。
  - 风险：删除后不能直接观察每轮 BFS 次数和节点扩展数；如果实机退化或需要继续分析 target-cache / BFS 长尾，需要临时恢复诊断计数。

## 下一步优化方向

- 围绕当前 `dfs_bfs` 继续降低实际移动和重定位等待成本，而不是退回 A* 或 2x2 基线
- 必须补证据的关键点：
  - Treasure 延迟换位对单榜时序的影响
  - `8x8` 下 301 次重定位的平均移动距离
  - 墙消失后是否能用低成本局部刷新吃到直线路径收益，而不引入贪心绕路
  - 是否存在比每次 BFS 更低成本、但不需要完整 next-hop 查表的轻量路径缓存
- 已验证静态方向 tie-break 有明显影响：`East, North, West, South` 连续两次短窗快于旧方向顺序，后续方向类候选应以 East-first 为基线。
- 已验证删除内部诊断 `quick_print` 没有刷新，默认保留 `explore_time` 与 `total_time / bfs / nodes` 输出。
- 已验证 East-first 单源 BFS 没有刷新，默认保留双向 BFS。
- 已验证 BFS 成功移动后不能删除逐步 `refresh_current_edges(graph)`；逐步刷新会显著降低后续 BFS 节点数。
- 已验证只删除开局中心移动明显退化，默认保留中心开局。
- 已通过 request `553` probe 确认 `no_path=0` / `blocked=0`，后续不优先优化 BFS 失败兜底。
- 已通过 request `554` probe 确认 `(start, target)` 重复率约 `3.31%`，后续不优先做完整 pair 路径缓存。
- 已通过 request `555` probe 确认目标格重复率约 `78.88%`，可以验证“按 target 懒缓存 BFS 树”，但仍需真实成绩判断是否被缓存构建和旧路径长尾抵消。
- 已通过 request `556` 验证懒 target-cache 退化到 `3:46.522`，后续不要保留旧图状态的 target-cache；如果还要碰缓存，只能是会随动态图刷新或只缓存距离启发，不直接复用旧路径。
- `.codex/tests/maze_single_target_cache_rebuild_screen.py` 证明按使用次数 / 年龄重建 target-cache 也不过线；不再重开按目标格缓存路径树方向。
- 2026-06-10 已把路径执行前的重复 `can_move()` 检查删掉，但保留每步 `refresh_current_edges(graph)`；确认前不更新成绩注释。

## 候选策略方向（猜测 / 待验证）

### 方向 1：直接转 `8x8` 一次到位路线

- 核心思路：不再把 2x2 / 4x4 当最终形态，而是直接围绕 `8x8` 一次做满来设计
- 主瓶颈：`8x8` 迷宫的路径复杂度明显高于 2x2
- 可能更强的原因：从收益公式看，`8x8` 才是和目标值完全对齐的一次到位规模
- 优先探针：
  - `8x8` 单轮完整做满的真实时间
  - `8x8` 下平均寻宝步数

### 方向 2：先修复延迟换位时序，再看 4x4 是否还能当过渡基线

- 核心思路：把当前版本下 Treasure 延迟换位的问题先处理对，再重新测 4x4 是否还有价值
- 主瓶颈：如果时序判断本身错了，比较尺寸没有意义
- 可能更强的原因：修好时序后，4x4 也许还能作为比 2x2 更强的过渡基线
- 优先探针：
  - 延迟换位修复前后的 4x4 时间差
  - 修复后 4x4 与 8x8 的差距

### 方向 3：单机探图 + A* 路径规划

- 核心思路：接受“要真正走迷宫”这件事，把信息收集和路径规划做对
- 主瓶颈：大图一次到位路线的最大难点就是寻宝路径本身
- 可能更强的原因：如果路径规划足够强，大图一次到位的理论收益才有机会落地
- 优先探针：
  - 已探明区域对后续寻宝的加速效果
  - A* 路径在真实迷宫里相对简单墙跟随的收益
