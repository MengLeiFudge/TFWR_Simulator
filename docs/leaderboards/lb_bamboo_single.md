# 竹子单机（bamboo_single）

2026-11-06：新增可复核基线，目标为25000000 Bamboo。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

先按(x+2y)%5构造空中心，环边未被四邻覆盖的格子也留空。每株竹子唯一分配给一个实际相邻空中心；单机8×8实机得到46个种植位、18个空中心。低飞只在空中心与本株之间出入，转移高飞18；保留两次切花、第三次整收及切花成功验证。父机规划约0.62游戏秒，已计入完整成绩。

主要成员：`lb_bamboo_single`、`bamboo_fans`、`bamboo_move_to`。规划只遍历有限格点与四邻，支持环边；生产最多3600游戏秒，按实际库存退出。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 961.959989400 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 956.579 游戏秒 | 构建26462009，请求364，8轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 960.789063600 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo_single/star-model-seed1/report.json` |
| 2 | 962.005202280 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo_single/star-model-seed2/report.json` |
| 3 | 963.085702320 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/bamboo_single/star-model-seed3/report.json` |

首版部署源码 SHA256：`f8c5298651d7dc05dfb62ad2f372932999ec75f4142aad17480fabaf6f1710d2`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[25000000,200000],"ordinary_world_size":8,"ordinary_max_drones":1}`；正式榜原目标仍由上方三seed验证。

请求 `323` 正常结束。本地与原生simulate完整返回时间均为 **28.670617530 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/bamboo_single/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`6817e463c7e9a77d8e852b9b28e44e3c450e33eaf13d64d88b78ef1035d38c23`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首花即整株收获的旧候选吞吐不足；保干跨两次花节能取得完整茎秆的平方收益。未确认切花成功就推进阶段的候选已归档。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。当前源码字节副本的ty LSP有2项错误和3项提示：measure联合类型桩不能推断竹子高度是数值；spawn_drone桩把None分支标为不可达，初始化phase的x/y未使用。保留运行时失败处理，未修改外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:341 -->

请求341完整正常结束，共7轮。官方最终日志均值为 **18:15.017（1095.017游戏秒）**；逐轮日志重算均值为1095.017428571秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`f8c5298651d7dc05dfb62ad2f372932999ec75f4142aad17480fabaf6f1710d2`。当前源码SHA256：`2fd3a0105889aa3fa7c75b7989c00c7fae37bc6344746c6a9cedee7f8945e907`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo_single/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：star-26462009

<!-- official:star-26462009:360 -->

请求360完整正常结束，共8轮。官方最终日志均值为 **16:07.961（967.961游戏秒）**；逐轮日志重算均值为967.961500000秒，保留两者的显示舍入口径。

同构建前版完整均值1095.017428571秒/7轮；当前正式均值967.961秒/8轮，缩短约11.60%。空中心按四邻覆盖分配全部非中心植株，环边未覆盖格也留空；每株仅一个工人写入，低飞只在空中心与本株间往返，所有转移高飞18。

部署源码SHA256：`6c57d180e1f577c80c2357a139d04cc7e0577bb67a5e2615f618bd21cab890fb`。当前源码SHA256：`7df0547cfd91bac100180aa2f9d258006e5ef21f82ee8cecea565ca64f8d2d8e`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo_single/star-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：star-current-26462009

<!-- official:star-current-26462009:364 -->

请求364完整正常结束，共8轮。官方最终日志均值为 **15:56.579（956.579游戏秒）**；逐轮日志重算均值为956.579375000秒，保留两者的显示舍入口径。

同构建前版完整均值1095.017428571秒/7轮；当前正式均值956.579秒/8轮，缩短约12.64%。空中心按四邻覆盖分配全部非中心植株，环边未覆盖格也留空；每株仅一个工人写入，低飞只在空中心与本株间往返，所有转移高飞18。

部署源码SHA256：`7df0547cfd91bac100180aa2f9d258006e5ef21f82ee8cecea565ca64f8d2d8e`。当前源码SHA256：`232b7d18c3f515a1bea41295d7e76c468dcbc08188a92ce9789a7710cbabee80`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo_single/star-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
