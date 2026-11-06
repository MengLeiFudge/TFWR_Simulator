# 稻米（rice）

2026-11-06：新增可复核基线，目标为2000000 Rice。当前流水结构已完成三seed原目标模拟和构建26462009的正式完整统计；首版普通场景对照保留在历史节。

## 当前实现

每列唯一写者，先种满首层；逐株成功收割后立即准备并播种该柱下一Clay。第二层成长与首层余下收割重叠，最后回访第二层清单。等待时用do_a_flip，全部句柄回收后才clear。

主要成员：`rice_columns`、`rice_move_to`。最多128片、3600游戏秒；等待当前未收株时不下挖，成功收获后才准备下一Clay。下挖可能改变邻柱高度，按实际地面和实体状态处理。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 172.494434910 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 172.606 游戏秒 | 构建26462009，请求344，42轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 172.585519110 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice/pipeline-model-seed1/report.json` |
| 2 | 172.164775950 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice/pipeline-model-seed2/report.json` |
| 3 | 172.733009670 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/rice/pipeline-model-seed3/report.json` |

首版部署源码 SHA256：`7b486c35c2ec470f255fc1bf083683f37b27ba20f32f4c190d6db8cb98d4ff77`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[2000000,8192],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `324` 正常结束。本地与原生simulate完整返回时间均为 **9.523017720 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/rice/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`3e54352fc015e1431c0ff7168d86bd7188e9b2c36af8d9c96745bf08e894a58a`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

忙轮询候选触及语句预算；一秒等待降低了本地执行开销，保持实际成熟后收获。普通地层的搜Clay上限为128次dig。

## 静态检查与后续

当前流水源码已通过AST、游戏执行和入口结构检查。ty LSP检查当前源码字节副本，无错误；仅一条游戏类型桩将spawn_drone标为非空返回而产生的不可达提示。保留真实API可能返回None时的失败处理，未修改外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：pipeline-26462009

<!-- official:pipeline-26462009:344 -->

请求344完整正常结束，共42轮。官方最终日志均值为 **2:52.606（172.606游戏秒）**；逐轮日志重算均值为172.605761905秒，保留两者的显示舍入口径。

同构建旧结构完整统计为189.882289474秒/38轮；当前结构正式均值172.606秒，缩短约9.10%。每株首层成功harvest后立即挖去干梯田，仅在实际露出下一Clay时种第二株，第二层成熟与首层剩余收割重叠；全部工人退出后才clear。

部署源码SHA256：`a7ab182338e3b429bbaa6f1bf9bbe8c6133206c4db0cf45d4a4dba8c4bce3550`。当前源码SHA256：`3a03a7d36508dafc2032285496ddb95c1e825bde947a04951532521a3d149c84`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/rice/pipeline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
