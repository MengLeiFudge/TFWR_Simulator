# lb_cactus_single

## 榜单目标

- 目标资源：`Items.Cactus`
- 单机路线
- 当前脚本目标数量为 `131072`
- 你补充的当前关键事实：
  - `8 * 8 = 64`
  - 满 `8x8` 仙人掌盘收割一次的收益是 `64 * 64 * 32 = 131072`
- 这意味着单机榜单目标值正好等于“满 `8x8` 合法盘面收割一次”

## 结算机制说明

- 单机 cactus 的计算逻辑和多机完全一样，仍然来自反编译源码里的：
  - `Cactus#Harvest()`
  - `Cactus#CountSorted(...)`
  - `Cactus#GetDrops(...)`
  - `Growable#YieldFactor`
- 关键点不是“连成一簇”本身，而是“连成一整块成熟且 `IsSorted()` 的合法盘面”。
- `CountSorted(...)` 只统计那些：
  - 已成熟
  - 自己满足 `IsSorted()`
  - 与当前起点 cactus 连通
  的仙人掌。
- 所以“只追求同簇”是错误说法；正确目标是“做出合法有序连通块”。
- `GetDrops(...)` 在 `numWeird = 0` 时可化简成：
  - `掉落 = 连通块大小 * 连通块大小 * YieldFactor`
- 当前 cactus leaderboard 下 `YieldFactor = 32`
- 因此只要做出大小为 `64` 的合法有序连通块，收益就是：
  - `64 * 64 * 32 = 131072`
- 这也解释了为什么单机榜单不是多轮滚动问题，而是：
  - 一次做出满 `8x8` 合法盘面
  - 然后收这一轮就结束

## 当前基线

- 当前默认入口：`main2()`
- 当前路线：8x8 世界，随机种植后做行排序和列排序，形成合法有序满盘后统一收割
- 当前目标不需要多轮滚动；只要完成一次满 `8x8` 合法收割就直接达标
- 2026-04-24 真实验证：`main2` 行列排序路线 324 轮均值 `0:22.195`
- 2026-04-30 真实请求 `396`：种植阶段加入四邻一步局部排序后，完整统计 `finished=true runs=332 average=0:21.696`，刷新当前基线。
- 2026-05-02 当前默认入口短窗复测：请求 `409` 在 71 轮时达到 runner 稳定停表，均值 `0:21.667`，小幅刷新短窗本地最好；该请求不是完整官方统计，`finished=false` 取消摘要不作为完整统计结果。
- 2026-05-02 收窄局部排序邻居检查：请求 `415` 在 148 轮时达到 runner 稳定停表，均值 `0:21.514`，刷新短窗本地最好。
- 2026-05-02 West 交换后复用测量值：请求 `433` 完整结束 `finished=true runs=336 average=0:21.494`，刷新当前本地最好。
- 2026-05-02 局部排序位置由外层传入：请求 `438` 完整结束 `finished=true runs=338 average=0:21.325`，刷新当前本地最好。
- 2026-05-30 当前版本复跑：请求 `605` 有效 `108` 轮稳定均值 `0:21.534`；后续 `finished=false` 取消摘要不作为成绩。

## 通用注意事项下的榜单特化

- 单机 cactus 更像“先把整盘状态做对，再一次性兑现收益”的榜单
- 这里不该套 companion 榜单的思路，核心是减少形成大簇前的无效动作
- 这里的“大簇”必须理解成“成熟且 `IsSorted()` 的合法有序连通块”，不是单纯同簇即可
- 在你给出的公式下，`8x8` 不是“也许最优”，而是当前目标值反推出来的正确盘面规模
- 因此单机 cactus 当前也是一次性构盘问题，而不是多轮轮转问题

## 当前版本结论

- `main1`
  - 8x8 全图统一 `variant=9` 后收一次
  - 已被 `main2` 的合法有序盘面路线替代，`main1` 实现已从 `.py` 删除
