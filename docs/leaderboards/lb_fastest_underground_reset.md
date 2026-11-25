# 地下重置（`lb_fastest_underground_reset`）

## 当前策略与成绩

当前脚本：[lb_fastest_underground_reset.py](../../scripts/leaderboard/lb_fastest_underground_reset.py)。2026-11-25 请求 `575` 的 4 轮完整统计均值 **36:43.926（#4）**，比账号原纪录 43:21.273 快 6:37.347，低于 #1 的两倍线 36:47.346。[进度总表](leaderboard_progress.md) · [公开快照](../../references/leaderboards/status_snapshot.md)

2026-11-25 重构后，原版地下重置初始条件 + 默认游戏随机（`game_leaderboard_random`）12 轮完整验收：**12/12 达标、0 失败**（彻底根治旧版 2026-11-21 复测 19/20 失败），累计 **26,303.925 游戏秒**，均值 **36:31.994（2191.994s）**，SD **79.501s**，SE **22.950s**，95% CI **±50.513s**，区间 **35:07.073～39:27.300**（相对 `#1` 距 **+98.6%**，跨入 2× 线并较实机 `#4` 提速 **-6:49.3**、较旧版 21 轮本地均值 `43:41.735` 提速 **-7:09.7**；同 seed 1..6 配对由 `43:28.950` 降至 **`35:10.521`**，-8:18.4，0 警告；原失败种子 `1438323200` 验证通过）。

核心改动：
1. **根治 19/20 失败缺口**：移除 `ur_dynamite_stock`、`ur_mushroom_stock`、`ur_i_stock`、`ur_c_ur_mine_parallel` 等处的 `empty >= 8` 致命退出；修复 `ur_d_open_ground` 并发结算 TOCTOU 竞态（遇非 `Dynamite` 重读 `ur_d_read_ground` 识别 `"ended"`），令 `"ended"` 终态优先于竞态 `"error"`，且单盘异常改为 `need_clear = True` 换盘继续而非中止整轮。
2. **地上高效前缀 + `solar_wave` 供电**：移植普通重置高效前缀（正交 3×3、`solar_reserve` 收花后 `clear()`、跨区伴生 `stock_anchors`、连续批多机南瓜与四机小迷宫）消除旧版 `ur_s_tick_cell` 100% 纯胡萝卜 0% 伴生缺陷，将 4 机前缀由 `1073s` 压至 **`~865s`**（-208s）；单机 `do_a_flip()` 补电替换为四机 `solar_wave`（省 ~50s）。
3. **地下双引擎提速**：
   - **连续深探扫雷 + 差集推理 + 零下行风险猜格**：`ur_dynamite_stock` 满清后不再 `clear()` 回浅层，利用 `GetMineRatio(z)` 随深度由 `0.10→0.17` 爬升及 112 层硬度重置，自适应限深搜索（浅层 `covers < 224`，深层 `z <= -250` 放宽至 `covers < 420`），叠加两线索差集推理与低风险破局猜格，单盘 12×12 炸药收益由 `2,832` 升至 `4,512～5,568`，末段 20k 炸药由 `~470s` 压至 **`~180–210s`**（-260s+）。
   - **保桩浇水竹子**：迁入 `hover(1)` 齐根保桩三趟收割并利用积累水箱浇水，200k 竹子所需稻米储备由 `6,112` 骤降至 `~1,120`，末段稻米+竹子由 `~133s` 压至 **`~60s`**（-70s+），并省去昂贵的 `Rice 5`（2000 Block）。
   - **四机并行矿采与浅层找菇**：`ur_i_stock` 改为主机 `prospect_iron()` 命中后 4 机并行掘目标柱及邻柱；`ur_q_stock` 三角定位后 4 机并行掘邻柱且同片多矿脉续采；`ur_mushroom_stock` 限制浅层搜索（`covers < 112` 避开 300+ 层全田揭盖）；筹资按 `Quartz → Iron → Coal` 依赖倒序避免重复采煤；`Mushrooms 2` 时一次筹齐 7,600 金覆盖后续 `Mushrooms 3 + Dynamite 1`；`Ore_Boost 1` 前移至 `Quartz 3` 之前；稻米收割去除 `do_a_flip()` 改为浇水轮询。

以下为旧版 `4ee5f51` 的 2026-11-17 历史对照记录：

