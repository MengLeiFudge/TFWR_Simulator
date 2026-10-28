# lb_fastest_reset

## 2026-10-28：骨头阶段迁入边界绕行，完整统计51:46.851

将恐龙榜已验证的边界绕行与后期填隙迁入`run_dinosaur_chase_loop`，删除旧方向表构建；`finish_bones`仍按实际16×16、Speed5、Dinosaurs4筹料并收取四条完整蛇。解锁顺序、供料、金币及补电流程的执行AST保持，路径来源及MIT许可沿用`lb_dinosaur.py`与`enihsyou_LICENSE.txt`，不利用漏洞。

先用同科技骨头组件固定seed0/1/123对照：旧均值458.332347秒，新427.699304秒，均取得2080800 Bone；移动数和解释器费用均下降。随后完整Reset固定seed0/1，新版3135.982898776/3142.939359001秒，均值3139.461128889；同模拟器新复跑的旧版3188.793060419/3195.684251306秒，均值3192.238655863。两组均Leaderboard1、Bone80800、终态科技相同、库存非负、spawn/wait分别722/722和717/717，无模型警告、错误或丢输出。

前段日志不逐字相同：删除一个顶层函数定义使首阶段提前0.0025秒，后续成熟和调度时序也有变化；不能把整轮节省52.778秒全部归于恐龙路径。末次补电至第四条蛇收取的区间，两个seed分别省32.987515/44.324535秒。旧历史模型报告保留；本轮比较采用新复跑基线，未混用旧计费结果。

实机request181短筛2轮3089.349/3099.799秒，均值3094.574。request182正常完成官方3轮3076.953/3128.799/3114.799秒，逐轮均值3106.850333333秒，官方显示51:46.851；较上一完整3135.910666667秒省29.060333秒，约0.927%。迁入正式仅改注释与空白，执行AST相同；重新部署request183复核2轮3104.869/3043.484秒，均值3074.1765，单列而不替换完整统计。

三类时间为3139.461129 / 3094.574 / 3106.850333秒。短筛、完整、正式复核分别保留18/28/13条既有水不足警告；BepInEx与Unity无非预期错误，筛选停止对应`sample_limit`。全部请求按同ID回到idle，idle183后逐字恢复两份存档备份。公开账号查询此前失败，本轮未取得新的提交或名次确认。

执行候选SHA256：`cf13da3f92e20890472f140a8d16dbaed1ecb8a1f6b448f6d144db8c942b3294`。完整实机报告SHA256：`e03c5cddc4e27467766f1b1e2445065b17f998e0bb94d1139f2e44bdf47fcc8d`。原源码、固定seed报告、同版本基线、三份完整游戏报告、存档备份恢复和正式源哈希保存在`.codex/leaderboard-astra/reset-boundary-dinosaur/`；`acceptance.json`为本轮汇总，`full-analysis.json`保留最初历史对照。

下一方向：把此前因固定80秒门槛关闭的“供料前补电”迁入当前基线，按完整实际费用重新比较；旧单seed节省78秒不能直接迁作新收益。

## 2026-10-26：南瓜修补队列正式上榜52:15.911

当前正式版只改变`pumpkin_stock`和`pumpkin_strip`：第一次照常准备各格，后续仅回访尚未健康成熟的南瓜，移除成熟格的重复访问。每列保持唯一写者，主机等待所有任务完成后才收整田；保留原种子预算、补水条件、升级路线及资源费用。每田以120游戏秒和全局7000秒为有限截止，不利用重复领取或计时漏洞。

同场景固定seed0/1完整本地时间3180.089830198/3164.788358335秒，均值3172.439094267秒，比父两seed均值省65.511秒。两个样本终态科技一致、Leaderboard1、Bone80800、库存非负、全部worker回收；成熟苗圃产量按当时科技及伴生逐条核对通过。本地没有错误、警告、失败或输出丢失；不宣称罕见失败分支已动态覆盖。收益主要来自中段南瓜供料，seed1伴生仅提前约3.39秒。

候选实机request97短筛2轮均值3142.0615秒，随后request98正常完成官方3轮：3120.134/3109.099/3178.499秒，均值3135.910666667秒，官方显示52:15.911。相比上一正式3223.604秒，节省87.693秒、约2.72%。Steam账号查询于18:45:19 UTC确认第57名、3135911ms；排名仅代表查询时点。#10仍为1966.927秒，当前差距约1.594倍。

三类时间独立保留：本地3172.439秒；短时3142.062秒；完整游戏3135.911秒。执行候选SHA256为`f772d2bf20b079692a7b20dc6a44b35f271943c1abd82ae6aff9f72d9d9d6eb3`，迁入正式时仅更新完整成绩注释，AST相同，正式SHA256为`d774293c3f64bb182b8615e941c4d7794905ed6d853ee8e0297459c0420b1a9b`。

短筛及完整统计分别保留19/22条水不足警告，均达到相应完成轮数；完整统计BepInEx与Unity请求日志无错误，结果页自动关闭并按同一请求回到idle。短筛的`oracle_error ... reached stable leaderboard runs`对应正常筛选停止`sample_limit`。原始源码、两seed报告、完整实机输出与双日志、公开榜查询和迁入清单保存在`.codex/leaderboard-astra/iteration-20261026/`及其`reset-pumpkin-pending/`子目录。

正式源复核request99短时2轮3152.194/3148.451秒，均值3150.3225秒；这是独立复核，不替换request97短筛或request98完整统计。核对终态idle后，已逐字恢复本轮Reset及lb_start两份Save0备份。

## 2026-10-26：伴生前生产升级正式版上榜53:43.604

当前正式版迁入本地首选：在首次Polyculture准备前买Speed4和Pumpkins2，提前支付种子与1500 Carrot成本，将3000 Pumpkin准备由14片田降到7片；保留早期驻点、分档供料、金币和骨头链。只做预期机制优化，不采用迷宫重复领取或模块缓存漏洞。

候选源`b396db3ab1f49a3c7e9918415511292f6b8754740aa58a68692f79e0928bdb9b`首次实机request 87完整3轮3256.249/3324.699/3246.176秒，官方均值3275.708秒。迁入时把入口及末尾调用由`lb_reset_directed`统一改名为`lb_fastest_reset`，其余执行AST不变；重新完整打榜request 94取得3214.586/3244.163/3212.063秒，官方均值3223.604秒。两个独立批次分别保存，不把改名当作提速原因。

Steam账号成绩查询在17:45 UTC确认第61名、3223604ms。当前正式版53:43.604比旧历史实测168:48.299少115:04.695。三类时间：原入口本地两seed均值3237.950217819秒；无独立短时统计；正式入口官方完整3223.604秒。本地成绩与入口改名版本关系明确保留，不伪造新的本地运行。

request 94执行源SHA256为`15f748661e541f4e843b1190e9a5e5a59e1c24019e9ae1ac321ee2c5b44f3df9`。结束后只更新文件头时间注释并核对AST相同；执行原文存于`.codex/leaderboard-astra/real-20261026/executed-sources/lb_fastest_reset.py`，最终源哈希及注释差异存于`closeout-manifest.json`。

两次完整统计分别有18和13条水数量不足警告，均正常达到结束目标。BepInEx与Unity请求日志未见异常错误。`request87-full.json`、`request94-full.json`保存完整输出与双日志；`public-confirmation-last-two.json`保存公开成绩与时间。全部请求回到idle后恢复8份临时存档覆盖，request 95正常保存退出，health确认游戏进程消失。

## 此前研究记录

## 2026-10-26：伴生前生产升级，两seed完整3237.950秒

当前本地首选b396db3a：第一次产电及Trees3/Grass4/Carrots3/Pumpkins1后，提前购买Speed4、Pumpkins2，再筹3000 Pumpkin解锁伴生。后续只补Speed至5和Pumpkins至2，保持最终科技；未并入上一补电候选。Poly前南瓜从14田降到7田，种子价格翻倍，提前1500 Carrot、Power和成熟反馈全部实付。

先seed1正常完整且净省96.164434秒，通过80秒门槛后再同SHA seed0，净省84.894406秒。0/1分别3255.765007309/3220.135428329，均值3237.950217819，比父3328.4796378075省90.5294199885秒/2.719843%。seed1伴生提前49.237秒、8机提前89.624秒，优势保留至终点。

两组Leaderboard1、科技同父、Bone80800、库存非负；全部单机及多机苗圃成熟收益按当时伴生核对通过，spawn/wait分别716/716和712/712，无错误警告失败丢输出。三值3237.950217819/null/null，非实机成绩。证据`.codex/leaderboard-astra/reset-bootstrap-capital/`，报告0=fbb5ebc3、1=704b5773；双编译、两脚本ty零诊断、无模型残留。正式py/Save0/79保持。

## 2026-10-26：供料前产电单seed省78.107秒，未到扩样线

候选b0af9c35仅在原a0e54ad4的P4备料之前调用一批solar_reserve，保留后段全部门槛。唯一seed1完整3238.192720174秒，对原3316.299862335净省78.107142161秒；低于事前80秒门槛，保留单样本并停止扩样，不替代3328.479638两seed首选。

新增准备使P4完成晚13.991秒，但P4时Power30.136→1056.538，Expand7从0→296.986，扩田完成提前58.784秒。1M金币时Power2081.575→2301.411，越过原骨头段2200门槛而自然省下一批产电，整轮累计省78.107秒；末Power3474.220→1828.293，不将各段简单减半。

Leaderboard1、科技同父、714spawn/714wait、成熟生产全当前伴生、无错误警告失败负库存。证据`.codex/leaderboard-astra/reset-supply-power/`源码、原报告852a5bab、analysis-seed1与research-note；三值3238.192720174/null/null，双静态编译及ty0。仅一次模型，正式、Save0和79保持。

## 2026-10-26：前伴生混种自供料完整负例

固定奇格Carrot、4步网格Tree、其余Grass，试图将种子材料生产并入必要巡回；不查询尚未解锁的伴生。首版d7364a43的Speed3复合订单在Carrot达标后仍补种，持续消耗Wood，完整3451.361134秒。只修补种停止条件的3bdd336e完整seed1为3331.598561631秒，仍比父a0e54ad4同seed慢15.298699296秒；未过100秒扩样门槛，关闭固定布局，不调配比/水量。

修正后首4×4混种段仍160.423462秒，原生收获13次Tree5和1次Tree25，单树供料限制复合订单；后期6×6的764 Carrot只用38.721177秒，但Poly和首次双机仍晚，整轮未回本。两版均Leaderboard1/科技同父/全部回收/无错误警告失败负库存；Poly后1370/1355次多机成熟收益核对通过。证据`.codex/leaderboard-astra/reset-prepoly-mixed/`原两源码、原报告、analysis和research-note；修正版三值3331.598561631/null/null，当前3328.479638两seed首选保持。正式、模型和Save0未改。

## 2026-10-26：提前Maze2并复用早期驻点，两seed完整3328.480秒

候选a0e54ad40863594ae804c18c9dd398527d4b1f4ca534f8089c46cda10e08848d在P4版上提前实付Cactus1/Mazes2，再将已有两机、四机的金币段接入晚段驻点服务。实际Weird、建图建表、派发复制、巡逻返程、Power及全部wait均收费；后段只支付剩余科技，Cactus目标按剩余费用调整为1052000。

seed1完整3316.299862335秒，相对P4省102.759911065秒，通过预设100秒门槛后才跑seed0；seed0完整3340.659413280秒、省29.580529467秒。同SHA均值`3328.479637808 / null / null`，较P4均值3394.649858073省66.170220266秒。两机驻点收益不稳定：四机时刻seed0提前5.966秒、seed1反晚24.070秒；八机时刻分别提前33.848/85.519秒。结束此固定接入分支，不继续按两机差异做局部调参。

两次Leaderboard1、终态科技同P4、Bone80800，Cactus18992/Gold1744的取整反馈单列，不强配父库存。所有worker回收，无错误/警告/失败/丢输出/负库存；多机苗圃成熟收益按实际科技和日志逐条相符。证据`.codex/leaderboard-astra/reset-early-stations/`两份原报告、analysis-seed0/1、source-manifest和three-times；尚无实机成绩。

此前仅提前Maze2、仍单机追宝的fe2eada5单seed完整3366.999939331秒，省52.059834069秒，未过80秒扩样门槛；证据`reset-early-maze2/`，没有以该单样本替代两seed均值。

另一个前伴生普通Carrot网格候选55da845e在1413.199982秒有限退出，Leaderboard0，完整三值null。虽首次两机提前32.095秒，随后原并行Carrot苗圃耗尽Wood，204库存未达到324目标。该变化暴露原苗圃按预计次数备料不能保证任意随机序列成功；现有两样本通过不解除此材料边界。失败报告保存在`reset-prepoly-carrot/`，未重试或修改模型。正式py、Save0和79保持。

## 2026-10-26：八机供料先升南瓜四级，两seed完整3394.650秒

在4c2876ce并行苗圃版上只改staged_supply：先真实支付16000 Carrot购买Pumpkins4，再支付Expand7与Cactus科技供料。12×12整田产量3456→6912，使64000 Pumpkin扩田由19田减至10田；种植成本同步随等级升高，原动态备料/失败出口保持，没有借后期库存或免费补Power。

同SHAa2b67effa29ab4253e247ecaf1323fe8bac1ab05d4e786f3d1805a6bd95d8058的seed1完整3419.059773秒，比父省132.538771，过事前80秒门槛后才跑seed0；seed0为3370.239943秒、省139.505543。均值`3394.649858073 / null / null`，比父3530.672015省136.022157秒/3.852585%。两组到Water5的84/87条日志逐字同，八机时刻不变；供料结束提前138.754263/132.188152秒，整轮收益没有回吐。

两次Leaderboard1，终态只多一级Pumpkins，其余科技及Bone80800/Cactus129328/Gold1600同父。全部worker回收，无错误/警告/失败/负库存/丢输出；多机苗圃成熟收益按实际科技和生产日志核对通过。证据`.codex/leaderboard-astra/reset-pumpkin-multiplier/`的source-manifest、两份原报告、analysis-seed0/1及three-times。模型、正式py、Save0和79保持；尚无该版本实机成绩。

## 2026-10-26：自循环感染提前双机，完整偿付只省3秒

非Bush成熟Tree可消耗正数1 Weird切换感染；Trees3普通感染收益10、净增9，棋盘Tree四邻均Grass而不互相取消感染。实际一次肥料启动可供给Maze1与首双机，单独前缀958.699588秒完成。该机制核对Core与模型一致，不用零数量调用；前缀尚欠Power、伴生和Speed4/5，不能算同等科技领先。

完整847446a739450267955e008c977ee0a934c64bf282cd84ba4b37e0fdf08415c0实际以双机普通备料、并行南瓜偿付前置，Poly后切回原并行苗圃。唯一seed1为`3548.590528 / null / null`，比当前同seed3551.598544只省3.008016秒，未过事先150秒扩样门槛，不跑seed0，不替换3530.672015两seed首选。新增定义/判断导致首双机962.696997，较父1426.050070早463.353073；偿付完毕已1429.665593，四机1599.918423反晚于父1571.163003，说明早期领先主要是欠款。

完整Leaderboard1、科技和Bone80800/Cactus129328/Gold1600同父，823spawn/823wait，无错误/警告/失败/负库存/丢输出。所有后期苗圃成熟收益按实际科技与生产日志核对通过；前伴生阶段允许Reset实际低倍率。证据`.codex/leaderboard-astra/reset-weird-recycle/{full-manifest.json,full-seed1.json,full-analysis.json,three-times.json,research-note.md}`；报告986624fc、墙钟21.460秒。关闭该固定偿付顺序，不否定自循环感染机制的其他用途。正式py、模型、Save0与79保持。

## 2026-10-26：苗圃生产并行，两seed完整3530.672秒

在33f1c591多机补电版上，仅把已有多机后的九锚点串行苗圃改为全图四分之一生产位与永久支撑：支撑先分区准备并全部join，生产随后独占行巡回；Carrot重抽所需Hay/Wood实际备料。单机前期、科技、补电目标和后段路线保持，新增定义及并发反馈均进入完整计时。

候选4c2876ce2700778868f8fa7361b6d736fa959764f2303711eda39b23f4a13067的seed1为3551.598544秒，比父同seed省450.468250秒，通过150秒门槛后才补seed0；seed0为3509.745486秒、省404.813654秒。同SHA均值`3530.672015 / null / null`，较父3958.312967秒省427.640952秒/10.803616%。这仍是模型结果，尚无实机时间。

初版158fce78在接受种植时感染，未兑现树占用肥料；第二座迷宫前肥料耗尽并触250万API上限，完整时间null。原失败源码/报告保留。修正版仅在成熟收获前施肥，主机派发前备足本批实际肥料；不足时用原生一秒flip等待并计入整轮。两次正常样本未触发该等待，不宣称等待或罕见失败分支已动态覆盖。

两次Leaderboard1、终态科技同父，Bone80800/Cactus129328/Gold1600，无错误、警告、失败、丢输出或负库存，全部worker回收。按升级时间核对1075/1067次多机苗圃成熟收益均符合当前伴生倍率，数量与生产日志一致；向日葵仍每份1232×8+72×1。随机和其他资源反馈不同，不作逐步等价声明。证据`.codex/leaderboard-astra/reset-parallel-nursery/{v2-source-manifest.json,v2-seed0.json,v2-seed1.json,v2-seed0-admission.json,v2-seed1-admission.json,analysis.json,three-times.json,research-note.md}`；正式py、模型、Save0与79保持。

## 2026-10-26：已有多机分档补电，两seed完整3958.313秒

父37a4e31a仅修改solar_reserve的多机分支：分区播种并回收全部任务，再按15→7逐档派发收花并全部join。单机仍原流程，所有科技与2000/2200 Power门槛保持；Carrot备料在父调用中实付，未并行或遗漏。普通失败仍全回收并停止，单次补电180游戏秒有限截止。

候选33f1c591515642db8f764b78794e25b80f56300416191711ea740bc90ed2ed60完整seed1为4002.066795秒，比父同seed省307.033158，达到预设150秒门槛后才补seed0；seed0为3914.559139秒。两seed均值`3958.312967 / null / null`，较父4314.688317省356.375350秒/8.259585%。8机后的四次补电调用约18～27秒；旧相邻日志间隔还含备料，不能全部归为种收节时。

两次Leaderboard1、648/644次spawn与wait相等，无错误/警告/失败/丢输出/负库存，终点科技一致，Bone80800/Cactus129328/Gold1600。每份8批共1304花，1232×8+72×1，恰每批最后9株低倍；随机与水肥Power反馈不同，未宣称前缀逐步配对。证据`.codex/leaderboard-astra/reset-parallel-solar/{source-manifest.json,seed1-admission.json,seed0.json,seed1.json,analysis.json,three-times.json}`。正式py、模型、Save0与79保持，尚无实机成绩。

## 2026-10-26：先双机后伴生，实付速度与供电后单样本4248.380秒

先以Trees4/Fertilizer2的真实感染收获供给Maze1，暂缓Polyculture，私有619107cd前缀1156.899859秒取得双机，比父版早约313秒；此时Poly0/Speed3，不能视为同等科技的整轮领先。首次前缀d4aeaf4d误把感染收益限定20，遇Poly0偶然伴生的100后有限退出，失败报告保留；修正只接受真实20/100，没有提前调用未解锁get_companion。

直接接回完整路线62017bdc得4396.291945秒，比父版同seed4309.099953慢87.191992秒。双机南瓜后半及后续速度付款无电，前缀领先被回吐。仅将入口改为双机后先实付Speed4并实际补电，再生产Pumpkin/解锁Poly、购买Speed5，ff0af0d660161fb2c1219a3ac258f332cd3e621d2cf59d3190db35c4c69fee24完整seed1为4248.379847秒，省60.720106秒；未达预设100秒扩样门槛，保留单样本并停止此分支调参。没有把未扩样的单样本替换驻点版两seed均值4314.688317。

两次完整运行均Leaderboard1、347次spawn/wait，终点Bone80800/Cactus129328/Gold1600，无错误、警告、丢输出或负库存。当前候选三值`4248.379847 / null / null`；前缀不是完整Reset时间。证据`.codex/leaderboard-astra/reset-megafarm-before-poly/`的四份来源manifest、各原报告、analysis.json和research-note.md。正式py、模型、Save0与请求79保持。

## 2026-10-26：16×16金币驻点服务，两seed完整结果

私有37a4e31a79e946d32c82649bb1b84bf96ca28e5e779bba325052b1a03f079dba继承Expand7路线，把晚段单机追宝改为一次建图、8个固定图距离覆盖中心及唯一owner响应。服务机按缓存路径出去兑现后返回驻点，沿路补新开墙并更新后续路线；每张迷宫前实际补到2000 Power，全部worker回收后才换图。原生spawn复制、所有等待和返程均计费。

seed0/1完整4320.276681/4309.099953秒；同SHA两seed均值`4314.688317 / null / null`，较16×16串行金币版4711.199915省396.511598秒/8.416%。两次正常解锁Leaderboard，无错误、警告、失败、输出丢失或负库存，各333次spawn/wait相等。两个迷宫合计489次成功重定位，终点仍余80800 Bone、1600 Gold、129328 Cactus；供应和前缀时间受新增解释器及随机反馈影响，不宣称前缀逐字相同。

先前v1使用1t忙等且仅补1200电，seed1在200万API上限退出，Gold915584、Power0，完整三值null；未覆盖失败报告。v2改为付费的相邻边往返等待，并在每图前重新备电，供电成本包含在完整结果中。证据`.codex/leaderboard-astra/maze-station-team/{lb_reset_stations_v2.py,v2-manifest.json,v2-seed0.json,v2-seed1.json,analysis.json,three-times.json}`。这是本地候选，尚无实机结果；正式py、模型、Save0和请求79保持。


## 2026-10-26：Expand7全链路16×16，两seed完整结果

私有`ee2146459e29d4c800e1cc6a1049581d4dff02b849e212b4ea93347082b299e5`在流水苗圃路线的8机后实际支付64000 Pumpkin升级Expand7，后续Cactus、Gold和Bone都维持16×16；苹果库存保护同步按真实田面面积。其余helper函数AST保持，不把闭式产量直接换算为时间。