- `main2`
  - 当前推荐入口
  - 不再强刷固定数字，而是用随机种植 + 行列排序满足 `IsSorted()` 条件
  - 2026-04-30 起保留种植阶段局部排序：每格种完后只检查四邻相邻逆序，后续仍用原行列排序兜底
  - 真实验证请求 `396` 完整统计 332 轮均值 `0:21.696`
  - 2026-05-02 请求 `409` 短窗稳定均值 `0:21.667`
  - 2026-05-02 请求 `415` 把局部排序收窄到 West / South 已种邻居后，短窗稳定均值 `0:21.514`
  - 2026-05-02 请求 `433` 在 West 交换后直接复用已读 `neighbor`，完整统计均值 `0:21.494`
  - 2026-05-02 请求 `438` 把局部排序位置由外层扫描传入后，完整统计均值 `0:21.325`
  - 2026-05-30 当前版本复跑请求 `605` 稳定均值 `0:21.534`

## 失败对照

- 当前仓库没有留下明确的单机失败路线
- 全图强刷 `variant=9`
  - 这条路线不再作为默认入口
  - 原因是合法有序盘面不要求所有格子都是同一个固定数字，强刷 `9` 会浪费大量 reroll
  - 实现已从 `.py` 删除，仅保留结论
- 列排序阶段用顺序 `move(East)` 换列，避免每列 `goto(x, 0)`
  - 2026-04-25 真实验证：323 轮均值 `0:22.250`
  - 慢于当前基线 `0:22.195`
  - 结论：`sort_one_way("y")` 内部仍要回到列起点，外层少写 `goto()` 没有净收益，不保留实现
- 但任何“小图多轮滚动”的理解现在都应视为错误口径，因为目标值本身就是一次满 `8x8` 收割

## 成功对照

- 种植阶段顺手做四邻一步局部排序
  - 2026-04-30 请求 `396` 验证。
  - 改法：`plant_and_sort_rows()` 每格种完后调用 `local_sort_after_plant()`；只比较当前格与 West / East / South / North 的相邻逆序，不做全局重排，也不删除后续行列排序。
  - 结果：完整统计 `finished=true runs=332 average=0:21.696`，优于旧基线 `0:22.195`。
  - 结论：该候选保留为当前默认实现；收益来自种植阶段消掉一部分明显逆序，且额外 `measure()` / `swap()` 成本低于后续排序节省。
- 当前默认入口短窗复测
  - 2026-05-02 请求 `409`：runner 在 71 轮时输出 `reached stable leaderboard runs 71 avg=0:21.667`。
  - 输出尾部仍继续产生完成轮并最终因外部停表显示 `finished=false runs=159 average=0:21.463`；该取消摘要不作为完整官方统计结果。
  - 结论：当前默认实现没有改代码也能小幅刷新短窗本地最好，当时 `lb_start.py` 时间同步更新为 `0:21.667`。
- 种植阶段只检查已种邻居
  - 2026-05-02 请求 `415`：runner 在 148 轮时输出 `reached stable leaderboard runs 148 avg=0:21.514`。
  - 改法：`local_sort_after_plant()` 只保留 West 与 South 检查，删除 East 与 North 检查；后续行排序、列排序和统一收割不变。
  - 结论：East / North 在当前逐行种植阶段大多是尚未种植方向，额外 `measure()` 成本高于收益；该候选保留为当前默认实现，当时 `lb_start.py` 时间同步更新为 `0:21.514`。
- 局部排序改成 South 后 West
  - 2026-05-02 请求 `416`：完整结束 `finished=true runs=123 average=0:58.612`。
  - 改法：只调整 `local_sort_after_plant()` 的已种邻居检查顺序，先 South 后 West，其他逻辑不变。
  - 结论：明显失败；South 先交换会破坏当前行扫描下的局部行关系，导致很多轮拖到 `50s+`。代码已回退为 West 后 South。
- 局部排序只保留 West
  - 2026-05-02 请求 `417`：完整结束 `finished=true runs=334 average=0:21.602`。
  - 改法：`local_sort_after_plant()` 只保留 West 检查，删除 South / East / North。
  - 结论：比旧四邻局部排序的完整统计 `0:21.696` 快，但慢于 West + South 的短窗稳定 `0:21.514`；South 检查仍能降低后续列排序成本。代码已回退为 West 后 South。
