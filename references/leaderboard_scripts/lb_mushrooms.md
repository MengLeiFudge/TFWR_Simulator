# 蘑菇（mushrooms）

2026-11-06：新增可复核基线，目标为240000 Mushroom。正式真源仍采用请求365的557.580秒版本。2026-11-07本地结构候选已完成三个seed的原目标，均值320.579402秒；尚未达到#1的1.5倍实机门槛，候选与正式成绩分开记录，见末节。

## 当前实现

主孔先找到Mushroom顶面，再一次派发把全田准备到同一高度。按不相交矩形分区做同色推送和双邻配对。非蘑菇接收柱须先找到两块同色且高出共同floor至少两格的邻块，才挖到floor；遇到新蘑菇立即保留。保留(0,0)采样柱，整层工人全部结束后主机才推进采样高度。

主要成员：`dig_layer`、`dig_columns`、`make_blocks`、`run_layer`、`work_layer`、`push_match`、`feed_column`。最多128片、7200游戏秒；每个工人受共同两格高度带限制，失败仍先回收全部句柄。来源为本机既有Mushroom.py，必需逻辑已内联，无新存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 566.820213930 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 557.580 游戏秒 | 构建26462009，请求365，13轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 576.858954780 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-model-seed1/report.json` |
| 2 | 562.069404720 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-model-seed2/report.json` |
| 3 | 561.532282290 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-model-seed3/report.json` |

首版部署源码 SHA256：`358c2f73cf9f2586652eaf5f5a330df5e59ba9ace0b603579024f7cbe6247b06`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":{"item":"Mushroom","amount":512},"ordinary_world_size":8,"find_stratum_limit":256}`；正式榜原目标仍由上方三seed验证。

