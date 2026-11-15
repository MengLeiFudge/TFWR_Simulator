# 固定脚本生成器

`generate.py`把可读母版按显式标记转换为唯一部署版。它只生成代码，不启动游戏或模拟器，不选择算法或自动替换存档。优化流程与文件职责见[解释器费用说明](../../docs/leaderboards/interpreter_cost_notes.md#母版与固定代码生成)。

从仓库根目录生成并核对：

```bash
python3 simulator/optimizer/generate.py scripts/templates/leaderboard/lb_sunflowers_single.codegen.json
python3 simulator/optimizer/generate.py scripts/templates/leaderboard/lb_sunflowers_single.codegen.json --check
```

同名配方保存母版、输出路径、选中转换、生成命令及母版／生成器／产物的SHA256。生成会更新产物和配方指纹；`--check`核对生成命令、三个指纹及逐字节重建结果，不写文件。生成链路径通过根`.gitattributes`固定LF，避免Windows检出改变指纹。修改母版或生成器后重新生成，并按[脚本验证要求](../../docs/script-validation.md)验证新产物；已有报告只覆盖报告中的源码指纹。生成物第3行起注明来源与配方，人工修改母版，随后重建产物。

支持的转换：

| 配方项 | 母版标记 | 转换与限制 |
| --- | --- | --- |
| `unroll: true` | 固定`for`前一行的`#@unroll` | 只展开普通变量遍历整数常量`range`，1～64次；逐次写回循环变量。拒绝本层`break`／`continue`、循环`else`、内部函数／类定义、重绑定`range`及重叠标记；内层循环自己的退出可保留 |
| `wrap_paths: {"size": 8, "stride": 16}` | `#@wrap_paths 8 16`，下一行为`SUN_DISTANCE, SUN_PATHS = sunflower_tables()` | 预生成相对坐标的距离和方向表，替换运行时初始化；母版保留可直接执行的等价建表函数 |
| `unroll: false`或省略转换 | 可保留标记 | 保持策略源码，只添加溯源头；用于展开未改善整轮时间的配方 |

这是受限的源码转换，CPython AST只用于定位转换范围。母版和产物均须经过模拟器的原版游戏Tokenizer／Parser，以及相同初始场景、目标、seed和预算的效率对照。预生成减少初始化时间后，成熟、补水、随机调用和无人机调度仍可能改变，不能把省下的解释器tick直接相加当整轮收益。

当前接入：

- [向日葵单机母版](../../scripts/templates/leaderboard/lb_sunflowers_single.py)与[配方](../../scripts/templates/leaderboard/lb_sunflowers_single.codegen.json)：预生成8格环绕表。原版10k Power完整目标，seed0/1/123，母版280.691307／273.444023／272.665250秒，生成版274.942145／271.259655／270.254543秒；每例15墙钟秒。整轮收益包含时间变化后的实际成熟与生产，不声称三例动作序列完全一致。更早动态距离表示的源码费用与完整对照见[单榜记录](../../docs/leaderboards/lb_sunflowers_single.md)。
- [稻米多机母版](../../scripts/templates/leaderboard/lb_rice.py)与[配方](../../scripts/templates/leaderboard/lb_rice.codegen.json)：保留三个固定循环标记，选中`unroll: false`。2M Rice完整目标三seed均值111.758228秒；相同母版展开为112.073841秒，两个seed退步。稻米单机展开也未改善均值，继续直接维护其执行版。结果与重建规则见[多机](../../docs/leaderboards/lb_rice.md)、[单机](../../docs/leaderboards/lb_rice_single.md)。
