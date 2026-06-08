# lb_wood

## 榜单目标

- 目标资源：`Items.Wood`
- 多无人机路线
- 当前脚本目标数量为 `10000000000`

## 收益机制说明

- 木头榜和胡萝卜、草一样，本质也是 companion 榜，只是主作物换成了树。
- 这榜的主基调非常明确：
  - 主体一定是种树
  - 树之间不能相邻
- 因为树不能相邻，所以树位之间天然需要穿插别的格子来做 support。
- 在所有可接受伴生里，灌木是最理想状态：
  - 它能满足树的伴生需求
  - 同时灌木自己也会产木头
- 换句话说，木头榜最自然的好局面就是：
  - 主格种树
  - support 格尽量变成灌木
- 这也是为什么木头榜虽然表面上跟胡萝卜、草不同，但思考方式其实类似：
  - 先明确主作物是什么
  - 再明确哪些伴生是最佳、哪些伴生只是次优、哪些直接废掉

## 当前基线

- 当前默认入口：`main3()`
- 当前路线：外部 `Save0/wood.py` 修正目标后的 32 无人机 Tree/Bush 交替路线；不再用 `Wood > Hay` 作为退出条件，而是明确跑到 `10,000,000,000 Wood`
- 真实短窗口记录：
  - 旧 `main1` 记录：`28:36.265`
  - `main2` 初版：1 轮 `18:16.992`，但有大量并发用水 / 用肥不足警告
  - `main2` 加库存阈值后：3 轮均值 `18:14.543`，警告消失
  - `main3` 迁入前验证：请求 `223` 两轮均值 `10:15.633`，单轮 `10:14.297` / `10:16.968`
  - `main3` 真源同步后验证：请求 `224` 两轮均值 `10:22.886`，单轮 `10:21.919` / `10:23.854`
  - `main3` 2026-05-30 当前版本复跑：请求 `614` 两轮 `10:22.851` / `10:16.770`，稳定均值 `10:19.811`；仍有大量 `Items.Water` 不足 warning，后续 `finished=false` 取消摘要不作为成绩
  - `main3` 2026-06-08 收益拆分探针：请求 `624` 两轮 `10:42.356` / `10:43.340`，稳定均值 `10:42.848`；慢于当前基线，探针不保留在 `.py`
  - Grass-only 动态 support：请求 `638` 完成 13 轮，最快 `7:36.580`，均值 `7:38.905`；相对 `10:19.811` 明显刷新，后续手动停止产生的 `finished=false runs=14 average=7:08.576` 不作为成绩
  - Grass+Carrot 动态 support：请求 `641` 完成 8 轮，最快 `7:06.871`，均值约 `7:08.255`；相对 Grass-only 继续刷新，但仍有少量 `不能在 Grounds.Grassland 上种植 Entities.Carrot` 警告
  - 未成熟 Bush 强制改 Carrot：请求 `660` 两轮 `6:40.746` / `6:40.073`，均值 `6:40.410`；相对 Grass+Carrot guard 版继续刷新
  - 剩余 reroll 来源探针：请求 `661` / `662` 确认剩余 reroll 主要来自 Tree-slot companion，探针不保留在 `.py`
- 当前仍慢于 #1 `3:44.313`，但相对 `main3` 已有明确进步
- 证据来源：真实游戏 `run_real_game_script.py` 请求 `56`、`57`、`223`、`224`、`614`、`624`、`638`、`641`、`642`、`660`、`661`、`662`

## 通用注意事项下的榜单特化

- `main3` 证明木头榜的第一原则需要修正：不是先追求“每棵树都有稳定 companion”，而是先确认“低调度成本的全图 Tree/Bush 吞吐”能不能直接压过复杂伴生维护路线
- 灌木是最理想伴生，因为它不是纯 support，而是还能继续产木头
- 所以多机木头榜的核心不是到处找奇怪结构，而是：
  - 主作物 Tree 与副产作物 Bush 的总吞吐
  - 为了稳定 companion 付出的 reroll / 移动 / 初始化 / 等待成本
  - 复杂 support 网络是否真的比“低成本反复种收”更划算
  - 为了追更复杂伴生值是否反而破坏了全图并行吞吐

## 新路线复盘：为什么 `main3` 更快

