# 游戏更新后的16榜配对复验

本批对应Steam构建26385848。用户要求每个榜单都运行本地模拟和真实排行榜，并比较误差；此前成绩保留为旧版本记录。本页中的本地数据不是排行榜成绩，也不能与旧游戏成绩相减后称为模拟误差。

## 当前证据

- 当前正式源码已逐榜归档，固定seed 1本地完整执行16/16，全部达到对应目标；Fastest Reset已解锁Leaderboard。
- 初始条件从本版LeaderboardSO重新提取。30个榜中16个属于基础游戏，这16个的目标和初始库存与旧版相同。单机使用Expand 5、Megafarm 0；向日葵初始Power为0；Reset使用榜单基础能力。
- 游戏固定seed模拟和本版完整官方统计尚未运行。当前进程中的旧Oracle DLL调用已移除的静态Logger.Log，每帧抛MissingMethodException，阻断请求处理。兼容代码已改用MainSim实例日志器，Windows Release编译0警告、0错误；尚未替换运行中的DLL。
- 用户此前要求游戏保持开启。加载修正DLL需要一次正常重启；不强杀进程、不选择云存档冲突，复验结束保持游戏运行。

## 当前正式源码的本地结果

时间单位为游戏秒。实机列留空表示尚无本版本配对证据。这里只列已执行的当前基线，尚未据此选择历史候选中的本版最快实现。

| 榜单 | 本地seed 1完整时间 | 游戏同seed模拟 | 同seed误差 | 本版完整排行榜均值 |
| --- | ---: | ---: | ---: | ---: |
| Cactus | 34.753451 | | | |
| Cactus Single | 19.804558 | | | |
| Carrots | 231.101740 | | | |
| Carrots Single | 251.839967 | | | |
| Dinosaur | 775.380425 | | | |
| Fastest Reset | 3044.450907 | | | |
| Hay | 112.696615 | | | |
| Hay Single | 178.349667 | | | |
| Maze | 85.639011 | | | |
| Maze Single | 128.237281 | | | |
| Pumpkins | 373.391447 | | | |
| Pumpkins Single | 440.872658 | | | |
| Sunflowers | 207.491675 | | | |
| Sunflowers Single | 293.356868 | | | |
| Wood | 276.645212 | | | |
| Wood Single | 313.237686 | | | |

本地源文件、场景、指纹、完整JSON和进度日志保存在本机`.codex/leaderboard-sol/game-update-revalidation/baseline/`；索引为同目录上级的`local-baseline-index.json`。每榜仅运行一次固定输入，未扫描seed或参数。

## 比较口径

同seed误差定义为“本地完整时间－游戏simulate返回时间”，百分比以游戏simulate时间为分母。两端必须使用相同源码、基础研究等级、初始库存和seed；不继承主农场当前研究。出现偏差时先定位首次分歧，不加经验倍率修整轮时间。约900游戏秒的绝对误差小于1秒仍是模型长程验收目标；本表尚不证明通过。

正式资源榜和Reset在本版使用系统加密随机源，不能用固定seed精确重放。正式轮均值与本地seed 1的差异另记为样本差异，保留实际完成轮数和范围，不冒充同seed模型误差。选定实现必须正常完成完整官方统计，才能更新脚本头时间及`lb_start.py`成绩列。

## API提示同步

Save1当前仅有0字节`save.json`，尚未生成`__builtins__.py`。游戏的`Saver.WriteCodeFiles`调用`Localizer.LoadBuiltins`，原样读取`StreamingAssets/Languages/builtins.py`作为新存档模板。本批采用该同源模板，而不是猜测Save1接口。

官方模板SHA256为`6e3f67b85e5c97ebac4eea4b9484425bf7fee9b81d6690c0ace661a8fdce8651`。中文候选已翻译259处说明字符串及自然语言注释；静态AST核对确认全部声明、注解、重载和常量不变。官方说明中向日葵“五倍”和宝藏“边长产量”与当前机制源码不符，中文按当前机制修正。旧Save0提示文件已经备份；中文候选尚未写入Save0。

## 新发现问题

本版UnityPy类型树生成器把LeaderboardSO新增的`whitelistedGroundFeatureUnlocks: List<string>`误标为string，原快照工具报`EOFError: read_i_array out of bounds`。本批只读提取时按源码还原为vector后成功，未修改公共提取工具；原始快照和处理方式保留在本机证据目录。该工具问题不改变已提取的16榜初始条件。
