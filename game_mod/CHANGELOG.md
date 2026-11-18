# 更新记录

## 0.3.1 — 2026-11-18

- 新增实时字段 `saving`（取原版 `Saver.IsSaving`），与请求终态无关；保存超时或取消后仍反映后台写盘，客户端据此阻止覆盖存档脚本，避免旧快照把旧代码写回。
- 修复即时 `stop` 与旧请求收口相撞：活动请求已被更新请求接替时不再写旧终态，避免 `stop --replace` 的完成状态被覆盖成 `failed`。
- 运行不再有时间语义：`run` 不要求 `timeout_seconds`，模组启动后一直观察到脚本自然结束；新增 `Advanced.MaxRunSeconds`（默认0，范围0～86400），是每次 run 都生效的现实秒上限，不检测客户端是否存活，被它掐掉记 `failed`（`run exceeded MaxRunSeconds=<n>s`），不算完成。
- `Advanced.ScriptReadyTimeoutSeconds` 默认改为0并明确表示不限时（与 `SaveTimeoutSeconds` 一致），不再是"0即立即失败"；工作区已就绪但目标窗口不存在时立即判失败，不再等上限。
- 重复或落后的 `request_id` 不再静默丢弃：写 `failed` 并在 `last_error` 说明已处理到哪个编号。
- 取消请求字段 `timeout_seconds`；`protocol_version` 改为只由模组发布（升到4），客户端声明不再参与判定，已知命令按名字执行、未知命令写 `failed`。
- 终态 `done`/`failed`/`superseded` 不是活动请求，新请求可直接覆盖，客户端不必先写 `idle`。

## 0.3.0 — 2026-11-17

- 新增控制命令，外部工具不必再做坐标点击或手工建窗：`save`（异步保存并等确认）、`play`（主菜单进工作区）、`stop`、`ok`（关闭排行榜结果页）、`open`（按文件内容新建脚本窗口并停靠）、`close`、`minimize`、`unminimize`、`dock`、`arrange`、`list`（窗口清单写 `result_text`）。
- 请求字段新增 `second_script`（dock/open 的停靠窗口）、`code_file`（open 读取的源码，超过 1 MB 拒绝）、`result_text`（命令输出）。
- `ok`、`list`、`minimize`、`unminimize`、`play`、`stop` 为即时命令，不等待工作区空闲；其中 `stop` 主动停止当前程序。
- 协议版本升到 3；新增命令要求 `protocol_version >= 3`，旧客户端仍可只用 `run`/`prepare`/`quit`。
- 配置改为 `General`（`AutoPlayMainMenu`、`AutoOkLeaderboardResult`、`Enabled`）与 `Advanced`（缺省窗口、轮询间隔、各类超时）两段。
- 脚本运行由调用方显式提供正的有限 `timeout_seconds`，CLI运行提交必须传 `--request-timeout`；移除模组默认运行时限。控制和查询操作不使用运行时限。
- 保存统一走异步 `Saver.Save`：窗口变更、`save` 和 `quit` 仅使用 `Advanced.SaveTimeoutSeconds`（默认10秒，范围0～60秒，0表示不限时），与脚本运行时限独立。取消或替换撤销退出，保存失败保留现场；状态文件丢失或读取失败时记录请求上下文。
- 状态文件新增实时字段 `executing`、`leaderboard_running`、`leaderboard_screen`、`busy_windows`，每轮轮询刷新；外部队列据此判断运行何时结束、何时可以改脚本文件。
- 新增配置 `AutoOkLeaderboardResult`：结果页一出现就按 OK。结果页打开期间游戏仍报告 `IsExecuting=true`，等结束的外部脚本会被卡死。

## 0.2.4 — 2026-11-17

- 补上本文件：此前各版本把更新说明写在 README 里，Thunderstore 的 Changelog 页签一直是空的。
- 打包清单加入 `CHANGELOG.md`；README 的版本段改为指向本文件。
- 功能与 0.2.3 完全相同，插件 DLL 只差版本字符串。

## 0.2.3 — 2026-11-17

- 适配游戏更新后的保存签名：游戏把 `Saver.Save(MainSim)` 改成返回 `Task<bool>`，用旧签名编译的 DLL 会在 `quit` 抛 `MissingMethodException`，并连带阻断 `prepare` 等请求。本版按当前游戏程序集重新编译，`quit` 逐帧等待保存完成。
- `quit` 只在保存确认成功且没有警告弹窗时发布完成状态再退出；保存未确认时保留游戏并报告失败。
- 取消请求或投递新请求会撤销尚未执行的退出，不提前确认终态。
- 该修复此前只在本机替换的 DLL 上生效，0.2.3 是它第一次进入公开包。

## 0.2.2 — 2026-10-24

- 新增 `prepare` 后台准备工作区和 `quit` 保存退出接口，客户端确认游戏退出后返回结果。
- 脚本请求可从主菜单直接进入工作区；无需模拟鼠标点击。
- 控制命令沿用请求 ID、文件锁与终态确认，活动外部请求须显式替换。
- 协议版本升级为 2，原有脚本请求仍兼容；配套客户端从 GitHub 更新。

## 0.2.1 — 2026-10-24

- 修复停止后再次执行时的输出文件占用，以及短请求日志尚未落盘的问题。
- 启动等待期限按每个请求计时；替换和取消请求时重新核对状态，避免执行已过期请求。
- 手动运行保留排行榜结果页；外部请求开始前确认已有结果页，完成后只自动关闭所属结果页。
- 补记官方完整统计的最后完成轮，增加 Steam 初始化与榜单下载诊断。
- 配套客户端提供适合 AI 调用的 JSON 任务接口、幂等提交、增量监控和结果归档。

## 0.2.0 — 2026-10-22

- 首次公开发布（预览版）：让外部工具运行和停止真实游戏脚本，并把状态与排行榜日志落盘。
- 依赖 BepInEx 5 与 `BepInEx-BepInExPack-5.4.2305`；模组只执行存档中已有的脚本窗口，不提供外部 Python 解释器。
- 当时游戏内加载、脚本控制与结果回读尚待实机验证。
