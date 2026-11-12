# 游戏脚本类型检查

仓库根目录的 [ty.toml](../ty.toml) 将本目录加入模块搜索路径。`scripts/functional` 和 `scripts/leaderboard` 的 `from __builtins__ import *` 因此使用 [__builtins__.pyi](__builtins__.pyi)，无需连接真实存档。该文件只供编辑器和静态检查使用。

从仓库根目录执行：

```bash
ty check scripts/functional typings
```

ty LSP使用同一份游戏配置。历史代码库已在`ty.toml`的`src.exclude`显式排除；默认检查和部署都不将归档当当前入口。诊断关注错误和警告，可选返回近似及未用变量仍可能有提示；静态检查不替代原版语法、本地模拟或实机。

普通Python控制工具不使用游戏内置声明。根目录的游戏桩会把`str`等当函数而影响宿主注解检查；需要核对`game_control`时，使用不带游戏桩的独立CPython工作区检查同源包副本，核对副本与实际源码逐字节一致，再报告LSP结果。不要修改宿主类型来迎合游戏声明。

## 声明来源与维护

声明从游戏提供的类型模板提取，保留函数签名、泛型、枚举和贡献者信息，省略说明字符串与函数体；来源SHA256写在文件头。地下帽子、排行榜和科技按[资源快照](../simulator/local_simulator/underground_resources.json)并核对`Core.decompiled.cs`补齐，当前语言与导入边界见[原版语法检查](../simulator/headless/syntax-validation.md)。

枚举与游戏冲突时先核资源注册表和实机，再同步声明及来源指纹。Windows挂载盘按[完整性要求](../docs/wsl-file-read.md#完整性要求)核对全部字节；彩色块声明校正与截断拦截见[既有证据](../docs/wsl-file-read.md#本次证据)。

游戏更新后，先读取新的真实 `__builtins__.py`，核对函数声明和资源枚举，再更新本地声明及来源指纹。新增API必须由游戏注册表与资源证据支持；反编译中未注册的方法不能作为可用接口。不要修改真实存档的类型文件来满足检查器。

## 游戏语言的静态边界

- `measure()` 保留整数、整数坐标和字符串的联合类型。检查器无法根据当前农田状态收窄结果时，只在已核实实体或地面的调用位置使用带错误码的 `ty: ignore`，并说明状态前提。更换该位置的实体、地面或返回值用途时，必须重新核对前提与抑制范围。
- 游戏的 `global` 沿父作用域寻找绑定。配置只在两个游戏脚本目录关闭Python模块绑定的 `unresolved-global` 告警；未定义名称、未知属性和参数类型等检查保持启用。
- 沿用模板对部分可选返回省略 `None` 的近似，包括 `measure`、`get_companion`、`spawn_drone`、实体查询和部分勘探接口。它们在游戏中仍可能返回 `None`，不能依据编辑器的不可达提示删除失败处理。
- `.pyi` 中的现代Python类型语法只由检查器读取。游戏脚本继续遵守游戏语言规则，不为类型检查添加运行时 `typing` 导入、断言或转换调用。
