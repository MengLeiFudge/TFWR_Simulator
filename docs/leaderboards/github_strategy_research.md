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
| [enihsyou/The-Farmer-Was-Replaced](https://github.com/enihsyou/The-Farmer-Was-Replaced) | 固定树`37a97b58e15dc60bb6aff8829eeb58293be18b39`及blob ID；已完整读单/多机仙人掌、单/多机胡萝卜、单/多机木头、恐龙、单/多机向日葵、单/多机南瓜、单/多机干草、README和LICENSE | 多机原文固定seed1完整39.799900秒、达标，但慢于36.484325秒基线，未进实机。本仓库取其铺田时预交换的思路，保留已有窗口排序，再独立实现树形派发，组合收益见下文。单机反对角插入补足1秒自然成熟界，核对末三株肥料/治愈与完整64株收益后，正式355轮20.308270秒，较旧版快5.4182%。随后完整阅读`dianosaus.py`、`sunflowers.py`和MIT许可：恐龙适配后官方9轮818.713889秒，比旧版快7.6813%；向日葵的固定Carrot种植屏障没有计入reroll额外消耗，未采用。胡萝卜动态请求适配后单机29轮250.641483秒、多机32轮231.309969秒，分别比旧版快21.1566%和16.4324%；多机补31句柄等待及水库存余量检查。木头单机动态请求适配后23轮321.147652秒，比旧版快4.9774%；开局允许的低倍率树收割已按实际收益计费。多机木头保留跨区请求、计入实际低倍率后，完整26轮277.692385秒，较旧版快2.1847%；强制区域内请求的308.666960秒版本关闭。单机向日葵修正桶记录及肥料后成熟检查后，完整24轮306.3335秒，较旧版快8.0635%，未成熟收割从原文seed1的3株降为最终三seed均0。南瓜多机改为16个双机区域，补空编号检查、资源余量和完整派发回收，正式20轮374.30835秒；单机合并编号早停正式16轮452.9105625秒，分别较旧版快6.7870%和1.4329%。干草固定seed1适配分层派发并回收后112.695298秒，与同批基线相同；单机高水位版175.429651秒，比同批175.156233秒稍慢，均关闭而不进实机；单seed不代表稳定总体差距。 |
| [xw1225/The-Farmer-Was-Replaced-Ultimate-Solution](https://github.com/xw1225/The-Farmer-Was-Replaced-Ultimate-Solution) | 固定树`6398151fad53b9c0af02d304076193a1553c9a58`及blob；已取得100167字节`farm_auto.py` | 按调用链读仙人掌的铺田、行插入、列插入、成熟巡查四阶段；每次交换跟随移动。未发现更低完整费用依据，未运行整文件，未将“覆盖16榜”当作性能证据。其他榜代码与README未完成阅读。 |
| [MartinOpat/The-Farmer-Was-Replaced-Dinosaur-Solution](https://github.com/MartinOpat/The-Farmer-Was-Replaced-Dinosaur-Solution) | 固定树`6754008045a62dcf46f51acd6e33d1f68f341b99`；README、dinosaur.py、queue.py全文 | 蛇形Hamilton环按头尾顺序取水平捷径。内联队列并补失败移动传播后，唯一seed1在100万API上限处已1818.478秒、735个Dinosaur格，尚未完成，关闭；不是完整时间。原树未附许可，未对外发布源码。 |
| [janmagnusdev/the-farmer-was-replaced-programs](https://github.com/janmagnusdev/the-farmer-was-replaced-programs) | 固定树`3b04936e81dc26ccbd515d11a271c06b07fef237`；README、apple_strat.py、apple_utils.py、moving.py、points.py及APPLE_THOUGHTS已读 | 盘尾后向右追苹果，半场后完整蛇形遍历；不可移动时清场后仍继续move，主phase缺少正常退出路径。planting依赖未读，未执行，也没有完整成绩证据。 |

通过GitHub公开API进行仓库检索，不需要账号；本轮部分请求超时，raw域名多次TLS EOF，随后用固定blob API取得了迷宫全文。搜索范围有限，不能声称已找到GitHub最快实现。原始搜索响应、仓库树、上游原文、哈希及运行报告保存在`.codex/leaderboard-astra/github-strategy-search/`；上游原文没有被入口适配覆盖。

## 接续选择

仙人掌已完成一项可兑现的改善：沿本仓库三格窗口排序加入铺田预交换与树形派发，组合完整本地三seed34.348839秒，官方208轮34.7273125秒，比上一正式36.576868秒快5.0566%。原文、两个单项和组合分别计费，未拼接不同算法的低交换数与低规划成本；见[仙人掌记录](lb_cactus.md)。新来源和证据在`.codex/leaderboard-astra/cactus-github-algorithms/`。

旧单机Young插入此前只因15%旧门槛停止，本轮重评发现seed0/123仅收60株、115200 Cactus，未达到目标；补齐末次种植后的1秒成熟界后三seed均达标，但均值21.900098秒慢于同批基线21.658177秒，因此关闭。上游反对角线近点访问与末步免移动是另一实现，完整355轮20.308270秒已迁入；见[单机仙人掌记录](lb_cactus_single.md)。随后小迷宫对称构建取得完整83轮86.968566秒；迁入8×8单机的增量路由取得完整57轮126.703281秒，较单机旧版145.112秒快12.6859%。来源和执行证据分别写入迷宫同名文档。

单机沿途探墙完整seed1为134.296739秒，比出发点版本128.242054秒慢；少114move但多3013次探测，关闭该固定方案。恐龙的边界绕行填隙已获实际收益，见[恐龙记录](lb_dinosaur.md)。胡萝卜动态请求的完整成熟收割均按实际伴生倍率核对，未成熟改种单列；见[多机记录](lb_carrots.md)与[单机记录](lb_carrots_single.md)。木头单机与多机的同类动态请求也已兑现收益，见[木头单机记录](lb_wood_single.md)与[多机记录](lb_wood.md)。多机允许部分低倍率，少重抽的收益超过这部分损失；不能把“全部满倍率”预设为最快结构。单机向日葵的分瓣用水与分桶巡收已完成实机，见[单机向日葵记录](lb_sunflowers_single.md)。南瓜的双机队列修补与单机合并编号早停已兑现收益，见[多机记录](lb_pumpkins.md)与[单机记录](lb_pumpkins_single.md)。首次探索回退路径、多机末代按需建表仍无新收益证据。当前任务优先级随可实现的收益、成功把握和验证成本重新比较。

## 第二批仙人掌来源的静态筛选

追加两次仓库检索，分别得到19项和7项，去重既有来源后读取五份新算法；不声称覆盖整个GitHub。源码由固定blob下载并核对Git对象哈希，原搜索响应、树、源码与预算在`.codex/leaderboard-astra/github-cactus-search2/`。

| 来源 | 固定树 / 已读算法 | 结论与未覆盖范围 |
| --- | --- | --- |
| [KyleGough/the-farmer-was-replaced](https://github.com/KyleGough/the-farmer-was-replaced) | `af472f52d7c01af5630863150cecdc92c17a2cd8`；`cactus/cactus_odd_even_sort.py`全文 | 两轴各16条线、每线31次固定比较，加移动共1024个200t动作；按当前模型计费33.712128秒，加必要铺田至少36.872640秒，尚未计派发与解释器，已高于当前34.727313秒。README自述43秒不代替本机成绩。三个依赖未读，未执行。 |
| [lukasvermeer/the-farmer-was-replaced](https://github.com/lukasvermeer/the-farmer-was-replaced) | `6f09cc0c40c59e42f1ac32db65603c94fc4ae6ee`；`farm_cactus.py`全文 | 串行全田成熟巡查与施肥，再逐行逐列双向冒泡，无新的并行或交换节省依据，未执行。 |
| [Berman510/tfwr](https://github.com/Berman510/tfwr) | `0f0f4fd01f708363cca70001e526426393fb535d`；`cact_sort.py`全文及README相关算法/成绩段 | 普通行列双向冒泡，每趟边界缩一格；22格8机65.44秒不与32格32机混比。两个依赖未读，未执行。 |
| [insivam/The-Farmer-Was-Replaced](https://github.com/insivam/The-Farmer-Was-Replaced) | `56daa789af9341afd1e1ea1f60659ade5c7ff764`；`plantCactus.py`全文 | 逐行列插入、每交换跟随移动，仍含旧`trade(Items.Cactus_Seed)`；`moveTo`依赖未读，未执行。 |
| [RubenNijhuis/the-farmer-was-replaced](https://github.com/RubenNijhuis/the-farmer-was-replaced) | `518ca0068c81be6839b9d114706d945aefec9d02`；`cactus.py`全文 | 排序前预检查、最后交换收缩的双向冒泡与行列切片，仍是已覆盖结构；四个依赖未读，未执行。 |

本批只作本地静态研究，没有模型、游戏或发布动作。固定网络预算明确依赖当前模型API计费，不能冒充上游真实测试。其余候选因没有新的改善依据暂不投入适配，不能据此证明它们在所有条件都更慢。

## 快速重置路线检索

补充README范围检索`"the farmer was replaced" "fastest_reset" in:readme`得到10项；此前仅名称/描述两次检索0项不代表没有脚本。原响应、固定树、blob及SHA256保存于`.codex/leaderboard-astra/github-reset-search/`，取得的blob均核对Git对象SHA1。每次18秒、批次25秒上限，未执行任何本批外部代码。

| 来源与固定版本 | 本轮阅读 | 取舍 |
| --- | --- | --- |
| enihsyou，树`37a97b58e15dc60bb6aff8829eeb58293be18b39` | `fastest_reset.py`722行全文，blob`f866d8dd3be04b642224a790e15364402c4b8bc8`；沿用已核对MIT许可 | 基础资源多机函数只有max_drones()==2分支，多机向日葵空实现，补电调用注释。单机向日葵桶7..15却从16取值、金币入口重复写COSTS等静态问题保留。未执行，未适配。 |
| KyleGough，树`af472f52d7c01af5630863150cecdc92c17a2cd8` | `fastest_reset/fastest_reset.py`453行全文，blob`063dc84b6851e1ab730948bfb52335cc3cf05674`及README全文 | 作者自述49m37s/#20，不是本机实测。路线提前多档浇水、肥料及16机，最后预备2M Bone；尚无比当前路线减少生产需求的依据。custom_harvest下载TLS EOF，其他十余依赖未读；未执行，固定树未见LICENSE文件，不发布。 |
| Zwidek12，树`9388deb7d9bd4e87e7d8eed46e6607045439b29c` | README82行及`full_reset_solution.py`86行全文，blob`767338f2b1799180bdf932317613bd98dba0927f` | 目标是成就通关，自述6:59:34。固定高等级解锁次序，9个生产依赖未读；未见低费用主路径依据，不执行。README允许游戏内使用修改，未迁入正式代码。 |
| PKDGOOD，树`9e879f2f2d2d6602706529f7a7e79e356d43514b` | README18行全文 | 完整科技自动化引擎，无可比较时间；主程序和设计未读，不给性能结论。 |
| Berman510，树`0f0f4fd01f708363cca70001e526426393fb535d` | 仅定位`farm_unlocks.py` blob`ff5052938d512e79ae4ee9ede62ff13da06b9f3c` | 下载TLS EOF，正文未取得，不给算法结论。 |

本批没有新实机候选，不把“找到Reset入口”视为更快证据。六个下载/检索工具ty零诊断，两次TLS失败保留且未重复请求。另从本地代码发现单机补电正向绕路，独立候选完整统计3032.746秒未优于正式3000.959667秒，见[Reset记录](lb_fastest_reset.md)；该改动不归为上游算法。

## 2026-10-29：第二批恐龙来源静态筛选

两次公开仓库检索返回59项和13项，各限前30项；不声称覆盖整个GitHub。六个新来源中的五份树已固定，已取得正文均核对Git blob SHA1，原JSON与SHA256保存在`.codex/leaderboard-astra/github-dinosaur-search2/`。没有执行任何本批外部源码，也没有据仓库名称或作者自述认定更快。

| 来源 / 固定树 | 已读范围与判断 |
| --- | --- |
| fol21/the-farmer-was-replaced-algorithms / `2eb0c104c73de4b9f776813f804047893b6d5aa5` | README111行全文，描述追目标和受阻侧步，无可比成绩。compose.py未读，不给实现性能结论；固定树无LICENSE。 |
| fenxi-uint8/the-farmer-was-downgraded / `57072e98847ab6564dbb249a0869f84c467c3740` | dinosaur.py105行、README、0BSD许可全文。静态Hamilton编号按头尾顺序取捷径，半场后退回固定环，每步list.insert(0,...)维护身体；constant/utils未读。未发现新的中后期移动构造，不执行。 |
| 401rk8/The-Farmer-Was-Replaced / `0bdfd063a3fd08a03a8dc5b7c90b110305432952` | 两份bone.py共116行及README131行全文。前n个苹果按轴追踪，受阻可摘帽重来，之后固定环；README主要讨论成就，没有当前榜单完整统计。固定树无LICENSE，不迁入或发布。WSL两次读取超时，改Windows网络栈取得相同blob。 |
| claud2893/TFWR_Best-Functions / `69ecf22db888ef53208416630d96bf452c958a6a` | README29行全文，仅描述perfect_move；代码blob读取超时，未读正文，不给算法结论。树有LICENSE但正文未读。 |
| luki4fun/TheFarmerWasReplaced / `9c313f53b2baca6bfdb080f332774e8060abfc57` | mainSnakeSolver2.py138行全文：前25%贪心轴向侧步，未到目标递归，没有循环进展保证；后段无限固定路线、不检查move失败且无正常摘帽结算。README和另一solver下载超时；固定树无LICENSE。未执行。 |
| veisveer/TheFarmerWasReplaced-Solutions | 树请求超时，未取得正文，不给结论。 |

这一批静态检索未形成可执行的新候选，当时818.713889秒保留为历史。后续B站作者的递归矩形构造已取得完整改善，当前版本见[恐龙策略](lb_dinosaur.md)和[B站来源](bilibili_strategy_research.md#恐龙递归区域)；后续研究须证明自由区连通、尾部释放和持续恢复，不能用本批静态环覆盖声明否定新的区域变形。