seed0/1完整4743.299982/4679.099849秒，正常Leaderboard1；同SHA两seed均值`4711.199915 / null / null`，较12×12苗圃版4925.399962省214.200047秒/4.349%。均无错误、警告、失败、输出丢失或负库存，spawn/wait次数相等。每份9田C2各131072，科技支付1034000、苹果支付16320后余129328 Cactus；4轮D4各520200 Bone，终点付款后余80800 Bone、1600 Gold。

额外南瓜期间Power耗尽按实际计时，扩田和供应边界反而晚于父版；整轮收益主要由13轮骨头降到4轮兑现，金币仍有约880秒的准备/导航主路径。证据`.codex/leaderboard-astra/reset-expand16/{lb_reset_expand16.py,source-manifest.json,seed0.json,seed1.json,analysis.json,three-times.json}`。正式py、模型、Save0与请求79保持；本版尚无实机成绩。

另一次固定“先伴生后供电”前缀a4e7b045把中间作物与Sunflower科技延后，1396.467050秒才拿Poly1，比父版晚76.878859秒；1800秒苗圃上限触发仍未双机，关闭此固定顺序，完整三值全null。证据`.codex/leaderboard-astra/reset-early-polyculture/`。runner有限返回completed不代表该策略达到双机或完整目标。

## 2026-10-26：固定支撑流水苗圃，两seed完整结果

继路线重建后，私有`6eba370330b054a08c65499006f03a6a7ebe873b3ca19bc8eeda2821a5390715`把伴生供料改为多株巡回：Hay/Carrot使用永久Bush支撑，Tree/Weird使用永久Grass支撑；仅接受指向非生产位的指定伴生，成熟后才收获。Carrot重抽实际消耗Hay/Wood，开田前先按真实种价储备，缺料和128次重抽上限均有限退出。初期Polyculture之前保持前版流程。

完整seed1为4909.399929秒、seed0为4941.399996秒；均正常解锁Leaderboard，无错误、警告、输出丢失或库存透支。同SHA两seed均值为`4925.399962 / null / null`。seed1比上一串行路线5334.560231秒再省425.160303秒；对旧组合相同seed8646.885112秒省43.223%。这里的均值只合并当前SHA两份完整报告，不混入旧版或组件。

两份报告均26田C2各41472、支付科技1034000 Cactus，13轮D4各163592 Bone；供苹果29744 Cactus后余14528，支付Leaderboard后余126696 Bone、64 Gold。苗圃改变随机消耗与其他资源末态，不声明逐步配对。早期到Polyculture仍约1300秒，金币准备与导航仍是主要后续成本。

证据`.codex/leaderboard-astra/reset-directed-development/{lb_reset_nursery.py,nursery-seed1.json,nursery-seed0.json,nursery-analysis.json,nursery-three-times.json,nursery-manifest.json}`。正式py、Save0及请求79保持；尚无本版本实机成绩。

## 2026-10-25：定向前期与倍率链重建，完整seed1

私有候选`629b2fead16e4b0c62b2be511bf9dae21b310aad1db43a999f2b0b8c0a08ab53`完整完成：5334.560231秒，Leaderboard=1，无错误、警告或库存透支。三类时间为`5334.560231 / null / null`，仅seed1，尚不是跨seed均值。旧组合6ae88cad的同seed为8646.885112秒，本次整轮少3312.324880秒、38.307%。

这次替换前期随机混种：按真实科技费用定向安排资源田，提前买生产等级与Polyculture1；伴生后用实际支撑兑现当前10倍收益，分段种降序向日葵供电。多机后用P2/P3并行整田供料，购买Cactus2、Mazes4、Dinosaurs4；Trees5提高每份肥料的Weird产出，Watering5维持产线。

26田C2各41472，共1078272 Cactus；支付科技1034000、13轮苹果29744后余14528。13轮骨头各163592，共2126696，支付Leaderboard后余126696。完整结束库存另有Power1988.231、Fertilizer596、Gold64；这些是候选自身终态，不代填旧版缺失边界。

初期迭代、普通失败和API触限报告全部保留。首个整轮尝试在买Tree4后Hay归零、付不起Carrot支撑时退出；当前版本用最多128次拒绝缺料支撑请求修正，接受后才施肥，实际种收费用保留。早期资源流曾把初始Grass误作0，旧`budget.json`只是失效条件模型，不作验收预测。

前期8机门槛的库存科技与旧版不同，其时间差不能单独当净收益；以上收益只比较实际完整结果。当前主路径仍是约2200秒的前期和约1070秒的金币准备/导航。后续先估算减少这些工作的结构，再取得新版本实际结果。

证据：`.codex/leaderboard-astra/reset-directed-development/{lb_reset_directed_full_v1.py,full-v1-seed1.json,full-v1-analysis.json,three-times.json,full-v1-manifest.json}`。正式py、Save0、请求79和旧两seed均值8617.892521保持；新版本尚无实机成绩。


