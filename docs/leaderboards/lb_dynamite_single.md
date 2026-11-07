# 炸药单机（dynamite_single）

2026-11-06建立基线，目标为100000 Dynamite；2026-11-07迁入按需清覆盖层。当前实现已完成塌方修正后的三seed原目标模拟及迁入真源后的完整正式统计；普通场景成功历史与本次失败边界分别记录。

## 当前实现

单机维护公开数字与SAFE/MINE事实，先做直接和子集推理，停滞后有限低风险猜测。覆盖层仅在实际开格前清理该柱，利用零扩展自动揭露其他柱；按真实z和Dynamite地面核对后才dig，不提前清整片。同一物理棋盘在猜测前后复用状态；owned集合和几何探测顺序只初始化一次，新猜测后清除采样与局部检查记录，以便发现零扩展和新增数字。每次clear后重新建盘，绝不跨棋盘复用事实。仅当所有剩余格都已证明为雷时，才挖已揭开的Soot完成一次人工结算；踩雷后按真实盘面变化收口。

主要成员：`lb_dynamite_single`、`dynamite_solve`、`worker`、`dig_target`、`dynamite_guess`。最多512盘、14400游戏秒、每盘32次猜测，寻找雷层和单次开格准备各最多256次dig。来源为本机既有Dynamite.py，必需逻辑已内联；不跳层、不新增存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 832.552606080 游戏秒 | 当前结构，原目标；地下资源快照来源26410308 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 880.591 游戏秒 | 构建26462009，请求407，9轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 705.694921920 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/lazy-cover-model-seed1/report.json` |
| 2 | 922.315755960 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/lazy-cover-model-seed2/report.json` |
| 3 | 869.647140360 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/lazy-cover-model-seed3/report.json` |

首版部署源码SHA256：`d4a9964459e78aa2471e31476f2723f0d897209e91689da117869126e38f3af3`。地下资源快照来源为26410308，基础模型字段保留26385848；报告保留两组来源指纹，当前三seed均使用塌方修正后的模型，manifest记录模型文件哈希。资源榜专用地形的验证级别仍为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 当前普通场景失败边界核对

普通8×8、满级科技、seed1下，原字节候选在256次搜层上限处返回，仅32.053517640秒，未送实机。仅把搜层和开格覆盖层边界从256改为2048，保留100000目标后，本地在1316.479833090秒以`dynamite_cycle 27 error 0 368`返回，实际库存50144。实机请求405在相同源码、参数和seed下复现37条输出及完整纳秒，误差0ns；双日志无新增错误，同ID回idle后逐字节恢复已有test.py/simulate.py，其余Python文件未变。

证据：`.codex/leaderboard-sol/underground-official/alignment-26462009/dynamite-single-lazy-cover-ordinary-failure/game-seed1/comparison.json`，派生源码SHA256为`37d25d4a2be386d2f6a34c98fc6d3113618826e5c2e055130c32613f5cf20924`。该项只确认模型复现失败，`goal_reached=false`和`long_window_passed=false`；不计为100000目标通过。普通地形返回error的精确分支尚未定位，不把该策略外推为任意普通地层通用求解器。正式版仍保持256次边界，专用榜完整目标另由下方两次正式统计验证。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":2048,"find_stratum_limit":2048,"ordinary_world_size":8}`；正式榜原目标仍由上方三seed验证。

