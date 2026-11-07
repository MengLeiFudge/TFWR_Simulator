# lb_maze

## 2026-11-03：新版完整统计86.964699秒

Steam build26385848。沿用此前正式执行逻辑，只刷新完整轮时间注释；执行AST不变。游戏同seed模拟request241为85.64秒，相同源码、研究、库存和seed 1的本地完整时间为85.639010940秒，差-0.000989060秒。simulate只输出到0.01秒，不据舍入值声称tick完全一致。

request257正常结束官方完整83轮，均值**86.964698795秒**，范围83.615–91.105秒。三类时间为**85.639010940 / 未另开短时统计 / 86.964698795**；同seed模拟另列，不充当短时打榜。正式榜使用加密随机源，其均值与固定seed的差异不是模型误差。游戏输出无警告。BepInEx与Unity新增日志无Error/Exception；终态按同ID回idle后逐字恢复临时存档覆盖，结果页已自动确认。

Steam公开账号行在2026-11-03T05:06:07.825233+00:00查询为86.965秒、#20。这是账号跨版本历史最好；比本轮更快时不能当作本版成绩。来源：https://steamcommunity.com/stats/2060160/leaderboards/17869891/。

执行源SHA256 `ca6a5d19bd4284337e0db156d531f134412096924ef9c1474fe3708402dc9845`；仅更新时间注释后的正式源`f0a97d3a2d29690e75bcb86102dee823a7339e1973521c42e4f40e3fbbce8722`；完整报告`9f2536c5cd2f2039f6536aa6352735564542f63a1d6cabe2305ebe7e075c55ca`。原始场景、修正前后本地报告、部署/恢复清单及双日志见本机`.codex/leaderboard-sol/game-update-revalidation/`，逐榜误差和模型边界见[新版16榜复验](game-update-validation.md)。历史下文按原游戏版本保留。本批未新增策略搜索。Implementation deviations：None。

## 2026-10-30：并行分枝探图与树距离责任区

固定16座8×8宫、每宫两机。在初始树的首个分叉处派一个助手探独立子枝，wait汇总64格后建对称路由表；以树直径四分点驻扎，按初始树距离唯一分派，开墙后归属保持。各机独立发现新边并维护路由，移动、轮询、复制与规划全部实计，不依赖实时知道另一机位置。满300次后唯一负责者正常收末箱，回收全部助手才重建，没有重复兑现。

唯一原生seed1完整为**115.85893779秒**，比旧左右责任区双机版130.54675887秒快14.68782108秒，仍慢于同seed正式独立小宫85.11703263秒。move58783→47398、解释器9802492→8732672t。此次同时改变探图与责任区，不能将差额独归于一项，也不能把总tick直接换算成共享墙钟差额。停止这个固定代表，不扫驻点或分枝常数；多人共宫类别保持开放。

正常达9865216 Gold，29代4817箱，29次64格无重复建图，73spawn/wait配对。13次满额最终收箱、4804次成功搬迁；WS消耗32+(29+4804)×256=1237280，与终态库存一致。库存非负，无错误、警告、失败输出或丢输出；构造/分析工具ty零诊断。证据`.codex/leaderboard-astra/maze-branch-team/`，源`d79777e5b3433c187b39eaf9c30e5cb5aeacef1c145306854ce135bc847c445a`，报告`6e9c91b19c88f132231b8f532d3bba53ca0c17b7568b08da593783a2574c2692`。三类时间115.858937790/null/null；正式86.968566秒不变。Implementation deviations：None。

## 2026-10-29：第二代按需建路未取得收益

首代保持对称全点对路由；第二代及以后仍完整DFS探图，但只为实际宝箱目标做反向BFS，并缓存该目标的全起点距离/首步。出发点发现新边就清空缓存，避免对未使用目标维护路由。每宫独占，仍正常搬迁300次后走到末箱收割；没有重复领取同一宝藏。原基线报告实际55代，早期接续摘要误记56代，本轮按原报告纠正。

固定完整seed1从85.11703263退到**90.23278221秒**，慢5.11574958秒。解释器1316677→1838072tick，move64399→66651，can_move14548→14927。整体失效后的反复BFS没有换来费用收益；等长路径次序和运行节奏也改变，不能把全部差额归为单一操作。关闭这个固定尾代按需方案，不扫切换阈值，不进实机。

候选正常达到9863552 Gold，32无人机记录、31spawn/wait、57代10198宝箱；各边长的宝箱数×面积×32与净Gold一致，库存非负，无错误、警告、丢输出。30/40秒内外限、100万API/1000万steps，实际墙钟6.764秒。构建/分析工具ty零诊断。源`314bcabb5e3c3463a809d29c2647592473b4d6225aedc8fb86dd69405dda743f`，报告`60752e42fe0d614fc12e71564ef0d3ecf7f8e9edbcb8ae1c4b91eb0334c2aca9`；证据`.codex/leaderboard-astra/maze-lazy-final-generation/`。三类时间**90.23278221 / 未取得 / 未取得**；正式86.968566秒及策略保持。Implementation deviations：None。


## 2026-10-28：延迟探墙与沿途探墙均未优于出发点扫描

从当前对称建表版出发，分别固定两种信息采集策略，未扫描频率常数。第一种在已知路线达到宫内Manhattan几何下界时延迟探墙；当前这趟不可能更短，但会推迟其他路线的新边发现。第二种在每个途经节点探墙，发现新边后立即增量更新全点对表，以while沿最新路线前进。

| 固定seed1完整模型 | 游戏秒 | move | can_move | 解释器tick |
| --- | ---: | ---: | ---: | ---: |
| 当前出发点扫描 | 85.117033 | 64399 | 14548 | 1316677 |
| 达几何下界则延迟 | 86.832763 | 65597 | 10779 | 1380580 |
| 每个途经节点扫描 | 89.726442 | 64222 | 62880 | 2213356 |

前者省探墙但增加移动，后者只少177步却大幅增加计算，两者完整费用均未回本，不进实机，不以新常数或追加种子救活。均达到9863168 Gold，实际9863520/9863296，31次spawn/wait配对，32份worker结果，正常搬箱后只收最后宝藏一次；无错误、警告或丢日志。分别6.089/9.029墙钟秒，在30/40秒内外限、100万API/1000万steps内完成。两个构建工具ty零诊断。三类时间分别86.83276266/null/null和89.72644185/null/null；正式86.968566秒保持。

证据`.codex/leaderboard-astra/maze-demand-scan/`和`maze-route-scan/`。源SHA256分别`1b8e53f1d0542028ce7c987b76bd6aa2ca319673288fc49a715e4b738c1b3e52`、`9d17ebab1a48ddb0a799817454c2e06e71d5379bc00fffaf235e6b20d0b00fdf`；报告分别`a0bd2b35a3aa42af7e11e47fc2e845f848d832e92f4bbc1d8cbd73ef6508a70e`、`1a6f541155eaaa84cfe54620cdd19f478d2c6222f476add179d21435589bf793`。首次延迟版构建因CRLF匹配断言失败，修正输入换行后只执行一次有效模型。Implementation deviations：None。


## 2026-10-28：初始路由表对称构建，官方83轮86.968566秒

当前版保持32座独立小迷宫、布局、出发点探墙、增量新边更新和正常宝藏兑现流程，只替换`build_all_routes`。按父节点先于子节点的顺序加入叶节点，每个无序点对只算一次距离，同时填写双向首步。原树中的唯一路径不变，避免旧版逐目标反转祖先链及再次填充距离。

三类时间：完整本地seed0/1/123为86.673420、85.117033、87.376634秒，均值86.389029秒；request154短筛实际8轮86.494625秒；request155官方完整83轮86.968566秒，范围83.899–89.993秒。较上一正式87.673855秒缩短0.705289秒、0.8044%。固定seed1旧版87.650051→85.117033秒，解释器1416846→1316677tick；实机平均收益较小，不能把单seed节省直接外推为官方收益。

9组原生树（5/6/7边长×seed0/1/123）共12966个有序点对，旧表、新表逐项相等；独立BFS距离和逐步通路核对通过。三份完整模型均达9863168 Gold、31次spawn/wait、库存非负且无警告。实机完整报告`done/full_statistics/output_complete`，BepInEx和Unity日志无异常，结果页自动关闭；原存档在idle155恢复。公开Steam账号查询的网络错误仍未解决，本节不声称已确认新公开名次。

证据：`.codex/leaderboard-astra/maze-symmetric-initialization/`中的`manifest.json`、`equivalence.json`、四份完整模型、request154/155原始完整结果、`acceptance.json`及存档恢复哈希。执行源SHA256 `038762c7f08dae9d922b0a1726cef3d89c2d10b9a2cfa76f4d69081681880f0d`；正式文件只调整成绩和解释注释，执行AST相同。两个主机工具LSP零诊断，游戏编译与完整运行通过。上游来源与许可边界沿用下节，不使用重复收取同一宝藏的漏洞。

## 2026-10-28：32座独立小迷宫，完整83轮87.674秒

当前正式版采用32座互不重叠的小迷宫，每机独立寻宝。request146正常完成官方**83轮、87.673855秒**，范围83.984–92.532秒。相比上一正式版127.169105秒，缩短**39.495250秒、31.0573%**。公开Steam账号查询遇到WSL TLS EOF和Windows网络错误，提交是否已公开及当前名次未验证；不能用旧缓存估计位置替代确认。