当前本地候选（2026-10-24）：晚段备电与已验证固定绕环尾段组合，SHA6ae88cad，完整seed 0/1均正常且验收通过；本地均值8617.892521游戏秒，比配对正式原版10007.049873秒省1389.157352秒（13.882%），较纯备电再省47.305786秒。两组至首bone_prep的92条日志逐字同纯备电，25轮材料、移动tick、snake及持续供电通过。短时实机和游戏打榜时间均未取得；正式py保持原版，纯备电及历史版本独立保留。预算以[缓存#10](leaderboard_targets.md)为准。
## 榜单目标

- 目标类型：`fastest_reset`
- 这不是单纯资源榜，而是“以最短时间完成一轮从开局到解锁排行榜 / reset 的完整流程”
- 当前脚本是明确的阶段式路线：前期解锁、能量阶段、奇异物质/金币阶段、后续扩张与排行榜解锁

## 目标判定与核心难点

- reset 榜的成功判定不是“攒够某类资源”，而是“真正解锁 `leaderboard`”。
- 反编译源码 `Core.decompiled.cs` 里，`LeaderboardType.reset` 的完成条件明确写成：
  - `sim.farm.IsUnlocked("leaderboard")`
- 你当前给出的已知门槛是：
  - `leaderboard` 科技需要 `2M bones`
  - `leaderboard` 科技需要 `1M gold`
- 这也是为什么这榜最难：
  - 目标本身很明确
  - 但路径实现方式极多
  - 真正决定成绩的不是“代码写得多花”，而是“节奏、阶段切换、资源与科技的取舍”
- 你当前的实跑观察也很关键：
  - `#1` 已经进入半小时以内
  - 但你自己二十多分钟时还只是运行到 `main2 -> main3` 这一带
  - 这说明榜前玩家大概率不是把相关科技全升满后才去开排行榜
  - 他们一定在“提前进入下一阶段”与“把当前科技继续升高来换效率”之间做了动态平衡

## 当前基线

- 当前默认入口：`main()`
- 当前实现已经完整覆盖：
  - `step1()`：从开局推进到解锁胡萝卜
  - `step2()`：混种并升级速度，直到积累 `1000 power`
  - `step3()`：刷奇异物质并解锁迷宫
  - `try_unlock_early_megafarm()`：用 `6x6` 小迷宫金币提前解锁 `Megafarm 1`
  - `step4()`：借助多无人机南瓜推进 `Expand 6`、仙人掌、恐龙和伴生
  - `step5()`：推进 `Megafarm 3`、`1M gold`、`2M bone` 并解锁排行榜
- 2026-05-30 当前版本复跑：请求 `620` 完整结算 `finished=true runs=1 average=168:48.299`。
- 证据来源：`lb_fastest_reset.py` 当前代码结构

## 通用注意事项下的榜单特化

- 这个榜单的主瓶颈是“解锁顺序、转阶段时机、资源门槛”和“哪些系统值得提前碰”
- 不能把资源榜的“稳定吞吐”模板直接套进来；这里更重要的是最短路径和避免过解锁
- 所有资源都应视作“为了推进下一门槛服务”，而不是单独追求储量
- 这榜最核心的不是“程序技巧”，而是流程取舍：
  - 科技先不开，意味着更早进入后续阶段，但短期效率更低
  - 科技开得更高，意味着前期牺牲时间，但后续效率更高
- 尤其是这几类科技最需要做平衡：
  - 无人机速度
  - 农场大小 / 扩张
  - 无人机数目 / 巨大农场
- 但按你当前给的执行策略，第一版先不讨论“科技不升满”的极限优化，而是先做出一条能稳定跑通的满科技解锁路线

## 当前版本结论

- 当前文件只有一条主线 `main()`
- 已知结论：
  - 早期草 -> 扩张 -> 种植 -> 灌木木头 -> 胡萝卜 是当前起手骨架
  - 中期通过混种和持续解锁推进到 `1000 power`
  - 后续走“南瓜扩张 -> 仙人掌 -> 恐龙 -> 迷宫金币 -> leaderboard”的完整路线
- 当前 `step4()` / `step5()` 已经不是空实现：
  - `step4()` 会解锁南瓜，把扩张推进到 `Expand 6`，再解锁仙人掌和恐龙
  - `step5()` 会先升 `Mazes 2`、凑第一档 `Megafarm`，再补 `1M gold` / `2M bone` 并尝试解锁 `Leaderboard`
- 这不是最终成绩路线；它是第一条可继续观测的完整候选路线。
- 2026-05-30 当前版本复跑已完整结算，当前记录为 `168:48.299`。
- 真实短窗口验证显示，“满扩张”不是合适第一版：
  - `Expand 5` 后下一级需要 `8,000 pumpkin`
  - `Expand 6` 后下一级需要 `64,000 pumpkin`
  - 再继续还要 `512,000 / 4,100,000 pumpkin`
  - 60 秒窗口里，满扩张路线主要时间会被南瓜阶段吞掉
- 因此当前默认路线先在 `Expand 6` 切走，不继续刷 `64,000+` 南瓜扩张。

## 2026-04-24 真实成本探针

- `get_cost(Unlocks.Pumpkins)`：`{Items.Wood:500, Items.Carrot:200}`
- `get_cost(Unlocks.Cactus)`：`{Items.Pumpkin:5000}`
- `get_cost(Unlocks.Dinosaurs)`：`{Items.Cactus:2000}`
- `get_cost(Unlocks.Leaderboard)`：`{Items.Bone:2000000, Items.Gold:1000000}`
- 实体种植成本：
  - `get_cost(Entities.Pumpkin)`：`{Items.Carrot:1}`
  - `get_cost(Entities.Cactus)`：`{Items.Pumpkin:2}`
- 多级科技关键成本：
  - `Expand 4 -> 5`：`1,000 pumpkin`
  - `Expand 5 -> 6`：`8,000 pumpkin`
  - `Expand 6 -> 7`：`64,000 pumpkin`
  - `Expand 7 -> 8`：`512,000 pumpkin`
  - `Expand 8 -> 9`：`4,100,000 pumpkin`
  - `Megafarm`：`2,000 / 8,000 / 32,000 / 128,000 / 512,000 gold`

## 2026-04-24 真实短窗口结论

- 命令：
  - `python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_fastest_reset`
  - `timeout 100s python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 45 --startup-timeout 20 --total-timeout 75 --poll-interval 0.5`
- 45 秒窗口结果：
  - 无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 但能稳定推进到南瓜扩张阶段
  - 一次记录到 `Expand 7 time=8779.61 pumpkin=80`
- 60 秒窗口结果：
  - 无完成轮次，协调器返回 `leaderboard finished without completed runs`
  - 在“跳过满扩张”的路线里，曾推进到 `step4 time=10226.29 size=16 cactus=172`
  - 随后进入 `step5` 的奇异物质准备阶段，记录到 `weird=3019 target=1149`
- 结论：
  - `step4()` / `step5()` 现在已经有可执行骨架
  - 当前短板仍是 `step2/step3` 的种子资源警告、南瓜扩张耗时，以及首轮金币阶段效率
  - 下一轮不应回到“满扩张”，应继续压缩 `Expand 7` 之前的南瓜成本，或更早切到恐龙 / 金币阶段

## 2026-04-25 真实短窗口结论

- 计时口径修正：
  - `1min` 是真实游戏 oracle 的外层墙钟保护，只用于避免迭代时误等完整 leaderboard。
  - `fastest_reset` 策略快慢必须按脚本输出的游戏内 `time=`、阶段切换日志和资源增量判断。
  - 多无人机路线可能让真实执行达不到 `200x` 加速；这不能直接当成策略慢的证据。
  - `simulate()` / `leaderboard_run()` 的速度参数只是上限；参数很大时会受机器性能和脚本计算量限制，高计算脚本出现现实 `1s` 只推进游戏内约 `10s` 属于正常现象。
  - 验证时应根据 `reset_stage ... time=` 动态决定是否提前停止：例如金币已达到 `1M`、骨头单轮收益已经可外推、或某条探针在游戏内阶段时间明显落后。
- 命令：
  - `python3 -m py_compile references/leaderboard_scripts/lb_fastest_reset.py`
  - `python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_fastest_reset`
  - `timeout 100s python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 60 --startup-timeout 20 --total-timeout 90 --poll-interval 0.5`
- `request_id=140`：
  - `Mazes 2` + 金币单批 `600` 可以在短窗口推进到 `gold=1000240`。
  - 迷宫金币阶段结束后进入恐龙升级，记录到 `dinosaurs 2 time=11060.65 cactus=15472`。
- `request_id=141`：
  - 金币单批改成 `300` 后，`gold=1000240` 变为 `time=11178.7`。
  - 对比 `600` 批量更慢，因此当前保留 `600`。
- `request_id=142`：
  - 继续升到 `Dinosaurs 4` 需要大量仙人掌，`dinosaurs 4 time=15131.87 cactus=9136`。
  - `Dinosaurs 4` 单轮骨头为 `161312`，但剩余仙人掌不足以持续支付苹果成本，后续出现 `Entities.Apple` 缺种子警告。
- `request_id=143` / `request_id=144`：
  - 把恐龙上限改为 `Dinosaurs 3`，并在每轮骨头前按 `get_cost(Entities.Apple)` 与恐龙等级补足苹果成本。
  - 这两轮只返回了外层 `lb_start` 的 `status=done`，没有 `game_output` 里的 `reset_stage done` 或 leaderboard 平均值证据。
  - 后续发现 `lb_fastest_reset.py` 里残留游戏脚本不支持的 `<<`，因此这两轮不能作为“榜单已完成”的证据。
- `request_id=149`：
  - 直接运行 `lb_fastest_reset` 可以解析并运行到 `reset_stage done`，证明 `<<` 修复后脚本语法路径不再阻塞。
  - 但直接运行继承当前存档资源，不等价于 `Fastest_Reset` 排行榜重置环境，不能作为排行榜完成证据。
- 当前结论：
  - 快速重置当前路线已推进过金币和骨头瓶颈，但真实排行榜完成仍需要新的有效证据。
  - `Expand 7`、`Megafarm 2+`、`Dinosaurs 4+` 都是已验证不适合当前默认路线的过度投资。
  - `Mazes 2` 仍保留，因为它减少金币阶段的宝箱迁移次数；金币单批 `600` 在 `300 / 600 / 1200` 中当前证据最好。
- 提交后继续 A/B：
  - `request_id=145`：外层 `lb_start` 墙钟约 `9.64s`，但因缺少榜单结果证据，不能视为完成成绩。
  - `request_id=146`：跳过 `Mazes 2` 外层墙钟约 `9.98s`，暂不采用。
  - `request_id=147`：只升到 `Dinosaurs 2` 外层墙钟约 `10.60s`，暂不采用。
  - `request_id=148`：金币单批 `450` 外层墙钟约 `10.62s`，暂不采用。
- `request_id=166`：
  - 这轮按游戏内 `time=` 重新评估，不再用外层 `60s` timeout 判定策略优劣。
  - `gold=1000560` 出现在 `time=10246.49`。
  - `Dinosaurs 2` 解锁出现在 `time=10246.58`。
  - 骨头阶段在 `time=10438.42` 达到 `bone=40328`，在 `time=11691.57` 达到 `bone=282296`。
  - 对比无恐龙升级路线同类窗口只到约 `bone=120984`，`Dinosaurs 2` 按游戏内时间是正收益。
- `request_id=167`：
  - `Dinosaurs 3` 解锁出现在 `time=11367.47`，比 `Dinosaurs 2` 多付出仙人掌准备时间。
  - 骨头阶段在 `time=11582.07` 达到 `bone=80656`，在 `time=14274.83` 达到 `bone=1129184`。
  - 按游戏内 `time=` 外推，`Dinosaurs 3` 的单轮骨头收益明显优于 `Dinosaurs 2`。
  - 该轮暴露了新问题：后续出现 `没有种植 Entities.Apple 所需的物品`，说明每轮恐龙前只补了一颗苹果成本，没有按整轮尾长预留苹果成本。
- `request_id=168`：
  - `Dinosaurs 3` 后不再出现 `Entities.Apple` 缺材料警告，说明按整轮尾长预留苹果材料是正确方向。
  - 骨头推进到 `time=13753.87 bone=887216` 后，开始反复小额补仙人掌；这暴露了“每轮补苹果材料”会把骨头阶段切碎。
- `request_id=169`：
  - 改为按剩余骨头轮数提前预留苹果材料，可以跑到 `reset_stage done time=17160.82`。
  - 但该版把苹果成本又按 `Dinosaurs 3` 乘了 `4`，最终剩余约 `92848 cactus`，属于明显过量预留。
- `request_id=170`：
  - 金币单机批量从 `600` 改为 `900` 后，`Megafarm 3 -> gold 1M` 净耗时约 `6995`。
  - 对照 `request_id=169` 同段约 `6865`，`900` 批量不采用，保留 `600`。
  - 2026-04-26 补充：这是旧前期结构下的结论；接入早期 `Megafarm 2` 和多无人机南瓜后，需要重新验证金币批次。
- `request_id=171`：
  - 打开现有多无人机金币实现后，到 `time=14005.09` 只有 `gold=230448`。
  - 同阶段单机迷宫金币已经能到 `1M`，因此当前这版多机金币不是正收益；问题在共享宝箱与重复补奇异物质，不是外层墙钟误判。
- `request_id=172`：
  - 增加 `plant_if_affordable(...)` 和施肥数量守卫后，前期胡萝卜 / 肥料 / 向日葵警告消失。
  - 该轮跑到 `reset_stage done time=17174.86`，说明警告清理不破坏主路线，但主要收益来自稳定性而不是总时间。
- `request_id=173`：
  - 移除苹果成本上的错误恐龙等级倍率后，`bone_prep` 只补到 `cactus=37360`，最终剩余 `cactus=9904`。
  - 无 `Entities.Apple` 警告，并跑到 `reset_stage done time=16479.57`。
  - 当前采用该路线：`Dinosaurs 3` + 按剩余骨头轮数预留苹果材料 + 苹果成本不乘恐龙等级。
- `request_id=174`：
  - 尝试在奇异物质阶段跳过自动草收割、直接覆种树，跑到 `reset_stage done time=16725.91`。
  - 相比 `request_id=173` 退步，说明当前真实行为下“先收割再种树”更稳；该 A/B 已回退。
- `request_id=175`：
  - 当前默认路线可跑到 `reset_stage done time=16512.99`。
  - 关键阶段：`step2 time=1312.43 power=1001.82`、`Megafarm 3 time=3777.95`、`gold 1M time=10452.55`。
  - 这轮确认 `Power` 在后段会归零，但没有主动补电。
- `request_id=177`：
  - 在 `Megafarm 3` 后主动补到 `3000 Power`，`power_start time=3808.26 power=0`，`power time=6003.77 power=3054.75`。
  - 单独补电净耗约 `2195` 游戏秒，`gold 1M time=11103.21`，比不补电更慢；该方向不采用。
- `request_id=179`：
  - 把 `step2` 的 `Power` 目标提高到 `3000`，`step2 time=1807.64 power=3011.09`，但到 `Megafarm 3` 后仍归零。
  - 后续 `gold 1M time=16525.87`，总完成 `reset_stage done time=22523.38`，明显退步；该方向已回退。
  - `apple_prep_start` 显示苹果成本只需要 `Cactus`，`hay_need/wood_need/carrot_need/pumpkin_need` 均为 `0`，所以骨头阶段不是后段割草根因。
- `request_id=180`：
  - 保持 `step2` 目标 `1000 Power`，在奇异物质阶段空闲格尝试顺手补太阳花。
  - 真实完成 `reset_stage done time=16365.53`，略优于 `request_id=173/175`；但 `Power` 仍在后段为 `0`，说明当前资源结构下没有足够胡萝卜支撑顺手补太阳花。
  - 当前采用：不再做后段清场补电，保留 `Power` / 苹果成本日志，避免再次误判“补电一定正收益”。
- `request_id=185` / `request_id=186`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 比较树、伴生树、南瓜获取 `Weird_Substance` 的效率。
  - 普通感染树 16 株平均约 `2940 weird / 1000 tick`，逐棵伴生树平均约 `2657 weird / 1000 tick`。
  - 普通 `8x8` 感染南瓜田只有约 `232 weird / 1000 tick`；修复死南瓜并形成完整巨型南瓜后，`6x6` 约 `832 weird / 1000 tick`、`8x8` 约 `806 weird / 1000 tick`。
  - 结论：南瓜确实能获取奇异物质，但即使满足 `>=6x6` 巨型南瓜条件，专门刷 `Weird_Substance` 仍明显慢于树；南瓜只适合在需要南瓜本体时顺带产出奇异物质。
- `request_id=187` / `request_id=188` / `request_id=189`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 专测批量伴生树，比较普通树、批量补 companion、种树后先施 1 次肥再批量补 companion、逐棵伴生等路线。
  - 测试前提后来确认是 `Polyculture 1`、`Trees 10`；因此这组结论只能排除低级伴生，不能外推到高等级伴生。
  - `request_id=189` 同场均值：`sequential_plain_8_sparse16` 约 `2951 weird / 1000 tick`，`batch_preinfect_8_sparse16` 约 `2965 weird / 1000 tick`，只高约 `0.5%`；同时平均 `conflict_companions=3.00`、`blocked_companions=0.75`，实现复杂度明显更高。
  - 大田结果反而退步：`plain_12_sparse36` 约 `3068 weird / 1000 tick`，`batch_preinfect_12_sparse36` 约 `2344 weird / 1000 tick`。
  - 未预感染的批量伴生树会因为补 companion 时间过长导致树自然成熟，后续无法用肥料感染，`batch_companion_12_sparse36` 的 `weird_delta=0`。
  - 结论修正：`Polyculture 1` 下批量伴生树没有形成稳定、明显的 `Weird_Substance` 效率优势；正式脚本是否要引入 companion 需要看更高伴生等级和解锁成本。
- `request_id=195`：
  - 固定 `Trees 10`，分别测试请求 `Polyculture 1/3/6`；真实输出显示请求 `6` 会钳到 `Polyculture 5`，因此满级应为 `5`。
  - `Polyculture 1`：`batch_preinfect_8_sparse16` 约 `2789 weird / 1000 tick`，`sequential_plain_8_sparse16` 约 `2796`，小图也没有优势；`12x12` 明显落后。
  - `Polyculture 3`：`batch_preinfect_8_sparse16` 约 `10967`，`sequential_plain_8_sparse16` 约 `9552`，小图约 `+14.8%`；`12x12` 约 `9788` vs `9755`，基本持平。
  - `Polyculture 5`：`batch_preinfect_8_sparse16` 约 `43677`，`sequential_plain_8_sparse16` 约 `36574`，小图约 `+19.4%`；`12x12` 约 `38933` vs `37449`，约 `+4.0%`。
  - 结论口径修正：快速重置看收益曲线，`Polyculture 3` 的普通树效率已经从 `Polyculture 1` 的约 `2796` 提到约 `9552`，约 `3.4x`；`Polyculture 5` 的普通树效率约 `36574`，约 `13.1x`。
  - 因此 `Polyculture` 本身应进入快速重置的高优先级科技，而不是只看批量伴生相对普通树的边际收益。
  - 批量预感染伴生树在伴生等级提高后继续提供额外收益，`Polyculture 3/5` 的 `8x8/16 株` 分别约 `+14.8%` / `+19.4%`；因此只要路线已经决定刷伴生科技，批量伴生策略也应作为默认 Weird 产线候选，而不是失败对照。
- `request_id=196`：
  - 成本 probe 显示 `Polyculture 0 -> 1` 成本是 `{Items.Pumpkin:3000}`。
  - `Polyculture 1 -> 2` 成本是 `{Items.Bone:10000}`，所以快速重置在骨头阶段前实际只能稳定使用 `Polyculture 1`。
  - 结论：先把 `Polyculture 1` 接入南瓜阶段；更高伴生等级无法提前服务金币前的 Weird 产线，除非路线结构发生大改。
- `request_id=197`：
  - 正式路线在 `step4()` 把南瓜目标从 `5000` 提到 `8000`，先解锁 `Cactus`，再用剩余南瓜解锁 `Polyculture 1`。
  - 真实输出 `polyculture 1 time=2729.52 pumpkin=784`，额外南瓜成本没有吞掉节奏。
  - 后续 `gold 1M time=8364.55`，明显优于之前 `request_id=190` 的 `gold 1M time=10437.83`。
  - 最终跑到 `reset_stage done time=14521.64`，优于此前 `request_id=180` 的 `done time=16365.53`；该改动保留。
- `request_id=198`：
  - 在 `Polyculture 1` 已接入后，临时把 `upgrade_mazes_for_gold()` 的目标从 `Mazes 3` 降到 `Mazes 2`。
  - 真实输出最终 `reset_stage done time=17331.81`，明显慢于 `request_id=197` 的 `14521.64`。
  - 结论：`Polyculture 1` 改善了 Weird 成本曲线，但还不足以让跳过 `Mazes 3` 变成正收益；正式路线继续保留 `Mazes 3`。
- `request_id=199`：
  - 在 `Polyculture 1` 正式路线基础上，`farm_weird_substance_worker()` 对树位调用 `get_companion()`，只在同一无人机列负责的奇偶空格补 companion。
  - 真实输出 `gold 1M time=7885.12`，`reset_stage done time=13944.29`。
  - 对比 `request_id=197` 的 `14521.64` 明显正收益；说明即使只有 `Polyculture 1`，正式全路线里显式补 companion 也值得保留。
- `request_id=200`：
  - 放宽 `request_id=199` 的列限制，允许跨列补 companion，但仍只补奇偶空格，避免覆盖树位。
  - 真实输出 `gold 1M time=7349.45`，`reset_stage done time=13409.57`，继续优于同列版 `13944.29`。
  - 当前保留跨列补 companion 版本；它提高了 Weird 产线，也顺带保留了更多 `Carrot`，没有引入新的缺材料警告。
- `request_id=201`：
  - 按“骨头阶段棋盘太小”的怀疑，临时改成 `gold 1M` 之后再补 `Expand 7`，希望用 `16x16` 恐龙棋盘减少骨头轮数。
  - 真实输出 `gold 1M time=7863.17`，随后在 `12x12` 上刷 `64000 Pumpkin`，到 `expand_bones 7 time=13758.78` 才完成。
  - 超时前只推进到 `dinosaurs 2 time=13758.87`，没有进入有效骨头循环；尾部持续南瓜/基础资源采集，被用户观察为“像无限收草”。
  - 结论：金币后补 `Expand 7` 仍被 `64000 Pumpkin` 成本吞掉，不能作为主线；如果要继续处理骨头瓶颈，优先测试更便宜的 `Dinosaurs 4`，而不是继续冲大地图。
- `request_id=202`：
  - 临时把骨头前恐龙科技目标从 `Dinosaurs 3` 提到 `Dinosaurs 4`。
  - 真实输出最终 `reset_stage done time=14979.76`，慢于 `request_id=200` 的 `13409.57`。
  - 结论：`Dinosaurs 4` 的 `432000 Cactus` 成本高于骨头轮数减半收益；正式路线继续停在 `Dinosaurs 3`。
- `request_id=203`：
  - 临时在金币迷宫每 300 次 Treasure 重定位后调用 `harvest_treasure_once()`，尝试补拿第 301 份最终宝箱收益。
  - 真实输出最终 `reset_stage done time=14051.74`，慢于 `request_id=200` 的 `13409.57`。
  - 结论：最终宝箱收益太小，额外寻路 / 收割 / 清场成本不值；已回退。
- `request_id=326`：
  - 参考单迷宫 `dfs_bfs` 的验证结论，临时禁用金币迷宫里的 `move_direct_toward_treasure()`，强制完整图 BFS 寻宝。
  - 真实输出 `gold 1M time=7849.40`，慢于当前正式基线 `request_id=200` 的 `gold 1M time=7349.45`。
  - 中途停止前骨头阶段推进到 `bone=1613120`，停止摘要 `finished=false runs=1 average=215:12.520`；该候选已回退。
  - 结论：单迷宫中直线贪心不占优，但快速重置金币阶段的 `12x12` 迷宫和墙消失收益不同，当前正式路线继续保留直线优先 + BFS 兜底。
- `request_id=329`：
  - 临时把 `STEP2_POWER_TARGET` 降为 `0`，同时新增 `step2_core_unlocks_ready()`，确保 `Speed 5 / Expand 4 / Trees / Watering / Fertilizer / Sunflowers` 仍解锁后才退出 `step2()`。
  - 真实输出 `step2 time=1211.21 power=112.36 size=6`，比正式基线 `step2 time=1312.43 power=1001.82` 早约 `101s`。
  - 但后续 `Megafarm 3 time=4628.30`，明显慢于正式基线 `Megafarm 3 time=3777.95`；该候选已回退。
  - 结论：不能简单取消 `1000 Power` 前置；前期少刷的 `Power` 会让 `step3/step4` 的南瓜、仙人掌和早期金币整体降速，省下的 `101s` 覆盖不了后续损失。
- `request_id=330`：
  - 在 `step3()` 后插入 `try_unlock_early_megafarm()`，用 `6x6` 小迷宫金币先刷到 `2000 gold`，提前解锁 `Megafarm 1`。
  - `farm_pumpkins_until()` 在 `max_drones() > 1`、地图 `>=6x6` 且缺口超过一整图时，改用多无人机按列并行种植、修补死南瓜和收割。
  - 真实输出 `early_megafarm 1 time=1646.66 gold=16 max_drones=2`，随后并行南瓜把 `expand 6 time=1994.53`，明显优于 `request_id=329` 的 `2557.62`。
  - 中段输出 `megafarm 3 time=3523.49`，优于正式基线 `3777.95`；`gold 1M time=7289.27`，略优于正式基线 `7349.45`。
  - 最终输出 `[lb_fastest_reset] finished=true runs=1 average=221:46.199`，同轮 `reset_stage done time=13306.14`，优于 `request_id=200` 的 `13409.57`。
  - 当前保留：早期 `Megafarm 1` + 多无人机南瓜是正收益；它主要压缩 `step4` 和 `Megafarm 3` 之前的节奏，不改变后段金币 / 骨头主结构。
- `request_id=331`：
  - 把 `try_unlock_early_megafarm()` 从只解锁 `Megafarm 1` 扩展到 `Megafarm 2`，继续用 `6x6` 小迷宫刷到第二级所需金币。
  - 真实输出 `early_megafarm 2 time=1765.06 gold=8 max_drones=4`；虽然额外金币投入约 `125s`，但后续 `step4 time=2547.29`，快于 `request_id=330` 的 `2605.77`。
  - 更关键的是 `Megafarm 3 time=3353.48`、`gold 1M time=6769.67`，分别优于 `request_id=330` 的 `3523.49` / `7289.27`。
  - 最终输出 `[lb_fastest_reset] finished=true runs=1 average=216:26.969`，同轮 `reset_stage done time=12986.9`，继续优于 `request_id=330` 的 `13306.14`。
  - 当前保留：早期推到 `Megafarm 2` 是明确正收益；它证明“先用小迷宫买更多无人机，再滚南瓜 / Weird / 金币”这条结构路线成立。
- `request_id=335/336`：
  - 在 `request_id=331` 路线基础上，把 `farm_gold_single_cycle()` 的批次上限从 `600` 提到 `900`，即每次 Weird 预采覆盖 `3` 个 300 次迷宫周期。
  - `request_id=335` 输出 `gold 1M time=6899.86`、`done time=12944.26`、`average=215:44.299`，刷新当前本地最好。
  - `request_id=336` 复跑输出 `gold 1M time=7013.02`、`done time=12997.38`、`average=216:37.399`；两轮差距约 `0.41%`，低于 `10%` 继续运行阈值。
  - 当前保留：在新前期结构下，`900` 批次虽然不稳定压低 `gold 1M`，但两轮均值约 `216:10.849`，仍优于旧 `216:26.969`；正式路线改为 `900`。
- `request_id=337/338`：
  - 临时把 `WEIRD_POWER_FLOOR` 从 `500` 提到 `1500`，目标是在 Weird 阶段顺手保留更多 `Power`，不单独清场补电。
  - `request_id=337` 完整结算，输出 `gold 1M time=6797.53`、`done time=12876.89`、`average=214:36.899`，单轮优于 `request_id=335`。
  - `request_id=338` 复跑在 `120s` 墙钟超时前仍未完成，输出 `gold 1M time=10083.89`，停止摘要 `[lb_fastest_reset] finished=false runs=1 average=241:14.740`。
  - 结论：`1500` 地板单轮有正向波动，但复跑超过 `10%` 退步且未完整结算，不满足两轮稳定采用规则；当前回退到 `WEIRD_POWER_FLOOR=500`，只保留证据，不刷新 `lb_start.py` 本地最好时间。
- `request_id=340`：
  - 临时把 `farm_gold_single_cycle()` 批次上限从 `900` 提到 `1200`，目标是减少金币阶段 Weird 补给批次数。
  - 真实输出 `gold 1M time=7687.93`，慢于 `request_id=335/336` 的 `6899.86` / `7013.02`。
  - 主动停止前摘要 `[lb_fastest_reset] finished=false runs=1 average=223:06.250`，骨头阶段仍未完成。
  - 结论：`1200` 批次会在 Megafarm 3 后过量预采 Weird，把金币阶段拖慢；当前回退并继续保留 `900`。
- `request_id=341/342`：
  - 临时把 `WEIRD_POWER_FLOOR` 从 `500` 提到 `1000`，目标是在 Weird 阶段顺手保留更多 `Power`，但不采用 `1500` 那种会显著拉长补给的地板。
  - `request_id=341` 完整结算，输出 `step2 time=1290.01`、`megafarm 3 time=3511.85`、`gold 1M time=6662.25`、`dinosaurs 3 time=7339.98`、`done time=12746.67`、`average=212:26.699`。
  - `request_id=342` 复跑完整结算，输出 `step2 time=1365.18`、`megafarm 3 time=3548.06`、`gold 1M time=6929.51`、`dinosaurs 3 time=7619.70`、`done time=13006.78`、`average=216:46.799`。
  - 两轮差距约 `2.0%`，低于 `10%` 继续采样阈值；两轮均值约 `214:36.749`，优于 `request_id=335/336` 的两轮均值约 `216:10.849`。
  - 当前保留：`WEIRD_POWER_FLOOR=1000` 是稳定正收益；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:32:26.699`。
- `request_id=349/350`：
  - 在 `WEIRD_POWER_FLOOR=1000` 的稳定路线基础上，把 Weird 阶段顺手补电地板继续提高到 `1250`，仍然不做单独清场补电。
  - `request_id=349` 完整结算，输出 `step2 time=1399.06`、`megafarm 3 time=3635.67`、`gold 1M time=6690.76`、`dinosaurs 3 time=7024.07`、`done time=12556.77`、`average=209:16.799`。
  - `request_id=350` 复跑完整结算，输出 `step2 time=1378.47`、`megafarm 3 time=3635.77`、`gold 1M time=6908.67`、`dinosaurs 3 time=7634.63`、`done time=12945.17`、`average=215:45.199`。
  - 两轮差距约 `3.1%`，低于 `10%` 继续采样阈值；两轮均值约 `212:30.999`，优于 `request_id=341/342` 的两轮均值约 `214:36.749`。
  - 当前保留：`WEIRD_POWER_FLOOR=1250` 是新的稳定最好；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:29:16.799`。
- `request_id=351/352`：
  - 在 `WEIRD_POWER_FLOOR=1250` 的稳定路线基础上，把 Weird 阶段顺手补电地板继续提高到 `1350`，仍然不做单独清场补电。
  - `request_id=351` 完整结算，输出 `early_megafarm 2 time=1791.76`、`expand 6 time=2123.77`、`step4 time=2575.03`、`mazes 3 time=3169.92`、`megafarm 3 time=3421.91`、`gold 1M time=6652.18`、`dinosaurs 3 time=7334.75`、`done time=12693.07`、`average=211:33.099`。
  - `request_id=352` 复跑完整结算，输出 `early_megafarm 2 time=2071.52`、`expand 6 time=2404.12`、`step4 time=2864.79`、`mazes 3 time=3447.02`、`megafarm 3 time=3697.21`、`gold 1M time=6771.83`、`dinosaurs 3 time=7195.97`、`done time=12639.57`、`average=210:39.599`。
  - 两轮差距约 `0.42%`，低于 `10%` 继续采样阈值；两轮均值约 `211:06.349`，优于 `request_id=349/350` 的两轮均值约 `212:30.999`。
  - 当前保留：`WEIRD_POWER_FLOOR=1350` 是新的稳定最好；但当前最好单轮仍是 `request_id=349` 的 `3:29:16.799`，所以不刷新 `lb_start.py` 本地实测时间。
- `request_id=357/358`：
  - 修复 `farm_gold_single_cycle()` 的批次循环边界：当 `remaining_paid_move_count` 刚好降到 `0` 时，不再额外 `clear()`、开迷宫、探图但执行 `0` 次 Treasure。
  - `request_id=357` 完整结算，输出 `step2 time=1330.70`、`early_megafarm 2 time=1916.13`、`step4 time=2720.55`、`mazes 3 time=3309.57`、`megafarm 3 time=3588.80`、`gold 1M time=6661.66`、`dinosaurs 3 time=7375.67`、`done time=12721.99`、`average=212:01.999`。
  - `request_id=358` 完整结算，输出 `step2 time=1305.69`、`early_megafarm 2 time=1764.25`、`step4 time=2558.85`、`mazes 3 time=3199.73`、`megafarm 3 time=3483.86`、`gold 1M time=6490.07`、`dinosaurs 3 time=7182.89`、`done time=12570.11`、`average=209:30.176`。
  - 两轮差距约 `1.19%`，低于 `10%` 继续采样阈值；两轮均值约 `210:46.087`，略优于 `request_id=351/352` 的 `211:06.349`。
  - 当前保留：金币批次 `0` 次额外迷宫确认为真实浪费，应删除；但当前最好单轮仍是 `request_id=349` 的 `3:29:16.799`，所以不刷新 `lb_start.py` 本地实测时间。
- `request_id=359/360`：
  - 修正 `farm_gold_single_cycle()` 的单次 Treasure 金币估算：每次付费重定位收益应为 `maze_size * maze_size * maze_multiplier`，不是只按 `maze_size * maze_size` 计算。
  - 直接效果是 12x12、`Mazes 3` 后的 Weird 目标从约 `10752/每 100 万金币批次` 降为实际需要的 `2736/早期 Megafarm 3`、`43344 + 40272/1M 金币两批`，避免按未乘迷宫倍率的错误值过量预采。
  - `request_id=359` 完整结算，输出 `step2 time=1346.18`、`early_megafarm 2 time=1834.58`、`step4 time=2621.97`、`mazes 3 time=3201.40`、`megafarm 3 time=3414.02`、`gold 1M time=6628.71`、`dinosaurs 3 time=6981.48`、`done time=12209.01`、`average=203:29.064`。
  - `request_id=360` 完整结算，输出 `step2 time=1403.93`、`early_megafarm 2 time=1957.28`、`step4 time=2736.60`、`mazes 3 time=3323.75`、`megafarm 3 time=3550.96`、`gold 1M time=6701.45`、`dinosaurs 3 time=7038.43`、`done time=12414.86`、`average=206:54.899`。
  - 两轮差距约 `1.67%`，低于 `10%` 继续采样阈值；两轮均值约 `205:11.982`，明显优于 `request_id=357/358` 的 `210:46.087`。
  - 当前保留：金币收益估算必须包含 `Mazes` 倍率；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:23:29.064`。
- `request_id=366/367`：
  - 在 `goto_treasure_with_graph()` 中取消每轮开头的整图 `refresh_maze_edges(graph, size)`，只保留直线试探时的局部边更新，以及图路径兜底。
  - 依据：迷宫墙只会消失，不会新增；旧图路径不会因为少刷边而失效，整图刷新会在每次 Treasure 寻路前重复做大量 `can_move()`。
  - `request_id=366` 完整结算，输出 `gold 1M time=6532.89`、`dinosaurs 3 time=6956.69`、`done time=12408.28`、`average=206:48.299`。
  - `request_id=367` 完整结算，输出 `step2 time=1424.01`、`early_megafarm 2 time=2017.73`、`step4 time=2773.68`、`mazes 3 time=3383.00`、`megafarm 3 time=3625.45`、`gold 1M time=6562.11`、`dinosaurs 3 time=6918.32`、`done time=12113.40`、`average=201:53.465`。
  - 两轮差距约 `2.41%`，低于 `10%` 继续采样阈值；两轮均值约 `204:20.882`，优于 `request_id=359/360` 的 `205:11.982`。
  - 当前保留：快速重置金币阶段同样不应每轮刷新整图墙；`lb_start.py` 本地实测时间刷新为当前最好单轮 `3:21:53.465`。
- `request_id=368/369`：
  - 将骨头阶段从固定蛇形全场扫描改为复用 `lb_dinosaur.py` 的“前期追苹果 + 后期安全路径”结构。
  - 依据：反编译 `DinosaurHat.OnMove()` 显示每吃一个苹果后移动成本降低 `3%`；越早吃到苹果，后续每一步都受益。固定蛇形平均吃苹果步数过高，没有利用早期苹果的复利收益。
  - `request_id=368` 完整结算，输出 `gold 1M time=6477.64`、`dinosaurs 3 time=6818.59`、`done time=9881.43`、`average=164:41.493`。
  - `request_id=369` 完整结算，输出 `gold 1M time=6143.85`、`dinosaurs 3 time=6826.62`、`done time=9985.42`、`average=166:25.484`。
  - 两轮差距约 `1.05%`，低于 `10%` 继续采样阈值；两轮均值约 `165:33.489`，明显优于 `request_id=366/367` 的 `204:20.882`。
  - 当前保留：骨头阶段必须利用恐龙榜的前期追苹果结构；`lb_start.py` 本地实测时间刷新为当前最好单轮 `2:44:41.493`。
- `request_id=370`：
  - 只把追苹果阈值从 `size * size / 3` 提到 `size * size / 2`，验证是否更长时间追苹果能继续加速。
  - 结果：完整结算 `gold 1M time=6846.93`、`dinosaurs 3 time=7190.25`、`done time=10275.23`、`average=171:15.290`，慢于 `request_id=368/369`。
  - 结论：阈值 `1/2` 不采用，当前回退并保留 `1/3`；追苹果过久会增加路径绕行和后期风险成本。
- `request_id=345/346`：
  - `request_id=345` 直接把 `STEP2_POWER_TARGET` 改为 `0`，导致 `step2()` 不执行，树等关键科技未解锁，脚本立即运行时报错；这是无效探针。
  - `request_id=346` 修正为“达到 `6x6` 和关键科技后退出 step2，不额外刷 `1000 Power`”。
  - 结果：`step2 time=1085.20`，确实比请求 `341/342` 的 `1290.01/1365.18` 少约 `205~280s`。
  - 但后续 `Megafarm 3 time=4839.46`，明显慢于请求 `341/342` 的 `3511.85/3548.06`。
  - 主动停止前 `weird_parallel` 已到 `time=5896.14`，仍在补 `43,344 Weird_Substance`，说明前置电力和伴随资源不足会被后段 Weird 产线放大偿还。
  - 结论：不采用取消前置电力；`STEP2_POWER_TARGET` 回退并继续保留 `1000`。

## 第二轮结构重写策略校正

- 已落地并保留：
  - `6x6` 小迷宫早期金币推进 `Megafarm 1`：请求 `330` 证明正收益。
  - `6x6` 小迷宫早期金币推进 `Megafarm 2`：请求 `331` 继续证明正收益。
  - `900` 金币批次：请求 `335/336` 两轮差异约 `0.41%`，优于旧批次。
  - `WEIRD_POWER_FLOOR=1350`：请求 `351/352` 两轮差异约 `0.42%`，刷新当前稳定最好。
- 已证伪，不应重复：
  - 取消前置 `1000 Power`：请求 `346` 证明后段 Weird / Megafarm 节奏明显变慢。
  - 早期小迷宫直接推到 `Megafarm 3`：请求 `332` 证明前置金币成本覆盖不了收益。
  - 金币阶段 BFS-only：请求 `326` 证明 `12x12` 金币阶段仍需要直线优先 + BFS 兜底。
  - `Mazes 2` 替代 `Mazes 3`：请求 `198` 证明金币阶段次数增加不值。
  - `Dinosaurs 4`、`Expand 7`、多无人机恐龙：请求 `202/192/201/191` 均已证伪。
- 仍可测的结构变量：
  - 金币阶段的轻量路径缓存：不能做完整全对路径表，应只缓存首步或最近 BFS 结果，避免 `Maze Single` 请求 `325` 的 `table_time` 问题在 `12x12` 上放大。
  - 金币阶段的 Treasure 延迟利用：当前直线优先能吃到墙消失收益，但仍需验证等待期间是否能做低成本刷新，而不是空等或重建全图。
  - Weird 产线的 companion 布局：`Polyculture 1` 与跨列补 companion 已是正收益，后续只测更低调度成本的布局，不再测试南瓜专职 Weird。
- `request_id=204`：
  - 回退 `Expand 7`、`Dinosaurs 4`、最终宝箱补收后，用当前保留版本复测。
  - 真实 `output.txt` 有完整 `reset_stage done time=14018.42`；`run_real_game_script.py` 本轮没有抓到 `game_output` 正文，但文件尾部证明脚本完成且状态已回到 `idle`。
  - 结论：当前代码没有残留失败候选；单轮随机波动下仍慢于 `request_id=200`，所以历史最佳证据继续看 `request_id=200`，代码结构保持同一版。
- `request_id=190`：
  - 当前 Expand 6 路线短跑到 `gold 1M time=10437.83`，随后骨头阶段在 75 秒墙钟窗口推进到 `bone=1371152` 后超时。
  - 这轮确认当前短窗口未完成的主因已经转向骨头循环；金币阶段仍是大段耗时，但不是本轮停止点。
- `request_id=191`：
  - 用 `gamesave/simulate.py` + `gamesave/test.py` 测多无人机恐龙，单机 `12x12` 一轮为 `bone_delta=80656`、`bone_per_1000tick=116.11`。
  - 多机尝试直接报错：`恐龙帽只有一个，而且已在使用中。无法将其用于第二架无人机上。`
  - 结论：骨头阶段不能简单用多无人机并行恐龙；除非找到非恐龙帽的骨头路线，否则正式脚本继续单机恐龙。
- `request_id=192`：
  - 把 `step4()` 临时改为推进到 `Expand 7`，验证更大棋盘是否能抵消南瓜成本。
  - 结果到 `time=8649.02` 才刚 `expand 7`，期间 `64000` 南瓜成本吞掉大量时间并触发一次 `Entities.Carrot` 缺材料警告。
  - 对比 Expand 6 路线同窗口已进入金币 / 骨头阶段，Expand 7 明显退步；已回退到 `Expand 6`。
- `request_id=193` / `request_id=194`：
  - 尝试把骨头阶段改成“一次预留剩余轮数苹果成本后，连续跑完多轮恐龙”，减少重复换帽和循环检查。
  - 两次短跑都只输出到 `bone_prep cycles=25`，在 `125s` 请求窗口内没有产生 `bones_batch` 或完成输出，无法证明变快，且可观测性差。
  - 结论：该改法已回退；骨头阶段继续保持每轮恐龙后输出进度，便于短窗口动态判断。

## 失败对照

- 文件里已经保留了一段被注释掉的金币循环
- 原因很明确：会因为奇异物质不足而死循环
- 这说明 `fastest_reset` 里不能把“资源前提不满足的阶段跳转”直接当成理所当然
- “满扩张后再进后续阶段”
  - 真实短窗口显示这个方向会被 `512,000 / 4,100,000 pumpkin` 吞掉
  - 当前不再作为默认路线，只保留为失败对照
- “一开始就直接做科技取舍最优解”
  - 这条线当前不适合当第一版目标
  - 因为在还没有一条完整可跑通路线之前，先卷科技不升满只会把问题空间放大得过早
- “当前这版多无人机金币”
  - `request_id=171` 证明现有实现到 `time=14005.09` 只有 `gold=230448`
  - 不是因为真实墙钟慢，而是游戏内 `time=` 与资源增量都落后；除非重写为更少共享宝箱寻路 / 更少奇异物质补给，否则不作为默认路线
- “苹果成本按恐龙等级再乘一次”
  - `request_id=169` 能完成，但最终剩余约 `92848 cactus`
  - 真实每轮 D3 骨头只消耗约 `1144 cactus` 的苹果材料，额外乘 `4` 是过量预留
- “奇异物质阶段跳过自动草收割直接覆种树”
  - `request_id=174` 总时间退到 `16725.91`
  - 当前保留先收割再种树的实现
- “主动清场补 `Power`”
  - `request_id=177` 补到 `3000 Power` 净耗约 `2195` 游戏秒，金币阶段仍更慢
  - `request_id=179` 把前期目标提到 `3000 Power` 后总时间退到 `22523.38`
  - 当前结论：`Power` 归零是事实，但主动补电成本高于后段收益；后续只能考虑不触发额外草/胡萝卜链的顺手补电
- “专门用南瓜刷 `Weird_Substance`”
  - `request_id=185/186` 显示完整 `6x6/8x8` 感染南瓜田可以产出大量奇异物质，但单位 tick 效率只有树的约三成以内
  - 当前不把南瓜作为专职奇异物质来源；更值得继续测试的是批量伴生树，而不是继续优化南瓜 Weird 路线
  - 2026-04-25 补充结论：南瓜 Weird 路线到此先停止投入；下一轮只用 `gamesave/simulate.py` / `gamesave/test.py` 做批量伴生树 probe，确认“批量补 companion 后统一施肥收割”能否压过普通感染树，再决定是否改正式 `lb_fastest_reset.py`
- “批量伴生树刷 `Weird_Substance`”
  - `request_id=187/188/189` 只覆盖 `Polyculture 1`、`Trees 10`，原先“批量伴生树整体排除”的结论过强
  - `request_id=195` 显示 `Polyculture` 等级本身是主收益曲线：`Polyculture 3` 的普通树 Weird 效率约为 `Polyculture 1` 的 `3.4x`，`Polyculture 5` 约为 `13.1x`
  - 批量预感染伴生树在高伴生等级上还会进一步抬高收益：小图 `8x8/16 株` 在 `Polyculture 3/5` 分别约 `+14.8%` / `+19.4%`
  - `request_id=196/197` 已确认 `Polyculture 1` 可用 `3000 Pumpkin` 提前接入，并把完成时间压到 `14521.64`
  - 当前结论：`Polyculture 1` 保留为正式路线；高等级 `Polyculture` 虽然收益曲线很强，但 `2+` 级需要骨头，暂时不能服务前置 Weird / 金币阶段
- “多无人机恐龙骨头”
  - `request_id=191` 真实报错 `恐龙帽只有一个`，不能把恐龙帽同时给第二架无人机
  - 当前结论：骨头阶段不能按“无人机数 x N”直接并行
- “`Dinosaurs 4`”
  - `request_id=202` 完成时间退到 `14979.76`
  - 当前结论：`432000 Cactus` 成本不值，继续保留 `Dinosaurs 3`
- “Expand 7 换更大恐龙棋盘”
  - `request_id=192` 显示 `64000` 南瓜成本到 `time=8649.02` 才完成，远慢于 Expand 6 路线进入金币 / 骨头阶段
  - `request_id=201` 改成金币后再补 `Expand 7`，仍到 `time=13758.78` 才完成扩张，随后还没形成有效骨头收益
  - 当前结论：Expand 7 仍不回到默认路线；最大扩张更不应直接测试，除非先把南瓜收益曲线整体改掉
- “只升到 `Mazes 2`”
  - `request_id=198` 在 `Polyculture 1` 正式路线基础上完成时间退到 `17331.81`
  - 当前结论：`Mazes 3` 仍是金币阶段默认配置，不再把 `Mazes 2` 当成当前主线
- “金币迷宫 300 次后补收最终宝箱”
  - `request_id=203` 完成时间退到 `14051.74`
  - 当前结论：不补收最终宝箱，继续靠重定位金币推进
- “按迷宫等级倍率下调金币重定位次数估算”
  - `request_id=333` 先误把单次金币收益估成 `size * size * substance`，真实输出立刻证明早期 `6x6 / Mazes 1` 每次 Treasure 只涨 `36` 金币，而不是 `216`，该轮已手动停止。
  - `request_id=334` 改为 `size * size * 2^(Mazes-1)` 后完整结算，`gold 1M time=7378.28`、`done time=13347.51`、`average=222:27.573`，慢于当前最佳 `216:26.969`。
  - 当前结论：金币次数估算不能只看理论每次金币；较小 Weird 预采会增加拆批和重复清迷宫 / 探图成本，正式路线继续保留原来的 `size * size` 估算与 `600` 上限。
- “早期小迷宫直接推到 `Megafarm 3`”
  - `request_id=332` 临时把 `try_unlock_early_megafarm()` 从目标 `Megafarm 2` 提到 `Megafarm 3`。
  - 真实输出 `early_megafarm 3 time=2980.87`，但 `step4 time=3651.98`，明显慢于 `request_id=331` 的 `step4 time=2547.29`。
  - 后续即使省掉一次 `Megafarm 3` 升级，也无法覆盖前置 `6x6` 小迷宫刷 `32000 gold` 的成本；该请求已在证伪后停止并回退。
  - 当前结论：早期巨大农场的正收益上限暂定为 `Megafarm 2`；第三级必须等地图扩大、迷宫和资源结构更强后再做。
- “快速重置金币阶段禁用直线贪心”
  - `request_id=326` 的 `gold 1M time=7849.40` 慢于正式基线 `7349.45`
  - 当前结论：`12x12` 快速重置金币阶段继续保留直线优先；单迷宫的 BFS-only 结论不能直接迁移
- “单次帽子状态连续跑多轮恐龙”
  - `request_id=193/194` 没有在 `125s` 请求窗口内形成可用进度证据，且会让骨头阶段长时间无输出
  - 当前结论：不采用，保留每轮 `bones` 日志
- “外部 `Save0/fastest_reset.py` 复合候选”
  - 2026-04-25 读取当前文件后，将 `move_utils` / `math` / `fastest_reset_action` / `pumpkin3` 内联到既有 `lb_fastest_reset.py`，没有向存档新增依赖文件
  - 请求 `263` 能推进到阶段一完成，输出 `17 分 28.8 秒 完成了阶段一`，随后因内联 `back` 名称冲突在迷宫探图报错
  - 修正内联变量冲突后请求 `264` 仍 30 秒无完成轮，资源停在 `hay=171 wood=406 carrot=268 weird_substance=100 gold=7`
  - 2026-04-26 重新确认用户所指是存档根目录 `Save0/fastest_reset.py`，不是外部 `lb_fastest_reset.py` 包装入口
  - 请求 `280` 暴露后半段卡点：`item_snapshot` 中 `hay` 持续增长到 `682642`，`wood=429 carrot=50 pumpkin=80 cactus=0`，根因是补草/补木后地块残留草或灌木，胡萝卜没有覆盖种下
  - 修复 `farm_hay_until()` / `farm_wood_until()` / `farm_carrots_until()` 后，请求 `281` 能脱离割草卡点并推进到 `gold=345927`，但删掉外部 phase2 尾段后节奏偏慢
  - 恢复 `Save0/fastest_reset.py` 的 phase2 尾段，并加 `5000` 游戏秒保护；请求 `282` 在 `90s` 窗口内回到 `Expand 6 / Pumpkins 2 / 12x12` 节奏，`gold 345927 time=7578.41`
  - 请求 `283` 完整跑到 `reset_stage save0_fastreset_done time=22484.01`，但旧轮询仍因 `numLeaderboardRuns` 被游戏清零误判为 `leaderboard finished without completed runs`
  - 修改模组为 Harmony 捕获 `LeaderboardManager.StopLeaderboardRun(...)` 后，请求 `284` 完整结算：`[lb_fastest_reset] finished=true runs=1 average=376:11.397`，同轮 `reset_stage save0_fastreset_done time=22571.33`
  - 当前结论：外部 `Save0/fastest_reset.py` 已作为候选迁入并跑通；它比当前正式 `13409.57` 慢，不应替代正式最优路线，但 phase2 尾段“先 Megafarm，再 12x12 + Pumpkins 2”的节奏可继续作为前期参考

## 下一步优化方向

- 当前路线已经能完成一轮，下一步应围绕真实成绩继续压缩阶段耗时，而不是再追求“能跑通”。
- 必须补证据的关键点：
  - 每个解锁门槛前后的资源短板
  - 迷宫 / 金币 / 无人机阶段是否真的比继续滚基础资源更值
  - `step4()` / `step5()` 最短完成条件
- 下一轮优先级：
  - 骨头阶段现在仍耗时很长，但 `Expand 7` 和 `Dinosaurs 4` 都已被新证据排除；后续只能找更便宜的仙人掌准备方式或更短恐龙行走路径
  - 继续压缩 `Megafarm 3 -> gold 1M`，这是当前最大单段瓶颈
  - 只有重写宝箱分配 / 寻路 / 奇异物质补给后，才重新开启多无人机金币
  - 若继续处理 `Power`，只能在已有资源循环里搭便车；不要再单独清场种太阳花或抬高 `step2` 目标
  - 奇异物质来源已排除南瓜专职路线；`Polyculture 1` 已接入正式路线，跨列补 companion 已验证正收益，后续只在出现新 companion 排布策略时继续改 Weird 产线
  - `Dinosaurs 3` 当前优于 `Dinosaurs 2`，多无人机恐龙已被帽子唯一性排除，`Dinosaurs 4` 暂不回到默认路线，除非先找到更便宜的仙人掌准备方式

## 候选策略方向（猜测 / 待验证）

### 方向 1：第一版满科技基线路线

- 核心思路：先不碰“科技不升满”的取舍，按你给出的方向做一条完整基线：
  - 所有科技至少 `1` 级
  - 无人机速度、农场大小、无人机数目升满
  - 最后解锁 `leaderboard`
- 主瓶颈：当前路线已经能跑通，但不是满科技路线；继续升后几级科技会明显拖慢
- 可能更强的原因：先有完整可跑通路线，后续才有可靠基线可以做科技取舍优化
- 优先探针：
  - 这条满科技路线的真实总时间
  - 时间大头落在解锁、资源积累，还是最后排行榜门槛

### 方向 2：满科技基线完成后，再做“科技不升满”剪枝

- 核心思路：先记住“榜前玩家大概率不会全升满”，但把它放到第一版完成之后处理
- 主瓶颈：如果现在就开始同时优化流程和科技等级，问题空间会失控
- 可能更强的原因：有了满科技基线以后，才能逐项判断“哪个满级其实不值”
- 优先探针：
  - 把某一类科技从满级降到次满级后，总时间变化多少
  - 哪个科技的“最后几级”回报最差

### 方向 3：围绕阶段切换而不是代码结构做优化

- 核心思路：把思考重点放在“什么时候切到下一阶段”，而不是先在代码结构上做花样优化
- 主瓶颈：当前路线真正的损失很可能来自切阶段太早或太晚
- 可能更强的原因：对这榜来说，流程节奏的收益远大于局部代码层面的微修
- 优先探针：
  - `step1 -> step2 -> step3` 的切换时机是否已经合理
  - 满科技路线里，哪一段资源积累最可能被压缩

- `request_id=371`：
  - 临时新增金币迷宫首步查表：在 `build_maze_graph()` 后构建 `next_step[source][target]`，导航保留直线优先，失败时用首步表替代每次 BFS。
  - 真实输出在早期 `6x6` 金币阶段只到 `reset_stage gold_table time=1774.03 cost=4.26 size=6`，随后 `LogOutput.log` 中 `real_elapsed=9.0` 到 `31.0` 期间 `gold=0`、`weird_substance=1085` 基本不变，只自动增长水和肥料。
  - 该状态说明脚本卡在首步表导航循环内，没有形成 Treasure 使用；已写入 `stop_requested`，结果为 `oracle_error request_id=371 leaderboard cancelled: fastest_reset`。
  - 结论：首步查表候选不采用。原因不是表构建耗时（`6x6` 只耗 `4.26s` 游戏时间），而是固定首步表替换动态 BFS 后存在卡死风险；正式路线继续使用直线优先 + 动态 BFS 兜底。

- `request_id=372`：
  - 临时新增 `WEIRD_COMPANION_MAX_DISTANCE = 6`，对 Weird 阶段树伴生只保留跨边界曼哈顿距离 `<= 6` 的补位，目标是减少远距离 `goto_wrap()` 往返。
  - 真实输出 `step4 time=2811.81`、`mazes 3 time=3394.23`、`megafarm 3 time=3635.82`、`gold 1M time=6999.47`、`dinosaurs 3 time=7350.58`。
  - 对比当前最好请求 `368/369` 的 `gold 1M time=6477.64 / 6143.85`，阈值 6 明显拖慢金币阶段；主动停止前骨头阶段也落后，摘要为 `finished=false runs=1 average=155:21.292`。
  - 结论：伴生远距离补位不能简单按距离阈值裁剪。跨列伴生虽然有移动成本，但对 Weird / Power / 后续金币的综合收益仍覆盖了成本；当前回退为不限距离补 companion。

- `request_id=373`：
  - 临时禁用 Weird 阶段树施肥：新增 `WEIRD_FERTILIZER_ENABLED = False`，让 `farm_weird_substance_worker()` 不再调用 `use_item(Items.Fertilizer)`。
  - 真实输出只推进到 `step3 time=1736.87`、`gold time=1768.39`、`early_megafarm 1 time=1768.43`、`weird_parallel_start time=1768.51 weird=685 target=1338`。
  - 随后 `LogOutput.log` 中 `real_elapsed=9.0` 到 `29.0` 期间 `weird_substance=685`、`gold=16` 不再增长，只看到 `hay/wood/water/fertilizer` 持续增加，说明不施肥会让早期 Weird 产线卡住，连 `Megafarm 2` 都无法继续。
  - 结论：Weird 阶段施肥不是边际优化，而是当前早期树产线成立的必要加速；不采用禁用施肥，正式路线继续施肥。

- `request_id=374`：
  - 临时把 `step3()` 的 Weird 目标从 `2000` 降到 `1000`，验证是否只刷够 `Mazes 1` 就更快进入早期金币 / Megafarm。
  - 真实输出 `step2 time=1327.45`、`step3 time=1741.55 weird=8`、`early_megafarm 1 time=1815.54`、`early_megafarm 2 time=2076.65`、`step4 time=2880.09`、`mazes 3 time=3487.58`、`megafarm 3 time=3706.03`。
  - 对比近邻正式路线的早期阶段（例如请求 `371` 前一轮正式输出 `step3 time=1892.87`、`early_megafarm 2 time=2025.98`，以及请求 `370` 的 `step4 time=2795.85`），降低 step3 目标虽然让 `step3` 提前，但会把 Weird 缺口转移到 `try_unlock_early_megafarm()` 和后续阶段，`Megafarm 3` 前已经落后。
  - 结论：`step3` 的额外 Weird 不是纯浪费，它支撑早期 `Megafarm 2` 和后续节奏；不采用 `1000` 目标，回退到 `2000`。

- `request_id=375`：
  - 临时在 `step5()` 的 `Megafarm 3` 后追加 `upgrade_megafarm_for_final_push(4)`，验证中途花 `128000` 金币换 `16` 台无人机是否能加速后续 Weird 产线。
  - 真实输出 `megafarm 3 time=3600.27`、`gold time=4139.41 gold=128136 target=128000`、`megafarm 4 time=4139.48 gold=136 max_drones=16`，随后 `weird_parallel_start time=4139.63 weird=46 target=43344 drones=12`。
  - 结果 `gold 1M time=8362.31`、`dinosaurs 3 time=9043.48`、`done time=12228.41`，最终 `average=203:48.478`。对比当前最好请求 `368/369` 的 `gold 1M time=6477.64 / 6143.85` 和 `done time=9881.43 / 9985.42`，该路线明显退步。
  - 结论：`Megafarm 4` 的额外金币导航成本无法被 Weird 并行收益抵消；且实际 Weird worker 只显示 `drones=12`，没有吃满 `max_drones=16`。不采用中途升级 `Megafarm 4`，正式路线保持 `Megafarm 3` 后直接冲 `1M Gold`。

- `request_id=376/377`：
  - 临时加入 `dino_hat_apple_plant` 探针，验证 S4“单次换帽批量恐龙”的关键前提：戴 `Hats.Dinosaur_Hat` 时能否主动 `plant(Entities.Apple)`。
  - `request_id=376` 输出 `reset_probe dino_hat_apple_plant time=6722.56 can_pay=True before=Entities.Grass planted=False after=Entities.Apple cactus=16616`。该探针不充分，因为切换恐龙帽会在脚下自动生成苹果，`after=Entities.Apple` 不能证明 `plant()` 生效。
  - 修正后的 `request_id=377` 在切帽后先记录脚下自动苹果，再 `move(East)` 到邻格，收割后尝试主动种苹果。真实输出为 `reset_probe dino_hat_apple_plant time=7109.17 can_pay=True auto=Entities.Apple before=Entities.Grass after_harvest=Entities.Grass planted=False after=Entities.Grass cactus=16608`。
  - 结论：恐龙帽下即使材料足够，也不能主动种苹果；S4“保持恐龙帽、边跑边补苹果、减少换帽次数”的路线不成立。正式脚本回滚探针代码，骨头阶段继续使用每轮补苹果后切恐龙帽的现有路线。

- `request_id=378`：
  - 临时把 `STEP2_POWER_TARGET` 从 `1000` 降到 `200`，不改 `step2()` 的解锁逻辑，验证第三轮 S1 的“少刷 Power 是否能压缩前期”。
  - 真实输出 `step2 time=1320.03 power=203.04`、`step3 time=1761.30 weird=1043`、`early_megafarm 2 time=2064.53`、`expand 6 time=2475.18`、`step4 time=2904.60`、`mazes 3 time=3525.72`、`megafarm 3 time=3763.51`。
  - 对比 `request_id=377` 近邻正式路线的 `early_megafarm 2 time=1867.73`、`expand 6 time=2194.23`、`step4 time=2622.32`、`mazes 3 time=3216.66`、`megafarm 3 time=3460.74`，`200 Power` 路线在进入正式金币前已经落后约 `200~300s`。
  - 结论：`STEP2_POWER_TARGET=200` 不采用。Power 本身虽然会在后段归零，但前期多刷到 `1000` 对早期 Weird / 南瓜 / 仙人掌节奏有实际收益；正式脚本回退到 `STEP2_POWER_TARGET=1000`。

- `request_id=379/380`：
  - 临时让 `main()` 只跑 `fr_phase1()`，验证 S2 的早期确定性路线结束状态。`request_id=379` 因没有中间输出，只能从模组 `item_snapshot` 看到大约 `game_time=798` 时仍在推进，无法定位阶段；因此 `request_id=380` 追加 `s2_phase1_checkpoint` 输出后复跑。
  - `request_id=380` 最终输出 `reset_probe s2_phase1 time=1008.75 size=6 hay=163 wood=749 carrot=392 pumpkin=0 gold=0 weird=681 power=0 speed=5 expand=4 mazes=1 pumpkins=1 fertilizer=1 sunflowers=1 unlocks={Unlocks.Speed:5,Unlocks.Expand:4,Unlocks.Plant:1,Unlocks.Watering:3,Unlocks.Carrots:3,Unlocks.Trees:3,Unlocks.Grass:2,Unlocks.Fertilizer:1,Unlocks.Sunflowers:1,Unlocks.Pumpkins:1,Unlocks.Mazes:1}`。
  - 对比当前正式路线近邻 `request_id=376` 的 `step2 time=1309.41`、`step3 time=1589.31 weird=1032`、`early_megafarm 2 time=1736.87`，`fr_phase1` 以更早时间拿到 `Speed 5 / Expand 4 / Mazes 1 / Pumpkins 1`，但代价是没有 Power、Weird 只有 `681`，且尚未解锁 `Megafarm`。
  - 结论：`fr_phase1` 本身值得继续作为前期替代候选；下一步不直接替换全路线，而是验证 `fr_phase1 -> try_unlock_early_megafarm() -> step4() -> Megafarm 3` 的桥接时间是否优于正式路线的 `megafarm 3 time=3288.64~3460.74`。

- `request_id=381`：
  - 临时让 `main()` 执行 `fr_phase1() -> try_unlock_early_megafarm() -> step4() -> upgrade_mazes_for_gold() -> upgrade_megafarm_for_final_push(3)`，验证 S2 早期路线能否顺利桥接到正式金币阶段。
  - 真实输出 `early_megafarm 1 time=1074.45`、`early_megafarm 2 time=1717.70`、`s2_bridge_step4 time=3008.23`、`mazes 3 time=3617.62`、`s2_bridge_megafarm3 time=3833.84 max_drones=8`。
  - 对比近邻正式路线 `request_id=376/377` 的 `step4 time=2476.56 / 2622.32`、`megafarm 3 time=3288.64 / 3460.74`，桥接路线到 `Megafarm 3` 已经慢 `373~545s`；继续跑完整 `1M Gold` 没有采用价值。
  - 结论：`fr_phase1` 单看早期解锁更快，但缺 Power 与 Weird 储备会把成本转移到后续早期金币、南瓜和仙人掌阶段；不采用 `fr_phase1` 桥接正式路线。正式脚本回滚为 `main_current_route()`。

- `request_id=382`：
  - 临时跳过 `Polyculture 1`，把 `step4()` 中的南瓜目标从 `8000` 降到 `5000`，只解锁 `Cactus` 后进入 `Mazes 3 / Megafarm 3 / Gold`，验证科技最小化是否能抵消 Weird 伴生损失。
  - 真实输出 `skip_polyculture time=2323.11`、`step4 time=2453.59`、`mazes 3 time=3026.58`、`megafarm 3 time=3258.46`，前半段明显快于近邻正式路线。
  - 但无 `Polyculture` 后 Weird 产线退化：`weird_parallel_start time=3258.61 target=43344` 到 `weird_parallel time=5508.84 weird=43378`，单次大 Weird 预备耗约 `2250s`；随后 `gold time=7197.75 gold=518664 target=1000000`，已经慢于当前最好 `gold 1M time=6143.85~6477.64` 且只完成约一半金币。
  - 结论：`Polyculture 1` 不能跳过。它的 `3000` 南瓜成本能被 Weird 伴生产线收益覆盖；正式路线恢复 `farm_pumpkins_until(8000) -> unlock(Cactus) -> unlock(Polyculture)`。

- `request_id=383`：
  - 临时把 `farm_gold_single_cycle()` 的 `batch_paid_move_count` 上限从 `900` 提高到 `1800`，验证 `1M Gold` 阶段一次性预备更多 Weird、连续跑多个迷宫 cycle 是否能减少产线重建成本。
  - 真实输出 `step2 time=1384.54`、`step3 time=1798.33`、`early_megafarm 2 time=1956.24`、`polyculture1 time=2627.51`、`step4 time=2746.88`、`mazes 3 time=3355.62`、`megafarm 3 time=3572.59`。
  - 金币阶段输出 `weird_parallel_start target=83616 time=3572.74`、`weird_parallel time=5809.08 weird=83706`、`gold 1M time=7759.57`、`dinosaurs 3 time=8436.09`；后续手动停止时已有 `average=154:49.063`，并由模组记录 `oracle_error request_id=383 leaderboard cancelled`。
  - 对比当前最好 `gold 1M time=6143.85~6477.64`，一次性大 Weird 预备导致金币阶段明显变慢。
  - 结论：`batch_paid_move_count` 上限不提高到 `1800`；正式路线保持 `900`，分批 Weird 预备比一次性大批量更稳。

- `request_id=384`：
  - 临时新增 `SKIP_GRASS_UNLOCK_PROBE = True`，只跳过正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Grass)`，验证省掉 `Grass` 解锁成本是否能覆盖后续 Hay 产量损失。
  - 真实输出 `step3 time=1785.53`、`early_megafarm 2 time=1970.47`、`expand 6 time=2408.56`、`polyculture 1 time=2875.06`、`step4 time=2996.53`、`mazes 3 time=3592.67`。
  - 对比近邻正式路线 `request_id=383` 的 `step4 time=2746.88`、`mazes 3 time=3355.62`，以及 `request_id=377` 的 `step4 time=2622.32`、`mazes 3 time=3216.66`，跳过 `Grass` 在进入金币前已慢 `~237s` 以上。
  - 结论：`Grass` 不能跳过。虽然其直接成本不高，但后续南瓜 / 胡萝卜补料阶段出现额外 `carrots` 补给，Hay 产量下降会拖慢中段节奏；正式路线恢复 `unlock(Unlocks.Grass)`。

- `request_id=385`：
  - 临时新增 `WATERING_UNLOCK_CAP_PROBE = 3`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Watering)`，验证少升 Watering 是否能节省前期 Wood 投入。
  - 真实输出 `early_megafarm 2 time=1951.83`、`step4 time=2739.88`、`mazes 3 time=3323.21`、`megafarm 3 time=3568.90`、`gold 1M time=6233.89`、`dinosaurs 3 time=6804.14`、`done time=10031.76`、`average=167:11.799`。
  - 对比当前正式最好请求 `368/369` 的 `done time=9881.43 / 9985.42` 与 `average=164:41.493 / 166:25.484`，Watering 上限 `3` 虽然让金币阶段单轮接近最好，但总完成时间退步。
  - 结论：不限制 Watering 到 `3`。当前路线继续允许 `step2()` / `step3()` 自然升级 Watering；该投入对后续完整路线仍有净收益。

- `request_id=386/387`：
  - 临时新增 `FERTILIZER_UNLOCK_CAP_PROBE = 3`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Fertilizer)`，保留所有 `use_item(Items.Fertilizer)` 行为，避免重复 W4“禁用施肥”探针。
  - `request_id=386` 完整结算，输出 `step4 time=2774.12`、`mazes 3 time=3363.93`、`megafarm 3 time=3585.26`、`done time=9897.70`、`average=164:57.699`。
  - `request_id=387` 完整结算，输出 `step4 time=2704.41`、`mazes 3 time=3303.46`、`megafarm 3 time=3545.05`、`gold 1M time=6501.29`、`dinosaurs 3 time=6848.27`、`done time=9811.38`、`average=163:31.378`。
  - 两轮平均约 `164:14.539`，轮次差异约 `0.88%`，低于 `10%` 稳定阈值；对比当前正式最好 `request_id=368/369` 两轮平均约 `165:33.489`，该路线稳定刷新。
  - 结论：采用 Fertilizer 解锁上限 `3`。正式脚本使用 `FERTILIZER_UNLOCK_CAP = 3`，同时更新 `lb_start.py` 的 Fastest Reset 本地最好时间为 `2:43:31.378`。

