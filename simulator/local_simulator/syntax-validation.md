# 游戏语言静态检查

本地模拟器在编译入口和每个实际导入的同目录模块时，检查已实现的游戏语法与解析后静态规则。失败返回 `GameSyntaxError`，停止该脚本的模拟，不生成可放行的效率结论。Python语法解析及既有受支持节点检查仍先执行。

实现位于 [syntax.py](syntax.py)。调用参数规则依据当前反编译 `Core.decompiled.cs` 中 `Parser.IndexDotOrCallExpression()` 与 `Sequence()`；无意义表达式规则依据 `CodeWindow.Parse()` 调用的 `CheckForNonsensicalCode()`，涵盖该层全部三个覆写。这些规则不代表完整游戏语法、类型及解锁门槛已经全部复刻。

| 游戏检查 | 本地拒绝的形式 | 错误码 |
| --- | --- | --- |
| `Parser.IndexDotOrCallExpression` / `Sequence` | 调用中使用 `target=target` 这类关键字参数，或 `**mapping` 参数解包 | `error_expected_close_token`、`error_invalid_expression` |
| `BinaryExprNode.CheckTautologicalOrExpressions` | 直接比较表达式后用 `or` 接字面常量，例如 `x == 5 or True`、`x == 5 or 6` | `error_nonsensical_or` |
| `BranchNode.CheckWeirdAlwaysTrueConditions` | `if`、`while`直接使用物品、实体、地面或科技常量作条件，例如 `if Items.Hay:` | `error_item_condition`、`error_entity_condition`、`error_ground_condition`、`error_unlock_condition` |
| `ComparisonNode.CheckFarmLiteralsComparedWithNumbers` | 把物品、实体或科技常量当作数量比较，例如 `Items.Hay > 0`、`Entities.Tree == 1` | `error_compared_item_with_number`、`error_compared_entity_with_number`、`error_compared_unlock_with_number` |

保留原版的检查边界：变量的 `value or 6`、`while True`、`if True`以及两个实际比较的组合均可使用。游戏保留括号节点，`(x == 5) or 6`与 `x == 5 or (6)`不匹配第一条规则；本地使用词法位置保留这项差异，不通过常量传播扩大拒绝范围。链式比较的检查停止位置也按原版处理。

错误报告含 `error.code`、`path`、`line`、`column`、`end_line` 和 `end_column`，行列从1开始；中文字符串前缀按字符列定位。入口编译失败发生在世界初始化前；模块编译失败会报告出错模块的位置，而不是入口中import那一行。

## 调用参数规则

游戏支持函数定义中的默认值，例如 `def block(target=-1):`；函数调用只接受按声明顺序传入的位置参数。需要跳过有默认值的中间参数时，显式传入该默认值：

```python
def mine(item, kind, depth, unlock=None, target=-1):
    pass

mine(Items.Block, None, 16, None, target)
```

2026-11-08的游戏报错图确认 `block.py` 中的 `mining.mine(Items.Block, None, 16, target=target)` 在等号处被拒绝。原版调用参数由 `Sequence()` 解析普通表达式，表达式后只接受逗号或右括号；该形式对应 `error_expected_close_token`。本地此前允许 `ast.keyword` 而漏报，现由调用语法检查在编译阶段拒绝，并保留文件、行列与等号位置。该修复不改变函数默认值或位置参数的运行语义。

## 木材脚本修正

`wood.py` 的胡萝卜补料判断误写成了 `num_items(Items.Hay) < carrot_hay or True`。正确条件为：

```python
if c == Entities.Carrot and (num_items(Items.Hay) < carrot_hay or num_items(Items.Wood) < carrot_wood):
```

该条件恢复了源排行榜算法：Hay或Wood不够支付胡萝卜种子时才退回Bush。移除排行榜库存终点时，材料判断必须保留，不能按目标物品名称批量替换所有比较。

2026-11-08的用户报错图与本地冻结文件对应第86行。修正前，本地现在会在第86行、第80列的 `or` 返回 `error_nonsensical_or`；从另一个入口导入坏文件也返回相同模块位置。修正后21个功能模块通过本层及既有编译检查。

21项有界编译检查覆盖12项拒绝、9项合法保留，包括括号、连续or、恒真循环、资源常量、数值比较和中文列定位。原始记录保存在 `.codex/functional-syntax-20261108/`。这些是静态编译证据，其他规则以原版源码及具体实机记录为准。

修正后的木材脚本按30秒现实预算完成连续产出采样，数据与完整轮对照保存于[功能效率记录](../../docs/functional-validation.md)及[实际时间采样数据](../../docs/functional-rate-validation.json)。早先含 `or True` 的候选即使曾被旧模型执行，其效率数据也已撤回。现有Save0的 `wood.py`已在idle状态下同步同一行修复，备份保存在本地证据目录。
