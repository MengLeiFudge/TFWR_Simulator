# 地下模拟与同种子实机对照

地下资源快照来自构建 **26410308**，支持全部 **14个地下排行榜场景**。本地仅依赖Python标准库。当前构建26462009的塌方修正、方法复核和长程对照见下节；旧版23个用例单列为历史证据。资源快照版本、方法覆盖、普通场景时间精度和专用排行榜盘面分别记录。

## 2026-11-06：构建26462009塌方传播同步

Quartz定位版Reset源码在普通初始科技、零库存和seed1下，修正前本地为19713.690940317秒，实机请求395为19716.483046656秒，误差为 **-2.792106339秒**。首次阶段差异出现在解锁Bamboo1后的Rice400采集，库存同为288，时间先差约1.204秒；后续等待使误差有正负变化，不能按固定倍率校正。

免费日志探针保留原脚本前118条阶段输出的完整本地时间，进一步定位到坐标(2,2)种植前。请求397的地面序列有748条，本地749条；唯一状态序列差异是本地在该格多一次Dirt挖掘，实机已露出Clay。当前Core.dll反编译的`GridManager.ClearGroundWithCaveins`按半径2方环相对挖掘点的偏移执行`dx != dy`筛选，模型却按世界坐标执行`x != y`。已只修正`Underground.clear_with_caveins`的这一条件，并保留原方环顺序、四邻/对角和传播阈值。没有修改Rice生长参数或为整轮时间加补偿。

| 当前构建对照 | 原始实机请求 | 核对输出行数 | 完整时间（游戏秒） | 修正后完整误差 |
| --- | ---: | ---: | ---: | ---: |
| 首次地层差异定位，普通Reset前段，seed1 | 397 | 748 / 748 | 4293.274462345 | 0ns |
| Quartz定位版Reset原源码，从零库存至解锁目标，seed1 | 395 | 585 / 585 | 19716.483046656 | 0ns |
| 4×4连挖72层、矿石掉落及公开铁矿/石英勘探，seed1 | 398 | 82 / 82 | 334.205213850 | 0ns |
| 铁矿勘探版，从普通Reset初始状态至解锁目标，seed1 | 399 | 713 / 713 | 17540.865550588 | 0ns |
| 扫雷覆盖层按需清理版，从普通Reset初始状态至解锁目标，seed1 | 402 | 713 / 713 | 16649.129798428 | 0ns |
| Mining5/Iron2后晚升Coal3版，从零库存至解锁目标，seed1 | 409 | 714 / 714 | 15752.701420357 | 0ns |
| Mining5/Iron2后先升Rice5再升Coal3，从零库存至解锁目标，seed1 | 412 | 722 / 722 | 15810.350362724 | 0ns |

前两项在修改后重放本地固定输入，对照保留的原始当前构建实机归档；后五项在修正后重新运行实机。原源码、场景、修前报告和原始请求均未覆盖。七项离散状态、整数值一致，小数只按quick_print的0.01显示精度比较；完整返回时间来自simulate返回值的整数纳秒，单独精确核对。六个长程窗口均超过900游戏秒，满足误差小于1秒的门槛。`underground.py`的ty LSP无诊断。

证据根目录：`.codex/leaderboard-sol/underground-official/alignment-26462009/`。`current-reset`与`rice-ground-only`下的`model-after-cavein.json`及`game-seed1/comparison-after-cavein.json`保留修后重放；`ore-methods`、`iron-prospect`、`lazy-cover`、`late-coal3`、`late-rice5`下的`game-seed1/comparison.json`保留新鲜方法与组合复核。Core.dll SHA256为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。各请求检查BepInEx和Unity双日志，未见新增错误，同ID回idle后恢复已有test.py/simulate.py，其他存档Python文件哈希未变。

本次只确认上述源码、参数、seed和组合。资源快照及原有模型元数据仍保留真实来源版本；未将全部API、任意并发或正式榜单专用盘面标为当前构建精度通过。修正前的策略预测保留为历史，后续候选使用修正后报告；没有为验收模型逐榜运行14个完整策略。

## 2026-11-07：普通扫雷失败边界（构建26462009）

炸药单机候选在普通8×8、满级科技、seed1下保留100000 Dynamite目标。原256次搜层边界在32.053517640秒停止，未投递实机。仅把搜层和开格覆盖层上限放宽到2048后，模型在1316.479833090秒以`dynamite_cycle 27 error 0 368`返回，实际库存50144，仍未达目标。两份失败报告保留，未改变正式专用榜的256次边界或100000目标。

