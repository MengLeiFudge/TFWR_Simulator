# 石英矿单机（ores_single）

2026-11-06：新增可复核基线，目标为4000 Quartz。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

每个x唯一写者，错开布置两口稀疏井。排行榜首石英区块为32–47，针长8/9，交叉层选39；实际dig收取沿途矿块，到交叉层后只追挖当前连续Quartz。

主要成员：`ore_wells`、`ore_move_to`。最多512片、7200游戏秒；连续8片零收益明确失败。普通场景首石英区块48–63，因此实机诊断将交叉层单独改为55。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1300.739989500 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1309.984816320 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores_single/sparse-seed1/report.json` |
| 2 | 1204.511781870 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores_single/sparse-seed2/report.json` |
| 3 | 1387.723370310 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores_single/sparse-seed3/report.json` |

源码 SHA256：`8d6b41dea5333b3e0807ab93a257304fa1694365cfc373cbb3169b8916c16392`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[4000,64],"ordinary_world_size":8,"ordinary_max_drones":1,"quartz_cross_section":[39,55]}`；正式榜原目标仍由上方三seed验证。

请求 `327` 正常结束。本地与原生simulate完整返回时间均为 **21.098557530 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/ores_single/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`73c5b126a01109c4467d27d5f27cf495b9b05ba02248ba60f93916c42a9bd5ea`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐层剥离全田的单机候选在7200秒仅得到3432 Quartz，未达4000目标。当前稀疏井省去大部分空岩挖掘与付费探测；不读取隐藏针的位置或预记产量。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
