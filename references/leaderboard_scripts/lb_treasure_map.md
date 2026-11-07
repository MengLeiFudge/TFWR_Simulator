# 藏宝图（treasure_map）

2026-11-06：新增可复核基线，目标为115000 Gold。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

单机找到Basalt并读地图坐标，到达Treasure_Map后只读一次路线。方向字典把N/E/S/W映射到公开move方向；仍按完整路线逐字符执行，保留回头路，每个D只挖一次，最后验证Underground_Treasure再harvest。

主要成员：`lb_treasure_map`、`treasure_map_move_to`。最多256张地图、7200游戏秒；每张Basalt搜索256步、地图定位32步，所有动作失败均明确停止。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 289.540320540 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 274.988 游戏秒 | 构建26462009，请求384，27轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 290.074918950 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/treasure_map/direction-table-model-seed1/report.json` |
| 2 | 279.835024680 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/treasure_map/direction-table-model-seed2/report.json` |
| 3 | 298.711017990 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/treasure_map/direction-table-model-seed3/report.json` |

首版部署源码 SHA256：`b39cf5aa09bb6a95e3347f8bd40e56b8b58e57ea51599511ffa76c7be39c9709`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[115000,40000],"ordinary_world_size":8,"ordinary_max_drones":1}`；正式榜原目标仍由上方三seed验证。

请求 `330` 正常结束。本地与原生simulate完整返回时间均为 **135.558639540 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/treasure_map/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`2eaa436434bdba8b3a61f61c8a27e72b84af528901956698f4038b4c4ff21fc6`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

路线首个D已经处理地图块，额外预挖会改变路径状态。当前正式版本不压缩路线，不跨无人机交接，不在路径内clear或重定位。这里描述的是当前实现，不是禁止去环的游戏规则。

2026-11-07方向复核：当前构建26462009的Core.dll只读反编译确认，`TreasureMapController.CheckDronePosition`检查路径坐标及地块有效性，并以`TREASURE_OPTIMAL`奖励同层不重复访问格子。正常沿有效通路去环、逐层走到下行口有机制依据；此前把20ms完整性检查理解为“所有回头路都必须照走”是错误推断。下一方向比较线性去环、逐层最短路和选图收益，预算见[地下策略分析](underground_strategy_analysis.md)。这次仅修正研究约束，未修改正式代码，也未新增模型或实机成绩。

方向查表的三seed完整目标均比原分支版快约2.46–2.70游戏秒，均值从292.105493040降到289.540320540。为核对这一小收益，请求382在当前构建用同一seed、普通8×8、单机、40000 Gold目标成对运行：原版135.559956420秒，查表版134.631062190秒，省0.928894230秒。地图周期、路线长度、Block/Gold库存及最终坐标一致；本地配对得到同样的时间差，API次数也相同。两份simulate返回值各比独立本地脚本多8t入口分派，未把它当作模型零误差验收。

配对证据：`.codex/leaderboard-sol/underground-official/treasure_map/direction-table-price-pair/native-seed1/comparison.json`及同目录请求和restoration；已有test.py/simulate.py在同ID回idle后恢复，其他存档Python文件未变。这项普通场景只证明分派费用，正式115000 Gold另由请求383和真源复验384分别完成27轮，当前成绩采用384的274.988秒。

## 静态检查与后续

AST解析、仓库游戏语法、入口结构及禁止jump检查通过。当前执行逻辑的字节副本已运行ty LSP：4项错误来自measure的联合返回类型无法静态区分Basalt坐标与地图字符串，另有2条None分支提示；未修改外部类型桩。方向查表未引入新接口或路线变换，当前构建另有同seed配对及两次完整正式统计。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:354 -->

请求354完整正常结束，共26轮。官方最终日志均值为 **4:37.200（277.200游戏秒）**；逐轮日志重算均值为277.200153846秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`b39cf5aa09bb6a95e3347f8bd40e56b8b58e57ea51599511ffa76c7be39c9709`。当前源码SHA256：`f67e162a082dd02872dca495c1bbb2e84ac0115860cd6bad9c1747f8e03d2260`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/treasure_map/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：direction-table-26462009

<!-- official:direction-table-26462009:383 -->

请求383完整正常结束，共27轮。官方最终日志均值为 **4:36.330（276.330游戏秒）**；逐轮日志重算均值为276.329481481秒，保留两者的显示舍入口径。

同构建前版完整均值277.200153846秒/26轮；当前正式均值276.330秒/27轮，缩短约0.31%。方向字符通过同一字典映射到公开move方向，D仍逐次dig；完整路线、回头路、单机归属、动作检查与115000 Gold目标全部保留，同seed普通场景实机另有配对收益证据。

部署源码SHA256：`dfe48568ceb65a471a8d9bc45f6a287d4453d6ad7cb186d86cd55acbc6eec2c4`。当前源码SHA256：`6a4d5cba086040b68477b9ee6864a72a6acc17bebf8d297ac6f4afe1b12fb86c`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/treasure_map/direction-table-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：direction-table-current-26462009

<!-- official:direction-table-current-26462009:384 -->

请求384完整正常结束，共27轮。官方最终日志均值为 **4:34.988（274.988游戏秒）**；逐轮日志重算均值为274.987629630秒，保留两者的显示舍入口径。

同构建前版完整均值277.200153846秒/26轮；当前正式均值274.988秒/27轮，缩短约0.80%。方向字符通过同一字典映射到公开move方向，D仍逐次dig；完整路线、回头路、单机归属、动作检查与115000 Gold目标全部保留，同seed普通场景实机另有配对收益证据。

部署源码SHA256：`6a4d5cba086040b68477b9ee6864a72a6acc17bebf8d297ac6f4afe1b12fb86c`。当前源码SHA256：`fa35ea56ef201e70231ee5f17e3cb6aa40339628c9238f2cd3e16ca30353f884`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/treasure_map/direction-table-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 2026-11-07 本地候选：最后出口去环

在公开地图路径内按三维坐标保留最后出口，删除回环而保留每次下降；8格世界每图重生。原目标三seed预估34.584396390/42.404359050/36.856014390秒，均值37.948256610；当前完整路线fresh三seed均值289.540320540，减少86.89%。全部原目标完成，未做实机验证，正式274.988秒不变。

脚本为`.codex/leaderboard-sol/underground-official/treasure_map/last-exit-reset8-candidate/lb_treasure_map.py`。尺寸4/6、逐层BFS及按原串长度筛图的比较、源码指纹与检查限制见[本地候选记录](underground_local_candidates.md)。这是此前“必须照走回头路”错误约束被纠正后的结构收益，不是字符分派优化。
