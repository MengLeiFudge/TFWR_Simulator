# 当前游戏规则核对

本页记录2026-10-24对当前安装游戏的静态核对结果。游戏更新后先比较下列指纹；不一致时重新提取资源、读取对应程序集，不能把本页或旧策略文档直接当作新版本规则。实际游戏结果优先于静态推断。

| 来源 | SHA256 |
| --- | --- |
| Core.dll | `b8ac8d22b614d9e48d3affa9a4de9c77e799b824ed8f50dc2e494cc2dd9f9082` |
| Utils.dll | `e2bec8c874a94bd24c5c73e1f967c1f30b2c90912dc83474b77cbf7c6448f9b3` |
| resources.assets | `a465a0e642a5e34687693fee927ef9343f4d2329e75f23a421c03a149d77b6e0` |

这些指纹与本地模拟精度验收来源一致。通过`leaderboard_snapshot_tool.extract_snapshot(resolve_game_root())`重新提取全部16个LeaderboardSO，本机原始结果在`.codex/leaderboard-astra/current-game-rules.json`。已有提取环境可用`uv run --offline --no-project --with UnityPy==1.25.4 --with TypeTreeGeneratorAPI==0.0.10 python`复用缓存；它不是模拟器运行依赖。

## 目标和初始库存

下表列出的初始物品各为十亿；未列出的物品为零，包括初始水和肥料。目标与仓库`lb_start.py`成功条件一致，但这不证明各策略当前时间已复跑准确。

| 榜单 | 目标物品 | 多机目标 | 单机目标 | 初始物品 |
| --- | --- | ---: | ---: | --- |
| Hay | Hay | 2,000,000,000 | 100,000,000 | Power |
| Wood | Wood | 10,000,000,000 | 500,000,000 | Power |
| Carrots | Carrot | 2,000,000,000 | 100,000,000 | Power、Hay、Wood |
| Pumpkins | Pumpkin | 200,000,000 | 10,000,000 | Power、Carrot |
| Cactus | Cactus | 33,554,432 | 131,072 | Power、Pumpkin |
| Maze | Gold | 9,863,168 | 616,448 | Power、Weird_Substance |
| Sunflowers | Power | 100,000 | 10,000 | Carrot |
| Dinosaur | Bone | 33,488,928 | 无对应榜 | Power、Cactus |
| Fastest Reset | 解锁Leaderboard | 解锁等级大于零 | 无对应榜 | 无 |

资源榜使用满级科技；单机入口在`BuiltinFunctions.GetUnlockStrings`将Expand设为5，并跳过Megafarm，地图上限8×8、仅一台无人机。多机使用满级Expand/Megafarm，地图上限32×32、最多32台无人机。策略可以主动缩图；地图及人数应从该榜初始条件推导，不能直接套用模型默认值。

本地`preset=max`默认提供Pumpkin与Power各十亿。构造其他榜的场景时，先将模型默认库存归零，再按上表设置；尤其Sunflowers不能带入默认Power，否则目标、速度和扣款状态都会失真。

## Fastest Reset基础能力

`LeaderboardRun`对非全解锁榜使用`BuiltinFunctions.resetUnlocks`；`Farm`构造器另外提供基础草地、草、收割等能力。对应现有模拟场景可表达的科技覆盖如下，均为等级1：

```json
{
  "preset": "reset",
  "unlocks": {
    "loops": 1, "debug": 1, "debug_2": 1, "timing": 1,
    "lists": 1, "dictionaries": 1, "costs": 1, "auto_unlock": 1,
    "operators": 1, "variables": 1, "senses": 1, "utilities": 1,
    "functions": 1, "import": 1, "simulation": 1
  }
}
```

Grass 1由reset预设已有；Speed、Expand、Plant及其他生产科技仍从零开始，初始库存全零。这些初始能力直接授予，不递归授予它们的父科技。源码列表含有部分历史通信符号，也不代表当前脚本API注册了send/receive等方法。

裸`preset=reset`会令Speed因缺loops而解锁失败，继而阻止Expand和Plant；该停止不构成策略失败或真实完成时间。上述场景已静态对齐基础能力，完整Reset执行仍须单独验证。

## 成功条件、计时和随机种子

`MainSim.LeaderboardExecutionFinished`在脚本结束时检查目标：Reset检查Leaderboard解锁，资源榜检查目标库存。达到库存后仍继续执行的时间会计入成绩；脚本提前结束但未达标也不能算有效完成轮。

官方统计累计至少7200游戏秒后结束，公布累计时间除以完成轮数的均值。单轮较长的Reset可能只完成一轮便结束官方统计；基线比较仍需结合多次运行波动。取消汇总不能替代真实完成轮。

首轮未指定seed时创建新的随机源；后续轮的seed由前一轮多个随机流的状态生成。因此两个算法的后续官方轮次不天然共享同一seed。机制对照应显式使用相同seed的simulate；排行榜比较使用足够完成轮，记录均值、范围和样本数，允许不同seed造成数秒差异。不能把不同seed差异误称为同seed模拟误差，也不能以“有随机性”掩盖持续的阶段偏差。

## 向日葵：必须读完整产量调用链

当前`Sunflower.Harvest`包含`hadIncorrectSunflowerHarvest`判断，但随后进入`Growable.Harvest`，其虚调用`GetYield()`再次进入`Sunflower.GetYield`，重新按当前最大花瓣与至少10株计算`getBoost`。因此单读Harvest中的标记会错误推导实际产量存在惩罚链。

当前资源每株基础Power为1，满足倍率条件时为8；花瓣数本身不乘产量。该调用链解释了已记录实机“先收非最大，再收最大仍有8倍”的结果。旧实测慢成绩保留；采用惩罚链的离线代理结论须重新核对，不能直接用于排除新结构。

源码定位：本机`.codex/tests/high-precision/source/Core.decompiled.cs`中的`Sunflower.Harvest/GetYield`、`Growable.Harvest`、`Farm`构造器、`BuiltinFunctions.resetUnlocks/LeaderboardRun/GetUnlockStrings`与`MainSim.LeaderboardExecutionFinished`。资源条件来自上述新提取快照。

## 当前脚本基线校准

每榜优化前，先核对当前规则，再复跑当前真源；不能把旧文件头时间直接作为当前游戏成绩。记录脚本SHA256、游戏指纹、请求ID、实际完成轮数、均值与范围，并检查BepInEx和Unity两份日志。

至少两轮判断方向，最近两轮差异超过10%则增加轮次。正式更新复跑参考或比较接近候选时使用完整统计或足够轮数；历史成绩保留在同名策略文档。确认后同步脚本头时间、同名文档、`lb_start.py`复跑列，再离线重建比较报告。未完成复跑的榜仍标历史参考，不宣称全榜已校准。
