# 地下Reset（fastest_underground_reset）

2026-11-08：仓库采用真实向日葵供能与增量扫雷，本地三seed原始重置目标均值11912.122406秒，尚未实机。旧版晚升Rice5/Coal3、首段采煤的完整实机13559.391秒及普通同seed对照作为历史保存。

## 当前实现

从零库存读取当前get_cost筹资，逐步发展6×6单机。保留Rice3后Coal2、Expand4后的Grass2/Trees2/Carrots2/Speed5、Mining5后的Iron2/Rice5/Coal3及付费勘探路线。随后真实支付Mining6/7/8与蘑菇、藏宝图、Quartz等前置，最终支付20000 Dynamite和200000 Bamboo解锁Underground_Leaderboard。每次unlock前复核整组成本；种子随科技变化仍实付。

Speed5后新增Sunflowers1投资。Power低于100时先筹1000：支付整田种子，测花瓣后降序收成熟向日葵，最后9株保留，保证收获时至少10株的倍率条件。解锁、种植材料、成熟、走路及后续清场全部计入，不白送Power或满科技库存。

煤仍只采每片首16层，初始Rice0的Coal10和其他资源保留原边界。Iron用Coal付费读取方向，Quartz用Iron读取距离，只认实际dig入库，并保留有限回退。扫雷仍仅按需清覆盖层；改为实际变化数字的增量直接约束，零扩展连续开格，推理停滞时正常部分结算一次，再重生。每盘新建事实，不沿用旧盘状态，不再使用子集枚举或猜测。

主要成员：`lb_fastest_underground_reset`、`ur_need`、`ur_power_stock`、`ur_mine`、`ur_i_stock`、`ur_q_locate`、`ur_dynamite_stock`、`ur_d_solve`、`ur_d_work`、`ur_d_propagate`。主流程72000游戏秒；农作7200秒，供能3600秒/64田，逐层矿采18000秒。采煤最多128片、连续8片无产出停止；Iron/Quartz保留各64片、既有探测和回退截止。扫雷最多512盘、每次覆盖准备256刀、局部和全局推理256步，连续8次找层未命中停止。没有新增Jump、爆破钻或无人机投资。

## 特殊土壤方向
当前地下Reset路线尚未投资 `Special_Soils`。该科技需要 `Rice=800`、`Bamboo=1000`，并依赖 Rice 科技；解锁后生成两层地下特殊土壤。模拟器中壤土和珍珠岩的种植增益均为 2.0，但只对种在对应地块上的作物生效，不会全局提高地上普通土壤上的产量。

| 地层 | 可获得双倍产量的作物 | 对地下Reset的主要价值 |
| --- | --- | --- |
| Loam | Carrot、Sunflower | 比较早期筹资、向日葵供能是否能收回开层和整地成本 |
| Perlite | Bamboo、Tree、Bush、Cactus | 优先验证最终 200000 Bamboo 的筹资是否值得改到地下高产田 |

必须把解锁、挖到特殊土层、整地、种植、成熟、收获及塌方/回程成本一起计入。排行榜脚本禁止 Jump，不能用跳跃到达地层的功能脚本吞掉访问成本。下一步先做有限时长的 Perlite+Bamboo 组件对照，再决定是否纳入完整地下Reset路线；在本地效率证据出来前不替换存档或进行实机验证。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值11912.122406496游戏秒 | 当前供能与增量扫雷，零库存、原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 当前版本未取得 | 历史13559.391秒，构建26462009，请求418，1轮正常结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 12568.197810635 | 实际解锁目标，done True | `final-reset-s1/report.json` |
| 2 | 11456.605092401 | 实际解锁目标，done True | `final-reset-s2/report.json` |
| 3 | 11711.564316453 | 实际解锁目标，done True | `final-reset-s3/report.json` |

地下资源快照构建26410308，基础模型字段保留26385848；本轮报告路径共同根目录为`.codex/underground-efficiency-20261108/reports/`，源码、依赖和模型指纹见[长期JSON](../underground-efficiency-validation.json)。普通Reset目标虽不强制专用资源地形，正式局仍使用加密随机源，不能由固定seed重放。首版部署SHA256及后续实机指纹均归下方历史对应版本。

## 旧版普通场景同seed对照（历史）

首段采煤旧版在普通Reset初始科技、零库存、seed1下，实机请求416完整为14311.509098242游戏秒，与当时修正后的本地模型相同到整数纳秒。704条阶段输出的离散状态和整数值一致，小数按原生0.01显示精度比较。本次供能与增量扫雷尚未做实机同seed对照，不能继承该0ns结论。