2026-11-17按原版零库存地下重置目标比较，固定模型与资源，每批60墙钟秒、最多4进程、7000单轮游戏秒、500万API／1亿解释器节点。先用`session.py`完成共同seed1..7且各累计超过18000游戏秒；随后预先固定扩样到seed1..21，保留全部失败：

| 版本／样本 | 完成轮数／累计游戏秒 | 均值／标准差／标准误（秒） | 结论 |
| --- | --- | --- | --- |
| 改前视频开局＋共用大迷宫，seed1..7 | 7/7／19178.968474 | 2739.852639／123.073052／46.517241 | 同条件效率对照 |
| 当前四机独立小迷宫，seed1..7 | 7/7／18319.854894 | 2617.122128／72.299581／27.326673 | 7/7更快，均省122.730511秒（4.48%）；配对标准误26.134003秒 |
| 改前版，扩到seed1..21 | 20/21，整组无效 | 不报成功均值 | seed8扫雷连续8次查层扑空，未解锁终点 |
| 当前版，扩到seed1..21 | 21/21／55056.439806 | 2621.735229／94.524108／20.626851 | 作为当前模拟时间 |

效率节省只引用共同7轮有效对照，不拿旧版21轮中成功的20轮重算均值。当前版21轮通过不代表消除了原有查层限次风险；稻米4级组合也在新增seed8遇到扫雷8次扑空，其整组时间已撤回。原始会话、扩样批次、预算、源／模型指纹与前后存档回执统一索引在`.codex/reset-under-combinations-20261117/results.json`。最终正式路径seed1复现2681.264675502秒，目标实际支付、仅剩主机，ty零错误零警告（38条hint）。模型使用本地seed，不能作为已上传成绩。

首seed首次解锁向日葵602.53秒，双机984.62、四机并进入地下链1073.27秒；Mining6 1320.70、Mining8 1900.20、Dynamite4 2071.28、Expand6 2122.94秒，最终2681.264676秒。Mining7的90 Quartz、Mining8的250 Mushroom与各产量等级都仍是可比较的投资。扫雷查层208对应Quartz解锁后的7块循环白名单[3,5]，维持8次扑空退出；最终付款前补电目标500、其他链1000。末Power0、Block10568、Rice4180、Quartz360、Dynamite2588，尚未最小化；逐盘维护供电的代表已对照，见淘汰表。

Special_Soils只加成种在对应地块上的作物：Loam对Carrot/Sunflower、Perlite对Bamboo/Tree/Bush/Cactus各2倍，须计挖土、整地和回程。Jump榜内禁用，爆破钻需12M Dynamite远超终点20k，仍排除该投资。历史request542首轮找层失败整场作废，request550完整均值3118.780秒才是已上传记录。

