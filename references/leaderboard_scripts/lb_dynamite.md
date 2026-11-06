# 炸药（dynamite）

2026-11-06：新增可复核基线，目标为10000000 Dynamite。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

逐列准备到同一Dynamite顶面，再由唯一协调机合并实际Soot数字并作确定性约束、有限子集推理。工人只挖自己列已证明安全的格子，随后仅回访本列尚无数字的格子，已知数字保留缓存；其他列稍后发生的零扩展由下一批补读。每批检查已知Soot的结算状态，全部wait完成后才合并事实。停滞后有限猜测，按实际结算库存决定收益。

主要成员：`dynamite_prepare`、`dynamite_solve`、`dynamite_phase`、`dynamite_column`、`dynamite_subset`、`dynamite_guess`。最多512盘、24000游戏秒，每盘最多32次猜测与2048批；子集最多比较4096对。传播达到16轮时重建快照，避免拿过期约束作证明。公开启发式不作为安全证明，也不读取隐藏雷或随机状态。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 5554.525546020 游戏秒 | 修正前历史三seed；塌方修正后已另重算seed1，见候选记录 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 5561.376 游戏秒 | 构建26462009，请求367，2轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 5436.202286790 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite/selective-observe-model-seed1/report.json` |
| 2 | 5626.161732960 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite/selective-observe-model-seed2/report.json` |
| 3 | 5601.212618310 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite/selective-observe-model-seed3/report.json` |

首版部署源码 SHA256：`824e5a96fcd969f5c7ffdf5357328c56546866672f19dd454bb40918569d1fa6`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":4096,"find_stratum_limit":2048,"ordinary_world_size":8}`；正式榜原目标仍由上方三seed验证。

请求 `333` 正常结束。本地与原生simulate完整返回时间均为 **174.568575780 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/dynamite/ordinary-pair-v4/game-seed1/comparison.json`。派生脚本 SHA256：`1b011122ada60d127216d96030065a6c8703a266b61c79507d0247fc94c95a22`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

区域版与并行规划候选未表现出更低的本地游戏时间。当前版只改变观察路径，保留同批数字冲突检查与动作失败error。旧模型seed1需4052971次get_pos_z和2099691次move；只回访本列未知格的三seed原目标均完成。候选请求362的正式2轮均值5431.146秒；迁入真源后的请求367完整2轮为5561.376秒，当前采用复验结果，仍优于原6796.005秒。

成功结算可保留原深度下一格Soot，此时measure=None表示该盘数字表已移除，按ended收口。即使本列没有未知格，也先检查当前已知Soot；不能因只扫未知格而漏掉终态。

2026-11-07按塌方修正后的模型重新完成当前版seed1，原10000000目标5436.202286790秒，与修前同seed相同。证据：`.codex/leaderboard-sol/underground-official/dynamite/selective-observe-cavein-model-seed1/report.json`；本表另外两个seed仍为历史预测。

覆盖层按需准备另作多机候选，保留列唯一写者、全wait后合并、公开推理和原目标。候选在约8182350/10000000库存的进度样本中为4384.980游戏秒，邻近基线样本约8181250库存为4439.056秒；这是限频采样，进行中阶段和库存不完全相同，不能当作等库存完整对照。可见潜在收益较小，已提前停止并优先评估其他瓶颈；候选未完成原目标，不进入实机、不迁入，也未据此断言严格更慢。证据为`.codex/leaderboard-sol/underground-official/dynamite/lazy-cover-model-seed1/early-stop.json`及原进度日志。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。与当前执行逻辑一致的源码副本（仅时间注释不同）的ty LSP无错误，有2项measure()==None分支不可达提示：外部类型桩未包含结算后的None，保留已由实机证明必要的终态判断。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:350 -->

请求350完整正常结束，共2轮。官方最终日志均值为 **113:16.005（6796.005游戏秒）**；逐轮日志重算均值为6796.005000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`824e5a96fcd969f5c7ffdf5357328c56546866672f19dd454bb40918569d1fa6`。当前源码SHA256：`1d18e6730be3249a044f62b4a14b907dacd9068b0336681859f89b97f0e61cca`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：selective-observe-26462009

<!-- official:selective-observe-26462009:362 -->

请求362完整正常结束，共2轮。官方最终日志均值为 **90:31.146（5431.146游戏秒）**；逐轮日志重算均值为5431.146500000秒，保留两者的显示舍入口径。

同构建前版完整均值6796.005000000秒/2轮；当前正式均值5431.146秒/2轮，缩短约20.08%。安全任务执行后仅回访本列未知格，已知数字缓存；每批仍核对实际结算、回收全部工人再合并，不从启发式生成安全结论。

部署源码SHA256：`a9532e0f827ab6ccbd53796c33f79049168c676c897f6daace5bd4da822eb360`。当前源码SHA256：`7e21667ee377efc45d6f2da085396fa35d5e145eb7e42d49235a4f3545c2c0d8`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite/selective-observe-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：selective-observe-current-26462009

<!-- official:selective-observe-current-26462009:367 -->

请求367完整正常结束，共2轮。官方最终日志均值为 **92:41.376（5561.376游戏秒）**；逐轮日志重算均值为5561.376500000秒，保留两者的显示舍入口径。

同构建前版完整均值6796.005000000秒/2轮；当前正式均值5561.376秒/2轮，缩短约18.17%。安全任务执行后仅回访本列未知格，已知数字缓存；每批仍核对实际结算、回收全部工人再合并，不从启发式生成安全结论。

部署源码SHA256：`7e21667ee377efc45d6f2da085396fa35d5e145eb7e42d49235a4f3545c2c0d8`。当前源码SHA256：`35e1089fb396ba9b2fcbfc49eb4a2dc6e9ac771a89df0029944669819187295a`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite/selective-observe-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