- `request_id=388`：
  - 临时把已采用的 `FERTILIZER_UNLOCK_CAP = 3` 降到 `2`，验证是否还能继续减少前期 Wood 投入。
  - 真实输出 `step3 time=1836.91`、`early_megafarm 2 time=2067.64`、`polyculture 1 time=2739.94`、`step4 time=2866.61`、`mazes 3 time=3450.48`、`megafarm 3 time=3686.53`。
  - 对比 `request_id=386/387` 的 `step4 time=2774.12 / 2704.41`、`mazes 3 time=3363.93 / 3303.46`、`megafarm 3 time=3585.26 / 3545.05`，上限 `2` 在进入正式金币前已稳定慢 `~100s` 以上。
  - 结论：不采用 Fertilizer 上限 `2`；正式路线回到 `FERTILIZER_UNLOCK_CAP = 3`。

- `request_id=389`：
  - 临时把已采用的 `FERTILIZER_UNLOCK_CAP = 3` 提到 `4`，验证更多肥料等级是否能用前期加速覆盖额外 Wood 投入。
  - 真实输出 `step4 time=2666.57`、`mazes 3 time=3254.79`、`megafarm 3 time=3445.37`、`gold 1M time=6749.49`、`dinosaurs 3 time=7093.82`、`done time=10166.44`、`average=169:26.499`。
  - 对比已采用 `request_id=386/387` 的 `done time=9897.70 / 9811.38`、`average=164:57.699 / 163:31.378`，上限 `4` 虽然让 `step4/mazes 3/megafarm 3` 提前，但金币和骨头阶段回吐收益，完整结算慢约 `269s~355s`。
  - 结论：不采用 Fertilizer 上限 `4`；正式路线保持 `FERTILIZER_UNLOCK_CAP = 3`。

