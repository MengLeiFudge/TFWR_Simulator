# 炸药单机（dynamite_single）

2026-11-06：新增可复核基线，目标为100000 Dynamite。当前实现已完成三seed原目标模拟；普通场景对照保留为首版历史证据；已取得构建26462009的正式完整统计，见末节。

## 当前实现

单机维护公开数字与SAFE/MINE事实，先做直接和子集推理，停滞后有限低风险猜测。同一物理棋盘在猜测前后复用状态；owned集合和几何探测顺序只初始化一次，新猜测后清除采样与局部检查记录，以便发现零扩展和新增数字。每次clear后重新建盘，绝不跨棋盘复用事实。仅当所有剩余格都已证明为雷时，才挖已揭开的Soot完成一次人工结算；踩雷后按真实盘面变化收口。

主要成员：`dynamite_solve`、`worker`、`dig_target`、`dynamite_guess`、`prepare_all`。最多512盘、14400游戏秒、每盘32次猜测。来源为本机既有Dynamite.py，必需逻辑已内联；不跳层、不新增存档依赖。

## 时间记录

| 时间类别 | 当前记录 | 证据口径 |
| --- | --- | --- |
| 本地模拟预估时间 | 三seed均值 1206.387787170 游戏秒 | 地下模型26410308；当前结构，原目标 |
| 短时打榜测试时间 | 未取得 | 普通simulate不计为短时打榜 |
| 游戏打榜时间 | 1266.656 游戏秒 | 构建26462009，请求381，6轮，正常完整结束 |

| seed | 本地完整目标游戏秒 | 结果 | 本机证据 |
| --- | ---: | --- | --- |
| 1 | 1069.131744180 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-model-seed1/report.json` |
| 2 | 1314.684267210 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-model-seed2/report.json` |
| 3 | 1235.347350120 | 已达到原目标 | `.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-model-seed3/report.json` |

首版部署源码 SHA256：`d4a9964459e78aa2471e31476f2723f0d897209e91689da117869126e38f3af3`。地下模型元数据构建为26410308，基础模型字段保留26385848；报告分别保留两组来源指纹。资源榜专用地形的验证级别为`asset_and_source_only`，固定seed预测不能重放正式榜的加密随机盘面。

## 首版普通场景实机对照（历史）

普通8×8地层，显式传入满级基础和地下科技。诊断调整为 `{"goal":2048,"find_stratum_limit":2048,"ordinary_world_size":8}`；正式榜原目标仍由上方三seed验证。

请求 `334` 正常结束。本地与原生simulate完整返回时间均为 **123.470998020 游戏秒**，差值 **0.000000000 秒**。逐行状态、整数及坐标一致；小数日志仅按quick_print的0.01显示精度比较，完整返回时间另以整数纳秒核对。双日志未发现新增Error/Exception。

本机证据：`.codex/leaderboard-sol/underground-strategies/dynamite_single/ordinary-pair-v4/game-seed1/comparison.json`。派生脚本 SHA256：`deae1518e4517868c88a5919ec12ac9b17d362436ff41541b1bf1589884ee8f1`。覆盖前备份已有`test.py`/`simulate.py`，同一请求回到idle后逐字节恢复；其余存档Python文件哈希未变。

本项实机只覆盖所列普通场景与诊断目标；正式排行榜专用地形、32×32并发组合及长程误差尚未由本项实机证明。

## 候选与已处理边界

批次候选约2692秒、并行规划候选约4133秒，均慢于本机既有约束求解结构，因此保留串行结构。移除了没有调用路径的区域派发包装。

当前缓存版三seed的API调用次数均与原版相同，原目标均完成。seed1解释器开销从3298474t降到3082779t，省215695t，即35.505553950游戏秒；三seed均值由1244.993221770降到1206.387787170。这个约3.1%的同seed模型收益来自减少重建与重复推理。正式统计受随机盘面影响，不能把当前实机相对基线的11.87%全部归因于缓存。
三次完整统计分别为1288.764秒/6轮、1230.204秒/6轮、1266.656秒/6轮。第二次最后两轮差26.7%，因此追加第三次，最后两轮差约7.3%；当前时间和索引采用第三次。全部轮次正常达到100000 Dynamite，未出现矛盾诊断。

