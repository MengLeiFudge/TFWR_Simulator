# 随机数对齐研究

核对日期：2026-10-22。结论是：**相同 seed 和相同调用轨迹下可以对齐随机序列；这不等于完整游戏模拟已经对齐。** 本地模型仍只提供策略预期，候选必须到真实游戏打榜验证。

## 当前本地流程

`mechanism_model/` 的 C# Dinosaur、Cactus、Companion 模型通过 CLI 手动估算动作数、完成率和命中率。另有 [Python 农场API模拟](local_simulator/README.md)，可运行受支持的游戏脚本，已覆盖主要作物、恐龙、迷宫和无人机机制；二者都没有自动串入 `run_real_game_script.py`。

新增的 `rng` 命令只用于对照流初始化和初始抽样，不改变现有动作模型的采样口径：

```bash
dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- rng --seed 123 --samples 16
```

输出八条子流 seed、首台无人机的 `floor(random()*1000000)` 和 Cactus 的 `0..9` 数值。seed 范围为 `0..2147483647`，样本数为 `1..10000`。WSL 使用 Windows `dotnet.exe`。

后续请求 35 已把相同 RNG 接入实际单无人机仙人掌脚本：六 seed 的 9473 个离散 API 返回值、54 条边界观测与真实游戏一致。无水仙人掌固定 1 秒成熟，当前场景不依赖通用流决定生长时间；这不代表其他 Growable、浇水、伴生或完整通用流状态也已对齐。预计 API 时间仍比这六个实机样本低约 2.84%～2.92%，详情见上述模拟器说明。

## 游戏的生成链

从当前安装的 `Core.dll` 中 `Simulation`、`Helper.JustSha256It`、`ProgramState`，以及游戏 Mono `mscorlib.dll` 的 `System.Random` 核对：

1. `Simulation(seed)` 创建主 `System.Random(seed)`。
2. 依次派生 `various → maze → snake → cactus → sunflower → pumpkin → poly → random` 八条流。每条消耗主流 `NextBytes(16)`，对这 16 字节做 SHA256，取摘要前四字节小端有符号整数，再与 `0x7fffffff`。
3. `ProgramState` 从 `random` 子流取一次 `Next()` 作为无人机脚本 RNG 的 seed；脚本 `random()` 使用该 RNG。直接使用主 seed 或 random 子流都会错一层。
4. Cactus 使用 `randomCactus.Next(10)`。Mono 的显式 seed 算法是旧版 55 槽减法生成器；`NextBytes`、整数取值和浮点缩放的消耗方式必须一起对齐。

本次 .NET 10 显式 `new Random(seed)` 与上述采样吻合。Python 标准库 `random.Random` 使用不同算法，不能直接替换；若用 Python 实现，还需保留 C# 的整数溢出、字节截断和各重载抽样规则。

## 新鲜实机证据

在游戏内用 `simulate("test", Unlocks, items, {}, seed, 10000)`，依次运行 seed `0 / 1 / 123 / 161803399 / 20261022 / 2147483647`。每个 seed 检查主无人机和两个子无人机，再在 8×8 图交错调用 Cactus、Sunflower 与脚本 random。本地使用独立 Python 减法 RNG 与相同流派生规则。

| 项目 | 对照结果 |
| --- | --- |
| 主无人机初始与交错种植后的 `floor(random()*1000000)` | 768/768 相同 |
| 两个子无人机各自的脚本 random | 768/768 相同 |
| Cactus 首种与未成熟铲除后复种的 `measure()` | 768/768 相同 |
| Sunflower 花瓣数 | 384/384 相同 |
| 真实游戏观测值合计 | 2,688/2,688 相同 |

游戏请求 `30` 正常 done，BepInEx 与 Unity 新增日志无异常。六次实验复种前的成熟计数均为 0：`cactusNumbers` 在未成熟铲除时不会清空，复种沿用数值，不再消耗随机数。Sunflower 则每次重启从专用流取 `Next(7,16)`。

另用 .NET 10 显式 seed 的兼容实现作独立本地对照：12 个 seed，覆盖负数、Int32 两端和 161803398 邻界；`Next()`、整数区间（含跨 Int32 范围）、`NextDouble()` 的 IEEE 位模式、`NextBytes()` 和零宽区间混合调用，共 73,728 个值及 96 个子流 seed 全部相同。该部分不是在游戏 Mono 中执行全部重载，不能扩大实机覆盖范围。

本地实验与原始证据保存在 `.codex/tests/rng-parity/`：`probe.py`、`reference/Program.cs`、`game-test.py`、`game-simulate.py`、`game-output.txt` 和 `comparison.json`。原始游戏输出 SHA256 为 `3310a9946e1a588cb16df76837ae1cb39128f5f3c40804aec4046ded15f02857`。较早请求 `20` 的四 seed、128 值对照保留在 `.codex/oracle-r2-fix/`。

程序集 SHA256：

- Core.dll：`b8ac8d22b614d9e48d3affa9a4de9c77e799b824ed8f50dc2e494cc2dd9f9082`
- mscorlib.dll：`0e948cbd3c4fd36c10ed5bbbcf5ecab43d1a757a3afda30a662534cce7c6ec0f`

实机对照验证了三台无人机各自的脚本流，以及固定单无人机种植轨迹下的 Cactus/Sunflower 流。尚未验证负 seed 的游戏入口行为、共享随机流的并发种植、生长/浇水/伴生事件、迷宫、苹果生成与多轮 leaderboard 的完整世界轨迹。

## 旧 Python 偏差来自哪里

历史记录 `.codex/drafts/2026-04-21-randompoly-initialization-parity.md` 曾在限定 companion 探针里逐行对齐；当时剩余偏差牵涉初始草、解锁顺序、计时器重排和解释器 tick。不能把历史情况概括成“游戏随机数无法复刻”。

需要分别处理以下层次：

| 层次 | 偏差来源 |
| --- | --- |
| 生成器 | Python 默认 RNG 与 Mono System.Random 不同 |
| 流派生 | SHA256 字节序、八流顺序、每台无人机二次派生 |
| 抽样轨迹 | 相同分布不保证消耗次数相同；游戏 Apple 先抽 x/y 再拒绝占用格，当前动作模型按空格索引抽样 |
| 初始化 | 解锁、初始实体、缩放地图等在脚本前已消费部分流 |
| 调度 | 成长、水分、实体重启、tick 和无人机执行顺序改变后续随机调用 |
| 多轮 | leaderboard 后续 seed 来自八流后续抽样的求和，上一轮调用轨迹改变会影响下一轮 seed |

历史独立 water/growth/companion 分流设想也不能直接视为游戏事实：游戏 `various` 流实际承载多个机制，任意拆流会失去逐次对齐。Growable 的 companion 是先抽位置再抽类型，拒绝重抽次数必须一致。

## 继续推进的范围

快速优化优先用现有动作模型做分布和预算筛选，成本低于重建完整解释器。若某条策略确实需要 seed 精确回放，应按“初始世界 → 单个 API → 重启/生长事件 → 单无人机 → 多无人机 → 多轮”逐层比较首次分歧，记录流名、调用序号、实体和 tick。

模型通过只表示预测口径成立；真实 leaderboard 完成轮、均值和波动才支持更新最快策略。2026-10-23的后续实现已覆盖全部公开作物的主要机制并通过662条方法/机制观测对照，见[当前验收](local_simulator/validation.md)。完整解释器耗时与共享随机事件仍有近似，本文初始随机序列对齐不能推导整轮时间精度。