请求 `334` 正常结束。本地与原生simulate完整返回时间均为 **123.470998020 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/dynamite_single/ordinary-pair-v4/game-seed1/comparison.json`。派生脚本 SHA256：`deae1518e4517868c88a5919ec12ac9b17d362436ff41541b1bf1589884ee8f1`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

批次候选约2692秒、并行规划候选约4133秒，均慢于本机既有约束求解结构，因此保留串行结构。移除了没有调用路径的区域派发包装。

前版同盘缓存三seed的API调用次数均与原版相同，原目标均完成。seed1解释器开销从3298474t降到3082779t，省215695t，即35.505553950游戏秒；三seed均值由1244.993221770降到1206.387787170。这个约3.1%的同seed模型收益来自减少重建与重复推理。正式统计受随机盘面影响，不能把该阶段实机相对基线的11.87%全部归因于缓存。
缓存版三次完整统计分别为1288.764秒/6轮、1230.204秒/6轮、1266.656秒/6轮。第二次最后两轮差26.7%，因此追加第三次，最后两轮差约7.3%；该阶段时间和索引采用第三次。全部轮次正常达到100000 Dynamite，未出现矛盾诊断。

按需清覆盖层只改入口和`dig_target`，推理、猜测、同盘缓存、实际库存目标不变。先用修后模型重算基线三seed，仍为1069.131744180、1314.684267210、1235.347350120秒；候选对应为705.694921920、922.315755960、869.647140360秒，均完成原100000目标，均值少30.99%。seed1 dig由6018降到3005，move由8502降到4930；三个seed的clear、measure次数和盘数分别与前版相同。少清覆盖层和少走准备路线贡献了主要收益。

正式候选406完整9轮，官方均值843.916秒，最后两轮差18.6%，故继续迁入真源后完整复跑。407完整9轮为880.591秒，最后两轮差约8.99%，两批均值差约4.35%。当前采用407，比前版1266.656秒约快30.48%，比同构建首版1437.266秒约快38.73%。两批共18轮全部正常达标，双日志无新增错误，结束同ID回idle后恢复已有脚本。

## 静态检查与后续

AST解析、仓库游戏语法、入口结构及禁止jump检查通过。当前执行逻辑的字节副本已运行ty LSP：2项错误来自Soot数字measure的联合返回类型与整数比较，另有11条未使用变量或API返回类型提示，与前版相同。新增覆盖层准备没有增加诊断，未修改游戏外部类型桩。本版两次正式完整统计共18轮提供当前专用榜运行证据。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:351 -->

请求351完整正常结束，共6轮。官方最终日志均值为 **23:57.266（1437.266游戏秒）**；逐轮日志重算均值为1437.266000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`d4a9964459e78aa2471e31476f2723f0d897209e91689da117869126e38f3af3`。当前源码SHA256：`e6eb2af30509e510ed8b49a77bb7a365c9165f94b065551409352bce0da8f469`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-26462009

<!-- official:state-cache-26462009:379 -->

请求379完整正常结束，共6轮。官方最终日志均值为 **21:28.764（1288.764游戏秒）**；逐轮日志重算均值为1288.763833333秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1288.764秒/6轮，缩短约10.33%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`b0ba4e61ffb9d5bb7721c254ccd7005074fe4aaa8b45e0541cb246279e57002c`。当前源码SHA256：`a3fd18741b2cfdf5618044819c2b8c00406c0773f889fd9a4f9cac2c99d2c07b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-current-26462009

<!-- official:state-cache-current-26462009:380 -->

请求380完整正常结束，共6轮。官方最终日志均值为 **20:30.204（1230.204游戏秒）**；逐轮日志重算均值为1230.204166667秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1230.204秒/6轮，缩短约14.41%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`a3fd18741b2cfdf5618044819c2b8c00406c0773f889fd9a4f9cac2c99d2c07b`。当前源码SHA256：`3b630b4ff7abd4da3e051dd276b9257d04e610711baf1f8436117dbc9b0afb49`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-current-confirm-26462009

<!-- official:state-cache-current-confirm-26462009:381 -->

请求381完整正常结束，共6轮。官方最终日志均值为 **21:06.656（1266.656游戏秒）**；逐轮日志重算均值为1266.656666667秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1266.656秒/6轮，缩短约11.87%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`3b630b4ff7abd4da3e051dd276b9257d04e610711baf1f8436117dbc9b0afb49`。当前源码SHA256：`23301951a179d21923859b66cc69cf35646474faa029201dcd459cb82be91aa5`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-current-confirm-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：lazy-cover-26462009

<!-- official:lazy-cover-26462009:406 -->

请求406完整正常结束，共9轮。官方最终日志均值为 **14:03.916（843.916游戏秒）**；逐轮日志重算均值为843.916111111秒，保留两者的显示舍入口径。

同构建前版完整均值1266.656666667秒/6轮；当前正式均值843.916秒/9轮，缩短约33.37%。扫雷不再预先清理整片所有柱，只在实际开格前有限准备该柱覆盖层；按真实z和Dynamite地面核对，公开推理、猜测、资源与原榜完整目标不变。普通场景的成功与失败边界按各自实际目标单独记录，不将时间相符写成目标完成。

部署源码SHA256：`dc3530be737dd65047bfffd3f7013941822ee56c1b6fa17fedfbc59a852fcd5b`。当前源码SHA256：`ca28aae78d1ba3dccbbbdc410025d4af102126d683f08a2af2e013b4e064077b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/lazy-cover-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：lazy-cover-current-26462009

<!-- official:lazy-cover-current-26462009:407 -->

请求407完整正常结束，共9轮。官方最终日志均值为 **14:40.591（880.591游戏秒）**；逐轮日志重算均值为880.590666667秒，保留两者的显示舍入口径。

同构建前版完整均值1266.656666667秒/6轮；当前正式均值880.591秒/9轮，缩短约30.48%。扫雷不再预先清理整片所有柱，只在实际开格前有限准备该柱覆盖层；按真实z和Dynamite地面核对，公开推理、猜测、资源与原榜完整目标不变。普通场景的成功与失败边界按各自实际目标单独记录，不将时间相符写成目标完成。

部署源码SHA256：`ca28aae78d1ba3dccbbbdc410025d4af102126d683f08a2af2e013b4e064077b`。当前源码SHA256：`455727dcfcb9f315d6339c0fc5401310ce86670c4ba8e2454c28bcb2f4dd492a`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/lazy-cover-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
