# 功能脚本

本目录的初版以**科技全解、32×32农场、32台无人机**为运行前提，持续生产对应资源。Fastest Reset类脚本仍归排行榜目录，使用各自的重置初始条件。运行与文件同名的入口即可，例如打开 `rice.py` 执行。

有现成功能脚本时迁入原算法；没有时优先使用已验证的多机排行榜实现。之后按实际普通地形与持续入口做本地效率对照，采用确有收益的结构。效率与存档替换遵守[游戏脚本准入](../../docs/script-validation.md)；初版来源见[历史功能记录](../../docs/functional-validation.md)，持续生产优化见[布局复用与完整周期对照](../../docs/functional-optimization.md)，地下批次见[效率记录](../../docs/underground-functional-validation.md)，铁与石英的勘探对照见[勘探记录](../../docs/underground-prospecting.md)。成就入口的筛选边界见[特殊成就目录](../achievement/README.md)。常规入口只保留生产或排行榜机制本身；能随正常流程触发的成就不在 `scripts/achievement/` 重复建文件。

## 按库存目标补齐

打开 [resources.py](resources.py)，修改文件开头的 `TARGETS`，然后运行同名入口。数值表示最终库存下限，例如：

```python
TARGETS = {
    Items.Hay: 1000000,
    Items.Wood: 1000000,
    Items.Carrot: 100000,
    Items.Bone: -1,
}
```

- `0` 不设库存目标；正整数表示补到至少该数量；`-1` 表示持续生产。示例会补足干草、木材和胡萝卜，并持续生产骨头。
- 先补齐全部有限目标，并巡检补回被其他生产过程消耗的目标库存；没有 `-1` 时，所有目标同时达标后退出。随后按配置顺序调用 `-1` 入口；它会持续生产，因此多个无限目标时，后面的资源不会定时获得农场。
- 调度优先补齐当前资源需要的材料，再调用现有功能脚本。未设置目标的资源也可能作为材料生产；金币、能量和南瓜分别使用迷宫、向日葵和普通南瓜入口。
- 调度把目标直接传给资源入口，例如 `dynamite.dynamite(20000000)`。入口按实际库存判断完成，已开始的南瓜、恐龙、向日葵等周期先正常结算。炸药在同一次调用中复用邻接表，连续处理地层；初始化耗时不会触发调度返回或清场。
- 各入口可以因材料不足或动作失败提前返回。返回后先回收全部子机；仅在本次有净增长且材料储备不足时补料重试。没有净增长或没有已知材料短缺时打印原因并停止，保留现场供检查。
- 水和肥料目标通过等待游戏自动补给完成。目标库存全部已足够时直接退出；需要生产时会使用并清理32×32农场。

每个资源入口使用 `入口(target=-1)`。直接运行文件或无参调用表示持续生产；传入非负数表示最终库存下限，库存已达标时直接返回。新增或迁移算法时，在可正常结算的位置检查 `production.active(物品, target)`，并将同一目标显式传到生产子机或其闭包中。全部子机结束后才允许切换资源。

[production.py](production.py) 只提供库存目标判断和整次执行的一次Jump额度。地下入口通过 `production.jump_once(科技)` 跳跃；目标属于各次调用参数。

## 当前产出速率

2026-11-11，当前 C# 模拟器、全科技、普通32×32田、seed=1、其他材料充足。速率为实际净增长÷实际游戏秒×60，包含初始化、移动、成熟和结算；只显示正增长物品，自动补给的水和肥料不计入。这里是短程本地观测，不是实机成绩或无限期稳态承诺。