- `request_id=390`：
  - 临时新增 `WATERING_UNLOCK_CAP = 4`，只限制正式路线 `step2()` / `step3()` 中的 `unlock(Unlocks.Watering)`，验证自然升级 Watering 是否仍存在过度 Wood 投入。
  - 真实输出 `step4 time=2722.84`、`mazes 3 time=3328.55`、`megafarm 3 time=3546.10`、`gold 1M time=6636.10`、`dinosaurs 3 time=6993.16`、`done time=9983.75`、`average=166:23.749`。
  - 对比已采用 `request_id=386/387` 的 `done time=9897.70 / 9811.38`、`average=164:57.699 / 163:31.378`，Watering 上限 `4` 首轮完整结算已慢于两轮正式基线，也慢于最佳单轮 `request_id=387`。
  - 结论：不采用 Watering 上限 `4`；正式路线继续自然升级 Watering，只保留 `FERTILIZER_UNLOCK_CAP = 3`。

## 2026-04-26 暂停点与后续方向

- 当前正式基线：保留 `FERTILIZER_UNLOCK_CAP = 3`，Watering 自然升级，`lb_start.py` 的本地最好时间保持 `2:43:31.378`。`request_id=386/387` 两轮平均约 `164:14.539`，轮次差异约 `0.88%`，可作为后续 A/B 对照。
- 暂停原因：`Watering 3/4`、`Fertilizer 2/4`、`STEP2_POWER_TARGET=200`、`step3 Weird 1000`、`Megafarm 4`、`Polyculture/Grass` 跳过、金币大批量、恐龙批量换帽等单变量都已证伪；继续在同类科技上限小变量里试探，边际收益很低。
- 后续优先方向 1：重写骨头阶段的苹果补给 / 仙人掌补给节奏。当前 `request_id=390` 从 `dinosaurs 3 time=6993.16` 到 `done time=9983.75` 仍约 `2990s`，且每轮都有 `apple_prep_start -> bone_prep -> bones`，应优先分析 `farm_bones_until()` 与 `farm_dinosaur_apple_cost()`，目标是减少每轮补给和切帽成本，而不是再调 `Dinosaurs` 等级。
- 后续优先方向 2：重新拆解金币阶段 Weird 产线。当前正式路线金币阶段仍在 `gold 1M time=6501.29~6636.10` 左右；`batch_paid_move_count=1800` 和 `Megafarm 4` 已证伪，但可以尝试按 `item_snapshot` 计算每 1000 游戏秒的 Weird 产出，先确认瓶颈是树成熟、伴生兑现、移动还是 Power 归零，再决定是否改 `farm_gold_single_cycle()` 或 Weird worker 布局。
- 后续优先方向 3：做阶段预算逆推，不再只比较完整平均值。下一轮探针应在 `step2/step3/step4/mazes3/megafarm3/gold1M/dinosaurs3/done` 全部输出后，计算每段耗时和相对基线差值；只有某段至少缩短 `>100s` 且后续不明显回吐，才值得完整跑完。
- 后续优先方向 4：若继续做科技最小化，只测“大结构”而不是等级微调。候选是 `Expand 5` 完整路线、`Mazes 2/3` 与更低棋盘尺寸联动、或前期 `fr_phase1` 的局部片段重用；不要重复已证伪的单独 `fr_phase1 -> step4` 桥接。
- 下一次执行规则：先写一个明确单变量探针，静态验证并同步后用 `--request-only` 投递；运行中只轮询三路输出，不前台长等。首轮若明显慢于 `164:14.539` 基线，立即回滚并只记录结论；只有首轮刷新或接近刷新，才按两轮稳定规则复跑。


## 提前 Polyculture 2 的本地基线

方案在 `step4()` 后、金币大生产前以最小骨头批次购买 `Polyculture 2`，保留 `Mazes 3`、`Megafarm 3` 和最终排行榜目标。科技快照确认升级需要 `10000 Bone`，父科技为 `Pumpkins`。回本要求是骨头、升级和补给投入小于 Weird 产线节省；有效吞吐倍率必须测量，不能直接假定为两倍。

场景为 `{"preset":"reset"}`，seed 为 `1`；API 上限 `500000`，脚本检查点上限 `5000000`，墙钟上限 `25s`。脚本 SHA256 为 `270c7b99a2762993fe3b2a91515085f318831ec64685eefe373a029808f335ba`。报告 `.codex/leaderboard-sol/reset/baseline-seed1.json` 记录模型预计 `26.215s` 时在第 `591` 行停止，错误为 `ValueError: 尚未解锁：Entities.Bush`，没有完成任何阶段。停止时 `Hay=50`，`Speed/Expand/Plant/Loops` 均为零。

首个可静态定位的分歧在 `step1()` 的 Speed 解锁：其父科技是 `loops`，裸 reset 预设却将其设为零。真实 `Core.decompiled.cs` 的 `BuiltinFunctions.resetUnlocks` 包含 `loops` 等基础能力，排行榜入口使用该集合。此前的 Speed 解锁失败又阻止 Expand 和 Plant，Bush 异常是后续症状。

#10 基准 `1966.927s` 与历史复跑 `10128.299s` 均非本轮实测。裸预设首差已通过下述场景配置继续核查；模拟器默认 reset 预设本身未修改。当前没有完整的 Weird 吞吐、提前骨头投入或回本预算；实机和双日志未验证。

## 当前规则下的部分基线与前期预算

补齐真实 `resetUnlocks` 对应的基础能力后，`.codex/leaderboard-sol/reset/scenario.json` 保持 Speed、Plant、Expand 为零、库存为零，只给 loops、debug、debug_2、timing、lists、dictionaries、costs、auto_unlock、operators、variables、senses、utilities、functions、import、simulation 各一级。不能改用满科技模拟 Reset。

报告 `.codex/leaderboard-sol/reset/baseline-with-initial-unlocks-seed1.json` 在 `3999.718561s`、500000 次 API 调用时达到上限，墙钟 `12.6745s`；这是预算停止，不是新的机制异常，也不是完整完成时间。已记录阶段：

| 阶段完成 | 累计本地游戏秒 |
| --- | ---: |
| step1 | 146.379194 |
| step2，Power 1000.077 | 1473.272143 |
| step3 | 1920.688543 |
| 早期 Megafarm 2 | 2089.608527 |
| step4，Polyculture 1 / Dinosaurs 1 | 2899.004323 |
| Mazes 3 | 3502.565466 |
| Megafarm 3 | 3743.639371 |

按原报告 `harvests.at_ns` 与阶段时间筛选，step2 净耗 `1326.892950s`，期间向日葵收获676次，其中594次得到1 Power、82次得到8 Power，毛产量1250。首次向日葵收获为 `1170.599476s`，不能把它当作解锁时刻。低倍率确有损失，但前期尚未产电的时间更长；单独优化末尾补电不足以解决与#10的差距。

当前 `step2()` 每列先尝试 Speed，再到最后尝试 Sunflowers；当前成本中 Speed 4 与 Sunflowers 1 都需要500 Carrot。可筛选一个局部顺序候选：仅将原有 Sunflowers 解锁及成功标记块移到 Speed 尝试前，保留其余升级、混种、Power 100/1000 阈值和后续路线。Speed 3有Power时动作速率倍率约6.75，高于Speed 4无Power时的5.0625；这只是产电后动作吞吐的理论理由，成熟、种植、补料和推迟速度升级的代价仍须完整计入。

先用当前正式脚本补完整seed 1基线，有限提高API/语句预算、墙钟仍不超过60秒并保持进度；达标后同场景比较候选。只在解锁成功和已有阶段边界输出科技、库存与时间，不逐格输出。至少对照seed 0/1/123的完整时间及step2、Megafarm 3、最终金币/骨头阶段；若前期收益被后续回吐，停止候选，不继续枚举Power阈值。早期骨头购买Polyculture 2另作独立候选，不能与解锁顺序合并后归因。

## 2026-10-24：完整首配对与有界筛选结论

沿用补齐15项基础能力的reset场景，不添加库存或生产科技；正常结束且 `state.unlocks.leaderboard > 0` 才算完成。场景未配置物品goal，故 `goal_reached=null`。原版SHA256为 `270c7b99a2762993fe3b2a91515085f318831ec64685eefe373a029808f335ba`；候选为 `fb90c19851688da14952911c3d148bd335cf0fe12e73ef8d44dae0a3f3dc3dda`，仅把step2原Sunflowers解锁及成功标记块移到Speed之前。

| 样本 | 完整本地游戏秒 | 最终Leaderboard解锁 |
| --- | ---: | --- |
| 原版seed 0 | 9899.899869 | 是 |
| 原版seed 1 | 10114.199878 | 是 |
| 提前Sunflowers候选seed 1 | 10286.981630 | 是 |
| 原版seed 123 | 未取得 | 有界停止时否 |

seed 1候选step2累计从1473.272143降到1465.716942秒，只省7.555201秒；step4从2899.004323降到2838.356596秒，省60.647728秒；整轮却慢172.781752秒。不同后续随机轨迹和资源阶段会改变耗时，不能把这一负收益外推为所有seed的严格劣势，也不能混合未配对样本计算收益。3seed筛选未完成，停止该候选实机安排，不继续枚举Power阈值。

各次设置API上限300万、检查点1500万、总墙钟55秒，并每5墙钟秒报告实际API和游戏时间。原版seed 123初次CLI超时只保留99字节摘要；用正式run_script入口补取详细停止报告，55秒时为6501.544529游戏秒、2590308次API、Leaderboard仍为0，停在第二次大批Weird生产。该部分时间不计入完整预测。

Astra修复CLI父子报告截止竞争（0352baa）后，用原55秒场景复核，已收到BudgetExceeded、line 1637、完整state/output/API：5772.367003游戏秒、2297486次API，无BrokenPipe。回传预留使实际工作预算短于总硬预算，游戏机制和计费不变；报告竞争已解除，seed 123完整执行仍未覆盖。

| 时间名称 | 本次候选值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 10286.981630 | 仅seed 1一次完整完成，配对原版10114.199878，3seed不足 |
| 短时打榜测试时间 | 未取得 | 首配对无净收益且3seed不齐；实机准备79仍阻塞 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据位于 `.codex/leaderboard-sol/reset/`：`full-baseline-seed0.json`、`full-baseline-seed1.json`、`early-sunflowers/seed1.json`、`early-sunflowers/comparison.json`、`full-baseline-seed123-bounded-detail.json`、`cli-budget-recheck-seed123.json`及`three-times.json`。游戏指纹见[当前规则](current_game_rules.md)。正式py未改、Save0未部署Reset，未进行本候选实机或同seed精度验收；提前Polyculture 2未与本候选混合。

## 提前Polyculture 2：按完整报告核算阶段回本

当前源码Growable.GetYield在伴生倍率之后将感染产量的一半转为Weird。原版两次大批Weird生产期间Trees 4、Polyculture 1不变，树的Wood收益40/400分别为普通/伴生成熟收获，20/200分别为感染普通/感染伴生；后两类产生等量Weird。按既有完整报告的harvests.at_ns切阶段求和，所得Weird与阶段库存增量一致，无须重新运行基线。

| seed | 两次大批Weird净耗秒 | Weird增量 | 其中来自伴生 | 伴生产量占比 | 固定收获速率下的节时预算 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 1319.539994 | 83620 | 66800 | 79.89% | 584.716761秒 |
| 1 | 1011.016251 | 83680 | 68200 | 81.50% | 453.083531秒 |

每批独立按T×f/(1+f)计算最后一列，f是该批Weird中伴生产量占比；Polyculture 2将命中倍率10→20，只增加原命中部分的产量。这假定收获速率和命中结构不变，不是完整时间预测，也不是严格上界。提前结束Weird会减少顺手产电及被动肥料积累，随后金币或骨头可能变慢；初始化、成熟与改写支撑也不会按比例消失。

