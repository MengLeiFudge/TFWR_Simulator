# lb_cactus_single

## 2026-11-03：新版完整统计20.038333秒

Steam build26385848。沿用此前正式执行逻辑，只刷新完整轮时间注释；执行AST不变。游戏同seed模拟request234为20.19秒，相同源码、研究、库存和seed 1的本地完整时间为20.191721040秒，差+0.001721040秒。simulate只输出到0.01秒，不据舍入值声称tick完全一致。

request250正常结束官方完整360轮，均值**20.038333333秒**，范围17.084–23.717秒。三类时间为**20.191721040 / 未另开短时统计 / 20.038333333**；同seed模拟另列，不充当短时打榜。正式榜使用加密随机源，其均值与固定seed的差异不是模型误差。游戏输出无警告。BepInEx与Unity新增日志无Error/Exception；终态按同ID回idle后逐字恢复临时存档覆盖，结果页已自动确认。

Steam公开账号行在2026-11-03T05:05:46.097698+00:00查询为20.038秒、#56。这是账号跨版本历史最好；比本轮更快时不能当作本版成绩。来源：https://steamcommunity.com/stats/2060160/leaderboards/17827398/。

执行源SHA256 `a29a9a120b87fba7676223b4cf9352eb07cd8239fd4bf8efd141676067534a6b`；仅更新时间注释后的正式源`d38b3b24588373c5c474407d206465e859057b132987f485d8b7c450ed3e4d53`；完整报告`339c581fb7b6788cafa1fea45fa0fe8aad37c3fa1517e0cf7f911e51b24cf83a`。原始场景、修正前后本地报告、部署/恢复清单及双日志见本机`.codex/leaderboard-sol/game-update-revalidation/`，逐榜误差和模型边界见[新版16榜复验](game-update-validation.md)。历史下文按原游戏版本保留。本批未新增策略搜索。Implementation deviations：None。

## 2026-10-30：环绕距离选点正式完成359轮，20.055735秒

云同步恢复后，request216正常完成官方359轮，均值**20.055735376045秒**，范围16.796–23.359秒；较上一正式20.308270422535秒减少0.252535046490秒、约1.24%。仅将同反对角线选点距离改为实际8格环绕查表，插入、施肥治愈与成熟边界保持。

三类时间为**19.880114310 / 20.018226708 / 20.055735376秒**。短筛request215终态实际322轮，主动sample_limit停止；只计322条完整run，不使用含未完成轮的finished=false均值。完整request216输出361行、BepInEx及Unity各385行，无错误或警告，full_statistics及output_complete为true，结果页自动确认后回idle。

正式迁入仅改成绩注释，AST与执行候选一致。request217正式复核14个完成轮、19.950428571秒，独立保留，不替换官方完整统计；正常sample_limit产生的oracle_error不视为策略失败。idle217后按备份哈希恢复两份存档覆盖。游戏按用户要求保持开启。

执行源SHA256 `d4fea48dd3d1ff02b2de3c10afd55dccface9b5ec50553c3046e643b0b0d6620`；正式源`a29a9a120b87fba7676223b4cf9352eb07cd8239fd4bf8efd141676067534a6b`；完整报告`104d427b66eb0a5f36adcd72ea9cec081cfb2278248daf593f11ba47f886681d`。证据仍在`.codex/leaderboard-astra/cactus-single-wrap-choice/`，原始三份实机结果、部署/恢复清单和查询错误均保留。游戏兼容检查及真实执行通过；构造/模型分析工具ty零诊断。公开账号查询仍报SSL UNEXPECTED_EOF_WHILE_READING，未独立确认公开提交和新名次。Implementation deviations：公开成绩核验受网络错误阻塞。


## 2026-10-29：环绕距离选点候选，本地均值19.880114秒

当前反对角线方案选点采用普通Manhattan距离，实际`move_to`允许环绕。固定候选仅将同层选点改为8格环绕查表，保留西南插入、末三株施肥治愈及1秒自然成熟界；同层各点没有西南偏序依赖。初始化、查表和实际路线均收费，不预读随机数。

