# TFWR 科技事实表

本文件由真实游戏资源 `UnlockSO` 提取并按反编译逻辑展开。

## 事实源

- `UnlockSO` 字段定义：`Core.decompiled.cs` 的 `UnlockSO`。
- 每级成本：`Farm.GetUnlockCost()`；多级科技先使用 `multiUnlockCost`，超出后按 `multiUnlockFactor` 放大最后一档成本。
- 前置判断：`Farm.UnlockOrUpgrade()` 会检查 `parentUnlock`。
- 每级效果显示：`TooltipUtils.UnlockTooltip()` 的 `MultiUnlockDescrMode`。
- 实际速度：`Farm.MaxSpeedFactor()` 为 `1.5 ** speed_level`，有 Power 时再乘 `2`。
- 水和肥料：`ReceiveWater()` / `ReceiveFertilizer()` 为 `20 / (1 << level)` 秒获得 1 个。
- 作物 / 迷宫 / 恐龙产量类升级：`Growable.YieldFactor` 使用 `1 << (level - 1)`。
- 地图大小：`GridManager.WorldSize` 调 `Helper.WorldSizeScale(expand_level)`；一级扩张特判为 `1x3`。
- 多无人机：`max_drones()` / `spawn_drone()` 使用 `Helper.NumDrones(megafarm_level)`，即 `2 ** level`。

## 科技总览

| 科技 | 前置 | 最高级 | 首次成本 | 解锁符号 / 能力 |
| --- | --- | ---: | --- | --- |
| `auto_unlock` | `costs` | 1 | Pumpkin 5000 | Unlocks, unlock, num_unlocked |
| `cactus` | `pumpkins` | 6 | Pumpkin 5000 | swap, cactus_seed, measure |
| `carrots` | `plant` | 10 | Wood 50 | carrot, till, can_trade, trade, Items, carrot_seed |
| `costs` | `dictionaries` | 1 | Pumpkin 2500 | get_cost, Unlocks |
| `debug` | `plant` | 1 | Hay 50, Wood 50 | print, quick_print, Unlocks, str |
| `debug_2` | `debug` | 1 | Gold 500 | set_execution_speed, set_world_size |
| `dictionaries` | `lists` | 1 | Pumpkin 2500 | dicts, sets, add, dict, set |
| `dinosaurs` | `cactus` | 6 | Cactus 2000 | dinosaur, egg, bone, change_hat, hats, dinosaur_hat, apple, can_move |
| `expand` | `speed` | 9 | Hay 30 | move, North, South, East, West, 2for, 2range, 2get_world_size |
| `fertilizer` | `watering` | 4 | Wood 500 | use_item, weird_substance |
| `functions` | `variables` | 1 | Carrot 40 | functions, def, return, global |
| `grass` | `loops` | 10 | Hay 100 | - |
| `hats` | `loops` | 1 | Hay 50 | change_hat, gray_hat, purple_hat, green_hat, brown_hat |
| `import` | `functions` | 1 | Carrot 80 | from |
| `leaderboard` | `simulation` | 1 | Gold 1000000, Bone 2000000 | leaderboard_run, Leaderboards |
| `lists` | `variables` | 1 | Carrot 500 | append, remove, pop, insert, len, list |
| `loops` | `-` | 1 | Hay 5 | while, True, False, break, continue |
| `mazes` | `fertilizer` | 6 | Weird_Substance 1000 | hedge, treasure, gold, measure, can_move |
| `megafarm` | `mazes` | 5 | Gold 2000 | get_drone_id, num_drones, max_drones, wait_for, spawn_drone, has_finished |
| `operators` | `plant` | 1 | Hay 150, Wood 10 | and, or, not |
| `plant` | `speed` | 1 | Hay 50 | wood, bush, Entities, clear |
| `polyculture` | `pumpkins` | 5 | Pumpkin 3000 | get_companion |
| `pumpkins` | `trees` | 10 | Wood 500, Carrot 200 | pumpkin, pumpkin_seed, dead_pumpkin |
| `senses` | `operators` | 1 | Hay 100 | get_entity_type, get_ground_type, Grounds, get_pos_x, get_pos_y, None, num_items, Items, num_unlocked |
| `simulation` | `timing` | 1 | Gold 5000 | simulate |
| `speed` | `loops` | 5 | Hay 20 | can_harvest, if, else, elif |
| `sunflowers` | `watering` | 1 | Carrot 500 | sunflower_seed, sunflower, power, get_active_power, measure |
| `the_farmers_remains` | `dinosaurs` | 1 | Bone 100000000 | change_hat |
| `timing` | `debug` | 1 | Pumpkin 1000 | get_time, get_tick_count |
| `top_hat` | `mazes` | 1 | Gold 100000000, Cactus 1000000000, Hay 1000000000, Carrot 1000000000, Wood 10000000000 | change_hat |
| `trees` | `carrots` | 10 | Wood 50, Carrot 70 | tree |
| `utilities` | `functions` | 1 | Pumpkin 1000 | min, max, abs, random |
| `variables` | `operators` | 1 | Carrot 35 | - |
| `watering` | `carrots` | 9 | Wood 50 | water, use_item, get_water |

