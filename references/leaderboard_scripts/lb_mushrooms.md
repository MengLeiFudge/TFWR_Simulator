# 蘑菇（mushrooms）

2026-11-06：新增可复核基线，目标为240000 Mushroom。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

主孔先找到Mushroom顶面，再一次派发把全田准备到同一高度。按不相交矩形分区做同色推送和双邻配对。非蘑菇接收柱须先找到两块同色且高出共同floor至少两格的邻块，才挖到floor；遇到新蘑菇立即保留。保留(0,0)采样柱，整层工人全部结束后主机才推进采样高度。

主要成员：`dig_layer`、`dig_columns`、`make_blocks`、`run_layer`、`work_layer`、`push_match`、`feed_column`。最多128片、7200游戏秒；每个工人受共同两格高度带限制，失败仍先回收全部句柄。来源为本机既有Mushroom.py，必需逻辑已内联，无新存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 566.820213930 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 557.267 游戏秒 | 构建26462009，请求357，13轮，正常完整结束 |

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

逐覆盖层全田派发的旧版约1201秒/多机、2826秒/单机。单孔定位后一次准备减少了覆盖层派发与等待。空接收柱候选的多机版已通过三seed模型及请求357的13轮完整统计，正式均值557.267秒，较原572.673秒缩短约2.69%。单机同改动在请求358中更慢，未同步保留。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。当前源码字节副本的ty LSP无错误，3项提示分别为两处spawn_drone类型桩的None分支不可达和既有循环变量y未使用。保留运行时失败处理，未修改外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

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
