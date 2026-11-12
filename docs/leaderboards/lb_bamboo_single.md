# 竹子·单机（`lb_bamboo_single`）

## 当前策略与成绩

当前脚本：[lb_bamboo_single.py](../../scripts/leaderboard/lb_bamboo_single.py)。公开账号最高 **4:28.226（#16）**；已有最好本地模拟 **4:25.464**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/21444624/)，榜单抓取时间 `2026-11-11T09:13:17.340204+00:00`，账号查询时间 `2026-11-11T09:13:17.340235+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

8×8留一空列，共56株；公开筛出5/9两花节后保桩，整片按4→8→1反复切收。1.5秒趟间隔由实际巡回时间抵扣，选种/高度1按0.7阈值补最多四桶水，4/8阶段不浇水。第三节不限，按25M实际库存结束。

合法append初始化版三seed完整均265.46358402秒；2026-11-09 request469正式27轮268.225444444秒，显示268.226秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 逐株切花与整株重种 | 历史正式956.579秒，初版1095.017秒 | 重复升降与筛种成本，统一花节和树桩复用才取得结构收益 | [旧版合集](../../references/leaderboard_history/lb_bamboo_single/)（多方向见版本表） |
| 直接给旧单机入口补水 | 首seed986.668秒，对960.789秒 | 补水及飞行高度恢复开销没有回本，不能套用多机补水收益 | [20261107_rejected_efficiency_bamboo_water.py](../../references/leaderboard_history/lb_bamboo_single/20261107_rejected_efficiency_bamboo_water.py) |
| 三元表达式或列表乘法的统一花节版 | 旧265.463529秒语法放行撤回 | 游戏只支持原版子集，合法分支/append版重新完成原目标 | [20261108_rejected_bamboo_batch_v2.py](../../references/leaderboard_history/lb_bamboo_single/20261108_rejected_bamboo_batch_v2.py) |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 1095.017秒（构建26462009，7轮官方完整统计；请求341）。 | 记录新版竹子单双机正式完整成绩 | [20261106_v01_18m15.017s_6110f76b.py](../../references/leaderboard_history/lb_bamboo_single/20261106_v01_18m15.017s_6110f76b.py) |
| 2026-11-06 | 956.579秒（构建26462009，8轮官方完整统计；请求364）。 | 竹子空中心四邻布局通过单双机完整复验 | [20261106_v02_15m56.579s_6c5c5e64.py](../../references/leaderboard_history/lb_bamboo_single/20261106_v02_15m56.579s_6c5c5e64.py) |
| 2026-11-09 | 未取得（统一花节批量保桩；本地原目标已通过，详见同名文档）。 | 统一竹子花节并批量保桩切收达到榜一两倍内 | [20261109_v03_1455c1aa.py](../../references/leaderboard_history/lb_bamboo_single/20261109_v03_1455c1aa.py) |
| 2026-11-09 | 未取得（统一花节批量保桩；当前版本未实机验证）。 | 按游戏原版解析语法并纠正竹子条件表达式 | [20261109_v04_be0e2c24.py](../../references/leaderboard_history/lb_bamboo_single/20261109_v04_be0e2c24.py) |

## 下一步优化方向

- 比较部分田先生产与分组花节，避免为统一56株付过多筛选；按最终竹子收益而非首趟速度取舍。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
