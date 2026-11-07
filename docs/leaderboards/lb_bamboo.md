# 竹子（bamboo）

2026-11-06：目标为500000000 Bamboo。当前空中心四邻版已完成三seed原目标模拟及构建26462009的11轮正式统计；普通场景对照保留为首版历史证据。

## 当前实现

先按(x+2y)%5构造空中心，环边仍未被四邻覆盖的格子也留空。每株竹子唯一分配给一个实际相邻空中心，空中心按32个矩形区分给工人；32×32实机得到794个种植位、230个空中心。低飞只在空中心与本株之间出入，转移高飞18；保留两次切花、第三次整收及切花成功验证，等待全部子机后结束。父机规划约9.83游戏秒，已计入完整成绩。

主要成员：`lb_bamboo`、`bamboo_fans`、`bamboo_move_to`。规划只遍历有限格点与四邻，支持环边；生产最多3600游戏秒，按实际库存退出。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 706.452786360 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 705.024 游戏秒 | 构建26462009，请求363，11轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 706.091138190 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo/star-model-seed1/report.json` |
| 2 | 704.847345030 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo/star-model-seed2/report.json` |
| 3 | 708.419875860 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo/star-model-seed3/report.json` |

首版部署源码 SHA256：`6603de2d3e543992153548d70f2445d4764dc2b99ff2d86735782843bdfa45a6`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[500000000,400000],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `322` 正常结束。本地与原生simulate完整返回时间均为 **16.517296620 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/bamboo/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`3e1aa11c6474f2470b2f0e053b169d73a324488a34242544815197ac342f37fd`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首花即整株收获的旧候选吞吐不足；保干跨两次花节能取得完整茎秆的平方收益。未确认切花成功就推进阶段的候选已归档。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。当前源码字节副本的ty LSP有2项错误和3项提示：measure联合类型桩不能推断竹子高度是数值；spawn_drone桩把None分支标为不可达，初始化phase的x/y未使用。保留运行时失败处理，未修改外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:340 -->

请求340完整正常结束，共8轮。官方最终日志均值为 **16:43.920（1003.920游戏秒）**；逐轮日志重算均值为1003.920375000秒，保留两者的显示舍入口径。原协调器因test前缀漏认汇总；本值从该请求已存在的完整模组日志恢复，原始回执保留不改。

当前结构完成首次正式统计。

部署源码SHA256：`6603de2d3e543992153548d70f2445d4764dc2b99ff2d86735782843bdfa45a6`。当前源码SHA256：`f622052913d38bd2d417ed6b3dbf7e18bcec7e6b1c5b5e93dc31a6e45c7a7dd3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo/baseline-26462009/summary-recovered.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：horizontal-26462009

<!-- official:horizontal-26462009:356 -->

请求356完整正常结束，共8轮。官方最终日志均值为 **16:18.167（978.167游戏秒）**；逐轮日志重算均值为978.166500000秒，保留两者的显示舍入口径。

同构建原列巡回完整均值为1003.920375000秒/8轮；双机分半行横巡为978.167秒/8轮，缩短约2.57%。端点不连续重复检查，仍保留两次切花和第三次整收；实际收益由本次完整统计确认。

部署源码SHA256：`516fe040c02bdfe99ea8d0931a1259adbe5b1c50c05b193740782bfaf3a4207f`。当前源码SHA256：`3aa3eb3302e395587de13ef1f539926adba79ab2e90afeb5ed9a79f092f35306`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo/horizontal-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：star-26462009

<!-- official:star-26462009:359 -->

请求359完整正常结束，共11轮。官方最终日志均值为 **11:42.715（702.715游戏秒）**；逐轮日志重算均值为702.714636364秒，保留两者的显示舍入口径。

同构建前版完整均值978.166500000秒/8轮；当前正式均值702.715秒/11轮，缩短约28.16%。空中心按四邻覆盖分配全部非中心植株，环边未覆盖格也留空；每株仅一个工人写入，低飞只在空中心与本株间往返，所有转移高飞18。

部署源码SHA256：`27ada1af52fe9a8d0801a885327625a3b3c41863db2a9aa51e7f2830fe34f058`。当前源码SHA256：`d6bafb4dd2742bdadceeea9c650389ff77720ece0c2364662e30ecfd7c03ce05`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo/star-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：star-current-26462009

<!-- official:star-current-26462009:363 -->

请求363完整正常结束，共11轮。官方最终日志均值为 **11:45.024（705.024游戏秒）**；逐轮日志重算均值为705.024545455秒，保留两者的显示舍入口径。

同构建前版完整均值978.166500000秒/8轮；当前正式均值705.024秒/11轮，缩短约27.92%。空中心按四邻覆盖分配全部非中心植株，环边未覆盖格也留空；每株仅一个工人写入，低飞只在空中心与本株间往返，所有转移高飞18。

部署源码SHA256：`d6bafb4dd2742bdadceeea9c650389ff77720ece0c2364662e30ecfd7c03ce05`。当前源码SHA256：`a5ecf050e6cd514ea0e8e8ef78a6f9a115679aae3f954853429aa99834a260f2`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo/star-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
