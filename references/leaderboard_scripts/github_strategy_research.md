# GitHub 策略研究

2026-10-28按用户要求搜索公开算法，并以当前合规版本的实际改善作为选择依据。公开排名只作参考，#10不保证常规或可达；不以排名或固定提速百分比否决候选。作者自述时间、本地预测、短时实机与官方完整统计分别保存。

## 已取得的结果

本轮优先采用[zzlg-git的多小迷宫方案](https://github.com/zzlg-git/TheFarmerWasReplaced_Maze_1min28s/tree/e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629)。当前迷宫从一座大迷宫、多机分区响应，改为32座独立小迷宫；每机拥有自己的地图和路由表，连续兑现自己的宝藏。整理入口后的官方完整统计为**83轮87.673855秒**，比旧版127.169105秒缩短39.495250秒、31.0573%。源码、三类时间及正确性边界见[迷宫记录](lb_maze.md)。这项算法来自上游，本仓库本轮完成审阅、入口适配、完整计费和实机复核。

此前研究过度限定为“一座大迷宫的分区与驻点”，没有完整比较多座独立迷宫的产出。固定#10门槛又把研究注意力放在能否追平参考成绩。后续先比较任务数量、任务规模、独立执行与协作的费用，再选路径或局部实现；这不是每次穷举全部组合，而是检查是否遗漏了改变主路径的低成本选项。

## 本轮来源与取舍

| 来源 | 固定版本 / 实际阅读范围 | 结论 |
| --- | --- | --- |
| [zzlg-git/TheFarmerWasReplaced_Maze_1min28s](https://github.com/zzlg-git/TheFarmerWasReplaced_Maze_1min28s) | commit `e5d5e2d9c8df5c22fee0c1c591d70bd69d4a6629`；完整`V7TheRecord.py`和`readme.md` | 20座5×5、6座6×6、6座7×7；DFS一次建图，出发点探墙，增量更新全点对最短路。完整实机已验证收益，已适配为当前迷宫脚本。树中只有这两文件，未附许可证；保留作者与来源，本轮仅本地使用，未push或对外发布源码。 |
| [michaelvdnest/the-farmer-was-replaced-leaderboard](https://github.com/michaelvdnest/the-farmer-was-replaced-leaderboard) | commit `ea4ca99cb0e357ad5cbc2e4e3240e346d9342e4e`；`FarmCactus.py`、README与LICENSE已取得 | 所读仙人掌入口串行铺田，再逐列/逐行调用`bubble_sort`，依赖`utils`。尚未读齐依赖，无更快的证据，未执行。README没有可直接比较的完整时间。 |
| [enihsyou/The-Farmer-Was-Replaced](https://github.com/enihsyou/The-Farmer-Was-Replaced) | 固定树`37a97b58e15dc60bb6aff8829eeb58293be18b39`及响应中的blob ID；已完整读`cactus_single.py`，另取得`maze.py` | 单机仙人掌沿反对角线逐株插入，向West/South推送较小值，与已有Young tableau研究有重合。末段依赖肥料与固定成熟时间，不能直接当作当前资源场景下的可靠改善。未执行；多机文件、README和许可证请求未取得内容。 |
| [xw1225/The-Farmer-Was-Replaced-Ultimate-Solution](https://github.com/xw1225/The-Farmer-Was-Replaced-Ultimate-Solution) | 仅搜索结果元数据；源码请求超时 | 描述声称覆盖16榜，但未读源码，不评价算法或速度，留待后续有界查阅。 |

通过GitHub公开API进行仓库检索，不需要账号；本轮部分请求超时，raw域名多次TLS EOF，随后用固定blob API取得了迷宫全文。搜索范围有限，不能声称已找到GitHub最快实现。原始搜索响应、仓库树、上游原文、哈希及运行报告保存在`.codex/leaderboard-astra/github-strategy-search/`；上游原文没有被入口适配覆盖。

## 接续选择

迷宫这一结构已兑现，下一优先项是仙人掌的完整排序与工人安排。继续查阅可取得的多机实现，并与已有局部交换、行列排序和对角线插入证据去重。只有在同一份可执行方案中计入取样、规划、交换、移动、同步及成熟费用后，才判断是否优于36.576868秒的当前完整实机基线。不能把某算法的低交换数和另一个算法的低规划成本相拼接。

小迷宫仍可研究初始全点对表的对称构建、末代按需建表与布局，但这些尚无本仓库收益证据，不先做参数扫描。当前任务优先级随可实现的收益、成功把握和验证成本重新比较。