实机请求405复现后者：37条输出的文本、整数和状态一致，完整时间1316.479833090秒，误差0ns。双日志无新增错误，同ID回idle后恢复已有test.py/simulate.py，其余Python文件哈希未变。证据为`.codex/leaderboard-sol/underground-official/alignment-26462009/dynamite-single-lazy-cover-ordinary-failure/game-seed1/comparison.json`及原始日志、派生源码与参数清单。

该项只确认模型如实复现所列失败边界。`goal_reached=false`，`long_window_passed=false`；不计为完整目标组合通过，不外推到专用盘面。普通地层中返回error的精确分支尚未定位，正式榜的原目标验证另记策略文档。

## 2026-11-07：方向边界短方法对照

请求408在普通8×8、满级科技、seed1下核对地面/坐标查询、硬度/稳定性越界及成功/失败推送。先在(0,0)放置Block_Red，从(7,0)查询East得到该红块及z=1，而硬度和稳定性查询均为None。人工彩块不可推，can_push/push均返回False。移除彩块后找到实际Mushroom层-65，将西侧环绕邻柱(7,0)准备到-66，再从(0,0)向West成功push；实际两柱高度变为-66/-65。

本地与实机5条输出的文本、整数、状态一致，完整时间均为7.248601350游戏秒，误差0ns。双日志无新增错误，同ID回idle后恢复已有test.py/simulate.py，其他Python文件哈希未变。证据为`.codex/leaderboard-sol/underground-official/alignment-26462009/wrap-methods-v3/game-seed1/comparison.json`。该项只通过所列方法与边界，窗口小于900秒，`long_window_passed=false`。

## 2026-11-07：Rice升级费用短方法对照

请求413使用当前Reset在Mining5/Iron2后的正常前置科技，初始Rice3、Block3000。默认get_cost先返回Rice4所需1000 Block，解锁后Rice4/Block2000；再次返回Rice5所需2000 Block，解锁后Rice5/Block0。返回值、等级和扣减库存均逐项核对，本地与实机4条输出一致，完整时间均为0.139588856游戏秒，误差0ns。

证据为`.codex/leaderboard-sol/underground-official/alignment-26462009/rice-upgrade-costs/game-seed1/comparison.json`，探针为`.codex/tests/rice_upgrade_costs_probe.py`。双日志无新增错误，同ID回idle后恢复已有test.py/simulate.py，其他Python文件未变。该项只覆盖默认get_cost和这两个升级的资源扣减，`long_window_passed=false`。

## 实现范围

| 模块 | 主要职责 |
| --- | --- |
| `world.py` / `execution.py` | 地下 API、库存和科技、悬浮、并发无人机、挖掘调速、子机清图、跳跃与结束计时 |
| `underground.py` / `underground_types.py` | 16 层区块、柱深度、普通地层、煤层、粘土、硬块、塌方、推块、放置和矿脉搜索 |
| `underground_features.py` | 铁矿、石英、特殊土壤、石化南瓜、蘑菇、金字塔、扫雷与藏宝图的地形生成 |
| `underground_crops.py` | 竹子分段生长、花节、悬浮阻挡、入格切割；稻米梯田变化由通用作物流程处理 |
| `underground_explosives.py` | 炸药实体和物品、爆破钻、Single 精度爆炸传播、扫雷首挖布雷及成功/失败结算 |
| `underground_puzzles.py` | 金字塔几何与材料检查、清除和巨型向日葵奖励 |
| `underground_treasure.py` | 藏宝图路线生成、所属无人机、路径完整性、分层揭露和宝藏奖励 |
| `special.py` | 恐龙的同高连通区、禁止跨高度移动、地形变化后的苹果清理 |
| `scenarios.py` / `underground_resources.json` | 地下排行榜库存、科技、目标、地形白名单、虚拟深度、单机与操作限制；原版资产参数 |
| `noise.py` / `randomness.py` | 原版 OpenSimplex、Single 舍入、十条随机流及区块子流 |

新增公开操作为 `hover`、`get_hover`、`get_pos_z`、`get_hardness`、`get_stability`、`dig`、`push`、`can_push`、`place`、`prospect_iron`、`prospect_quartz`、`jump`。既有 `plant/harvest/measure/use_item/change_hat/unlock` 等接口同时支持地下机制。

`dig()`只接受零参数。硬度、稳定性方向查询不环绕，越界返回`None`；`get_ground_type(direction)`、`get_pos_z(direction)`、`can_push(direction)`与`push(direction)`的方向会环绕。`get_pos_z`返回向下为负的地面坐标，不含悬浮高度。挖掘按硬度、执行速度和Mining等级计时，动作本身不耗Power。塌方清除不发放物品，爆破钻按实际清除方块收集。普通地形依照科技形成循环，特征各用独立子流，不以普通土替代未识别地形。

## 地下排行榜入口

在仓库根目录执行，`strategy.py` 替换为要筛选的游戏脚本：

