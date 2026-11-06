# 蘑菇单机（mushrooms_single）

2026-11-06：新增可复核基线，目标为30000 Mushroom。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

主孔先找到Mushroom顶面，再一次派发把全田准备到同一高度。按不相交矩形分区做同色推送和双邻配对，保留(0,0)采样柱；整层工人全部结束后，主机才推进采样高度。

主要成员：`dig_layer`、`dig_columns`、`make_blocks`、`run_layer`、`work_layer`、`push_match`、`feed_column`。最多128片、7200游戏秒；当前单机采用共同三格高度带，保留实际高度回读和(0,0)采样柱；失败仍先回收全部句柄。来源为本机既有Mushroom.py，必需逻辑已内联，无新存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1180.015070370 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 1164.739 游戏秒 | 构建26462009，请求378，7轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1226.891828250 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms_single/band3-model-seed1/report.json` |
| 2 | 1148.126107860 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms_single/band3-model-seed2/report.json` |
| 3 | 1165.027275000 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/mushrooms_single/band3-model-seed3/report.json` |

首版部署源码 SHA256：`ee2dd468bffb0ab9d4f17f98764a15c6469b48c538da9e8b5be4f53e9c9dd803`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":{"item":"Mushroom","amount":512},"ordinary_world_size":8,"find_stratum_limit":256}`；正式榜原目标仍由上方三seed验证。

请求 `332` 正常结束。本地与原生simulate完整返回时间均为 **29.665355760 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/mushrooms_single/ordinary-pair-v2/game-seed1/comparison.json`。派生脚本 SHA256：`71539f3dbbeccdb4267c2f0955543925983c7b7cf87bb7908c064eac3f991c5b`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐覆盖层全田派发的旧版约1201秒/多机、2826秒/单机。单孔定位后一次准备减少了覆盖层派发与等待。末层空接收柱候选虽通过三seed模型，正式请求358未超过当时基线，因此保留不使用空接收柱的单机主线。

三格高度带只把共同floor由ceiling-2改为ceiling-3，让已公开的同色块有更多配对空间。三个模型seed均完成原30000目标；请求377完整7轮1186.730秒，迁入真源后的请求378完整7轮1164.739秒，当前采用378，较原1335.308秒缩短约12.77%。分区、采样柱、实际高度核对、同色证明和全部wait保持。多机空接收柱组合的三格候选未完成目标，未将此参数推广到多机。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。与当前三格带执行逻辑一致的源码副本的ty LSP无错误，3项提示分别为两处spawn_drone类型桩的None分支不可达和既有循环变量y未使用。未修改外部游戏类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:349 -->

请求349完整正常结束，共6轮。官方最终日志均值为 **22:15.308（1335.308游戏秒）**；逐轮日志重算均值为1335.308000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`ee2dd468bffb0ab9d4f17f98764a15c6469b48c538da9e8b5be4f53e9c9dd803`。当前源码SHA256：`f5a187947c79b2eee3d4913ef0bfc5b1a51bb2c6f7e8f17256eb37a97fbfe13b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms_single/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 空接收柱候选：未保留

请求358完成6轮正式完整统计，官方最终均值1344.643游戏秒；当前原版请求349为1335.308秒。本次候选实测慢约0.70%，盘面存在随机差异；三seed模型均值1341.851885700秒的改善没有在本次完整实机中兑现，未替换当前源码或成绩索引。

候选只在预先确认两邻块同色且高出floor至少两格后准备非蘑菇接收柱，保留分区、两格高度带、采样柱和等待全部工人的边界。未进行无界调参。

证据：`.codex/leaderboard-sol/underground-official/mushrooms_single/empty-receiver-26462009/summary.json`及同目录完整请求、部署清单、restoration记录；候选源码及三seed模型位于同榜empty-receiver-candidate/empty-receiver-model-seed1…3。双日志无新增Error/Exception；已有test.py/lb_start.py在同ID回idle后逐字节恢复，其余存档Python文件未变。

## 构建26462009正式统计：band3-26462009

<!-- official:band3-26462009:377 -->

请求377完整正常结束，共7轮。官方最终日志均值为 **19:46.730（1186.730游戏秒）**；逐轮日志重算均值为1186.729714286秒，保留两者的显示舍入口径。

同构建前版完整均值1335.308000000秒/6轮；当前正式均值1186.730秒/7轮，缩短约11.13%。把共同floor调整为ceiling-3，保留分区、采样柱、实际高度回读、同色推理及全部wait；更深高度带只保留已通过完整原目标验证的单机版本。

部署源码SHA256：`3c7cd8b2ac9723af03d80e32b1cf3accd84262562b5a0e2690bcbffb7c454c3b`。当前源码SHA256：`f195c579dfadb4ed78554de218fabb6544708e0046d8be0235059730906e628e`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms_single/band3-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：band3-current-26462009

<!-- official:band3-current-26462009:378 -->

请求378完整正常结束，共7轮。官方最终日志均值为 **19:24.739（1164.739游戏秒）**；逐轮日志重算均值为1164.738571429秒，保留两者的显示舍入口径。

同构建前版完整均值1335.308000000秒/6轮；当前正式均值1164.739秒/7轮，缩短约12.77%。把共同floor调整为ceiling-3，保留分区、采样柱、实际高度回读、同色推理及全部wait；更深高度带只保留已通过完整原目标验证的单机版本。

部署源码SHA256：`f195c579dfadb4ed78554de218fabb6544708e0046d8be0235059730906e628e`。当前源码SHA256：`11e6899fc5f92475f4077ed8c5d34fadd905bac82d8f0e3acf8c68a56ebca3fe`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/mushrooms_single/band3-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