证据：`.codex/leaderboard-sol/underground-official/alignment-26462009/shallow-coal16/game-seed1/comparison.json`及原请求、部署和恢复记录。部署SHA256为`37bf8b82b571d395ebf312ae4a2dbf9dd576acf1956350851c9ad18cf2ece335`，属于旧版执行逻辑。此前Rice5请求412为15810.350362724秒、722条/0ns；Coal3请求409为15752.701420357秒、714条/0ns；按需清覆盖层请求402为16649.129798428秒、713条/0ns；Iron勘探请求399为17540.865550588秒、713条/0ns。原始资料保留，覆盖范围见[地下对照记录](../../simulator/local_simulator/underground-validation.md)。普通同seed精度与正式随机榜均值分别记录，不用差额估算模型误差。

此前Quartz定位版的请求395为19716.483046656秒。原模型少2.792106339秒，经免费地层日志定位到塌方方环误按绝对坐标过滤，修正相对偏移后585条输出及完整纳秒一致。修后Quartz版三seed为19716.483046656、21570.882220494、21212.081613928秒，均值20833.148960359秒。原始源码、修前报告与修后重放保留于`alignment-26462009/current-reset/`，三seed位于`fastest_underground_reset/quartz-prospect-cavein-model-seed1..3/`。

## 首版普通场景实机对照（历史）

正式脚本原字节，无目标缩减；显式传入Reset初始科技和零库存。普通生成与该Reset配置同样不强制特殊地形。

