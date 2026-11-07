# 石英矿单机（ores_single）

2026-11-07：实付筹资的最近距离排除候选已通过请求423完整14轮，534.068秒，已迁入正式源码。完整沟网及强求三球同矿的比较见[本地候选记录](underground_local_candidates.md)。

2026-11-06：新增可复核基线，目标为4000 Quartz。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

先真实采煤，再支付方向勘探采铁，用铁支付Quartz距离查询。三个相邻锚点全部挖好后重读距离：第一读数约束候选在球面，其余读数只排除球内位置，不假设三次最近矿相同。按残差选择目标后实际挖掘确认；无解或未挖到矿时回退全覆盖沟网。

主要成员：`ore_fund`、`ore_prepare`、`ore_locate`、`ore_trench`、`ore_move_to`。主流程最多128片，每片最多8次定位，筹铁最多64片，共用7200游戏秒截止。实际筹资、错误定位和回退费用全部计入。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 572.568998700 游戏秒 | 当前结构，原目标；地下资源快照来源26410308 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 548.381 游戏秒 | 构建26462009，请求436，14轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 538.476018030 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/ores_single/sphere-exclusion-model-seed1/report.json` |
| 2 | 626.642780130 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/ores_single/sphere-exclusion-model-seed2/report.json` |
| 3 | 552.588197940 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/ores_single/sphere-exclusion-model-seed3/report.json` |

首版部署源码 SHA256：`8d6b41dea5333b3e0807ab93a257304fa1694365cfc373cbb3169b8916c16392`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[4000,64],"ordinary_world_size":8,"ordinary_max_drones":1,"quartz_cross_section":[39,55]}`；正式榜原目标仍由上方三seed验证。

请求 `327` 正常结束。本地与原生simulate完整返回时间均为 **21.098557530 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/ores_single/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`73c5b126a01109c4467d27d5f27cf495b9b05ba02248ba60f93916c42a9bd5ea`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐层剥离全田的旧候选在7200秒仅得到3432 Quartz，未达4000目标。四井版仍只读公开地面与高度，不读取隐藏针的位置、不预记产量，并保留库存、硬度、deadline和全部wait边界。

候选请求374完整7轮为1055.810秒；迁入真源后的请求375完整7轮为1045.728秒。375最后两轮差异约21%，因此增加请求376的完整7轮，最终均值1069.625秒、最后两轮差异约9.4%；当前采用这次追加完整统计，仍优于原1279.818秒。各次结果均保留，不用样本最好值替换当前复验。

## 静态检查与后续

当前执行源码与冻结模型、候选实机源码的AST一致，游戏语法检查通过。ty LSP无错误、2提示：未使用的attempt及prospect_iron返回None的运行时分支被外部桩判为不可达。未修改外部桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:347 -->

请求347完整正常结束，共6轮。官方最终日志均值为 **21:19.818（1279.818游戏秒）**；逐轮日志重算均值为1279.818333333秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`8d6b41dea5333b3e0807ab93a257304fa1694365cfc373cbb3169b8916c16392`。当前源码SHA256：`aca70b3c3fc955fec8b3c67bf85ac4e9c52207d98f2e3f2e1869aeda2f3d64b4`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores_single/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：four-wells-26462009

<!-- official:four-wells-26462009:374 -->

请求374完整正常结束，共7轮。官方最终日志均值为 **17:35.810（1055.810游戏秒）**；逐轮日志重算均值为1055.810428571秒，保留两者的显示舍入口径。

同构建前版完整均值1279.818333333秒/6轮；当前正式均值1055.810秒/7轮，缩短约17.50%。每个x仍为唯一写者；多机32×32和单机8×8分别采用对应的四口不重复井，复用本片准备并分摊清场，仍读取实际地层、只计真实dig库存，不预记产量。

部署源码SHA256：`90b7a39cf30cbfffea2dc0fee45c2dab2d9fa07eb760f578971e6fbf560265eb`。当前源码SHA256：`ba2b43300229ddce4a091348a09379c96109024ce8da159aaab949d409bdea30`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores_single/four-wells-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：four-wells-current-26462009

<!-- official:four-wells-current-26462009:375 -->

请求375完整正常结束，共7轮。官方最终日志均值为 **17:25.728（1045.728游戏秒）**；逐轮日志重算均值为1045.728428571秒，保留两者的显示舍入口径。

同构建前版完整均值1279.818333333秒/6轮；当前正式均值1045.728秒/7轮，缩短约18.29%。每个x仍为唯一写者；多机32×32和单机8×8分别采用对应的四口不重复井，复用本片准备并分摊清场，仍读取实际地层、只计真实dig库存，不预记产量。

部署源码SHA256：`ba2b43300229ddce4a091348a09379c96109024ce8da159aaab949d409bdea30`。当前源码SHA256：`c6f336094cefe20933a117e55268dcc94f1576a2f1241b1b9ed9fa4c59a81122`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores_single/four-wells-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：four-wells-current-confirm-26462009

<!-- official:four-wells-current-confirm-26462009:376 -->

请求376完整正常结束，共7轮。官方最终日志均值为 **17:49.625（1069.625游戏秒）**；逐轮日志重算均值为1069.624571429秒，保留两者的显示舍入口径。

同构建前版完整均值1279.818333333秒/6轮；当前正式均值1069.625秒/7轮，缩短约16.42%。每个x仍为唯一写者；多机32×32和单机8×8分别采用对应的四口不重复井，复用本片准备并分摊清场，仍读取实际地层、只计真实dig库存，不预记产量。

部署源码SHA256：`c6f336094cefe20933a117e55268dcc94f1576a2f1241b1b9ed9fa4c59a81122`。当前源码SHA256：`cb07156b724b1c3ecce92cdd184d6ac0bbaa21d6fc6aca912d80fcd7da999d6b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores_single/four-wells-current-confirm-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：sphere-exclusion-current-26462009

<!-- official:sphere-exclusion-current-26462009:436 -->

请求436完整正常结束，共14轮。官方最终日志均值为 **9:08.381（548.381游戏秒）**；逐轮日志重算均值为548.380785714秒，保留两者的显示舍入口径。

同构建前版完整均值1069.624571429秒/7轮；当前正式均值548.381秒/14轮，缩短约48.73%。实采煤铁支付勘探；全部锚点准备后重读最近距离，以球面和球内排除约束选择目标，实际挖掘验证，失败回退沟网。

部署源码SHA256：`bf4cff172302388f301a6f4270df835882c4f45eb17bd87ad3973a48b7d35164`。当前源码SHA256：`bbee2f6c2d2550eb688892e3c915d3c93df51070974f922c9b80ad33b1f420a4`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores_single/sphere-exclusion-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