- `main3` 的核心优势不是更精细，而是更便宜：每个无人机只沿一列循环，按 `(x + y) % 2` 在 Tree / Bush 间交替种植，几乎没有寻路、claim、support 初始化、companion reroll 和跨无人机协调成本。
- `main2` 的理论收益来自“稳定 Bush companion + 双树单元”，但真实成本很重：每个单元先初始化大 support 区，再反复 `get_companion()` / `harvest()` / `plant(Tree)` reroll，很多 tick 花在维护结构，而不是直接收木头。
- `main3` 虽然没有强制每棵树吃到最优 companion，但它把 32 个无人机全部变成持续生产线；Tree 和 Bush 都产 Wood，Bush 不只是 support，因此全图直接吞吐超过了低并行度的精修单元。
- `main3` 的并发缺水警告看起来很糟，但实测改水阈值会变慢，说明当前瓶颈不是警告本身，而是高频补水带来的成熟加速收益仍大于警告损耗。
- 之前思考的主要问题是把“木头榜本质是 companion 榜”理解得过窄，过早把优化空间锁死在“树位稳定 + Bush support 稳定”，没有先做最低成本全图吞吐基线。
- 以后遇到类似榜单，必须先做两个基线对照：一个是机制精修路线，一个是低调度成本暴力吞吐路线；只有暴力吞吐被真实验证压下去后，才继续深挖复杂 companion 网络。

## 当前版本结论

- `main1`
  - 用 Tree/Bush 棋盘来提高 Bush companion 的自然命中率，同时避免更复杂的动态 support 逻辑
  - 旧记录 `28:36.265`，已被 `main2` 淘汰
- `main2`
  - 32 个非相邻双树单元，只接受 Bush companion
  - 真实均值 `18:14.543`
  - 结论：固定 Bush support 方向有效，但当前单元吞吐仍远低于榜前，需要继续减少 reroll / 等待 / 支撑初始化成本
- `main3`
  - 来源：外部 `Save0/wood.py`，但原始 `exit_condition()` 是 `Wood > Hay`，会提前结束，不能直接用于木头榜
  - 迁入修正：改为 `num_items(Items.Wood) >= 10000000000`，并内联 `utils.py` 中的 `use_water()` / `harvest_if_can()`，避免向真实存档新增依赖文件
  - 2026-05-30 当前版本复跑均值 `10:19.811`
  - 结论：已被 Grass-only 动态 support 刷新；保留为旧低成本 Tree/Bush 扫描基线
- Grass-only 动态 support
  - 改法：仍保留 32 无人机 Tree/Bush 奇偶扫描；Tree 位成熟时读取 `get_companion()`，若伴生是 Bush 且坐标落在 Bush 奇偶格则直接收 Tree，若伴生是 Grass 且落在 Bush 奇偶格，则同一无人机移动过去把 support 改成 Grass，再回 Tree 位收割
  - Bush 位仍按旧逻辑正常收割并重种 Bush，避免把 Bush 完全冻结为纯 support
  - 请求 `638` 完成轮：`7:36.580`、`7:37.489`、`7:37.508`、`7:40.528`、`7:39.840`、`7:39.990`、`7:38.651`、`7:40.546`、`7:37.908`、`7:37.454`、`7:39.134`、`7:42.153`、`7:37.990`
  - 13 轮均值 `7:38.905`，最后两轮差异约 `0.9%`；`output.txt` 记录的 `finished=false runs=14 average=7:08.576` 是手动停止后的取消摘要，不作为有效成绩
  - 每轮统计显示 Grass rewrite 大约 `336~379` 次、static Bush 大约 `340~406` 次，证明 Grass companion 动态兑现是本次刷新来源
  - 结论：已被 Grass+Carrot 动态 support 刷新；保留为低 churn 对照。
- Grass+Carrot 动态 support
  - 改法：保留 32 无人机 Tree/Bush 奇偶扫描和 Grass 动态改写；Tree 位 companion 为 Carrot 且落在 Bush 奇偶格时，同无人机移动过去，必要时收割旧 support、`till()` 到 Soil、确认库存后 `plant(Entities.Carrot)`，再回 Tree 位收割。
  - Bush 位不再无条件覆盖未成熟 support；如果已有未成熟实体就跳过，成熟后收割，并把非 Grassland 地块 `till()` 回草地再 `plant(Entities.Bush)`。
  - 请求 `641` 完成轮：`7:08.850`、`7:09.447`、`7:08.612`、`7:08.542`、`7:08.156`、`7:07.888`、`7:06.871`、`7:07.670`。
  - 8 轮均值约 `7:08.255`，最快 `7:06.871`，稳定刷新 Grass-only 的 `7:38.905`。
  - 统计显示每轮约 `269~294` 次 Carrot request，其中约 `166~200` 次成功 rewrite，reroll 从 Grass-only 的约 `902~961` 降到约 `522~558`。
  - 仍会出现少量 `不能在 Grounds.Grassland 上种植 Entities.Carrot` 与水不足警告；这些 warning 未阻止有效完成轮，但后续若继续 Wood，可单独研究更低噪声的 Carrot 写入或补水节奏。
  - 结论：作为当前默认入口；锁版 request `642` 证明简单 support lock 不能消除 Carrot 地块 warning，且会把均值拖慢到 `7:13.784`。

