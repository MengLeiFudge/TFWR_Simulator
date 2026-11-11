# 成就脚本

本目录保存需要专门制造状态、常规生产或打榜流程不能稳定完成的成就入口。每个入口最多运行 **300游戏秒（5分钟）**，完成后立即返回；时间不足会停止并说明原因。这里的时间是游戏内时间，不是电脑墙钟时间。

## 成就与运行时间

名称来自 [Steam 简体中文成就页](https://steamcommunity.com/achievements/2060160?l=schinese)，[111项原始名称和说明](../../references/achievements/steam-schinese.json)保留抓取时间与来源哈希。下表使用2026-11-11当前 C# 模拟器、全科技、物料充足、seed=0/1/2的实际完成时间范围。随机盘面不保证每次都能完成，300秒是停止上限，不是预计时长。本地核对原版触发条件和实际动作，不代替 Steam 账号解锁记录。

| Steam 成就中文名 | 脚本 | 预计游戏时间 | 完成条件 / 注意事项 |
| --- | --- | ---: | --- |
| 杂技高手、杂技大师 | [acrobatics.py](acrobatics.py) | 约32.3秒 | 32机完成1000次翻转，兼得首次翻转。 |
| 手感不错 | [pet_piggy.py](pet_piggy.py) | 约1.0秒 | 执行抚摸小猪。 |
| 错误 | [cause_runtime_error.py](cause_runtime_error.py) | <1秒 | 预期除零错误。 |
| 无限循环 | [infinite_loop.py](infinite_loop.py) | 约1.0秒 | 进入字面量while True后主动退出，无需手动停机。 |
| 时装秀 | [fashion_show.py](fashion_show.py) | 约2.2秒 | 5台无人机同时戴不同普通帽子。 |
| 巨型南瓜 | [giant_pumpkin.py](giant_pumpkin.py) | 13.0–14.5秒 | 整田32×32合并后只收获一次。 |
| 你搞错了 | [wrong_order.py](wrong_order.py) | 4.8–5.7秒 | 成熟3×3仙人掌按行列降序。 |
| 泥泞农场 | [mud_farm.py](mud_farm.py) | 约4.3秒 | 32机同时补水；需要4096份水。 |
| 妙手回春 | [healer.py](healer.py) | <1秒 | 肥料感染胡萝卜，再用怪异物质治愈。 |
| 循环导入 | [circular_import.py](circular_import.py) | <1秒 | 依赖同目录 circular_import_a.py、circular_import_b.py。 |
| 高阶编程 | [higher_order_programming.py](higher_order_programming.py) | <1秒 | 把函数作为参数传递。 |
| 栈溢出 | [stack_overflow.py](stack_overflow.py) | <1秒 | 预期递归溢出。 |
| 梯田 | [rice_terrace.py](rice_terrace.py) | 约2.1秒 | 3×3田只种不收，整田同时覆盖水稻。 |
| 放置、建造者、大建造者、毕加索 | [block_builder.py](block_builder.py) | 约47.0秒 | 16机累计放置10000块彩色块，逐块挖回。 |
| 摩天大楼 | [reach_height.py](reach_height.py) | 约5.7秒 | 9机垫高3×3田到+150；需要1350份建材。 |
| 探矿者 | [prospector.py](prospector.py) | 约1.8秒 | 实际支付铁勘探1000次。 |
| 彩色金字塔 | [power_pyramids_color.py](power_pyramids_color.py) | 6.0–7.3秒 | 拆净最小原生5×5塔，再用35块彩色块重建。 |
| 蘑菇挤不下 | [push_mushroom_blocked.py](push_mushroom_blocked.py) | 6.0–13.3秒 | 刻意制造一次受阻推蘑菇。 |
| 牵线搭桥 | [mushroom_matchmaker.py](mushroom_matchmaker.py) | 150.5–236.9秒 | 实际配对比例严格超过95%，回收子机。 |
| 远距离友谊 | [mushroom_cross_stratum.py](mushroom_cross_stratum.py) | 22.5–228.9秒 | 原生不同地层的同色蘑菇相遇。 |
| 炸药排除、炸药排除专家 | [dynamite_expert.py](dynamite_expert.py) | 63.2–239.3秒 | 32×32、深度≤-600，完整解盘；无确定安全格则换田。 |
| 不安全的代码 | [mining_helmet_unsafe.py](mining_helmet_unsafe.py) | <1秒 | 戴非采矿帽挖掘。 |
| 坏掉的锄头 | [till_rock.py](till_rock.py) | 1.0–1.2秒 | 对岩石使用耕作。 |
| 宝藏猎人 | [treasure_hunter.py](treasure_hunter.py) | 20.9–70.2秒 | 覆盖32×32农场的迷宫，找到并收获宝藏。 |

原生金字塔的最小底边是5，不是3；5×5塔包含25+9+1=35块有效体积。该入口使用6×6田，因为原版在不大于5×5的田里不生成金字塔。

## 可以复用的成就

完整111项已逐项分类：29项由上面24个专用入口完成，76项复用常规流程，2项复用排行榜，4项通过界面或科技树完成。逐项中文名称、说明与对应入口见[完整筛选清单](../../docs/achievement-audit.json)。以下列出容易混淆的边界。

| 成就或类型 | 复用入口 | 时间与边界 |
| --- | --- | --- |
| 采矿大师 | [block.py](../functional/block.py) | 本轮seed=1约49.4秒窗口内实际净增104.46万建材，60秒共147.49万。继续作为常规生产入口。 |
| 各资源专业户、大亨、矿工、大矿工与大师 | [常规产出表](../functional/README.md#当前产出速率)中的对应资源入口 | 按实际收获累计；时间受已有进度、初始化和批量结算影响，不能一律标成5分钟。 |
| 恐龙、长龙、长度很重要、恐龙大师 | [bone_dinosaur.py](../functional/bone_dinosaur.py) | 本轮完整周期775.38游戏秒，结算3348.89万骨头；属于常规生产，不受专用入口的5分钟限制。 |
| 迷宫、循环利用 | [gold_maze.py](../functional/gold_maze.py) | 常规入口重用小迷宫；“宝藏猎人”的整田大迷宫使用上表专用入口。 |
| 金字塔、埃及学家、大金字塔 | [power_pyramids.py](../functional/power_pyramids.py) | 按实际塔边界修补；大金字塔需随机遇到29×29塔，不能承诺5分钟。彩色塔另用专用入口。 |
| 藏宝图、大宝藏、藏宝图大师 | [gold_treasure_map.py](../functional/gold_treasure_map.py) | 常规路线去环后挖掘，累计200张需持续生产。 |
| 深层采矿、坚持不懈的矿工、不知疲倦的矿工、爆破大师 | [block.py](../functional/block.py) | 连续深入地下；绝对深度与累计深度分别判定，不能用建材数量替代。 |
| 巨型农场、蜂群、各首次种植、时尚达人、Hello World | 对应多机、种植或换帽的常规入口 | 已包含正常触发动作，不另建重复入口。 |
| 农业竞争、全自动化 | [排行榜目录](../leaderboard/README.md) | 必须真实提交对应排行榜；本地模拟不触发公开排名。 |
| 蒸蒸日上、大型农场、然后呢？ | 科技树 | 分别对应扩张、最大农场和全部解锁。 |
| 混沌编程 | 游戏工作区 | 手动打开20个代码窗口。 |

## 运行与验证

- 全科技、完整DLC、足够库存，开始前只保留主机。大多数入口会清田或改变尺寸。`set_world_size`最小有效指定值是3；程序退出时游戏会恢复农场尺寸，结束快照不一定保留小田条件。
- `dynamite_expert.py`需要同目录的常规 [dynamite.py](../functional/dynamite.py) 和 [production.py](../functional/production.py)。本地验证把入口与依赖冻结到同一临时目录后执行；游戏也按同目录模块解析。不能只复制入口漏掉依赖。
- 截止时间贯穿派机、下挖和解盘；计时循环预留最后动作与回收时间。固定短序列和故意报错入口直接结束。所有专用入口均已在三个seed下于300游戏秒内完成本地条件或触发预期错误，结束时只剩主机。
- `cause_runtime_error.py`和`stack_overflow.py`的正确结果就是指定运行时错误；报告的`state_complete=false`不作为资源效率证据。`infinite_loop.py`按原版进入字面量循环的判定触发后主动退出。
- 本轮证据见[验证说明](../../docs/script-rate-validation.md)和[完整数据](../../docs/script-rate-validation.json)。既有三项实机成就记录继续归[历史验证](../../docs/achievement-validation.json)。本轮没有运行真实游戏，也没有修改Save0。
- 表格更新时间、脚本及依赖哈希、seed、实际游戏时长与停止原因一起保存。脚本改变后重新做有界模拟；先短墙钟预算，不能用未兑现的批量产量或“预计会完成”填成功时间。