## 每级成本与效果

### `auto_unlock`

- 前置：`costs`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_auto_unlock` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 5000 | 解锁符号/能力：Unlocks, unlock, num_unlocked |

### `cactus`

- 前置：`pumpkins`
- 最高级：`6`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_cactus` / `multi_unlock_descr_cactus`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 5000 | 100%（约 1x） |
| 2 | Pumpkin 20000 | 200%（约 2x） |
| 3 | Pumpkin 120000 | 400%（约 4x） |
| 4 | Pumpkin 720000 | 800%（约 8x） |
| 5 | Pumpkin 4320000 | 1600%（约 16x） |
| 6 | Pumpkin 25920000 | 3200%（约 32x） |

### `carrots`

- 前置：`plant`
- 最高级：`10`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_carrots` / `multi_unlock_descr_carrots`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Wood 50 | 100%（约 1x） |
| 2 | Wood 250 | 200%（约 2x） |
| 3 | Wood 1250 | 400%（约 4x） |
| 4 | Wood 6250 | 800%（约 8x） |
| 5 | Wood 31250 | 1600%（约 16x） |
| 6 | Wood 156250 | 3200%（约 32x） |
| 7 | Wood 781250 | 6400%（约 64x） |
| 8 | Wood 3906250 | 12800%（约 128x） |
| 9 | Wood 19531250 | 25600%（约 256x） |
| 10 | Wood 97656250 | 51200%（约 512x） |

### `costs`

- 前置：`dictionaries`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_costs` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 2500 | 解锁符号/能力：get_cost, Unlocks |

### `debug`

- 前置：`plant`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_debug` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 50, Wood 50 | 解锁符号/能力：print, quick_print, Unlocks, str |

### `debug_2`

- 前置：`debug`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_debug2` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Gold 500 | 解锁符号/能力：set_execution_speed, set_world_size |

### `dictionaries`

- 前置：`lists`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_dicts` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 2500 | 解锁符号/能力：dicts, sets, add, dict, set |

### `dinosaurs`

- 前置：`cactus`
- 最高级：`6`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_dinosaurs` / `multi_unlock_descr_dinosaur`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Cactus 2000 | 100%（约 1x） |
| 2 | Cactus 12000 | 200%（约 2x） |
| 3 | Cactus 72000 | 400%（约 4x） |
| 4 | Cactus 432000 | 800%（约 8x） |
| 5 | Cactus 2592000 | 1600%（约 16x） |
| 6 | Cactus 15552000 | 3200%（约 32x） |

### `expand`

- 前置：`speed`
- 最高级：`9`
- 效果模式：`grid_size`
- 描述键：`unlock_descr_expand` / `multi_unlock_descr_expand`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 30 | 1x3 |
| 2 | Wood 20 | 3x3 |
| 3 | Wood 30, Carrot 20 | 4x4 |
| 4 | Wood 100, Carrot 50 | 6x6 |
| 5 | Pumpkin 1000 | 8x8 |
| 6 | Pumpkin 8000 | 12x12 |
| 7 | Pumpkin 64000 | 16x16 |
| 8 | Pumpkin 512000 | 24x24 |
| 9 | Pumpkin 4096000 | 32x32 |

