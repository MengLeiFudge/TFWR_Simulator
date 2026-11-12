# 四榜同seed残差修复

2026-11-03，Steam build26385848。保持四份正式策略、初始科技/库存和seed 1不变，重新运行游戏simulate。修正本地模型后，四份完整策略的结束时间均与游戏返回值还原的整数纳秒相同。原有正式排行榜成绩继续保留，本次没有重新统计官方随机轮均值。

## 完整策略对照

误差为本地减原生simulate。修正前一列沿用上一批0.01秒显示值，因此不能与修正后整数纳秒直接混为同一种精度。

| 榜单 | 修正前误差/秒 | 修正后本地/秒 | 原生simulate/秒 | 修正后误差 | 原生请求 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fastest Reset | -0.281760249 | 3069.528578392 | 3069.528578392 | 0ns | 269 |
| Pumpkins | +0.221447400 | 373.169717730 | 373.169717730 | 0ns | 270 |
| Sunflowers | +0.657256217 | 204.120297707 | 204.120297707 | 0ns | 271 |
| Sunflowers Single | -0.653131745 | 294.007406975 | 294.007406975 | 0ns | 272 |

原生外层入口在simulate返回后输出`paired_time * 1000000000`，消除普通秒数打印到0.01秒的舍入；乘法发生在被测模拟之外。四份目标源码没有插桩，均在两端完整结束。最终16榜本地回归确认15个资源目标及Reset的Leaderboard解锁完成，库存非负。

最终模型完整复跑16份正式策略。其余12榜的本地结束时间与修正前逐项相同，和既有同源原生结果仍只差0.01秒显示的舍入量，最大0.003450860秒。这12榜未重新获取纳秒返回值，不能写成0ns误差。

## 根因与实现

1. **施肥的旧生长区间被少结算一次。** `Growable.Fertilize`在植株未成熟时先调用`StopGrowing`，随后`TryScheduleGrow`再次调用它；旧起点直到重排成熟事件时才更新。原模型在第一次结算时就更新起点，漏掉第二次旧区间结算。`FarmWorld.sync_growth/track_growth`现在保留这一顺序。向日葵单机据此完整对齐，施肥规则没有改变。
2. **批次内提前处理了新建事件。** 游戏`Execution.Execute`在一批解释器操作中只用`Simulation.AddOpsToCurrentTime`推进时钟，新timer由后续`RunNextStep`处理。原调度器每次内部推进都处理timer，施肥后的成熟可能被其他无人机提前看到。新增`FarmWorld.add_execution_ticks`，将批次内时钟推进与批次之间的事件处理分开。南瓜多机据此对齐。当前源码允许施肥产生负延迟，仍按原事件顺序排队，没有擅自钳制为立即成熟。
3. **枚举键被当成字符串收费。** 本地用`StrEnum`表示游戏常量，`Items.Weird_Substance`因此落入字符串长度计费，查表多收1t；原生`ItemSO`使用`IPyObject.Size()`的1t默认值。`timing.size`现在先判断枚举，再处理真正的字符串。Reset最早在首次Weird Substance供料入口发生的1t差异消失，后续154条已记录的阶段时间与资源观测一致到显示精度，完整时间也重新一致。
4. **子无人机提前一轮提交终态。** 原生`ProgramState.PerformExecutionStep`先耗尽执行栈，下一次调度才设置`Terminated`。原模型捕获`StopIteration`就直接结束，使向日葵一台子机提前被父机看成已完成，改变同刻`wait_for`进入立即返回还是阻塞唤醒分支。`Drone.exhausted`与`Scheduler.resume`现在保留这个中间阶段。正常已完成句柄的wait仍计1t，没有把全部wait改成免费。

四处修正都位于共用机制或解释器层，没有按榜单添加时间补偿、经验倍率或修改策略控制流。

## 检查点与边界

- Reset固定前缀的315条调用阶段tick观测与request279逐项相同，前缀结束时间同为1382.434027231秒。
- 向日葵两波固定前缀的9920条收割检查点tick与request277逐项相同，结束时间同为41.775989747秒。
- 三个生产Python文件LSP零诊断。只运行当前用户授权的有界模型及原生对照，没有运行测试套件。

这证明所列完整脚本、固定初始条件和seed的时间及已记录状态。没有重新验证全部API、非法参数、所有竞态或任意新策略；旧版662条方法记录仍属于其原始游戏指纹。正式资源榜和Reset使用加密随机源，固定seed对照不等于复现官方随机轮次。

## 证据

本机证据根目录为`.codex/leaderboard-sol/four-residual-alignment/`。`before-manifest.json`与`before-*.py`保留修正前来源；中间模型与原始结果分别归档；`final-model-manifest.json`固定最终模型，`regression/`及`selected-results.json`保存最终16榜完整结果。四个目标目录的`native-precision-v1/`保存原生269～272完整回执、双日志、入口、部署与恢复指纹；`checkpoint-replays/`及`checkpoint-replay-summary.json`保存最终检查点对照。

诊断中的`sun-merge-ticks`为定位wait竞态增加了每rank两次收费下标预览，两端都包含这些费用，仅作首差定位；没有把它的时间当成正式源的完整时间。私有插桩生成器的`elif`语法错误及汇总器误判JSON顶层结构均在实机投递前停止，失败源码和stderr保留，修正后才继续。

原生请求269～281全部正常结束并按同ID回到idle，BepInEx和Unity新增日志无Error/Exception；26次临时覆盖均已逐字节恢复，Save0中文API指纹保留。收口时为idle281、游戏PID70264，游戏保持开启。Implementation deviations：None。

关联：[新版16榜复验](validation.md)、[总验收记录](validation.md)、[解释器费用指南](../../docs/leaderboards/interpreter_cost_notes.md)。
