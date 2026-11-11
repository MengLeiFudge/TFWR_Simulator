# Python模拟器历史资料

旧Python模拟执行器已移除，不再提供 `python -m simulator.local_simulator` 入口或 `run_script` 等库接口。游戏脚本统一使用[C#模拟器](../headless/README.md)，当前语法关口见[C#游戏语言检查](../headless/syntax-validation.md)。

本目录仅保留历史机制研究、对照记录和原版资源快照，以维持已有报告的来源链及文档链接。文中的Python类名、旧命令、模型版本和“当前”描述对应各记录形成时的状态，不代表仍可执行，也不自动变成C#验收结论。

- [历史API覆盖](api-coverage.md)、[验收记录](validation.md)、[作物机制](mechanisms.md)。
- [地下对照](underground-validation.md)、[旧版更新影响](game-update-26385848.md)、[四榜残差](four-residual-alignment.md)。
- [旧语法修复](syntax-validation.md)、[运算对照](operator-validation.json)、[扫雷定时器对照](sweeper-timer-alignment.json)。
- `resources.json`、`underground_resources.json`是历史资源来源快照；C#执行实际读取 `headless/data/assets.json`。

已移除21个Python执行/解析/世界模型模块、旧噪声运行表和字节码缓存。旧源码可从移除前的Git版本 `1d04389` 查询，例如 `git show 1d04389:simulator/local_simulator/runner.py`。冻结的历史JSON中保留原路径和哈希，不把来源记录改写成C#源码。

`headless/import_native.py`、`export_assets.py`和`verify.py`仍是开发工具，分别生成C#源码、导出原版资源和调用C#重放归档；它们不包含Python农场模拟执行器。游戏控制工具也保持独立。
