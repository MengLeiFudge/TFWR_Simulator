# 地下Reset（fastest_underground_reset）

2026-11-06：新增可复核基线，目标为解锁Underground_Leaderboard。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

从零库存按当前get_cost筹集资源，逐步发展6×6单机与Mining6，采集稻米、竹子、藏宝图、蘑菇、扫雷资源，最后支付20000 Dynamite和200000 Bamboo解锁Underground_Leaderboard。每次unlock前复核整个成本字典。

主要成员：`lb_fastest_underground_reset`、`ur_need`、`ur_farm`、`ur_mine`及`ur_*_stock`。主流程72000游戏秒；农作7200秒、逐层矿采18000秒；蘑菇/扫雷另有有界盘数、连续未命中和总时间限制。仅复用公开API；基础与地下采集代码内联，存档只需临时已有test/simulate文件。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 34334.579200415 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 35057.738444295 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/final-seed1/report.json` |
| 2 | 34607.997515035 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/final-seed2/report.json` |
| 3 | 33338.001641915 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/final-seed3/report.json` |

源码 SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

正式脚本原字节，无目标缩减；显式传入Reset初始科技和零库存。普通生成与该Reset配置同样不强制特殊地形。

请求 `335` 正常结束。本地与原生simulate完整返回时间均为 **35057.738444295 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/ordinary-pair-v1/game-seed1/comparison.json`。实机脚本 SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

该Reset的原脚本整轮同seed对照已完成；其余seed为本地预测。

## 候选与已处理边界

首轮发现Grass即时再生导致Bush未种下；改为按目标实体补种。逐项筹资会消耗前项的种子资源，现最多8轮复核整组库存。普通地层可能未生成目标层，搜层256次未命中后有限clear重试，连续8次失败才停止；不能套用资源榜强制地形。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。普通Reset搜层未命中的生成原因仍未定位，有限重试已经通过三seed和整轮实机，但不能据此宣称修复模型。