请求 `335` 正常结束。本地与原生simulate完整返回时间均为 **35057.738444295 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/ordinary-pair-v1/game-seed1/comparison.json`。实机脚本 SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

该Reset的原脚本整轮同seed对照已完成；其余seed为本地预测。

## 候选与已处理边界

首轮发现Grass即时再生导致Bush未种下；改为按目标实体补种。逐项筹资会消耗前项的种子资源，现最多8轮复核整组库存。普通地层可能未生成目标层，搜层256次未命中后有限clear重试，连续8次失败才停止；不能套用资源榜强制地形。

提前Speed4、Speed5、补给科技配套Speed5为第一组有限代表。seed1模型依次为32480.250879794、29090.295371570、28410.363445127秒，原版同seed为35057.738444295秒。配套Speed5的三seed均值28416.469521305秒，候选正式请求361为27638.810秒，迁入真源后的请求366为29133.641秒。不同正式盘面有波动，不能把样本差异当成同seed模型误差。

随后按实际末段dig时间比较Mining7和Mining8两个代表，新增90 Quartz、250 Mushroom及对应前置采集全额支付。seed1分别为28287.750766862和26024.006745801秒；Mining8的三seed均值25849.977463678秒，候选正式请求369为25089.868秒，迁入真源后的正式请求371为25147.408秒，两次均正常完成1轮，为该阶段正式基线。Dig固定游戏时间随1.5**Mining缩短；Speed5已是速度科技上限，不能用继续升级Speed替代这笔投资。没有枚举任意科技顺序。

同盘扫雷缓存另作独立候选：全部33个ur_d函数去前缀后与单机炸药旧版AST一致，仅迁移已验证的solve/worker缓存。三seed完整目标为26003.257059888、26377.228745892、25104.483775299秒，API次数分别与Mining8基线完全相同，只省20.749685913、12.942586547、31.270537496秒。正式请求387完整1轮26658.525秒，正常达标且双日志无错误，已有test.py/lb_start.py在同ID回idle后恢复，其他存档Python文件未变。

缓存候选部署SHA256为`02a8246c449feea20d6e44d6cedce0f029293dac222642642aca65e913ad0bad`；证据在`.codex/leaderboard-sol/underground-official/fastest_underground_reset/dynamite-cache-26462009/summary.json`及同目录完整请求、部署和restoration。此轮没有取得优于当时正式值的样本，微小模型收益也远小于盘面波动，因此未单独采用；不据此断言缓存本身导致变慢。后续Coal2/Iron2投资版保留该结构，并重新验证整轮。

Mining5后提前升Iron2/Mining6，新增50 Coal与70 Iron全部支付。三seed均值24923.910328930秒，正式388为23976.796秒，迁入复验389为25748.013秒，两轮差约7.39%；后者高于Mining8旧基线，未把首轮23976.796当作稳定收益。随后在Rice3后支付150 Rice升Coal2，降低Coal30和Iron2所需Coal50的采集成本，三seed均值进一步降到22785.575809859秒。候选390完整1轮22143.688秒，真源391完整1轮22699.482秒，相差约2.51%；该阶段采用391，比Mining8基线25147.408秒约快9.73%，比最初31535.109秒约快28.02%。两次完整请求均正常恢复。

早升Coal3曾在Rice3后的相同小田位置再付1000 Rice，seed1完整目标24690.419270700秒，慢于当时Coal2同seed23091.030955295秒约6.93%，未进实机。证据为`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-coal3-model-seed1/report.json`。当时Coal4新增4000 Rice的预估成本也高于该阶段可节省的费用，没有进入模型；此为旧结构和升级时点的边界记录，不直接判断大田、Speed5及勘探加入后的投资。

Quartz公开距离定位每次支付1 Iron；Iron少于16时先按真实采矿筹到32。先完成锚点挖掘，再读取三点的实际x/y/z和距离，枚举世界内整数坐标，允许0.01的平方距离误差。最近矿可能在不同采样点之间变化，三点一致也不作为库存证明；只计真正dig到的Quartz，连续两片无收获则回退普通逐层矿采。原型因调用游戏没有的int在8223.326768699秒停止，未进实机；改用整除舍入，并让回退继承相同截止后，当时三seed均完成原目标，均值20832.143635273秒，已包含200/146/224次勘探及筹集所耗Iron的成本。此为塌方模型修正前记录，当前修后预测见上表。

正式392完整1轮20423.736秒；真源393为22667.688秒，两次差约10.99%，因此追加394，完整1轮22108.401秒，与393差约2.47%。该阶段采用394，相对Coal2阶段22699.482秒约快2.60%，相对首版31535.109秒约快29.89%。不同正式盘面的波动明显，不能把模型三seed约8.57%的收益直接写成实机收益。部署、Core指纹、双日志和恢复证据见下方三次正式记录。

后续先准备三锚点、取消挖掘前预读的候选虽把seed1勘探次数从200降到165，dig却由74262升到75545，修前模型完整目标20357.378612241秒，高于当时同seed19713.690940317秒约3.27%。未进实机，保留先探主柱再准备其他锚点的结构；证据在`.codex/leaderboard-sol/underground-official/fastest_underground_reset/quartz-prospect-batched-model-seed1/report.json`。

Iron公开方向勘探版在Mining5/Iron2后新增Prospecting1，实际支付32 Coal；每次查询再付1 Coal，煤不足16时先按原采矿法筹到32。每片分层准备主柱，最多沿公开方向移动2×世界宽度+1次，再按真实Iron地面挖掘；None也可能表示范围无矿，不作为找到矿的证明。两片无收获回退并继承同一截止。修后三seed完整目标均值17181.191108563秒，比修后Quartz版20833.148960359秒少约17.53%，包含额外煤与解锁成本。

普通同seed请求399另经完整时间和状态校准。正式候选400为16805.039秒，迁入真源后的401为18140.125秒，两次均正常完成1轮，差约7.94%。该阶段采用401，比前版22108.401秒约快17.95%，比同构建首版31535.109秒约快42.48%；以上为不同正式随机样本的完整成绩。双日志、实际达标与存档恢复证据分别保留，不由普通seed预测推算正式排名。

扫雷按需清覆盖层只改资源主循环和`ur_d_dig_target`：不再先把36柱全部挖到目标层，而在实际开格前有限清理本柱；仍核对真实z与Grounds.Dynamite，保留数字推理、猜测、结算、缓存和完整目标。三seed扫雷前523/527/521条输出分别与前版完全相同，整轮各省891.735752160、930.248119999、918.213190235秒，均值少5.32%。seed1 dig由71121降到66943，move由53761降到48885，clear和measure次数不变；减少的覆盖层开挖与移动解释了主要收益。

普通同seed请求402完整0ns误差。正式403为15311.563秒，真源复验404为16670.354秒，各完整1轮，两次差约8.87%。该阶段采用404，比前版18140.125秒约快8.10%，比同构建首版31535.109秒约快47.14%。不将超过模型收益的随机样本差异归为算法提速；完整正式成绩与三seed预测仍独立保存。

晚升Coal3只在主stages增加一步：先完成6×6、Speed5、Mining5和Iron2，再筹1000 Rice升级，随后才解锁Prospecting。前版seed1勘探前32 Coal筹备约814秒，而这个时点筹齐升级Rice用了约142.054秒。煤升级同时影响产量及矿层数量，新增种植、成熟、清场和后续Iron/Quartz筹资全部计入；不能只用产量倍率估算整轮。修后三seed完整均值15544.141791522秒，比前版16267.792087765秒少约4.45%，三个seed均完成原目标。seed1 dig66943→62365、move48885→47189；勘探次数因路线与库存改变而上升，完整时间仍降低，没有从单阶段差额直接推算整轮收益。

普通同seed请求409为15752.701420357秒，714条输出及完整纳秒匹配。正式候选410为15400.750秒，真源复验411为15440.645秒，各完整1轮，两次差约0.26%。该阶段采用411，比前版16670.354秒约快7.38%，比同构建首版31535.109秒约快51.04%。双日志无新增错误，目标正常完成并按同ID回idle后恢复已有脚本。

随后利用前置采矿积累的Block评估Rice升级。带观测分支的本地前缀在Mining5/Iron2后有4530 Block，只作库存预算；Rice4/5合计3000 Block，Rice6还需4000，因此先选Rice5。主stages只在Coal3前增加Rice5，其余采集逻辑不变。三模型seed均未新增Block采集调用，实际升级支付仍全额计入；库存不足时原ur_need会补齐。预算证据为`.codex/leaderboard-sol/underground-official/fastest_underground_reset/investment-budget-after-mining5/report.json`，不把带观察分支的前缀时间当作原字节精度证据。

Rice5首seed的稻米采集小计由1212.815626876降到663.931504287秒，但后续流程变化使整轮从15752.701420357升到15810.350362724秒。因此补齐另外两个seed，得到14888.956986669、14760.400296819秒；三seed均值15153.235882071秒，比前版15544.141791522秒少约2.52%。没有把单一阶段收益直接当作完整策略收益。新等级另经请求413短方法确认：默认get_cost分别返回1000/2000 Block，解锁后库存3000→2000→0，4条输出和0.139588856秒完整时间均与模型相符。

候选原字节普通同seed请求412完整15810.350362724秒、722条/0ns。正式414为14467.709秒，真源415为15255.250秒，各完整1轮，两次差约5.44%。该阶段采用415，比前版15440.645秒约快1.20%，比同构建首版31535.109秒约快51.62%。两次均正常达标、双日志干净、同ID恢复，正式随机样本与本地三seed分别保留。

随后仅修改`ur_mine`：普通CoalFeature只在每轮地层的首chunk、相对深度2–15生成；Rice开启后循环含不产煤的后续chunk。因此采煤在首16层后正常clear重生，保留最初Rice0时的Coal10、其他资源和原重试/截止。清场保留实际库存，所有实际动作和后续筹资照常计入。三seed完整目标14311.509098242、14107.939660990、13787.089433938秒，均值14068.846064390，比前版15153.235882071少约7.16%。首seed dig64970→60645、move46328→42895；其他seed的动作计数和后续路径不同，不能仅靠计数相减推算整轮收益。

首段采煤减少附带Block，三个seed都额外调用Block2000采集，首seed约338.05秒；即使计入补料，完整目标仍改善。此前Rice5阶段“已有Block足够”的预算仅适用于当时采矿结构，不能继续当作当前免费升级的依据。普通同seed请求416核对704条输出与14311.509098242秒完整时间，误差0ns。正式候选417为13737.473秒，迁入真源后418为13559.391秒，各完整1轮，两批差约1.30%。当前采用418，比前版415少约11.12%，比同构建首版少约57.00%；这两个比例只比较实际随机样本，模型收益另列。双日志无新增错误，同ID恢复已有脚本。

## 2026-11-08：供能与扫雷路线选择

同条件新鲜基线三seed14311.509098242、14107.939660990、13787.089433938秒，均值14068.846064390。先独立比较两个代表：向日葵供能seed1完整13711.130721568秒；增量扫雷seed1完整13038.301941136秒。两项各自通过完整原目标后再组合，没有用阶段费用简单相加预测。

最终合并源码三seed全部实际解锁，均值11912.122406496秒，缩短15.33%。供能新增前置和所有筹资、部分结算降低的单盘奖励以及额外重生均包含。最终自审移除旧扫雷常量、保留error优先级后，使用相同75秒现实预算再次完成三seed；上表仅使用最终版本结果。

爆破钻需要12M Dynamite而最终只需20k，投资明显不回本，直接关闭。没有扩展任意科技顺序枚举；后续优先预算地上伴生与产量投资的完整筹资闭包。

## 当前静态检查与后续

当前源码AST与最终三份冻结执行副本相同（仅时间注释不同），游戏语法与入口结构检查通过。真实外部类型桩的字节副本ty LSP为10项错误、23项提示：桩缺Underground_Leaderboard、竹子/藏宝图measure联合类型，以及新增向日葵花瓣索引的2项联合类型诊断；旧Soot数字比较的2项已随算法替换消失。未修改游戏类型桩，未写成LSP全通过。

当前候选只通过所列本地完整目标。旧正式段落中的当时“当前”源码、AST和实机通过结论均属于该段历史版本，不覆盖本次供能与扫雷改法。未启动游戏、写Save0、更新正式成绩或推算公开排名；下一阶段按[共用方法](README.md)继续研究结构收益。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:355 -->

请求355完整正常结束，共1轮。官方最终日志均值为 **525:35.109（31535.109游戏秒）**；逐轮日志重算均值为31535.109000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。当前源码SHA256：`8cce2ed22c106fc544ea59df52ff5bdfe65d18627b7f0cd94df191a953cee048`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：supply-speed5-26462009

<!-- official:supply-speed5-26462009:361 -->

请求361完整正常结束，共1轮。官方最终日志均值为 **460:38.810（27638.810游戏秒）**；逐轮日志重算均值为27638.810000000秒，保留两者的显示舍入口径。

同构建前版完整均值31535.109000000秒/1轮；当前正式均值27638.810秒/1轮，缩短约12.36%。Expand4后依次准备Grass2、Trees2、Carrots2和Speed5，继续读取真实get_cost支付各阶段资源，其他阶段与采集逻辑不变。

部署源码SHA256：`b974caa96347c3149631f02fc09c8a491a04f323eed26298a8271ee818642d43`。当前源码SHA256：`a6a149a2d1d00162d81e2d0bdd6bd1d2df0350ca22eefcaeaefb735d4cae1e06`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：supply-speed5-current-26462009

<!-- official:supply-speed5-current-26462009:366 -->

请求366完整正常结束，共1轮。官方最终日志均值为 **485:33.641（29133.641游戏秒）**；逐轮日志重算均值为29133.641000000秒，保留两者的显示舍入口径。

同构建前版完整均值31535.109000000秒/1轮；当前正式均值29133.641秒/1轮，缩短约7.62%。Expand4后依次准备Grass2、Trees2、Carrots2和Speed5，继续读取真实get_cost支付各阶段资源，其他阶段与采集逻辑不变。

部署源码SHA256：`a6a149a2d1d00162d81e2d0bdd6bd1d2df0350ca22eefcaeaefb735d4cae1e06`。当前源码SHA256：`a640359cc042414b04db423c29a94582d6200d524c364b0f5241e12b05ebc6f3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-mining8-26462009

