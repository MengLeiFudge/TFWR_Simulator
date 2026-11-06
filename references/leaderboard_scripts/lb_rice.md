# 稻米（rice）

2026-11-06：新增可复核基线，目标为2000000 Rice。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

每列唯一写者，在实际Clay上种植。每片处理两轮可用粘土，等待成熟时用do_a_flip推进一游戏秒；全体句柄回收后才clear下一片。

主要成员：`rice_columns`、`rice_move_to`。最多128片、3600游戏秒；岩层停止当前柱，不挖坏其他尚未成熟的稻米。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 189.961860450 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 189.949898790 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/rice/deep-cover-seed1/report.json` |
| 2 | 189.696728610 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/rice/deep-cover-seed2/report.json` |
| 3 | 190.238953950 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/rice/deep-cover-seed3/report.json` |

源码 SHA256：`7b486c35c2ec470f255fc1bf083683f37b27ba20f32f4c190d6db8cb98d4ff77`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[2000000,8192],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `324` 正常结束。本地与原生simulate完整返回时间均为 **9.523017720 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/rice/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`3e54352fc015e1431c0ff7168d86bd7188e9b2c36af8d9c96745bf08e894a58a`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

忙轮询候选触及语句预算；一秒等待降低了本地执行开销，保持实际成熟后收获。普通地层的搜Clay上限为128次dig。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