当前解锁成本为10000 Bone。已有Dinosaurs 1且12×12时，理论完整143尾的一轮兑现20449 Bone，足够购买；苹果每个2 Cactus，完整一轮143个共286，须按实际库存核对并保留已有补给。DinosaurHat的移动ops从400逐苹果递减，与恐龙科技等级无关；等级影响苹果价格和骨头倍率。现有seed 0/1最终Dinosaurs 3的12×12单轮日志可作成本量级参考，但不能当提前Dinosaurs 1的预测。

独立候选采用正式原版SHA270c7b99，而非提前Sunflowers失败版。在step5完成Mazes 3和Megafarm 3后、farm_gold_until(1000000)前，仅插入一次Polyculture 2准备：读当前等级和实际cost，调用已有farm_bones_until满足Bone成本，再unlock并确认等级达到2。保持世界尺寸、全部Power/Weird阈值、金币批次和最终Dinosaurs 3路线。借用现有完整绕环，允许骨头超额并保留余量计入最终目标，不另写刚好100尾截断算法。原有清场/补给成本必须进入记录。

此处原先安排的候选筛选已暂缓。下节整轮预算发现Weird阶段还输出大量Power，仅有Weird局部收益不足以支持执行。先核算联产资源回吐；已启动的有界单次只保留诊断，不自动扩seed或进入实机。

本节保留为局部预算来源，不再作为候选准入结论。整轮决策以下节为准；不枚举骨头数量、Power阈值或Polyculture等级。

## 整轮时间切片与候选准入（2026-10-24）

研究先回答“增加A1后，B/C真正能省多少”，再写候选。以下直接解析当前正式脚本seed 0/1的完整本地报告，不重跑；它们是模拟结果，未经本版本完整实机校准。两样本均解锁Leaderboard，整轮9899.900/10114.200秒，均值10007.050秒；样本范围不是统计置信区间。分析脚本与结构化账在 `.codex/leaderboard-astra/summarize_reset_budget.py`、`reset-time-budget.json`，输入SHA与来源随账保存。

### 当前时间花在哪里

阶段按既有日志相减，合计与报告完整时间一致；表中的金币段已扣除两次Weird，不能重复相加。骨头段含每轮轻量补给检查及最终解锁，尚未拆成精确追击/固定绕环两段。

| 阶段 | seed 0秒 | seed 1秒 | 均值秒 | 整轮占比 |
| --- | ---: | ---: | ---: | ---: |
| 初始能力 | 146.039 | 146.379 | 146.209 | 1.46% |
| 前期资源与1000 Power | 1297.745 | 1326.893 | 1312.319 | 13.11% |
| 首次Weird与迷宫解锁 | 436.596 | 447.416 | 442.006 | 4.42% |
| 首个并行解锁 | 25.873 | 35.170 | 30.521 | 0.30% |
| 升至4机 | 104.476 | 133.750 | 119.113 | 1.19% |
| 扩田与一级恐龙 | 794.662 | 809.396 | 802.029 | 8.01% |
| 升至Mazes 3 | 596.074 | 603.561 | 599.817 | 5.99% |
| 升至8机 | 203.918 | 241.074 | 222.496 | 2.22% |
| 两批大规模Weird | 1319.540 | 1011.016 | 1165.278 | 11.64% |
| 1M金币导航及衔接 | 1727.921 | 1930.922 | 1829.422 | 18.28% |
| Dino 3升级及首轮苹果准备 | 419.488 | 417.589 | 418.539 | 4.18% |
| 25轮骨头及最终解锁 | 2827.568 | 3011.033 | 2919.301 | 29.17% |

粗分A为准备到8机（均值3674.511秒），B为Weird与1M金币（2994.700秒），C为恐龙准备与骨头（3337.840秒）。只在A之后插入升级，不能让不变的A低于#10整轮1966.927秒；骨头段本身也超过#10。后期改进只能是增量收益，不能宣称单项能达到前十。

### 科技效果只能作用于受影响部分

每个候选先列新增步骤时间/资源、各后续阶段可受益的比例、其他产物变化及有效并行数。阶段内部动作、生长和补给可能重叠，不能把它们当独立耗时相加；没有计数支持时把比例标为未知。

`整轮净节时 = 各阶段直接节时之和 − 新增准备/升级/恢复时间 − 后续资源缺口造成的额外时间`

对已识别的受益比例a和有效加速r，可暂用 `T′ = T × (1−a+a/r)`；只有机制和阶段数据支持a、r时才代数值。收获倍率先换算所需收获次数并取整，不能直接除整个阶段。已知误差、种子波动与结构假设分开记录。

| 改动 | 必须计入的成本 | 可受影响部分 | 当前判断 |
| --- | --- | --- | --- |
| 提前Polyculture 2 | 10000 Bone；额外恐龙、清场、补给 | 伴生命中的产量，当前占Weird约80%；不直接加速金币移动或骨头 | 缺联产Power保持率，暂缓 |
| Trees 4→5 | 19200 Hay及购买时的补料；不能拿期末库存当当时可用库存 | 所有Tree产量，可能减少Weird生产周期 | 同样可能少产Power；先补资源账，不直接试完整路线 |
| Megafarm 3→4 | 128000 Gold及其Weird/导航成本 | 当前按列产线受12列限制，8→最多12有效工人；不加速单机迷宫和恐龙 | 即使全部Weird可并行，局部节时上界约388秒；已有失败记录，不重试 |
| Mazes 3→4 | 432000 Cactus及基础补料 | 单次金币翻倍，所需迁移近半；每次Weird成本也翻倍，单位Gold所需Weird不因等级下降 | 不把Weird和导航同时减半；先过仙人掌准备预算 |
| Dinosaurs 3→4 | 432000 Cactus及补料 | 12×12完整轮产量81796→163592，25轮→13轮；每个苹果价格同时翻倍 | 只可削掉约12轮，准备成本须抵扣；历史失败，不重试 |
| Expand 6→7 | 64000 Pumpkin和整条补料链 | 改变南瓜/仙人掌产量、迷宫规模及恐龙尾长，也改变移动与排序 | 不能只按骨头倍率算收益；历史扩田成本失败仍有效 |

### Power是Weird阶段的联产收益

源码Execution以累计操作数/6000计Power消耗，Farm.MaxSpeedFactor在有Power时将动作速度翻倍。Speed 5下，一份Power对随后串行动作的节时折算约 `6000×0.0025/(1.5^5×2)=0.987654秒`，有扣款批次边界；不能直接套到多机并行时间或自然生长。

两个大批Weird结束时，seed 0输出870.532与1381.749 Power，seed 1输出660.904与1371.934 Power。第一次的库存随后在金币段用尽，第二次的库存继续支持金币、仙人掌和骨头，最终也耗尽。减少其中任一批Power都会影响后续；只看1M金币结束时剩余的589.610/450.880，会漏掉金币过程中已经消耗的Power。

用120秒作为额外骨头步骤的敏感性参数：现有无Power的12×12、Dino 3单轮共46个样本，范围109.896～133.280秒，中位数约118～119秒；等级不改变移动ops，但该量级不是提前Dino 1的实测，额外恢复成本也未确认。下表没有概率含义，只检验局部预算对Power损失的敏感程度；正数为省时，负数为退步。

| 两批留给后续的Power减少比例 | seed 0净节时秒 | seed 1净节时秒 |
| --- | ---: | ---: |
| 0% | +464.717 | +333.084 |
| 25% | −91.402 | −168.852 |
| 50% | −647.521 | −670.787 |

所以“额外一轮骨头约120秒，小于Weird省453～585秒”还不够。该参数下，两seed最多容忍损失约471/337 Power，即原后续可用量的20.9%/16.6%；其余成本会继续压低容忍值。现在没有证据保证能保留所需Power，提前Poly 2尚不具备保守净收益依据。科技提升可能改变命中、成熟和产电速率，不能用固定速率表当作真实结果。

### 下一步先获取最有价值的局部证据

优先看占29.17%的骨头段中不需要新资源的成本。当前run_dinosaur_chase_loop在退出追击后，固定绕环仍调用完整update_and_move，每步执行measure并维护step、苹果目标和length；这些值在固定绕环结束后不再读取。候选仅简化这一尾段，保持追击、路径、can_move失败退出、实际move与坐标更新不变。它没有升级或清场投资，也不压缩前面的Weird产电阶段，跨阶段副作用较少。

先由Sol抽取现有12×12绕环作有界局部对照，使用当前Reset科技、Dino 3、Power=0、足够但固定的苹果材料、单机，比较相同seed 0/1/123的原版与仅尾段简化版。确认骨头产量、move次数/动作tick和随机抽样一致，记录完整单轮时间、measure调用与解释器tick。每少10000次measure，单此API在Speed 5下约省1.646～3.292秒，另计被删维护语句；不能在没有尾段计数时给整轮百分比。

用局部每轮差额乘现有25轮，再按有/无Power分段修正，得到整轮回本预算；稳定改善才迁入完整Reset候选并作配对验证。局部结果不填“完整本地预估时间”，也不进实机。若所得收益很小，保留结论后转向A段的资源/科技依赖路径预算，不围绕尾段做参数枚举。

候选准入要同时满足：当前规则可执行；新增成本有来源；主要联产资源与后续时间已纳入；在明确的保守假设下仍有净收益。未知项可能改变正负号时，先做针对该未知项的有界局部检查。只有两个完整seed时，不给95%置信度之类结论；最终仍以同版本实机和完整官方统计确认。

### 已启动的Poly 2单次诊断：局部收益确实发生后续回吐

暂停通知到达前已启动的一次seed 1本地运行完成，未扩样本。候选SHA `7de63e5635c1e607c0d1838077d3f0961b14e020f4e8b3b65ca73dafffde8d95`，正常解锁Leaderboard并确认Poly 2，完整11258.980534秒；既有原版10114.199878秒，慢1144.780657秒。新增helper定义多1t，使start从0.2800变为0.2825秒，前期轨迹已经分歧；这是完整诊断，不能把所有差异严格归因于升级。

| 时间切片 | 候选减原版（秒） |
| --- | ---: |
| 升到8机前的前缀 | −49.368 |
| 新增骨头与Poly 2升级 | +126.234 |
| 两批Weird | −939.089 |
| 两批Weird之后的金币导航 | +1557.007 |
| 1M金币之后的准备与骨头 | +449.990 |
| 其他边界语句 | +0.006 |
| 合计 | +1144.781 |

Weird从1011.016秒降到71.928秒，但其后可用Power从两批合计2032.838降到5.042。减少2027.796 Power的串行动作折算约2002.762秒，实际金币及后续合计多2006.998秒，量级接近，支持把联产Power纳入预算；它不证明全部差值只来自Power。原版两批Weird结束Fertilizer均为8，候选为173/392，显示资源短缺边界也发生变化；之前固定收获速率只预测省453秒，不能表达这种跨阈值变化。

本候选三类时间：完整本地预估11258.980534秒（仅1seed诊断）；短时实机未取得；完整游戏打榜未取得。不扩seed或实机。原始报告及三值在 `.codex/leaderboard-sol/reset/early-poly2/`；相加闭合的时间差账在 `.codex/leaderboard-astra/reset-poly2-accounting.json`。后续预算必须同时检查资源等待阈值与联产资源，不能仅由科技倍率线性外推。

## 骨头固定绕环尾段：3seed组件对照与25轮预算

本次仅抽取当前正式脚本的build_dinosaur_path和run_dinosaur_chase_loop，来源SHA256为270c7b99。共同入口只执行12×12缩图、清场、戴恐龙帽、单轮绕环和换草帽结算，不包含升级或材料准备。科技复制既有Reset完整seed 1最终快照，保留Speed 5、Expand 6、Dinosaurs 3等当前等级，仅将Megafarm置0限定单机、Leaderboard置0避免预先达标。12种初始库存归零，仅固定Cactus 1000000，Power始终0；目标81796 Bone。

原组件SHA256为 `627abf5291fc842884cbb8554f0157d64cce9e6056beecb74bcfb8312e80daac`，精简组件为 `fc42d5f701e87602a234c40c5ced609abe7d019a8ff8bd7357d729c0db0fdf97`。只把固定绕环尾段内联为方向有效性检查、can_move失败退出、move及原get_pos_x/y坐标更新；追击和path不变，删除此后无人读取的step、measure、目标和length维护。两版函数定义数相同，没有单方新增helper产生的开局tick。

| seed | 原组件游戏秒 | 精简组件游戏秒 | 单轮省秒 | 相同move数 / 动作tick | measure原→新 | 解释器tick原→新 | 相同snake抽样数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 119.799831 | 115.789285 | 4.010546 | 2870 / 306727 | 2871→949 | 44494→34226 | 2048 |
| 1 | 126.165939 | 122.399674 | 3.766265 | 2932 / 324665 | 2933→1139 | 45650→36036 | 3062 |
| 123 | 122.599839 | 118.699910 | 3.899928 | 2825 / 316316 | 2826→961 | 43809→33819 | 2358 |

六次运行均完整达标，每轮Bone 81796、Cactus消耗1144，配对can_move调用也一致。原组件均值122.855203秒，精简组件118.962956秒，单轮省3.892246秒；measure少1922/1794/1865次，解释器tick少10268/9614/9990。模型570dbb2，每seed上限50万API/200万检查点，每版三seed批次共享25秒墙钟。

随机数按机制区分：全部非various流的抽样数及流seed配对一致，特别是snake流不变。various流因世界时长缩短而少抽5760/5472/5616次，逐seed恰等于少经历的0.1秒水分衰减次数×144格；不能强称全部八流抽样一致，也不把这种计时变化当作骨头路径失效。

按现有25轮预算：若全程无Power，三seed局部差额线性换算约94.157～100.264秒，均值97.306秒；若25轮始终有Power且路径与其他条件相同，动作tick约减半，对应约47.078～50.132秒，均值48.653秒。这是情景预算，不是完整Reset预测、严格上下界或统计置信区间。

既有完整seed 0/1分别有22/24轮在Power=0时开始，其余3/1轮可能只部分有Power。把这些不确定轮的收益系数放在0.5～1，结合当前组件样本差额得到约88.507～100.264秒、92.274～100.264秒的敏感性范围；不假设这三个局部seed覆盖所有25轮苹果轨迹。减少时间也使组件期末被动Fertilizer少1/2/2份、Water少3/3/4份；如果完整路线依赖这些补给而发生额外等待，仍须抵扣回吐。Cactus、move和当前骨头收益未增加资源需求，但不能据此保证整轮反馈为零。

| 时间名称 | 当前值 | 依据 |
| --- | --- | --- |
| 完整本地模拟预估时间 | 未取得 | 只做组件，122.855/118.963秒不代填完整Reset |
| 短时打榜测试时间 | 未取得 | 未部署组件或完整候选 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

原始证据在 `.codex/leaderboard-sol/reset/bone-tail/` 的 `source-manifest.json`、`scenario.json`、`baseline/seeds0-1-123.json`、`candidate/seeds0-1-123.json`、`comparison.json`及`three-times.json`。此处组件结果只作预算输入；后续完整本地候选见末节，正式py和Save0仍未修改，未进行实机或同seed精度验收。后续是否推进由整轮成本与补给边界决定，不继续围绕尾段枚举参数。

### 整轮准入：水肥减少在当前两基线没有后续消费路径

Astra核对正式step5调用链：金币与Dinosaurs 3升级完成后调用farm_bones_until，结束后只解锁Leaderboard并输出；解锁成本仅1000000 Gold与2000000 Bone。骨头循环自身不使用Water或Fertilizer，只有苹果材料不足时才可能转回生产。

两个完整基线首轮bone_prep均为37360 Cactus，25轮每轮消耗1144，总共28600，余8760。逐一核对两份报告的全部25条bone_prep，当前库存减剩余轮数×1144的余量始终8760。因此只要完整候选保持相同骨头路径与产量，骨头开始后不会再次触发种植补料；少积累的水/肥没有当前流程的消费方，不应凭这一库存差单独扣减预算。此结论限于这些初始库存和路线，不泛化到缺材料场景。

组件SHA、复制函数AST、六份达标终态已复核。various抽样差由时长减少的水衰减解释，snake及其余流计数保持一致；完整连续25轮仍需检查苹果路径、供料、Power转折和成功条件，组件不能代替整轮验证。

准入结论：值得进入完整本地对照。由正式原版复制候选，只替换已核对的固定绕环尾段，不增加函数定义、不改变顶部语句或日志，不并入其他候选。先运行seed 0/1，复用同版本已完成的原版；每次仍55秒墙钟、300万API、1500万检查点并输出进度。先核对start、step1～4、Megafarm 3、1M Gold、首轮bone_prep的时间和库存；改动执行前如已分歧，先定位，不将整轮差额归因为尾段。

两seed完整成功且净收益稳定后，再决定额外seed和实机队列。seed 123原版已在同预算停止，不机械重跑；预算停止仍记为未完成。保留全部25轮Bone/Cactus/Power阶段、末态Leaderboard、随机流与三类独立时间；若新增补料或动作路径改变则重新核算。预计约90～100秒仅是约0.9%～1.0%的增量收益，不代表接近#10，完成该项后回到A段资源/科技依赖的结构预算。

## 首轮55秒预算记录：完整尾段候选seed 0/1配对（历史）

候选 `.codex/leaderboard-sol/reset/bone-tail/full/lb_fastest_reset.py` 的SHA256为 `acb8130f570ba12592fb69c534f5ff11796fe2c3dda3263424f38185f3bcb153`。由正式原版270c7b99直接复制，只替换已验证尾段；run_dinosaur_chase_loop的追击前缀及其他全部模块AST节点保持一致，不新增函数、顶部语句或日志，不混入其他候选。场景仍是补齐15项初始基础能力的reset，原版复用既有完整seed 0/1报告，未重跑原版或seed 123。模型570dbb2；每次总墙钟55秒、API上限300万、检查点1500万，保留5秒进度。

| seed | 原版完整游戏秒 | 候选完整游戏秒 | 完整净收益 | 候选骨头完成轮数 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 9899.899869 | 未取得 | 未取得 | 10/25，有界停止 |
| 1 | 10114.199878 | 10021.383165 | 省92.816713秒，0.918% | 25/25，Leaderboard已解锁 |

两seed从start、step1～4、Megafarm 3、1M Gold直到首次bone_prep的79条日志均与各自原版逐条相同，包含时间和库存；没有新增helper定义造成的开局tick或改动前轨迹分歧。两版对照按相同完整脚本场景进行，局部修改生效前的前缀已核对。

seed 1全部25轮每轮产出81796 Bone，bone_prep的Cactus余量恒8760，整轮move均342942次、move动作tick均62277474，can_move/get_pos_x/get_pos_y/plant/use_item/harvest调用数相同。snake抽样均53558，其他非various流计数亦相同；various少133632次，恰对应12×12少经历928次0.1秒水衰减。measure从90192降到45917，解释器tick从8306842降到8069024；没有靠改移动路径或补料取得收益。

seed 1各轮开始时只有第1轮Power为正，两版标记一致，末态Power均0。末态Leaderboard科技一致，Bone44900、Gold200、Cactus8760、Pumpkin496及其余生产库存一致；仅被动Fertilizer从1743降到1706、Water从6883降到6809。没有新增plant/use_item调用，符合骨头后无水肥消费方的准入分析。未逐API采样轮内Power精确归零时刻，不宣称该时刻完全相同。

seed 0工作进程在53.763秒触预算，总命令仍受55秒限制，报告8131.868406游戏秒、Bone817960；完成10轮并正在第11轮。已完成10轮的Bone/Cactus/剩余轮数均与原版一致，第10轮结束累计省38.921587秒；各轮开始时Power为正的仍为第1～3轮。该部分进度不计入完整候选时间，也不与seed 1混成两seed均值。未放宽预算或机械重跑失败样本，issue #56记录完整两seed验证仍受计算预算阻塞。

| 时间名称 | 当前完整尾段候选值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 10021.383165 | 仅seed 1一次完整正常结束；同seed原版10114.199878，两seed筛选未齐 |
| 短时打榜测试时间 | 未取得 | 完整两seed确认不足；游戏重开尚待授权 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据在 `.codex/leaderboard-sol/reset/bone-tail/full/`：`source-manifest.json`、`seed0.json`、`seed1.json`、`comparison.json`和`three-times.json`。组件与完整候选的三类时间分别保存，不互相覆盖。正式py和Save0未修改，未运行实机或同seed模型精度验收；单个完整样本只能支持该次净收益，不宣称两seed稳定刷新或统计置信度。

## 75秒单次补齐：完整seed 0/1均通过本地筛选

Astra按旧报告末段仍持续推进、估计尚需约5秒墙钟的证据，批准仅seed 0一次新的75秒总墙钟方案。runner提交7b63d27使CLI校验、帮助和文档支持此有限预算，默认10秒、父子绝对截止、最多1秒报告余量和5秒进度保持；脚本SHA acb8130f、场景、300万API和1500万检查点均不变。seed 1与两份原版复用，不重跑seed 1/123；旧55秒JSON及进度均未覆盖。

seed 0本次工作进程54.803秒正常结束，Leaderboard已解锁。旧55秒停止报告全部输出是本次完整输出的精确前缀；两seed从start到首轮bone_prep的79条日志仍与各自原版逐条相同。预算变化只允许执行完成，不改变模型机制或候选逻辑。

| seed | 原版完整游戏秒 | 候选完整游戏秒 | 省游戏秒 | 改善 | 完成情况 |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 9899.899869 | 9803.578949 | 96.320920 | 0.973% | 25/25骨头轮，Leaderboard 1 |
| 1 | 10114.199878 | 10021.383165 | 92.816713 | 0.918% | 25/25骨头轮，Leaderboard 1 |
| 两seed均值 | 10007.049873 | 9912.481057 | 94.568816 | 0.945% | 两个完整候选样本 |

两组25轮每轮均产81796 Bone，Cactus每轮消耗1144，prep库存扣除全部剩余轮需求后始终余8760。完整API计数只有measure减少，其他调用全部一致；seed 0/1整轮move分别398579/342942，move动作tick分别73163911/62277474，均与配对原版一致。没有新增材料生产、移动或水肥使用。

