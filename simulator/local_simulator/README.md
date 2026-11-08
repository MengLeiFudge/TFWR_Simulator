# 农场 API 本地模拟

此入口执行受支持的游戏脚本，计算农田状态、资源和预计游戏时间，不需要打开游戏，只依赖 Python 3.11+ 标准库。已适配基础游戏作物、南瓜合并、恐龙和迷宫，并实现地下地形、作物、解谜与14个地下排行榜场景；基础范围见 [全作物机制](mechanisms.md)。[API覆盖记录](api-coverage.md) 保留49个公开函数的方法级对照。精度取舍遵循 [模拟精度与验收](../README.md#模拟精度与验收)，结果不能作为真实成绩或排名。

游戏版本、更新影响及基础验收边界见[更新对齐记录](game-update-26385848.md)。固定seed对应游戏simulate，正式榜单的加密随机轨迹不能由该seed重放。地下资源快照与23个历史同seed用例来自26410308；当前构建26462009已修正塌方传播的相对坐标筛选，当前Reset源码seed1完整19716.483046656秒与实机误差0ns，另有地层定位和勘探方法复核，范围见[地下对照记录](underground-validation.md)。

## 使用

在仓库根目录运行：

```bash
python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seed 1
```

保存报告和逐 API 轨迹：

```bash
python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seed 1 --output .codex/cactus-local.json --trace .codex/cactus-local.jsonl
```

`--output` / `--trace` 会覆盖指定文件，父目录须存在。命令不会访问真实存档、启动游戏或更新排行榜缓存。默认关闭逐API快照、JSON序列化和轨迹哈希；需要定位差异时再传 `--trace`。

同一脚本批量筛选多个seed：

```bash
python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seeds 0 1 123 --timeout 30 --output .codex/cactus-batch.json
```

`--seeds` 接受1～100个不重复的非负Int32，与 `--seed` 互斥。默认工作进程数取当前进程可用的逻辑CPU数与seed数的较小值，不区分大小核，不设置绑核；每个seed重建独立世界。CPU数量优先使用Python的进程可用CPU接口，旧Python读取进程亲和性；这些信息不可用时回退系统CPU数，仍无法获取则使用1。显式指定正整数 `--jobs` 可覆盖默认值，例如 `--jobs 3` 最多并行3个seed，`--jobs 1` 顺序执行并复用编译缓存。有效进程数始终不超过seed数，单个seed仍由一个进程按原有顺序调度无人机，农田状态与随机数不跨进程共享。

```bash
python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seeds 0 1 123 --jobs 3 --timeout 30 --output .codex/cactus-batch.json
```

报告为 `kind=prediction_batch`，包含 `reports` 和 `completed_seeds`；`reports` 始终按输入seed顺序排列，实时进度按各进程实际执行顺序显示。CLI在API检查点每隔至少5墙钟秒向stderr输出当前seed的虚拟游戏秒、API数和目标库存；配置目标时同时输出 `goal_net_gain`、`goal_per_game_second`，后者为净增长/实际游戏秒。每完成一个seed再报告工作进程的分组进度；stdout仍只承载JSON结果。进度不依赖脚本日志，也不增加游戏计费。若配置trace，分别写入 `名称.seed-N.扩展名`。

## 科技与初始库存

通过预设、场景JSON或只读存档快照选择科技组合。各选项都只影响本地世界，不会改写真实存档。

| 输入 | 初始配置 |
| --- | --- |
| 默认或 `--preset max` | 基础科技满级、DLC科技为0；Pumpkin和Power各1e9，其他库存0 |
| `--preset all` | 基础和DLC科技全部满级；库存默认值与max相同 |
| `--preset reset` | Grass及基础语言/调试/感知接口已开启，生产科技与库存从零开始 |
| `--save 路径/save.json` | 导入该文件的科技和库存；地形、作物、位置、无人机和计时仍按seed重新初始化 |
| `--unlock 名称=等级` | 覆盖单项科技，可重复；支持 `Mining=3`、`Unlocks.Megafarm=0`，范围按资源表检查 |

先选择预设或存档，再应用 `--scenario` 中的库存和科技，最后应用 `--unlock`。显式 `--preset` 覆盖场景中的preset；它与 `--save` 互斥。存档中的非科技解锁符号会忽略，`debug_2` 这类独立科技优先按完整名称识别。不会自动补齐被显式关闭的前置科技。

功能初版使用 `--preset all`。其余科技组合用于重置榜或明确指定的机制场景，不代表功能脚本已适配低科技。

```bash
python3 -m simulator.local_simulator scripts/functional/rice.py --preset all --timeout 30
python3 -m simulator.local_simulator scripts/leaderboard/lb_fastest_reset.py --preset reset --unlock Expand=1 --timeout 30
python3 -m simulator.local_simulator scripts/functional/bamboo.py --save gamesave/save.json --timeout 30
```

用 `--scenario scenario.json` 指定初始库存、科技及可选目标。将下列JSON保存为 `scenario.json` 后传入；省略项保留所选预设或存档的值：

```json
{"items":{"Hay":1000000,"Wood":1000000,"Carrot":1000000,"Cactus":1000000,"Water":100,"Fertilizer":100,"Weird_Substance":10000},"unlocks":{"Speed":4},"goal":{"item":"Cactus","amount":131072}}
```

预设与JSON都支持 `preset=max/all/reset`。科技决定速度、产量、成本、地图和无人机容量，具体组合的机制覆盖仍以验收记录为准；语言解锁门槛尚未全面对齐。`Expand=1` 是1×3，其余地图尺寸随等级变化。地下资源榜用 `--leaderboard` 加载原版场景，可以用 `--unlock` 或JSON覆盖单项科技，与 `--save/--preset` 互斥；正式榜仍统一移除爆破钻头。普通功能脚本持续运行，可用 `--game-seconds` 按游戏时间停止；场景物品目标只记录达标状态，不会自动停止入口。

| 报告字段 | 含义 |
| --- | --- |
| `kind: prediction` | 本地预测 |
| `initial_state` | 实际初始unlocks、items、width、size和max_drones，先于任何脚本动作采集；用于确认科技组合实际生效 |
| `model_version` / `underground_model_version` / `random_mode` | 基础/地下资源及机制快照的来源构建与Core/Utils哈希；当前代码的实机覆盖见验证记录。随机口径固定为`seeded_simulate` |
| `status` / `error` | 脚本完成或被停止，以及失败原因、行号 |
| `goal_reached` | 脚本结束时是否达到场景物品目标或解锁目标；未配置目标时为null。达到库存目标不会自动停止脚本。 |
| `leaderboard_profile` / `leaderboard_validation` | 地下榜原版场景参数与验证口径；专用地形为 `asset_and_source_only`，不能同seed重放正式加密随机盘面。 |
| `predicted_game_seconds` | 脚本操作、API及定时事件推进的共享游戏秒；旧字段 `predicted_api_seconds` 保留为同值兼容字段 |
| `efficiency.elapsed_game_seconds` | 从初始化到当前停止点实际经过的游戏秒，不使用现实计算时间 |
| `efficiency.items.名称.net_change` | 该物品最终库存减初始库存，计入产出、消耗及自动获取；负数表示净消耗 |
| `efficiency.items.名称.net_per_game_second` | 净变化除以实际游戏秒；游戏时间为0时为null。对预算停止的连续生产样本仍计算该值；批量结算须先完成完整周期才能用于效率判断 |
| `interpreter_ticks` | 已执行的脚本表达式、控制流、用户函数和容器操作成本，各无人机相加 |
| `api_calls` / `api_ticks_by_function` | 按 API 拆分的调用数与动作成本；各无人机成本相加，不等于共享时间 |
| `state` / `harvests` | 最终全实体/分组、库存和随机抽取次数；harvests记录成熟普通作物收获，恐龙/迷宫收益体现在库存 |
| `immature_harvests` / `immature_companion_harvests` | 按实体名统计未成熟harvest调用次数，以及其中收割瞬间伴生支撑类型匹配的次数；只计数，不写逐调用轨迹、不改计费或随机数。前者包含主动重抽，后者也不直接等于可挽回产量 |
| `estimated_loop_ticks` | 兼容字段，固定为0；循环成本计入 `interpreter_ticks` |
| `script_steps` / `step_basis` | 源语句和循环边界的预算检查点数；`step_basis=compiled_checkpoint`，不同于历史CPython事件计数，仅用于执行上限 |
| `wall_seconds` | 本机计算时间，不是游戏时间；不含 CLI 子进程启动 |
| `output` / `output_dropped` | 最近1000条脚本输出（每条最多4096字符）及已丢弃的早期输出条数；未丢弃时为0 |
| `state.grounds` | 最终地面矩阵，按 `[y][x]` 读取，`size`行、`width`列，值为对应的`Grounds`枚举名；`state.depths`同样按`[y][x]`记录向下为正的深度，`state.hover_heights`记录已设置的无人机悬浮高度（未设置为1）；只读序列化，不推进模拟时间。旧报告缺少此字段时表示未观测，不从till次数反推。 |

JSONL 每行记录调用序号、无人机、API、参数、返回值、调用时刻的坐标/库存/当前格状态，以及预计可再次运行的 `ready_ns`。与单机按调用完成后记录的旧轨迹不同，它保留并发调用的时间顺序。报告附脚本哈希、seed和十流派生seed；`module_dependencies`记录实际加载模块的路径与源码SHA256，没有导入时为空。只有开启trace才计算轨迹哈希，否则 `trace_sha256=null`。`warnings` 记录模拟内部启动入口被拒绝等情况。

## 地下排行榜模拟

将 `strategy.py` 替换为要执行的游戏脚本：

```bash
python3 -m simulator.local_simulator strategy.py --leaderboard mushrooms_single --seed 1 --timeout 30 --output result.json
```

支持 Bamboo、Dynamite、Mushrooms、Ores、Pyramids、Rice 的单双机榜，以及 Treasure_Map 和 Fastest_Underground_Reset，共14榜。场景也可写 `{"leaderboard":"Mushrooms_Single"}`，并用 `items/unlocks/goal` 覆盖初始条件。正式榜单场景初始化时统一移除 `Explosive_Drill` 科技，显式科技覆盖也不能保留它；这对齐游戏 `Core.StartLeaderboard` 对非 `simulation` 的过滤。普通场景不应用该规则，已解锁时仍可使用钻头。默认库存、目标、地层规则和实测边界见[地下模拟与同种子对照](underground-validation.md)。本地命令只执行传入脚本，不生成策略、不提交成绩。

## 机制与执行边界

基础作物参数来自已核对的原版资源快照，科技成本复用 `references/unlocks/unlock_snapshot.json`。全部作物、伴生、水肥/感染、南瓜合并、向日葵倍率、恐龙、迷宫和地图升级的实现与实机范围统一见 [全作物机制](mechanisms.md)。

脚本调用和计费操作转为协程，执行器按原版最多199t的批次推进，在共同操作时刻按无人机编号应用副作用。批次内只推进时钟，新建定时事件留到批次结束后处理；协程耗尽后保留下一轮才提交Terminated的阶段。每台无人机有独立位置、随机流和复制后的全局/闭包作用域，棋盘与资源共享；`wait_for`只阻塞调用者，返回值再次复制。清场取消其他无人机；等待已取消句柄会停止并报告原因，避免无界等待。

成功的普通移动/交换/种植/收获、翻地、清场和缩图计200t；失败动作和普通查询计1t。恐龙移动由400t起随吃苹果递减。时间查询与quick_print为0t；print、翻转和摸猪约1游戏秒。赋值和变量读取不计费，算术、比较、容器和函数调用按操作成本计费；for/while在首次进入时计1t，循环体单独计费。用户函数的默认参数在调用时求值。直接静态绑定的函数调用免费；别名、重新赋值及条件定义的函数调用计1t。

游戏的 `global` 跳过当前函数，在最近的父作用域查找已有绑定；外层函数没有该名称时才落到模块。本地编译器据此转换闭包写入，并保持函数调用静态标记与同一无人机内共享闭包绑定一致。依据为当前Core源码 `Parser.Statement`、`Scope.SetVar/Evaluate`；此边界在2026-10-24因单机迷宫 `bfs_stamp` 被Python模块global误解析而修正，实机同seed对照尚待补充。

字符串字面量按原版直接保留引号中内容，不采用Python转义。字符串键按`max(1, UTF16长度 // 8)`计费，`str`本身1t，包含判断按全串长度计费；索引、切片、迭代和解包按UTF-16单元。普通值的点运算支持函数绑参。支持同目录显式`import helper` / `from helper import f`，首次导入执行模块初始化，后续导入保留导出静态标记；无人机复制相关作用域，新无人机首次导入仍执行初始化。旧版139条专项实机观测已逐项对齐，具体写法与限制见[解释器计费指南](../../docs/leaderboards/interpreter_cost_notes.md)。

入口及实际导入模块先按原版Tokenizer/Parser检查源语法，再交给本地执行后端。三元条件表达式、推导式、lambda、参数解包等不属于游戏语言的写法在编译阶段拒绝；普通默认参数、分支和切片保留。解析后继续检查赋值目标、global声明顺序及三类无意义表达式规则。失败带原版错误码、文件和行列；语言子集、合法写法及覆盖边界见[游戏语言静态检查](syntax-validation.md)。

尚未全面对齐非整数range、所有类型/解锁门槛、完整浮点字符串格式化、地区相关字符串排序和完整游戏语言运行语义。原版允许但本地未覆盖的通配导入（builtins类型提示导入除外）、模块属性赋值、返回类型注解等明确报UnsupportedMechanism；多名称global等原版语法错误报GameSyntaxError，不混作模型覆盖问题。非法参数会停止，不返回固定成功值。`simulate` / `leaderboard_run`只复现模拟内部禁止递归启动的行为；外部游戏启动使用真实协调器。

成熟使用纳秒定时事件，作物随机倍率保留Single精度；水分每0.1秒逐格抽取，包括干地，Power每0.2秒结算执行批次累计的消耗。实体外观和感染切换也消耗共享various随机流。同刻事件保留原版四叉堆顺序。旧版长场景达到单seed时间门槛；基础构建26385848曾完成16榜同seed策略对照。该阶段修正施肥结算、批次事件顺序、枚举键收费及子机终态后，Reset、南瓜多机和向日葵单双机完整时间均与原生返回值相同到整数纳秒；其余12榜当时本地结果不变，只核对到原生0.01秒显示精度。历史证据见[四榜修复](four-residual-alignment.md)和[验收记录](validation.md)，不替代后续构建及代码的重新验证。

Power账不能直接用`(sum(api_ticks_by_function)+interpreter_ticks)/6000`代替。Core在`wait_for`等待的子机结束时把调用者OpCount补到GlobalOpCount，但不同时更新LastConsumedOpCount；后续ConsumeOps将这段补齐计入UsedPower。本地Scheduler.finish/run遵循同一源码路径，而API/解释器字段不包含这段等待补齐。print、翻转、摸猪、挖掘的免耗电动作，以及0.2秒结算时尚未扣款的消耗，也须另计；有产电或耗尽时还需分别核算收入与库存截断。现有报告未单列等待补齐及待结算总量，缺少这些量时不能仅凭上述工作量与库存差认定计费错误。此为源码语义核对，任意并发等待组合仍未全面通过实机验证。

集合字面量和`set()`按游戏HashSet槽位顺序枚举，删除槽位在后续添加时优先复用；无人机复制按当前活跃元素重新构造集合。`get_cost()`字典按物品priority对应的ID顺序插入。游戏常量作为键时大小为1，不按本地StrEnum的显示字符串长度收费。集合顺序会改变等距离选点，成本键顺序会改变资源检查的短路路径，均可能使同seed轨迹分歧；不能用CPython集合或JSON字母排序替代。函数返回表达式也保留静态标记，工厂返回静态名称后立即调用不多收动态分派tick；普通赋值仍使该名称变为动态。当前实机覆盖与残余限制见验收记录。

游戏没有int()/float()，运行器也不提供。输出与运行资源有限制；脚本仅适用于已记录的机制组合。

## 执行上限

连续生产可先用 `--timeout 30` 给有限现实计算预算。正常触及墙钟、API或检查点预算时，报告仍包含 `efficiency`；比如推进100游戏秒、净增1e8，增长率就是1e6/游戏秒。它是该观测段的实际增长率，不是600秒或未来产量的预测。无需为凑固定游戏时长延长预算。恐龙等批量结算须用有限入口完成至少一个完整生产周期，再按结算净收益/周期总游戏秒评价；未完成时0库存不能说明周期效率为0。

可选 `--game-seconds 600` 为每个seed设置600游戏秒上限，必须是有限正数。窗口从0秒起计，包含脚本初始化与全部动作；在检查点发现共享游戏时间已到时停止，报告 `status=stopped` 和 `BudgetExceeded: 达到游戏时间窗口 600s`。动作或事件可能跨过边界，实际值以 `predicted_game_seconds` 为准。它不放宽其他预算；先触及现实预算时照常报告已观测增长率，不能把实际短段产量填写成已完成600秒。详细口径见[脚本验证](../../docs/script-validation.md)。

默认每个seed限制 100000 次 API 调用、2000000 个编译检查点，可用 `--max-api-calls`、`--max-steps` 修改。检查点位于源语句和循环边界，纯计算循环及递归也受限；不再开启 `sys.settrace`。`_budget`等内部执行函数及`_timing_`前缀属于运行器保留名称。检查本身不增加虚拟游戏时间。`--timeout` 默认10秒、最多75秒，包含所有子进程启动；串行和并行批次中的所有seed共享这一墙钟截止时间。CLI在该预算内预留10%、最多1秒用于生成和回传停止报告，执行预算因此略短；正常触及预算时返回已有状态、效率、阶段输出和调用统计。超出报告余量或卡在不可中断操作时，父进程终止并回收全部工作进程，保留超时摘要、已回传seed报告和轨迹；没有世界快照的超时摘要不能计算效率。CLI停止仍返回非零退出码，调用者应区分正常预算停止和脚本/机制错误。回收进程另有有限等待，不计入游戏预测时间。

并行影响本机计算时间、CPU和内存占用，不改变完整执行的单seed模拟结果。受墙钟限制而中途停止时，已完成seed数与停止位置可能不同；比较模拟一致性应让脚本正常结束，或使用相同API/检查点上限。

输出超出保留容量时只丢弃最早的日志，不停止脚本。`quick_print()`仍计0t，`print()`仍按原版计费；无限输出循环由API、检查点和墙钟预算终止。

脚本执行器只用于已审阅的本地策略，不是运行不可信代码的安全沙箱。直接调用 Python `run_script()` 没有 CLI 的进程级兜底，日常筛选使用上述命令。库调用默认不输出进度，需要时传入 `progress=True`。

## 模拟开销

本地执行只推进虚拟游戏时间，没有UI帧率或时间倍率。默认关闭API轨迹；调度只扫描活动无人机，已结束任务的返回值由脚本句柄保留。恐龙尾巴使用deque，已销毁迷宫移出调度列表，批量seed复用编译结果。

生长进度按当前定时区间延迟读取；水分、邻树或肥料改变生长条件时才重新排定成熟事件。未成熟植株施肥按当前源码结算两次旧区间，起点仅在重排时更新。取消的事件在到达堆顶时移除，保留同刻事件顺序。南瓜成熟或移除只更新受影响的正方形索引，合并候选按原规则选择。

向日葵按7～15瓣维护数量，收获倍率最多检查9种花瓣数，包含未成熟植株。仙人掌连锁收获只在本次遍历内缓存排序检查。苹果/恐龙数量随实体增删更新，用于空格数和骨头结算；生成苹果目标时按原版DFS顺序构造候选列表。

脚本循环、API上限和进程墙钟限制保留。批量seed可通过 `--jobs` 分进程执行，每个工作进程内复用编译缓存；短任务可能因进程启动成本而无明显收益。逐格随机衰减的成本随地图面积和游戏时长增长，不能省略干地抽取以加速，否则会改变后续随机轨迹。验证状态与历史结果见 [模拟与实机验收](validation.md)。

## 方法级验证

旧版计时与事件改造后通过49个公开函数及662条离散观测，另完成单seed长程对照；新版验收边界见[当前验收](validation.md)。以下保留改造前的历史基线。2026-10-23实机请求43～47：49个公开函数和作物/交互/地图/优化专项共662条离散观测一致，20项本地错误与限额检查通过。批量CLI与逐次执行结果一致；双日志无新增错误，存档入口已恢复。自然成熟采样最大差约2.008秒，水量与Power近似单独记录，完整结果见 [本次验收](validation.md)。

性能优化前的请求38/39/41/42累计635条离散观测一致；当时20项本地错误/限额检查通过。自然成熟和Power误差单独记录，完整证据见 [全作物机制](mechanisms.md) 与 [API覆盖记录](api-coverage.md)。这些是历史机制验证，不能当作当前优化版本重新通过实机对照的证明。

## 初始仙人掌版本的历史基线

请求 35，在真实游戏内分别运行未插桩策略函数、记录 API 返回值的版本和边界探针。显式传入满级科技、相同资源与 seed，避免 `simulate(Unlocks)` 捕获主农场的当前升级级别。

| seed | 一致的 API 返回值数 | 本地 API 秒 | 实机 tick 折算秒 | 低估比例 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1588 | 21.2261 | 21.8464 | 2.839% |
| 1 | 1606 | 21.3601 | 21.9996 | 2.907% |
| 123 | 1537 | 20.4971 | 21.1010 | 2.862% |
| 161803399 | 1618 | 21.3293 | 21.9629 | 2.885% |
| 20261022 | 1515 | 19.7073 | 20.2999 | 2.919% |
| 2147483647 | 1609 | 21.4261 | 22.0569 | 2.860% |

9473 个离散 API 返回值按顺序相同，六轮最终 Cactus 均为 131072，Pumpkin 均为 999995904；时间查询单独比较，不计入精确一致数量。54 条边界观测覆盖未成熟复种、越界交换、移动环绕、草交换失败、翻地缓存、交换、成熟后收获/复种和脚本随机数。正式 RNG 实现另通过既有独立 .NET 参考的 73728 个混合值对照。

时间列来自当时未插桩策略的get_tick_count()，包含验证入口额外函数定义、分支和末尾库存读取，不是官方榜单成绩。初始版本未添加经验倍率，约3%的偏差只描述该版本和场景；当时本地单轮计算约0.05～0.06秒。扩展版本按方法验证，未用这些历史数字冒充重新测量的整轮误差。

初始版本的API上限、纯计算步数上限、墙钟终止、未知API、Python专有函数、额外导入和错误实体类型七项检查通过。当时Python 3.12的opcode跟踪没有产生预期事件，使用行/函数调用事件计步；该历史结果不能代替当前编译检查点实现的运行验证。

请求结束后已逐字节恢复真实 `test.py` / `simulate.py`；BepInEx 与 Unity 请求 35 期间的新增日志无 Error/Exception。原始输出、两份日志、逐 seed 报告、探针和首次差异比较器保存在本机 `.codex/tests/local-cactus/`。请求 34 曾因探针使用游戏不支持的 `int()` 失败，修正后请求 35 完整通过。后续方法级验证见 API 覆盖记录；显示刷新率异常的处理见 [模组运行排查](../../game_mod/README.md#显示帧率与-vsync)。

事实源为当前安装资源 `FarmObjectSO(cactus)`、`LeaderboardSO(cactus_single)`，及反编译的 `Simulation`、`Growable`、`GridManager`、`Drone`、`Cactus`、`Execution.ApplySideEffect`。资源提取只是本次核对工具，模拟命令不依赖 UnityPy。

| 证据 | SHA256 |
| --- | --- |
| Core.dll | `b8ac8d22b614d9e48d3affa9a4de9c77e799b824ed8f50dc2e494cc2dd9f9082` |
| resources.assets | `a465a0e642a5e34687693fee927ef9343f4d2329e75f23a421c03a149d77b6e0` |
| lb_cactus_single.py | `a013b1fc641c0fa5e782fb0ad9946d7d7db55f11314f17d6ad410c4f9b9c7bfd` |
| 本次 game-output.txt | `6a214957427e87e9a321c6c6c228594f93e7e8ceeb37e4959c629bac5be42193` |