### `fertilizer`

- 前置：`watering`
- 最高级：`4`
- 效果模式：`per_10_seconds`
- 描述键：`unlock_descr_fertilizer` / `multi_unlock_descr_fertilizer`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Wood 500 | 0.1/s（每 10s 1 个） |
| 2 | Wood 1500 | 0.2/s（每 10s 2 个） |
| 3 | Wood 9000 | 0.4/s（每 10s 4 个） |
| 4 | Wood 54000 | 0.8/s（每 10s 8 个） |

### `functions`

- 前置：`variables`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_functions` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Carrot 40 | 解锁符号/能力：functions, def, return, global |

### `grass`

- 前置：`loops`
- 最高级：`10`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_grass` / `unlock_descr_grass`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 100 | 100%（约 1x） |
| 2 | Hay 300 | 200%（约 2x） |
| 3 | Wood 500 | 400%（约 4x） |
| 4 | Wood 2500 | 800%（约 8x） |
| 5 | Wood 12500 | 1600%（约 16x） |
| 6 | Wood 62500 | 3200%（约 32x） |
| 7 | Wood 312500 | 6400%（约 64x） |
| 8 | Wood 1562500 | 12800%（约 128x） |
| 9 | Wood 7812500 | 25600%（约 256x） |
| 10 | Wood 39062500 | 51200%（约 512x） |

### `hats`

- 前置：`loops`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_hats` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 50 | 解锁符号/能力：change_hat, gray_hat, purple_hat, green_hat, brown_hat |

### `import`

- 前置：`functions`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_import` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Carrot 80 | 解锁符号/能力：from |

### `leaderboard`

- 前置：`simulation`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_leaderboard` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Gold 1000000, Bone 2000000 | 解锁符号/能力：leaderboard_run, Leaderboards |

### `lists`

- 前置：`variables`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_lists` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Carrot 500 | 解锁符号/能力：append, remove, pop, insert, len, list |

### `loops`

- 前置：`-`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_loops` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 5 | 解锁符号/能力：while, True, False, break, continue |

### `mazes`

- 前置：`fertilizer`
- 最高级：`6`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_mazes` / `multi_unlock_descr_mazes`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Weird_Substance 1000 | 100%（约 1x） |
| 2 | Cactus 12000 | 200%（约 2x） |
| 3 | Cactus 72000 | 400%（约 4x） |
| 4 | Cactus 432000 | 800%（约 8x） |
| 5 | Cactus 2592000 | 1600%（约 16x） |
| 6 | Cactus 15552000 | 3200%（约 32x） |

### `megafarm`

- 前置：`mazes`
- 最高级：`5`
- 效果模式：`megafarm`
- 描述键：`unlock_descr_megafarm` / `multi_unlock_descr_megafarm`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Gold 2000 | 最多 2 架无人机 |
| 2 | Gold 8000 | 最多 4 架无人机 |
| 3 | Gold 32000 | 最多 8 架无人机 |
| 4 | Gold 128000 | 最多 16 架无人机 |
| 5 | Gold 512000 | 最多 32 架无人机 |

### `operators`

- 前置：`plant`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_operators` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 150, Wood 10 | 解锁符号/能力：and, or, not |

### `plant`

- 前置：`speed`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_plant` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 50 | 解锁符号/能力：wood, bush, Entities, clear |

### `polyculture`

- 前置：`pumpkins`
- 最高级：`5`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_polyculture` / `multi_unlock_descr_polyculture`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 3000 | 1000%（约 10x） |
| 2 | Bone 10000 | 2000%（约 20x） |
| 3 | Bone 50000 | 4000%（约 40x） |
| 4 | Bone 250000 | 8000%（约 80x） |
| 5 | Bone 1250000 | 16000%（约 160x） |

### `pumpkins`

- 前置：`trees`
- 最高级：`10`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_pumpkin` / `multi_unlock_descr_pumpkins`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Wood 500, Carrot 200 | 100%（约 1x） |
| 2 | Carrot 1000 | 200%（约 2x） |
| 3 | Carrot 4000 | 400%（约 4x） |
| 4 | Carrot 16000 | 800%（约 8x） |
| 5 | Carrot 64000 | 1600%（约 16x） |
| 6 | Carrot 256000 | 3200%（约 32x） |
| 7 | Carrot 1024000 | 6400%（约 64x） |
| 8 | Carrot 4096000 | 12800%（约 128x） |
| 9 | Carrot 16384000 | 25600%（约 256x） |
| 10 | Carrot 65536000 | 51200%（约 512x） |