算法来自[zzlg-git的V7方案](https://github.com/zzlg-git/TheFarmerWasReplaced_Maze_1min28s/tree/e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629)，固定commit `e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629`。完整读过代码和README后先跑原文，再仅整理仓库入口：main改名lb_maze并置于第一个函数、增加builtins类型提示导入及末尾入口条件。上游树未附许可证，本轮仅本地使用，保留作者归属，未push或对外发布源码。

| 执行版本 | 完整本地预测seed1 | 短时实机 | 官方完整统计 |
| --- | ---: | ---: | ---: |
| 上游原文81ad3b48 | 88.945203秒 | 86.0285秒（request143，2轮） | 88.080768秒（request144，82轮） |
| 仓库入口392f6079 | 87.650051秒 | 89.290秒（request145，2轮） | **87.673855秒（request146，83轮）** |

旧版同版本模型新鲜seed1复跑为122.617166秒。入口顺序变化会影响并发随机流，不把两版约0.407秒的官方均值差解释成改名提速。完整预测采用运行器整轮计时，不用原文晚于初始化开始的t0输出。单seed预测接近多轮均值不证明逐tick精度。

make_jobs安排20座5×5、6座6×6、6座7×7，覆盖1010格。每台先到中心，用两次各1 Weird感染/恢复草，累计64消耗构成部署屏障，全部到位后才建宫。二叉派发31次spawn，末尾回收31句柄。每宫单一写者，无共享Python地图或同宝藏竞争。explore一次DFS建图，build_all_routes建立全点对首步和距离；scan_departure只从出发点探墙，add_route_edge冻结旧距离再对称增量更新。每宫正常迁移300次后harvest最后一箱，再重建；每次迁移支付200t，不利用结算窗口重入。

本地整理版Gold9863872、32份worker结果、54代建图、10291次兑现；边长5/6/7分别7248/1697/1346次，按面积及Mazes6倍率核算与库存一致。Weird消耗1792768，库存非负，无警告或丢输出。两批完整实机均正常完成，游戏输出及BepInEx/Unity双日志无失败或异常；短筛sample_limit仅表示主动停表。

执行源SHA256 `392f60793ea926c5c59cc5085348e34c97334c88d2aaa31a18e851dae1fac61b`；本地报告 `bf98d83a72769c31ea7bed119802a77eb1de0c126b55c7c1bc695f699dadfa49`；request146完整报告 `5e131cffcdb0dd8501aad5802b094358f0fc224d6e64137a2e3575a45512b785`。成绩和类型桩说明注释在运行后补充，AST与归档一致。普通LSP无法解析游戏builtins；指定gamesave搜索路径的ty静态检查通过。

证据在`.codex/leaderboard-astra/github-strategy-search/zzlg-git/`，含上游原文、两版执行源、同源报告、请求143–146完整归档和恢复清单。idle146后按哈希恢复Save0两份原文件，随后正常退出游戏。

本轮纠偏：以前把搜索范围过早限定为一座大迷宫，没有完整比较多宫独立产金。下文固定#10或1.1倍线仅保留为历史决策，不再作为准入规则。后续先比较任务数量、规模和协调费用，再决定局部优化；对称初始化、末代按需建表尚无收益证据。

## 2026-10-26：唯一负责权与完整覆盖版正式上榜2:07.169

当前正式版正常完成官方 **57轮、127.169105秒**（request134）。2026-10-26 20:53:45 UTC公开Steam账号查询确认 **#103、127169毫秒**。它是新的合规与完整性基线；历史103.336秒不是本版本成绩。当前#10缓存36.409秒，仍有90.760秒差距，不用异常前排名次推导漏洞策略。

| 执行源f23a07cf | 完整本地预测 | 短时实机 | 官方完整统计 |
| --- | ---: | ---: | ---: |
| 唯一负责、边界树补图 | 122.617166秒（seed1） | 124.6955秒（request133，2轮） | **127.169105秒（request134，57轮）** |

每个格子的负责集合互斥。负责机到达后再次核对当前位置与Treasure；完成300次正常重定位奖励后只收割一次，不利用200tick结算窗口重复取宝。路线可途经其他区域，但只为本机负责目标保存路线。空闲机使用普通200tick换草帽动作降低现实CPU空转，游戏时间与Power照常支付。

探图全部回收后，`complete_map`先核对1024格连通覆盖；有缺口时只规划一次通向所有未知边界的已知树枝，真实走访并探测未知分支，墙面失败不再触发全图重算。`maze_chunking`先完成全部负责权分配，派发失败的区域合并到主机，再开始主机求解，避免容量耗尽时阻塞剩余区域。仍保留180游戏秒截止，未通过增大时限掩盖失败。

57轮逐轮日志都核对到map/nodes1024、300次成功重定位、一次最终收割、Gold9863168。其中3轮实际补齐42/2/1个遗漏格；5轮由主机承担2/50/13/9/13个溢出负责格，全部完成。含补2格和主机50格的较慢轮为177.29秒，接近截止，不能据此声称任意拓扑都不会超时。有限探图派发失败诊断保留，但这些缺口均被补齐；没有策略失败、警告或输出丢失，完整统计BepInEx/Unity日志无异常。

本地正常seed1严格得到Gold9863168、Weird消费308224、use_item301（创建1+重定位300）、harvest1，库存非负。另有固定26子机的容量不足诊断和人工删7格子树诊断；后者完整176.699946秒，其中5.59674秒是人工生成诊断输入，只有这段从诊断截止扣除。诊断不作正常性能预测，也不改变候选180秒截止；实机已经分别触发上述两类真实边界。

执行源码SHA256 `f23a07cfa1f7aad68af2240181393890aa27ca6ae5bdb1d20b1a5bb6375d7f9d`，本地报告SHA256 `c492044feb061f961d8d20a2cbc6a3b5de0142ad22bdeb235b6834d6aff24b15`。正式迁入仅更新成绩注释，执行AST一致；request135再完成2轮124.697秒，独立记录，不替换短筛或完整成绩。idle135后目标脚本和入口按备份哈希恢复。

此前失败均保留：124因纯轮询现实速度不足而取消；126暴露漏格；127暴露分区同步回退死锁；132在第7轮逐格补图过慢而截止。它们的已完成轮不算官方成绩。root-overflow全图路线复制和branch-repair撞墙后重算的诊断负例也未进入正式版。完整源码、各阶段原报告、request133–135双日志、逐轮验证、公开查询和恢复清单位于`.codex/leaderboard-astra/maze-single-owner/frontier-tree/`，前序记录保存在同级各版本目录。游戏语言编译通过，构造与运行工具ty零诊断。

## 2026-10-26：唯一负责机与归位途中改道未提速

保留正式探图、radius14及原覆盖分区，改为owned_set唯一负责机兑现；路径只保存父节点、深度及双向动作，沿实际新开墙做私有增量松弛。闲时逐步归位，自己负责的新宝藏出现时从当前位置经树上共同祖先改道，避免必须先回中心。只在300次正常重定位奖励已经取得后最终收割一次，不以普通失败或结算窗口重入重复领取。

唯一seed1源`03c24cd6c66ec605b97f443929cc254b8db2ae9c7db166e47537af2536a0f8b1`完整106.75254798秒，比正式同seed106.051803慢0.700745秒，未过事前15%收益门槛。28份worker结果合计300次成功重定位、3750次服务及归位move、仅14次途中响应；全程move9590、解释器13529354t。唯一责任消除竞争，但改道机会稀少，也舍弃了重叠区邻机更早响应；总移动减少不能代表服务关键链缩短。

Gold9863168、Weird消费308224，use_item301次恰为创建一次加300次重定位，harvest一次，无失败/警告/丢输出/负库存。三类时间106.75254798/null/null，不扩seed、实机或等待参数扫描。原始源码、报告SHA`68dba2425f0dba62d8cebe289202406d77eb6efcf8bfcf0a73ecda76f9a3f5af`及逐worker分析在`.codex/leaderboard-astra/iteration-20261026/maze-mobile/`。本轮刷新#10为36.409秒；正式策略与此前成绩保持。

## 2026-10-26：跨辖区全局中心交换仍未留下实际费用余量

固定原生seed1的301拓扑，在事件0/50/100/150/200/250各最多八次全局PAM交换，允许任意新中心替换任意旧中心，突破旧medoid仅辖区内移动的限制。每次目标值下降与全图独立重算一致，32中心互异；选址不读取当前/未来宝藏。实际响应1173→1149步，但加301次兑现仍47.7369秒，已超过1.1×#10的47.0547秒；建图、规划、迁站和服务返程均免费，关闭本固定协议，不增加迭代数。

六更新点优化后均匀平均图距离6.011719/4.617188/3.877930/3.485352/3.273438/3.146484；迁站另有521步免费。规划包含6445 BFS、15631376邻边、48758784候选点距离读取，不能当游戏免费能力。唯一几何运行墙钟5.022秒；证据`.codex/leaderboard-astra/maze-global-center-swap/`，原执行源归档后仅补局部类型注释、ty0，未重跑。完整三值null，正式/模型/Save0/队列不变；局部下降及固定限额不证明全局最优，也不否定所有动态覆盖。


## 2026-10-26：原生拓扑的覆盖条件期望界

按Claude讨论复核同一原生Maze seed1的301拓扑，所有目标与旧驻点报告逐项相同。每个半径以最大的32个图球格数之和作为覆盖上界，截断到1023个候选目标（首目标1024）；在目标均匀且不可预知的条件下，累计响应期望下界898.702992步，加301次兑现为39.496622秒，距#10仅余3.280378秒。

同一组自适应medoid中心的均匀目标期望为1205.913875步、49.610619动作秒；其实际seed1173步另列，不混合两种口径。球和忽略重叠，界可能松；真实PRNG条件独立性未证明，不能把期望当单seed硬界，不能据此断言#10不可能或所有分迷宫无收益。未继续数百轮优化下界，也不更改#10基准；后续需有改善主路径的具体机制。

证据`.codex/leaderboard-astra/maze-coverage-bound/`，301拓扑哈希、逐半径球和及实际并集全保存；离线1.920秒、ty零诊断，无策略执行，完整三值null。


## 2026-10-26：随开墙更新驻点仍没有足够响应预算

沿同一原生seed1的301目标/拆墙流，在第50/100/150/200/250次后按当时完整墙图做三轮medoid更新，不读取未来目标。赠送全部建图、规划、搬站、归位及解释器，响应move由固定驻点1261降至1173，连同301次兑现仍需48.527028秒，高于#10=42.777秒。固定目标与对应距离逐项和原报告核对；新方案不进入在线实现，不扫描更新频率。

本次全图BFS5421次、检查22204416条边，说明所赠送的规划亦不可忽略。此结果只关闭该固定更新规则，不证明全部动态覆盖无解。证据`.codex/leaderboard-astra/maze-adaptive-medoids/`；唯一离线工作4.877秒，执行源独立保留，当前源只补类型且逐字还原核对，ty0。完整三值null，正式与Save0保持。

## 2026-10-26：规则预分散站位的局部探图存在覆盖缺口

固定8×4站位先到场、各探图距离12范围，原生seed1初图只覆盖740/1024格，漏284格；301个宝藏位置中82个不在任何局部图，第一处宝藏即未覆盖。局部DFS回站最大90move/2.96298秒，但几何最近站位的图距离最大40，不能用规则格点间距替代墙内路径。

即使只计219个已覆盖事件，赠送局部新增墙洞、免费最短路和归位，1045move加219兑现仍41.613408秒；未覆盖事件不填时间。关闭这个固定局部图方案，不枚举半径，也不泛化全部分布式探图。证据`.codex/leaderboard-astra/maze-local-bootstrap/`，源码8668e06c；无候选执行、三值null，正式105.335568记录保持。

## 2026-10-26：平均距离驻点与四座小迷宫的免费几何筛选

按真实初图贪心降低总最近距离，再做三轮medoid更新，32×32的32驻点在301次真实目标/拆墙流中需1261响应move。赠送每次免费归位、全图最短路、建图、部署、规划与解释器后，响应加301动作仍51.424164秒，高于#10的42.777秒，不实现该固定配置。

四座16×16各8驻点沿同一规则规划，固定建图顺序、轮流推进真实重定位。四座响应move为1479/1372/1216/1337，免费服务动作关键链58.601160秒，产量合计9863168。这里的随机分配不是实际并行执行，结果不泛化所有四迷宫策略。证据`.codex/leaderboard-astra/maze-median-centers/{seed1.json,four-seed1.json,research-note.md}`；两项完整三值均null，无候选或实机运行。

## 2026-10-26：并行树图与固定驻点实现未过筛选

私有4f25adeb在32×32原场景seed1构建真实1024节点、2046有向边的初始树；26.881471秒完成建图，桶式最远覆盖规划到44.297868秒，最后一台驻点到位60.652036秒。固定owner回应与返程没有抵销开局成本，160秒服务截止后报告160.599936秒、Gold6815744，未达9863168。136次spawn/wait相等，无错误或warning，但有station_failed/service，完整三值全null，关闭此固定实现。Reset8机驻点完整收益不能外推本榜。

另对同初图31个驻点做极有利的动态最近赢家几何：免费全图最短路、赢家停在新目标、其他机不动，真实301次迷宫重定位及拆墙流中共1507move。仅move+301次动作59.522976秒，尚未计建图、到位、互斥、选择与解释器，已不支持用该固定驻点配置冲击#10。因此没有实现最后一个空闲无人机充当锁的派发协议。此结果只限本输入和配置，不是所有动态覆盖的下界。

证据`.codex/leaderboard-astra/maze-parallel-stations/`的seed1.json、analysis.json、dynamic-winner-seed1.json及research-note.md。三类完整时间均null；正式py、模型、队列、Save0和请求79保持。

## 2026-10-26：真实成功服务时间与32连通分区判别

在97.999905秒的可中止候选上增加成功服务摘要，唯一seed1完整98.274968秒，Gold9863168、无错误/警告/丢输出。新增日志与分支付费，不能当原版精确时间。300次成功取宝路线共1668move，出发至到达累计57.280329秒，兑现9.925983秒；相邻成功服务的赢家出发间隔合计10.558908秒。首个赢家17.503804秒出发，最后重定位后至报告尾3.005943秒。三段严格闭合77.765221秒服务跨度。间隔合并回程、责任区短等待、轮询和竞争，未分别强归因。

另按初始真实树递归切为32个连通分区、各取树中位点；初图冻结owner平均6.586914步，真实301目标在各次免费完整图上的最近中心平均4.551495步，纯响应与兑现55.012662秒。赠送完整墙发现、归位和规划后也只比观测成功路线部分少约12秒，而还须支付新分区及站位；这个固定重分区未形成足够结构收益，不实现在线版本。期望覆盖估计不能用作每个有限成绩的不可达证明，#10基准保持。

证据`.codex/leaderboard-astra/maze-response/{lb_maze_observe.py,observation-seed1.json,response-analysis.json,balanced_geometry.py,balanced-geometry-seed1.json}`。观测版与几何协议不进入首选成绩表，正式py、此前完整候选、Save0和79保持。

## 2026-10-25：动态32站响应与可抢占归位

同一真实Maze seed1的301次获宝，允许当前位置随获宝改变。获宝后原地停留需1478响应move，动作链58.568238秒；其他机同期归位且允许途中抢占时，1347响应move加1321真实归位move，动作链54.255456秒。每步邻接/开墙检查通过，不读取未来next_pos。

初始优化站位及布站、完整实时墙图、选主、最短路、通信和解释器仍免费。两种固定贪心都没有支付42.777秒#10预算的余量，暂不写全局动态调度器；不是最优控制下界，三类完整时间null。证据`.codex/leaderboard-astra/maze-moving-coverage/`，来源SHA已复核、ty0。


当前研究（2026-10-25）：持久新开墙缓存取得完整seed1的98.099988秒，可中止扩区版97.999905秒，对同seed正式106.051803秒省7.50%/7.59%。均仅一个完整本地样本，尚未短测或官方统计；约2.29倍#10的差距仍在，不为这点收益扩样或迁真源。原局部逐次建索引捷径三seed负例保留。正式`lb_maze.py`及Save0未改。

此前研究（2026-10-24）：局部捷径候选完成相同条件seed 0/1/123完整本地对照，均达标但比当前真源慢10.87%～12.05%，不进入实机。正式`lb_maze.py`保留原实现，实际入口为`lb_maze()`；下文`main9`等旧命名和成绩为历史记录。原100条输出限额和长seed进度阻塞已由Astra处理，并取得六次完整执行证据；本次没有Maze实机精度验收或新游戏打榜时间。

## 2026-10-25：十六座8×8与局部补充无人机组件

实现私有`maze-sixteen/lb_maze.py`，十六个不重叠8×8框各两台初始无人机。32台先在独有Grass格收获512Hay，达到16384后才创建迷宫；每台独立建所属64格地图并缓存驻点路线，发现新墙道后重建当地路径。追击期间目标改变就按实际已走前缀返回。每座controller负责等待本地全部句柄后最终收割；局部任务可在其他座释放槽位后招募新worker，按固定整数区间细分驻点，不使用共享可变全局图或从总Gold猜某一座进度。

先用真实迷宫机制取十六座完整重定位轨迹，但赠送全图可见、每次双机免费回家、无竞争和无规划开销。固定驻点的平均/最慢分区仅路程与兑现费用约60.393/79.046秒；初始树直径四分位驻点约59.813/71.869秒。生成顺序不是并发执行顺序，这些只作条件几何估计，不能当实际时间或普遍下界。

随后唯一seed1在45游戏秒组件截止后完成回程和回收，最终报告46.48059648秒、本地计算6.801墙钟秒。16份结果全部`ok=True, exhausted=False`，各2台worker，成功重定位合计741次、Gold1517568，仅为完整目标的约15.39%；无error/warning/丢输出。Weird消耗193792，精确对应16次创建加741次重定位、每次256；Grass收割32次、Hay16384，spawn/wait各31，move26552次，解释器2652244t。最后日志46.47302442另列，不冒充最终报告时刻。

没有一座完成300次重定位，因此跨座释放槽位后的实际招募、controller最终收割及其终态未动态验证。源上的这些分支不能算组件已经通过。当前固定双机驻点/独立DFS结构的吞吐和有利几何账均不足以支持#10=42.777秒，不扩大为完整榜、调驻点或扩seed；三项完整时间全部null。

证据`.codex/leaderboard-astra/maze-sixteen/{geometry.py,geometry-seed1.json,geometry_diameter.py,geometry-diameter-seed1.json,lb_maze.py,component-seed1.json,analysis.json}`。执行源码SHA869b30cf与报告一致。正式py、现有完整结果和实机请求79/Save0均保持。

## 2026-10-25：持久墙图、扩区与可中止追宝

本次连续实现三版私有脚本，均复用正式探图、radius=14、原负责区优先和同一满级显式库存场景。第一版只在回程访问点检查仍关闭的候选边；发现开墙后双向记入worker私有图，回到中心后仅传播真正下降的路径深度，避免每次取宝重建路线索引。第二版允许较短新路径将服务区域扩到原区外；第三版每走一步复查当前宝藏，变化就停止旧追击，沿实际已走前缀返回，防止继续走失效路线。全部查询、路径复制、回程及保护均计费。

| seed1完整结果 | 游戏秒 | move | use_item | 解释器t |
| --- | ---: | ---: | ---: | ---: |
| 正式同seed基线 | 106.051803 | 10894 | 339 | 12059052 |
| 固定区域持久缓存 | 98.099988 | 10218 | 338 | 10980330 |
| 持久缓存并扩区 | 101.790709 | 15570 | 620 | 10687085 |
| 扩区并可中止追宝 | 97.999905 | 12442 | 320 | 10433468 |

三版均正常完成Gold9863168，无error、warning或丢输出，Maze随机流均623194次；同流计数不代表全状态逐步等价。固定区及可中止版末Weird999691776，与正式相同；扩区版999688704，多消耗3072，竞争并非只有时间代价。完整完成墙钟分别49.847/48.720/34.705秒，有限55秒CLI及API/检查点上限均未触发。

扩区使use_item与移动大幅上升，加入可中止逻辑后明显下降，但净时间仅比固定区域版快0.100083秒。保留两版作后续结构基底；当前证据支持避免逐次重建与失效追击，尚不足以填平到#10=42.777秒的差距。不因单seed正收益继续扩样、实机或调等待参数。三项时间分别为各行完整本地值/未取得/未取得，不合并不同SHA均值。

另用现有FarmWorld/Maze直接生成seed1并完成300次正式relocate，取0/30/75/150/300次后的真实墙图；没有另造随机墙代理。免费全图距离、32站位贪心初始化及最多6轮区域medoid更新下，平均最近距离为6.251/4.891/4.160/3.606/3.170步；原28中心为7.229/6.560/5.440/4.521/3.884步。末期32站位路程与一次200t兑现动作套到300次，仍约41.184650秒，尚未计建图、派发、站位规划、墙发现、回程、竞争和解释器。此为单seed五个截面的条件估算，既不是最优下界，也不是整轮预测；它提示只重选静态中心余量很窄，后续须继续改变主要响应路径。

Core Treasure.RepositionTreasure先检查repositioning，成功后才付200t延迟并在CompleteRepositioning开墙；等待中重入不会额外兑现或提前拆墙。没有用失效调用为拆墙加速的依据。实机请求79及Save0冻结继续保持。

证据`.codex/leaderboard-astra/maze-persistent/`：三份私有脚本及seed1报告、`comparison-seed1.json`、`geometry_screen.py`与`geometry-screen.json`。固定区SHA112bf624、扩区29c5c3a6、可中止e79c00e2；几何筛选仅离线使用已有模型机制，完整三值全null。

## 四座16×16：独立完整建图协议的静态剪枝

四个中心(8,8)/(24,8)/(8,24)/(24,24)形成不重叠象限，各8机。满级每座创建与每次重定位各需512 Weird；300次重定位加最后收割共301次兑现。四座总产9863168 Gold，耗616448 Weird，分别等于当前目标和单座32协议Weird用量的两倍。Core Treasure在200t定时器结束后才显示新位置，每座300次串行延迟合计9.8766秒；不能按动画collectionDuration=0把成功harvest免费化。

所审协议先让32台各到独有Grass格并收获512Hay，以16384Hay作为全到位屏障，再创建四座迷宫。每台独立完整DFS建所属16图；每座配额4×38+4×37=300，helper仅返回成功次数，controller收齐7个返回再最终收割，最后主机回收其他controller。无需可变全局共享图或从全局Gold猜分区进度，但须支付32份建图和配额耗尽后活跃机减少的代价。

每机完整DFS至少510move；保留原Reset visited列表时，两类首次not-in比较至少65280项。新隐藏目标在除旧点外255格均匀、worker不预知的条件模型下，即使8机理想站位且所有墙免费开放，Manhattan半径0/1/2/3球并集最多8/40/104/200格，最近距离期望至少668/255。299次转移对应至少783.262745步的条件期望。该条件不能替代逐seed实际路径。

| 小计 | 游戏秒 |
| --- | ---: |
| 入场、完整DFS移动、300串行延迟 | 28.279998 |
| 上项加必需列表比较 | 39.025739 |
| 动作小计加理想搜宝期望，全部解释器免费 | 54.066574 |
| 再计必需列表比较 | 64.812315 |

#10为42.777秒，1.1倍准入线47.0547秒。关闭这一独立完整建图协议，不为它新增候选或样本；39.025739的硬小计本身未超线，关闭依据包含明确的均匀条件期望，不声称所有seed必慢，也不排除分工建图等其他四分区结构。真实四座时长取最慢分区，不能将小计再除4或32。

Astra已复核Core创建/重定位/measure规则、原DFS两类列表查找及有限公式。证据`.codex/leaderboard-sol/maze/four-partition-budget/analysis.json`（SHA前缀ecc17d96）、`research-note.md`（edcf38e7）；没有16图新样本或运行。当前正式本地105.335530秒保持，新协议三值均null。

## 榜单目标

- 目标资源：`Items.Gold`
- 多无人机路线
- 当前脚本目标数量为 `9863168`
- 当前默认入口：`main9()`

## 结算机制说明

- 迷宫榜的收益核心不是普通 harvest，而是“生成迷宫 -> 找到 Treasure -> 对 Treasure 重复使用 `Weird_Substance` -> 在合适时机收割”。
- 迷宫大小的基本规则是：
  - 对 Bush 使用 `use_item(Items.Weird_Substance, amount)`。
  - 未升级迷宫时，`amount = n` 会生成 `n x n` 迷宫。
  - 每次迷宫升级，宝藏金币翻倍，但所需 `Weird_Substance` 数量也会翻倍。
- Treasure 的基础收益是 `迷宫面积 * YieldFactor`。
- Treasure 最多可以被重新定位 `300` 次。
- 一个吃满重定位次数的迷宫总量级可近似看成 `迷宫面积 * 301 * 32`。
- 套回当前 leaderboard 目标：
  - `32x32` 全场迷宫面积是 `1024`。
  - `1024 * 301 * 32 = 9863168`。
  - 理论上完整吃满一次全场迷宫即可结算。

## 当前基线

- 旧站桩流已废弃：
  - 旧文件内的迷宫时间属于迷宫机制更新前的数据。
  - 这些时间不能再作为当前版本基准、候选成绩或优化目标。
  - 对应本地实现已从 `lb_maze.py` 删除，避免后续误用。
- 当前默认路线是外部 `Save0/maze_multi.py` 修复后的 `main9()`：
  - `32x32` 先多无人机探图。
  - 探图完成后按区域并发追 Treasure。
  - 当前已禁用 solver 行走过程中的动态墙刷新；墙只会消失，旧路径仍可走，真实验证显示省掉每步 `can_move()` 刷新有轻微收益。
- 2026-04-26 真实验证：
  - 请求 `300` 跑出第一轮 `1:53.548`。
  - 同轮输出 `maze_multi explore_done edges=2046`。
  - 同轮输出 `maze_multi chunks=31 nodes=1024`。
  - 第二轮因 `--request-timeout 90` 取消，不计有效均值。
- 2026-04-26 阶段耗时探针：
  - 请求 `353` 第一轮 `1:50.579`，比请求 `300` 略快，但未刷新 `lb_start.py` 的长期基线。
  - 第一轮输出 `maze_multi solve_done gold=9863168 time=109.61 solve_time=92`。
  - 第二轮输出 `maze_multi explore_done edges=2046 time=8.37`、`maze_multi chunks=31 nodes=1024`。
  - 结论：探图约 `8s`，首金约 `21s`，主要瓶颈在区域 solver 的寻宝 / 回中心 / 重复竞争阶段，而不是全图探图阶段。
  - 第二轮在 `--request-timeout 90` 到期时取消，`finished=false runs=2 average=1:20.231` 不是有效均值。
- 2026-04-26 请求 `363` 基线复测：
  - 探图输出 `maze_multi explore_done edges=2046 time=9.06`，仍证明探图不是主瓶颈。
  - 主动停止时首轮 `gold≈7,110,656`、`game_time≈91.61`，模组估算剩余约 `32s` 游戏时间。
  - 停止摘要为 `[lb_maze] finished=false runs=1 average=1:31.786`，不是完整有效成绩。
  - 结论：解题段仍是核心瓶颈；当前单变量候选改为降低 `maze_multi gold=` 输出频率，验证日志开销是否影响 solver 段。
- 2026-04-26 禁用 solver 动态墙刷新候选：
  - 请求 `365` 有效完成两轮：`run=1 time=1:52.899`、`run=2 time=1:51.165`。
  - 两轮均值 `1:52.032`，相对请求 `300` 的 `1:53.548` 小幅刷新约 `1.3%`。
  - 停止摘要 `[lb_maze] finished=false runs=3 average=1:29.085` 混入第三个未完成轮，不能作为有效成绩。
  - 结论：保留该候选为当前默认；它只省掉 solver 每步 `check_new_path()` 的 4 方向 `can_move()`，不改变寻路拓扑。
- 2026-05-02 当前默认路线复测：
  - 请求 `405` 有效完成两轮：`run=1 time=1:46.445`、`run=2 time=1:52.499`。
  - 两轮均值 `1:49.472`，最近两轮差异 `5.7%`，满足 runner 稳定停表规则。
  - 第一轮输出 `maze_multi explore_done edges=2046 time=9.19`、`maze_multi chunks=32 nodes=1024`；第二轮输出 `maze_multi explore_done edges=2046 time=9.11`、`maze_multi chunks=29 nodes=1024`。
  - 结论：不改脚本逻辑，仅把当前默认路线的本地最好记录从 `1:52.032` 刷新为 `1:49.472`；该成绩仍明显落后 #1 `0:32.998`，后续继续攻区域 solver。
- 2026-05-30 当前版本复跑：
  - 请求 `617` 有效两轮：`1:49.837` / `1:46.523`。
  - 稳定均值 `1:48.180`；后续 `finished=false` 取消摘要不作为成绩。
- 2026-06-08 动态负责区短等待 fallback：
  - 请求 `627` 有效两轮：`1:48.085` / `1:38.587`。
  - 稳定均值 `1:43.336`，刷新当前本地记录；后续 `finished=false runs=3 average=1:10.160` 是取消摘要，不作为成绩。
  - 两轮 `solve_time` 为 `88.66` / `79.52`，相对请求 `625` 探针的 `91.31` / `89.2` 有净收益。

## 当前版本结论

- 现版本不再保留“站桩流 / 小迷宫固定格子流水线”作为本地候选。
- 废弃原因：
  - 旧路线依赖 Treasure 被 `Weird_Substance` 影响后快速进入下一个可处理状态。
  - 当前版本里 Treasure 重定位存在延迟，旧流水线会把大量 tick 花在失效操作或错误收获时序上。
  - 用户已确认旧成绩是机制更新前数据，现版本不能用。
- 当前有效候选只保留 `main9()` 的大迷宫多无人机探图路线。
- 当前版本复跑成绩：`1:43.336`（请求 `627` 两轮有效均值）。
- `finished=false` 或 timeout 后打印的 average 不是有效完成轮均值；有效成绩只认真实 `run=` 轮次输出。

## 失败对照

- `Save0/maze_mzlbe.py`
  - 2026-04-25 重新读取当前文件后复测，不沿用旧结论。
  - 临时覆盖为 `lb_maze` 并用 `leaderboard_run(Leaderboards.Maze, "lb_maze", 10000)` 验证。
  - 请求 `247` 只有 `[lb_maze] start`，`30s` output stall 内没有任何 `run=`。
  - `item_snapshot` 显示 gold 从约 `674816` 增至 `1137664`，说明脚本确实在获取金币。
  - 但 leaderboard 没有完成轮次，最终按 `leaderboard finished without completed runs` 处理。
  - 2026-04-26 尝试把它改成目标受控循环并压缩成候选，早期 `gold` 卡在 `512`，没有形成原脚本的 Gold 增长。
  - 根因：压缩版改变了原始多机展开时序，导致开迷宫 / 推 Treasure / 收割流水线没有跑起来。
  - 结论：当前形态不迁入；失败实现已从 `.py` 删除。
- 旧站桩流
  - 本地代码已删除，不再修复、不再复测、不再与当前候选比较。
  - 如果未来有人重新提供同类思路，必须先按当前版本机制重写并重新跑真实完成轮，不能沿用历史文件内时间。
- 大图墙跟随式探索
  - 已明确不是榜前方向。
  - 后续只保留“大迷宫 + 多机分区 + 动态路径更新”的方向，不回退到单机贴墙。
- 区域 solver 的 `parent + dist` 路径缓存
  - 2026-04-26 请求 `327` 验证。
  - 改法：把 `solve_maze_in_area()` 内 `path` / `reverse_path` 的完整方向列表替换成 `parent` / `dist`，走路时临时回溯路径。
  - 结果：第一轮 `1:59.798`，慢于请求 `300` 基线 `1:53.548`。
  - 同轮输出 `maze_multi explore_done edges=2046`、`maze_multi chunks=29 nodes=1024`。
  - 结论：脚本执行层面减少列表复制没有抵消每次寻宝临时回溯路径的成本；候选已从 `.py` 回退，只保留本记录。
- 互斥分区
  - 2026-04-26 请求 `328` 验证。
  - 改法：`maze_chunking()` 中区域扩展不再穿过已覆盖节点，避免多个 solver 区域重叠抢同一个 Treasure。
  - 结果：到 `game_time≈48.8` 仍为 `gold=0`，明显慢于基线首轮早期 `time≈20.65` 已开始涨金币。
  - 根因判断：互斥分区让部分中心到 Treasure 的可用路径被剪断；当前 `solve_maze_in_area()` 依赖区域内连通路径，不适合简单切成互斥片区。
  - 结论：候选已停止并从 `.py` 回退；后续如果做固定片区，必须把“负责区域”和“允许寻路经过的图”分离。
- 区内当前位置 BFS、不回中心
  - 2026-04-26 请求 `339` 验证。
  - 改法：移除每个 solver 的 `center -> treasure -> center` 固定路径缓存，改成每次从当前位置在 `area` 内 BFS 到 Treasure，并且取宝后不再回中心。
  - 结果：主动停止前 `gold=3,407,872`、`game_time=84.288`，模组估算剩余 `eta_game_seconds=139.313`，总计约 `223.6s`，明显慢于请求 `300` 的完整轮 `1:53.548`。
  - 根因判断：虽然省掉了回中心移动，但每次区内 BFS 和缺少中心路径缓存带来的脚本执行成本更高；当前多机迷宫仍更适合保留中心缓存。
  - 结论：候选已从 `.py` 回退，只保留失败记录；后续不要再把“当前位置 BFS”作为轻量优化方向，除非同时改变分区和寻路缓存结构。
- 分区半径 `14 -> 16`
  - 2026-04-26 请求 `343` 验证。
  - 改法：仅把 `k_center_on_tree()` 返回值从 `14` 改为 `16`，期望减少 chunks 和无人机调度碎片。
  - 结果：第一轮输出 `maze_multi chunks=25 nodes=1024`，完成时间 `2:03.939`，慢于请求 `300` 基线 `1:53.548`。
  - 第二轮中途取消，`finished=false runs=2 average=1:38.199` 不作为有效完成轮成绩。
  - 根因判断：半径变大虽然减少分区数量，但每区内寻路距离和等待 Treasure 落入区域的成本上升；减少 chunks 没有带来净收益。
  - 结论：候选已从 `.py` 回退，只保留失败记录；下一步如继续测半径，应反向尝试更小半径或先补探图/首金时间探针。
- 分区半径 `14 -> 12`
  - 2026-04-26 请求 `344` 验证。
  - 改法：仅把 `k_center_on_tree()` 返回值从 `14` 改为 `12`，验证增加 chunks / 缩小区域是否能提高覆盖并发。
  - 结果：`maze_multi explore_done edges=2046` 后早期金币只涨到 `196608`。
  - 关键诊断：BepInEx `item_snapshot` 显示从 `game_time=22.114` 到 `game_time=74.423`，`gold=196608` 恒定不变；`progress_estimate` 输出 `unavailable reason=no_positive_rate`。
  - 结论：半径过小会让 Treasure 进入区域后路径或回收逻辑失效，形成低金币卡死；候选已停止并从 `.py` 回退。
- 分区半径 `14 -> 15`
  - 2026-04-26 请求 `347` 验证。
  - 改法：仅把 `k_center_on_tree()` 返回值从 `14` 改为 `15`，作为 `16` 与基线之间的中间半径对照。
  - 结果：第一轮输出 `maze_multi chunks=27 nodes=1024`，完成时间 `2:03.743`，慢于请求 `300` 基线 `1:53.548`。
  - 第二轮主动停止前 `gold=5,767,168`、`game_time=81.031`，模组估算还需 `eta_game_seconds=37.208`，总计约 `118.2s`，仍慢于基线。
  - 注意：停止摘要里 `finished=false runs=2 average=1:42.578` 不是有效完成轮均值，不能作为刷新成绩。
  - 结论：半径 `12 / 15 / 16` 均已证伪，半径微调方向基本收敛；候选已从 `.py` 回退，只保留本记录。
- 负责区域 / 可通行图分离
  - 2026-04-26 请求 `354` 验证。
  - 改法：保持原有 center 选择，但用多源 BFS 给每个 Treasure 分配唯一负责区域；每个 solver 的寻路图放宽到全图，避免互斥分区剪断路径。
  - 结果：`maze_multi explore_done edges=2046 time=9.77` 后，到 `game_time≈108.125` 仍为 `gold=0`，被主动停止。
  - 根因判断：每个 solver 预构建全图路径的脚本执行成本过高，导致解题阶段开始后长时间没有任何 Treasure 兑现；它比原重叠区域抢宝更差。
  - 结论：候选已从 `.py` 回退；后续不能用“每个 solver 全图 path 表”实现负责权分离，必须限制路径缓存规模或改为少量共享 dispatcher。
- 同区连续 Treasure 不回中心
  - 2026-04-26 请求 `355` 验证。
  - 改法：保留当前重叠分区，删除 `reverse_path`，用 `route_between(current_node, treasure)` 通过 center 路径公共前缀拼接同区内两点路线；如果下一个 Treasure 仍在本区则不回中心。
  - 结果：主动停止时 `gold=2,260,992`、`game_time=46.842`，模组估算 `eta_game_seconds=92.212`，总计约 `139s`，慢于请求 `353` 第一轮 `1:50.579`。
  - 根因判断：同区连续追宝虽然减少部分回中心路程，但 solver 停在非中心点后更容易与其他重叠 solver 冲突，且 `route_between()` 的脚本执行成本抵消了移动收益。
  - 结论：候选已从 `.py` 回退；后续不要再做“单 solver 漂移式不回中心”，除非同时解决重叠区抢宝冲突。
- 降低 `maze_multi gold=` 输出频率
  - 2026-04-26 请求 `364` 验证。
  - 改法：只在金币每增加 `262144` 时输出一次 `maze_multi gold=`，保留 `last_progress_time` 的逐次金币变化更新。
  - 结果：主动停止时 `gold=3,637,248`、`game_time≈65.16`；请求 `363` 同区间约 `game_time=65.42` 已到 `gold=3,964,928`。
  - 根因判断：输出频率不是当前 solver 段主要瓶颈；降低输出没有形成净收益，早期金速反而低约 `8%`。
  - 结论：候选已从 `.py` 回退，只保留本记录；后续不要把日志降频当作主要优化方向。
- 到位即开始收宝箱探针
  - 2026-04-30 请求 `393` 验证。
  - 改法：只在 solver task 内临时加入 `solver_spawned` / `solver_start` 探针，不改变 `maze_chunking()` 的调度结构。
  - 结果：有效完成轮为 `run=1 time=1:48.515`、`run=2 time=1:49.531`，两轮均快于当前记录的 `1:52.032`。
  - 调度证据：第二轮中最早 `maze_multi solver_start ... time=17.27`，随后才输出 `maze_multi chunks=30 nodes=1024`，之后其他 solver 继续在 `17.36` 到 `25.48` 间陆续启动。
  - 结论：当前实现已经是 worker 到达各自 center 后直接 `solve_maze_in_area()`，不存在“全员等齐再开始收宝箱”的等待点；后续请求 `405` 的无探针复测也达到 `1:49.472`，说明这更像当前默认路线可达到的波动区间，不作为新策略保留，`.py` 已回退到无探针实现。
- East-first 方向优先级迁移
  - 2026-05-02 请求 `429`：runner 输出 `reached stable leaderboard runs 2 avg=1:51.172`。
  - 改法：将 `local_dirs` 从 `[North, East, South, West]` 改为单迷宫有效的 `[East, North, West, South]`，不改变探图分支、区域切块、求解半径或寻宝时序。
  - 有效轮为 `1:52.070`、`1:50.273`；探图输出分别为 `edges=2046 time=11.33 chunks=30 nodes=1024`、`edges=2046 time=9.07 chunks=32 nodes=1024`。
  - 结论：没有刷新当前 `1:49.472`；单迷宫方向 tie-break 收益不能直接迁移到多无人机区域 solver，代码已回退。
- 2026-06-08 solver 分项探针
  - 请求 `625` 只加 solver 结束摘要，不改变 center、area、路径选择或收宝逻辑；验证后已从 `.py` 回退，并重新同步正常版到 `gamesave/`。
  - 有效轮为 `1:52.226`、`1:46.676`，稳定均值 `1:49.451`；慢于当前 `1:48.180`，不刷新成绩。
  - 第一轮：`explore_done time=11.97`、`chunks=30`、`solve_time=91.31`；第二轮：`explore_done time=8.8`、`chunks=30`、`solve_time=89.2`。
  - 两轮共 `60` 条 solver summary：平均 `hits=12.07`、平均 `approach=144.9`、平均 `route+back=185.4`、平均 `wait_time=73.8`；最大 `approach=341`，最大 `route+back=378`。
  - 两轮总 `hits=724`，约每轮 `362` 次 `use_item`，而理论结算只需要 `301` 次 Treasure 推进；说明当前重叠区域存在约 `20%` 级别的重复竞争 / 无效兑现空间。
  - 结论：下一步不要继续做半径微调、日志降频或单 solver 不回中心；优先看“减少所有 solver 从同一起点长距离走到 center”的调度结构，以及“减少重叠区域重复 use_item”的轻量负责权机制，但不能回到每个 solver 全图 path 表。
- 轻量负责区 / 通行区分离
  - 2026-06-08 请求 `626` 验证。
  - 改法：保留原 `node_set` 作为可通行 / path 区域，新增 `owned_set` 作为唯一 Treasure 负责区域；`solve_maze_in_area()` 只等待 `treasure in owned_set`，避免不同 solver 对同一个 Treasure 重复 `use_item`。
  - 结果：有效完成轮只有 `run=1 time=1:53.743`，慢于当前 `1:48.180`；第二轮在 timeout 时取消，`finished=false runs=2 average=1:46.787` 不是有效成绩。
  - 同轮输出 `maze_multi chunks=30 nodes=1024`、`maze_multi solve_done gold=9863168 time=113.72 solve_time=94.97`；早期 `game_time=60.283` 时 `gold=4,390,912`，低于请求 `625` 类似区间的 `gold≈4,915,200`。
  - 根因判断：唯一负责权减少了重叠竞争，但也让部分 solver 在 Treasure 不属于自己时空等；失去的并发抢宝收益大于减少重复 `use_item` 的收益。
  - 结论：该候选已从 `.py` 回退，并重新同步正常版到 `gamesave/`；后续如果继续做负责权，不能只按初始 chunk 唯一分配，需要 dispatcher 或动态最近可达分配，并且要证明不会让 solver 长时间空等。
- 动态负责区短等待 fallback
  - 2026-06-08 请求 `627` 验证。
  - 改法：保留 `owned_set` 的 owner 优先权，但当 Treasure 位于当前 `area` 且不属于 `owned_set` 时，只等待 `0.2` 游戏秒；若 owner 没有处理，则 fallback 到原 area 逻辑，避免非 owner solver 长时间空等。
  - 结果：有效两轮 `1:48.085` / `1:38.587`，稳定均值 `1:43.336`，优于当前 `1:48.180`。
  - 同轮输出：第一轮 `maze_multi chunks=31 nodes=1024`、`solve_done time=107.71 solve_time=88.66`；第二轮 `chunks=31 nodes=1024`、`solve_done time=98.56 solve_time=79.52`。
  - 结论：保留该候选为当前默认；它不是互斥分区，而是“owner 优先 + 短等待兜底”，收益来自减少部分重复抢宝，同时保留并发处理能力。
- `owner_wait` 参数对照
  - 2026-06-08 请求 `628`：`owner_wait=0.1`，两轮 `1:51.595` / `1:48.699`，稳定均值 `1:50.147`，慢于默认 `0.2`。
  - 2026-06-08 请求 `629`：`owner_wait=0.3`，两轮 `1:48.085` / `1:48.945`，稳定均值 `1:48.515`，慢于默认 `0.2`。
  - 结论：当前保留 `owner_wait=0.2`；`0.1` 太接近原始抢宝，重复竞争收益不足，`0.3` 又开始增加 owner 等待成本。
- 近距离非 owner fallback
  - 2026-06-08 请求 `636` 验证。
  - 改法：保留 `owner_wait=0.2`，但当 Treasure 位于当前 `area` 且路径长度 `<= radius // 2` 时，不再等待 owner，直接由当前 solver 处理。
  - 结果：两轮 `1:55.898` / `1:47.298`，稳定均值 `1:51.598`，慢于当前默认 `1:43.336`；同轮 `solve_time` 为 `97.57` / `88.58`，也慢于 request `627` 的 `88.66` / `79.52`。
  - 结论：只按当前 solver 距离放开近距离抢宝会增加重复竞争和路径扰动，不保留；代码已回退并重新同步正式版到 `gamesave/`。
- 极近距离非 owner fallback
  - 2026-06-09 请求 `699` 验证。
  - 改法：保留 `owner_wait=0.2`，仅当 Treasure 位于当前 `area`、不属于 `owned_set`，且当前 solver 到 Treasure 的路径长度 `<=3` 时立即处理；其余非 owner 仍等待 `0.2` 秒。
  - 结果：首轮完成 `1:52.571`，`explore_done time=9.71`，`solve_done time=112.54 solve_time=92.95`，明显慢于当前默认 `1:43.336`；第二轮早期已被主动停止，`finished=false runs=2 average=1:39.071` 不作为成绩。
  - 结论：把近距离放开从 `radius // 2` 收窄到 `<=3` 仍会退化；下一步不要继续按固定距离阈值抢宝，应改成真正的动态负责权 / dispatcher，或先做更细 solver 竞争探针。
- 距离编码等待
  - 2026-06-09 请求 `700` 验证。
  - 改法：不再用固定 `owner_wait=0.2` 等待全部非 owner Treasure，而是按 `path` 长度给 owner / non-owner 分别计算等待时间，试图让近距离 solver 更早接管。
  - 结果：首轮完成 `1:51.367`，`solve_done time=111.34 solve_time=92.21`，明显慢于当前默认 `1:43.336`；第二轮早期已主动停止，取消摘要不作为成绩。
  - 结论：把等待时间编码成路径长度仍会退化，说明问题不是单个 solver 的静态距离阈值，而是缺少真正的动态派发 / 最近可达判定；后续不要继续调 `owner_wait_per_step` / `non_owner_wait_per_step` 这类参数。
- solver 竞争探针
  - 2026-06-09 请求 `702` 验证。
  - 改法：临时在 `solve_maze_in_area()` 内统计每个 solver 的 `owned` / `fallback` 命中、累计等待、路径长度和 Treasure 变化次数；探针后已从 `.py` 回退，并重新同步正式版到 `gamesave/`。
  - 结果：探针首轮 `1:55.071`，因计数和输出开销明显慢于默认，不作为成绩；同轮 `solve_done time=115.04 solve_time=94.11`。
  - 聚合：30 个 solver 共 `374` 次处理，`owned=290`、`fallback=84`，fallback 占 `22.5%`；14 个 solver 完全没有 fallback，9 个 solver fallback `>=5`，1 个 solver 只有 fallback 没有 owned 命中。
  - 路径：总路径均长 `7.95`，owned 均长 `7.86`，fallback 均长 `8.26`，最大路径 `14`，Treasure 移动前变化次数 `0`。
  - 结论：fallback 并不主要慢在“距离更远”，而是少数 chunk / owner 分配与实际 Treasure 时序错位；下一步应研究 chunk 生成顺序、owned_set 覆盖和开局中心分布，不再做全局等待或距离函数微调。
- arrival-weighted owner 重分配
  - 2026-06-09 请求 `707` 验证。
  - 改法：保持 center、radius、`owner_wait=0.2` 和每个 solver 的可通行 `node_set` 不变；先收集所有 chunk，再把重叠区域节点的 owner 改为 `approach_len + node_dist` 最小的 solver，试图让预计更早到位的 solver 负责重叠 Treasure。
  - 结果：两轮 `2:06.874` / `2:03.867`，稳定均值 `2:05.371`，明显慢于当前默认 `1:43.336`；第一轮 `explore_done time=9.39`、`chunks=31`、`solve_done time=126.6 solve_time=100.2`。
  - 结论：静态按到位成本重算 owner 会把重叠区所有权推向更靠近 root 的 solver，导致远端 center 的有效 owned 命中不足，整体 solve_time 退化；代码已回退并重新同步正式版到 `gamesave/`。后续不要继续做 `approach + dist` 这类静态 owner score，除非同时改变 solver 开局位置或引入真正动态 dispatcher。
- 共享 `claimed_treasures` 去重
  - 2026-06-09 请求 `708` 验证。
  - 改法：保留当前 owner 优先 + `0.2` 短等待 fallback，但每个 solver 准备追某个 Treasure 前先把该 Treasure 坐标加入共享 `claimed_treasures`，其他 solver 看到同坐标已被 claim 时继续等待，试图减少多个 solver 同时追同一个 Treasure 的重复竞争。
  - 结果：两轮 `1:55.195` / `1:56.835`，稳定均值 `1:56.015`，慢于当前默认 `1:43.336`；第二轮 `explore_done time=9.44`、`chunks=30`、`solve_done time=116.16 solve_time=96.91`。
  - 结论：简单共享 claim set 会把重复竞争换成更多空等，且不能判断当前 claim 是否由真正最近 / 最快可达的 solver 持有；代码已回退并重新同步正式版到 `gamesave/`。后续不要做“同坐标全局加锁”式 dispatcher，除非 claim 选择同时考虑当前 solver 位置和可取消 / 可抢占。
- solver 路径前缀 launcher 分组
  - 2026-06-09 请求 `717/718` 验证。
  - 改法：不改 `radius=14`、`owner_wait=0.2`、`owned_set` 和 Treasure 处理逻辑；先按 root 到 solver center 的前 `6` 步路径前缀分组，派 launcher 走到共同前缀锚点，再从锚点 `spawn_drone()` 对应 solver，试图减少多个 solver 重复走同一段开局路径。
  - 请求 `717` 先暴露运行时限制：游戏脚本环境没有 `tuple()`，`tuple(prefix)` 直接 runtime error；修成整数 key 后继续验证。
  - 请求 `718` 两轮有效成绩 `2:10.799` / `2:03.398`，稳定均值 `2:07.099`，明显慢于当前默认 `1:43.336`。第一轮 `explore_done time=10.18`、`chunks=30`、`launchers=3`、`solve_done time=130.57 solve_time=99.73`。
  - 结论：launcher 分组把 root 共同前缀迁移换成额外 launcher 调度、spawn 占位和 solver 启动延迟，首金和 solve_time 都退化；代码已回退并重新同步正式版到 `gamesave/`。后续不要按“固定前缀 launcher / 分组 spawn”继续做 solver 开局调度，除非能证明不增加活跃 drone 占位且不推迟首金。
- 主无人机前缀锚点批量 spawn
  - 2026-06-09 请求 `720` 验证。
  - 改法：不再额外生成 launcher drone；先收集所有 chunk，按 root 到 solver center 的前 `6` 步路径分组，由主无人机依次走到每个前缀锚点，直接在锚点批量 `spawn_drone()` 对应 solver，再返回 root 处理下一组，试图避免 request `718` 的 launcher 占用无人机槽问题。
  - 结果：首轮 `2:06.868`，明显慢于当前默认 `1:43.336`；同轮 `explore_done time=8.64`、`chunks=31`、`spawn_groups=2`、`solve_done time=126.85 solve_time=89.9`。第二轮中途停止，`finished=false runs=2 average=2:00.452` 是取消摘要，不作为成绩。
  - 结论：即使不占用额外 launcher drone，主无人机串行走前缀锚点仍会推迟 solver 启动和首金；前缀共享节省的路程吃不回批量调度延迟。代码已回退并重新同步正式版到 `gamesave/`。后续不要按“主机巡回锚点批量 spawn”继续做开局调度。
- root-first chunk 生成顺序
  - 2026-06-09 请求 `721` 验证。
  - 改法：只把 `maze_chunking()` 的 chunk 遍历从叶子到根改为从 root 向外，保持 `radius=14`、`owner_wait=0.2`、owner/fallback 和 solver 逻辑不变，试图让中心区域先启动并降低首金延迟。
  - 结果：`explore_done time=9.7` 后一直没有正向金币增长；到停止前 `game_time≈167.846` 仍 `gold=0`，最终 `finished=false runs=1 average=2:48.557` 是取消摘要，不作为成绩。
  - 结论：root-first 会让先覆盖的中心 owned/area 分布破坏外圈 solver 的有效追宝，直接卡在无金币进展；代码已回退并重新同步正式版到 `gamesave/`。后续不要把 chunk 顺序简单改成 root-first。
- 探图分支局部抢宝
  - 2026-06-09 请求 `722` 验证。
  - 改法：每个探图分支结束并拿到自己的局部 `paths` 后，先把局部路径建图并尝试追当前 Treasure；Treasure 不在局部图或短时间没有命中时退出，再让主流程收集完整地图并进入原 `maze_chunking()` 兜底，目标是复用探图结束时已经分散到远端的位置，减少所有 solver 从中心重走的开局迁移。
  - 结果：早期只获得 `gold=65536` 后长期停滞；到主动停止前 `game_time=249.845` 仍无新增金币，`finished=false runs=1 average=4:10.754` 是取消摘要，不作为成绩。结束输出 `maze_multi chunks=28 nodes=975`，低于默认完整探图的 `1024` 节点。
  - 结论：探图分支局部抢宝会干扰完整地图收集；局部命中率不足以覆盖它对全图 solver 启动的延迟。代码已回退并重新同步正式版到 `gamesave/`。后续不要让 explorer 在返回路径前抢宝，除非能保持完整 `nodes=1024` 且不延迟主流程收图。
- 单一 graph-center solver root
  - 2026-06-09 请求 `723` 验证。
  - 改法：完整探图后用两次 BFS 估算当前迷宫图的直径中心，主机只沿完整图路径移动一次到该 `solver_root`，再从这个 root 生成所有 solver；owner/fallback、`radius=14` 和 chunk 逻辑不变，目标是减少所有 solver 的平均开局迁移。
  - 结果：首轮 `1:58.275`，慢于当前默认 `1:43.336`；同轮 `explore_done time=8.95`、`solver_root=(13,17) time=27.58`、`chunks=30 nodes=1024`、`solve_done time=117.9 solve_time=87.27`。第二轮主动停止，`finished=false runs=2 average=1:31.843` 是取消摘要，不作为成绩。
  - 结论：虽然完整探图节点数保持 `1024`，但 BFS 估中心和主机移动到新 root 会把 solver 启动推迟约 `18s`，没有换回足够的 solve_time 收益。代码已回退并重新同步正式版到 `gamesave/`。后续不要做单一 solver root 重选，除非 root 选择能零额外移动或在探图阶段自然落位。
- 静态 chunk 形状筛选
  - 2026-06-09 `.codex/tests/maze_chunk_static_screen.py` 用开放 `32x32` BFS 树代理比较 `shift/radius/order` 的 chunks、approach、owned_min、overlap 和 fallback exposure，只用于筛掉静态几何方向，不作为真实 Treasure 时序模型。
  - `timeout 60s python3 .codex/tests/maze_chunk_static_screen.py` 约 `5.4s` 完成。
  - 结果：root-order 候选纸面分数更好，但 request `721` 已证明 root-first 会卡到 `gold=0`；小半径 leaf 候选如 `shift=9 radius=10` 纸面 chunks 合格，但与已失败的 `radius=12` 低金币卡死同向；`shift>radius` 的近当前候选虽然可把 proxy chunks 拉到 `30`，但触发节点不保证在 solver area 内，结构风险高。
  - 结论：静态 chunk 形状本身不足以进实机。后续若继续 Maze，只剩真正动态 dispatcher / 可抢占负责权 / 不推迟首金的自然落位 solver 调度；不要继续做 root-first、半径微调、静态 owner score 或固定前缀开局搬运。
- 动态 dispatcher 上界筛选
  - 2026-06-09 `.codex/tests/maze_dispatcher_ceiling_screen.py` 用当前 `radius=14`、leaf-first chunk 规则在开放 `32x32` BFS 树代理上比较当前 owner 分配与“免费完美最近覆盖 solver dispatcher”。
  - `timeout 60s python3 .codex/tests/maze_dispatcher_ceiling_screen.py` 约 `2s` 完成；模型输出 `chunks=38`，比真实随机迷宫常见 `29~32` 偏多，因此只作为上界筛选，不作为实机时间预测。
  - 结果：`owner_route_avg=22.015`、`nearest_route_avg=13.389`、`route_save_ratio=39.1832%`、`owner_not_nearest_rate=89.0078%`、`avg_covering_solvers=12.664`。
  - 结论：免费完美 dispatcher 的理论空间存在，说明 Maze 不是只能靠局部微调；但这个结果假设零协调成本。request `700` 已证明距离编码等待会退化，request `708` 已证明简单 claim 锁会把重复竞争换成空等，所以当前不改 `lb_maze.py`。后续只有能在不增加共享状态等待、不推迟首金的前提下接近“最近可达 solver”的结构，才进入实机。
- 静态最近 owner / dispatcher policy 筛选
  - 2026-06-10 `.codex/tests/maze_dispatcher_policy_screen.py` 先用反编译 `BushPlant.GenerateHedgeMaze()` 逻辑复刻“随机起点 DFS 生成迷宫树，再从中心 BFS chunking”的 game-like 代理；该代理 `chunk_count avg=30.5 min=28 p50=31 max=33`，贴近真实常见 `29~32`。
  - 同脚本对比当前 `owned_set + owner_wait=0.2 fallback`、静态最近 owner，以及免费 perfect dispatcher。game-like 代理结果：`static_nearest_owner_wait ratio_avg=0.919 p10=0.889 p50=0.921 p90=0.947`；perfect dispatcher 在该简化事件模型里同为 `0.919`。
  - 结论：静态最近 owner 有小幅纸面空间，且不需要 per-claim 共享锁；但它只解释约 `5%~11%` 的 route 代理收益，不足以解释当前到 `1.2x` 的结构差距，也远小于开放图上界。游戏执行态恢复后可短跑一次，但不能把它当作 Maze 主攻结构；主攻仍应是低成本动态负责权、自然落位 solver 或能减少首金/重复竞争的大结构。
- 非 owner 等待策略网格筛选
  - 2026-06-10 `.codex/tests/maze_wait_policy_grid_screen.py` 继续用 game-like DFS 迷宫树，额外把“多个 solver 在 Treasure 被赢家处理前已经出发”的重复追宝计入 busy / route 成本，避免免费 dispatcher 模型过度乐观。
  - 命令：`timeout 60s python3 .codex/tests/maze_wait_policy_grid_screen.py`，约 `20.5s` 完成；模型 `chunk_count avg=30.6 min=28 p50=31 max=33`。
  - 结果：最佳 `rank_0.05` / `dist_0.10` 只有 `ratio=0.998`，约 `0.2%` 代理收益；`nearest_0.2` 为 `ratio=0.999`；`current_0.4` 退化到 `1.002`。
  - 结论：固定等待函数、距离 rank、静态 nearest 等低通信等待策略都没有足够 margin；不改 `lb_maze.py`，也不在游戏恢复后优先短跑这类等待网格候选。Maze 后续只接受比“调等待”更大的结构，例如真正可取消 / 可抢占 dispatcher，或者不推迟首金的自然落位 solver。
- 保守 owner 重分配筛选
  - 2026-06-10 `.codex/tests/maze_owner_preserve_reassign_screen.py` 继续使用 game-like DFS 迷宫树和重复追宝 busy 成本；保持当前 `radius=14`、chunk `area`、路径缓存和 `owner_wait=0.2` 不变，只把重叠节点从 leaf-first owner 改给更近 solver，并给每个原 owner 保留最少 owned 节点，避免 request `707` 那类远端 solver 被掏空。
  - 命令：`timeout 60s python3 .codex/tests/maze_owner_preserve_reassign_screen.py`，约 `18.9s` 完成；`python3 -m py_compile .codex/tests/maze_owner_preserve_reassign_screen.py` 通过。
  - 结果：模型 `chunk_count avg=30.6 min=28 p50=31 max=33`；最佳 `preserve_12` 只有 `finish ratio=0.997`，约 `0.3%` 代理收益；其他 `preserve_1/4/8/16/24/32` 仅 `0.998x~0.999x`；每张图平均改 owner 约 `74~126` 个节点，但 duplicate 和 route 基本不降。
  - 结论：不改 `lb_maze.py`，不实机保守 owner 重分配。即使避免了静态 owner score 的明显掏空问题，收益也只有噪声级；Maze 后续不要继续做“只改 owned_set、area/path 不变”的静态重分配。
- 少量全图 dispatcher 筛选
  - 2026-06-10 `.codex/tests/maze_global_dispatcher_count_screen.py` 筛“用 `4/8/16` 个全图路径缓存 solver 替代约 `30` 个半径 chunk solver”的结构；对照包括固定几何中心和 farthest-point 中心上界。
  - 命令：`timeout 60s python3 .codex/tests/maze_global_dispatcher_count_screen.py`，约 `60s` 内完成；`python3 -m py_compile .codex/tests/maze_global_dispatcher_count_screen.py` 通过。
  - 结果：game-like DFS 迷宫树下，即使 `build_node_cost=0.00` 把全图 path-build 设为免费，`fixed_4/fixed_8/fixed_16` 也分别为当前 `6.732x / 4.175x / 2.054x`；farthest-point 上界也为 `7.610x / 4.132x / 2.206x`。`build_node_cost` 提高到 `0.10` 时结论不变，`fixed_16` 仍约 `2.053x`。
  - 结论：不改 `lb_maze.py`，不实机少量全图 dispatcher。减少 solver 数会让每个 Treasure 的负责中心太远，损失的并发和路径成本远大于减少重叠 chunk 的收益；后续不要再做 `4/8/16` 个全图 solver 或固定几何 dispatcher，除非同时改变 Treasure 收宝模型。
- 自然落位 seed solver 上界筛选
  - 2026-06-09 `.codex/tests/maze_natural_seed_solver_screen.py` 检查一个偏乐观的自然落位上界：假设探图的 8 个 seed 位置和中心位置都能在完整地图已知后免费派出 solver，且忽略 finished explorer 不能复用、保活 explorer 会延迟 `wait_for()`、缺少通信和 drone slot 压力等真实限制。
  - 命令：`timeout 60s python3 .codex/tests/maze_natural_seed_solver_screen.py`，约 `2.8s` 完成；`python3 -m py_compile .codex/tests/maze_natural_seed_solver_screen.py` 通过。
  - 结果：模型 `chunk_count avg=30.60 min=28 p50=31 max=33`；solver 到 center 的起步距离从当前中心派发的 `avg=164.537 p90=331 max=572`，在自然 seed 上界下降到 `avg=30.454 p90=66 max=219`，但完整事件模型只从 `current_finish=4846.796` 到 `natural_finish=4624.321`，`ratio=0.954`；首个 Treasure 确实从 `180.645` 提前到 `45.119`，但 route / duplicate 几乎不变。
  - 结论：不改 `lb_maze.py`，不实机自然落位 seed solver。即使把最难的运行时限制全部忽略，这条谱系也只有约 `4.6%` 上界收益，远不足以解释当前到 `1.2x` 的结构差距；后续不要再按“复用 explorer 位置 / 从 seed 派 solver / 换 solver 起点”推进，除非同时改变 Treasure 处理模型，而不是只减少开局到 center 的路程。
- 短竞价 dispatcher 筛选
  - 2026-06-10 `.codex/tests/maze_bid_dispatcher_screen.py` 比较当前 `owner_wait=0.2` 与“同一 Treasure 出现后，覆盖它的 solver 在极短窗口内发布距离 / 预计完成时间，只让最优 bid 出发”的候选；该路线不同于已失败的共享 `claimed_treasures`，因为不是谁先 claim 谁持有，而是等一个短窗口后选最优。
  - 命令：`python3 -m py_compile .codex/tests/maze_bid_dispatcher_screen.py` 通过；`timeout 60s python3 .codex/tests/maze_bid_dispatcher_screen.py` 约 `12.6s` 完成。
  - 结果：game-like DFS 迷宫树 `chunk_count avg=30.6 min=28 p50=31 max=33`；当前 `finish=4578.144`；`bid_0.02 finish=4557.608 ratio=0.996`，`bid_0.05 finish=4566.638 ratio=0.997`，`bid_0.10 finish=4581.687 ratio=1.001`；bid 路线把 `dup` 从约 `69.864` 压到 `0`，但每次 Treasure 的竞价等待会快速吃掉去重收益。
  - 结论：不改 `lb_maze.py`，不实机短竞价 dispatcher。它证明“可取消 / 可抢占 dispatcher”仍是正确结构方向，但单纯每个 Treasure 等一个全局竞价窗口的收益只有噪声级；后续 Maze 需要的是不额外等待 Treasure 周期的动态分配，而不是固定 bid window。
- 诊断计数删除候选
  - 2026-06-10 代码候选：删除只服务阶段日志的 `edge_count`、`chunk_count` 及 `explore_done edges=` / `chunks=` 输出字段；保留 `explore_done time`、`nodes`、`gold` 进度、`solve_stall` 和 `solve_done`。
  - 这不改变探图、`maze_map` 构建、chunk 生成、owner/fallback、solver 路径或 Treasure 处理；只减少探图合并边和 chunk 创建时的计数维护。
  - 验证：`python3 -m py_compile scripts/leaderboard/lb_maze.py` 通过。真实游戏当前仍为 `game_tick=0`，暂未能跑完成轮；文件头成绩不更新。
  - 结论：这是多机 Maze 主结构内的管理成本候选。游戏恢复后短跑确认；若需要重新观察 edges / chunks 分布，则临时恢复诊断计数。

## 下一步优化方向

- 压缩 `main9()` 探图阶段：
  - 减少重复边记录和无收益 branch drone。
  - 优先让无人机先到区域锚点，再开始全图探图。
  - 记录探图完成时的 `edges`、`nodes`、游戏 tick，用于判断探图是否是主瓶颈。
- 优化区域 solver：
  - 请求 `353` 证明当前优先级应转向解题阶段；单纯压探图最多只有个位数秒收益。
  - 半径 `12 / 15 / 16` 均已证伪，后续不再继续盲调 `k_center_on_tree()` 的固定半径。
  - 若继续做分区，必须把“Treasure 负责区域”和“允许寻路经过的图”分离；互斥片区不能直接剪断可通行路径。
  - 让每个无人机先到固定片区锚点，再探图 / 解题，避免所有无人机重复执行单机式全局流程。
  - 当墙消失或发现更短边时，直接走直线或局部更新路径，不继续套旧路径。
  - 请求 `625` 显示 solver 到 center 的平均 `approach` 约 `145` 步，最大 `341` 步；若要改调度，优先减少这段开局迁移，而不是继续压探图阶段本身。
  - 请求 `625` 显示每轮约 `362` 次 Treasure 处理才达到 `301` 次理论需求；请求 `626` 的初始唯一负责区已经退化，说明减少重复 `use_item` 不能以牺牲并发抢宝为代价。
  - 请求 `627` 证明短等待 fallback 有正收益；请求 `628/629` 显示 `owner_wait=0.2` 暂时优于 `0.1 / 0.3`，请求 `636/699/700` 证明固定距离阈值和路径长度等待都会退化。下一步不要继续做粗粒度等待参数或固定距离微调，应转向动态最近可达判定、dispatcher 或 solver 开局调度。
  - 请求 `702` 显示 fallback 只占约 `22.5%`，且 fallback 路径并不明显长于 owned 路径；如果不能使用通信 API，优先做离线 / 探针驱动的 chunk owner 重分配，而不是让所有 solver 更积极抢非 owner Treasure。
  - 请求 `707` 证明仅按 `approach_len + node_dist` 做静态 owner 重分配会明显变慢；owner 重分配不能只看理论到位成本，必须保住远端 center 的 owned 命中和并发度。
  - `.codex/tests/maze_owner_preserve_reassign_screen.py` 证明保住每个 solver 最少 owned 数以后，静态 owner 重分配仍只有约 `0.3%` 代理收益；后续不要再做只改 `owned_set` 的静态重分配，除非同时改变 Treasure 派发 / 可抢占模型。
  - 请求 `708` 证明共享 `claimed_treasures` 的简单全局去重也会变慢；减少重复竞争不能靠无条件加锁，否则会把并发抢宝收益换成空等。
  - `.codex/tests/maze_global_dispatcher_count_screen.py` 证明少量全图路径缓存 dispatcher 会比当前慢 `2x+`，即使全图 path-build 免费也不过线；不要再试 `4/8/16` 个全图 solver 替代 chunk solver。
  - 请求 `718` 证明固定前缀 launcher 分组会明显变慢；减少重复 root 前缀迁移不能以额外 launcher 调度和 spawn 占位为代价。
  - 请求 `720` 证明主无人机巡回前缀锚点批量 spawn 也会明显变慢；即使不占额外 drone slot，串行前缀调度仍会推迟首金。
  - 请求 `721` 证明 root-first chunk 生成会卡在无金币进展；当前叶子到根覆盖顺序不能简单反转。
  - 请求 `722` 证明探图分支在返回路径前局部抢宝会破坏完整地图收集，`nodes` 只到 `975` 且 `gold` 卡在 `65536`；复用 explorer 位置不能以延迟全图 solver 为代价。
  - 请求 `723` 证明单一 graph-center solver root 会把 solver 启动推迟到 `time=27.58`，一次性 root 重选 / 主机移动成本吃不回。
  - `.codex/tests/maze_natural_seed_solver_screen.py` 证明自然 seed 起点即使按免费上界也只有约 `4.6%` 代理收益；后续不要继续只围绕 solver 出发点 / 开局迁移做结构重排，必须改变 Treasure 分配、可抢占 dispatcher 或收宝模型本身。
- 改进进度判断：
  - 首轮未完成时看 `gold` 增速和 `progress_estimate`。
  - 第一轮完成后只用真实完成轮时间判断。
  - 两轮偏差超过 `10%` 才继续加样本。

## 旧路线内部局部捷径（2026-10-24）

### 机制预算和有限上界

当前缓存#10为42.777游戏秒。32×32、Mazes 6每次兑现32768 Gold，目标9863168对应301次兑现。满速且有Power时一个200t动作约0.032922秒，#10平均只容纳每次兑现4.32个串行动作，初始化和派发另计。该预算描述关键路径，不等于所有无人机动作之和。

采用正式模型按seed 0/1/123生成的迷宫，经当前并发探图得到完整1024节点/1023边树，再按现有radius=14、leaf-first chunk规则选路线。每seed最多取8个chunk、每chunk取中等长度与最长的两条owned中心路线，共48条；偏向长路线，只用于乐观筛选。没有沿用旧开放图或独立DFS代理。

| seed | chunk数 | 路线数 | 原往返move | 全部几何捷径免费开放时最多省move | 比例 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 29 | 16 | 336 | 132 | 39.29% |
| 1 | 28 | 16 | 346 | 192 | 55.49% |
| 123 | 31 | 16 | 354 | 136 | 38.42% |

只考虑当前不重复节点路线中几何相邻、路线索引至少跳过两条旧边的通道，以索引递增的最短路径算免费上界。所有潜在捷径同时开放、建索引和查询免费、样本偏长，均偏乐观；该比例不能外推为整轮时间改善。它只说明值得实现一个候选，再计入真实查询/解释器成本。

### 唯一候选及边界

候选位于`.codex/leaderboard-sol/maze/candidate/lb_maze.py`。新增`walk_route_with_shortcuts(center, directions)`，只为本次已选路线建立最多15个节点的索引；检查能跳过至少两条旧边的几何通道，先尝试最靠后的节点，只有`can_move()`为真才走，否则沿原下一步。实际去程单独记方向，回程按其逆向回原中心；墙只消失，因此已走过的捷径不会恢复成墙。

保持探图、radius=14、owner_wait=0.2、chunk/owned_set和Treasure处理时序逻辑。路线索引严格递增，不进入旧路线外未知格；无全图BFS、全墙扫描、共享claim或全点对预计算。原初始化路径缓存保留，新增建索引、分支、失败查询和回程记录全部进入模型计费。候选已通过游戏脚本编译并完成三seed全流程；净收益为负，不迁入真源。

### 三项时间与完整本地对照

| 类型 | 候选时间（游戏秒） | 状态 |
| --- | --- | --- |
| 本地模拟预估时间 | 117.341635 | seed 0/1/123完整均值，三次达标但均慢于基线 |
| 短时打榜测试时间 | 未取得 | 候选未部署Save0 |
| 游戏打榜时间 | 未取得 | 没有完整官方统计 |

本地场景为满级科技、32×32、最多32无人机，库存12项显式归零后仅Power和Weird_Substance各十亿，目标Gold9863168。首次原真源seed1在100万API上限处停止于42.248803预测秒、Gold2490368；提高到200万API后，在49.120776预测秒、Gold3244032、1283972次API、14.20墙钟秒处触发`RuntimeError: 输出超过100条，请减少日志`。游戏脚本每次Gold变化使用`quick_print()`，完整流程约300条。该停止属于执行限额，未作为策略失败或时间首差。

Astra提交`be51729`将日志改为有界保留最近1000条并报告丢弃数，`207d450`补每5墙钟秒的实际游戏秒/API/目标库存进度。保留原基线全部日志，在正式CLI上分seed执行；每个seed上限600万API、1200万检查点、55墙钟秒，不开启逐API大轨迹。六次运行均完成目标，分别保留303/304条输出，`output_dropped=0`，墙钟37.71～48.28秒，过程中持续有实际推进信息。该证据证明原阻塞解除，不是同seed实机精度通过。

| seed | 基线预测秒 | 候选预测秒 | 候选/基线 | 基线→候选move | 基线→候选can_move |
| --- | ---: | ---: | ---: | --- | --- |
| 0 | 102.337708 | 113.860902 | 1.1126× | 11315→10803 | 10110→10447 |
| 1 | 106.051803 | 117.578125 | 1.1087× | 10894→10382 | 9662→10019 |
| 123 | 107.617080 | 120.585879 | 1.1205× | 12833→12369 | 10005→10400 |

基线均值105.335530秒，候选117.341635秒，整体慢11.40%。候选平均每轮少496次move（约4.25%），多363次can_move；平均解释器tick由12407373升到14374406，约增15.85%。探图时间基本相同，solver均时由87.631升到99.798秒。实际省下的移动远小于免费全开几何上界，当前路线建索引、局部判断和回程记录的成本没有回本；不能只凭move减少宣称更快。

结论：仅此一个候选不进入实机，不改正式脚本，不更新其历史游戏打榜时间。后续若重开局部捷径，必须先给出能覆盖索引/查询/回程成本的新预算或复用结构；本轮不继续微调同一实现。按研究队列转向下一榜。

原真源SHA256：`4370b14de86aa58b7307fa79cd820d79f70c86e86a01d99ac77b5d43e0507301`；唯一候选SHA256：`679e5ac924ca2dc3305341c30fce92e9006ca78cf1d8c4704bac67d678d16d26`。游戏指纹沿用[当前规则](current_game_rules.md)的Core/Utils/resources三项。原始场景、分行迷宫样本、`route-bound.json`、历史截断报告及`full-baseline/`、`full-candidate/`六份完整报告/进度保存在`.codex/leaderboard-sol/maze/`；`comparison.json`记录汇总，`three-times.json`只填候选模拟均值，短时与完整游戏打榜时间保持`null`。
