# 参考资料

本目录保存可追溯的来源事实。引用时保留游戏版本、来源和获取时间；策略解释与验证结论写入 [docs](../docs/README.md) 或所属模块的文档。

| 位置 | 内容 |
| --- | --- |
| `DecompiledSource/` | 游戏反编译源码及 `source-manifest.json` 来源清单 |
| [unlocks/](unlocks/README.md) | 科技前置、成本和解锁事实快照 |
| [achievements/steam-schinese.json](achievements/steam-schinese.json) | Steam官方简体中文成就名、说明、API ID及来源时间；入口筛选归docs/achievement-audit.json |
| [leaderboards/leaderboard_cache.json](leaderboards/leaderboard_cache.json) | 公开排行榜来源、抓取时间和成绩缓存 |
| [leaderboards/status_snapshot.md](leaderboards/status_snapshot.md) | 七列状态总表所用的30榜公开#1、#10或末名、人数及当前账号最高记录和排名，逐榜保留查询时间 |
| [bilibili/strategy_sources_20261112.json](bilibili/strategy_sources_20261112.json) | B站视频、评论和文章的公开来源，以及恐龙作者固定commit、文件指纹和许可；取舍归[策略筛选](../docs/leaderboards/bilibili_strategy_research.md) |

排行榜可执行脚本位于 [scripts/leaderboard](../scripts/leaderboard/README.md)，策略记录和生成的成绩比较报告位于 [docs/leaderboards](../docs/leaderboards/README.md)。C#模拟器执行所需的资源表位于 `simulator/headless/data/assets.json`；`simulator/local_simulator/`只保留历史来源快照和对照资料。
