# 排行榜脚本

本目录保存 `lb_*.py` 可执行策略，按 `lb_榜单名.py` 命名。单无人机榜通常使用 `_single` 后缀。脚本针对对应榜单的初始条件和成功目标，不承诺适用于普通存档的各科技阶段。

本目录每榜只保留当前确认最快的可执行实现。未接入固定生成的脚本直接在此维护；已接入者人工修改`scripts/templates/leaderboard/lb_xxx.py`母版及`simulator/optimizer/`规则，母版旁同名`*.codegen.json`保存选中参数和指纹，本目录产物只由工具重建。母版、规则、当前配方和最好产物一起入Git，临时变体留`.codex/`，目录按实际接入创建。完整步骤归[母版与固定代码生成](../../docs/leaderboards/interpreter_cost_notes.md#母版与固定代码生成)。

完整轮时间写在执行版顶部，尚无完整实测时明确标注，生成物第3行起按[固定溯源头](../../docs/leaderboards/interpreter_cost_notes.md#文件存放与人工修改)标明母版、配方及修改提示；结构见[共用方法](../../docs/leaderboards/README.md#lb_py-注释边界)。策略文档位于[docs/leaderboards](../../docs/leaderboards/README.md)同名`.md`，固定“当前策略与成绩 / 淘汰与未采用方案 / 历史正式版本演进 / 下一步优化方向”四节。

旧正式版及有价值且无法重建的淘汰候选归[references/leaderboard_history](../../references/leaderboard_history/)下对应`<lb_xxx>/`，按日期、版本／方向及有效成绩命名；[manifest.json](../../references/leaderboard_history/manifest.json)提供原`.codex`路径和Git提交映射。可从母版／转换器Git版本及参数重建的临时变体不重复归档展开代码。淘汰表注明表现、失败原因及归档链接或重建依据，原始回执留`.codex/`，不新增阶段过程文档。归档不参与类型检查或存档同步。

[lb_start.py](lb_start.py) 是仓库内的历史成绩索引。部署时，`game_control/tools/sync_leaderboard_scripts.py` 从指定的目标脚本生成存档内的 `lb_start.py`，两者职责不同。默认只同步目标脚本与派生入口，部署方法见 [游戏控制](../../game_control/README.md)。

外部代码的来源、commit和适用规则记录在对应策略文档中；[enihsyou_LICENSE.txt](enihsyou_LICENSE.txt)与恐龙来源的[lywlucas_LICENSE.txt](lywlucas_LICENSE.txt)随相关脚本保留。

全科技下持续生产资源的普通脚本见 [功能脚本约定](../functional/README.md)。它们优先迁入成熟功能或多机榜算法，遵守[本地效率与替换准入](../../docs/script-validation.md)。
