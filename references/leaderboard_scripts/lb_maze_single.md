# lb_maze_single

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

- 当前默认入口：文件顶层 DFS 全探图 + 单源 BFS 寻宝
- 当前路线：8x8 单机一次 DFS 建完整迷宫图；每次 `measure()` 后用单源 BFS 走到 Treasure，再用 `Weird_Substance` 重定位，直到收获达标
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

- “DFS 全探图 + 单源 BFS”已经是当前默认实现，不再作为待实现 P0。
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
