# 游戏更新对齐：Steam build 26385848

本次核对以已安装游戏的 `Core.dll`、`Utils.dll` 和静态资产为依据。Python模拟器按下列源码规则迁移后，已完成16榜的同seed完整策略对照，结果和残余误差见[新版配对复验](../../references/leaderboard_scripts/game-update-validation.md)。对照定位并修正了集合枚举、成本字典顺序和函数返回静态标记。木头/胡萝卜多机现与游戏显示值分别相差约0.002/0.0002秒；16榜最大时间残差约0.653秒，部分状态仍不一致，不能宣称全模型完全对齐。旧版通过记录保留在[验收历史](validation.md)。

## 对打榜的影响

| 机制 | 新版规则及策略影响 | 本地实现 |
| --- | --- | --- |
| 向日葵错收 | 按收割瞬间全田株数和最高瓣数判断资格。上次向日葵收割不合格时，本次即使合格也只有基础收益；本次合格会清除标记。未成熟铲除也更新标记。普通作物收割、clear和缩扩图不清除此标记。独立区域、乱序收割和丢弃慢花策略需要重新比较完整产量。 | `FarmWorld.harvest` 保存全田错收标记，按最终有效倍率分配Power和感染产物；快照包含标记。 |
| 邻树移除 | `Tree.OnFree` 会立即刷新四邻生长计时。密植树、伴生支撑轮换和Reset的树木阶段可能更快。 | `FarmWorld.remove/update_neighbors` 在实体离开棋盘后重新安排邻树成熟事件。 |
| Power耗尽 | 每次0.2秒扣款后都重新检查最高速度；库存恰好等于本次扣款也必须减速。影响所有会耗尽Power的榜单及Reset阶段。 | `FarmWorld.settle_power` 在扣款后统一限速。 |
| 迷宫迁移 | 迁移中 `can_harvest()` 为False；`harvest()` 仍返回True并计200t，但不给金币，也不删除迷宫。第二次再利用失败仍计200t。迁移完成前检查源宝藏和目标树篱仍属于同一迷宫。 | `FarmWorld.harvest/api_can_harvest` 和 `Maze.relocate` 加入迁移状态与归属检查。合规策略不能把重复收奖算入收益。 |
| 恐龙苹果 | 新版从同层连通区域按深度优先顺序得到空格列表，再随机抽索引；排除头、恐龙和苹果，选取新目标时另排除新苹果自身。旧版按x/y重抽的同seed轨迹已经失效。 | `Dinosaur.free_cells/choose_target/move` 使用移动前的候选快照；C#的 `lb-current-game` 动作代理同步采用此规则。 |
| 恐龙末果与清理 | 苹果预选格被恐龙占据且棋盘只有一格空地时，measure返回那格空地。换帽只清除仍是原苹果对象的实体，保留其他无人机的替代作物。 | `Dinosaur.measure_apple/finish`；C#动作代理同步处理末果观测。 |
| 邻格查询 | `get_entity_type(direction=None)`、`get_ground_type(direction=None)` 都计1t；方向查询始终环绕，不受墙和恐龙帽移动限制。可减少策略中的专门移动，但不会免费获取全图。 | 两个 `FarmWorld` API接受可选方向并沿用方向校验。 |
| 限制地图后升级Expand | 升级清除地图大小限制，并按科技等级重新生成农田。`set_world_size` 的整数参数不等于当前边长时重置全部无人机；需要生成地图时，即使实际尺寸不变也重新生成。 | `api_unlock/api_set_world_size` 与原有调度器的位置重置配合。重新生成地图清空仙人掌数字缓存；普通clear保留缓存。 |
| 初始化和遍历顺序 | 新Farm构造器最后只应用一次目标Expand等级。初始草地、clear和水分衰减使用按行的Cell数组顺序。相同seed下的伴生、成熟与水分轨迹会变化。 | `FarmWorld.__init__/reset_grid/decay_water` 改为新版顺序。 |
| 结束计时 | 游戏在挑战/模拟脚本结束后停止继续推进时间。本地最后一台无人机结束时也立即停表，不再补到199t批次末尾。所有短组件都可能受影响。 | `Scheduler.run` 在活动无人机清空后结束。旧版长程记录中的末尾误差是否全部由此产生，尚未验证。 |
| 正式榜随机源 | Reset和资源榜的作物随机流改为 `BufferedCryptoRandom`，从系统加密随机源取字节，并混合实例序号与salt；salt相同也不能复现。固定seed的simulate仍用Mono兼容随机流。 | 本地固定seed明确表示 `seeded_simulate`；报告保存游戏版本。预测不能冒充正式榜单的同seed回放。 |