<!-- official:late-mining8-26462009:369 -->

请求369完整正常结束，共1轮。官方最终日志均值为 **418:09.868（25089.868游戏秒）**；逐轮日志重算均值为25089.868000000秒，保留两者的显示舍入口径。

同构建前版完整均值29133.641000000秒/1轮；当前正式均值25089.868秒/1轮，缩短约13.88%。现有补给Speed5后继续付90 Quartz升Mining7，Mushrooms2后付250 Mushroom升Mining8；新增资源全额计入整轮，减少末段dig的固定游戏时间。

部署源码SHA256：`748e2425fcfd3efa875e25de4909dfc5c38132b627c9767396d2317c413b2b07`。当前源码SHA256：`3269550c84964efa4a7eaae37ad5ca15ec9f3208665f5e3e02b52dcb0380a469`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-mining8-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-mining8-current-26462009

<!-- official:late-mining8-current-26462009:371 -->

请求371完整正常结束，共1轮。官方最终日志均值为 **419:07.408（25147.408游戏秒）**；逐轮日志重算均值为25147.408000000秒，保留两者的显示舍入口径。

同构建前版完整均值29133.641000000秒/1轮；当前正式均值25147.408秒/1轮，缩短约13.68%。现有补给Speed5后继续付90 Quartz升Mining7，Mushrooms2后付250 Mushroom升Mining8；新增资源全额计入整轮，减少末段dig的固定游戏时间。

