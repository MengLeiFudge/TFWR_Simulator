# 功能脚本

本目录的初版以**科技全解、32×32农场、32台无人机**为运行前提，持续生产对应资源。Fastest Reset类脚本仍归排行榜目录，使用各自的重置初始条件。运行与文件同名的入口即可，例如打开 `rice.py` 执行。

有现成功能脚本时迁入原算法；没有时优先使用已验证的多机排行榜实现。只适配持续入口和普通地形的必要差异，保留成熟布局、并行方式和热路径。效率与存档替换遵守[游戏脚本准入](../../docs/script-validation.md)，本批来源和本地结果见[功能脚本效率记录](../../docs/functional-validation.md)。

## 脚本清单

| 资源或机制 | 入口 | 算法来源 |
| --- | --- | --- |
| 干草 | [hay.py](hay.py) | `lb_hay.py`，32组双锚点伴生草 |
| 木材 | [wood.py](wood.py) | `lb_wood.py`，32机区域伴生树 |
| 胡萝卜 | [carrot.py](carrot.py) | `lb_carrots.py`，区域动态伴生请求 |
| 南瓜 | [pumpkin.py](pumpkin.py) | `lb_pumpkins.py`，16个双机区域及成熟队列 |
| 仙人掌 | [cactus.py](cactus.py) | `lb_cactus.py`，树形派发、铺田预交换和三格窗口排序 |
| 恐龙产骨头 | [bone_dinosaur.py](bone_dinosaur.py) | `lb_dinosaur.py`，贪心前缀、安全桥接和后段捷径 |
| 迷宫产金币 | [gold_maze.py](gold_maze.py) | `lb_maze.py`，32座独立小迷宫及增量路由 |
| 向日葵产能量 | [power_sunflower.py](power_sunflower.py) | `lb_sunflowers.py`，16组双机分瓣收获与同步 |
| 水稻 | [rice.py](rice.py) | 用户原 `Rice.py`，按列巡回采收、下挖、补种 |
| 竹子 | [bamboo.py](bamboo.py) | 用户原 `Bamboo.py`，通道多株状态与到期轮转 |
| 煤 | [coal.py](coal.py) | 用户原 `Coal.py`，分散探孔、发现煤后沿矿层扩展 |
| 蘑菇 | [mushroom.py](mushroom.py) | 用户原 `Mushroom.py`，Jump、浅层爆破与分区配对 |
| 炸药 | [dynamite.py](dynamite.py) | 用户原 `Dynamite.py`，Jump、协同找层及数字推理 |
| 藏宝图产金币 | [gold_treasure_map.py](gold_treasure_map.py) | `lb_treasure_map.py`，按层去环，适配普通地形入口 |
| 金字塔产能量 | [power_pyramids.py](power_pyramids.py) | `lb_pyramids.py`修补主体，普通田使用Jump和浅层爆破钻头 |
| 建材 | [block.py](block.py) | `lb_ores.py`的按列并行沟挖，浅层爆破收集 |
| 铁 | [iron.py](iron.py) | `lb_ores.py`的按列并行沟挖，Jump及全科技爆破 |
| 石英 | [quartz.py](quartz.py) | `lb_ores.py`的按列并行沟挖，Jump及全科技爆破 |
| 石化南瓜 | [pumpkin_petrified.py](pumpkin_petrified.py) | `lb_ores.py`的按列并行沟挖，Jump至石化层后爆破收集 |
| 怪异物质 | [weird_substance.py](weird_substance.py) | `lb_fastest_reset.py`的并行伴生树苗圃 |

水和肥料由游戏自动补给，不设生产脚本。`mining.py`集中矿石榜迁入的派工、沟挖和导航，不是独立生产入口。矿物的全科技爆破实现消耗炸药，未计入补做炸药的用时，材料净消耗见效率记录。

## 运行与依赖

- 资源生产持续运行，直到用户停止、原算法检测到材料不足或出现动作错误。种子、肥料、怪异物质、煤/铁勘探消耗品以及爆破所需炸药，须按所选机制准备；不要用无成本资源假设估算实际净收益。
- 多机榜的固定资源目标改为持续生产条件；完整周期型算法在正常结算并回收子机后继续下一轮。原功能脚本保留其Jump、布局、等待、钻头和进度日志。
- 多数入口会整理或重生农田，运行前确认当前农田可被清理。Jump每次执行只能使用一次，后续循环按原算法继续或重生。
- 金字塔只同时修一座，底层就绪后再补高层，主机在中心放最后顶块。爆破钻头只用于远离塔区的浅覆盖层，接近塔区前换回采矿帽；结果须以实际模拟记录为准。
- `block.py`、`iron.py`、`quartz.py`、`pumpkin_petrified.py`需要同目录的 `mining.py`。其余入口独立保存对应成熟算法，运行时不导入 `lb_*.py`。

MIT来源的木材、胡萝卜、南瓜和恐龙脚本保留作者声明及 [enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)。迷宫上游来源和本地使用边界见[迷宫策略文档](../../docs/leaderboards/lb_maze.md)。

## 本地效率对照

```bash
python3 -m simulator.local_simulator scripts/functional/bamboo.py --preset all --scenario scenario.json --timeout 30 --max-api-calls 5000000 --max-steps 50000000 --output result.json
```

`scenario.json`必须明确初始库存；比较双方使用相同科技、地图、库存和seed。连续产出先给有限现实预算，直接读取报告 `efficiency.items.资源名.net_change` 和 `net_per_game_second`，按实际游戏时间评价。现实预算到即停止，无须凑满600游戏秒；`--game-seconds 600`仅在需要固定展示窗口时使用，未跑满就保留实际时间，不填写成600秒产量。

恐龙等批量结算机制必须跑完至少一个完整周期，收益以实际入库为准；未结算时不把0当作周期效率。持续脚本可通过本地有限入口调用原有完整生产周期，保留算法与依赖哈希，不在真实存档新增入口。材料消耗、首次Jump、初始化及后续周期都要记录。

只有通过本地正确性和效率对照、且效率严格高于当前存档对应版本时，才允许覆盖该文件。同效迁入、批量尚未结算、错误或对照不足都保留当前存档。运行前确认4个矿物入口所需的 `mining.py`已在同目录；检查[游戏语言静态规则](../../simulator/local_simulator/syntax-validation.md)，语法不合格的模型产量不能作为替换依据。