## 失败对照

- 2026-04-24 `main2` 初版没有库存阈值
  - 真实 1 轮 `18:16.992`
  - 输出大量 `Items.Water` / `Items.Fertilizer` 不足警告
  - 后续用库存阈值压掉警告，均值小幅提升到 `18:14.543`
- 2026-04-24 降低补水 / 施肥阈值
  - 真实 4 轮均值 `18:16.608`
  - 输出大量 `Items.Water` / `Items.Fertilizer` 不足警告
  - 结论：多机并发下低阈值会放大资源抢占和警告开销，不如保留当前库存阈值
- 2026-04-25 删除两个不可能成为任一树位 companion 的支撑点 `(-3, 1)` / `(3, 1)`
  - 真实 3 轮均值 `18:16.497`
  - 慢于当前基线 `18:14.543`
  - 结论：裁剪支撑区没有减少足够成本，反而削弱了稳定灌木支撑，不保留实现
- 2026-04-25 外部 `Save0/wood_lb.py` 候选
  - 覆盖真实存档既有 `lb_wood.py` 后请求 `219`
  - `LogOutput.log` 的 `item_snapshot` 显示约 8 秒 `wood=8746807040`，约 9 秒 `wood=9856929024`
  - 游戏 `output.txt` 新增 `run=` 行数为 0，模组返回 `leaderboard finished without completed runs`
  - 结论：资源增长很快，但没有触发 leaderboard 完成轮，疑似目标判定 / 最终 harvest / 结算时机不对；不能直接迁入，后续只能作为“高产结构”拆解参考
- 2026-04-25 重新读取当前 `Save0/wood_lb.py` 后复测
  - 请求 `252` 仍无任何 `run=`
  - `item_snapshot` 显示约 9 秒 `wood=9624283392`，接近目标但最终仍 `leaderboard finished without completed runs`
  - 结论不变：结构可作为参考，当前文件不迁入
- 2026-04-26 修正 `Save0/wood_lb.py` 真实结算目标后复测
  - 临时迁入为 `main4`，把退出条件修成 `num_items(Items.Wood) >= 10_000_000_000`，并补最后 leaderboard 结算
  - 请求 `285` 完成 1 轮，`[lb_wood] finished=true runs=1 average=141:32.734`
  - 脚本输出 `main4 done wood=10000180992 time=8492.71`
  - 结论：修目标后可以结算，但游戏内时间远慢于当前 `main3` 的约 `10:15~10:23`；之前现实约 9 秒接近 10B Wood 只是高模拟速度下的现实时间现象，不能当 leaderboard 游戏时间
  - 处理：不迁入默认入口，只保留“外部脚本必须先修真实目标再评估”的反例证据
- 2026-04-25 `main3` 水阈值变体
  - 把 `use_water()` 改成 `num_items(Items.Water) > 128` 后两轮均值 `10:35.912`
  - 改成 `num_items(Items.Water) > 0` 单次补水后两轮均值 `10:32.253`
  - 两者都慢于原始 `while get_water() < min(num_items(Water) / 100, 0.75)` 的 `10:15.633`；虽然原始写法有并发缺水警告，但净收益仍更高，暂时保留原始补水节奏
- 2026-04-30 `main3` 多无人机探针
  - 请求 `399` 只加 `wood_multi_probe` 日志，不改变产木策略。
  - 真实完成轮：`run=1 time=10:25.487`、第二轮后 runner 停表 `reached stable leaderboard runs 2 avg=10:20.343`。
  - 探针持续输出 `wood_multi_probe drones=32 start=(0,0)`，并且 `(0,0)` worker 的位置沿同一列变化，证明当前 `main3` 实际使用 32 个 worker 并行生产，不是单无人机路线。
  - 结论：用户指出“多机榜像只用了 1 个无人机”的怀疑在当前 `main3` 代码上不成立；探针已从 `.py` 回退，只保留本记录。后续优化重点不是“启用多机”，而是重写更高产的 32 机协作结构。