固定seed0/1/123完整模型为20.49987096 / 19.80455832 / 19.33591365秒，均**19.88011431秒**；父同seed均20.36406771秒，节省0.4839534秒、2.3765%。三组均一次成熟64株、131072 Cactus，Pumpkin消耗4096、use_item5次，无未成熟收割、负库存、错误、警告或丢输出。move284/271/266，对照300/271/282；swap158/152/143，对照161/159/143。访问顺序也改变随机值的空间分配，不把交换差额全归于路程缩短。

三类时间为**19.88011431 / 未取得 / 未取得**。准入实机后已核对R2 Preloader并经Steam启动，但Action24停在SynchronizingCloud，prepare未分配请求，后续health仍idle213、无游戏进程。尚未覆盖存档，正式20.308270秒保持。

候选SHA256 `d4fea48dd3d1ff02b2de3c10afd55dccface9b5ec50553c3046e643b0b0d6620`；完整报告`5756e2d0627b2f87313998bc035e932dca004af20ef5bb52429c0b7219bd01f6`。证据`.codex/leaderboard-astra/cactus-single-wrap-choice/`保留父源、构造/分析工具、原报告、三类时间与启动日志；两工具ty零诊断，游戏源尚未实机编译。Implementation deviations：Steam云同步阻塞实机验证。

## 2026-10-28：反对角线插入完整355轮20.308270秒

当前正式版本采用enihsyou的反对角线最近点访问与西南插入，request179官方完整355轮均值**20.308270422535秒**，较上一正式21.471645833333秒减少1.163375410798秒（5.4182%）。同源三类时间为**20.364068 / 20.848629 / 20.308270**；本地seed0/1/123，request178短筛终态实际35轮。公开账号成绩尚未独立核验，不报告新名次。