部署源码SHA256：`3269550c84964efa4a7eaae37ad5ca15ec9f3208665f5e3e02b52dcb0380a469`。当前源码SHA256：`7f4cf18eff4fcdb25ed33d79592023a42a8d996b0df800015279d7f4a79f5934`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-mining8-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：early-iron2-26462009

<!-- official:early-iron2-26462009:388 -->

请求388完整正常结束，共1轮。官方最终日志均值为 **399:36.796（23976.796游戏秒）**；逐轮日志重算均值为23976.796000000秒，保留两者的显示舍入口径。

同构建前版完整均值25147.408000000秒/1轮；当前正式均值23976.796秒/1轮，缩短约4.66%。Mining5后全额支付50 Coal升Iron2、70 Iron升Mining6，再支付后续Quartz等阶段；保留Mining7/8和同盘扫雷缓存，新增资源筹集与全部前置计入整轮。

部署源码SHA256：`0efa57461a2dcf409e8d20f0355fc5cdf9490c10a68225f288dd450b722bb313`。当前源码SHA256：`9608a37d5e704f703ce4dabe5ebde6c2bb4348d21b21a073eff4c2951f5023ee`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-iron2-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：early-iron2-current-26462009

<!-- official:early-iron2-current-26462009:389 -->

请求389完整正常结束，共1轮。官方最终日志均值为 **429:08.013（25748.013游戏秒）**；逐轮日志重算均值为25748.013000000秒，保留两者的显示舍入口径。

同构建前版完整均值25147.408000000秒/1轮；当前正式均值25748.013秒/1轮，缩短约-2.39%。Mining5后全额支付50 Coal升Iron2、70 Iron升Mining6，再支付后续Quartz等阶段；保留Mining7/8和同盘扫雷缓存，新增资源筹集与全部前置计入整轮。