seed 0的measure从90885降到44847，解释器tick从9173925降到8927257；seed 1分别从90192降到45917、从8306842降到8069024。snake抽样分别57062/53558，所有非various流计数配对一致。various分别少138672/133632次，恰等于少经历963/928次0.1秒水分衰减×144格；不宣称全部随机流完全相同。

两版轮开始Power为正的标记一致：seed 0为第1～3轮，seed 1仅第1轮；末态Power均0。两组末态解锁与所有生产库存均相同，包括Bone44900、Gold200、Cactus8760、Pumpkin496。只有被动积累库存减少：seed 0的Fertilizer 1619→1581、Water 6740→6663；seed 1为1743→1706、6883→6809。当前流程没有这些水肥的后续消费方。未逐API采样轮内Power归零时刻，不宣称其时间完全一致。

| 时间名称 | 本候选当前值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 9912.481057 | 同脚本、同场景完整seed 0/1均值；配对原版10007.049873 |
| 短时打榜测试时间 | 未取得 | 本候选尚未部署实机；游戏正常重开待授权，79/Save0仍冻结 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

新证据在 `.codex/leaderboard-sol/reset/bone-tail/full/` 的 `seed0-budget75.json`、`seed0-budget75.progress`、`seed0-budget75.client.json`、`comparison-budget75.json`及`three-times-budget75.json`；原55秒的`seed0.json`、`seed0.progress`、`comparison.json`和`three-times.json`作为历史保留。正式py和Save0未修改；组件三值也单独保留。两seed均支持该项约0.9%的完整本地净收益，不构成统计置信区间、实机成绩、排名或同seed模型精度验收。结果交Astra判断实机队列；后续回到A段资源/科技依赖的结构预算，不继续围绕尾段枚举。

## Reset A段观测：seed 1科技、产电与动作成本账

本项只观测当前正式原版270c7b99。副本SHA `6d4e776ff5ac90e7fb585205a04c62ba78c00d1b3382b1078018ae683e58e22d`，仅在入口原step2日志后插入return；移除此Return后全模块AST与原版相同，其余函数、顶部语句和日志均保留。沿原reset场景只运行seed 1一次，55秒总墙钟、30万API、300万检查点；CLI保留5秒进度和30秒无进度停止约束，子进程继承256MiB的RLIMIT_FSIZE硬上限。工作进程3.785秒正常完成，轨迹75111条、16750256字节（15.975MiB），未触任何预算。

前三条输出与既有完整seed 1基线逐字相同。step1原日志146.379193764秒，step2原日志1473.272143310秒，区间为1326.892949546秒。此前预算1312.318851278秒是原seed 0/1的step2均值，其中seed 0为1297.744753009秒；本项不将均值当seed 1。报告末态1473.299962400秒包含新增return及调度收尾，超出原日志边界的0.027819090秒不计A段。

库存按原API副作用时刻记录，成功升级列出立即支付后的余额；预计返回时刻另列。step1/step2显示原日志get_time，库存查询和quick_print可稍晚。非Power库存由既有收获、成功种植、升级、用料及原补给时序推导；20546条num_items读数和全部非Power末态逐一相符。伴生额外收益由实际收获记录纳入，未假设Polyculture 0时所有收获均只有基础产量。Power只用同一0.2秒结算周期内的既有读数和收获增量还原，不跨周期外推扣款。

| 边界 | 游戏秒 | Hay | Wood | Carrot | Power | Water / Fertilizer / Weird |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| step1原日志 | 146.379194 | 21 | 1 | 0 | 0.000000 | 0 / 0 / 0 |
| Sunflowers 1支付后 | 1156.740193 | 233 | 355 | 1 | 0.000000 | 30 / 0 / 72 |
| Speed 5支付后 | 1337.895069 | 94 | 412 | 22 | 105.108833 | 39 / 0 / 134 |
| 达到1000Power后的step2原日志 | 1473.272143 | 4 | 960 | 3 | 1000.076667 | 40 / 0 / 170 |

三个子区间分别为1010.360999、181.154876、135.377075秒：step1→Sunflowers、Sunflowers→Speed 5、Speed 5→step2原日志。Sunflowers在Speed 4之后、Speed 5之前解锁；首次向日葵成熟收获发生在1170.599476秒，距解锁应用13.859283秒。升级成本在应用时刻支付，不等于API返回时间；下表覆盖这次前缀内全部19次成功升级。

| 科技 | 新等级 | 应用游戏秒 | 预计返回游戏秒 | 实际支付成本 |
| --- | ---: | ---: | ---: | --- |
| Speed | 1 | 10.892500 | 11.225833 | 20 Hay |
| Expand | 1 | 26.167503 | 26.500836 | 30 Hay |
| Plant | 1 | 51.669175 | 52.002508 | 50 Hay |
| Expand | 2 | 85.280848 | 85.614182 | 20 Wood |
| Carrots | 1 | 146.045860 | 146.379194 | 50 Wood |
| Speed | 2 | 444.289253 | 444.511476 | 20 Wood |
| Expand | 3 | 474.770389 | 474.992611 | 20 Carrot + 30 Wood |
| Speed | 3 | 582.649364 | 582.797512 | 50 Carrot + 50 Wood |
| Trees | 1 | 665.719023 | 665.867171 | 70 Carrot + 50 Wood |
| Watering | 1 | 695.159774 | 695.307922 | 50 Wood |
| Expand | 4 | 744.073865 | 744.222013 | 50 Carrot + 100 Wood |
| Watering | 2 | 790.093881 | 790.242029 | 200 Wood |
| Carrots | 2 | 830.179821 | 830.327969 | 250 Wood |
| Fertilizer | 1 | 946.775417 | 946.923566 | 500 Wood |
| Speed | 4 | 966.073202 | 966.171968 | 500 Carrot |
| Watering | 3 | 1098.980588 | 1099.079354 | 800 Wood |
| Sunflowers | 1 | 1156.740193 | 1156.838958 | 500 Carrot |
| Carrots | 3 | 1280.385588 | 1280.434971 | 1250 Wood |
| Speed | 5 | 1337.895069 | 1337.927991 | 1000 Carrot |

整个step1+step2前缀成功升级共支付100 Hay、3370 Wood、2190 Carrot；其中step2为3300 Wood、2190 Carrot。全部成功种植另支付1441 Hay、1441 Wood、688 Carrot；不能把向日葵解锁的500 Carrot当作全部产电投入。水/肥实际使用180/52份，被动收到220/52份，期末40/0。此账只列实际支出，不将生产这些材料的所有时间直接归因给某一科技。

### 向日葵毛收入、耗电与期末库存

成功种植688株，成熟收获676株：594次×1 Power、82次×8 Power，共1250 Power；结束尚有12株未收。期末净库存1000.076667，收入减库存为249.923333，表示期间已结算的Power支出；未在此虚构未结算used_power。Speed 5支付时累计毛收入218、净库存105.108833；其后再产1032，库存净增加894.967833。

已收676株从种下到收获的平均年龄5.364984秒。按每株最后未成熟与首次已成熟快照，平均成熟年龄只能约束在1.210758～5.215571秒，成熟后未收平均区间为0.149412～4.154226秒。这些是每株的观测区间，时间彼此重叠，不能相加成全局等待秒或当作已知成熟事件时刻。

### 能辨明的step2时间占用

单机副作用API的[api_time_ns, ready_ns)区间已逐段核对不重叠，并裁剪至两个原日志get_time边界。以下按实际时间累加，包含当时Speed与Power变化；random、解释器、分支和调度无法由现有轨迹单独拆开，保留余项。

| 占用 | 游戏秒 | 占step2 |
| --- | ---: | ---: |
| 种植API | 350.362656 | 26.405% |
| 收获API | 338.224482 | 25.490% |
| 移动API | 491.432722 | 37.036% |
| 翻土API | 11.888894 | 0.896% |
| 使用水肥API | 15.687274 | 1.182% |
| 升级尝试API（成功和失败） | 5.435581 | 0.410% |
| 其余已分离API | 17.654495 | 1.331% |
| 解释器、random与调度余项 | 96.206845 | 7.251% |
| 合计 | 1326.892950 | 100.000% |

can_harvest=false本身的API时间仅0.492120秒，已经包含在上表，不能另加。识别到718次判熟失败后未收割、未种植或施肥便移走的访问，从失败查询到移动返回合计52.744129秒（3.975%，也已包含在上表）；这是巡视与判断区间，不是纯等待。step2没有连续两次false can_harvest形成的纯轮询序列。成熟与其他格生产重叠，纯成熟等待的全局墙钟占比仍为未知，不将全部false查询或株秒归为等待。

原始数据及推导代码在 `.codex/leaderboard-sol/reset/a-stage/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.jsonl`、`seed1.client.json`、`analyze.py`、`accounting.json`和`sunflower-lifetimes.json`。轨迹SHA `312baf8f44943c05288dcb5a792d48d6e9601e9fe82418dcc1efa16bfeeed2b7`与模拟报告一致。

本项为单seed前缀观测，不是新优化算法。该副本的完整Reset本地模拟预估时间、短时打榜测试时间和游戏打榜时间均为未取得/null，1473秒前缀或1327秒step2不代填完整时间；此前骨头尾段候选三值独立保留。正式py与真实Save0均未修改，未开展实机或同seed模型精度验收。观测交Astra结合静态科技成本选择一个结构方向，不重跑已失败的提前Sunflowers，不扩seed或枚举cap。

## 提前Speed 2：集中补20 Wood的单次A段筛选

候选SHA `bdf14ca61eedefdb1fdf4594ce6f2baafff4ebd3b8121ecb0e9de59296d04ad5`，从前述A段原版观测副本复制，只在原step1日志后、step2前增加farm_wood_until(20)和unlock(Unlocks.Speed)。复用既有helper，保留step2原日志后return；无新增函数定义，其余模块AST与观测原版一致，不混入骨头尾段、向日葵结构或科技cap候选。沿同reset场景只运行seed 1一次，仍为55秒总墙钟、30万API、300万检查点、trace256MiB硬限；工作4.129秒正常结束，78718次API、194084检查点，轨迹17560034字节，未触预算。

原start/step1两条日志逐字相同，完整基线复用前述观测，不重跑原版或其他seed。Wood初始1，helper首次检查146.384193765秒，到175.554199599秒首次读到20，观察跨度29.170006秒；包含最终查询返回为29.171673秒。Speed 2应用175.557532933秒、返回175.779755333秒，花20 Wood；从原step1日志到升级返回共29.400562秒。以下净收益已经包含补木及升级，不把这段准备排除。

| Speed新等级 | 原版应用游戏秒 | 候选应用游戏秒 | 候选预计返回游戏秒 | 提前游戏秒 |
| --- | ---: | ---: | ---: | ---: |
| 2 | 444.289253 | 175.557533 | 175.779755 | 268.731720 |
| 3 | 582.649364 | 413.285501 | 413.433649 | 169.363863 |
| 4 | 966.073202 | 806.024157 | 806.122922 | 160.049045 |
| 5 | 1337.895069 | 1200.851989 | 1200.884911 | 137.043080 |

| 时间边界 | 原版游戏秒 | 候选游戏秒 |
| --- | ---: | ---: |
| step1原日志 | 146.379194 | 146.379194 |
| step2原日志 | 1473.272143 | 1350.878036 |
| step1→step2日志区间，候选包含准备 | 1326.892950 | 1204.498843 |

含准备的A段净省122.394107秒（9.224%）。候选首个step2 Power循环API发生于175.779755333秒，从该点到step2日志为1175.098281秒；这只是函数内观察区间，不能用它排除补木投资后再与原版总阶段比较。应用Sunflowers从1156.740193提前至998.754361秒，首次成熟收花从1170.599476提前至1012.598829秒。

### 期末科技相同，资源差额先列后段负债

两版全部科技字典相同：Speed 5、Expand 4、Carrots 3、Trees 1、Grass 1、Watering 3、Fertilizer 1、Sunflowers 1、Plant 1；原有15项基础能力保留，其他科技仍0。完整科技字典和全部12项库存均保存在comparison.json，不以节时替代资源验收。

| 库存 | 原版 | 候选 | 候选减原版 |
| --- | ---: | ---: | ---: |
| Bone | 0 | 0 | 0 |
| Cactus | 0 | 0 | 0 |
| Carrot | 3 | 0 | -3 |
| Fertilizer | 0 | 0 | 0 |
| Gold | 0 | 0 | 0 |
| Hay | 4 | 5 | 1 |
| Piggy | 0 | 0 | 0 |
| Power | 1000.076667 | 1001.098333 | 1.021667 |
| Pumpkin | 0 | 0 | 0 |
| Water | 40 | 42 | 2 |
| Weird_Substance | 170 | 120 | -50 |
| Wood | 960 | 1302 | 342 |

Carrot少3、Weird少50是待核算的后段负债，不能直接折成整轮净收益。Wood多342、Hay多1、Water多2、Power多1.021667，Fertilizer期末仍0。两版成功升级总支出相同，候选未跳过科技换取节时；种植支出则由1441 Hay/1441 Wood/688 Carrot变为1460/1460/718。候选用水199份、用肥58份（原180/52），被动供水241份、供肥58份（原220/52）；更早的解锁时刻会改变补给时序，不能只按总时长推断末态。

### Power毛净账

| 产电项目 | 原版 | 候选 |
| --- | ---: | ---: |
| 成功种花 | 688 | 718 |
| 成熟收花 | 676 | 706 |
| 一倍 / 八倍收获次数 | 594 / 82 | 624 / 82 |
| 毛Power | 1250 | 1280 |
| 期末净Power | 1000.076667 | 1001.098333 |
| 已结算Power支出 | 249.923333 | 278.901667 |
| 期末未收花 | 12 | 12 |

候选21922条非Power库存读数与推导账相符，所有非Power末态一致于账本，轨迹SHA与报告一致。插入准备后动作量和随机轨迹已改变；不能把122秒全部归因为基线同动作加速的91秒预算。现有轨迹仍不能单独确定纯成熟等待的全局占比。

证据在 `.codex/leaderboard-sol/reset/early-speed2/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.jsonl`、`seed1.client.json`、`accounting.json`、`comparison.json`、`three-times.json`及推导代码`analyze.py`。该副本尚未完成完整Reset，本地模拟预估时间、短时打榜测试时间和游戏打榜时间均为null；原骨头尾段三值独立保留。

按准入停止条件，现交Astra核算Carrot/Weird及供给时序的后段影响，再决定是否推进step3或完整Reset；当前不扩seed、不继续完整候选或实机。正式py及真实Save0未修改。

## 提前Speed 2延伸至4机：保留131.353秒领先

按A段负债预算，只把前述bdf14ca6副本step2日志后的return移到入口try_unlock_early_megafarm()之后，其他AST一致；候选SHA `bc8e3c3a59d8b1f5f8011c5fc5e2519af73bde4eb830147c546c7f682f28fd6f`。未混入骨头尾段或其他策略。沿同reset场景单次seed 1，仍为55秒总墙钟、30万API、300万检查点、trace256MiB硬限，5秒进度及30秒无进度停止；工作8.307秒正常结束，158397次API、406154检查点，轨迹35096817字节且哈希与报告一致。

前三条日志逐字匹配A段候选。4机原日志2089.608526730秒，候选1958.255191350秒，领先131.353335秒；比较只取同类原日志get_time，不含新return及调度收尾。候选报告快照1958.287619520秒，晚0.032428170秒，下面完整候选库存明确使用这一快照。基线复用既有完整seed 1报告，没有重跑原版或扩seed。

| 原日志边界 | 原版游戏秒 | 候选游戏秒 | 候选领先游戏秒 |
| --- | ---: | ---: | ---: |
| step2（A段结束） | 1473.272143 | 1350.878036 | 122.394107 |
| step3（Mazes 1支付后） | 1920.688543 | 1798.109250 | 122.579293 |
| 金币达到2000 | 1955.823066 | 1833.243773 | 122.579293 |
| Megafarm 1 / 2机 | 1955.858128 | 1833.278835 | 122.579293 |
| 2机补Weird开始 | 1955.942738 | 1833.363444 | 122.579293 |
| 2机补Weird结束 | 2002.657409 | 1871.304074 | 131.353335 |
| 金币达到8000 | 2089.573465 | 1958.220129 | 131.353335 |
| Megafarm 2 / 4机 | 2089.608527 | 1958.255191 | 131.353335 |

从A段结束到4机，领先额由122.394107增至131.353335秒，再省8.959228秒。step3原447.416400、候选447.231214秒，省0.185186秒；两机补Weird原46.714672、候选37.940630秒，省8.774042秒。两个金币生产区间及两次Megafarm升级间隔配对相同。此处只比较已观测时间，不据此断言后续资源反馈为零。

### 直接可比的Weird、材料与Power日志

| 同类日志字段 | 原版 | 候选 | 候选减原版 |
| --- | ---: | ---: | ---: |
| step3（Mazes 1支付后）：weird | 1003 | 1003 | 0 |
| step3（Mazes 1支付后）：gold | 0 | 0 | 0 |
| 2机补Weird开始：weird | 661 | 661 | 0 |
| 2机补Weird开始：wood | 7890 | 7265 | -625 |
| 2机补Weird开始：carrot | 4883 | 4812 | -71 |
| 2机补Weird开始：fert | 14 | 14 | 0 |
| 2机补Weird开始：power | 523.426833 | 524.669333 | 1.242500 |
| 2机补Weird结束：weird | 1341 | 1421 | 80 |
| 2机补Weird结束：wood | 13730 | 13425 | -305 |
| 2机补Weird结束：carrot | 4883 | 4812 | -71 |
| 2机补Weird结束：fert | 2 | 2 | 0 |
| 2机补Weird结束：power | 428.852000 | 447.899333 | 19.047333 |
| 金币达到8000：gold | 8008 | 8008 | 0 |
| 金币达到8000：weird | 3 | 83 | 80 |
| 金币达到8000：power | 340.957500 | 359.756667 | 18.799167 |

A段结束Weird 170→120的50份差额，在step3支付Mazes 1后两版均为1003；对应本段补产1833/1883份。当前样本未表现为额外12秒等待，实际阶段略快；不能把单次结果当作Weird边际生产成本恒为零。两机补Weird结束时，候选Carrot少71、Wood少305；这些是同类日志处的直接差额，不冒充4机边界的原版库存。

原4机边界日志只直接记录Gold 8、max_drones 4及Megafarm等级2。原版其他库存和未记录科技为unknown/null，不用邻近补Weird/金币日志或完整Reset最终库存代填。候选下表来自1958.287619520秒的停机报告快照，已经在4机返回后，尚未执行step4。

| 4机边界或停机快照库存 | 原版4机日志 | 候选停机快照 |
| --- | ---: | ---: |
| Bone | 未知 | 0 |
| Cactus | 未知 | 0 |
| Carrot | 未知 | 4812 |
| Fertilizer | 未知 | 37 |
| Gold | 8 | 8 |
| Hay | 未知 | 9543 |
| Piggy | 未知 | 0 |
| Power | 未知 | 359.756667 |
| Pumpkin | 未知 | 0 |
| Water | 未知 | 459 |
| Weird_Substance | 未知 | 83 |
| Wood | 未知 | 13425 |

候选科技完整快照保存在comparison.json：Speed 5、Expand 4、Grass 4、Trees 4、Carrots 4、Watering 4、Fertilizer 3、Sunflowers 1、Plant 1、Mazes 1、Megafarm 2；15项基础能力保留，Leaderboard等其余科技仍0。原版4机边界未记录的科技同样保留null，不使用其完整Reset最终等级替代。

### Power差额按同类金币日志单列

以最后target=8000的gold日志为同口径：原版Power340.957500，候选359.756667，多18.799167。按各自有时刻的收花记录累加，到该日志毛Power为1262/1292，已结算支出921.042500/932.243333。候选4机停机快照Power359.756667；原版4机日志未记录Power，该精确边界的净库存差保持null，不把稍早的gold日志值当成4机库存。

证据在 `.codex/leaderboard-sol/reset/early-speed2/four-drones/` 的 `source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.jsonl`、`seed1.client.json`、`comparison.json`及`three-times.json`。完整Reset本地模拟预估时间、短时打榜测试时间和游戏打榜时间均仍为null；前缀领先不代填完整净收益。

按本阶段停止条件，4机领先保留后先交Astra核算下一边界；当前没有进入step4或整轮，不扩seed、不部署实机。正式py和Save0未修改，旧候选及三值分别保留。

## 提前Speed 2完整seed 1：Power回吐后慢456秒，停止候选

按4机资源与南瓜用料预算，单次延伸完整seed 1。完整候选SHA `3ec2e8436302c86a4fe3edd92897f5c4faecaa7ad0a739f2f104f667bd15f391`，只从4机副本删除新增return，正式270c7b99仅多入口farm_wood_until(20)、unlock(Unlocks.Speed)两行；其余全模块AST相同，不并入已验证骨头尾段。原reset场景、CLI总75秒、300万API、1500万检查点，不开trace，保留5秒进度及30秒无进度停止。

工作45.677秒正常结束，1495521次API、6040390检查点，Leaderboard 1。前10条输出与4机前缀逐字相同，未重跑原版或扩seed。复用原版完整10114.199877606秒，候选10570.199931311秒，慢456.000053705秒（4.509%）；完整本地净收益不成立，停止本方向的扩样、合并和实机。

### 前缀领先在哪保留、在哪回吐

| 边界 | 原版游戏秒 | 候选游戏秒 | 候选领先游戏秒，负数为落后 |
| --- | ---: | ---: | ---: |
| 4机 | 2089.608527 | 1958.255191 | 131.353335 |
| step4 | 2899.004323 | 2752.919897 | 146.084426 |
| 8机 | 3743.639371 | 3573.336279 | 170.303093 |
| 1M金币 | 6685.577702 | 6676.030027 | 9.547676 |
| 首bone_prep | 7103.166441 | 7531.469713 | -428.303272 |
| 报告正常结束 | 10114.199878 | 10570.199931 | -456.000054 |

| 区间 | 原版耗时 | 候选耗时 | 候选减原版（游戏秒） |
| --- | ---: | ---: | ---: |
| 4机→step4 | 809.395796 | 794.664706 | -14.731091 |
| step4→8机 | 844.635048 | 820.416382 | -24.218667 |
| 8机→1M金币 | 2941.938331 | 3102.693748 | 160.755417 |
| 1M金币→首bone_prep | 417.588739 | 855.439687 | 437.850948 |
| 首bone_prep→报告正常结束 | 3011.033437 | 3038.730218 | 27.696781 |