- 跳过每行完整横向排序
  - 2026-05-02 请求 `418`：完整结束 `finished=true runs=126 average=0:57.399`。
  - 改法：保留种植阶段 West + South 局部排序，但删除每行结束后的 `sort_one_way("x")`，后续列排序和统一收割不变。
  - 结论：明显失败；局部排序不足以替代行内完整排序，行顺序不稳定会拖成多余处理。代码已回退为每行保留 `sort_one_way("x")`。
- 移除 `main2` 完成日志
  - 2026-05-02 请求 `420`：runner 在 214 轮时输出 `reached stable leaderboard runs 214 avg=0:21.560`；取消摘要 `finished=false runs=304 average=0:21.470` 不作为刷新依据。
  - 2026-05-02 追加请求 `421`：完整结束 `finished=true runs=334 average=0:21.571`。
  - 改法：删除 `main2()` 末尾 `quick_print("main2 done cactus=", ...)`，只保留 leaderboard 自带 `[lb_cactus_single] run=` 输出。
  - 结论：没有刷新 `0:21.514`，说明 done 日志不是当前主瓶颈；代码已恢复完成日志，便于短窗输出继续保留每轮脚本内时间。
- West 交换后复用测量值
  - 2026-05-02 请求 `433`：完整结束 `finished=true runs=336 average=0:21.494`。
  - 改法：`local_sort_after_plant()` 中 West 方向 `swap(West)` 后直接 `current = neighbor`，省掉一次 `measure()`；West / South 检查顺序、行排序、列排序和统一 `harvest()` 不变。
  - 结论：等价减少测量成本形成小幅收益；保留为当前默认实现，`lb_start.py` 同步更新。
- 局部排序位置由外层传入
  - 2026-05-02 请求 `438`：完整结束 `finished=true runs=338 average=0:21.325`。
  - 改法：`plant_and_sort_rows()` 内层改为 `for x in range(size)`，调用 `local_sort_after_plant(x, y)`，删除函数内 `get_pos_x()` / `get_pos_y()`；保留 `size = get_world_size()`，避免混入 no-size 失败变量。
  - 结论：减少每格两次位置读取后刷新当前本地最好；该候选保留为默认实现，`lb_start.py` 同步更新。
- 种植阶段直接 `plant(Entities.Cactus)`
  - 2026-05-02 请求 `435`：runner 输出 `reached stable leaderboard runs 134 avg=0:21.571`，尾部状态摘要为 `finished=false runs=197 average=0:21.582`，不作为刷新。
  - 改法：在 `plant_and_sort_rows()` 中删除 `get_entity_type()` 检查，每格直接 `plant(Entities.Cactus)`。
  - 结论：没有刷新 `0:21.494`；直接 `plant` 不能替代实体检查，代码已回退。
- 种植阶段直接 `till()`
  - 2026-05-02 请求 `436`：完整结束 `finished=true runs=335 average=0:21.516`。
  - 改法：在 `plant_and_sort_rows()` 中删除 `get_ground_type()` 检查，每格直接 `till()`。
  - 结论：没有刷新 `0:21.494`；直接 `till` 不能替代地面检查，代码已回退。
- 删除局部排序开头未使用的 `get_world_size()`
  - 2026-05-02 请求 `437`：完整结束 `finished=true runs=334 average=0:21.576`。
  - 改法：删除 `local_sort_after_plant()` 开头的 `size = get_world_size()`，其他 West / South 检查和测量复用不变。
  - 结论：没有刷新 `0:21.494`；这个调用虽然未直接使用，但删除后真实均值变慢，代码已回退。
- pass-position 基础上再次删除未使用的 `get_world_size()`
  - 2026-05-02 请求 `439`：runner 在 123 轮时输出 `reached stable leaderboard runs 123 avg=0:21.433`；尾部取消摘要 `finished=false runs=212 average=0:21.467` 不作为完整统计。
  - 改法：在请求 `438` 的外层传入 `x, y` 基础上，再删除 `local_sort_after_plant(x, y)` 开头的 `size = get_world_size()`。
  - 结论：没有刷新 `0:21.325`；即使该调用未直接使用，真实短窗仍变慢，代码已回退。