## 淘汰与未采用方案

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 参考代码 |
| --- | --- | --- | --- |
| 早12格＋八机，其余原包 | 3轮均2863.553615秒，对同批2724.105314秒，慢139.448秒；单seed1却更快 | 32000Gold投资未回本；不能把单轮优势当采用依据 | 从`8e6be61`重建：将Pumpkins3/Expand6移到矿物链前，再插Megafarm3；原资源筹资函数不变 |
| 八机提前16格＋Carrots4/Pumpkins4 | seed1完整3226.182146秒；低M6/D3/B3代表3367.906231秒 | 新供料／扩田投资超过末段少跑扫雷盘的收益；关闭所测组合，不调参数挽救 | 从`8e6be61`重建：链前P3/E6/Megafarm3/C4/P4/E7；低包再将Mining/Mushrooms/Dynamite/Bamboo上限改6/2/3/3 |
| 双机＋早12格＋M6/D3/B3 | seed1完整4746.822837秒 | 少8000Gold不能抵偿大幅降低的供料和扫雷吞吐 | 以上低包去Megafarm3，并省前缀`ur_s_next_megafarm`；保留供电 |
| 提前矿脉强化＋Quartz4 | 3轮均2756.718259秒，慢32.612945秒；八机组合seed1 2799.536869秒 | 多800Iron投资没有稳定回收；只排除对应顺序 | 从`8e6be61`将Quartz3改先Q1→Ore_Boost1→Q4；八机版叠加早12/8机 |
| 早12格／八机／Mazes2／Poly2 | seed1实际2947.285501秒，慢134.812秒 | D1真实筹10000Bone并付伴生2，但筹资、补电和后续采矿使整轮更慢；不否定其他高伴生时点 | [实际付款的Poly2组合](../../references/leaderboard_history/lb_fastest_underground_reset/20261117_rejected_early12_eight_poly2_maze2.py) |
| 八机12格＋Quartz4/Dynamite5 | 3轮均2922.254685秒，慢198.149371秒 | 额外800Iron与800Quartz未回收，不能仅看末段盘数减半 | 早12/八机版在M8后买Q4，Dynamite目标级改5 |
| 联合预备后续7600Gold的Weird，买Trees3/Carrots4/Watering4 | 七轮均2700.565122秒，对同批基线2739.852639秒；只比八机小宫版2693.732687秒更慢 | 相对八机小宫没有新增收益，且只4/7快于原基线，不替换已采用四机版 | 八机小宫首次筹32000Gold时额外预备后续金币Weird及派机开销；先T3，再C4/W4，实际付款 |
| 八机购买时点移到M6后 | 七轮均2693.129490秒，只有5/7快于原基线；只省46.723秒，配对标准误48.283秒 | 不足以替代四机小宫；提前八机、延后扩田的另一代表seed6未解锁，整场无效 | 当前`ur_route_gold`加早P3/E6/Megafarm3；将其中P3/E6或全部移到M6后，宫数限定在地图容量内 |
| 四机小宫＋Rice4 | 前7轮均2587.129552秒，扩样21轮有seed8扫雷8次扑空，整组无效 | 必须保留失败；不能把43:07当可用成绩，也不能说是缺米造成 | [稻米4级失败组合](../../references/leaderboard_history/lb_fastest_underground_reset/20261117_rejected_small_maze_rice4_seed8_failure.py) |
| 四机小宫，逐盘低电时补到500 | 七轮均2613.115326秒，对四机小宫2617.122128秒只省4.007秒，配对标准误13.263秒 | 补电与随机盘变化未给出可区分收益，继续保留采用版 | 当前源`ur_dynamite_stock`每盘开始若Power<100则真实`ur_power_stock(500)`；R4/M7叠加代表seed1为2770.828130秒 |
| Ore_Boost2、Jump、12M炸药爆破钻 | 机制／成本直接排除，不模拟不可能代表 | Ore_Boost最高1级；Jump榜内禁用；钻头费远超终点2万炸药 | 原版UnlockSO、API与榜内规则 |
| 只加胡萝卜一田预备与提前供电 | 7200秒会话3轮均3057.933735秒，对同批2991.607495秒 | 首seed四机前缀1424.16秒虽比1483.03早，整轮反慢66.326秒；不采用，不能否定视频固定布局与路径 | [前缀候选](../../references/leaderboard_history/lb_fastest_underground_reset/20261116_rejected_carrot_forecast_prefix.py) |
| 轻量Mining6/D3/B3或M7/D3/B4 | 完整3941.048～4334.263秒及4002.216秒 | 少科技费没有抵消慢矿采、蘑菇与更多扫雷盘 | [20261111_rejected_sim_72m14.263s_package_m6_d3_b3_funded.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_72m14.263s_package_m6_d3_b3_funded.py) |
| Mining7/D4/B4及中档矿物等级 | 合并供料三seed3309.435秒；Iron4/Quartz2首seed3249.595秒 | 少90石英或低一级增产的整条成本仍高于当时3182.025秒 | [20261111_rejected_sim_54m09.595s_balanced_ore_i4_q2.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_54m09.595s_balanced_ore_i4_q2.py) |
| 单机早下地、藏宝图筹Gold后买机 | 首双机2068.51秒，完整4783.336秒；旧早下地7000秒未完成 | 较短地上前缀被串行矿采和筹Gold回吐，只关闭所测组合 | [20261111_rejected_sim_79m43.336s_minimal_treasure_light_ore_complete.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_sim_79m43.336s_minimal_treasure_light_ore_complete.py) |
| 无电感染先四机/不买伴生 | 完整3644.515/3750.546秒 | 缺电且推迟提速/增产，四机1619.88秒仍晚，不能否定有电早并行 | [20261111_rejected_infected_lean.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_infected_lean.py) |
| 独占列并行采铁、额外备煤 | 采铁代表3503.526秒；备煤共同八seed均3136.516秒 | 阶段备煤虽省约27.5秒，地形/供料及后续费用回吐 | [20261111_rejected_parallel_iron.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_rejected_parallel_iron.py) |
| 所有筹金小宫、蘑菇查层48/80 | 中期小宫三seed3024.479秒对3006.673秒；查层八seed3142.196/3075.309秒 | 单项均未改善；部分组合有失败seed，不能删坏样本报均值 | [20261112_rejected_followup_under-seg80.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_under-seg80.py) |
| Rice6/Bamboo5及米预留减半 | 八seed3072.353/3147.393秒；米减半组seed8找层失败 | 升级未回本、减少种子储备后完整组合未通过，保留联产时点账 | [20261112_rejected_followup_rice6-late.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_rice6-late.py) |
| 全程减供电/末段仅300 | 前者途中断电，后者又补一整批 | 需区分前期工作量和末段余额；末段500才有同条件完整收益 | [20261112_rejected_followup_power-late300.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_power-late300.py) |
| 常规蘑菇按片路线复用迁入 | 八seed3052.779018秒，对3034.092696秒，仅3/8更快 | 全科技局部收益不等于低科技整轮收益；只缓存或其他派发仍开放 | [20261112_rejected_followup_mushroom-route.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_mushroom-route.py) |
| 竹子完整功能版迁入 | 末段20万组件三seed87.543秒，对现源63.877秒 | 500M重派收益不在该目标触发，筛种和升降增加成本 | [20261112_rejected_followup_bamboo-retained-stumps.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_rejected_followup_bamboo-retained-stumps.py) |
| 早Special_Soils、Treasure_Map3、Petrified_Pumpkins4 | 历史晚土组合六seed10172.228秒，其他代表更慢 | 局部2倍增产不足以抵偿整链投资/访问，历史结果不能套到当前路线 | [归档入口](../../references/leaderboard_history/lb_fastest_underground_reset/)（原记录未标独立源） |
| 稻米同田连续找Clay、三趟种收 | 2026-11-15共同seed1/2/3完整均3028.405526312秒，对父版2991.607494878秒，慢36.798秒 | 普通地层的深挖、成熟、塌方和供料全部计入；专用稻米榜的收益不能直接迁移，关闭这一实现 | [深挖模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_deep_rice.py)，原报告`under-rice-seed*.json` |
| 竹子每机单井闭环、首花及次花全筛 | 早期200目标seed1耗尽Rice、Bamboo0；仅末段启用仍在126605/200000时耗尽Rice | 旧6112米储备不能支付140株完整花节筛选；禁止补虚拟种子或将提前退出当完成 | [全筛模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_closed_bamboo_full.py)，原报告`under-bamboo[-late]-seed1.json` |
| 竹子闭环仅筛首花、保留竹桩 | 共同三seed完整均3045.906270510秒，对2991.607494878秒，慢54.299秒 | 能完成目标；省去二次筛选后整轮仍无改善，不替换现源 | [首花模块](../../references/leaderboard_history/lb_fastest_underground_reset/20261115_rejected_reset_closed_bamboo_first.py)，原报告`under-bamboo-first-seed*.json` |
| 后期供电复用四机分瓣生产、达标免收余档 | 共同三seed完整均3028.261093838秒，对2991.607494878秒，慢36.654秒 | 补电局部缩短但整轮未改善；真实Carrot、水、成熟及后续生产均计入，未实现统一时钟 | 从`5f34716`重建：`ur_s_parallel_solar_reserve(size,target=0)`每瓣前检查目标；`ur_power_stock`保留实际筹种和clear，后接该调用，替代原串行种收；原源`under-power/lb_fastest_underground_reset.py` |

