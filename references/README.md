# 参考资料

本目录保存来源事实与历史代码。引用时保留版本、来源和获取时间；机制解释、失败原因与采用判断写入[项目文档](../docs/README.md)或所属模块的README。

| 位置 | 内容 |
| --- | --- |
| `DecompiledSource/` | 游戏反编译源码及`source-manifest.json`来源清单 |
| [unlocks/](unlocks/README.md) | 科技前置、费用和解锁事实快照 |
| [achievements/steam-schinese.json](achievements/steam-schinese.json) | Steam官方中文成就名称、说明、API ID和来源时间；逐项入口映射归[成就目录](../scripts/achievement/README.md#完整成就映射) |
| [leaderboards/leaderboard_cache.json](leaderboards/leaderboard_cache.json) | 公开榜单、抓取时间、账号最高记录与查询状态 |
| [leaderboards/status_snapshot.md](leaderboards/status_snapshot.md) | 30榜公开#1／#3／#10或末名、人数、账号最高及排名，逐榜保留来源和查询时间 |
| [leaderboard_history/](leaderboard_history/) | 30榜旧正式版本与淘汰候选代码，按`<lb_xxx>/`独立存放，隔离类型检查和存档同步 |
| [leaderboard_history/manifest.json](leaderboard_history/manifest.json) | 各榜版本清单、原`.codex`路径及Git提交到归档代码的映射 |
| [bilibili/strategy_sources_20261112.json](bilibili/strategy_sources_20261112.json) | 视频、评论、文章和恐龙作者固定commit、指纹与许可；采用判断归[B站研究](../docs/leaderboards/bilibili_strategy_research.md) |

排行榜当前实现归[scripts/leaderboard](../scripts/leaderboard/README.md)，每榜策略、淘汰原因、历史成绩及后续方向归[docs/leaderboards](../docs/leaderboards/README.md)。归档文件不是可部署入口；复用前重新读源码、依赖和现行机制，再验证。

旧正式版按日期、版本号、成绩和提交号命名，候选按日期、方向及有效时间命名。档名时间可能只是局部窗口或停止时刻，以对应单榜文档的口径为准。`leaderboards/`仅保留公开缓存与快照，不保存日期实验JSON。原始实验回执留`.codex/`，长期结论写回既有正式文档。

C#模拟所需资源表归`simulator/headless/data/assets.json`；`simulator/local_simulator/`仅保留历史来源快照与对照资料。
