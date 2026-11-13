# 项目文档

`docs/`根目录仅保留以下六份核心文档。新增结论先更新所属文档，不新增日期、阶段或单次验证报告。

| 文档 | 内容 |
| --- | --- |
| [README.md](README.md) | 阅读入口与文档归属 |
| [architecture.md](architecture.md) | 模块职责、脚本分类、数据流和目录边界 |
| [script-validation.md](script-validation.md) | 游戏语法、本地正确性与效率、存档替换要求 |
| [script-rate-validation.md](script-rate-validation.md) | 功能算法、速率口径、已采用／未采用结论及成就条件 |
| [block-mining.md](block-mining.md) | 深钻、爆破掉落、建材窗口和铁／石英勘探机制 |
| [wsl-file-read.md](wsl-file-read.md) | Windows挂载盘短读、64KB边界和整文件完整性检查 |

[leaderboards/](leaderboards/README.md)保存30份单榜四节文档、三阶段计划、解释器费用、GitHub／B站来源研究，以及进度MD／研究JSON。状态统一为七列：排行榜、实机、模拟、#1、#3、#10、改进方向；各公开名次时间后附实机与模拟较快值相对该名次的差距百分比。当前总表见[排行榜进度](leaderboards/leaderboard_progress.md)，来源日期及账号查询状态见[公开快照](../references/leaderboards/status_snapshot.md)。

当前实现归[scripts/leaderboard](../scripts/leaderboard/README.md)，历史和淘汰代码归[references/leaderboard_history](../references/leaderboard_history/)，每榜文档记录原因并链接源码；`manifest.json`提供原实验路径及Git提交映射。公开缓存目录只保存缓存JSON与快照MD。

运行说明就近归[功能脚本](../scripts/functional/README.md)、[成就脚本](../scripts/achievement/README.md)、[模拟器](../simulator/README.md)、[游戏控制](../game_control/README.md)和[模组](../game_mod/README.md)。原始日志、冻结报告与进行中草稿留`.codex/`；正式文档保留可复用结论和核心数值，不依赖临时文件才能理解。