请求 `331` 正常结束。本地与原生simulate完整返回时间均为 **14.629549140 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/mushrooms/ordinary-pair-v2/game-seed1/comparison.json`。派生脚本 SHA256：`430d8f84f88ef33bdbb2c561f2d8c1d97245593a70f9c94d48f40ef08b551444`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐覆盖层全田派发的旧版约1201秒/多机、2826秒/单机。单孔定位后一次准备减少了覆盖层派发与等待。空接收柱候选的多机版已通过三seed模型及请求357的13轮完整统计，候选正式均值557.267秒；迁入真源后的请求365完整13轮为557.580秒，当前采用复验结果，较原572.673秒缩短约2.64%。单机同改动在请求358中更慢，未同步保留。

三格高度带候选只把floor从ceiling-2改为ceiling-3。多机seed1在137.483095050秒正常返回，但仅得到70816/240000 Mushroom，输出`mushrooms_failed layer 3 5 -7`，未达到原目标；精确失败分支尚未定位。该多机候选不进入实机、不替换当前两格版，也不继续无界调整深度。证据：`.codex/leaderboard-sol/underground-official/mushrooms/band3-model-seed1/report.json`。仅凭Mushroom稳定性为3不能证明整个跨层、空接收柱及分区组合安全。

2026-11-07修后模型重算当前版seed1，仍为576.858954780秒，原目标完成；证据为`.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-cavein-model-seed1/report.json`，另两个seed保留历史口径。层间平移x分区半块宽的首版缺少最右列East环绕到(0,0)的保护，在65.075600520秒以`mushrooms_failed sample 2 1`返回，仅25072/240000，未部署。地面方向查询与push都会环绕，不能套用硬度查询的越界规则。

补全East保护后，生成器按环绕坐标核对1024格唯一归属、邻格仍属本块及采样柱不被任何方向写入。候选完整seed1为579.165470100秒，慢于当前同seed约0.40%；push由16384降到16356，解释器由14286871t升到14717903t，clear与派发数不变，没有得到配对收益。不再扩大种子或枚举偏移，也不进入完整实机。证据为`.codex/leaderboard-sol/underground-official/mushrooms/shifted-partitions-wrap-guard-model-seed1/report.json`；首版失败证据另保留于`shifted-partitions-model-seed1/`。当前源码和正式成绩均未变。方向边界另经当前构建请求408短方法对照，具体范围见[地下模型对照](../../mechanism_model/local_simulator/underground-validation.md)。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。与当前执行逻辑一致的源码副本（仅时间注释不同）的ty LSP无错误，3项提示分别为两处spawn_drone类型桩的None分支不可达和既有循环变量y未使用。保留运行时失败处理，未修改外部类型桩。

继续按[共用研究流程](README.md)做本地算法研究。打榜实机只允许完整目标模拟时间≤对应榜单#1的1.5倍，或用户明确指定实机运行具体脚本；短时筛选与迁入后复验同样受限。当前候选未达标，不投递实机，不更新正式源码和成绩索引。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:348 -->

请求348完整正常结束，共13轮。官方最终日志均值为 **9:32.673（572.673游戏秒）**；逐轮日志重算均值为572.672769231秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`358c2f73cf9f2586652eaf5f5a330df5e59ba9ace0b603579024f7cbe6247b06`。当前源码SHA256：`1298cea19856d52bdc8073493895cadb6c96f0869aee0db2bdb0ff6ecc2b8683`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：empty-receiver-26462009

<!-- official:empty-receiver-26462009:357 -->

请求357完整正常结束，共13轮。官方最终日志均值为 **9:17.267（557.267游戏秒）**；逐轮日志重算均值为557.267384615秒，保留两者的显示舍入口径。

同构建前版完整均值572.672769231秒/13轮；当前正式均值557.267秒/13轮，缩短约2.69%。非蘑菇接收柱先验证两邻块同色且高出floor至少两格，再只挖到共同floor；遇新蘑菇保留，分区、采样柱和两格高度带不变。

部署源码SHA256：`38273503f80f4d76cda203168f461474f9454bc67cdedc43a631e84d56e3b8f3`。当前源码SHA256：`cce5c353662e81ceebc340cb61dc77cf1dd2b5920366f6d083eba83fd3f90146`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：empty-receiver-current-26462009

<!-- official:empty-receiver-current-26462009:365 -->

请求365完整正常结束，共13轮。官方最终日志均值为 **9:17.580（557.580游戏秒）**；逐轮日志重算均值为557.580461538秒，保留两者的显示舍入口径。

同构建前版完整均值572.672769231秒/13轮；当前正式均值557.580秒/13轮，缩短约2.64%。非蘑菇接收柱先验证两邻块同色且高出floor至少两格，再只挖到共同floor；遇新蘑菇保留，分区、采样柱和两格高度带不变。

部署源码SHA256：`cce5c353662e81ceebc340cb61dc77cf1dd2b5920366f6d083eba83fd3f90146`。当前源码SHA256：`3f6beef7a90e86715726703f3c97f9bc217c41a027b7929116da8b1e00a3d63f`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms/empty-receiver-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 2026-11-07 本地候选：常驻工人、同高中转与末层预算

仅刷新[蘑菇多机榜](https://steamcommunity.com/stats/2060160/leaderboards/21444618/)，2026-11-07T09:07:20Z的#1为94.538秒，实机门槛为141.807秒。最新三seed完整目标均值320.579402秒，为#1的3.391倍；仍需再缩短约55.77%才达到准入门槛。本节均为本地模型筛选，不是游戏成绩或排名。

| 时间类别 | 本候选记录 | 口径 |
| --- | ---: | --- |
| 本地模拟预估时间 | 320.579402秒 | seed1/2/3，均完成原240000目标 |
| 短时打榜测试时间 | 未取得 | 本候选未实机运行 |
| 游戏打榜时间 | 未取得 | 正式真源仍为557.580秒 |

| seed | 原目标本地游戏秒 | 结果 |
| --- | ---: | --- |
| 1 | 327.393816660 | 达标 |
| 2 | 319.572701730 | 达标 |
| 3 | 314.771686470 | 达标 |

同一当前模型的新鲜seed1基线为576.858954780秒，候选327.393816660秒，缩短43.25%。基线证据为`.codex/leaderboard-sol/underground-official/mushrooms/current-baseline-model-seed1/report.json`。上方旧三seed均值566.820214保留历史口径，不冒充本轮重新运行的三seed基线。

本地结构采用以下机制：

- 每片只派发一次工人。各工人在不相交分区内连续推进，按实际柱顶处理高度变化，所有句柄回收后才clear。
- 先直接合并；缺少邻接同色时，利用已公开的低平台两步搬运。只在已找到同色终点、缺一格中转高度时消耗已有Block补土。
- 相邻同高同色的A/B不能直接相推时，借B旁低两格的C做B→C、A→B、B→C，共三次push、两次move，避免把A/B直接挖掉。
- 主机用预留(0,0)柱读出实际蘑菇厚度。工人只处理厚度减一的层数，避免空层扫描和低产末层。保留两格工作窗口，不把三格候选推广到多机。

主要成员为`work_patch`、`work_layer`、`carry_match`、`fixture_match`和`feed_column`。高度、颜色与库存仍由公开API取得；匹配只按真实push计产量。模型中的该组合已完成所列三个seed，不代表全部并发盘面或长程精度已通过实机验收。

冻结候选：`.codex/tests/mushroom-leaderboard/local-best-20261107/lb_mushrooms.py`，SHA256 `c8830e949d79136e6209799df4ee052c8f96e6cc0ad40a24a7d4093ab5f3e8a5`。冻结时仅修正说明注释，AST与报告执行版相同，manifest同时记录两份哈希。原目标报告及执行副本位于`.codex/leaderboard-sol/underground-official/mushrooms/probe1-full-model-seed1/`至`seed3/`；模型每seed限180墙钟秒、600万API、7000万源步骤，并输出进度。

### 有界筛选与停止依据

| 候选 | 本地证据 | 结论 |
| --- | --- | --- |
| 常驻工人、原配对 | 80000短筛181.887→151.438秒 | 派发和返回有成本，方向保留 |
| 常驻＋补平台 | 完整seed1为400.446089秒 | 有改善，仍未达实机门槛 |
| 已测厚度、保留全部层 | 80000短筛116.811865秒 | 仍花费低产末层成本 |
| 跳过末一层 / 末两层 | 80000短筛104.592700 / 109.449683秒 | 保留跳过一层 |
| 三格窗口 | 80000短筛39.485165秒时`patch 1`失败，目标未达 | 淘汰，不凭快速返回判成功 |
| 复用已测柱顶 / 延期拉回 | 完整seed1为322.762185 / 320.421596秒 | 只有单seed记录，未替代冻结三seed基线 |
| 分阶段配对 / 保护预约 | 80000短筛99.181146 / 106.081762秒 | 预约维护成本高，未扩大到完整统计 |

短筛目标改为80000，仅判断方向，不能拿短筛时间对比240000榜首或判断实机准入。短筛与完整报告均保留实际库存、目标和源码哈希。

早先两步搬运候选曾投递请求441；用户指出远超#1后取消。16个真实`run=`均值449.1375秒，`full_statistics=false`，只记该旧候选的筛选证据，不记正式成绩。临时test.py/lb_start.py已回idle后恢复，其余存档Python未变。新准入规则生效后的上述研究均只在本地运行，未再次启动游戏。

冻结候选的游戏语法、入口及无jump检查通过；ty LSP无错误、5条hint为3个未使用循环变量及2个类型桩导致的不可达提示。保留实际spawn失败处理，不修改外部类型桩。

下一阶段继续研究配对兑现率和每对move/dig下界。只省解释器费用或重复开田仍不能解释94.538秒；未达到141.807秒之前继续留在本地。

Implementation deviations：None。