```bash
python3 -m mechanism_model.local_simulator strategy.py --leaderboard mushrooms_single --seed 1 --timeout 30 --output result.json
```

也可以使用 `--scenario` 中的 `{"leaderboard":"Mushrooms_Single"}`。名称接受 `Mushrooms_Single`、`mushrooms_single`、`lb_mushrooms_single` 或 `Leaderboards.Mushrooms_Single`。可同时用场景 `items/unlocks/goal` 覆盖默认值；覆盖后属于自定义筛选场景，报告保留输入。`--leaderboard` 不能与场景中的同名字段重复设置。

| 名称 | 达标条件 | 初始物品 |
| --- | --- | --- |
| `bamboo` / `bamboo_single` | Bamboo 500,000,000 / 25,000,000 | Power、Rice 各 1,000,000,000 |
| `dynamite` / `dynamite_single` | Dynamite 10,000,000 / 100,000 | Power 1,000,000,000 |
| `mushrooms` / `mushrooms_single` | Mushroom 240,000 / 30,000 | Power 1,000,000,000 |
| `ores` / `ores_single` | Quartz 20,000 / 4,000 | Power 1,000,000,000 |
| `pyramids` / `pyramids_single` | Power 150,000 / 30,000 | 无 |
| `rice` / `rice_single` | Rice 2,000,000 / 100,000 | Power 1,000,000,000 |
| `treasure_map`（仅单机） | Gold 115,000 | Power 1,000,000,000 |
| `fastest_underground_reset` | 解锁 `Underground_Leaderboard` | 无 |

资源榜默认全科技；单机榜初始 8×8、最多一台无人机并禁止升级 Expand/Megafarm。Reset 从原版初始科技和 1×1 农田开始。竹子榜禁止挖掘；地下资源榜除稻米外禁止种植；所有榜禁止 `jump`。地图按各榜的特征白名单、虚拟区块及深度生成，正式资源场景的扫雷密度取原版固定值。

与原版一致，**脚本自行判断何时结束，运行器在结束后检查目标，不在库存达标瞬间截断脚本**。报告的 `goal_reached` 支持物品目标或科技目标；`leaderboard_profile` 保存资产配置。14 个场景的初始化、有界挖掘及未达标报告已在本地通过；Reset 解锁目标和竹子库存目标分别通过已有实机配对脚本的本地场景复验，完整时间为 8.701250000 秒和 1.099759410 秒。这两项覆盖过渡与目标判断，不是从零打榜成绩。

## 构建26410308历史同seed实机对照

以下是构建26410308与当时模型的历史结果。每个机制实现后，将同一份`probe.py`、显式科技和库存、相同seed交给本地运行器和游戏simulate，最后用当时实现重放23个本地用例对照实机归档。共2994条输出：2972条逐字一致，22条仅有已知数值显示舍入差异；当时没有状态、整数tick或完整返回时间差异。当前代码的验证范围以上节为准，不能把本表视为全部旧用例在后续修正后已重新通过。

| 用例 | seed | 实机请求 | 输出数 | 完整返回时间（秒） |
| --- | ---: | ---: | ---: | ---: |
| 悬浮与动作重置 | 1 | 283 | 39 | 仅保留 0.01 秒显示 |
| 4×4 连挖 28 层、巡视与清场 | 1 | 285 | 126 | 仅保留 0.01 秒显示 |
| 同一挖掘脚本 | 2 | 286 | 126 | 仅保留 0.01 秒显示 |
| 双机同格挖掘与全田巡视 | 1 | 287 | 83 | 仅保留 0.01 秒显示 |
| 同一双机脚本 | 2 | 288 | 83 | 4.550478840 |
| 煤层及掉落 | 1 | 291 | 577 | 73.924211070 |
| 粘土、稻米、梯田变化 | 1 | 292 | 450 | 127.833492240 |
| 竹子花节、生长、切割与子机阻挡 | 1 | 293 | 21 | 47.831715360 |
| 铁矿、石英、特殊土壤、石化南瓜及勘探 | 1 | 294 | 82 | 334.205213850 |
| 蘑菇颜色与 173 次推动 | 2 | 296 | 544 | 301.440745620 |
| 放置、沙支撑及彩块重建金字塔 | 3 | 297 | 166 | 15.403051530 |
| 炸药实体、物品和爆破钻 | 1 | 298 | 15 | 3.018782790 |
| 扫雷布雷、测量与失败结算 | 1 | 299 | 174 | 304.244383140 |
| 扫雷完整解盘和奖励 | 1 | 300 | 18 | 5.159865060 |
| 藏宝图路线、逐层前进和兑奖 | 1 | 301 | 276 | 16.892772030 |
| 跳跃至稻米地层 | 1 | 302 | 10 | 12.728632860 |
| 地下科技、成本、条件与解锁目标 | 1 | 303 | 46 | 8.701250000 |
| 多机挖掘期间调速 | 1 | 304 | 6 | 0.733616610 |
| 全地下科技、8×8 连续 112 层 | 2 | 307 | 114 | 1095.828029370 |
| 子机清图、编号归零与帽子保留 | 1 | 310 | 4 | 0.792103320 |
| 竹子库存目标后继续执行并返回 | 1 | 311 | 3 | 1.099759410 |
| 恐龙同高连通区与远端挖掘移除苹果 | 1 | 314 | 14 | 1.048071870 |
| 壤土/珍珠岩上的七类作物种植 | 1 | 313 | 17 | 256.345671510 |

