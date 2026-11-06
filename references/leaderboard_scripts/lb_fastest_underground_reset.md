# 地下Reset（fastest_underground_reset）

2026-11-06：新增可复核基线，目标为解锁Underground_Leaderboard。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

从零库存按当前get_cost筹集资源，逐步发展6×6单机与Mining6。Expand4后先准备Grass2、Trees2、Carrots2和Speed5，再进入竹子、藏宝图、蘑菇与扫雷资源阶段，最后支付20000 Dynamite和200000 Bamboo解锁Underground_Leaderboard。每次unlock前复核整个成本字典；Carrot种子成本随科技倍率增加，仍按get_cost实付。

主要成员：`lb_fastest_underground_reset`、`ur_need`、`ur_farm`、`ur_mine`及`ur_*_stock`。主流程72000游戏秒；农作7200秒、逐层矿采18000秒；蘑菇/扫雷另有有界盘数、连续未命中和总时间限制。仅复用公开API；基础与地下采集代码内联，存档只需临时已有test/simulate文件。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 28416.469521305 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 29133.641 游戏秒 | 构建26462009，请求366，1轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 28410.363445127 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-model-seed1/report.json` |
| 2 | 30241.142704110 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-model-seed2/report.json` |
| 3 | 26597.902414677 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-model-seed3/report.json` |

首版部署源码 SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

正式脚本原字节，无目标缩减；显式传入Reset初始科技和零库存。普通生成与该Reset配置同样不强制特殊地形。

请求 `335` 正常结束。本地与原生simulate完整返回时间均为 **35057.738444295 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/fastest_underground_reset/ordinary-pair-v1/game-seed1/comparison.json`。实机脚本 SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

该Reset的原脚本整轮同seed对照已完成；其余seed为本地预测。

## 候选与已处理边界

首轮发现Grass即时再生导致Bush未种下；改为按目标实体补种。逐项筹资会消耗前项的种子资源，现最多8轮复核整组库存。普通地层可能未生成目标层，搜层256次未命中后有限clear重试，连续8次失败才停止；不能套用资源榜强制地形。

提前Speed4、Speed5、补给科技配套Speed5为本轮有限代表。seed1模型依次为32480.250879794、29090.295371570、28410.363445127秒，原版同seed为35057.738444295秒。配套Speed5的三seed均值28416.469521305秒，候选正式请求361为27638.810秒，迁入真源后的请求366为29133.641秒，当前成绩采用后一次完整复验。不同正式盘面有波动；两次结果都优于原31535.109秒，不能把样本差异当成同seed模型误差。没有枚举任意科技顺序。

## 静态检查与后续

AST解析、仓库游戏语法检查、入口结构及禁止jump的静态检查通过。与当前执行逻辑一致的源码副本（仅时间注释不同）的ty LSP有10项错误、25项提示：外部桩缺少Underground_Leaderboard，measure联合类型不能按竹子、藏宝图、Soot上下文收窄；其余为spawn/None不可达或既有未使用局部变量。新增四项科技枚举无诊断；未修改外部游戏类型桩。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。普通Reset搜层未命中的生成原因仍未定位，有限重试已经通过三seed和整轮实机，但不能据此宣称修复模型。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:355 -->

请求355完整正常结束，共1轮。官方最终日志均值为 **525:35.109（31535.109游戏秒）**；逐轮日志重算均值为31535.109000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`e0d06a2030e6710ff353a31dba813d1406d27121ba54973f9e65aaaacbcfddcc`。当前源码SHA256：`8cce2ed22c106fc544ea59df52ff5bdfe65d18627b7f0cd94df191a953cee048`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：supply-speed5-26462009

<!-- official:supply-speed5-26462009:361 -->

请求361完整正常结束，共1轮。官方最终日志均值为 **460:38.810（27638.810游戏秒）**；逐轮日志重算均值为27638.810000000秒，保留两者的显示舍入口径。

同构建前版完整均值31535.109000000秒/1轮；当前正式均值27638.810秒/1轮，缩短约12.36%。Expand4后依次准备Grass2、Trees2、Carrots2和Speed5，继续读取真实get_cost支付各阶段资源，其他阶段与采集逻辑不变。

部署源码SHA256：`b974caa96347c3149631f02fc09c8a491a04f323eed26298a8271ee818642d43`。当前源码SHA256：`a6a149a2d1d00162d81e2d0bdd6bd1d2df0350ca22eefcaeaefb735d4cae1e06`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：supply-speed5-current-26462009

<!-- official:supply-speed5-current-26462009:366 -->

请求366完整正常结束，共1轮。官方最终日志均值为 **485:33.641（29133.641游戏秒）**；逐轮日志重算均值为29133.641000000秒，保留两者的显示舍入口径。

同构建前版完整均值31535.109000000秒/1轮；当前正式均值29133.641秒/1轮，缩短约7.62%。Expand4后依次准备Grass2、Trees2、Carrots2和Speed5，继续读取真实get_cost支付各阶段资源，其他阶段与采集逻辑不变。

部署源码SHA256：`a6a149a2d1d00162d81e2d0bdd6bd1d2df0350ca22eefcaeaefb735d4cae1e06`。当前源码SHA256：`a640359cc042414b04db423c29a94582d6200d524c364b0f5241e12b05ebc6f3`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/fastest_underground_reset/supply-speed5-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
