# 竹子（bamboo）

2026-11-06：新增可复核基线，目标为500000000 Bamboo。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；已取得构建26462009的正式完整统计，见末节。

## 当前实现

每列唯一写者，偶数行种竹、奇数行通行。高飞到专属通道，前两次开花只切花节并确认measure增长；第三次开花后整株收获、补种。所有子机返回后才结束。

主要成员：`bamboo_columns`、`bamboo_move_to`。最多3600游戏秒；按实际库存退出，不把株数或未来产量计入目标。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1010.184189870 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 1003.920 游戏秒 | 构建26462009，请求340，8轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1012.934384010 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/bamboo/checked/seed1.json` |
| 2 | 1007.680526640 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/bamboo/checked/seed2.json` |
| 3 | 1009.937658960 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/bamboo/checked/seed3.json` |

首版部署源码 SHA256：`6603de2d3e543992153548d70f2445d4764dc2b99ff2d86735782843bdfa45a6`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[500000000,400000],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `322` 正常结束。本地与原生simulate完整返回时间均为 **16.517296620 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/bamboo/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`3e1aa11c6474f2470b2f0e053b169d73a324488a34242544815197ac342f37fd`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首花即整株收获的旧候选吞吐不足；保干跨两次花节能取得完整茎秆的平方收益。未确认切花成功就推进阶段的候选已归档。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:340 -->

请求340完整正常结束，共8轮。官方最终日志均值为 **16:43.920（1003.920游戏秒）**；逐轮日志重算均值为1003.920375000秒，保留两者的显示舍入口径。原协调器因test前缀漏认汇总；本值从该请求已存在的完整模组日志恢复，原始回执保留不改。

当前结构完成首次正式统计。

部署源码SHA256：`6603de2d3e543992153548d70f2445d4764dc2b99ff2d86735782843bdfa45a6`。当前源码SHA256：`f622052913d38bd2d417ed6b3dbf7e18bcec7e6b1c5b5e93dc31a6e45c7a7dd3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/bamboo/baseline-26462009/summary-recovered.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