本批原源、完整报告和指纹索引留`.codex/gemini-reset-maze-20261115/results.json`（原始材料已于 2026-11-17 清理）。稻米和竹子模块重建时分别复制为`deep_rice.py`、`closed_bamboo.py`，取`5f34716`入口，在末尾main之前静态导入`reset_rice_stock`或`reset_bamboo_stock`，以同名`ur_rice_stock`或`ur_bamboo_stock`返回其结果。末段竹子代表将原`ur_bamboo_stock`改名`ur_bamboo_stock_original`，新入口对goal<10000沿用原版，其余调用模块；`ur_need`的实际稻米预算保持不变。归档及原路径/SHA256映射见[manifest](../../references/leaderboard_history/manifest.json)。

2026-11-15这批完整比较均为原版零库存重置场景、同一seed、原目标，每例15墙钟秒，最多两进程；三个新整轮代表均正常完成、目标达成、状态完整、效率有效并回收全部工人。因初筛均值已退步，没有选择性扩seed或与旧八seed均值混比，也没有撤回八seed3026.821846秒的有效旧候选。这里只关闭已测的低科技组合，不否定同田、闭环或并行供电的全部构造。

## 历史正式版本演进

下表按首次提交日期排列，归档包含当时源码。完整轮注释保留原口径；仅有文件名时间而未注明类别的早期记录写为“版本注记”，不当作本机正式成绩。

