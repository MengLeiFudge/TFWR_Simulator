# 功能脚本

本目录保存直接在游戏内运行、持续获取目标资源的脚本。运行与文件同名的入口，例如打开 `rice.py` 直接执行，或在同目录脚本中调用 `rice.rice()`。除 `farm_support.py` 共用模块外，每个文件都提供持续入口和按绝对库存目标停止的 `collect(goal)`。

## 命名

使用小写英文和下划线，保证文件名可直接用作游戏模块名。资源生产脚本直接按资源命名；需要区分机制时使用 `资源_机制.py`。

| 目标资源 | 脚本 | 生产方式与前置 |
| --- | --- | --- |
| 干草 | [hay.py](hay.py) | 自然草地；无种植科技也可收草 |
| 木材 | [wood.py](wood.py) | 早期灌木；解锁树后交错种植 |
| 胡萝卜 | [carrot.py](carrot.py) | 自动补干草、木材种子成本 |
| 南瓜 | [pumpkin.py](pumpkin.py) | 整田种植、补死株、成熟合并后收获 |
| 仙人掌 | [cactus.py](cactus.py) | 补南瓜种子，行列排序后连锁收获 |
| 骨头 | [bone_dinosaur.py](bone_dinosaur.py) | 补苹果所需资源，恐龙巡回后换帽结算 |
| 怪异物质 | [weird_substance.py](weird_substance.py) | 肥料科技；感染成熟草后收获 |
| 金币（迷宫） | [gold_maze.py](gold_maze.py) | 补怪异物质，DFS寻找每座新迷宫的宝藏 |
| 能量（向日葵） | [power_sunflower.py](power_sunflower.py) | 补胡萝卜种子，花瓣从高到低收获 |
| 水稻 | [rice.py](rice.py) | 稻米、挖掘、种植；逐柱两层粘土，按可用无人机分担 |
| 竹子 | [bamboo.py](bamboo.py) | 补稻米种子；空通道切花后整株收获 |
| 建材 | [block.py](block.py) | 挖掘；普通地层开采 |
| 煤 | [coal.py](coal.py) | 煤、挖掘；稻米解锁后优先开采首区块 |
| 铁 | [iron.py](iron.py) | 铁、挖掘；逐层开采，不依赖勘探消耗品 |
| 石英 | [quartz.py](quartz.py) | 石英、挖掘；普通地形开采，不套排行榜固定深度 |
| 蘑菇 | [mushroom.py](mushroom.py) | 蘑菇、挖掘、地下感知；按分区配对，层间回收子机 |
| 炸药 | [dynamite.py](dynamite.py) | 炸药、挖掘、地下感知；数字传播、子集推理、按列开安全格 |
| 金币（藏宝图） | [gold_treasure_map.py](gold_treasure_map.py) | 藏宝图、挖掘、地下感知；公开路线按层去环 |
| 能量（金字塔） | [power_pyramids.py](power_pyramids.py) | 金字塔、挖掘、地下感知；定位同一座塔、逐层补缺、中心补尖 |
| 南瓜（石化南瓜） | [pumpkin_petrified.py](pumpkin_petrified.py) | 石化南瓜、挖掘；直接开采地下南瓜 |
| 水 | [water.py](water.py) | 等待浇水科技的被动补给，保留农田 |
| 肥料 | [fertilizer.py](fertilizer.py) | 等待肥料科技的被动补给，保留农田 |

## 运行约定

- 用户运行入口后持续生产目标资源，不以排行榜目标库存为停止条件，不调用排行榜计时入口。
- 入口函数与文件同名，直接执行文件即可调用入口。依赖、必要资源及解锁前提在脚本说明中列明。
- 根据当前解锁、科技等级、可用地块和无人机数量选择可执行方式；低科技阶段采用可用方案，高科技阶段利用已解锁能力。不默认满科技、32×32 地图或 32 台无人机。
- 对种植材料、消耗品和其他必需资源处理补给。机制本身未解锁且无可行替代，或缺少无法自产的前置资源时，明确说明条件后停止，不空转，也不调用尚未解锁的 API。
- 脚本需要相应的语言与查询功能：函数、导入、变量、循环、列表/字典、感知、成本查询与自动解锁查询。科技适配指当前已具备脚本执行能力后的资源科技等级、地图及无人机配置；机制未解锁时停止。
- 竹子需要相邻通道格，恐龙需要至少两个相连格，炸药需要至少2×2正方形，金字塔需要至少5×5。一般开采在没有地下感知时只按公开地面避开基岩，有地下感知后按高度/硬度跳过已塌落地块。
- 地表种植、稻米、竹子、一般开采、蘑菇和炸药按可用无人机分工；其他机制使用主机。地形重生和补料会调用 `clear()`，请在可以重新整理农田时启动。水与肥料入口只等待补给。
- 本批新实现完成游戏语法静态编译、依赖检查和代码自审；各科技组合的模拟产量、净吞吐与实机行为尚未验证。能量会被普通动作消耗，收益取决于实际科技和产能，不能把毛产量当净增长。

## 本地模拟

```bash
python3 -m simulator.local_simulator scripts/functional/carrot.py --preset reset --unlock Plant=1 --unlock Carrots=1 --unlock Expand=1 --max-api-calls 20000 --timeout 10
python3 -m simulator.local_simulator scripts/functional/rice.py --preset all --unlock Mining=3 --unlock Megafarm=0 --timeout 10
python3 -m simulator.local_simulator scripts/functional/mushroom.py --save gamesave/save.json --timeout 10
```

持续入口按模拟器的API/检查点/墙钟预算停止，`status=stopped` 可能表示正常触及执行上限；应同时查看库存、输出和具体错误。需要有限目标时，在同目录入口中调用对应模块的 `collect(goal)`；场景的 `goal` 只记录达标状态，不会自动停止持续脚本。科技选项与覆盖顺序见[模拟器说明](../../simulator/local_simulator/README.md#科技与初始库存)。

## 依赖与来源

运行时保留本目录的模块名，尤其是 `farm_support.py`。胡萝卜、南瓜、仙人掌、骨头、竹子、迷宫和金字塔的补料可能继续导入其他功能模块，不能只复制单个入口而省去补给依赖。脚本不导入 `lb_*.py`。

稻米、竹子与煤参考本机已有功能脚本和对应排行榜/重置策略；蘑菇的分层配对、炸药的数字推理主体来自本机 `Mushroom.py` / `Dynamite.py`。藏宝图去环和金字塔几何补缺参考仓库已记录的排行榜实现，再适配普通地形与持续入口。排行榜本身的研究与实测证据仍归 [docs/leaderboards](../../docs/leaderboards/README.md)。

部署遵守仓库的真实存档边界。现有 `sync_leaderboard_scripts.py` 只处理排行榜脚本；本次只补齐仓库文件，未同步或新增真实存档文件。