部署源码SHA256：`9608a37d5e704f703ce4dabe5ebde6c2bb4348d21b21a073eff4c2951f5023ee`。当前源码SHA256：`c6fd366be6584dc1988bb13bc1fc3856bdeecd03ce963434189a6085b841b180`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-iron2-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：early-coal2-26462009

<!-- official:early-coal2-26462009:390 -->

请求390完整正常结束，共1轮。官方最终日志均值为 **369:03.688（22143.688游戏秒）**；逐轮日志重算均值为22143.688000000秒，保留两者的显示舍入口径。

同构建前版完整均值25147.408000000秒/1轮；当前正式均值22143.688秒/1轮，缩短约11.94%。Rice3后全额支付150 Rice升Coal2，保留Mining5后的Iron2/Mining6、Mining7/8及同盘扫雷缓存；提前投资和全部后续资源均计入整轮。

部署源码SHA256：`97f48610235087df383024f1d3dc84397a98841565bda91182f2b2cfa0aa94e6`。当前源码SHA256：`35a32a92bfc5949651f0a6781604b48ec195f90531701fa4148549b9cfedfa27`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-coal2-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：early-coal2-current-26462009

<!-- official:early-coal2-current-26462009:391 -->

请求391完整正常结束，共1轮。官方最终日志均值为 **378:19.482（22699.482游戏秒）**；逐轮日志重算均值为22699.482000000秒，保留两者的显示舍入口径。

同构建前版完整均值25147.408000000秒/1轮；当前正式均值22699.482秒/1轮，缩短约9.73%。Rice3后全额支付150 Rice升Coal2，保留Mining5后的Iron2/Mining6、Mining7/8及同盘扫雷缓存；提前投资和全部后续资源均计入整轮。

部署源码SHA256：`35a32a92bfc5949651f0a6781604b48ec195f90531701fa4148549b9cfedfa27`。当前源码SHA256：`a4aeb7e0d676372f33e18da60280256219fb79bab07c0bd978ddadaf031e7cc4`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-coal2-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：quartz-prospect-bounded-26462009

<!-- official:quartz-prospect-bounded-26462009:392 -->

请求392完整正常结束，共1轮。官方最终日志均值为 **340:23.736（20423.736游戏秒）**；逐轮日志重算均值为20423.736000000秒，保留两者的显示舍入口径。

同构建前版完整均值22699.482000000秒/1轮；当前正式均值20423.736秒/1轮，缩短约10.03%。Quartz阶段先全额筹集勘探Iron，锚点挖完后重读三点公开距离，枚举并核对整数坐标；只计实际dig库存，定位失败有限回退，回退共用原截止。

部署源码SHA256：`0ee096a2fbb4d8f6075b75076c9645fbbf51850aa26e4e52b32c14a64f982dff`。当前源码SHA256：`e77fcd133344440b3477ed17c92ed6cbe28353138d44a4b183a5b011de2485e7`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/quartz-prospect-bounded-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：quartz-prospect-bounded-current-26462009

<!-- official:quartz-prospect-bounded-current-26462009:393 -->

请求393完整正常结束，共1轮。官方最终日志均值为 **377:47.688（22667.688游戏秒）**；逐轮日志重算均值为22667.688000000秒，保留两者的显示舍入口径。

同构建前版完整均值22699.482000000秒/1轮；当前正式均值22667.688秒/1轮，缩短约0.14%。Quartz阶段先全额筹集勘探Iron，锚点挖完后重读三点公开距离，枚举并核对整数坐标；只计实际dig库存，定位失败有限回退，回退共用原截止。

