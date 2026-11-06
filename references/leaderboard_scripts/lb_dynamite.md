# 炸药（dynamite）

2026-11-06：新增可复核基线，目标为10000000 Dynamite。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；尚未取得正式排行榜完整统计。

## 当前实现

逐列准备到同一Dynamite顶面，再由唯一协调机合并实际Soot数字并作确定性约束、有限子集推理。工人只挖自己列的已证明安全格并返回事实；快照在全部wait之前只读。停滞后有限猜测，最后按实际结算库存决定收益。

主要成员：`dynamite_prepare`、`dynamite_solve`、`dynamite_phase`、`dynamite_column`、`dynamite_subset`、`dynamite_guess`。最多512盘、24000游戏秒，每盘最多32次猜测与2048批；子集最多比较4096对。传播达到16轮时重建快照，避免拿过期约束作证明。公开启发式不作为安全证明，也不读取隐藏雷或随机状态。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 6708.185128770 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 未取得 | 尚无finished=true的官方完整统计 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 6589.968591690 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite/terminal-fixed-seed1/report.json` |
| 2 | 6798.148224930 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite/terminal-fixed-seed2/report.json` |
| 3 | 6736.438569690 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/dynamite/terminal-fixed-seed3/report.json` |

源码 SHA256：`824e5a96fcd969f5c7ffdf5357328c56546866672f19dd454bb40918569d1fa6`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 实机对照

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":4096,"find_stratum_limit":2048,"ordinary_world_size":8}`；正式榜原目标仍由上方三seed验证。

请求 `333` 正常结束。本地与原生simulate完整返回时间均为 **174.568575780 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/dynamite/ordinary-pair-v4/game-seed1/comparison.json`。派生脚本 SHA256：`1b011122ada60d127216d96030065a6c8703a266b61c79507d0247fc94c95a22`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

区域版与并行规划候选未表现出更低的本地游戏时间。当前批次版保留同批数字冲突检查；动作失败为error。成功结算可保留原深度下一格Soot，此时measure=None表示该盘数字表已移除，按ended收口。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)做正式榜至少两轮筛选与一次完整统计；只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。
