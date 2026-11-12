# 向日葵·多机（`lb_sunflowers`）

## 当前策略与成绩

当前脚本：[lb_sunflowers.py](../../scripts/leaderboard/lb_sunflowers.py)。公开账号最高 **3:25.817（#8）**；已有最好本地模拟 **3:27.419**。

公开数据取自[该榜Steam页面](https://steamcommunity.com/stats/2060160/leaderboards/17869894/)，榜单抓取时间 `2026-11-10T06:15:47.701441+00:00`，账号查询时间 `2026-11-10T06:15:47.701469+00:00`。#1、#3、#10及差距见[进度总表](leaderboard_progress.md)；各榜来源时间见[公开快照](../../references/leaderboards/status_snapshot.md)。

32机组成16个双机Hilbert区域，每组62花与两个草标记。按15→7瓣全局同步收割，组内比较正反花序及两机顺序后切段平衡路程，同瓣闭环在最大间隔处断开。用本次Hay增量与真实Pumpkin种子消费作为屏障；未成熟花有库存时单次施肥并重新确认成熟。第14波按净Power达标广播退出，全体回收。

当前相对库存同步版seed1完整207.418751969秒；request319短筛两轮205.300500秒，2026-11-06 request320正式35轮205.816485714秒。公开毫秒记录为205.817秒。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 绝对Hay库存阈值屏障 | 普通已有库存可提前放行并使慢机永远等待 | clear保留库存，固定满科技产量/种子费不能作为任意场景常量；现源按起点增量核算 | [旧版合集](../../references/leaderboard_history/lb_sunflowers/)（多方向见版本表） |
| 全场逐花贪心/四机DP切段 | 全场规划约28.00秒；四机最慢组规划2.476秒 | 免费几何有收益，在线计算未回本；两机单切点才可实际采用 | [20261026_rejected_cut_planner_planner.py](../../references/leaderboard_history/lb_sunflowers/20261026_rejected_cut_planner_planner.py) |
| 16×16小田固定消费屏障 | 六批43.671837秒，净9207.484 Power，210.83/s | 信号、成熟和低密度收益限制吞吐；组件不是10万目标成绩 | [20261029_rejected_small_field.py](../../references/leaderboard_history/lb_sunflowers/20261029_rejected_small_field.py) |
| 32步闭合播种、固定方向模板 | 完整209.199998/209.296789秒，父约208.669秒 | 少移动仍多付重建桶序/管理及后续等待 | [20261029_rejected_seed_cycle.py](../../references/leaderboard_history/lb_sunflowers/20261029_rejected_seed_cycle.py) |
| 三带流水、不断重种 | 组件2731花中2423次仅1倍，净4060.410 Power | 跨代高瓣抬高全局最大值，低档收获失去8倍 | [20261030_rejected_pipeline.py](../../references/leaderboard_history/lb_sunflowers/20261030_rejected_pipeline.py) |
| 冷启动切换、16秒统一截止 | 六批净426.09/422.39 Power/s，父429.73/s | 丢花和等待策略未改善真实净产出 | [20261030_rejected_cutoff_rescue.py](../../references/leaderboard_history/lb_sunflowers/20261030_rejected_cutoff_rescue.py) |
| 只救最高两档水分 | 冻结路径后两批至多省0.924/0.613秒 | 低档干花接过等待尾部，不是整批等待消失 | [归档入口](../../references/leaderboard_history/lb_sunflowers/)（原记录未标独立源） |

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-04-18 | 未记录 | 导入 TFWR_Simulator | [20260418_v01_5bf0cea6.py](../../references/leaderboard_history/lb_sunflowers/20260418_v01_5bf0cea6.py) |
| 2026-04-22 | 未记录 | 初步更新部分打榜脚本 | [20260422_v02_aa7209f3.py](../../references/leaderboard_history/lb_sunflowers/20260422_v02_aa7209f3.py) |
| 2026-04-24 | 未记录 | 杂项：整理打榜策略脚本与迭代规则 | [20260424_v03_8deede45.py](../../references/leaderboard_history/lb_sunflowers/20260424_v03_8deede45.py) |
| 2026-04-24 | 未记录 | 提升向日葵打榜吞吐 | [20260424_v04_5bd6de97.py](../../references/leaderboard_history/lb_sunflowers/20260424_v04_5bd6de97.py) |
| 2026-05-31 | 版本注记 3m57.101s | 调整：收敛 leaderboard 脚本真源 | [20260531_v05_3m57.101s_0224fb21.py](../../references/leaderboard_history/lb_sunflowers/20260531_v05_3m57.101s_0224fb21.py) |
| 2026-10-29 | 3:46.886（2026-10-28，官方完整32轮，request 191）。 | 向日葵两机切段完整生产提升实机成绩 | [20261029_v06_3m46.886s_5614d749.py](../../references/leaderboard_history/lb_sunflowers/20261029_v06_3m46.886s_5614d749.py) |
| 2026-10-29 | 3:43.460（2026-10-28，官方完整33轮，request 194）。 | 向日葵使用局部距离表降低规划费用 | [20261029_v07_3m43.460s_cae04bc7.py](../../references/leaderboard_history/lb_sunflowers/20261029_v07_3m43.460s_cae04bc7.py) |
| 2026-10-29 | 3:35.906（2026-10-28，官方完整34轮，request 197）。 | 向日葵比较两机顺序减少收割移动 | [20261029_v08_3m35.906s_abd698ae.py](../../references/leaderboard_history/lb_sunflowers/20261029_v08_3m35.906s_abd698ae.py) |
| 2026-10-29 | 3:32.883（2026-10-28，官方完整34轮，request 200）。 | 向日葵比较正反花序四种切段 | [20261029_v09_3m32.883s_2a694954.py](../../references/leaderboard_history/lb_sunflowers/20261029_v09_3m32.883s_2a694954.py) |
| 2026-10-29 | 3:29.487（2026-10-28，官方完整35轮，request 203）。 | 向日葵达到目标后统一结束最后一波 | [20261029_v10_3m29.487s_67f96e26.py](../../references/leaderboard_history/lb_sunflowers/20261029_v10_3m29.487s_67f96e26.py) |
| 2026-10-30 | 3:27.825（2026-10-30，官方完整35轮，request219）。 | 向日葵最大间隔收割完成207.825秒打榜 | [20261030_v11_3m27.825s_d879be17.py](../../references/leaderboard_history/lb_sunflowers/20261030_v11_3m27.825s_d879be17.py) |
| 2026-11-03 | 3:26.089（2026-11-03，build26385848，官方完整35轮，request267）。 | 采用新版实测更快的向日葵施肥实现 | [20261103_v12_3m26.089s_55f9f221.py](../../references/leaderboard_history/lb_sunflowers/20261103_v12_3m26.089s_55f9f221.py) |

## 下一步优化方向

- 比较每档最慢区负载、播种与成熟重叠及少档筛花的完整费用；供水仍积累时不能把前三波当长期上限。

新方向按[共用策略选择流程](README.md#策略选择与淘汰)记录机制、预算、置信度和停止条件；新结果写回本页及研究状态JSON。
