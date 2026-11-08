# 游戏脚本类型检查

仓库根目录的 [ty.toml](../ty.toml) 将本目录加入模块搜索路径。`scripts/functional` 和 `scripts/leaderboard` 的 `from __builtins__ import *` 因此使用 [__builtins__.pyi](__builtins__.pyi)，无需连接真实存档。该文件只供编辑器和静态检查使用。

从仓库根目录执行：

```bash
ty check scripts/functional typings
```

ty LSP 使用同一份配置。诊断关注错误和警告；模板省略的可选返回值与未用变量仍可能产生提示。静态类型检查不替代游戏语言编译、本地模拟或实机验证。

## 声明来源与维护

声明从游戏提供的类型模板提取，保留函数签名、泛型、枚举和贡献者信息，省略说明字符串与函数体。来源SHA256写在文件头；中文模板的来源记录见[游戏更新验证](../docs/leaderboards/game-update-validation.md#api提示同步)。地下新增帽子、排行榜和科技按 [underground_resources.json](../simulator/local_simulator/underground_resources.json) 补齐，爆破钻头及地下排行榜同时核对了 `Core.decompiled.cs`。

游戏更新后，先读取新的真实 `__builtins__.py`，核对函数声明和资源枚举，再更新本地声明及来源指纹。新增API必须由游戏注册表与资源证据支持；反编译中未注册的方法不能作为可用接口。不要修改真实存档的类型文件来满足检查器。

## 游戏语言的静态边界

- `measure()` 保留整数、整数坐标和字符串的联合类型。检查器无法根据当前农田状态收窄结果时，只在已核实实体或地面的调用位置使用带错误码的 `ty: ignore`，并说明状态前提。更换该位置的实体、地面或返回值用途时，必须重新核对前提与抑制范围。
- 游戏的 `global` 沿父作用域寻找绑定。配置只在两个游戏脚本目录关闭Python模块绑定的 `unresolved-global` 告警；未定义名称、未知属性和参数类型等检查保持启用。
- 沿用模板对部分可选返回省略 `None` 的近似，包括 `measure`、`get_companion`、`spawn_drone`、实体查询和部分勘探接口。它们在游戏中仍可能返回 `None`，不能依据编辑器的不可达提示删除失败处理。
- `.pyi` 中的现代Python类型语法只由检查器读取。游戏脚本继续遵守游戏语言规则，不为类型检查添加运行时 `typing` 导入、断言或转换调用。
