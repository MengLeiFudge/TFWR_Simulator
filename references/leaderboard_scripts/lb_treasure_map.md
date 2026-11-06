# 藏宝图（treasure_map）

2026-11-06：新增可复核基线，目标为115000 Gold。目前证据包含当前源码的三seed完整目标模拟和一次普通场景实机对照；已取得构建26462009的正式完整统计，见末节。

## 当前实现

单机找到Basalt并读地图坐标，到达Treasure_Map后只读一次路线。按N/E/S/W/D逐字符执行，保留回头路，每个D只挖一次；最后验证Underground_Treasure再harvest。

主要成员：`lb_treasure_map`、`treasure_map_move_to`。最多256张地图、7200游戏秒；每张Basalt搜索256步、地图定位32步，所有动作失败均明确停止。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 292.105493040 游戏秒 | 当前源码、原榜单目标；各seed见下表 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 277.200 游戏秒 | 构建26462009，请求354，26轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 292.613369760 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/treasure-map/seeds1-2-3.json` |
| 2 | 282.295285740 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/treasure-map/seeds1-2-3.json` |
| 3 | 301.407823620 | 已达到原目标 | `.codex/leaderboard-sol/underground-strategies/treasure-map/seeds1-2-3.json` |

首版部署源码 SHA256：`b39cf5aa09bb6a95e3347f8bd40e56b8b58e57ea51599511ffa76c7be39c9709`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[115000,40000],"ordinary_world_size":8,"ordinary_max_drones":1}`；正式榜原目标仍由上方三seed验证。

请求 `330` 正常结束。本地与原生simulate完整返回时间均为 **135.558639540 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/treasure_map/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`2eaa436434bdba8b3a61f61c8a27e72b84af528901956698f4038b4c4ff21fc6`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

路线首个D已经处理地图块，额外预挖会改变路径状态。当前版本不压缩路线，不跨无人机交接，不在路径内clear或重定位。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。已在当前源码的字节副本上运行ty LSP；游戏类型桩缺少`Grounds.Block_Red`、`Unlocks.Underground_Leaderboard`，并把按实体/地面变化的measure返回值合并成联合类型，因而LSP仍有相关诊断。未修改游戏外部类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:354 -->

请求354完整正常结束，共26轮。官方最终日志均值为 **4:37.200（277.200游戏秒）**；逐轮日志重算均值为277.200153846秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`b39cf5aa09bb6a95e3347f8bd40e56b8b58e57ea51599511ffa76c7be39c9709`。当前源码SHA256：`f67e162a082dd02872dca495c1bbb2e84ac0115860cd6bad9c1747f8e03d2260`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/treasure_map/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