- pass-position 基础上直接 `plant(Entities.Cactus)`
  - 2026-05-02 请求 `440`：完整结束 `finished=true runs=337 average=0:21.385`。
  - 改法：在请求 `438` 的外层传入 `x, y` 基础上，删除 `get_entity_type()` 检查，每格直接 `plant(Entities.Cactus)`。
  - 结论：没有刷新 `0:21.325`；实体检查仍能避免无效种植成本，代码已回退。
- pass-position 基础上直接 `till()`
  - 2026-05-02 请求 `441`：完整结束 `finished=true runs=337 average=0:21.398`。
  - 改法：在请求 `438` 的外层传入 `x, y` 基础上，删除 `get_ground_type()` 检查，每格直接 `till()`。
  - 结论：没有刷新 `0:21.325`；地面检查仍能避免无效翻地成本，代码已回退。
- 删除局部排序 `current == None` 早退
  - 2026-05-02 请求 `442`：runner 在 121 轮时输出 `reached stable leaderboard runs 121 avg=0:21.381`；尾部取消摘要 `finished=false runs=205 average=0:21.222` 不作为完整统计。
  - 2026-05-02 请求 `443`：为排除取消摘要误判，追加完整统计，结果 `finished=true runs=334 average=0:21.577`。
  - 改法：删除 `local_sort_after_plant(x, y)` 中 `if current == None: return`。
  - 结论：没有刷新 `0:21.325`；虽然种植后理论上应可测量，保留早退分支的真实表现更好，代码已回退。
- 内联 `local_sort_after_plant(x, y)`
  - 2026-05-02 请求 `444`：完整结束 `finished=true runs=336 average=0:21.436`。
  - 改法：把 `local_sort_after_plant(x, y)` 的逻辑直接展开到 `plant_and_sort_rows()` 内，保持 `size = get_world_size()`、`current == None` 早退、West / South 检查和测量复用不变。
  - 结论：没有刷新 `0:21.325`；函数调用不是当前主要瓶颈，或内联后局部执行成本更高，代码已回退。
- 删除已种邻居 `None` 检查
  - 2026-05-02 请求 `445`：完整结束 `finished=true runs=336 average=0:21.493`。
  - 改法：把 West / South 的 `neighbor != None and neighbor > current` 改为 `neighbor > current`。
  - 结论：没有刷新 `0:21.325`；即使邻居理论上已种，保留 `None` 检查的真实表现更好，代码已回退。
- 反向列排序顺序
  - 2026-05-02 请求 `468`：完整结束 `finished=true runs=335 average=0:21.499`。
  - 改法：在 `sort_columns()` 中把列访问从 `0..7` 改为 `7..0`，不改变列内排序算法。
  - 结论：没有刷新 `0:21.325`；反向访问没有减少有效过渡成本，代码已回退正向列排序。
- 列排序后就地 harvest
  - 2026-05-02 请求 `483`：完整结束 `finished=true runs=338 average=0:21.338`。
  - 改法：删除 `main2()` 中 `sort_columns()` 后、`harvest()` 前的 `goto(0, 0)`，直接在列排序结束位置收割。
  - 结论：能正确结算满盘 cactus，但略慢于当时可靠基线 `0:21.325`；最后回 `(0, 0)` 不是净亏，代码已恢复 harvest 前 `goto(0, 0)`。
- 拆分横向/纵向排序函数：
  - 2026-05-02 请求 `492`：完整结束 `finished=true runs=335 average=0:21.499`。
  - 改法：把 `sort_one_way("x"/"y")` 拆成 `sort_one_way_x()` / `sort_one_way_y()`，试图减少方向分支和闭包创建。
  - 结论：没有刷新 `0:21.325`；拆分后代码更长但真实成本没有下降，已回退通用 `sort_one_way()`。
- 删除 `sort_one_way()` 尾部二元比较：
  - 2026-05-02 请求 `513`：完整结束 `finished=true runs=261 average=0:27.664`。
  - 改法：删除 `if bound_low + 1 == bound_high:` 的尾部 window2 比较，保留其余局部排序、行排序、列排序和统一收割。
  - 运行中大量轮次退化到 `0:38~0:45`，例如 `run=81 time=0:44.140`、`run=123 time=0:50.999`、`run=199 time=0:45.273`。
  - 结论：没有刷新；单机 8x8 也需要尾部二元比较清理残留逆序，代码已恢复该分支。
