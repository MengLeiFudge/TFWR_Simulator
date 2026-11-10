# 功能脚本

本目录的初版以**科技全解、32×32农场、32台无人机**为运行前提，持续生产对应资源。Fastest Reset类脚本仍归排行榜目录，使用各自的重置初始条件。运行与文件同名的入口即可，例如打开 `rice.py` 执行。

有现成功能脚本时迁入原算法；没有时优先使用已验证的多机排行榜实现。之后按实际普通地形与持续入口做本地效率对照，采用确有收益的结构。效率与存档替换遵守[游戏脚本准入](../../docs/script-validation.md)；初版来源见[历史功能记录](../../docs/functional-validation.md)，地下批次见[效率记录](../../docs/underground-functional-validation.md)，铁与石英的勘探对照见[勘探记录](../../docs/underground-prospecting.md)。成就入口的筛选边界见[特殊成就目录](../achievement/README.md)。常规入口只保留生产或排行榜机制本身；能随正常流程触发的成就不在 `scripts/achievement/` 重复建文件。

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
| 竹子 | [bamboo.py](bamboo.py) | `lb_bamboo.py`按行分片、统一花节并批量切收 |
| 煤 | [coal.py](coal.py) | 用户原 `Coal.py`，分散探孔、发现煤后沿矿层扩展 |
| 蘑菇 | [mushroom.py](mushroom.py) | 用户原逐层同步与采样柱，加公开颜色缓存、低台搬运与同高配对 |
| 炸药 | [dynamite.py](dynamite.py) | `lb_dynamite.py`区域差集推理、并行找层和逐盘正常结算 |
| 藏宝图产金币 | [gold_treasure_map.py](gold_treasure_map.py) | `lb_treasure_map.py`，按层去环，适配普通地形入口 |
| 金字塔产能量 | [power_pyramids.py](power_pyramids.py) | `lb_pyramids.py`修补主体，普通田使用Jump和浅层爆破钻头 |
| 建材 | [block.py](block.py) | 单机连续深钻与原生炸药层连锁收集；[机制与验证记录](../../docs/block-mining.md) |
| 铁 | [iron.py](iron.py) | 已露矿及邻柱追脉，否则支付Coal读取铁方向，主机单钻定点开采 |
| 石英 | [quartz.py](quartz.py) | 单爆破钻、四格间距蛇形开孔，保留石英深度与矿层终止条件 |
| 石化南瓜 | [pumpkin_petrified.py](pumpkin_petrified.py) | 同上，Jump至石化层附近后收取真实爆破掉落 |
| 怪异物质 | [weird_substance.py](weird_substance.py) | `lb_fastest_reset.py`的并行伴生树苗圃 |

向日葵入口保留完整生产周期；传入有限 `target` 时，最后一波同步点会读取该目标并提前收口，`-1` 仍表示持续生产。

水和肥料由游戏自动获取，不设生产脚本。`mining.py`集中石英、石化南瓜的稀疏钻孔及矿采导航，不是独立生产入口；建材的连续深钻和60秒库存窗口由 `block.py` 保存。铁的方向勘探直接由 `iron.py` 保存；`resources.materials` 为其准备Coal查询储备。爆破只计真实入库，勘探结果不直接记作产量。

## 运行与依赖

- 独立功能入口以其他资源库存充足为前提；效率按目标资源的实际净增长/游戏秒比较，不另计生产Coal、Iron、Dynamite等材料的时间。游戏动作仍正常扣材料，耗尽或动作失败时返回原因；库存调度按材料表准备和补齐。
- 完整周期型在正常结算并回收子机后检查库存目标。建材按每次开挖检查，稀疏矿采按整片、蘑菇按整片、炸药按整盘检查，因此最终库存可能略超目标。竹子按行分片统一培育与批量切收，运行中不再占用共享Jump额度。
- 多数入口会整理或重生农田，运行前确认当前农田可被清理。Jump每次执行只能使用一次，后续循环按原算法继续或重生。
- 金字塔只同时修一座，底层就绪后再补高层，主机在中心放最后顶块。爆破钻头只用于远离塔区的浅覆盖层，接近塔区前换回采矿帽；结果须以实际模拟记录为准。
- `block.py`只依赖同目录的 `production.py`，单机独占爆破钻连续向下开采。每次挖掘消耗一份炸药；调度按 `DYNAMITE_RESERVE` 准备2000份，不再准备向日葵种子或土台。入口记录实际不超过60游戏秒的Block净增窗口。`quartz.py`、`pumpkin_petrified.py`需要 `mining.py`；铁入口依赖 `production.py`。验证范围见各入口说明，运行时不导入 `lb_*.py`。

MIT来源的木材、胡萝卜、南瓜和恐龙脚本保留作者声明及 [enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)。迷宫上游来源和本地使用边界见[迷宫策略文档](../../docs/leaderboards/lb_maze.md)。

## 本地效率对照

```bash
python3 -m simulator.local_simulator scripts/functional/bamboo.py --preset all --scenario scenario.json --timeout 30 --max-api-calls 5000000 --max-steps 50000000 --output result.json
```

`scenario.json`必须明确初始库存；比较双方使用相同科技、地图、库存和seed。连续产出先给有限现实预算，直接读取报告 `efficiency.items.资源名.net_change` 和 `net_per_game_second`，按实际游戏时间评价。现实预算到即停止，无须凑满600游戏秒；`--game-seconds 600`仅在需要固定展示窗口时使用，未跑满就保留实际时间，不填写成600秒产量。

恐龙等批量结算机制必须跑完至少一个完整周期，收益以实际入库为准；未结算时不把0当作周期效率。持续脚本可通过本地有限入口调用原有完整生产周期，保留算法与依赖哈希，不在真实存档新增入口。材料消耗、首次Jump、初始化及后续周期都要记录。

只有通过本地正确性和效率对照、且效率严格高于当前存档对应版本时，才允许覆盖该文件。同效迁入、批量尚未结算、错误或对照不足都保留当前存档。运行前核对同目录依赖；检查[游戏语言静态规则](../../simulator/local_simulator/syntax-validation.md)，语法不合格的模型产量不能作为替换依据。
