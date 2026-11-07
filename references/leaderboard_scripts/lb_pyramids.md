# 金字塔（pyramids）

2026-11-07：保沙定位与常驻修补候选已通过请求430完整5轮，1484.696秒；此前两次启动失败及恢复过程见末节。当前正式源码采用此结构，模型和实机分别记录；横向候选比较见[本地候选记录](underground_local_candidates.md)。

2026-11-06：新增可复核基线，目标为150000 Power。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

中央采样首16层，未找到塔则重生；保留Sand向边缘探测，再钻到Limestone。四向边界探测遇Sand即确认在塔内，避免整条轴钻穿。全部清土结束后读取缺块，常驻工人按精确Block消耗阈值同步层次；修补期间不再产出或以其他方式消耗Block。等待使用hover(1)，全部工人退出后主机放中心顶块并收取Sunflower。

主要成员：`pyramid_find`、`pyramid_bounds`、`pyramid_clean_column`、`pyramid_missing_column`、`pyramid_repair`、`pyramid_patch_layers`。最多512片，主流程14400游戏秒截止；每次修补共用120游戏秒截止，失败后仍回收全部工人。库存目标留100 Power缓冲。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1500.266529233 游戏秒 | 当前结构，原目标；地下资源快照来源26410308 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 1480.702 游戏秒 | 构建26462009，请求440，5轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1522.782332395 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/persistent-wait-model-seed1/report.json` |
| 2 | 1455.725979333 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/persistent-wait-model-seed2/report.json` |
| 3 | 1522.291275970 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/pyramids/persistent-wait-model-seed3/report.json` |

首版部署源码 SHA256：`0b434951ee261eba2cdcb38b25e01d7f595da89bfb65a644cdcaa778c4395337`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"target":[150100,100],"ordinary_world_size":8,"ordinary_max_drones":8}`；正式榜原目标仍由上方三seed验证。

请求 `328` 正常结束。本地与原生simulate完整返回时间均为 **138.043508379 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/pyramids/ordinary-pair-v1/game-seed1/comparison.json`。派生脚本 SHA256：`ea8326468d448931840bb8af4701fee842c9a475d3f4d1081133cd30d5491eda`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

首版彩块重建在数轮后缺Block，后改为按完整体积筹资。当前版保留尚存的沙体，只补实际缺块，并在所有清理和中心预留完成后重读高度，避免把并发塌方前的缓存当成最终预算。

Sand上层放置依赖下层八邻支撑，不能像彩块一样逐列一次堆到顶。中心顶块是完成屏障：全部工人退出后才放置，防止金字塔完成自动清场时其他工人仍在施工。早期通用单机保沙布局比彩块慢；后来单机改用固定5×5足印才取得结构收益，见对应文档。

当前多机首seed1522.782秒修87座塔、重生129次。按阶段日志相邻时间差统计：找塔失败重生102.456秒；成功塔定位、清土、统计与备料919.717秒；修补、同步、顶块与收获500.608秒。平均每完成一塔约17.50秒。全轮共有5031次spawn、188422次move及13352次place；并发调用累计费用不能直接相加当作墙钟时间。919.717秒包含多种工作，不能称为定位时间。后续优先减少完整格复扫、清理阶段和额外塌方，当前约1481秒不代表最优。

沿边直接修补候选`pyramids/edge-direct-candidate/lb_pyramids.py`先到西边、沿西边到南角，再沿南边量边长，用正方形几何推另一端。`edge-direct-model-seed1/report.json`在35秒现实预算停止，游戏时间1157.269772421秒，未完成150000 Power目标；已完成49塔的阶段均值为入口与基座2.896秒、边界2.940秒、清土3.091秒、逐层修补13.014秒。定位逻辑可行，但此实现仍逐层扫描完整格，净吞吐劣于当前缺块版，未进实机、未迁入。这里只关闭这一具体重复扫描实现，不否定沿边定尺寸、固定高度公式和就地补缺方向。路径共同根目录为`.codex/leaderboard-sol/underground-official/`。

请求425在启动前因another script is still executing失败，同时出现BlinkManager.OnGUI/CodeWindow.IsMinimized空引用异常；prepare426后，427又在启动约0.055秒时取消，均无完成轮。quit428保存退出、经Steam重启并prepare429后，相同源码在430完整通过。原因尚未定位，不把它算作模型失配或算法失败；两次失败的summary、完整日志及恢复证据原样保留。

## 静态检查与后续

当前执行源码与冻结模型、候选实机源码的AST一致，游戏语法检查通过。ty LSP无错误、10提示，分别为未使用局部变量及spawn失败分支被外部桩判为不可达；未修改外部游戏类型桩。

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

## 构建26462009正式统计：persistent-wait-current-26462009

<!-- official:persistent-wait-current-26462009:440 -->

请求440完整正常结束，共5轮。官方最终日志均值为 **24:40.702（1480.702游戏秒）**；逐轮日志重算均值为1480.701600000秒，保留两者的显示舍入口径。

同构建前版完整均值4738.376000000秒/2轮；当前正式均值1480.702秒/5轮，缩短约68.75%。边缘定位保留原塔沙块，清理后只修实际缺口；常驻工人按精确Block消耗阈值同步，每层完整支撑后才上升，主机最后放顶块。

部署源码SHA256：`1723c2c6021c71ab00ede11217f0daf374d2ea82da101e8f8a36b07458fcd8c6`。当前源码SHA256：`f58d46c0421434c1ea2dde5a42226416500d46e936d73493de4102a4b75d6aae`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/pyramids/persistent-wait-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