- 2026-05-30 `main4` 低移动显式 Bush companion 筛选
  - 改法：保留 `main3` 的 32 无人机按列移动和 Tree/Bush 棋盘；树格成熟时调用 `get_companion()`，只有 `companion_entity == Entities.Bush` 且 companion 坐标落在 Bush 奇偶格时才视为有效，否则收割并重种树以重刷 companion。
  - 请求 `600` 使用 `20s` timeout，在首轮完成前被取消；`item_snapshot` 在 `game_time=503.684` 时为 `wood=7937406464`，取消摘要 `finished=false runs=1 average=8:44.772` 不作为有效成绩。
  - 请求 `601` 使用 `45s` timeout，真实新增完成轮 `run=1 time=10:18.888`，脚本输出 `main4 done wood=10000461312 time=618.77`。
  - 请求 `601` 的取消摘要 `finished=false runs=2 average=9:45.728` 不是有效刷新；`output.txt` 没有对应的第二条 `[lb_wood] run=2`。
  - 结论：该低移动显式 Bush 筛选没有刷新 `main3` 的历史 `10:15.633`，也没有稳定优于真源同步后的 `10:22.886`；只读 `get_companion()` 加筛选不足以让木头榜接近 100% 伴生收益，失败实现已从 `.py` 回退。
- 2026-06-08 `main3` Tree/Bush 收益拆分探针
  - 改法：不改变默认 Tree/Bush 扫描结构，只统计 Tree/Bush 收割次数、收割前后 Wood delta、Tree 位 companion 类型分布、水和肥料调用次数。
  - 请求 `624` 使用 `--max-leaderboard-runs 2`，真实完成轮为 `10:42.356` / `10:43.340`，稳定均值 `10:42.848`；慢于当前 `10:19.811`，不作为成绩刷新。
  - 第一轮：`tree_harvest=2757`、`bush_harvest=2915`、`tree_delta=2071226880`、`bush_delta=1776668928`、`companion_bush=995`、`companion_tree=7`、`companion_grass=1042`、`water_calls=524`、`fertilizer_calls=16`。
  - 第二轮：`tree_harvest=2759`、`bush_harvest=2934`、`tree_delta=1987860992`、`bush_delta=1834168064`、`companion_bush=1003`、`companion_tree=4`、`companion_grass=1007`、`water_calls=516`、`fertilizer_calls=13`。
  - 结论：Bush 自身贡献了约 `1.78B~1.83B` Wood，不是纯 support；冻结 Bush support 会直接损失大块产量，必须先算净收益。
  - Tree 位 companion 采样里 Bush 和 Grass 接近同量级，Tree 极少；当前结构不是稳定 Bush companion 路线。单纯加入统计和 `get_companion()` 开销也会显著拖慢，所以探针已从 `.py` 回退并重新同步 `gamesave/`。
- 2026-06-08 Tree/Bush 取舍离线模型
  - 输入：请求 `624` 两轮 Tree/Bush delta、当前 `10:19.811`、#1 `3:44.313`、companion 半径 `3` 和满级 `160x` companion 倍率。
  - 计数收益里 Tree 约占 `52.9%`，Bush 约占 `47.1%`；因此牺牲 Bush harvest 不是小代价。
  - 当前 Tree/Bush 棋盘的一种静态 support 理论命中率约为 `16 / (24 * 3) = 22.2%`；即使把 Tree 周围 `24` 个坐标都变成某种静态可用 support，因每格只能放一种实体，理论成功率也只有 `33.3%`。
  - 从 `22.2%` 提到静态上限 `33.3%`，Tree 侧理论收益约 `1.49x`，若 Bush 完全不损失，总收益也只有约 `1.26x`；不足以解释当前对 #1 的 `2.76x` 差距。
  - 若冻结 `25%` Bush harvest，Tree 侧至少要提升 `1.22x` 才能不退化；冻结 `50%` 时要 `1.45x`。要接近 #1，在不损失 Bush 的理想情况下 Tree 侧也要约 `4.33x`。
  - 结论：不要直接实机尝试“静态混合 support”“冻结一批 Bush”或“减少一批 worker 当 support”这类粗改；它们要么上限太低，要么需要 Tree 吞吐提升幅度不现实。下一步只有两类值得继续：能近似动态兑现 companion 且几乎不牺牲 Bush 的局部接力结构，或转向其他更可能推进的榜单。
- 2026-06-08 Grass-only 动态 support 接力
  - 离线预算 `.codex/tests/wood_dynamic_relay_budget.py` 估算 same-drone Grass-only distance<=3 为 `6:46.308`；实机请求 `638` 证明模型方向成立但偏乐观。
  - 真实完成 13 轮，均值 `7:38.905`，最快 `7:36.580`，稳定刷新旧基线 `10:19.811`。
  - 统计样例：第一轮 `static_bush=342`、`grass_request=357`、`grass_rewrite=357`、`reroll=950`；第十轮 `static_bush=347`、`grass_request=379`、`grass_rewrite=379`、`reroll=902`。
  - 结论：动态兑现 Grass companion 的收益足以覆盖同无人机移动和改写成本；已被 Grass+Carrot 动态 support 刷新。
