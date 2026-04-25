# TFWR 科技事实表

本目录固化科技解锁事实，供 leaderboard 策略脚本和策略文档引用。

## 文件职责

- `unlock_snapshot.json`
  - 机器可读事实表
  - 包含每个科技的前置、最高等级、成本字段、效果字段和每级展开结果
- `unlock_snapshot.md`
  - 人工阅读版事实表
  - 用于快速检查每个科技的解锁顺序、每级成本和每级效果

## 事实来源

- 科技原始数据来自真实游戏资源里的 `UnlockSO`。
- 字段定义参考 `references/DecompiledSource/Core/Core.decompiled.cs` 的 `UnlockSO`。
- 每级成本展开参考 `Farm.GetUnlockCost()`。
- 前置检查参考 `Farm.UnlockOrUpgrade()`。
- 每级效果显示参考 `TooltipUtils.UnlockTooltip()`。
- 实际机制额外参考：
  - `Farm.MaxSpeedFactor()`
  - `Farm.ReceiveWater()`
  - `Farm.ReceiveFertilizer()`
  - `Growable.YieldFactor`
  - `GridManager.WorldSize`
  - `Helper.NumDrones()`

## 刷新命令

需要先安装提取 Unity 资源所需的 Python 依赖：

```bash
python3 -m pip install UnityPy TypeTreeGeneratorAPI
```

然后在仓库根目录执行：

```bash
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format json --output references/unlocks/unlock_snapshot.json
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format markdown --output references/unlocks/unlock_snapshot.md
```

如果不想修改当前 Python 环境，可以把依赖安装到临时目录，再临时设置
`PYTHONPATH`：

```bash
python3 -m pip install --target /tmp/tfwr_unitypy_deps UnityPy TypeTreeGeneratorAPI
PYTHONPATH=/tmp/tfwr_unitypy_deps python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format json --output references/unlocks/unlock_snapshot.json
PYTHONPATH=/tmp/tfwr_unitypy_deps python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format markdown --output references/unlocks/unlock_snapshot.md
```

刷新后应重点检查：

- `parent_unlock` 是否符合当前游戏科技树。
- `max_unlock_level` 是否符合当前游戏资源。
- `levels[].cost` 是否已经按 `multiUnlockFactor` 展开。
- `levels[].effect` 是否符合反编译 tooltip 和真实机制。