区间差额加上4机时的−131.353335秒，精确闭合到整轮+456.000054秒。到8机仍领先170.303093秒，到1M金币仅余9.547676秒；随后准备到首bone_prep多437.850948秒，成为主要回吐区间。1M金币日志Power由原450.880333变为候选0；首轮apple_prep的Power由103.402167变为0。

### 两大Weird批次更快，联产Power减少

| 批次 | Weird原耗时 | Weird候选耗时 | 后续金币原耗时 | 后续金币候选耗时 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 370.806599 | 347.449248 | 1021.084915 | 1151.630552 |
| 2 | 640.209652 | 411.072842 | 909.538892 | 1192.242833 |

| 批次 | 原毛Power | 候选毛Power | 原批末净Power | 候选批末净Power |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3266 | 2894 | 660.904000 | 528.919167 |
| 2 | 6221 | 3560 | 1371.934000 | 635.988000 |

两批毛Power合计9487→6454，少3033。毛收入来自原始报告中带时刻的向日葵成熟收获记录，批末净库存来自对应日志，未用库存变化冒充产电量。阶段账与Power库存支持联产资源减少后在金币和准备阶段回吐的判断；资源、田面、补给时序和随机轨迹也已改变，未进行只改变Power的状态干预，不能把全部456秒严格归因给单一因素。

### 25轮骨头和完整末态

两版均完成25轮，每轮81796 Bone，累计2044900，解锁Leaderboard后余44900。所有bone_prep的剩余轮数、Cactus库存和Pumpkin496配对一致：首轮Cactus37360，每轮消耗1144，库存扣除剩余轮需求的余量恒8760，期末Cactus8760。snake随机流抽样数均53558；未以完整move总数替代骨头段路径证据。原版仅第1轮apple_prep开始Power为正，候选25轮开始均0；25轮的日志、各轮耗时与差额完整保存在comparison.json。

两版最终全部科技字典相同，Leaderboard均1。完整库存如下：

| 末态库存 | 原版 | 候选 | 候选减原版 |
| --- | ---: | ---: | ---: |
| Bone | 44900 | 44900 | 0 |
| Cactus | 8760 | 8760 | 0 |
| Carrot | 25457 | 20554 | -4903 |
| Fertilizer | 1743 | 2043 | 300 |
| Gold | 200 | 200 | 0 |
| Hay | 91913 | 82615 | -9298 |
| Piggy | 0 | 0 | 0 |
| Power | 0 | 0 | 0 |
| Pumpkin | 496 | 496 | 0 |
| Water | 6883 | 7349 | 466 |
| Weird_Substance | 71 | 131 | 60 |
| Wood | 1082290 | 834445 | -247845 |

| 时间名称 | 本候选游戏秒 | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 10570.199931 | 仅seed 1一次完整正常结束，配对原版10114.199878；候选慢456.000054 |
| 短时打榜测试时间 | 未取得 | 完整本地候选变慢，未进入实机 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据在 `.codex/leaderboard-sol/reset/early-speed2/full/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.progress`、`seed1.client.json`、`comparison.json`及`three-times.json`。A段与4机副本的三值null记录保持历史原样，不用完整候选值覆盖不同SHA的观测版本；骨头尾段9912.481057秒候选也独立保留。

结论限于本次完整seed 1：该候选完整时间更慢，停止扩seed，不将前缀成功作为整轮准入后的成功结果。不继续调参、合并骨头尾段或部署实机；正式py、lb_start和真实Save0均未修改。此记录不是同seed实机精度验收或榜单成绩。

## 正式原版晚段备电：资源受限产电组件通过本地成本门槛

本方向以正式原版270c7b99的1M金币后备电为研究对象，独立于已停止的提前Speed 2分支。本次只验证产电组件，未修改完整Reset。算法来源为已实机确认的Sunflowers Single（SHA556dd19a）；原7个算法函数AST均保持，只把Power目标改为2100、MAX_BATCHES改为8，并用独立入口在生产结束后恢复12×12、执行clear。组件SHA `b99c4e9f506b07176fb78767ebeaec8b7f6ed18b246c27c9b66023126b2cbd2a`。

场景是明确构造的资源受限组件，不是精确1M金币快照，也不声称最坏时间上界。Reset预设保留初始15项基础能力，相关生产等级为Speed 5、Expand 6、Sunflowers 1、Watering 4、Carrots 4，补齐Plant 1前置，Grass 1；Megafarm、Fertilizer及其余生产科技为0。初始Carrot2000，Power/Water/Fertilizer及其他全部生产库存0，允许Watering 4被动供水。完整全部科技、库存和场景哈希写入scenario.json与source-manifest.json，没有借用原版最终库存。

只执行seed 1一次CLI，30秒总墙钟、10万API、200万检查点，不开trace；保留5秒进度、支撑单格256次重抽和单株12秒成熟等待上限。工作0.969秒正常完成，77544次API、94749检查点，无支撑/成熟限额触发。单机且无spawn调用，结束无未完成工作者。

| 组件验收项 | 本次结果 |
| --- | --- |
| 全部初始化、支撑、生产、恢复、clear及调度的总游戏时间 | 109.799881934秒，≤250秒 |
| 支撑准备完成原日志 | 21.002526105秒 |
| 生产批次数 | 5，≤8；生产目标2100已达到 |
| 恢复前原日志 | 109.711815584秒，Power2103.345333 |
| 恢复后原日志 | 109.778153414秒，12×12、Power2103.345333 |
| 最终地图与清场 | 12×12，144个Grass；clear调用1次 |
| 无资源透支 | 全部末态库存非负；资源账与API计数吻合 |

总成本使用完整报告predicted_game_seconds，包含脚本定义与入口、所有准备及恢复，不以生产循环片段代替。恢复后原日志与报告收尾相差0.021728520秒，同样纳入总成本；恢复后Power2103.345333，高于2000门槛。

### 实际资源和Power账

| 资源或动作 | 本次结果 |
| --- | --- |
| Carrot | 初始2000，种花支付368，结束1632 |
| Water | 初始0，被动收到87，使用75，结束12 |
| Fertilizer | 初始、使用、结束均0 |
| 成熟向日葵收获 | 273次，全部8 Power，共2184毛Power |
| 支撑重抽的未成熟收割 | 84次，无产电收益 |
| 支撑与生产的总种植 | 368次，与Carrot支出一致 |
| Power | 初始0，毛收入2184，结束净2103.345333，已结算支出80.654667 |
| 其余库存 | Bone/Cactus/Gold/Hay/Piggy/Pumpkin/Weird/Wood均0 |

Watering 4始终不变，补给每1.25游戏秒触发一次，因此总时长内收到87份；使用次数75与use_item计数、库存差一致。Power毛净差只列已结算支出，不把未结算used_power补造进账。九株7瓣支撑、整批降序与延迟重种逻辑及其限额沿用来源版本；全部准备和清场损失已包含在368 Carrot与总时间内。

证据在 `.codex/leaderboard-sol/reset/power-reserve/` 的 `component_power_reserve.py`、`scenario.json`、`source-manifest.json`、`seed1.json`、`seed1.client.json`、`comparison.json`及`three-times.json`。场景与报告均附哈希，来源函数复用以AST核对，未扩大seed或调参重跑。

| 完整Reset时间名称 | 本项值 | 原因 |
| --- | --- | --- |
| 本地模拟预估时间 | 未取得/null | 仅产电组件，109.800秒不代填完整Reset |
| 短时打榜测试时间 | 未取得/null | 未部署实机 |
| 游戏打榜时间 | 未取得/null | 无本方向完整正常结束的官方统计 |

结论：仅通过本场景、单seed的组件成本门槛。实际1M金币处的资源、田面、Power及计时器相位尚未在此复现；通过后先交Astra核算调用位置、清场损失和整合成本，再决定后续方案，当前不运行完整新候选。正式Reset与Sunflowers Single脚本、lb_start和真实Save0均未修改，原有实机队列不变。

## 正式原版晚段备电完整seed 1：净省1420.900秒

完整候选SHA `62be28920e16185157743298ea0232be3a5a5389eab75b1cea777885201c1259`，以正式270c7b99为底，仅在step5的farm_gold_until(1000000)返回后、upgrade_dinosaurs_for_bones前加入备电。新增常量、七个嵌套helper及日志均在该处执行，使用reserve_局部命名，模块顶部与其余AST节点保持。七个向日葵函数逆向改名后与已确认来源AST一致，目标2100、8批、支撑256次与成熟12秒限额保持；不混入提前Speed 2或骨头尾段。

成功及原支撑/成熟限额正常返回后统一恢复原12×12并clear，再检查目标、恢复Power≥2000、地图12及成本≤250。保护失败会停止step5，不能仅凭CLI completed认定成功；本次全部验收成立且Leaderboard 1。仅seed 1一次、原reset场景、CLI75秒/300万API/1500万检查点，无trace，5秒进度和30秒无进度停止；工作50.757秒正常结束，1781697次API、6723919检查点。

从start到末次1M金币日志的68条输出与原版逐字相同，包括全部阶段时间和已记录库存。末次1M金币时间均6685.577702430秒；新增定义未改变此前计费。完整时间10114.199877606→8693.299864050秒，净省1420.900013556秒（14.049%）。这是一个完整seed的本地筛选结果，尚非跨seed保证或实机成绩。

### 真实晚段输入与备电成本

入口原日志6685.578525480秒，恢复原日志6751.021370910秒，验收日志6751.024333890秒；实际备电成本65.444656140秒，包含该处新增定义、准备、收花、恢复和资源记录。实际运行4批；不使用构造组件的109.799882秒代填。

| 库存 | 实际入口 | 恢复后 | 账目 |
| --- | ---: | ---: | --- |
| Carrot | 25816 | 25518 | 种花支付298 |
| Water | 4140 | 4018 | 被动收到52，使用174 |
| Fertilizer | 372 | 398 | 被动增加26，无施肥 |
| Power | 450.880333 | 2104.449333 | 毛产1720，已结算耗66.431，净增加1653.569 |
| Cactus | 17680 | 17680 | 不支出 |
| Pumpkin | 208 | 208 | 不支出 |

实际入口Hay89673、Wood1082290、Weird71、Gold1000200、Bone0、Piggy0，恢复后这些库存均不变。215次向日葵成熟收获产1720 Power；入口已有450.880333 Power和4140 Water，解释了实际成本与缺水零Power构造组件不同。场景、田面及随机计时器由完整原版前缀实际产生，未替换为组件快照。

### 净收益如何闭合

| 区间 | 原版游戏秒 | 候选游戏秒 | 候选减原版 |
| --- | ---: | ---: | ---: |
| 1M金币→首bone_prep | 417.588739 | 488.364948 | 70.776209 |
| 首bone_prep→正常结束 | 3011.033437 | 1519.357214 | -1491.676223 |

首bone_prep由7103.166441000延至7173.942650430秒，包含备电后总准备多70.776209430秒；首prep至完整结束从3011.033436606降至1519.357213620秒，省1491.676222986秒，扣除前段成本后精确闭合净省1420.900013556秒。首轮apple_prep开始Power由103.402167升至1751.708333；原版仅第1轮开始有Power，候选25轮开始均为正，末态仍余138.004000。

全部25轮各产81796 Bone，Cactus每轮消耗1144，首prep37360、Pumpkin496、剩余轮数配对一致；库存减全部剩余轮需求的余量恒8760。最终Bone44900、Cactus8760、Gold200、Pumpkin496，Leaderboard 1及全部科技与原版相同。各轮完整日志和时间差保存在comparison.json；snake抽样均53558，Cactus1440/Maze548940/Pumpkin73100/random334计数也相同。新增种花使Sunflower6054→6352、Poly188454→190340，Various随时长与清场改变，未宣称全部随机流不变。

其他末态Carrot25159、Hay91929、Wood1082290、Fertilizer1175、Water5572、Weird71、Piggy0。末态全部库存与科技字典在comparison.json分别保留，减少的被动水肥不掩盖在时间收益内。

| 时间名称 | 本候选游戏秒 | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 8693.299864 | 仅seed 1一次完整正常结束且备电验收成立，配对原版10114.199878 |
| 短时打榜测试时间 | 未取得 | 本轮仅本地完整筛选，未进入实机 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

证据在 `.codex/leaderboard-sol/reset/power-reserve/full/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1.progress`、`seed1.client.json`、`comparison.json`及`three-times.json`。构造组件、失败的提前Speed 2和原骨头尾段候选均保留独立版本及三值，不用本次值覆盖其他SHA。

本阶段只确认单seed完整本地净收益，交Astra核对并判断下一验证；不自动扩seed、合并尾段、迁正式脚本或实机。正式Reset与Sunflowers Single脚本、lb_start及真实Save0均未修改。

## 晚段备电同SHA完整seed 0/1：本地均值8665.198秒

在seed 1完整配对通过后，仅按同SHA `62be28920e16185157743298ea0232be3a5a5389eab75b1cea777885201c1259`补seed 0一次；原reset场景、CLI75秒/300万API/1500万检查点、无trace及原进度/停止/回收机制保持。未修改2100目标，未合并骨头尾段，seed 1及两份原版报告均复用且哈希核对保持。

| seed | 原版完整游戏秒 | 备电候选完整游戏秒 | 净省游戏秒 | 改善 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 9899.899869 | 8637.096751 | 1262.803118 | 12.756% |
| 1 | 10114.199878 | 8693.299864 | 1420.900014 | 14.049% |
| 两seed均值 | 10007.049873 | 8665.198308 | 1341.851566 | 13.409% |

seed 0工作57.775秒正常完成，Leaderboard 1、备电保护通过。该seed从start到末次1M金币的68条日志与对应原版逐字一致；seed 1同样通过68条前缀核对。两个完整样本均正常且有净收益后才计算本地均值，不将触限、前缀或组件值纳入。

### 两组实际备电成本和资源

| seed | 备电游戏秒 | Carrot消耗 | Water消耗 | 恢复Power | 末态Power |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 63.463081 | 307 | 174 | 2101.424667 | 156.598167 |
| 1 | 65.444656 | 298 | 174 | 2104.449333 | 138.004000 |

seed 0实际入口6652.843860302秒，Carrot33591、Power589.609833、Water4143、Fertilizer321；恢复6716.305130552秒，Carrot33284、Power2101.424667、Water4020、Fertilizer346。197次成熟收花产1576 Power，已结算耗64.185167，净增加1511.814833。被动供水51、使用174，肥料被动增加25且无施肥。Hay95532、Wood1423223、Weird96、Cactus17680、Pumpkin208、Gold1000200、Bone0和Piggy0在备电入口与恢复之间均不变。

两组都恢复原12×12并clear，成本低于250、目标已达到且恢复Power高于2000。实际输入来自各自完整前缀；没有沿用构造组件的Carrot2000/Power0/Water0输入或109.800秒成本。

### 25轮与后段闭合

| seed 0区间 | 原版游戏秒 | 候选游戏秒 | 候选减原版 |
| --- | ---: | ---: | ---: |
| 1M金币→首bone_prep | 419.488338 | 489.009067 | 69.520729 |
| 首bone_prep→正常结束 | 2827.568494 | 1495.244647 | -1332.323847 |

seed 0首bone_prep前多69.520729秒，其后省1332.323847秒，闭合完整净省1262.803118秒；seed 1对应多70.776209、省1491.676223，净省1420.900014秒。两组均完成25轮，每轮81796 Bone、1144 Cactus，prep剩余轮数、Cactus/Pumpkin配对；余量恒8760。两组候选25轮开始均有Power，最终仍为正。

snake计数按seed配对相同：seed 0为57062，seed 1为53558。各组最终全部科技均与各自原版相同，Leaderboard均1，Bone44900、Cactus8760、Gold200、Pumpkin496。未声称全部随机流不变；新增种花和清场带来的Sunflower/Poly/Various变化在各自比较文件单列。

seed 0其他末态Carrot32919、Hay97788、Wood1423223、Fertilizer1114、Water5556、Weird96、Piggy0，Power156.598167。seed 1末态和25轮记录保留在其原始比较文件中，不用跨seed库存互相填补。

| 时间名称 | 同SHA两seed当前值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 8665.198308 | 完整seed 0/1均值，配对原版10007.049873，净省1341.851566 |
| 短时打榜测试时间 | 未取得 | 本阶段仅两seed本地确认，未部署实机 |
| 游戏打榜时间 | 未取得 | 无本候选完整正常结束的官方统计 |

新增证据在 `.codex/leaderboard-sol/reset/power-reserve/full/` 的 `seed0-manifest.json`、`seed0.json`、`seed0.progress`、`seed0.client.json`、`comparison-seed0.json`、`comparison-seeds0-1.json`及`three-times-seeds0-1.json`。原`seed1.json`、`comparison.json`及单seed `three-times.json`作为历史完整保留，脚本SHA不变。

结论限于这两个完整本地配对：均有净收益，尚不构成统计置信度、实机精度验收或榜单成绩。候选队列与尾段合并交Astra判断，本阶段不继续扩seed或变体、不迁正式py或实机。正式Reset与Sunflowers Single脚本、lb_start及真实Save0保持。

## 晚段备电与固定尾段组合：两seed本地均值8617.893秒

组合SHA `6ae88cad1613e1beab8157d02dd23e4536e479c0b878fe70cf94ab2061899677`，以纯备电62be2892为底，只换入旧acb8130f已验证的固定绕环尾段。追击前缀、其他AST节点、模块顶部、2100Power目标和备电保护均保持；不混入已失败的提前Speed 2。执行顺序严格为seed 1先跑一次并验收，再按同SHA运行seed 0一次，均沿原场景75秒/300万API/1500万检查点、无trace、5秒进度/30秒无进度停止；原版、纯备电和已有种子报告均不重跑。

先行seed 1全部条件成立才准入seed 0：完整正常且Leaderboard 1、至首bone_prep含该日志的92条输出与纯备电逐字同、备电保护通过、25轮材料/移动次数与动作tick/snake配对、骨头持续有电，增量处于40～55游戏秒。seed1-admission.json保存了13项条件全部通过的结果，之后才产生seed0客户端记录。

| seed | 正式原版游戏秒 | 纯备电游戏秒 | 组合游戏秒 | 相对纯备电再省 | 相对原版共省 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 9899.899869 | 8637.096751 | 8588.899931 | 48.196820 | 1310.999938 |
| 1 | 10114.199878 | 8693.299864 | 8646.885112 | 46.414752 | 1467.314766 |
| 两seed均值 | 10007.049873 | 8665.198308 | 8617.892521 | 47.305786 | 1389.157352 |

两次均完整且验收成立后才计算组合均值。相对正式原版净省13.882%，相对纯备电平均再省47.305786秒；不将旧无Power尾段约95秒直接叠加到持续供电版本。

### 移动、材料和持续供电

| seed | 两版相同move数 | 两版相同move动作tick | 两版相同snake抽样 | 组合末态Power |
| --- | ---: | ---: | ---: | ---: |
| 0 | 399520 | 73352111 | 57062 | 205.431333 |
| 1 | 343904 | 62469874 | 53558 | 184.965000 |

两组都与各自纯备电版本逐字匹配首prep前92条日志，备电入口/恢复资源和保护条件不变。25轮各产81796 Bone，Cactus每轮消耗1144，首prep37360，剩余轮数和Pumpkin496相同，库存扣除剩余需求后恒余8760。最终Leaderboard 1、全部科技相同，Bone44900、Cactus8760、Gold200、Pumpkin496。

25轮开始Power均为正，首prep以后没有向日葵Power收入，结束Power仍205.431333/184.965；此段只消费Power，证明骨头期间未耗尽电。两组完整API计数仅measure减少：seed 0为91192→45154，seed 1为90490→46215；移动次数与动作tick相同，未靠换路径或少供料取得增量。

组合与纯备电的其他生产库存配对相同。被动库存因更早结束而减少：seed 0 Fertilizer1114→1095、Water5556→5518；seed 1 Fertilizer1175→1156、Water5572→5535。骨头以后原流程只支付Leaderboard的Gold/Bone，不存在这些水肥的后续消费；Power余量相应增加。所有末态字典及25轮完整日志分别保留。

### 实际tick预算与报告收尾

| seed | 少解释器tick | 少API tick | 实际tick纳秒 | 末done日志省秒 | 报告总时间省秒 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 246668 | 46038 | 164610 | 48.182334660 | 48.196820340 |
| 1 | 237818 | 44275 | 164610 | 46.435328730 | 46.414752480 |

实际tick_ns为164610。两版少执行的解释器和API tick乘该长度，等于各自末次done日志差；完整报告时间还包含末日志之后的调度收尾。seed 1收尾由0.012181140变为0.032757390，多0.020576250秒，因此报告增量46.414752480秒小于末日志差46.435328730秒。两seed这项账均已精确闭合，完整本地时间统一采用报告值；这是模型内部计时解释，不是实机精度证明，不据此修改模型或重跑。

| 时间名称 | 组合当前值（游戏秒） | 依据 |
| --- | ---: | --- |
| 本地模拟预估时间 | 8617.892521 | 同SHA完整seed 0/1均值；较纯备电再省47.305786，较原版共省1389.157352 |
| 短时打榜测试时间 | 未取得 | 本轮仅顺序本地配对，未部署实机 |
| 游戏打榜时间 | 未取得 | 无本组合完整正常结束的官方统计 |

组合证据在 `.codex/leaderboard-sol/reset/power-reserve/combined/`：`source-manifest.json`、`lb_fastest_reset.py`、`seed1.json`、`seed1-admission.json`、`seed0.json`、两份客户端记录与进度、`comparison-seed0.json`、`comparison-seed1.json`、`comparison-seeds0-1.json`、`timing-budget.json`及`three-times.json`。纯备电和正式原版报告、各历史三值独立保留。

结论限于两个完整本地样本：组合增量与总收益均成立，尚非统计置信度、实机精度验收或榜单成绩。经协作#94独立复核，组合6ae88cad已列为Reset首选待实机候选，纯备电和单独尾段保留作对照；Hay与Carrot Single仍在前。停止本轮本地扩seed、调参和重跑，不调整2100目标、不迁正式py或变更Save0；请求79未收口时不提交新实机请求，恢复后沿短测、模型差异核对、完整统计、迁真源复验流程。
