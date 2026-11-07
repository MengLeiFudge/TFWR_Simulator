# 项目文档

- [项目结构与边界](architecture.md)：模块分工、脚本分类、数据流和命名迁移。
- [游戏脚本验证与替换准入](script-validation.md)：全科技前提、本地效率验证、严格更快才允许覆盖存档。
- [功能脚本效率对照](functional-validation.md)：成熟算法来源、实际增长率、固定窗口库存及完整周期。
- [游戏语言静态检查](../simulator/local_simulator/syntax-validation.md)：原版静态规则、错误行列和木材条件修复。
- [排行榜共用方法](leaderboards/README.md)：方向探索、机制淘汰、预算与实机准入。
- [排行榜进度](leaderboards/leaderboard_progress.md)：各榜的预测、短时实机和完整打榜记录。
- [公开成绩比较](leaderboards/leaderboard_targets.md)：从缓存生成的成绩报告，时效以报告中的抓取时间为准。

各榜长期结论归 `leaderboards/lb_*.md`。模拟器的接口与精度记录就近保存在 [simulator](../simulator/README.md)；模组与控制工具的使用说明各自保存。`.codex/drafts/` 只记录进行中工作，已确定的规则和可复用方法应归入对应正式文档，再从草稿引用。