- 2026-06-08 Grass+Carrot 动态 support
  - 用 Grass-only 实测校准旧预算后，Grass+Carrot distance<=3 估算约 `5:50.900`，相对 `7:38.905` 仍有约 `1.31x` 余量。
  - 请求 `640` 的安全版已有三轮 `7:10.150` / `7:09.016` / `7:05.698`，但仍缺少后续库存和地块 guard；作为方向成立证据，不作为最终默认版本成绩。
  - 请求 `641` 的 guard 版补入库存检查、Soil 复核和 Bush 位地块恢复，完成 8 轮，最快 `7:06.871`，均值约 `7:08.255`。
  - 请求 `642` 尝试 support lock 后三轮 `7:15.859` / `7:12.259` / `7:13.233`，均值 `7:13.784`；`support_lock_skip=0` 且仍有 Carrot Grassland warning，说明锁没有解决该 warning，失败实现不保留。
  - 结论：保留无锁 guard 版为默认入口；Carrot warning 属于已知噪声，后续如果处理，必须同时证明不损失当前约 `7:08` 的速度。
- 2026-06-08 Carrot 写入失败探针
  - 改法：临时只在 `rewrite_carrot_support()` 的失败路径增加统计，记录 `plant(Entities.Carrot)` 返回失败前后的 ground / entity；成功路径不改。
  - 请求 `643` 有效两轮 `7:11.941` / `7:06.210`，稳定均值 `7:09.076`，没有刷新当前 `7:08.255`。
  - 第一轮统计：`carrot_request=281`、`carrot_rewrite=178`、`carrot_skip=103`、`carrot_ground_fail=1`、`carrot_plant_fail=0`。
  - 第二轮统计：`carrot_request=289`、`carrot_rewrite=170`、`carrot_skip=119`、`carrot_ground_fail=0`、`carrot_plant_fail=2`、失败后状态为 `grassland=1 / soil=1`，实体为 `grass=1 / carrot=1`。
  - 运行中仍出现多条 `不能在 Grounds.Grassland 上种植 Entities.Carrot` warning，但实际 `plant()` 返回失败只有 0 / 2 次；warning 数量不等同于 companion 兑现失败数。
  - 结论：单纯消除 Carrot Grassland warning 不是主要优化源头；下一步应转向减少 `carrot_skip` / `reroll` 或寻找更低成本的动态接力，而不是继续给当前写入路径加锁或加日志。探针已从 `.py` 回退。
- 2026-06-08 Carrot skip 原因探针：
  - 改法：继续临时统计 `rewrite_carrot_support()` 的 False 出口，区分 support 未成熟、地块失败、材料不足和 `plant()` 返回失败。
  - 请求 `644` 有效两轮 `7:09.317` / `7:09.736`，稳定均值 `7:09.527`，没有刷新当前 `7:08.255`。
  - 第一轮 `carrot_skip=112`，其中 `unready=108`、`ground=2`、`cost=1`、`plant=1`；第二轮 `carrot_skip=96`，其中 `unready=94`、`ground=1`、`cost=1`、`plant=0`。
  - 结论：Carrot skip 几乎全部来自 support 位未成熟；材料、地块和 `plant()` 失败都不是主项。探针已从 `.py` 回退。
- 2026-06-08 unready support 一次补水救援：
  - 改法：遇到 unready support 时最多 `use_item(Items.Water)` 一次，若补水后 `can_harvest()` 成立则继续 harvest 并写入 Carrot，否则仍按原逻辑跳过。
  - 请求 `645` 有效两轮 `7:08.007` / `7:09.795`，稳定均值 `7:08.901`，没有刷新当前 `7:08.255`。
  - 第一轮 `carrot_skip_unready=85`、`carrot_unready_water=80`、`carrot_unready_rescue=1`；第二轮 `carrot_skip_unready=82`、`carrot_unready_water=75`、`carrot_unready_rescue=2`。
  - 结论：一次补水的救援率太低，还会引入额外水不足 warning；不保留。后续若继续处理 unready support，不能靠当前无人机补水硬救，必须改 support 更新节奏或结构。
- 2026-06-08 support 改写后补水候选：
  - 改法：在 `rewrite_grass_support()` / `rewrite_carrot_support()` 成功种下动态 support 后，仍停在 support 格时做一次库存门槛补水，目标是把 support 成熟时间前移，减少后续 `carrot_skip`。
  - 请求 `646` 同时补 Grass / Carrot support，两轮 `7:10.030` / `7:07.109`，均值 `7:08.569`，慢于当前 `7:08.255`；统计为 `support_water=146/149`、`carrot_skip=74/89`。
  - 请求 `647` 收窄为只补 Grass support，两轮 `7:11.024` / `7:06.699`，均值 `7:08.862`，仍慢于当前 `7:08.255`；统计为 `support_water=123/119`、`carrot_skip=111/86`。
  - 结论：前置补水能在部分轮次降低 `carrot_skip`，但额外 `use_item(Items.Water)` 动作和水资源竞争抵消了收益；不保留。单轮 `7:06.699` 只是短窗波动，四轮合并均值仍慢于当前默认版。