- 列排序前预检跳过已排序列：
  - 2026-05-02 请求 `552`：完整结束 `finished=true runs=326 average=0:22.126`。
  - 改法：在 `sort_columns()` 中每列先从 `y=0` 开始扫描相邻 `measure()` / `measure(North)`，只有发现逆序时才调用 `sort_one_way("y")`。
  - 尾部有效轮大量落在 `0:22~0:24`，整体慢于当前可靠 `0:21.325`。
  - 结论：预检扫描成本高于跳过少数已排序列的收益；默认每列直接执行完整 `sort_one_way("y")`，代码已恢复。
- 行/列排序从近端开始的筛选
  - 2026-06-10 `.codex/tests/cactus_single_sort_orientation_screen.py` 比较当前 `sort_one_way()` 固定从 `bound_low` 开始，和“按当前位置从近端开始，必要时先做 high-to-low pass”的候选。
  - `timeout 60s python3 .codex/tests/cactus_single_sort_orientation_screen.py` 快速完成，`samples=50000`、`failures=0`；代理结果：`low_first score=5668.755`、`nearer_side score=5531.450`、`score_ratio=0.9758`，只有约 `2.4%` 的单线动作代理收益。
  - 结论：不改 `lb_cactus_single.py`，不进入实机。该候选需要新增 high-first 排序分支，收益只来自小幅减少 line-sort 起点移动；而单机仙人掌已有大量微调实机反例，2.4% 的局部代理不足以覆盖分支成本和行列交互风险。
- 行列交替融合筛选
  - 2026-06-10 `.codex/tests/cactus_single_fusion_screen.py` 保留当前种植阶段 West + South 局部排序，比较当前完整行排序再完整列排序，与重复执行便宜的 row/column relax 直到盘面合法。
  - `timeout 60s python3 .codex/tests/cactus_single_fusion_screen.py` 约 `9.8s` 完成；`python3 -m py_compile .codex/tests/cactus_single_fusion_screen.py` 通过。
  - 结果：当前 `current_rows_cols score=66269.327`，`failed=0`；`relax_forward score=85622.524`、`ratio=1.2920`，`relax_cocktail score=91203.451`、`ratio=1.3763`，两者都能生成合法盘面但动作代理明显慢。
  - 结论：不改 `lb_cactus_single.py`，不进入实机。单机 `8x8` 下行列 relax 只是减少很少 swap，却增加更多移动和测量；后续不要继续做“把完整行列排序拆成多轮轻 relax”的融合变体。
- 蛇形连贯行列排序筛选
  - 2026-06-10 `.codex/tests/cactus_single_serpentine_line_order_screen.py` 检查“行 / 列按当前位置选择 low-first 或 high-first 起手，列排序阶段按当前位置贪心选择最近未排序列”的偏乐观上界，目标是量化文档里剩余的更少 `goto()` 蛇形连贯流程。
  - 命令：`python3 -m py_compile .codex/tests/cactus_single_serpentine_line_order_screen.py` 通过；`timeout 60s python3 .codex/tests/cactus_single_serpentine_line_order_screen.py` 约 `12.8s` 完成。
  - 结果：`current score=76105.222 failed=0`；`serpentine score=73476.106 failed=0`，`serpentine_score_ratio=0.9655`；high-first 被选择在 `17.676%` 行和 `48.303%` 列。该模型已经不计真实脚本里的额外分支、选择列、函数层和二维 `goto()` 细节成本。
  - 结论：不改 `lb_cactus_single.py`，不实机蛇形连贯排序。即使在偏向候选的代理里也只有约 `3.45%` 局部动作收益；考虑单机仙人掌已有大量 `1%~3%` 微调实机失败，这个 margin 不足以支撑重写排序控制流。

## 下一步优化方向

