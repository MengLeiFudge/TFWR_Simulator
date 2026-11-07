# 排行榜脚本

本目录保存 `lb_*.py` 可执行策略，按 `lb_榜单名.py` 命名。单无人机榜通常使用 `_single` 后缀。脚本针对对应榜单的初始条件和成功目标，不承诺适用于普通存档的各科技阶段。

每个榜单的策略、候选、历史成绩和验证证据保存到 [docs/leaderboards](../../docs/leaderboards/README.md) 下的同名 `.md`。实现只保留当前确认最快的版本；完整轮时间写在脚本顶部，尚无完整实测时明确标注。具体结构与研究流程见共用文档。

[lb_start.py](lb_start.py) 是仓库内的历史成绩索引。部署时，`game_control/tools/sync_leaderboard_scripts.py` 从指定的目标脚本生成存档内的 `lb_start.py`，两者职责不同。默认只同步目标脚本与派生入口，部署方法见 [游戏控制](../../game_control/README.md)。

外部代码的来源、commit 和适用规则记录在对应策略文档中；`enihsyou_LICENSE.txt` 随相关脚本保留。

持续生产、适配科技进度的普通脚本见 [功能脚本约定](../functional/README.md)。
