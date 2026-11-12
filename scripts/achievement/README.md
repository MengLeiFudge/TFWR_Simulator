# 成就脚本

本目录只保存需要专门制造状态的成就入口，最多运行300游戏秒，完成即返回；超时说明原因。常规资源累计与排行榜提交复用既有脚本，不另造重复入口。

## 成就与运行时间

官方名称来自[Steam简体中文成就页](https://steamcommunity.com/achievements/2060160?l=schinese)，[原始schema](../../references/achievements/steam-schinese.json)保留API ID、来源及抓取时间。下表为已有C#模拟、全科技、物料充足、seed0／1／2实际范围，炸药依赖已按12日版本复验；随机机制不保证任意seed成功，300秒是上限。本地条件成立不等于Steam账号已解锁。

| Steam 成就中文名 | 脚本 | 预计游戏时间 | 完成条件 / 注意事项 |
| --- | --- | ---: | --- |
| 杂技高手、杂技大师 | [acrobatics.py](acrobatics.py) | 约32.3秒 | 32机完成1000次翻转，兼得首次翻转。 |
| 手感不错 | [pet_piggy.py](pet_piggy.py) | 约1.0秒 | 执行抚摸小猪。 |
| 错误 | [cause_runtime_error.py](cause_runtime_error.py) | <1秒 | 预期除零错误。 |
| 无限循环 | [infinite_loop.py](infinite_loop.py) | 约1.0秒 | 进入字面量while True后主动退出，无需手动停机。 |
| 时装秀 | [fashion_show.py](fashion_show.py) | 约2.2秒 | 5台无人机同时戴不同普通帽子。 |
| 巨型南瓜 | [giant_pumpkin.py](giant_pumpkin.py) | 13.0–14.5秒 | 整田32×32合并后只收获一次。 |
| 你搞错了 | [wrong_order.py](wrong_order.py) | 4.8–5.7秒 | 成熟3×3仙人掌按行列降序。 |
| 泥泞农场 | [mud_farm.py](mud_farm.py) | 约4.3秒 | 32机同时补水；需要4096份水。 |
| 妙手回春 | [healer.py](healer.py) | <1秒 | 肥料感染胡萝卜，再用怪异物质治愈。 |
| 循环导入 | [circular_import.py](circular_import.py) | <1秒 | 依赖同目录 circular_import_a.py、circular_import_b.py。 |
| 高阶编程 | [higher_order_programming.py](higher_order_programming.py) | <1秒 | 把函数作为参数传递。 |
| 栈溢出 | [stack_overflow.py](stack_overflow.py) | <1秒 | 预期递归溢出。 |
| 梯田 | [rice_terrace.py](rice_terrace.py) | 约2.1秒 | 3×3田只种不收，整田同时覆盖水稻。 |
| 放置、建造者、大建造者、毕加索 | [block_builder.py](block_builder.py) | 约47.0秒 | 16机累计放置10000块彩色块，逐块挖回。 |
| 摩天大楼 | [reach_height.py](reach_height.py) | 约5.7秒 | 9机垫高3×3田到+150；需要1350份建材。 |
| 探矿者 | [prospector.py](prospector.py) | 约1.8秒 | 实际支付铁勘探1000次。 |
| 彩色金字塔 | [power_pyramids_color.py](power_pyramids_color.py) | 6.0–7.3秒 | 拆净最小原生5×5塔，再用35块彩色块重建。 |
| 蘑菇挤不下 | [push_mushroom_blocked.py](push_mushroom_blocked.py) | 6.0–13.3秒 | 刻意制造一次受阻推蘑菇。 |
| 牵线搭桥 | [mushroom_matchmaker.py](mushroom_matchmaker.py) | 150.5–236.9秒 | 实际配对比例严格超过95%，回收子机。 |
| 远距离友谊 | [mushroom_cross_stratum.py](mushroom_cross_stratum.py) | 22.5–228.9秒 | 原生不同地层的同色蘑菇相遇。 |
| 炸药排除、炸药排除专家 | [dynamite_expert.py](dynamite_expert.py) | 63.4–239.7秒 | 32×32、深度≤-600，完整解盘；无确定安全格则换田。 |
| 不安全的代码 | [mining_helmet_unsafe.py](mining_helmet_unsafe.py) | <1秒 | 戴非采矿帽挖掘。 |
| 坏掉的锄头 | [till_rock.py](till_rock.py) | 1.0–1.2秒 | 对岩石使用耕作。 |
| 宝藏猎人 | [treasure_hunter.py](treasure_hunter.py) | 20.9–70.2秒 | 覆盖32×32农场的迷宫，找到并收获宝藏。 |

原生金字塔最小底边5、有效体积35。彩色塔使用6格田中的5格原生塔；小于等于5格的田不会生成塔，不能用人造3格塔替代。

## 可以复用的成就

111项中，29项由24个专用入口处理，76项复用功能流程，2项复用排行榜，4项手动完成。逐项分类见[完整映射](#完整成就映射)。

| 成就或类型 | 复用入口 | 时间与边界 |
| --- | --- | --- |
| 采矿大师 | [block.py](../functional/block.py) | 本轮seed=1约49.4秒窗口内实际净增104.46万建材，60秒共147.49万。继续作为常规生产入口。 |
| 各资源专业户、大亨、矿工、大矿工与大师 | [常规产出表](../functional/README.md#当前产出速率)中的对应资源入口 | 按实际收获累计；时间受已有进度、初始化和批量结算影响，不能一律标成5分钟。 |
| 恐龙、长龙、长度很重要、恐龙大师 | [bone_dinosaur.py](../functional/bone_dinosaur.py) | 当前seed1完整周期684.09游戏秒，结算3348.89万骨头；属于常规生产，不受专用入口的5分钟限制。 |
| 迷宫、循环利用 | [gold_maze.py](../functional/gold_maze.py) | 常规入口重用小迷宫；“宝藏猎人”的整田大迷宫使用上表专用入口。 |
| 金字塔、埃及学家、大金字塔 | [power_pyramids.py](../functional/power_pyramids.py) | 按实际塔边界修补；大金字塔需随机遇到29×29塔，不能承诺5分钟。彩色塔另用专用入口。 |
| 藏宝图、大宝藏、藏宝图大师 | [gold_treasure_map.py](../functional/gold_treasure_map.py) | 常规路线去环后挖掘，累计200张需持续生产。 |
| 深层采矿、坚持不懈的矿工、不知疲倦的矿工、爆破大师 | [block.py](../functional/block.py) | 连续深入地下；绝对深度与累计深度分别判定，不能用建材数量替代。 |
| 巨型农场、蜂群、各首次种植、时尚达人、Hello World | 对应多机、种植或换帽的常规入口 | 已包含正常触发动作，不另建重复入口。 |
| 农业竞争、全自动化 | [排行榜目录](../leaderboard/README.md) | 必须真实提交对应排行榜；本地模拟不触发公开排名。 |
| 蒸蒸日上、大型农场、然后呢？ | 科技树 | 分别对应扩张、最大农场和全部解锁。 |
| 混沌编程 | 游戏工作区 | 手动打开20个代码窗口。 |

## 运行与验证

- 全科技含DLC、材料充足，独立启动只留主机。多数入口清田或改尺寸；最小可指定田边3，结束时游戏可能恢复尺寸，应核完成前状态。
- `dynamite_expert.py`依赖常规[dynamite.py](../functional/dynamite.py)及[production.py](../functional/production.py)，实际运行按同目录解析；入口与依赖一起冻结、语法检查和模拟，不能只复制入口。
- 截止时间贯穿派机、挖掘、解盘和回收。已有72次本地对照中22入口正常结束，2入口按预期报除零／栈溢出，均小于300游戏秒且结束仅主机。预期错误不作生产效率证明。
- 无限循环用字面量`while True`触发后主动break；特殊条件及已有证据归[速率与成就条件](../../docs/script-rate-validation.md#成就条件)，建材实际窗口及request491实机证据归[建材说明](../../docs/block-mining.md#采矿大师的窗口)。
- 新源码或依赖变化重新做有界模拟，保存版本、场景、seed、实际时长与停止原因。真实存档不新增文件，临时入口按项目[存档约束](../../AGENTS.md#存档与部署)处理。

## 完整成就映射

官方名称与说明保持schema原文；分类和入口是本项目维护的执行说明。此表承接原成就审计的111项映射，分类变化直接改本表。专用入口的时间见上表；累计型不承诺固定完成时长。

| 官方成就 | 说明 | 类别 | 入口／操作 |
| --- | --- | --- | --- |
| 杂技高手 | 来个后空翻。 | 专用 | [acrobatics.py](acrobatics.py) |
| 手感不错 | 抚摸小猪。 | 专用 | [pet_piggy.py](pet_piggy.py) |
| 杂技大师 | 来 1000 个后空翻。 | 专用 | [acrobatics.py](acrobatics.py) |
| Hello World | 运行你的第一个程序。 | 常规复用 | 任意游戏脚本 |
| 错误 | 造成一个运行时错误。 | 专用 | [cause_runtime_error.py](cause_runtime_error.py) |
| 无限循环 | 创建一个无限循环。 | 专用 | [infinite_loop.py](infinite_loop.py) |
| 时尚达人 | 装备一顶新帽子。 | 常规复用 | [block.py](../functional/block.py) |
| 灌木丛 | 种植一丛灌木。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 胡萝卜 | 种植胡萝卜。 | 常规复用 | [carrot.py](../functional/carrot.py) |
| 树木 | 种植一棵树。 | 常规复用 | [wood.py](../functional/wood.py) |
| 向日葵 | 种植一棵向日葵。 | 常规复用 | [power_sunflower.py](../functional/power_sunflower.py) |
| 仙人掌 | 种植一棵仙人掌。 | 常规复用 | [cactus.py](../functional/cactus.py) |
| 迷宫 | 生成一座迷宫。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 恐龙 | 装备恐龙帽。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 南瓜 | 种植一棵南瓜。 | 常规复用 | [pumpkin.py](../functional/pumpkin.py) |
| 然后呢？ | 解锁所有内容。 | 手动 | 科技树：全部解锁 |
| 巨型农场 | 使用多架无人机。 | 常规复用 | [hay.py](../functional/hay.py) |
| 蜂群 | 同时使用 32 架无人机。 | 常规复用 | [hay.py](../functional/hay.py) |
| 蒸蒸日上 | 扩张农场。 | 手动 | 科技树：扩张 |
| 大型农场 | 农场达到最大规模。 | 手动 | 科技树：最大扩张 |
| 巨型南瓜 | 收获一颗 32x32 的南瓜。 | 专用 | [giant_pumpkin.py](giant_pumpkin.py) |
| 时装秀 | 为 5 架无人机装备 5 顶不同的帽子。 | 专用 | [fashion_show.py](fashion_show.py) |
| 长龙 | 让一个恐龙填满整个农场。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 长度很重要 | 让一个恐龙的长度达到 1000。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 宝藏猎人 | 解开一座填满整个农场的迷宫。 | 专用 | [treasure_hunter.py](treasure_hunter.py) |
| 循环利用 | 重复使用同一座迷宫 300 次。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 农业竞争 | 登上排行榜。 | 榜单复用 | [lb_start.py](../leaderboard/lb_start.py) |
| 全自动化 | 登上“完全复位”排行榜。 | 榜单复用 | [lb_fastest_reset.py](../leaderboard/lb_fastest_reset.py) |
| 干草专业户 | 收获 1000 干草。 | 常规复用 | [hay.py](../functional/hay.py) |
| 木材专业户 | 收获 1000 木材。 | 常规复用 | [wood.py](../functional/wood.py) |
| 胡萝卜专业户 | 收获 1000 胡萝卜。 | 常规复用 | [carrot.py](../functional/carrot.py) |
| 能量专业户 | 收获 1000 能量。 | 常规复用 | [power_sunflower.py](../functional/power_sunflower.py) |
| 南瓜专业户 | 收获 1000 南瓜。 | 常规复用 | [pumpkin.py](../functional/pumpkin.py) |
| 黄金专业户 | 收获 1000 黄金。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 仙人掌专业户 | 收获 1000 仙人掌。 | 常规复用 | [cactus.py](../functional/cactus.py) |
| 骨头专业户 | 收获 1000 骨头。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 干草大亨 | 收获 10 亿干草。 | 常规复用 | [hay.py](../functional/hay.py) |
| 木材大亨 | 收获 10 亿木材。 | 常规复用 | [wood.py](../functional/wood.py) |
| 胡萝卜大亨 | 收获 10 亿胡萝卜。 | 常规复用 | [carrot.py](../functional/carrot.py) |
| 能量大亨 | 收获 100000 能量。 | 常规复用 | [power_sunflower.py](../functional/power_sunflower.py) |
| 南瓜大亨 | 收获 1 亿南瓜。 | 常规复用 | [pumpkin.py](../functional/pumpkin.py) |
| 仙人掌大亨 | 收获 1 亿仙人掌。 | 常规复用 | [cactus.py](../functional/cactus.py) |
| 黄金大亨 | 收获 1 亿黄金。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 骨头大亨 | 收获 1 亿骨头。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 你搞错了 | 将一整片仙人掌按照错误的顺序排列。 | 专用 | [wrong_order.py](wrong_order.py) |
| 泥泞农场 | 让农场整体水位超过 0.5。 | 专用 | [mud_farm.py](mud_farm.py) |
| 妙手回春 | 治愈一株受感染的植物。 | 专用 | [healer.py](healer.py) |
| 循环导入 | 创造一个导入循环（import cycle）。 | 专用 | [circular_import.py](circular_import.py) |
| 高阶编程 | 将一个函数作为参数传递给另一个函数。 | 专用 | [higher_order_programming.py](higher_order_programming.py) |
| 栈溢出 | 造成一次栈溢出（stack overflow）。 | 专用 | [stack_overflow.py](stack_overflow.py) |
| 混沌编程 | 打开 20 个代码窗口。 | 手动 | 工作区打开20个代码窗口 |
| 恐龙大师 | 1 分钟内收获 100 万骨头。 | 常规复用 | [bone_dinosaur.py](../functional/bone_dinosaur.py) |
| 迷宫大师 | 1 分钟内收获 200 万黄金。 | 常规复用 | [gold_maze.py](../functional/gold_maze.py) |
| 干草大师 | 1 分钟内收获 2 亿干草。 | 常规复用 | [hay.py](../functional/hay.py) |
| 胡萝卜大师 | 1 分钟内收获 2 亿胡萝卜。 | 常规复用 | [carrot.py](../functional/carrot.py) |
| 木材大师 | 1 分钟内收获 10 亿木材。 | 常规复用 | [wood.py](../functional/wood.py) |
| 向日葵大师 | 1 分钟内收获 12000 能量。 | 常规复用 | [power_sunflower.py](../functional/power_sunflower.py) |
| 南瓜大师 | 1 分钟内收获 2000 万南瓜。 | 常规复用 | [pumpkin.py](../functional/pumpkin.py) |
| 仙人掌大师 | 1 分钟内收获 2000 万仙人掌。 | 常规复用 | [cactus.py](../functional/cactus.py) |
| 向下挖掘 | 挖掘 1 个地块。 | 常规复用 | [block.py](../functional/block.py) |
| 矿工 | 挖掘 1,000 个地块。 | 常规复用 | [block.py](../functional/block.py) |
| 大矿工 | 挖掘 500,000 个地块。 | 常规复用 | [block.py](../functional/block.py) |
| 采矿大师 | 在 1 分钟内挖掘 1,000,000 个地块。 | 常规复用 | [block.py](../functional/block.py) |
| 铁矿 | 找到 1 个铁矿地块。 | 常规复用 | [iron.py](../functional/iron.py) |
| 铁矿矿工 | 开采 1,000 份铁矿。 | 常规复用 | [iron.py](../functional/iron.py) |
| 铁矿大矿工 | 开采 500,000 份铁矿。 | 常规复用 | [iron.py](../functional/iron.py) |
| 煤炭 | 找到 1 个煤炭地块。 | 常规复用 | [coal.py](../functional/coal.py) |
| 煤炭矿工 | 开采 1,000 份煤炭。 | 常规复用 | [coal.py](../functional/coal.py) |
| 煤炭大矿工 | 开采 500,000 份煤炭。 | 常规复用 | [coal.py](../functional/coal.py) |
| 石英 | 找到 1 个石英地块。 | 常规复用 | [quartz.py](../functional/quartz.py) |
| 石英矿工 | 开采 1,000 份石英。 | 常规复用 | [quartz.py](../functional/quartz.py) |
| 石英大矿工 | 开采 500,000 份石英。 | 常规复用 | [quartz.py](../functional/quartz.py) |
| 梯田 | 种植水稻，覆盖农场的整个地表。 | 专用 | [rice_terrace.py](rice_terrace.py) |
| 稻农 | 收获 1,000 份水稻。 | 常规复用 | [rice.py](../functional/rice.py) |
| 大稻农 | 收获 1,000,000 份水稻。 | 常规复用 | [rice.py](../functional/rice.py) |
| 南瓜古生物学家 | 开采 1,000 个石化南瓜。 | 常规复用 | [pumpkin_petrified.py](../functional/pumpkin_petrified.py) |
| 南瓜古生物学教授 | 开采 500,000 个石化南瓜。 | 常规复用 | [pumpkin_petrified.py](../functional/pumpkin_petrified.py) |
| 竹子 | 种植竹子。 | 常规复用 | [bamboo.py](../functional/bamboo.py) |
| 竹农 | 收获 1,000 份竹子。 | 常规复用 | [bamboo.py](../functional/bamboo.py) |
| 大竹农 | 收获 1,000,000,000 份竹子。 | 常规复用 | [bamboo.py](../functional/bamboo.py) |
| 竹子大师 | 在 1 分钟内开采 15,000,000 份竹子。 | 常规复用 | [bamboo.py](../functional/bamboo.py) |
| 蘑菇 | 找到 1 个蘑菇。 | 常规复用 | [mushroom.py](../functional/mushroom.py) |
| 蘑菇矿工 | 收获 1,000 个蘑菇。 | 常规复用 | [mushroom.py](../functional/mushroom.py) |
| 蘑菇大矿工 | 收获 500,000 个蘑菇。 | 常规复用 | [mushroom.py](../functional/mushroom.py) |
| 炸药 | 找到 1 层炸药。 | 常规复用 | [dynamite.py](../functional/dynamite.py) |
| 炸药矿工 | 开采 1,000 份炸药。 | 常规复用 | [dynamite.py](../functional/dynamite.py) |
| 炸药大矿工 | 开采 50,000,000 份炸药。 | 常规复用 | [dynamite.py](../functional/dynamite.py) |
| 放置 | 放置 1 个地块。 | 专用 | [block_builder.py](block_builder.py) |
| 建造者 | 放置 1,000 个地块。 | 专用 | [block_builder.py](block_builder.py) |
| 大建造者 | 放置 10,000 个地块。 | 专用 | [block_builder.py](block_builder.py) |
| 毕加索 | 放置 1,000 个彩色地块。 | 专用 | [block_builder.py](block_builder.py) |
| 深层采矿 | 到达 z = -10,000 的深度。 | 常规复用 | [block.py](../functional/block.py) |
| 坚持不懈的矿工 | 累计挖掘深度达到 1,000。 | 常规复用 | [block.py](../functional/block.py) |
| 不知疲倦的矿工 | 累计挖掘深度达到 100,000。 | 常规复用 | [block.py](../functional/block.py) |
| 摩天大楼 | 放置地块，使高度达到 z = +150。 | 专用 | [reach_height.py](reach_height.py) |
| 坏掉的锄头 | 尝试耕作岩石。 | 专用 | [till_rock.py](till_rock.py) |
| 探矿者 | 使用铁矿探查 1,000 次。 | 专用 | [prospector.py](prospector.py) |
| 金字塔 | 找到并修复 1 座金字塔。 | 常规复用 | [power_pyramids.py](../functional/power_pyramids.py) |
| 埃及学家 | 找到并修复 200 座金字塔。 | 常规复用 | [power_pyramids.py](../functional/power_pyramids.py) |
| 大金字塔 | 找到并修复 1 座底座为 29×29 的金字塔。 | 常规复用 | [power_pyramids.py](../functional/power_pyramids.py) |
| 彩色金字塔 | 用彩色地块修复 1 座金字塔。 | 专用 | [power_pyramids_color.py](power_pyramids_color.py) |
| 藏宝图 | 使用地图找到宝藏。 | 常规复用 | [gold_treasure_map.py](../functional/gold_treasure_map.py) |
| 大宝藏 | 使用 200 张藏宝图，找到各自指向的宝藏。 | 常规复用 | [gold_treasure_map.py](../functional/gold_treasure_map.py) |
| 藏宝图大师 | 找到宝藏，且不重复经过同一个地块。 | 常规复用 | [gold_treasure_map.py](../functional/gold_treasure_map.py) |
| 蘑菇挤不下 | 尝试推动蘑菇，但未能成功。 | 专用 | [push_mushroom_blocked.py](push_mushroom_blocked.py) |
| 牵线搭桥 | 将同一层中的 95% 蘑菇配对。 | 专用 | [mushroom_matchmaker.py](mushroom_matchmaker.py) |
| 远距离友谊 | 将蘑菇与更下方蘑菇层中颜色相同的蘑菇配对。 | 专用 | [mushroom_cross_stratum.py](mushroom_cross_stratum.py) |
| 炸药排除 | 挖出同一炸药层中的所有哑弹地块。 | 专用 | [dynamite_expert.py](dynamite_expert.py) |
| 炸药排除专家 | 在 32×32 的农场中，挖出 z = -600 或更深处同一炸药层中的所有哑弹地块。 | 专用 | [dynamite_expert.py](dynamite_expert.py) |
| 爆破大师 | 使用爆破钻头。 | 常规复用 | [block.py](../functional/block.py) |
| 不安全的代码 | 摘下矿工帽，继续挖掘。 | 专用 | [mining_helmet_unsafe.py](mining_helmet_unsafe.py) |
