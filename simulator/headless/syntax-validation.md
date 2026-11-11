# C#入口的游戏语言检查

游戏脚本按原版Tokenizer、Parser和AST静态规则检查；CPython可以运行不代表游戏允许。C#模拟器在创建世界前检查入口及全部静态导入，包括未执行分支内的导入。缺失模块或非法语法都会停止运行，不生成有效效率结论。

在仓库根目录构建后，可单独检查：

```bash
dotnet simulator/headless/bin/Release/net10.0/TFWRSimulator.dll scripts/functional/resources.py --syntax-only
```

WSL使用Windows `dotnet.exe`。正常模拟也自动执行这一步，无须重复运行。成功报告为 `stop_reason=syntax_valid`，包含依赖源码哈希。失败时退出码非零，`error`包含模块路径、行列及原版错误键，例如 `error_expected_close_token`。这只证明源语法通过，正确性、材料、目标和效率仍须执行模拟验证。

## 调用参数规则

函数定义允许普通默认参数；调用只用位置参数，不使用关键字参数、`*args`或`**mapping`。要跳过中间参数，显式传入默认值：

```python
def mine(item, kind, depth, unlock=None, target=-1):
    pass

mine(Items.Block, None, 16, None, target)
```

条件参数写成普通分支，不用 `value if condition else other`。

## 源语言边界

| 类别 | 约束 |
| --- | --- |
| 分支与循环 | 使用换行缩进的if/elif/else、for、while；不用三元表达式、推导式或循环else |
| 容器 | 支持普通list/tuple/dict/set、索引及切片；切片不能作赋值目标 |
| 导入 | 使用同目录模块名及普通import/from，不用as；内置模块由游戏运行时提供 |
| 作用域 | 每条global声明一个名称，且在同作用域首次赋值之前声明 |
| 运算 | 使用原版算术、比较、in/not in及and/or/not；不用is、位运算、链式赋值或**= |
| 数字和字符串 | 不用科学计数、数字分隔符、十六进制、f-string、三引号或隐式字符串拼接 |
| 其他结构 | 不用类、装饰器、lambda、生成器、异常处理、上下文管理器或异步语法 |

原版还检查常量赋值、无意义or表达式、直接把游戏常量作条件，以及把物品/实体/科技常量当作数量比较。具体边界由 `Native/Language.cs` 中Parser和各Node的 `CheckForNonsensicalCode` 决定，不额外套用Python语法白名单。

语法通过不代表运行时类型正确。例如原版乘法不支持 `[value] * count`，列表初始化应使用循环和append。历史三元表达式、关键字调用、列表乘法漏检及实机证据见[旧后端语法对照记录](../local_simulator/syntax-validation.md)。

实现入口为 `HeadlessHost.cs` 的 `Workspace.Load`、`CodeWindow.Parse`。脚本或依赖发生变化后须重新模拟，旧源码的效率报告不能继续放行。