- 2026-06-08 动态 support 写入后施肥：
  - 第一版在 Grass / Carrot support 新写入后尝试 `num_items(Items.Fertilizer) > 100` 再施肥，但主循环 Tree 位施肥会先消耗库存；request `655` 两轮 `7:12.199` / `7:10.366`，均值 `7:11.283`，且 `support_fertilizer=0`，等于没有真正触发 support 施肥。
  - 第二版改成有肥就优先给动态 support 施肥，并取消主循环 Tree 位施肥；request `657` 两轮 `7:08.233` / `7:08.713`，均值 `7:08.473`，慢于当前 `7:08.255`。统计为 `support_fertilizer=9/17`、`carrot_skip=98/85`、`reroll=549/553`。
  - 结论：support 施肥触发次数太少，且会引入 `Items.Fertilizer` 不足 warning；即便部分降低 `carrot_skip`，也吃不回额外动作和 Tree 位施肥机会成本。候选已从 `.py` 回退。
- 2026-06-08 未成熟 Bush 强制改 Carrot：
  - 前置探针 request `658` 显示 Carrot skip 的未成熟实体几乎全是 Grassland 上的 Bush：两轮分别为 `unready_bush=95/93`、`unready_grass=5/3`、`unready_soil=0`、`unready_grassland=100/96`。
  - 改法：只在 `rewrite_carrot_support()` 遇到 `entity == Entities.Bush` 且 `not can_harvest()` 时，摧毁未成熟 Bush，随后按原路径 `till()` 到 Soil 并 `plant(Entities.Carrot)`；未成熟 Grass / Tree 仍跳过，不新增补水、施肥或 support lock。
  - request `659` 两轮 `6:39.925` / `6:41.434`，稳定均值 `6:40.679`，刷新当前 `7:08.255`。统计为 `force_unready_bush=78/68`、`carrot_skip=7/6`、`reroll=404/417`。
  - 精简正式版移除探针用 unready 类型 / 地块统计，只保留 `force_unready_bush` 计数；request `660` 两轮 `6:40.746` / `6:40.073`，稳定均值 `6:40.410`。统计为 `force_unready_bush=60/91`、`carrot_skip=8/10`、`reroll=439/371`。
  - 结论：未成熟 Bush 是当前 Carrot support 兑现的主要低 churn 入口；强制改写的额外 `harvest + till + plant` 成本能被大幅降低的 `carrot_skip` / `reroll` 吃回，保留精简版为当前默认策略。
- 2026-06-08 Soil 上未成熟 Grass 强制改 Carrot：
  - 机制前提：`plant()` 不能覆盖已有实体；`harvest()` 会摧毁未成熟实体并在移除实体时消耗 `200t`。因此不能无差别强制覆盖未成熟 support。
  - 改法：只在 `rewrite_carrot_support()` 遇到 `entity == Entities.Grass`、`not can_harvest()` 且地块已经是 `Grounds.Soil` 时，摧毁 Grass 并种 Carrot；不覆盖未成熟 Bush，不新增补水，不处理 Grassland 上的未成熟 Grass。
  - 请求 `652` 两轮 `7:06.993` / `7:10.696`，均值 `7:08.845`，慢于当前 `7:08.255`。
  - 第一轮统计 `carrot_soil_grass_force=0`，说明这个窄分支在实际路径里没有覆盖到有效机会；候选已从 `.py` 回退并重新同步正式版到 `gamesave/`。
  - 结论：不继续做“摧毁未成熟 Grass 来换 Carrot support”的分支；它既没有覆盖面，也没有刷新成绩。
