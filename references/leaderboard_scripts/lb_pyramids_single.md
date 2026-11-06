# 金字塔单机（pyramids_single）

2026-11-06：新增可复核基线，目标为30000 Power。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

4格间隔采样定位Sand/Limestone，再从实际Limestone高度探测正方形边界。清空足印上方、在足印外补齐Block，按离边缘距离逐列放置彩块。所有构造工人结束后才去中心验证、等待并收取Sunflower。

主要成员：`pyramid_find`、`pyramid_bounds`、`pyramid_materials`、`pyramid_dispatch`、`pyramid_build_column`。最多512片、14400游戏秒；找层每片最多128层/600秒。库存目标加100 Power缓冲，补偿末尾动作耗电。不能把模型预测写成官方成绩。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 3950.203908905 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 3924.364206101 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/pyramids_single/materials-seed1/report.json` |
| 2 | 3967.120817115 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/pyramids_single/materials-seed2/report.json` |
| 3 | 3959.126703500 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/pyramids_single/materials-seed3/report.json` |

源码 SHA256：`b8896be7f9004d1a853d8ba2b3247577e71b2ff234fecd86cabfde406462e079`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[30100,100],"ordinary_world_size":8,"ordinary_max_drones":1}`；正式榜原目标仍由上方三seed验证。

请求 `329` 正常结束。本地与原生simulate完整返回时间均为 **155.113342660 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/pyramids_single/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`e9b13122c7848c7f09ee99c4eb70f572abdd907210b64f0e8d5eda5bf6e7fa11`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首版在数轮后缺Block，构造失败。当前版按实际体积预算补料，足印外只挖到基座高度；仍不足时保留已收材料并重生下一片，避免挖穿基座。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
