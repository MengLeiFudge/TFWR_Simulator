# tfwr_orchestrator

`tfwr_orchestrator` 是本仓库里负责真实游戏 oracle 工作流的 Python 子项目。

如果你只想知道“第一次怎么把整个仓库跑起来”，先看仓库根目录 `README.md`。  
如果你要继续看 Python 协调器到底负责什么、CLI 怎么分工、路径怎么推导，看这里。

## 子项目职责

它负责以下工作：

1. 解析 `.env` / `TFWR_SAVE_ROOT` / `TFWR_GAME_ROOT` / `TFWR_BEPINEX_ROOT`
2. 部署 leaderboard 脚本，并在部署到真实存档时生成派生入口 `lb_start.py`
3. 通过 `state.json` 请求 Unity 模组执行脚本，并读取：
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`
   - Unity `Player.log`

## 目录约定

- `src/tfwr_orchestrator/`
  - 真实业务逻辑
- `tools/*.py`
  - CLI 入口
  - 只负责参数接线，不重复实现业务逻辑
- `tests/`
  - Python 测试

当前核心实现文件：

- `src/tfwr_orchestrator/config.py`
- `src/tfwr_orchestrator/leaderboard_sync.py`
- `src/tfwr_orchestrator/real_game_runner.py`
- `src/tfwr_orchestrator/output_capture.py`

## 配置输入与路径推导

配置默认来自仓库根目录 `.env`：

- `TFWR_SAVE_ROOT`
  - 指向真实 `Save0`
  - 用于推导 `gamesave/`
  - 用于推导游戏 `output.txt` 和 Unity `Player.log`
- `TFWR_GAME_ROOT`
  - 指向游戏安装目录
  - 用于定位游戏 EXE 和游戏资源
- `TFWR_BEPINEX_ROOT`（可选）
  - 指向手动安装或 R2 profile 的 `BepInEx` 目录
  - 未设置时使用 `TFWR_GAME_ROOT/BepInEx`
  - 用于推导 `config/mlj.tfwr.oracle-runner.state.json` 和 `LogOutput.log`
  - 运行 CLI 时可用 `--bepinex-root` 显式覆盖

补充说明：

- 如果 shell 已设置同名环境变量，代码会优先使用环境变量
- 在 WSL 中运行时，可以直接保留 `C:\...` / `D:\...` 写法，`config.py` 会自动转换为 `/mnt/c/...` / `/mnt/d/...`
- 仓库根目录真实存档链接目录名固定为 `gamesave/`

## CLI 入口

### `refresh_gamesave_link.py`

重建仓库根目录 `gamesave/` 到真实 `Save0` 的链接：

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
```

### `sync_leaderboard_scripts.py`

同步榜单脚本。默认只同步单个目标脚本：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
```

当目标目录是 `gamesave/` 时，会额外生成：

- `lb_start.py`

只有显式传 `--all` 时，才全量同步全部 `lb_*.py`：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --all
```

### `run_real_game_script.py`

启动或复用真实游戏，通过状态机请求模组执行目标脚本：

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

默认流程：

1. 手动安装模式启动或复用游戏进程；R2 profile 模式只连接已从 R2 启动的游戏
2. 等待模组状态机进入可请求状态
3. 写入 `requested`
4. 运行中轮询 `LogOutput.log` 与状态机，避免高频读取游戏 `output.txt`
5. 等待 `done / failed / superseded`；运行中通过游标读取新增日志行
6. `done / failed` 后在文件事务中回读本次输出并确认终态；被新请求覆盖时退出，保留新请求状态

模组与客户端通过独占创建的 `.lock` 文件协调请求 ID 分配、停止和终态确认。锁异常残留时先停止游戏和全部客户端，再移除残留锁。具体字段和自写客户端要求见 [文件协议](../oracle_runner_mod/README.md#文件协议)。

普通脚本可直接指定 `--target-script`，无需生成 `lb_start`。`lb_start` 会要求 leaderboard 结算证据；普通 simulate 探针应使用已有测试入口。`--request-only` 只提交请求，默认拒绝覆盖活动请求；明确替换须加 `--replace`。终态须先取结果回收，不能直接覆盖。默认文本等待模式先等待 idle，超时或 Ctrl+C 会请求停止自己的任务并有限等待清理。

AI调用推荐下述JSON接口。旧版文本提交及 Python `request_script_run()` 不建立完整请求回执；它们可用 `request_script_stop(state_path, request_id, reason)` 取消，再等待 `done/failed` 并调用 `acknowledge_terminal_state(state_path, request_id)`。不要直接写 JSON；旧 ID 无权停止或清除新请求。

`--status-only` 在 requested/running/stop_requested 时默认跳过 `output.txt`；确认游戏不再写入才显式加 `--include-game-output`。有回执时按本次请求日志统计；缺少回执时只显示有限日志尾部，并标记无法提供完整统计。

#### AI任务接口

指定 `--action` 后，stdout只返回一个JSON对象，过程日志写入stderr。沿用现有模组文件协议，无需更换DLL。R2模式仍连接用户已启动的profile。

```bash
python3 tfwr_orchestrator/tools/run_real_game_script.py --action health
python3 tfwr_orchestrator/tools/run_real_game_script.py --action submit --target-script lb_start --request-timeout 60 --idempotency-key cactus-candidate-01
python3 tfwr_orchestrator/tools/run_real_game_script.py --action status --request-id 123
python3 tfwr_orchestrator/tools/run_real_game_script.py --action wait --request-id 123 --total-timeout 90
python3 tfwr_orchestrator/tools/run_real_game_script.py --action cancel --request-id 123
python3 tfwr_orchestrator/tools/run_real_game_script.py --action result --request-id 123
```

`123`替换为提交返回的 `request_id`；各操作按需调用。`--json` 等价于默认 `--action run`，提交后持续监控并收取结果；`--request-only --json` 等价于submit。

| 操作 | 行为 |
| --- | --- |
| `submit` | 立即返回ID，不持续监控。遇忙返回 `busy`；只有显式 `--replace` 才能替换活动请求，终态仍须先回收 |
| `status` | 查看指定ID或当前请求，不确认终态；活动期间不读 `output.txt` |
| `wait` | 按ID监控、收取终态并回到idle；等待超时或中断只结束等待，可用相同ID继续 |
| `cancel` | 仅停止匹配ID；随后用wait/result收取终态 |
| `result` | 终态时读取三份输出，先留存结果再回到idle；已留存结果可重复读取 |
| `run` | 提交并等待；客户端等待超时或中断会停止自己的请求并有限等待回收 |
| `health` | 查询进程、状态、路径和有限日志中的模组版本；`workspace_ready=null`，不将文件存在当作工作区已就绪 |

幂等键在同一状态目录内持久有效。相同键、脚本名、请求超时与输出路径复用原ID；参数不同返回 `idempotency_conflict`。更换脚本内容或发起新一轮应使用新键。中断发生在回执写入与状态投递之间时返回 `submission_unknown`，不会自动重复启动。未提供键时，每次提交都是新请求。

回执在状态文件旁的 `config/mlj.tfwr.oracle-runner.state.requests/`，不写Save0。`<id>.json`保存输出起点、增量查询游标及终态摘要，`<id>.result.json`保存含三份完整输出的终态报告，`key-<hash>.json`保存幂等索引，`0.json`预留递增ID。新版仍可读取旧版内嵌完整结果的回执。回执随请求累计，当前不自动清理。完整报告及摘要保存后才确认idle；确认失败可用同一ID重试result回收。旧客户端请求缺少起点，或监测到模组日志被替换/截断时，`output_complete=false`。被替换且尚未保存的请求标记 `superseded`，不读取新请求的输出。

回执分别提供 `outcome`、`reason_code`、`completed_runs`、`average_game_seconds` 与 `full_statistics`。只将真实 `run=` 日志计入完成轮；`progress.prediction=true` 表示轮内估算。默认达到至少两轮且最近两轮差异不超过10%时主动停止，`reason_code=sample_limit`，不等于官方完整统计。要等待完整统计，设 `--max-leaderboard-runs 0`，并给足请求和等待超时。

JSON任务接口的 `--status-lines` 默认每份输出显示最后80行。活动任务按保存的字节游标读取新增完整日志行，并保留未完成行、完成轮和首末库存样本；重复查询不从请求起点重读全部日志。持续等待与状态查询共用增量统计，等待期间不累积完整日志历史；进度展示使用首末库存样本，均值和稳定性使用真实完成轮，官方成功摘要单独保留。终态摘要保留80行尾部，常规JSON查询直接返回摘要；显式要求更多行且输出超过80行时才加载完整归档。旧版文本 `--status-only` 保留原来的日志统计方式。

`output_lines`、`outputs_truncated`标明展示截断，完整终态报告在 `result_path`；新版归档直接保存报告对象，旧版路径仍指向含 `result` 字段的回执。结果同时保留BepInEx与Unity日志。退出码0表示该操作正常结束，仍须检查 `outcome/full_statistics`；忙为3，执行或接口错误为5，参数解析错误为2。`submit`没有持续监控：调用者应及时wait，或自行有界监看并取消、回收。

### 资源快照与反编译工具

```bash
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
python3 tfwr_orchestrator/tools/extract_leaderboard_snapshot.py --help
```

科技事实表默认固化到 `references/unlocks/`：

```bash
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format json --output references/unlocks/unlock_snapshot.json
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --format markdown --output references/unlocks/unlock_snapshot.md
```

## 输出与轮内预测

- 游戏 `output.txt`：脚本打印和游戏原生文本，执行时清空重写，结束后回读。
- BepInEx `LogOutput.log`：模组生命周期、完成轮/汇总、每秒 `item_snapshot`、取消和超时原因。
- Unity `Player.log`：引擎异常和堆栈，与模组日志共同诊断。

等待模式每 5 秒输出进度；`--status-only` 也能查看。首轮的 `progress_percent` 是当前库存/目标量，`prediction=true basis=inventory_linear` 明确标识线性预测：

- `eta_game_seconds` / `eta_game_time`：预计剩余游戏时间。
- `estimated_total_game_seconds` / `estimated_total_game_time`：当前游戏时间加剩余预测；与整轮基线和 #10 参考时间比较用这一项。
- `eta_real_seconds`：按当前实际加速率估算电脑占用时间，不用来比较策略。

估算只使用同一请求、同一轮的快照；缺采样、无正增长或 Fastest Reset 解锁目标时说明不可估算。批量收获前库存为零不能说明卡住，须看阶段日志。首轮完成后切换完成轮均值；`finished=false` 的取消摘要不计入成绩，也不把总均值复制成单轮样本来判定稳定。

## 最小联调顺序

```bash
python3 tfwr_orchestrator/tools/refresh_gamesave_link.py
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py cur2save --script lb_hay_single
python3 tfwr_orchestrator/tools/run_real_game_script.py --target-script lb_start --request-timeout 20
```

## 验证

帮助命令：

```bash
python3 tfwr_orchestrator/tools/sync_leaderboard_scripts.py --help
python3 tfwr_orchestrator/tools/run_real_game_script.py --help
python3 tfwr_orchestrator/tools/refresh_decompiled_sources.py --help
python3 tfwr_orchestrator/tools/extract_unlock_snapshot.py --help
python3 tfwr_orchestrator/tools/extract_leaderboard_snapshot.py --help
```

开发期测试：

```bash
PYTHONPATH=tfwr_orchestrator/src python3 -m unittest discover -s tfwr_orchestrator/tests -p 'test_*.py' -v
```
