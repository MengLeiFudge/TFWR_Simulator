# 游戏语言静态检查

游戏脚本使用原版`Tokenizer/Parser`定义的语言子集。Python能够解析或执行一段代码，不表示游戏支持它。不要在游戏脚本中使用三元条件表达式、推导式、lambda、f-string、参数解包、`is`比较等Python专属写法。此约束适用于游戏源文件；模拟器和控制工具使用标准Python。

编译入口及每个实际导入的同目录模块，统一先检查原版游戏语法和解析后的静态规则，再检查本地执行后端的覆盖范围。非法游戏语法返回`GameSyntaxError`；原版支持而本地尚未覆盖的形态返回`UnsupportedMechanism`。两者都停止模拟，不能生成可放行的效率结论。入口编译失败发生在世界初始化前；导入模块失败保留该模块的位置。

## 实现与依据

[game_parser.py](game_parser.py)对应当前反编译[Tokenizer与Parser](../../references/DecompiledSource/Core/Core.decompiled.cs#L18716)，检查原版词法、运算符层次、调用/容器序列、函数参数、缩进块、控制流及导入语法。[syntax.py](syntax.py)检查赋值目标、先声明global后赋值，以及`CodeWindow.Parse()`调用的三个`CheckForNonsensicalCode()`覆写。[runner.py](runner.py)的`compile_source`把它们放在执行覆盖检查之前。

后端计费转换为了模拟短路求值可以生成`IfExp`等内部节点；内部实现能力不能作为游戏源语法的支持依据。游戏源代码的执行白名单不再包含`ast.IfExp`、`ast.Is`和`ast.IsNot`。源码或依赖变化后须重新检查，不能沿用旧源码的效率报告。

## 可用写法与拒绝边界

| 类别 | 游戏脚本中的写法 |
| --- | --- |
| 条件分支 | 使用换行缩进的`if/elif/else`；不使用`a if condition else b` |
| 循环 | 使用普通`for`、`while`、`break`、`continue`；不使用`for/while ... else`或推导式 |
| 函数 | 使用`def`及普通默认参数；调用只用位置参数，不用关键字参数、`*args`或`**mapping` |
| 容器 | 使用普通list/tuple/dict/set字面量、索引及切片；切片不能作为赋值目标 |
| 导入与作用域 | 使用同层模块名及普通`import/from`，不用`as`；每条`global`只声明一个名称，且在同作用域首次赋值之前声明 |
| 运算 | 使用原版算术、比较、`in/not in`和`and/or/not`；不用`is/is not`、位运算、链式赋值或`**=` |
| 代码块 | 冒号后换行并缩进；不用分号串联语句或单行复合语句 |
| 数字 | 只用十进制整数或小数，不用`1e9`、`1_000`、`0xff`等形式 |
| 字符串 | 只用一对单/双引号，不用前缀、三引号、f-string或隐式拼接；内容按原版取引号内原文，不按Python解释转义 |
| 其他结构 | 不使用类、装饰器、lambda、生成器、异常处理、上下文管理器和异步语法 |

原版支持的类型注解与本地执行覆盖分开判断。例如当前返回类型注解会在游戏语法层通过，随后由本地后端返回`UnsupportedMechanism`；不能将其误记为游戏不支持，也不能当作已完成模拟。

推荐把调用中的条件参数写成普通分支：

```python
if height == 1:
    bamboo_sweep(rows, water_level)
else:
    bamboo_sweep(rows, -1)
```

函数定义中的默认值可以保留。需要跳过中间默认参数时，调用中显式传入该默认值：

```python
def mine(item, kind, depth, unlock=None, target=-1):
    pass

mine(Items.Block, None, 16, None, target)
```

## 解析后的静态规则

| 游戏检查 | 本地拒绝的形式 | 错误码 |
| --- | --- | --- |
| `Parser.Sequence` | 调用中使用三元表达式、关键字参数等无法继续解析的表达式 | `error_expected_close_token` |
| `Parser.AtomicExpression` | `*args`、`**mapping`等不属于原版表达式的输入 | `error_invalid_expression` |
| `Parser.CheckAssignmentLhsRec` | 给切片或游戏常量赋值 | `error_invalid_assign_expr` |
| `Parser.Statement` | 赋值后才声明同名global；把内置函数名直接作为独立语句 | `error_assign_before_global`、`error_not_a_statement2` |
| `BinaryExprNode.CheckTautologicalOrExpressions` | 直接比较表达式后用`or`接字面常量，例如`x == 5 or True`、`x == 5 or 6` | `error_nonsensical_or` |
| `BranchNode.CheckWeirdAlwaysTrueConditions` | `if/while`直接使用物品、实体、地面或科技常量作条件 | `error_item_condition`、`error_entity_condition`、`error_ground_condition`、`error_unlock_condition` |
| `ComparisonNode.CheckFarmLiteralsComparedWithNumbers` | 把物品、实体或科技常量当作数量比较 | `error_compared_item_with_number`、`error_compared_entity_with_number`、`error_compared_unlock_with_number` |

变量的`value or 6`、`while True`、`if True`及两个实际比较的组合可以使用。游戏保留括号节点，`(x == 5) or 6`与`x == 5 or (6)`不匹配无意义or规则；本地按词法位置保留该差异，不通过常量传播扩大拒绝范围。链式比较的检查停止位置也按原版处理。

错误报告包含`error.code`、`path`、`line`、`column`、`end_line`和`end_column`，行列从1开始。错误定位按字符计数，保留中文前缀后的正确列号。

## 运行时运算类型

语法合法还须满足原版类型规则。`*`只接受数值，包括原版作为数值子类的布尔值；`[value] * count`、元组或字符串重复在游戏中都不成立。初始化列表时使用普通循环和`append()`。这是运行时操作数错误，不能误报为解析失败，也不能因CPython支持序列重复就放行。

2026-11-09实机request456、458分别在炸药单机的第47行和竹子单机的第16行拒绝列表乘法。本地`timing.operation`现按当前`BinaryExprNode`限制乘法操作数；读取相同失败源也在上述行返回TypeError。两份竹子及炸药单机显式初始化后，分别重新完成三seed原目标及官方完整统计。原错误源的效率放行资格撤回。源、报告、当前DLL与反编译指纹见[运算对齐证据](operator-validation.json)。错误文案和所有类型组合尚未逐项实机核对，不据此声称整个语言语义已经对齐。

## 2026-11-08：竹子条件表达式漏检修复

用户截图中的`lb_bamboo_single.py`调用使用了`water_level if height == 1 else -1`，游戏在`if`处提示“应为逗号或右括号”。同一问题也存在于多机竹子。旧模拟器把`ast.IfExp`列入执行白名单，语法检查只覆盖少量规则，因而错误执行了原版无法解析的源文件。

现已按原版词法及语法增加前置解析，两份竹子均改为上方普通分支。旧的两个源码SHA及对应265.463529150/321.377046810秒预测撤回放行资格；不能用旧模型能执行来证明它们可在游戏运行。新源码重新完成单双机各三seed原目标，当前记录见[单机竹子](../../docs/leaderboards/lb_bamboo_single.md)与[多机竹子](../../docs/leaderboards/lb_bamboo.md)。

完整CLI重新读取旧冻结脚本后，退出码为1，在第66行、第44列返回`error_expected_close_token`，预测时间、效率与目标状态均为null，没有初始化世界或产生有效产量。修正后的54份现有游戏脚本全部通过静态编译；48项语法形态编译记录为38项按原版拒绝、9项合法保留、1项本地覆盖缺口。记录只编译源码，不执行其函数或构造测试套件。

代码和词法逐段依据当前原版源码核对；本轮未新增游戏端编译或完整打榜对照，不将静态编译等同于全部语义与时间精度通过。长期证据见[语法修复记录](../../docs/leaderboards/game_syntax_validation.json)，本机原始证据在`.codex/game-syntax-parity-20261108/`。

## 历史关键字参数与木材条件修正

此前`block.py`中的`mining.mine(Items.Block, None, 16, target=target)`在游戏等号处被拒绝。原版调用由`Sequence()`解析普通表达式，之后只接受逗号或右括号，错误码为`error_expected_close_token`。函数定义中的默认值不受影响。

此前`wood.py`的补料条件误写为`num_items(Items.Hay) < carrot_hay or True`。正确条件为：

```python
if c == Entities.Carrot and (num_items(Items.Hay) < carrot_hay or num_items(Items.Wood) < carrot_wood):
```

Hay或Wood不够支付胡萝卜种子时才退回Bush。移除排行榜库存终点时，材料判断必须保留。旧报错位置为第86行、第80列`or`；该修复的静态编译记录归`.codex/functional-syntax-20261108/`。修正后的连续产出采样及来源对照见[功能效率记录](../../docs/functional-validation.md)和[实际时间采样数据](../../docs/functional-rate-validation.json)；早先含`or True`的效率数据已经撤回。