| 脚本 | 主要产出 / 游戏分钟 | 其他净产出 / 游戏分钟 | 观测游戏秒 |
| --- | ---: | --- | ---: |
| [hay.py](hay.py) | 干草 10.21亿 | — | 60.00 |
| [wood.py](wood.py) | 木材 21.14亿 | 干草 1808.23万；胡萝卜 1064.55万 | 60.00 |
| [carrot.py](carrot.py) | 胡萝卜 5.06亿 | 干草 2853.94万；木材 1.03亿 | 60.00 |
| [pumpkin.py](pumpkin.py) | 南瓜 3129.29万 | 怪异物质 9.68万 | 60.00 |
| [cactus.py](cactus.py) | 仙人掌 3355.44万 | — | 60.00 |
| [bone_dinosaur.py](bone_dinosaur.py) | 骨头 259.14万 | — | 775.38 |
| [weird_substance.py](weird_substance.py) | 怪异物质 4.95亿 | 木材 4.95亿 | 60.00 |
| [gold_maze.py](gold_maze.py) | 金币 649.93万 | 干草 1.64万 | 60.00 |
| [rice.py](rice.py) | 水稻 104.79万 | 建材 9,456；煤 48 | 60.00 |
| [bamboo.py](bamboo.py) | 竹子 1.01亿 | — | 450.00 |
| [coal.py](coal.py) | 煤 1.53万 | 南瓜 382.31万；建材 147.66万；铁 21.30万；石英 13.99万 | 60.00 |
| [mushroom.py](mushroom.py) | 蘑菇 1.93万 | 建材 4,144；煤 60；铁 96 | 60.00 |
| [dynamite.py](dynamite.py) | 炸药 39.06万 | 南瓜 1.38万；建材 2,515；煤 2；铁 144；石英 120 | 60.00 |
| [block.py](block.py) | 建材 147.49万 | 南瓜 382.31万；煤 1.53万；铁 21.30万；石英 13.97万 | 60.00 |
| [iron.py](iron.py) | 铁 21.30万 | 南瓜 382.31万；建材 147.66万；煤 1.53万；石英 13.99万 | 60.00 |
| [quartz.py](quartz.py) | 石英 13.99万 | 南瓜 382.31万；建材 147.66万；煤 1.53万；铁 21.30万 | 60.00 |
| [gold_treasure_map.py](gold_treasure_map.py) | 金币 18.09万 | 南瓜 6.55万；建材 7,942；铁 1,648；石英 728 | 60.00 |
| [power_pyramids.py](power_pyramids.py) | 能量 2,888.1 | 南瓜 2.07万；建材 9,666.7；煤 400.5；铁 866.9；石英 245；炸药 5.7 | 127.35 |
| [power_sunflower.py](power_sunflower.py) | 能量 3.41万 | 干草 16.38万；怪异物质 148 | 60.00 |
| [pumpkin_petrified.py](pumpkin_petrified.py) | 南瓜 382.31万 | 建材 147.66万；煤 1.53万；铁 21.30万；石英 13.99万 | 60.00 |

竹子观察450游戏秒，覆盖500M批次后保留竹桩的阶段；首60秒仍受筛选成本影响，不能套用该长期平均值。金字塔以增加5000能量的完整周期取样，实际运行127.35游戏秒。恐龙按完整一轮入库3348.89万骨头折算，实际耗时10.76墙钟秒；其余入口观察60游戏秒。本轮优化每例限10墙钟秒，不为凑窗口延长预算。详细版本、数量及三seed对照见[持续生产优化](../../docs/functional-optimization.md)、[验证汇总](../../docs/script-rate-validation.md)和[数据](../../docs/script-rate-validation.json)。

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
| 水稻 | [rice.py](rice.py) | `lb_rice.py`两层粘土清单流水及补水，实际收割后下挖、全部回收后换田 |
| 竹子 | [bamboo.py](bamboo.py) | `lb_bamboo.py`按行分片、统一花节，后续批次复用合格竹桩 |
| 煤 | [coal.py](coal.py) | `mining.mine`，单爆破钻连续深挖，有限目标按煤库存停止 |
| 蘑菇 | [mushroom.py](mushroom.py) | 用户原逐层同步与采样柱，加公开颜色缓存、低台搬运与同高配对 |
| 炸药 | [dynamite.py](dynamite.py) | `lb_dynamite.py`区域差集推理、并行找层；固定邻接表并行建立，每盘正常结算 |
| 藏宝图产金币 | [gold_treasure_map.py](gold_treasure_map.py) | `lb_treasure_map.py`，按层去环，适配普通地形入口 |
| 金字塔产能量 | [power_pyramids.py](power_pyramids.py) | `lb_pyramids.py`并行探边、邻格采样和树形维修，普通田使用Jump与浅层爆破钻头 |
| 建材 | [block.py](block.py) | 单机连续深钻与原生炸药层连锁收集；[机制与验证记录](../../docs/block-mining.md) |
| 铁 | [iron.py](iron.py) | `mining.mine`，单爆破钻连续深挖，有限目标按铁库存停止 |
| 石英 | [quartz.py](quartz.py) | 同上，有限目标按石英库存停止 |
| 石化南瓜 | [pumpkin_petrified.py](pumpkin_petrified.py) | 同上，收取石化南瓜真实掉落，有限目标按南瓜库存停止 |
| 怪异物质 | [weird_substance.py](weird_substance.py) | `lb_fastest_reset.py`苗圃，持续入口保留未收获的合格树，定期回收后恢复真实状态 |