- 继续压缩 `main2` 的行列排序成本
- 尝试把行排序和列排序做成更少 `goto()` 的蛇形连贯流程
- 已验证局部排序只检查 West / South 更快；后续若继续动局部排序，应优先围绕“已种邻居”而不是四邻全查
- 已验证 West 后 South 的顺序明显优于 South 后 West，不要反过来
- 已验证 West-only 慢于 West + South，不要删除 South 检查
- 已验证跳过每行 `sort_one_way("x")` 会退化到 `0:57.399`，不要省掉行内完整排序
- 已验证移除 `main2 done` 日志没有刷新，默认保留完成日志
- 已验证 West 交换后复用已读 `neighbor` 可以把完整统计刷新到 `0:21.494`
- 已验证局部排序位置由外层传入可以把完整统计刷新到 `0:21.325`
- 已两次验证删除局部排序开头未使用的 `get_world_size()` 没有刷新，默认保留该调用
- 已两次验证直接 `plant(Entities.Cactus)` 没有刷新，默认保留实体检查
- 已两次验证直接 `till()` 没有刷新，默认保留地面检查
- 已验证删除 `current == None` 早退没有刷新，默认保留该保护分支
- 已验证内联局部排序没有刷新，默认保留 `local_sort_after_plant(x, y)` 函数
- 已验证删除已种邻居 `None` 检查没有刷新，默认保留 West / South 的 `neighbor != None`
- 已验证反向列排序顺序没有刷新，默认保留 `sort_columns()` 正向 `0..7`
- 已验证列排序后就地 harvest 没有刷新，默认保留 harvest 前 `goto(0, 0)`
- 已验证拆分横向/纵向排序函数没有刷新，默认保留通用 `sort_one_way("x"/"y")`
- 已验证删除尾部二元比较会显著退化，默认保留 `bound_low + 1 == bound_high` 分支
- 已验证列排序前预检跳过已排序列没有刷新，默认每列直接跑完整列排序
- `.codex/tests/cactus_single_sort_orientation_screen.py` 证明近端起手排序只有约 `2.4%` 单线代理收益，且需要新增排序分支；不作为当前实机候选。
- `.codex/tests/cactus_single_fusion_screen.py` 证明行列交替 relax 在单机 `8x8` 下代理成本为当前 `1.292x` 到 `1.376x`；不作为当前实机候选。
- `.codex/tests/cactus_single_serpentine_line_order_screen.py` 证明行列排序连贯化 / 近端起手 / 贪心最近列在偏乐观代理下也只有约 `3.45%` 局部收益，不作为当前实机候选。
- 优化目标应明确写成：
  - 尽快做出一次满 `8x8` 合法盘面
  - 而不是提高多轮平均产量

## 候选策略方向（猜测 / 待验证）

### 方向 1：以“尽快形成完整合法排序盘面”为目标，而不是执着某个固定数字

- 核心思路：优化目标不是“只要同簇就行”，而是“尽快让整盘变成成熟且 `IsSorted()` 的合法状态”；如果这件事不需要全盘都变成某个固定数字，就不必把某个数字当成目的本身
- 主瓶颈：当前可能把“某个固定数字”误当成了“合法收割条件”
- 可能更强的原因：如果存在比“全盘追某个固定值”更便宜的合法排序盘面，就能更快完成那一次关键收割
- 优先探针：
  - 哪些局部数字分布已经满足 `IsSorted()` 而无需继续重置
  - 比较“追固定数字”与“只追合法排序”两条路线的总处理时间

### 方向 2：种植阶段顺手做局部排序

- 核心思路：既然单机要逐格走完整个 `8x8`，就尝试在种植阶段顺手消掉一部分明显逆序
- 主瓶颈：当前成盘成本可能主要来自“种完后再单独整理”
- 可能更强的原因：单机没有多机调度包袱，边种边排也许更容易直接省下一段独立整理流程
- 优先探针：
  - 种植阶段能顺手做掉多少交换
  - 提前交换后最终成盘时间是否下降

### 方向 3：单轮内同时推进横向和纵向有序化

- 核心思路：利用 `measure(direction)` 在单轮扫描时同步收集横纵关系，而不是纯蛇扫后再补第二层整理
- 主瓶颈：横向和纵向整理如果完全拆开，会多一段显式整理成本
- 可能更强的原因：单机世界更小，双向融合的收益可能比多机更直接
- 优先探针：
  - 双向融合后总移动步数和总交换次数是否下降
  - 融合逻辑是否会因为判断过多反而拖慢成盘