- 2026-06-08 剩余 reroll 来源探针：
  - 探针只统计 `handle_tree_slot()` 失败收割路径，不改变收割、动态 support、补水或施肥逻辑。
  - request `661` 两轮 `6:41.661` / `6:39.854`，均值 `6:40.758`；探针不作为成绩刷新。
  - request `661` 统计显示剩余 `reroll` 几乎全来自 companion 坐标落在 Tree 奇偶位：第一轮 `reroll=382` 中 `reroll_bad_slot=369`，第二轮 `reroll=419` 中 `reroll_bad_slot=406`；`reroll_none=0`，`reroll_carrot_skip=8/8`。
  - request `662` 加入轻量目标实体取样，两轮 `6:40.579` / `6:42.269`，均值 `6:41.424`；bad slot 请求类型近似三等分，第一轮 `bad_slot_bush=128`、`bad_slot_grass=127`、`bad_slot_carrot=112`，第二轮 `118/139/149`。
  - 取样显示 bad slot 上通常是未成熟 Tree，且几乎没有现成匹配 support：第一轮 `bad_slot_target_tree_unready=1`、`bad_slot_target_match=0`，第二轮 `bad_slot_target_tree_unready=2`、`bad_slot_target_match=1`。
  - 结论：当前剩余 companion 利用率瓶颈主要是棋盘几何导致的 Tree-slot companion，不是缺少 Carrot/Grass 写入分支。后续若继续 `lb_wood`，应先离线评估“牺牲 / 暂借 Tree 位做 support”的净收益；不能直接实机做 Tree 位改写，因为它会破坏 Tree/Bush 主循环和 Bush 产木节奏。
- 2026-06-08 Tree-slot 改写离线预算：
  - 临时脚本 `.codex/tests/wood_tree_slot_budget.py` 用 request `660/661/662` 统计估算，当前有效 companion 成功率约 `65.7%`，平均 bad slot 约 `387.8`。
  - 如果把目标 Tree 位长期留作 support，纸面估算约 `6:32~6:35`，但结构上不安全：目标 worker 后续会在非 Tree 实体上运行 `handle_tree_slot()`，可能卡在未成熟 support、错误 companion 或延迟恢复 Tree。
  - 如果每次都恢复目标 Tree 位，估算慢于当前：转换 `25%` bad slot 约 `6:54.137`，`50%` 约 `7:10.705`，`100%` 约 `7:50.596`；Carrot 还需要额外 `till()`，更慢。
  - 结论：不实机实现 Tree-slot 即时改写。后续只有能不破坏目标 worker 主循环、或几乎零移动地由目标 worker 自己承接的结构，才重新评估 Tree-slot companion。
- 2026-06-08 Tree-slot 临时 Bush swap：
  - 离线预算 `.codex/tests/wood_tree_slot_swap_budget.py` 显示：跳过同 row 冲突、只处理 Bush 类型 Tree-slot 请求时，理想估算约 `6:34.989`；这是一个不依赖通信、理论上低破坏的候选。
  - 临时实现：当 Tree companion 为 `Bush` 且目标落在 Tree 奇偶位时，当前 worker 移到目标旁边 Bush 位，尝试 `swap()` 把 Bush 临时换到目标 Tree 位，收割当前 Tree 后再换回。
  - request `663` 两轮 `6:46.913` / `6:48.217`，稳定均值 `6:47.565`，慢于当前 `6:40.410`。
  - 关键统计：第一轮 `tree_slot_bush_request=126`、`tree_slot_bush_swap=0`、`tree_slot_same_row_skip=31`、`tree_slot_no_bush_skip=16`、`tree_slot_swap_fail=79`；`output.txt` 明确报 `Warning: 尝试交换 Entities.Bush，但这是不可交换的。`
  - 结论：Bush 不能通过 `swap()` 临时塞进 Tree-slot support；该路线不成立，候选已从 `.py` 回退并重新同步正式版到 `gamesave/`。
- 2026-06-08 Tree-slot 同列延迟承接筛选：
  - 离线预算 `.codex/tests/wood_tree_slot_same_column_budget.py` 只看 Tree-slot 请求中目标仍在同一列、由同一 worker 拥有的窄窗口，避免跨 worker 通信和 swap。
  - 同列目标只占 Tree-slot offsets 的 `25%`，朝前同列只占 `12.5%`；覆盖面本身偏小。
  - 乐观 immediate 同 worker 转换估算：Grass/Carrot 为 `6:41.773`，Bush-only 为 `6:40.381`；前者慢于当前 `6:40.410`，后者只快约 `0.029s`，低于两轮波动且未计入 phase 扰动。
  - 乐观 delayed forward 转换估算：all types 为 `7:18.798`，Bush-only 为 `6:53.115`，因为需要把成熟 Tree 延迟约一个 column cycle。
  - 结论：同列 ownership 不能提供足够大、足够稳的低破坏窗口；不进入实机。后续 Tree-slot 方向必须同时避免回程、避免 phase 扰动，并覆盖更多 bad-slot 请求。
