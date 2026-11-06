# 金字塔（pyramids）

2026-11-06：新增可复核基线，目标为150000 Power。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

4格间隔采样定位Sand/Limestone，再从实际Limestone高度探测正方形边界。清除覆盖土时保留Sand；全部清理结束后预留中心最后一块，另作只读并行统计实际缺块。按完整底层的八邻支撑逐层补沙，每层回收全部工人；最后由主机单独放中心顶块，确认Sunflower后收取。缺料时只在足印外挖到基座高度，不穿透Limestone。

主要成员：`pyramid_find`、`pyramid_bounds`、`pyramid_clean_column`、`pyramid_missing_column`、`pyramid_sand_column`、`pyramid_dispatch`、`pyramid_materials`。最多512片、14400游戏秒；找层每片最多128层/600秒。库存目标加100 Power缓冲，补偿末尾动作耗电。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 4640.788273099 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 4738.376 游戏秒 | 构建26462009，请求370，2轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 4499.099799525 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/sand-repair-model-seed1/report.json` |
| 2 | 4420.789900508 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/sand-repair-model-seed2/report.json` |
| 3 | 5002.475119264 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/sand-repair-model-seed3/report.json` |

首版部署源码 SHA256：`0b434951ee261eba2cdcb38b25e01d7f595da89bfb65a644cdcaa778c4395337`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[150100,100],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `328` 正常结束。本地与原生simulate完整返回时间均为 **138.043508379 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/pyramids/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`ea8326468d448931840bb8af4701fee842c9a475d3f4d1081133cd30d5491eda`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首版彩块重建在数轮后缺Block，后改为按完整体积筹资。当前版保留尚存的沙体，只补实际缺块，并在所有清理和中心预留完成后重读高度，避免把并发塌方前的缓存当成最终预算。

Sand上层放置依赖下层八邻支撑，不能像彩块一样逐列一次堆到顶。中心顶块是完成屏障：全部工人退出后才放置，防止金字塔完成自动清场时其他工人仍在施工。该布局的多机三seed及请求368完整2轮已达标；单机因额外移动更慢，保留原彩块版，见对应文档。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。与当前执行逻辑一致的源码副本的ty LSP无错误，7项提示均为边界元组中未使用的局部变量；未修改外部游戏类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:352 -->

请求352完整正常结束，共2轮。官方最终日志均值为 **97:15.884（5835.884游戏秒）**；逐轮日志重算均值为5835.884000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`0b434951ee261eba2cdcb38b25e01d7f595da89bfb65a644cdcaa778c4395337`。当前源码SHA256：`b73d8a97b1034732110965688cc9cfbf7adf1157b79ea7886b5fd4c2a3d5f0ff`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/pyramids/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：sand-repair-26462009

<!-- official:sand-repair-26462009:368 -->

请求368完整正常结束，共2轮。官方最终日志均值为 **74:05.195（4445.195游戏秒）**；逐轮日志重算均值为4445.195000000秒，保留两者的显示舍入口径。

同构建前版完整均值5835.884000000秒/2轮；当前正式均值4445.195秒/2轮，缩短约23.83%。覆盖层清理保留Sand，缺块在全部清理完成后重新读取；按完整底层提供八邻支撑逐层补沙，中心顶块留到所有工人退出后由主机放置，避免提前完成自动清场。

部署源码SHA256：`316c5d2f046aef972da079ef693c30cf011d0dd4167d37a260a415f8aec8a4d4`。当前源码SHA256：`276de9eb3d4bad8e2281085518b7c48fe4d2d4daa102724b8f18d3d243b224eb`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/pyramids/sand-repair-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：sand-repair-current-26462009

<!-- official:sand-repair-current-26462009:370 -->

请求370完整正常结束，共2轮。官方最终日志均值为 **78:58.376（4738.376游戏秒）**；逐轮日志重算均值为4738.376000000秒，保留两者的显示舍入口径。

同构建前版完整均值5835.884000000秒/2轮；当前正式均值4738.376秒/2轮，缩短约18.81%。覆盖层清理保留Sand，缺块在全部清理完成后重新读取；按完整底层提供八邻支撑逐层补沙，中心顶块留到所有工人退出后由主机放置，避免提前完成自动清场。

部署源码SHA256：`276de9eb3d4bad8e2281085518b7c48fe4d2d4daa102724b8f18d3d243b224eb`。当前源码SHA256：`b8e2c21e5dcfa657999f1c666816b9408549cc2d41b28227441499d7ded2f78a`；最终仅更新时间注释和新实现的空白格式，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/pyramids/sand-repair-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
