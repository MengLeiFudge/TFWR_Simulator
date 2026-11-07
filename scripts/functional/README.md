# 功能脚本

本目录的初版以**科技全解、32×32农场、32台无人机**为运行前提，持续生产对应资源。Fastest Reset类脚本仍归排行榜目录，使用各自的重置初始条件。运行与文件同名的入口即可，例如打开 `rice.py` 执行。

有现成功能脚本时迁入原算法；没有时优先使用已验证的多机排行榜实现。之后按实际普通地形与持续入口做本地效率对照，采用确有收益的结构。效率与存档替换遵守[游戏脚本准入](../../docs/script-validation.md)；初版来源见[历史功能记录](../../docs/functional-validation.md)，当前地下算法、三seed数据及材料见[本轮地下效率](../../docs/underground-functional-validation.md)。

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
- 全部有限目标同时达标后退出。有 `-1` 时持续轮转；每次按配置顺序检查，后续生产消耗掉的目标资源会再次补齐。
- 调度优先补齐当前资源需要的材料，再调用现有功能脚本。未设置目标的资源也可能作为材料生产；金币、能量和南瓜分别使用迷宫、向日葵和普通南瓜入口。
- 每批约60游戏秒后在生产边界返回。南瓜、恐龙、向日葵等已开始的完整周期先正常结算，因此可能超过60秒。切换前等待旧无人机全部结束；本批没有净增长时打印原因并停止。
- 水和肥料目标通过等待游戏自动补给完成。目标库存全部已足够时直接退出；需要生产时会使用并清理32×32农场。

各资源入口现在依赖同目录的 [production.py](production.py)。它统一保存本批目标、轮转时间和整次执行的一次Jump额度。单独运行资源入口时，默认继续持续生产。新增或迁移功能算法时，在可正常结算和回收子机的位置检查 `production.active(物品)`；地下入口通过 `production.jump_once(科技)` 跳跃。

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
| 竹子 | [bamboo.py](bamboo.py) | `lb_bamboo.py`星形四邻布局；首次Jump保留天然珍珠岩，补水后恢复高飞 |
| 煤 | [coal.py](coal.py) | 用户原 `Coal.py`，分散探孔、发现煤后沿矿层扩展 |
| 蘑菇 | [mushroom.py](mushroom.py) | 用户原逐层同步与采样柱，加公开颜色缓存、低台搬运与同高配对 |
| 炸药 | [dynamite.py](dynamite.py) | `lb_dynamite.py`区域增量求解；普通田单次Jump、协同找层和逐盘正常结算 |
| 藏宝图产金币 | [gold_treasure_map.py](gold_treasure_map.py) | `lb_treasure_map.py`，按层去环，适配普通地形入口 |
| 金字塔产能量 | [power_pyramids.py](power_pyramids.py) | `lb_pyramids.py`修补主体，普通田使用Jump和浅层爆破钻头 |
| 建材 | [block.py](block.py) | 单爆破钻、四格间距蛇形浅层开孔 |
| 铁 | [iron.py](iron.py) | 同一稀疏开孔结构，Jump后按铁目标深度爆破收取 |
| 石英 | [quartz.py](quartz.py) | 同上，保留石英深度与矿层终止条件 |
| 石化南瓜 | [pumpkin_petrified.py](pumpkin_petrified.py) | 同上，Jump至石化层附近后收取真实爆破掉落 |
| 怪异物质 | [weird_substance.py](weird_substance.py) | `lb_fastest_reset.py`的并行伴生树苗圃 |

水和肥料由游戏自动补给，不设生产脚本。`mining.py`集中四项矿采的固定稀疏孔、钻头和导航，不是独立生产入口。仅一台钻头实际爆破，子机默认帽；爆破消耗Dynamite，只计真实入库。单入口效率预备了材料，未计入重新生产炸药、能量或种子的时间，净消耗见效率记录。

## 运行与依赖

- 资源生产持续运行，直到用户停止、原算法检测到材料不足或出现动作错误。种子、肥料、怪异物质、煤/铁勘探消耗品以及爆破所需炸药，须按所选机制准备；不要用无成本资源假设估算实际净收益。
- 多机榜固定目标改为持续生产条件；完整周期型在正常结算并回收子机后继续。矿采按整片、蘑菇按整片、炸药按整盘返回，调度可能晚于60游戏秒。竹子已有Jump额度时采用地表星形，未用时先保留可达珍珠岩；不会为保土假设全图增产。
- 多数入口会整理或重生农田，运行前确认当前农田可被清理。Jump每次执行只能使用一次，后续循环按原算法继续或重生。
- 金字塔只同时修一座，底层就绪后再补高层，主机在中心放最后顶块。爆破钻头只用于远离塔区的浅覆盖层，接近塔区前换回采矿帽；结果须以实际模拟记录为准。
- `block.py`、`iron.py`、`quartz.py`、`pumpkin_petrified.py`还需要同目录的 `mining.py`。各入口保存对应成熟算法，运行时不导入 `lb_*.py`。

MIT来源的木材、胡萝卜、南瓜和恐龙脚本保留作者声明及 [enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)。迷宫上游来源和本地使用边界见[迷宫策略文档](../../docs/leaderboards/lb_maze.md)。

## 本地效率对照

```bash
python3 -m simulator.local_simulator scripts/functional/bamboo.py --preset all --scenario scenario.json --timeout 30 --max-api-calls 5000000 --max-steps 50000000 --output result.json
```

`scenario.json`必须明确初始库存；比较双方使用相同科技、地图、库存和seed。连续产出先给有限现实预算，直接读取报告 `efficiency.items.资源名.net_change` 和 `net_per_game_second`，按实际游戏时间评价。现实预算到即停止，无须凑满600游戏秒；`--game-seconds 600`仅在需要固定展示窗口时使用，未跑满就保留实际时间，不填写成600秒产量。

恐龙等批量结算机制必须跑完至少一个完整周期，收益以实际入库为准；未结算时不把0当作周期效率。持续脚本可通过本地有限入口调用原有完整生产周期，保留算法与依赖哈希，不在真实存档新增入口。材料消耗、首次Jump、初始化及后续周期都要记录。

只有通过本地正确性和效率对照、且效率严格高于当前存档对应版本时，才允许覆盖该文件。同效迁入、批量尚未结算、错误或对照不足都保留当前存档。运行前确认4个矿物入口所需的 `mining.py`已在同目录；检查[游戏语言静态规则](../../simulator/local_simulator/syntax-validation.md)，语法不合格的模型产量不能作为替换依据。
