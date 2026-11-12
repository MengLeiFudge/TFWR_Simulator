# 排行榜脚本

本目录保存 `lb_*.py` 可执行策略，按 `lb_榜单名.py` 命名。单无人机榜通常使用 `_single` 后缀。脚本针对对应榜单的初始条件和成功目标，不承诺适用于普通存档的各科技阶段。

本目录只保留当前确认最快的实现。完整轮时间写在顶部，尚无完整实测时明确标注；结构见[共用方法](../../docs/leaderboards/README.md#lb_py-注释边界)。策略文档位于[docs/leaderboards](../../docs/leaderboards/README.md)同名`.md`，固定“当前策略与成绩 / 淘汰与未采用方案 / 历史正式版本演进 / 下一步优化方向”四节。

旧正式版和验证淘汰的候选统一归[references/leaderboard_history](../../references/leaderboard_history/)下对应`<lb_xxx>/`，按日期、版本／方向及有效成绩命名；[manifest.json](../../references/leaderboard_history/manifest.json)提供原`.codex`路径和Git提交映射。淘汰表注明表现、失败原因并链接代码，原始回执留`.codex/`，不新增阶段过程文档。归档不参与类型检查或存档同步。

[lb_start.py](lb_start.py) 是仓库内的历史成绩索引。部署时，`game_control/tools/sync_leaderboard_scripts.py` 从指定的目标脚本生成存档内的 `lb_start.py`，两者职责不同。默认只同步目标脚本与派生入口，部署方法见 [游戏控制](../../game_control/README.md)。

外部代码的来源、commit和适用规则记录在对应策略文档中；[enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)与恐龙来源的[lywlucas_LICENSE.txt](lywlucas_LICENSE.txt)随相关脚本保留。

全科技下持续生产资源的普通脚本见 [功能脚本约定](../functional/README.md)。它们优先迁入成熟功能或多机榜算法，遵守[本地效率与替换准入](../../docs/script-validation.md)。