| 日期 | 成绩（实机／模拟／版本注记） | 核心改动 | 归档代码 |
| --- | --- | --- | --- |
| 2026-11-06 | 31535.109秒（构建26462009，1轮官方完整统计；请求355）。 | 补齐其余十个地下榜的正式实机基线 | [20261106_v01_525m35.109s_87447cee.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v01_525m35.109s_87447cee.py) |
| 2026-11-06 | 29133.641秒（构建26462009，1轮官方完整统计；请求366）。 | 地下重置提前准备补给科技与满级速度 | [20261106_v02_485m33.641s_5200e71b.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v02_485m33.641s_5200e71b.py) |
| 2026-11-06 | 25147.408秒（构建26462009，1轮官方完整统计；请求371）。 | 地下重置支付资源升级Mining8缩短末段挖掘 | [20261106_v03_419m07.408s_05774719.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v03_419m07.408s_05774719.py) |
| 2026-11-06 | 22699.482秒（构建26462009，1轮官方完整统计；请求391）。 | 地下重置提前投资煤铁产量并复用扫雷状态 | [20261106_v04_378m19.482s_34edeb18.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v04_378m19.482s_34edeb18.py) |
| 2026-11-06 | 22108.401秒（构建26462009，1轮官方完整统计；请求394）。 | 地下重置用公开石英距离定位并全额计入勘探成本 | [20261106_v05_368m28.401s_95e81154.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261106_v05_368m28.401s_95e81154.py) |
| 2026-11-07 | 18140.125秒（构建26462009，1轮官方完整统计；请求401）。 | 地下重置通过付费勘探减少采铁开挖 | [20261107_v06_302m20.125s_f9c155a2.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v06_302m20.125s_f9c155a2.py) |
| 2026-11-07 | 16670.354秒（构建26462009，1轮官方完整统计；请求404）。 | 地下重置扫雷按需清理覆盖层 | [20261107_v07_277m50.354s_5167e0ae.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v07_277m50.354s_5167e0ae.py) |
| 2026-11-07 | 15440.645秒（构建26462009，1轮官方完整统计；请求411）。 | 地下重置在大田与Mining5后升级Coal3 | [20261107_v08_257m20.645s_20d5421c.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v08_257m20.645s_20d5421c.py) |
| 2026-11-07 | 15255.250秒（构建26462009，1轮官方完整统计；请求415）。 | 地下重置用前置采矿库存升级Rice5 | [20261107_v09_254m15.250s_9d317937.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v09_254m15.250s_9d317937.py) |
| 2026-11-07 | 13559.391秒（构建26462009，1轮官方完整统计；请求418）。 | 地下重置采完首段煤后重生 | [20261107_v10_225m59.391s_b4d62610.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261107_v10_225m59.391s_b4d62610.py) |
| 2026-11-08 | 11912.122秒（本地原目标三seed均值；当前供能与增量扫雷版本未实机验证）。 | 迁入地下功能与榜单的高效结构并固化模拟证据 | [20261108_v11_198m32.122s_feca66ac.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261108_v11_198m32.122s_feca66ac.py) |
| 2026-11-10 | 11067.625秒（本地原目标三seed均值；Dynamite3后Expand5版本未实机验证）。 | 地下Reset末段提前纳入Expand5 | [20261110_v12_184m27.625s_59c3edc1.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261110_v12_184m27.625s_59c3edc1.py) |
| 2026-11-11 | 54:39.570（2026-11-11官方完整3轮，request497）；C#原目标3seed均值3390.747秒。 | 地下重置打榜压缩至一小时以内 | [20261111_v13_54m39.570s_05212f0a.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_v13_54m39.570s_05212f0a.py) |
| 2026-11-11 | 未取得；C#原目标3seed均值3182.025秒（2026-11-11，当前策略未实机）。 | 调整双重置迷宫筹资与矿物投资路线 | [20261111_v14_53m02.025s_8ec59b43.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261111_v14_53m02.025s_8ec59b43.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值3067.141秒（2026-11-12，当前策略未实机）。 | 重置榜按原料订单保留伴生产区 | [20261112_v15_51m07.141s_425a5024.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_v15_51m07.141s_425a5024.py) |
| 2026-11-12 | 未取得；C#原目标3seed均值3006.673秒（2026-11-12，当前策略未实机）。 | 迁入重置榜常驻采集与分区复用 | [20261112_v16_50m06.673s_5f25fe9a.py](../../references/leaderboard_history/lb_fastest_underground_reset/20261112_v16_50m06.673s_5f25fe9a.py) |
| 2026-11-16 | 改前7200秒会话3轮均2991.607495秒，非新实机 | 冻结旧固定前缀，作为视频混种与路径的共同对照 | [旧固定前缀](../../references/leaderboard_history/lb_fastest_underground_reset/20261116_v17_sim_49m51.607s_3973de2.py) |
| 2026-11-17 | 视频混种原3轮均2724.105314秒；本轮7轮2739.852639秒，新增seed8失败，21轮均值无效 | 作为小迷宫筹金改动的冻结对照，保留失败范围 | [8e6be61正式源](../../references/leaderboard_history/lb_fastest_underground_reset/20261117_v18_sim_45m24.105s_8e6be61.py) |
| 2026-11-17 | 实机 43:21.273（#4）；本地 seed1..21 均 43:41.735；2026-11-21 随机复测 19/20 失败（seed=1438323200） | 四机独立小迷宫筹金，仍含 `empty>=8` 与 `ur_d_open_ground` 竞态 | [4ee5f51正式源](../../references/leaderboard_history/lb_fastest_underground_reset/20261117_v19_sim_43m41.735s_4ee5f51.py) |
| 2026-11-25 | 实机 36:43.926（#4，4 轮，请求 575），随机模拟 36:31.994（12 轮） | 连续向下探测扫雷、保桩浇水采竹和四机矿采 | 当前 [lb_fastest_underground_reset.py](../../scripts/leaderboard/lb_fastest_underground_reset.py) |