部署源码SHA256：`e77fcd133344440b3477ed17c92ed6cbe28353138d44a4b183a5b011de2485e7`。当前源码SHA256：`fe31927d69349c81d510abdd414bf8c335cf4861f1a136eebcfe5baed0a47eb3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/quartz-prospect-bounded-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：quartz-prospect-bounded-current-confirm-26462009

<!-- official:quartz-prospect-bounded-current-confirm-26462009:394 -->

请求394完整正常结束，共1轮。官方最终日志均值为 **368:28.401（22108.401游戏秒）**；逐轮日志重算均值为22108.401000000秒，保留两者的显示舍入口径。

同构建前版完整均值22699.482000000秒/1轮；当前正式均值22108.401秒/1轮，缩短约2.60%。Quartz阶段先全额筹集勘探Iron，锚点挖完后重读三点公开距离，枚举并核对整数坐标；只计实际dig库存，定位失败有限回退，回退共用原截止。

部署源码SHA256：`fe31927d69349c81d510abdd414bf8c335cf4861f1a136eebcfe5baed0a47eb3`。当前源码SHA256：`8b06f7c61999d1e05007de9ff16bbf39132aa71be7e685db68fd09b2a8246020`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/quartz-prospect-bounded-current-confirm-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：iron-prospect-aligned-26462009

<!-- official:iron-prospect-aligned-26462009:400 -->

请求400完整正常结束，共1轮。官方最终日志均值为 **280:05.039（16805.039游戏秒）**；逐轮日志重算均值为16805.039000000秒，保留两者的显示舍入口径。

同构建前版完整均值22108.401000000秒/1轮；当前正式均值16805.039秒/1轮，缩短约23.99%。Mining5/Iron2后实付32 Coal解锁Prospecting，再用每次1 Coal的公开方向查询引导采铁；库存不足先筹煤，仅实际dig确认Iron，两片无收获回退且共用截止，包含全部前置与后续目标。

部署源码SHA256：`7d45b2335eef03fd5260351db20d5c17ce6c54893f7c37b5648bd985637c5dc3`。当前源码SHA256：`c9a8a282045341dd038a875128ca89e889e4cc7083f317cf3bdd6abcbc283a5b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/iron-prospect-aligned-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：iron-prospect-aligned-current-26462009

<!-- official:iron-prospect-aligned-current-26462009:401 -->

请求401完整正常结束，共1轮。官方最终日志均值为 **302:20.125（18140.125游戏秒）**；逐轮日志重算均值为18140.125000000秒，保留两者的显示舍入口径。

同构建前版完整均值22108.401000000秒/1轮；当前正式均值18140.125秒/1轮，缩短约17.95%。Mining5/Iron2后实付32 Coal解锁Prospecting，再用每次1 Coal的公开方向查询引导采铁；库存不足先筹煤，仅实际dig确认Iron，两片无收获回退且共用截止，包含全部前置与后续目标。

部署源码SHA256：`c9a8a282045341dd038a875128ca89e889e4cc7083f317cf3bdd6abcbc283a5b`。当前源码SHA256：`ace2e45be094fb4f6998d1cc0164f5b1dd17bc972b81f8e237817d50cc89e480`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/iron-prospect-aligned-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：lazy-cover-26462009

<!-- official:lazy-cover-26462009:403 -->

请求403完整正常结束，共1轮。官方最终日志均值为 **255:11.563（15311.563游戏秒）**；逐轮日志重算均值为15311.563000000秒，保留两者的显示舍入口径。

同构建前版完整均值18140.125000000秒/1轮；当前正式均值15311.563秒/1轮，缩短约15.59%。扫雷不再预先清理整片所有柱，只在实际开格前有限准备该柱覆盖层；按真实z和Dynamite地面核对，公开推理、猜测、资源与完整解锁目标不变。同seed普通长程实机另确认状态与完整时间。

部署源码SHA256：`d94736df16fd34a93eb9616bb467f6e1fedfdaf875695e7f81fcd3772095214c`。当前源码SHA256：`abc08f87f4ceaaa8ce37ec483a88bcee5413816d0119aa702ed0ba78035fd882`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/lazy-cover-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：lazy-cover-current-26462009

<!-- official:lazy-cover-current-26462009:404 -->

请求404完整正常结束，共1轮。官方最终日志均值为 **277:50.354（16670.354游戏秒）**；逐轮日志重算均值为16670.354000000秒，保留两者的显示舍入口径。

同构建前版完整均值18140.125000000秒/1轮；当前正式均值16670.354秒/1轮，缩短约8.10%。扫雷不再预先清理整片所有柱，只在实际开格前有限准备该柱覆盖层；按真实z和Dynamite地面核对，公开推理、猜测、资源与完整解锁目标不变。同seed普通长程实机另确认状态与完整时间。

部署源码SHA256：`abc08f87f4ceaaa8ce37ec483a88bcee5413816d0119aa702ed0ba78035fd882`。当前源码SHA256：`8decc050e6777dc1f8229bee88e8d4d076f9160f43eb1d74baaee8665eb1a0c5`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/lazy-cover-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-coal3-26462009

<!-- official:late-coal3-26462009:410 -->

请求410完整正常结束，共1轮。官方最终日志均值为 **256:40.750（15400.750游戏秒）**；逐轮日志重算均值为15400.750000000秒，保留两者的显示舍入口径。

同构建前版完整均值16670.354000000秒/1轮；当前正式均值15400.750秒/1轮，缩短约7.62%。保留小田阶段的Coal2，直到6×6/Speed5/Mining5/Iron2就绪后才支付1000 Rice升Coal3，随后解锁Prospecting；额外成熟、覆盖层与全部后续筹资全额计入，其他采集函数与原完整目标不变。