### `senses`

- 前置：`operators`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_senses` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 100 | 解锁符号/能力：get_entity_type, get_ground_type, Grounds, get_pos_x, get_pos_y, None, num_items, Items, num_unlocked |

### `simulation`

- 前置：`timing`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_simulation` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Gold 5000 | 解锁符号/能力：simulate |

### `speed`

- 前置：`loops`
- 最高级：`5`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_speed` / `unlock_descr_speed`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Hay 20 | 150%（约 1.5x） |
| 2 | Wood 20 | 225%（约 2.25x） |
| 3 | Wood 50, Carrot 50 | 337.5%（约 3.375x） |
| 4 | Carrot 500 | 506.25%（约 5.0625x） |
| 5 | Carrot 1000 | 759.375%（约 7.59375x） |

### `sunflowers`

- 前置：`watering`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_sunflowers` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Carrot 500 | 解锁符号/能力：sunflower_seed, sunflower, power, get_active_power, measure |

### `the_farmers_remains`

- 前置：`dinosaurs`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_the_farmers_remains` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Bone 100000000 | 解锁符号/能力：change_hat |

### `timing`

- 前置：`debug`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_timing` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 1000 | 解锁符号/能力：get_time, get_tick_count |

### `top_hat`

- 前置：`mazes`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_top_hat` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Gold 100000000, Cactus 1000000000, Hay 1000000000, Carrot 1000000000, Wood 10000000000 | 解锁符号/能力：change_hat |

### `trees`

- 前置：`carrots`
- 最高级：`10`
- 效果模式：`additive_percent`
- 描述键：`unlock_descr_trees` / `multi_unlock_descr_trees`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Wood 50, Carrot 70 | 100%（约 1x） |
| 2 | Hay 300 | 200%（约 2x） |
| 3 | Hay 1200 | 400%（约 4x） |
| 4 | Hay 4800 | 800%（约 8x） |
| 5 | Hay 19200 | 1600%（约 16x） |
| 6 | Hay 76800 | 3200%（约 32x） |
| 7 | Hay 307200 | 6400%（约 64x） |
| 8 | Hay 1228800 | 12800%（约 128x） |
| 9 | Hay 4915200 | 25600%（约 256x） |
| 10 | Hay 19660800 | 51200%（约 512x） |

### `utilities`

- 前置：`functions`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_utilities` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Pumpkin 1000 | 解锁符号/能力：min, max, abs, random |

### `variables`

- 前置：`operators`
- 最高级：`1`
- 效果模式：`none`
- 描述键：`unlock_descr_variables` / ``

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Carrot 35 | 一次性解锁 |

### `watering`

- 前置：`carrots`
- 最高级：`9`
- 效果模式：`per_10_seconds`
- 描述键：`unlock_descr_watering` / `multi_unlock_descr_watering`

| 等级 | 成本 | 效果 |
| ---: | --- | --- |
| 1 | Wood 50 | 0.1/s（每 10s 1 个） |
| 2 | Wood 200 | 0.2/s（每 10s 2 个） |
| 3 | Wood 800 | 0.4/s（每 10s 4 个） |
| 4 | Wood 3200 | 0.8/s（每 10s 8 个） |
| 5 | Wood 12800 | 1.6/s（每 10s 16 个） |
| 6 | Wood 51200 | 3.2/s（每 10s 32 个） |
| 7 | Wood 204800 | 6.4/s（每 10s 64 个） |
| 8 | Wood 819200 | 12.8/s（每 10s 128 个） |
| 9 | Wood 3276800 | 25.6/s（每 10s 256 个） |