19 个用例的 `simulate()` 完整返回时间与本地一致到整数纳秒。前四个用例仅保留完整返回时间的 0.01 秒显示，另有末尾时间采样，不能声称其完整返回时间精确到纳秒。表中时间来自驱动 `paired_ns`，不把脚本内 `get_time()*1e9` 的采样时刻当作脚本结束时刻；乘法及后续指令仍可能消耗 tick。

舍入只允许在已知数值字段：Power、勘探距离和秒数按游戏显示的两位小数比较，纳秒采样容差为 0.5 ns；离散状态及完整返回时间另行严格检查。组合场景逐层记录深度、地面类型、测量结果和 tick，另核对末尾库存；本次超过 900 游戏秒的窗口零时间偏差只适用于这个脚本和 seed。

## 证据与纠偏

原始资料保存在本机 `.codex/dlc-sim/`：每个用例含 `probe.py`、`scenario.json`、`seedN/local.json`、`fresh-local.json`、`outputs.json`、完整请求与双日志、`comparison.json`、`restoration.json`。总表为 `comparison.json`；工具为 `run_pair.py` 和 `compare.py --fresh`。排行榜本地检查位于 `leaderboards/reports.json`、`goal-reports.json`，CLI 检查为 `cli-mushrooms.json`。

失败与修正证据保留：

- 请求 282 的驱动漏开 Bamboo；请求 284 确认 `dig` 不接受方向参数。修正后重新配对。
- 请求 289 被手动程序占用，`prepare` 290 后继续；未覆盖运行中的存档脚本。
- 蘑菇首次 seed1 场景的地层循环不包含蘑菇，未算通过；seed2 增加 Iron1 后实际观察到蘑菇并完成推动。
- 金字塔首次本地运行调用了不存在的 timer 取消接口；改为既有 `timer.stopped` 后请求 297 通过。
- 组合场景初次状态、tick 一致但 Hay 少 120、Block 多 120。请求 306 诊断确认已清除/损坏的藏宝路径在原版克隆时未复制掉落物品 ID，实际掉落 Hay。按实际行为实现后，请求 307 全部一致。
- 请求 308 证实 `get_drone_id` 不是公开游戏函数，删除该探针调用。请求 309 暴露子机 `clear` 的重复清图：原版按旧编号清除副作用失败，编号归零后再次执行。修正调度后请求 310 一致。
- 恐龙初始探针的子机直接挖到苹果，不足以单独证明远端地形变化行为；请求 314 改为挖另一列，观察到移动前的 Apple 在移动后被清除。

所有成功配对均检查 BepInEx 与 Unity 新增日志，无新增错误。真实 Save0 仅临时覆盖既有 `test.py`、`simulate.py`，在同一请求回到 idle 后逐字节恢复；没有新增或删除存档文件，游戏保持运行。

## 使用边界

- 正式地下排行榜采用专用生成参数及 `BufferedCryptoRandom`；`simulate(seed)` 只能生成普通地下世界。专用场景已按资源和完整源码路径实现、通过有界本地运行，但没有原生同 seed 重放证据，报告明确标注 `leaderboard_validation=asset_and_source_only`。本地 seed 可比较候选，不能冒充正式榜同盘回放。
- 当前启用的地下特征均有实现。资产中禁用的 `BlockFeature`、`FullSizeFeature` 不作为启用内容；若未来启用未知特征会明确报错。动画、音效、装饰网格和成就不参与库存与 tick 模拟。
- 地下Reset已在当前构建以普通初始科技、零库存、seed1完成从零至解锁目标的完整源码对照，范围见上节。其他地下榜专用随机盘面没有逐榜同seed完整时间验收；正式统计与模型精度证据仍分开。
- 任意 seed、任意并发竞争、全部非法参数、所有跳跃目标及所有机制组合没有穷举。完整游戏语言和显示格式的既有限制仍见主 README；方法与本次长窗口通过不等于无条件完全一致。
