# 成就脚本

本目录只保存需要刻意制造特殊状态、且常规/排行榜流程不能稳定完成的 Steam 成就入口。每个入口都以 `MAX_GAME_SECONDS = 300` 为运行上限；完成目标后返回，故意触发错误的入口除外。采矿大师仍使用功能目录的 [`block.py`](../functional/block.py)。

## 完整筛选表

判定依据是 `references/DecompiledSource/Core/Core.decompiled.cs` 中的 `UnlockAchievement` 调用。表中“复用”表示正常流程已包含该触发动作，不再复制脚本；“手动”表示成就不是脚本入口能稳定完成的目标。

| 成就 | 入口或复用 | 分类 |
| --- | --- | --- |
| `SPAWN_MAZE` | `functional/gold_maze.py` / `leaderboard/lb_maze.py` | 复用建迷宫 |
| `WRONG_ORDER` | [`wrong_order.py`](wrong_order.py) | 特殊仙人掌排列 |
| `HEALER` | `functional/gold_maze.py` | 复用两次怪异物质恢复 |
| `MUSHROOM_STARTUM_SKIP` | [`mushroom_cross_stratum.py`](mushroom_cross_stratum.py) | 特殊跨原生地层 |
| `MUSHROOM_STRATUM_OPTIMAL` | [`mushroom_matchmaker.py`](mushroom_matchmaker.py) | 特殊95%同层配对 |
| `GIANT_PUMPKIN` | `functional/pumpkin.py` | 复用正常南瓜周期 |
| `RESTORE_MAX_PYRAMID` | `functional/power_pyramids.py` / `leaderboard/lb_pyramids.py` | 复用实际塔边界修复 |
| `RESTORE_COLOR_PYRAMID` | [`power_pyramids_color.py`](power_pyramids_color.py) | 特殊彩色修复 |
| `DYNAMITE_OPTIMAL`, `DYNAMITE_MAX_OPTIMAL` | `functional/dynamite.py` | 复用完整解盘结算 |
| `TREASURE_HUNTER`, `RECYCLING` | `functional/gold_maze.py` | 复用迷宫收获与重用 |
| `TREASURE_OPTIMAL` | `functional/gold_treasure_map.py` / `leaderboard/lb_treasure_map.py` | 复用无环路径 |
| `EQUIP_DINO_HAT`, `LONG_DINOSAUR`, `SIZE_MATTERS` | `functional/bone_dinosaur.py` | 复用恐龙周期 |
| `EXPLOSIVE_DRILL` | `functional/block.py` / `functional/mining.py` | 复用爆破钻挖掘 |
| `EQUIP_A_NEW_HAT` | 任一更换非草帽的功能入口 | 复用换帽 |
| `FASHION_SHOW` | [`fashion_show.py`](fashion_show.py) | 特殊5帽同时在场 |
| `PET_THE_PIGGY` | [`pet_piggy.py`](pet_piggy.py) | 特殊交互 |
| `MINING_HELMET_UNSAFE` | [`mining_helmet_unsafe.py`](mining_helmet_unsafe.py) | 特殊非采矿帽挖掘 |
| `REACH_HEIGHT` | [`reach_height.py`](reach_height.py) | 特殊深度放块 |
| `PUSH_MUSHROOM_BLOCKED` | [`push_mushroom_blocked.py`](push_mushroom_blocked.py) | 特殊受阻推蘑菇 |
| `TILL_ROCK` | [`till_rock.py`](till_rock.py) | 特殊对岩石翻地 |
| `PLANT_BUSH`, `PLANT_CARROTS`, `PLANT_TREE`, `PLANT_PUMPKIN`, `PLANT_SUNFLOWER`, `PLANT_CACTUS`, `PLANT_BAMBOO` | 对应 `functional/` 入口 | 复用正常种植 |
| `RICE_TERRACE` | `functional/rice.py` | 复用铺满水稻梯田 |
| `MUD_FARM` | [`mud_farm.py`](mud_farm.py) | 特殊全田补水 |
| `EXPAND`, `BIG_FARM` | 科技升级界面 | 手动/科技进度 |
| `RUN_YOUR_FIRST_CODE` | 任一游戏脚本 | 复用执行代码 |
| `USE_MULTIPLE_DRONES`, `SWARM` | 任一多机功能/排行榜入口 | 复用派机 |
| `CAUSE_A_RUNTIME_ERROR` | [`cause_runtime_error.py`](cause_runtime_error.py) | 特殊故意报错 |
| `REACH_DEPTH` | `functional/mining.py`、`block.py` | 长期累计挖掘，不伪造5分钟完成 |
| `INFINITE_LOOP` | [`infinite_loop.py`](infinite_loop.py) | 特殊字面量死循环 |
| `HIGHER_ORDER_PROGRAMMING` | [`higher_order_programming.py`](higher_order_programming.py) | 特殊函数参数 |
| `CIRCULAR_IMPORT` | [`circular_import.py`](circular_import.py) 及两个依赖 | 特殊循环导入 |
| `STACK_OVERFLOW` | [`stack_overflow.py`](stack_overflow.py) | 特殊递归溢出 |
| `COMPETITIVE_FARMING`, `FULL_AUTOMATION` | `leaderboard/lb_start.py` 对应完整榜单 | 复用榜单结算 |
| `UNLOCK_EVERYTHING` | 科技树升级 | 手动/科技进度 |
| `CHAOS` | 工作区窗口操作 | 手动/UI 状态 |

## 运行约定

- 入口必须用全科技场景和足够的物料做本地模拟；真实 Save0 未被本任务修改。`scripts/achievement/` 不通过 `resources.py` 调度。
- 彩色金字塔、跨地层蘑菇和牵线搭桥沿用已有的完整算法；其截止时间、材料和中止状态见 [`docs/achievement-validation.json`](../../docs/achievement-validation.json)。
- `mud_farm.py` 需要至少2048份水，`reach_height.py` 需要Block，`wrong_order.py` 需要至少9份仙人掌种子；其他入口也可能依赖全科技和基础库存。
- `cause_runtime_error.py`、`infinite_loop.py`、`stack_overflow.py` 是故意停止的入口。启动后只需确认成就触发，再停止，不应纳入自动资源调度。
- `circular_import.py` 的循环导入由游戏解释器判定；当前本地模拟器验证了入口、依赖和导入语法，但没有伪造 Steam 成就状态。
- `REACH_DEPTH`、`EXPAND`、`BIG_FARM`、`UNLOCK_EVERYTHING`、`CHAOS` 没有新增限时脚本：它们分别是长期累计、科技树或 UI 状态，强行写成一次性入口会造成错误完成承诺。

## 本轮常规入口审计

常规入口逐个与同名 `lb_*.py` 对照：有对应榜单的入口均保留成熟榜单算法，只增加库存目标、材料边界和子机回收；煤、铁、石英、石化南瓜、建材和怪异物质没有直接榜单入口，按各自地下机制独立保留。确认并修复的一项是 `functional/coal.py` 的有限目标没有传入探孔和矿层递归，导致子机继续挖掘并可能越过库存目标；现在所有递归、派机和实际挖掘都传递 `target`，并将周期日志改为零耗时 `quick_print`。

未发现可以在没有新鲜同场效率证据时安全替换的其他常规算法。排行榜脚本只作为算法来源，不把排行榜成绩或本地预估当作普通功能脚本的实测成绩。
