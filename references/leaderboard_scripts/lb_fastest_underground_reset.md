# 地下Reset（fastest_underground_reset）

2026-11-06：目标为解锁Underground_Leaderboard。当前实现已完成塌方模型修正后的三seed原目标模拟、普通同seed完整实机对照与迁入真源后的正式完整统计。

## 当前实现

从零库存按当前get_cost筹集资源，逐步发展6×6单机。Rice3后支付150 Rice升Coal2；Expand4后准备Grass2、Trees2、Carrots2和Speed5。Mining5后支付50 Coal升Iron2、32 Coal解锁Prospecting，再筹70 Iron升Mining6。Iron阶段支付Coal读取公开方向，Quartz阶段支付Iron读取公开距离；只有实际dig库存增加才算收获，失败有限回退到原采矿法。随后完成藏宝图和Quartz解锁，支付90 Quartz升Mining7，Mushrooms2后支付250 Mushroom升Mining8。扫雷在同一物理棋盘猜测前后复用公开状态，新棋盘重新建盘。最后支付20000 Dynamite和200000 Bamboo解锁Underground_Leaderboard。每次unlock前复核整个成本字典；Carrot种子成本随科技倍率增加，仍按get_cost实付。

主要成员：`lb_fastest_underground_reset`、`ur_need`、`ur_mine`、`ur_i_stock`、`ur_q_stock`、`ur_q_prepare`、`ur_q_locate`及各`ur_*_stock`和扫雷函数。主流程72000游戏秒；农作7200秒、逐层矿采18000秒。Iron最多64片、准备深度32/64/96/128、每层最多2×世界宽度+1次方向查询及64次dig；Quartz最多64片、探深0–128步长16、单柱最多192次dig。两者回退均共用已有截止。蘑菇/扫雷另有有界盘数、连续未命中和总时间限制。仅复用公开API，采集代码内联；正式验证临时覆盖已有test.py/lb_start.py，普通对照使用已有test.py/simulate.py。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 17181.191108563 游戏秒 | 当前结构，原目标；地下资源快照来源26410308 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 18140.125 游戏秒 | 构建26462009，请求401，1轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 17540.865550588 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/iron-prospect-aligned-model-seed1/report.json` |
| 2 | 17355.715817679 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/iron-prospect-aligned-model-seed2/report.json` |
| 3 | 16646.991957422 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/iron-prospect-aligned-model-seed3/report.json` |

首版部署源码SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。地下资源快照构建为26410308，基础模型字段保留26385848；报告保留真实来源指纹。上表三seed已按当前塌方传播修正重新生成，manifest记录模型文件哈希。专用资源榜仍标`asset_and_source_only`，不能由固定seed重放正式加密随机盘面。

## 当前普通场景同seed对照

当前执行逻辑在普通Reset初始科技、零库存、seed1下，实机请求399完整为17540.865550588游戏秒，与修正后的本地模型相同到整数纳秒。713条阶段输出的离散状态和整数值一致，小数只按原生0.01显示精度比较。上表seed2/3仍仅为模型预测。

证据：`.codex/leaderboard-sol/underground-official/alignment-26462009/iron-prospect/game-seed1/comparison.json`及同目录原请求、部署与恢复记录。部署源码SHA256为`7d45b2335eef03fd5260351db20d5c17ce6c54893f7c37b5648bd985637c5dc3`，与当前源码仅时间注释不同。模型修正与额外方法覆盖见[地下对照记录](../../mechanism_model/local_simulator/underground-validation.md)。普通同seed精度与正式随机榜均值分别记录，不用两者差额估算模型误差。

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

Coal3仅作下一成本边界代表：在相同位置再付1000 Rice，seed1完整目标24690.419270700秒，慢于Coal2同seed23091.030955295秒约6.93%，未进实机，不继续枚举。证据为`.codex/leaderboard-sol/underground-official/fastest_underground_reset/early-coal3-model-seed1/report.json`。Coal4新增4000 Rice的预估成本已高于当前煤阶段可节省的费用，也不进入模型；闭式预算只用于筛选，不能替代完整目标结果。

Quartz公开距离定位每次支付1 Iron；Iron少于16时先按真实采矿筹到32。先完成锚点挖掘，再读取三点的实际x/y/z和距离，枚举世界内整数坐标，允许0.01的平方距离误差。最近矿可能在不同采样点之间变化，三点一致也不作为库存证明；只计真正dig到的Quartz，连续两片无收获则回退普通逐层矿采。原型因调用游戏没有的int在8223.326768699秒停止，未进实机；改用整除舍入，并让回退继承相同截止后，当时三seed均完成原目标，均值20832.143635273秒，已包含200/146/224次勘探及筹集所耗Iron的成本。此为塌方模型修正前记录，当前修后预测见上表。

正式392完整1轮20423.736秒；真源393为22667.688秒，两次差约10.99%，因此追加394，完整1轮22108.401秒，与393差约2.47%。该阶段采用394，相对Coal2阶段22699.482秒约快2.60%，相对首版31535.109秒约快29.89%。不同正式盘面的波动明显，不能把模型三seed约8.57%的收益直接写成实机收益。部署、Core指纹、双日志和恢复证据见下方三次正式记录。

后续先准备三锚点、取消挖掘前预读的候选虽把seed1勘探次数从200降到165，dig却由74262升到75545，修前模型完整目标20357.378612241秒，高于当时同seed19713.690940317秒约3.27%。未进实机，保留先探主柱再准备其他锚点的结构；证据在`.codex/leaderboard-sol/underground-official/fastest_underground_reset/quartz-prospect-batched-model-seed1/report.json`。

Iron公开方向勘探版在Mining5/Iron2后新增Prospecting1，实际支付32 Coal；每次查询再付1 Coal，煤不足16时先按原采矿法筹到32。每片分层准备主柱，最多沿公开方向移动2×世界宽度+1次，再按真实Iron地面挖掘；None也可能表示范围无矿，不作为找到矿的证明。两片无收获回退并继承同一截止。修后三seed完整目标均值17181.191108563秒，比修后Quartz版20833.148960359秒少约17.53%，包含额外煤与解锁成本。

普通同seed请求399另经完整时间和状态校准。正式候选400为16805.039秒，迁入真源后的401为18140.125秒，两次均正常完成1轮，差约7.94%。当前采用401，比前版22108.401秒约快17.95%，比同构建首版31535.109秒约快42.48%；以上为不同正式随机样本的完整成绩。双日志、实际达标与存档恢复证据分别保留，不由普通seed预测推算正式排名。

## 静态检查与后续

AST解析、仓库游戏语法、入口结构及禁止jump检查通过。当前Iron/Quartz定位、Coal2/Iron2/Mining8及同盘缓存执行逻辑的源码副本已运行ty LSP：10项错误、26项提示。外部桩缺少Underground_Leaderboard，measure联合类型不能按竹子、藏宝图、Soot上下文收窄；其余为spawn/None不可达或既有未使用局部变量。新增Iron函数无错误，None分支多1项桩类型不可达提示；实机正常经过公开API，未修改外部游戏类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已取得公开排名。普通生成可能缺当前资源层，有限重试已通过所列三seed和整轮实机；覆盖范围按地下模型对照记录，不扩展为任意世界保证。

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
