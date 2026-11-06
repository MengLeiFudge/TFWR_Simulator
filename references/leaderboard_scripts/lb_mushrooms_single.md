# 蘑菇单机（mushrooms_single）

2026-11-06：新增可复核基线，目标为30000 Mushroom。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

主孔先找到Mushroom顶面，再一次派发把全田准备到同一高度。按不相交矩形分区做同色推送和双邻配对，保留(0,0)采样柱；整层工人全部结束后，主机才推进采样高度。

主要成员：`dig_layer`、`dig_columns`、`make_blocks`、`run_layer`、`work_layer`、`push_match`、`feed_column`。最多128片、7200游戏秒；每个工人受共同两格高度带限制，失败仍先回收全部句柄。来源为本机既有Mushroom.py，必需逻辑已内联，无新存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1371.143796240 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1395.108268740 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/mushrooms_single/single-probe-prepare-seed1/report.json` |
| 2 | 1333.373757390 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/mushrooms_single/single-probe-prepare-seed2/report.json` |
| 3 | 1384.949362590 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/mushrooms_single/single-probe-prepare-seed3/report.json` |

源码 SHA256：`ee2dd468bffb0ab9d4f17f98764a15c6469b48c538da9e8b5be4f53e9c9dd803`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":{"item":"Mushroom","amount":512},"ordinary_world_size":8,"find_stratum_limit":256}`；正式榜原目标仍由上方三seed验证。

请求 `332` 正常结束。本地与原生simulate完整返回时间均为 **29.665355760 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/mushrooms_single/ordinary-pair-v2/game-seed1/comparison.json`。派生脚本 SHA256：`71539f3dbbeccdb4267c2f0955543925983c7b7cf87bb7908c064eac3f991c5b`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐覆盖层全田派发的旧版约1201秒/多机、2826秒/单机。单孔定位后一次准备减少了覆盖层派发与等待；新的末层非蘑菇接收柱优化尚未混入当前版。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