- 2026-06-08 周期 Tree 掩码强破坏对照：
  - `.codex/tests/wood_periodic_tree_mask_screen.py` 枚举小周期非相邻 Tree/Bush 掩码；首次包含 `8x8` 的全枚举触发 `60s` timeout 且无有效输出，随后收窄到 `2x2..8x4`。
  - 乐观上界最佳为 `4x4` 对角掩码 `T.../.T../..T./...T`：Tree 密度从 `50%` 降到 `25%`，Tree companion support success 从当前 `66.7%` 提到 `91.7%`，估算 `6:14.474`。
  - 临时实机只把 Tree 判定改成 `x % 4 == y % 4`，保留动态 support、补水、施肥、统计和入口不变。
  - request `673` 两条有效 run 均为 `8:10.429`，明显慢于当前 `6:40.410`；取消摘要 `finished=false runs=3 average=5:33.212` 不作为成绩。
  - 结论：大幅降低 Tree 密度虽然能减少 Tree-slot reroll，但 Tree 产量损失、Bush/support 扫描节奏和额外 churn 远超纸面收益；不继续做周期掩码 / 低 Tree 密度布局实机微调。
- 当前仓库没有更多 multi wood 的成体系失败路线
- 但从 `wood_single` 可以推断：如果动态 support 改写过重，冲突很容易吞掉收益
- “只把灌木当陪衬、不把它当木头来源”的理解
  - 这条线也应视为偏弱口径
  - 因为灌木本身就能继续产木头，是木头榜里最理想的伴生

## 下一步优化方向

- 当前 Grass+Carrot 动态 support 已有真实成绩；下一步重点确认：
  - 如何减少 `carrot_skip` / `reroll`，而不是单纯消除 Carrot 地块 warning
  - support 位未成熟是 `carrot_skip` 主因；当前无人机一次补水救援已失败，后续要改 support 更新节奏或结构
  - Soil 上未成熟 Grass 强制改 Carrot 没有覆盖到实际机会，不再作为下一轮分支
  - 剩余 reroll 主要来自 companion 坐标落在 Tree 位；已用离线预算判定“当前无人机改写并恢复 Tree 位”慢于当前，不直接实机
  - Tree-slot 临时 Bush swap 已被 request `663` 证伪；`Entities.Bush` 不可交换，不能再按 swap 方向设计 Tree-slot 接力
  - Tree-slot 同列同 worker 延迟承接覆盖面太窄且 phase 成本过高，不进入实机
  - 周期 Tree 掩码 / 低 Tree 密度布局 request `673` 已证伪；不能靠牺牲大量 Tree 位换 support 命中率
  - 当前 Grass rewrite 对 Bush 产木的真实净损耗
  - 是否存在比同无人机往返更低成本的动态接力结构
- 已验证“在 `main3` 低移动框架里只加 `get_companion()` + Bush 奇偶格筛选”没有刷新；Grass-only 动态 support 说明同框架内只有在能实际改写并兑现非 Bush support 时才有足够收益。
- 已验证“冻结 Bush 当纯 support”的方向风险很高：Bush 本身贡献大量 Wood，必须先设计能保住 Bush 产木、同时提高 Tree companion 命中率的结构。
- 下一步不应直接实机大改；先离线计算 Tree/Bush 产量损失与 Tree companion 增益的平衡，再决定是否做小规模布局对照。
- 离线平衡已经排除静态混合 support、粗粒度 Bush freeze 和简单 support worker 分流；当前 Grass-only 动态接力已验证成立，下一步只考虑低 churn Grass+Carrot 或能进一步降低 reroll 的动态结构。

## 候选策略方向（猜测 / 待验证）

### 方向 1：继续保留 Tree/Bush 棋盘，但尽量把 support 固化成灌木

- 核心思路：不先发散到别的伴生，把当前 support 尽量稳定固化为灌木
- 主瓶颈：support 如果频繁改写，会同时损失树的稳定性和灌木的木头收益
- 可能更强的原因：灌木是这榜最自然的双收益 companion，先把这条线吃满才合理
- 优先探针：
  - support 位最终稳定成灌木的比例
  - 灌木木头贡献占总木头的比例

### 方向 2：树位排布继续围绕“树不相邻”做低冲突优化

- 核心思路：试 24x24 或 16x32，而不是默认 32x32 满铺
- 主瓶颈：真正拖后腿的可能不是树太少，而是树位与 support 位冲突太多
- 可能更强的原因：只要树位更干净、support 更稳定，收益往往比简单缩图更直接
- 优先探针：
  - 不同树位排布下的冲突频率
  - 树不相邻约束下，哪些几何布局最容易把 support 留给灌木

### 方向 3：只有在不破坏 Tree/Bush 主结构时，才评估其他伴生

- 核心思路：把“灌木最理想”当主判断，只有在不破坏树 / 灌木主结构时，才去试别的伴生
- 主瓶颈：过早追其他伴生，很容易把主结构搞乱
- 可能更强的原因：这能避免把木头榜做成另一个高冲突 companion 实验场
- 优先探针：
  - 非灌木伴生的净收益是否真的超过它带来的结构破坏
  - 试点位是否会引入跨线程冲突