### 2026-11-25 新增淘汰与对照记录

| 尝试方案 | 实测／模拟表现 | 原因与适用范围 | 重建依据 |
| --- | --- | --- | --- |
| 跳过 `Ore_Boost 1`（`ur_v3b`） | seed1..6 均 `36:28.018`（比保留 `Ore_Boost 1` 的 `35:27.359` 慢 **+60.7s**，6/6 更慢） | `Ore_Boost 1` 对后续 400+ 石英与铁矿提速远超自身成本，保留并前移至 `Quartz 3` 前 | `.codex/tests/reset/build_ur_v3.py` |
| 4 机分 2 列带各自 `prospect_iron()`（`ur_v1`） | 400 铁耗 ~147s 且反复重采 96 煤；4 机全沟网（`trench48/64`）耗 142s/192s | 窄带内勘探越界浪费煤；改为主机勘探+命中后 4 机掘相邻柱仅 **51.7s** | `.codex/tests/reset/probe_iron.py` |
| 连续扫雷不限单次跨层上限（`covers < 700`，`ur_v2`） vs 全局短上限（`covers < 256`，`ur_v3a`） | `covers < 700` 遇 678 层空洞耗时 ~100s；`covers < 256` 频繁清掉 `-430` 深层 | 改为浅层 `224` / 深层（`z <= -250`）`420` 自适应上限（`ur_v4` seed1..6 `35:10.521`） | `.codex/tests/reset/build_ur_v4.py` |

## 下一步优化方向

- 向 #1 的 +50% 线（27:35.510）推进，先比较 14.5 分钟前缀与两机早下地、藏宝图筹金，再算 8 机与 16×16 地块对末段 2 万炸药的投资回报。