部署源码SHA256：`93db402570d75608003c393cd76bf3d201fb1b1f9a053538a28edf2798582c7b`。当前源码SHA256：`1b8837b03793dcf3891dacd058ab63d1e177dde511695a1806b379e8e6add4ec`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-coal3-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-coal3-current-26462009

<!-- official:late-coal3-current-26462009:411 -->

请求411完整正常结束，共1轮。官方最终日志均值为 **257:20.645（15440.645游戏秒）**；逐轮日志重算均值为15440.645000000秒，保留两者的显示舍入口径。

同构建前版完整均值16670.354000000秒/1轮；当前正式均值15440.645秒/1轮，缩短约7.38%。保留小田阶段的Coal2，直到6×6/Speed5/Mining5/Iron2就绪后才支付1000 Rice升Coal3，随后解锁Prospecting；额外成熟、覆盖层与全部后续筹资全额计入，其他采集函数与原完整目标不变。

部署源码SHA256：`1b8837b03793dcf3891dacd058ab63d1e177dde511695a1806b379e8e6add4ec`。当前源码SHA256：`dbd224f0a15f1c201014708e6cedf62c8d3311f59b1e7b080c5ddf099fdd1579`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-coal3-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-rice5-26462009

<!-- official:late-rice5-26462009:414 -->

请求414完整正常结束，共1轮。官方最终日志均值为 **241:07.709（14467.709游戏秒）**；逐轮日志重算均值为14467.709000000秒，保留两者的显示舍入口径。

同构建前版完整均值15440.645000000秒/1轮；当前正式均值14467.709秒/1轮，缩短约6.30%。在Mining5/Iron2后、Coal3前把Rice从3升到5，全额支付1000+2000 Block，减少后续稻米采集；现存库存与全部前置计入，其他采集函数及原完整目标不变。

部署源码SHA256：`445e88b0389123e774dde0564536e07b715eae199335e33f848c7af6e7646598`。当前源码SHA256：`dd378e1fe9483bf592a36c4ebb04d2ae57514851bdfee3933e1f4e12cf6d38f2`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-rice5-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：late-rice5-current-26462009

<!-- official:late-rice5-current-26462009:415 -->

请求415完整正常结束，共1轮。官方最终日志均值为 **254:15.250（15255.250游戏秒）**；逐轮日志重算均值为15255.250000000秒，保留两者的显示舍入口径。

同构建前版完整均值15440.645000000秒/1轮；当前正式均值15255.250秒/1轮，缩短约1.20%。在Mining5/Iron2后、Coal3前把Rice从3升到5，全额支付1000+2000 Block，减少后续稻米采集；现存库存与全部前置计入，其他采集函数及原完整目标不变。

部署源码SHA256：`dd378e1fe9483bf592a36c4ebb04d2ae57514851bdfee3933e1f4e12cf6d38f2`。当前源码SHA256：`7f006f9cec28d1b6541f8f03c474934f7fc85336da526edd0a1a3991c0184f9d`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/late-rice5-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：shallow-coal16-26462009

<!-- official:shallow-coal16-26462009:417 -->

请求417完整正常结束，共1轮。官方最终日志均值为 **228:57.473（13737.473游戏秒）**；逐轮日志重算均值为13737.473000000秒，保留两者的显示舍入口径。

同构建前版完整均值15255.250000000秒/1轮；当前正式均值13737.473秒/1轮，缩短约9.95%。Rice已解锁后，Coal采集只处理每片首16层再用原clear循环重生；初始Rice0的Coal10及其他矿采仍走原层数。实际煤库存、清场和减少附带Block/Iron后的补料全额计入，科技和原完整目标不变。

部署源码SHA256：`37bf8b82b571d395ebf312ae4a2dbf9dd576acf1956350851c9ad18cf2ece335`。当前源码SHA256：`b701f34464a6ad0fed4281cc8909083bfb28aede023f0fc009a2b925025f58c3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/shallow-coal16-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：shallow-coal16-current-26462009

<!-- official:shallow-coal16-current-26462009:418 -->

请求418完整正常结束，共1轮。官方最终日志均值为 **225:59.391（13559.391游戏秒）**；逐轮日志重算均值为13559.391000000秒，保留两者的显示舍入口径。

同构建前版完整均值15255.250000000秒/1轮；当前正式均值13559.391秒/1轮，缩短约11.12%。Rice已解锁后，Coal采集只处理每片首16层再用原clear循环重生；初始Rice0的Coal10及其他矿采仍走原层数。实际煤库存、清场和减少附带Block/Iron后的补料全额计入，科技和原完整目标不变。

部署源码SHA256：`b701f34464a6ad0fed4281cc8909083bfb28aede023f0fc009a2b925025f58c3`。当前源码SHA256：`6cbaee3f77914966016c1872868a325cad79fb5701ce79d3da6f426aff32a00c`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/shallow-coal16-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