来源[enihsyou/The-Farmer-Was-Replaced](https://github.com/enihsyou/The-Farmer-Was-Replaced/tree/37a97b58e15dc60bb6aff8829eeb58293be18b39)，`cactus_single.py` blob `cbca43833b7a42398139179c8addd65a41a43a51`，全文及MIT许可已读，版权头和[许可](../../scripts/leaderboard/enihsyou_LICENSE.txt)保留。沿x+y反对角线依次扩展已排序区域，在同层选离当前位置最近的点；每株向西/南较大前驱插入，表中确认后续无需交换时省去末次跟随移动。

保留上游末三株先种后排的肥料与治愈路径：先从草取得Weird Substance，四次施肥及一次治愈均实际支付。自然成熟边界由0.97补足到末次自然种植完成后的1秒，避免把当前格成熟当作全田成熟。三seed均一次64株、131072 Cactus，未成熟收割0，库存非负；move300/271/282，swap161/159/143，measure503/496/457，use_item均5次。最终Weird Substance均255，Fertilizer12/12/11，未赠送资源或隐藏感染损失。原0.97入口适配版三seed恰好同时间，另存原报告，不替代最终1秒版本证据。

执行SHA256 `7c7ab1878922630d9efb86995ccb00bb5d3473ebb940228386ea063dee5b3bce`；正式化只改注释与换行，AST一致，正式SHA256 `b3141597b9b157b90d25dbf149bdf59fd5ae68e58c46c3e64d2bf327e074e3fb`。完整报告SHA256 `21ca6dde24133abd55d23876981554e5b9c80bd2be1715f1864e23cabfd078a2`。正式源request180复核终态34轮20.485352941秒，单列，不替换完整统计。

完整脚本、模组和Unity日志无错误、警告或资源不足；短筛sample_limit为主动停止，未完成轮不计成绩。最终idle180已逐字恢复目标与lb_start。证据`.codex/leaderboard-astra/cactus-single-diagonal/`保存原文来源、构建器、两版模型报告、acceptance、全部实机结果、部署和恢复清单。两项构建工具LSP零诊断，真实游戏编译及完整统计通过。Implementation deviations：None。

此前按行西南插入版的末段成熟问题另作固定修正：`.codex/leaderboard-astra/cactus-single-mature-insertion/`三seed均完整64株，但均值21.90009849秒慢于同批基线21.65817666秒，关闭。不能把原先两轮仅60株的时间当成有效成绩，也不以这个负例否决不同访问顺序的实现。

## 2026-10-26：当前正式版完成336轮实机统计

当前正式策略a013b1fc重新部署至已有`lb_cactus_single.py`。request100短筛最终48个完成轮均值21.3820625秒；设定至少两轮停止，但模组在发现稳定并处理取消期间继续完成了若干轮，按原始终态run逐条统计，不按预设轮数或中间42轮摘要填表。随后request101正常完成336轮官方统计，均值21.471645833333秒，显示0:21.472。两次输出完整，目标131072 Cactus达成，无游戏警告及异常；完整统计双日志无错误，结果页自动关闭并回到idle。

18:49:27 UTC查询当前Steam账号，公开榜第82名、21472ms。这个排名是实际账号记录，不是前100缓存插值。完整三类时间为21.658177（原三seed本地）/21.382063（短筛）/21.471646（完整游戏）；比#10的14.734秒仍慢约45.73%。本次只建立同版本实机证据，不把相对不同历史样本的波动声称为算法提速。

执行源SHA256为`a013b1fc641c0fa5e782fb0ad9946d7d7db55f11314f17d6ad410c4f9b9c7bfd`，正式文件仅更新完整时间注释，AST相同。原始源码、336轮结果、完整输出与BepInEx/Unity双日志、备份和公开榜查询保存在`.codex/leaderboard-astra/iteration-20261026/cactus-single-real/`。

更新注释后的正式源request102重新部署短轮复核，最终21轮均值21.031523810秒；独立保存，不替换前述短筛及完整成绩。终态回到idle后逐字恢复两份临时Save0覆盖。

## 2026-10-26：逐株西南插入未过15%收益门槛

固定8×8按行种植，每次新数与西/南前驱中的较大者交换，直到已有区域横纵非降，试图省掉整行和整列排序。实际交换后移动、回到下一种植格、维护二维表和最终有序校验全部进入解释器计费。没有重抽数字或预读随机数。

唯一seed1完整21.56242851秒，比父同seed21.999962仅省约0.438秒（1.99%），未达到事先18.6999677秒门槛。swap194→156、measure652→64，但move320→324，解释器3861→8561tick，减少交换的收益大部分被表维护和回程抵消。一次成熟64株收割131072，Pumpkin实耗4096、库存非负，无警告/失败/输出丢失；正常完成仍不代表性能准入。

关闭这个固定种植顺序与插入协议，不追加seed、调序或进入游戏。证据`.codex/leaderboard-astra/iteration-20261026/cactus-young-insertion/`保留执行源码、场景、SHA清单、原始报告与三类时间；只记录本地21.562429秒，短时/完整游戏均null。正式排序仍为上面的a013b1fc执行逻辑。

当前阶段（2026-10-24）：当前正式脚本完成3seed完整本地计费，均值21.658177游戏秒，短时打榜与完整游戏成绩尚未建立同版本记录。2026-10-23的六seed API-only对照保留为方法校准，不当作完整时间预测。优化重点转为减少排序动作。

## 2026-10-24：当前版本完整计费基线

源码SHA256：`a013b1fc641c0fa5e782fb0ad9946d7d7db55f11314f17d6ad410c4f9b9c7bfd`。显式满级8×8、Expand5/Megafarm0，Power/Pumpkin各十亿，其余库存0，目标131072 Cactus。一次seed0/1/123批次，共享墙钟20秒，每seed20万API、200万检查点，无trace；每seed本地计算约0.04–0.06秒。

| seed | 完整预测秒 | move | swap | measure | 解释器tick |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 21.874694 | 314 | 196 | 635 | 3744 |
| 1 | 21.999962 | 320 | 194 | 652 | 3861 |
| 123 | 21.099874 | 306 | 182 | 610 | 3645 |
| 均值 | 21.658177 | — | — | — | — |

三seed均一次收割达标，Pumpkin各消耗4096，无spawn或库存透支。当前三值为 **21.658177 / 未取得 / 未取得**；历史方法校准及无法归属当前源码的实机成绩不填入空缺。

当前#10为14.868秒，完整预测约为其1.457倍。当前动作序列只计move+swap、忽略全部其他成本仍需16.592688秒，故仅减少管理开销不足以达到#10；这个下界只用于候选剪枝。完整证据见 `.codex/leaderboard-sol/cactus-single/baseline/{manifest.json,baseline-seeds0-1-123.json,comparison.json,three-times.json}`。本次未改变正式排序或Save0，未运行实机。

## 2026-10-25：8×8对角目标的固定三阶段路由关闭

仅研究实际种植数字按`(x+y,x)`构造目标、同值row-major配对、Euler分色后行→列→行相邻插入的固定协议。每次swap跟随一步move，阶段和线序不搜索，规划在游戏内收费。单机三层Euler各处理64条边，不能套32机并行关键链。

已有请求35的种植后首次measure序列提供输入；它是历史种植数字序列，不是原策略某时刻的全盘快照。Sol报告三盘共4731条非时间包装API结果对齐。未启动模型、游戏或旧代理，也未重新生成随机盘。

seed0保留完整24线费用表：交换S=274，巡航C=414（含最终回位），路由动作2S+C=962；加64翻地、64种植、70初始移动、clear及收割共200动作，总1162动作，费用38.255364秒。已计解释器/查询子集另5215t，总39.11380515秒；未计成本不作为免费完整方案。仅物理动作已超过1.1×#10=16.3548，因此关闭这个固定协议，不准入实现或运行，不外推所有对角构盘均不可行。

保存时JSON曾被截断。恢复后analysis e9a5a1af合法且保留seed0完整明细；seed1/123仅保留原stdout汇总（含已计操作子集41.84435583/41.91019983秒），逐线及颜色表缺失，不标为独立复核通过，也未为恢复重跑。Astra核对16份来源SHA、seed0逐线逆序数、动作加和及位置衔接；关闭决定只依赖可审查的seed0账。

证据`.codex/leaderboard-sol/cactus-single/diagonal-budget/{analysis.json,research-note.md,three-times.json}`，note4aa30755、times eee2c8ec。该协议完整三值全null；正式版21.658177 / 未取得 / 未取得保持，正式py、模型、Save0与实机队列未改。

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

## 2026-10-23 本地模拟基线

- 实现未改：仍使用当前 `lb_cactus_single()`、`plant_and_sort_rows()`、`local_sort_after_plant()`、`sort_columns()` 与 `sort_one_way()`。
- 真实请求 35：六 seed 分别运行原策略、API 记录版和边界探针。9473 个离散 API 返回值、54 条边界观测一致；原策略与本地的最终库存均为 Cactus=131072、Pumpkin=999995904。
- seed=1：本地 API 时间 21.3601 秒，实机 tick 折算 21.9996 秒；差额含游戏解释器及验证入口开销，不用经验倍率抹平。其他五个 seed 的低估比例也在 2.84%～2.92% 内。
- 使用：`python3 -m simulator.local_simulator scripts/leaderboard/lb_cactus_single.py --seed 1`。支持轨迹与上限，范围见上方说明。
- 后续先补模拟器机制/计时覆盖，再用其筛选策略。模型预测通过后仍须真实游戏打榜，不能把本次 `simulate` 当作官方完整统计。

## 2026-10-25：种植预分区的重抽缓存约束

静态考虑用种植时的大小区间筛选减少排序，先遇到一项必要机制限制。当前Core的Cactus.OnRestart仅在本格cactusNumbers为−1时抽Next(10)，否则复用已有数字；OnFullyGrown才把当前格缓存置−1。未成熟时harvest会移除植株，但该路径没有清数字缓存。因此同格立即拔掉重种不能视为一次独立新数字，不能用每次成功率1/2给出免费连续重抽预算。

若改为成熟后再移除，必须付成熟/访问费用并处理真实连锁收获：Cactus.Harvest成熟分支调用Pop，符合邻株排序条件时可能连带删除其他成熟株，不能默认只替换一个生产格。这里没有证明所有预分区方案不可能，也没有运行候选；当前不准入基于立即独立重抽的结构。源码依据为Core.decompiled.cs的Harvest、OnFullyGrown、Pop、OnRestart；本地world.py同样保留未成熟数字缓存。这是策略预算约束，不是已确认的模型缺陷。