## 静态检查与后续

AST解析、仓库游戏语法、入口结构及禁止jump检查通过。当前执行逻辑的字节副本已运行ty LSP：2项错误来自Soot数字measure的联合返回类型与整数比较，另有11条未使用变量或API返回类型提示。未修改游戏外部类型桩。三次正式完整统计另提供当前游戏的运行证据。

下一步按[共用研究流程](README.md)继续比较结构候选；新版本仍须正式完整统计，只有官方正常结束结果才进入游戏打榜时间和成绩索引。当前记录不声明已确认最快或取得公开排名。

## 构建26462009正式统计：baseline-26462009

<!-- official:baseline-26462009:351 -->

请求351完整正常结束，共6轮。官方最终日志均值为 **23:57.266（1437.266游戏秒）**；逐轮日志重算均值为1437.266000000秒，保留两者的显示舍入口径。

当前结构完成首次正式统计。

部署源码SHA256：`d4a9964459e78aa2471e31476f2723f0d897209e91689da117869126e38f3af3`。当前源码SHA256：`e6eb2af30509e510ed8b49a77bb7a365c9165f94b065551409352bce0da8f469`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/baseline-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-26462009

<!-- official:state-cache-26462009:379 -->

请求379完整正常结束，共6轮。官方最终日志均值为 **21:28.764（1288.764游戏秒）**；逐轮日志重算均值为1288.763833333秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1288.764秒/6轮，缩短约10.33%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`b0ba4e61ffb9d5bb7721c254ccd7005074fe4aaa8b45e0541cb246279e57002c`。当前源码SHA256：`a3fd18741b2cfdf5618044819c2b8c00406c0773f889fd9a4f9cac2c99d2c07b`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-current-26462009

<!-- official:state-cache-current-26462009:380 -->

请求380完整正常结束，共6轮。官方最终日志均值为 **20:30.204（1230.204游戏秒）**；逐轮日志重算均值为1230.204166667秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1230.204秒/6轮，缩短约14.41%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`a3fd18741b2cfdf5618044819c2b8c00406c0773f889fd9a4f9cac2c99d2c07b`。当前源码SHA256：`3b630b4ff7abd4da3e051dd276b9257d04e610711baf1f8436117dbc9b0afb49`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-current-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。

## 构建26462009正式统计：state-cache-current-confirm-26462009

<!-- official:state-cache-current-confirm-26462009:381 -->

请求381完整正常结束，共6轮。官方最终日志均值为 **21:06.656（1266.656游戏秒）**；逐轮日志重算均值为1266.656666667秒，保留两者的显示舍入口径。

同构建前版完整均值1437.266000000秒/6轮；当前正式均值1266.656秒/6轮，缩短约11.87%。同一物理棋盘在猜测前后复用公开数字、已证明标志和版本约束；新猜测清采样及局部检查，owned和几何列表仅初始化一次，每次clear后的新棋盘重新创建状态。

部署源码SHA256：`3b630b4ff7abd4da3e051dd276b9257d04e610711baf1f8436117dbc9b0afb49`。当前源码SHA256：`23301951a179d21923859b66cc69cf35646474faa029201dcd459cb82be91aa5`；最终仅更新时间注释，AST与实测部署版本相同。版本Core.dll为`f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25`。模型仍标地下构建26410308，以上正式成绩来自当前游戏，不能据此宣称新版本模型精度全面通过。

证据：`.codex/leaderboard-sol/underground-official/dynamite_single/state-cache-current-confirm-26462009/summary.json`及同目录完整请求、部署清单与restoration记录。双日志无新增Error/Exception，全部脚本正常达标返回；已有test.py/lb_start.py在同ID回idle后逐字节恢复，非目标存档Python文件未变。
