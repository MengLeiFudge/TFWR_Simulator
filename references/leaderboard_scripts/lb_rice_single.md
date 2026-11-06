# 稻米单机（rice_single）

2026-11-06：新增可复核基线，目标为100000 Rice。当前流水结构已完成三seed原目标模拟和构建26462009的正式完整统计；首版普通场景对照保留在历史节。

## 当前实现

每列唯一写者，先种满首层；逐株成功收割后立即准备并播种该柱下一Clay。第二层成长与首层余下收割重叠，最后回访第二层清单。等待时用do_a_flip，全部句柄回收后才clear。

主要成员：`rice_columns`、`rice_move_to`。最多128片、3600游戏秒；等待当前未收株时不下挖，成功收获后才准备下一Clay。下挖可能改变邻柱高度，按实际地面和实体状态处理。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 174.989757900 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 174.566 游戏秒 | 构建26462009，请求345，42轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 175.909653450 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice_single/pipeline-model-seed1/report.json` |
| 2 | 174.396558330 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice_single/pipeline-model-seed2/report.json` |
| 3 | 174.663061920 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice_single/pipeline-model-seed3/report.json` |

首版部署源码 SHA256：`19b13c8790271db7e3bffc95a6debaf54f8c57be1cec3480c59260527c132aab`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[100000,2048],"ordinary_world_size":8,"ordinary_max_drones":1}`；正式榜原目标仍由上方三seed验证。

请求 `325` 正常结束。本地与原生simulate完整返回时间均为 **9.595610730 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/rice_single/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`6bd95f0fdb8b39da54ea3c077b0741ad2c0e7bff6577fbcda9718b07f90fa38f`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

忙轮询候选触及语句预算；一秒等待降低了本地执行开销，保持实际成熟后收获。普通地层的搜Clay上限为128次dig。

## 静态检查与后续

当前流水源码已通过AST、游戏执行和入口结构检查。ty LSP检查当前源码字节副本，无错误；仅一条游戏类型桩将spawn_drone标为非空返回而产生的不可达提示。保留真实API可能返回None时的失败处理，未修改外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：pipeline-26462009

<!-- official:pipeline-26462009:345 -->

请求345完整正常结束，共42轮。官方最终日志均值为 **2:54.566（174.566游戏秒）**；逐轮日志重算均值为174.565690476秒，保留两者的显示舍入口径。

同构建旧结构完整统计为202.351027778秒/36轮；当前结构正式均值174.566秒，缩短约13.73%。每株首层成功harvest后立即挖去干梯田，仅在实际露出下一Clay时种第二株，第二层成熟与首层剩余收割重叠；全部工人退出后才clear。

部署源码SHA256：`7fe605636e8e2bb960194f6528dba6f42155cf08e3ee011c6a27fd8f9a7874e1`。当前源码SHA256：`17c596655d4ce5ce4f97d75fd29bfe86b79309ba751da9cecb9cda00c9d86bf6`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/rice_single/pipeline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