基础游戏12种实体的已有数值参数，以及34项基础科技的上限、父节点、成本序列和成本倍率，与原快照比较没有差异。新增文档符号不改变这些生产参数。资产提取同时发现DLC实体、地面和榜单；本模型仍只覆盖基础平面农田，未实现地下、DLC作物和DLC榜单。

## 已有实现可沿用的语言行为

- `print()` 输出空行并按约1游戏秒计费；`quick_print()` 输出空行并计0t。本地原有变长参数输出已支持。
- 独立表达式和字符串说明语句由现有AST路径执行，表达式内部的运算仍正常计费。
- 长度为n的列表执行 `a += a` 时追加原来的n项，只收n个追加tick；现有实现先记修改前长度，再由列表自身扩展，已经符合新版。
- 集合的 `in` / `not in` 使用相同的成员判定，费用按查询元素的递归键大小计算；本地没有继承旧版两条分支不一致的实现。集合枚举现已改用游戏HashSet槽位顺序，避免CPython顺序改变同seed策略路线；实际单机仙人掌对照见配对记录。
- 工厂函数的返回表达式保留静态标记，返回静态局部函数后立即调用分派0t，普通赋值后再调用仍为1t。修正前多层派发累计1～3t偏移，足以改变共享伴生流；修正后request266的279条返回值、tick和纳秒时间全部一致。当前实机范围见配对复验，不泛化为任意高阶组合。
- `dict(d)` 浅复制计 `1 + 2 * len(d)` tick。补丁修正文档，不需要把当前模型改成每项1t。
- 不存在的本地脚本通过文件读取错误指出路径。模拟内部的嵌套 `simulate` / `leaderboard_run` 仍只覆盖拒绝递归的分支。

帽子朝向、个人外观拥有状态、音乐、文档/编辑器界面和保存可靠性不参与本地农田tick预测。官方最长提交时间提示属于真实挑战的提交生命周期，本地预测不生成可提交结果。

## 证据与使用边界

| 来源 | SHA256 |
| --- | --- |
| Core.dll | `27f621ba6e78f9b1db3506af571deceffd4a8d075a5d0aba42a2af230a9f7088` |
| Utils.dll | `d7ada71927581528a1e854f764540d16193c8cd859895deff56c7266bb9136a1` |
| resources.assets | `69530547e96315f230557c12d4133154b3dcdbace2cfe256ac018003a96ec931` |
| 被替代的旧Core.dll | `b8ac8d22b614d9e48d3affa9a4de9c77e799b824ed8f50dc2e494cc2dd9f9082` |

本机原始证据位于 `.codex/leaderboard-sol/game-update/`：`source-manifest.json`、两份完整反编译源码、`assets.current.json` 和 `asset-comparison.json`。资产共解析16实体、38帽子、20物品、30榜单、53科技，解析错误为0。提取使用隔离的UnityPy工具环境，模拟器运行依赖仍只有Python标准库。

关键源码入口是 `Sunflower.Harvest/GetHarvestYield`、`Tree.OnFree`、`Farm.UsePower`、`Treasure.Harvest/CompleteRepositioning`、`DinosaurHat.FindFreeCells/TryChooseTarget/OnMove/RemoveApple`、`Apple.Measure`、`GridManager.GenerateExpandedWorld/GenerateWorld/ClearGrid/WaterDecay`、`Simulation` 构造器和 `BufferedCryptoRandom`。

Save0 `__builtins__.py` 已按用户要求同步为本版官方模板的中文说明，保留全部接口声明。Save1尚未生成提示文件，采用的是游戏生成新存档时读取的同一StreamingAssets模板；来源指纹、备份和部署记录见新版配对复验。模型仍只实现已列出的基础农田机制，提示文件中新增的地下/DLC接口不等于已经模拟。