向日葵传入有限 `target` 时，每一整波9个瓣阶段同步结束后统一检查目标并收口；`-1` 持续生产，后续周期复用土壤与水位。补水每次使用4份水；最终库存可能超过目标。

水和肥料由游戏自动获取，不设生产脚本。`mining.py`集中煤、铁、石英、石化南瓜共用的连续深钻；建材的60秒库存窗口由 `block.py` 保存。`resources.materials` 为这些采矿入口准备炸药；煤不再沿浅矿层逐格搜索，铁不再额外支付煤勘探。爆破只计实际入库。

## 整体审查结论

常规入口沿用对应成熟功能或多机排行榜算法，按普通地形、库存目标和持续生产调整。煤、铁、石英、石化南瓜共用连续深钻；建材保留60秒净增窗口。怪异物质保留合格树，竹子跨批次复用竹桩，金字塔迁入并行探边与维修，向日葵按整波退出，炸药并行建立邻接表。

这些结构均有本地对照，具体窗口、收益范围与失败候选见[持续生产优化记录](../../docs/functional-optimization.md)。蘑菇连续向下找层、扩大探孔和减少重复读取的候选未取得稳定优势，当前保持原实现。

## 运行与依赖

- 独立功能入口以其他资源库存充足为前提；效率按目标资源的实际净增长/游戏秒比较，不另计生产Coal、Iron、Dynamite等材料的时间。游戏动作仍正常扣材料，耗尽或动作失败时返回原因；库存调度按材料表准备和补齐。
- 完整周期型在正常结算并回收子机后检查库存目标。建材每16次开挖采样库存，四个共用深钻入口每次开挖前检查；蘑菇按整片、炸药按整盘检查，因此最终库存可能略超目标。竹子按行分片统一培育与批量切收，运行中不再占用共享Jump额度。
- 多数入口会整理或重生农田，运行前确认当前农田可被清理。Jump每次执行只能使用一次，后续循环按原算法继续或重生。
- 金字塔只同时修一座，底层就绪后再补高层，主机在中心放最后顶块。爆破钻头只用于远离塔区的浅覆盖层，接近塔区前换回采矿帽；结果须以实际模拟记录为准。
- `block.py`依赖同目录 `production.py`；煤、铁、石英和石化南瓜还依赖 `mining.py`。爆破钻单机独占，每次消耗一份炸药；库存调度按对应 `DYNAMITE_RESERVE` 准备2000份。建材入口记录实际不超过60游戏秒的Block净增窗口。运行时不导入 `lb_*.py`。

MIT来源的木材、胡萝卜、南瓜和恐龙脚本保留作者声明及 [enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)。迷宫上游来源和本地使用边界见[迷宫策略文档](../../docs/leaderboards/lb_maze.md)。

## 本地效率对照

```bash
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/functional/bamboo.py --preset all --scenario scenario.json --seconds 30 --wall-seconds 10 --max-api-calls 5000000 --max-nodes 50000000 --json result.json
```

首次先按[C#入口说明](../../simulator/headless/README.md)构建；WSL使用Windows `dotnet.exe`。`scenario.json`必须明确初始库存；比较双方使用相同科技、地图、库存和seed。连续产出先给有限现实预算，读取 `net_inventory.资源名`，除以报告实际 `game_seconds` 得到每游戏秒净增长。预算到即停止，不为凑固定展示时长延长运行；未跑满 `--seconds` 时保留实际推进时间。

恐龙等批量结算机制必须跑完至少一个完整周期，收益以实际入库为准；未结算时不把0当作周期效率。持续脚本可通过本地有限入口调用原有完整生产周期，保留算法与依赖哈希，不在真实存档新增入口。材料消耗、首次Jump、初始化及后续周期都要记录。

只有通过本地正确性和效率对照、且效率严格高于当前存档对应版本时，才允许覆盖该文件。同效迁入、批量尚未结算、错误或对照不足都保留当前存档。运行前核对同目录依赖；检查[C#游戏语言规则](../../simulator/headless/syntax-validation.md)，语法不合格的模型产量不能作为替换依据。
