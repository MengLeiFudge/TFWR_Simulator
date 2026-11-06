# 石英矿（ores）

2026-11-06：新增可复核基线，目标为20000 Quartz。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；已取得构建26462009的正式完整统计，见末节。

## 当前实现

每个x唯一写者，错开布置两口稀疏井。排行榜首石英区块为32–47，针长8/9，交叉层选39；实际dig收取沿途矿块，到交叉层后只追挖当前连续Quartz。

主要成员：`ore_wells`、`ore_move_to`。最多512片、7200游戏秒；连续8片零收益明确失败。普通场景首石英区块48–63，因此实机诊断将交叉层单独改为55。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 871.942078110 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 867.389 游戏秒 | 构建26462009，请求346，9轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 854.025486750 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores/sparse-seed1/report.json` |
| 2 | 869.039894070 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores/sparse-seed2/report.json` |
| 3 | 892.760853510 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/ores/sparse-seed3/report.json` |

首版部署源码 SHA256：`8cfd45ff6858ee4b947cb42b485fd55860e9fac1203707b237fdd899f480e577`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[20000,128],"ordinary_world_size":8,"ordinary_max_drones":8,"quartz_cross_section":[39,55]}`；正式榜原目标仍由上方三seed验证。

请求 `326` 正常结束。本地与原生simulate完整返回时间均为 **17.191703790 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/ores/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`5a16693802c5d74dd5560298775ef9c9008fac68d240adc9c7b5e9f2e8035120`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

逐层剥离全田的单机候选在7200秒仅得到3432 Quartz，未达4000目标。当前稀疏井省去大部分空岩挖掘与付费探测；不读取隐藏针的位置或预记产量。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:346 -->

请求346完整正常结束，共9轮。官方最终日志均值为 **14:27.389（867.389游戏秒）**；逐轮日志重算均值为867.388777778秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`8cfd45ff6858ee4b947cb42b485fd55860e9fac1203707b237fdd899f480e577`。当前源码SHA256：`e0981b521b68d9fd1b4c2d6ed74bdde2871e071b474f8994505408222c858173`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/ores/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
