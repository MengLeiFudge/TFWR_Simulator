# 项目文档

- [项目结构与边界](architecture.md)：模块分工、脚本分类、数据流和命名迁移。
- [游戏脚本验证与替换准入](script-validation.md)：全科技前提、本地效率验证、严格更快才允许覆盖存档。
- [功能脚本效率对照](functional-validation.md)：成熟算法来源、历史实际增长率、固定窗口库存及完整周期。
- [地下功能批次效率](underground-functional-validation.md)：三seed净增长、完整两盘炸药与对应版本的调度边界。
- [铁与石英勘探对照](underground-prospecting.md)：探测返回值、铁的煤引导采矿与石英32机候选结果。
- [地下方向与淘汰记录](leaderboards/underground_efficiency_iteration.md)：14榜的策略筛选、完整目标结果和后续方向。
- [游戏语言静态检查](../simulator/local_simulator/syntax-validation.md)：原版静态规则、错误行列和木材条件修复。
- [排行榜共用方法](leaderboards/README.md)：方向探索、机制淘汰、预算与实机准入。
- [排行榜进度](leaderboards/leaderboard_progress.md)：统一七列——排行榜、#1、#10或末名、账号最高记录及排名、最好模拟时间、距#1的比例与改进方向；单次完整统计另保留历史归属。
- [公开成绩比较](leaderboards/leaderboard_targets.md)：从缓存生成的成绩报告，时效以报告中的抓取时间为准。

各榜长期结论归 `leaderboards/lb_*.md`。模拟器的接口与精度记录就近保存在 [simulator](../simulator/README.md)；模组与控制工具的使用说明各自保存。`.codex/drafts/` 只记录进行中工作，已确定的规则和可复用方法应归入对应正式文档，再从草稿引用。
