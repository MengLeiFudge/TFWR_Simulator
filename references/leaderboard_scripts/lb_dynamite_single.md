# 炸药单机（dynamite_single）

2026-11-06：新增可复核基线，目标为100000 Dynamite。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

单机维护公开数字与SAFE/MINE事实，先做直接和子集推理，停滞后有限低风险猜测。仅当所有剩余格都已证明为雷时，才挖已揭开的Soot完成一次人工结算；踩雷后按真实盘面变化收口。

主要成员：`dynamite_solve`、`worker`、`dig_target`、`dynamite_guess`、`prepare_all`。最多512盘、14400游戏秒、每盘32次猜测。来源为本机既有Dynamite.py，必需逻辑已内联；不跳层、不新增存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1244.993221770 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1104.637298130 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite_single/final-seed1/report.json` |
| 2 | 1353.980460240 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite_single/final-seed2/report.json` |
| 3 | 1276.361906940 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite_single/final-seed3/report.json` |

源码 SHA256：`d4a9964459e78aa2471e31476f2723f0d897209e91689da117869126e38f3af3`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":2048,"find_stratum_limit":2048,"ordinary_world_size":8}`；正式榜原目标仍由上方三seed验证。

请求 `334` 正常结束。本地与原生simulate完整返回时间均为 **123.470998020 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/dynamite_single/ordinary-pair-v4/game-seed1/comparison.json`。派生脚本 SHA256：`deae1518e4517868c88a5919ec12ac9b17d362436ff41541b1bf1589884ee8f1`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

批次候选约2692秒、并行规划候选约4133秒，均慢于本机既有约束求解结构，因此保留串行结构。移除了没有调用路径的区域派发包装。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
