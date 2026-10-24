using System;
using System.Globalization;
using System.IO;
using System.Runtime.Serialization;
using System.Text;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using TMPro;
using UnityEngine;

namespace TFWROracleRunner;

[BepInPlugin(PluginGuid, PluginName, PluginVersion)]
public sealed class Plugin : BaseUnityPlugin
{
    internal const string PluginGuid = "mlj.tfwr.oracle-runner";
    internal const string PluginName = "TFWR Oracle Runner";
    internal const string PluginVersion = "0.2.1";

    private enum StopReason
    {
        None,
        Timeout,
        Superseded,
        StopRequested,
    }

    private static Plugin? instance;
    private static readonly AccessTools.FieldRef<MainSim, Simulation> SimRef =
        AccessTools.FieldRefAccess<MainSim, Simulation>("sim");
    private static readonly AccessTools.FieldRef<MainSim, object> SimulationLockRef =
        AccessTools.FieldRefAccess<MainSim, object>("lockSimulation");
    private static readonly AccessTools.FieldRef<MainSim, MainSim.LeaderboardStartArgs> PrevLeaderboardStartRef =
        AccessTools.FieldRefAccess<MainSim, MainSim.LeaderboardStartArgs>("prevLeaderboardStart");
    private static readonly AccessTools.FieldRef<LeaderboardManager, GameObject> RunCancelledRef =
        AccessTools.FieldRefAccess<LeaderboardManager, GameObject>("runCancelled");
    private static readonly AccessTools.FieldRef<LeaderboardManager, TextMeshProUGUI> FinishTimeTextRef =
        AccessTools.FieldRefAccess<LeaderboardManager, TextMeshProUGUI>("finishTimeText");
    private static readonly AccessTools.FieldRef<Simulation, bool> SimulationHasErrorRef =
        AccessTools.FieldRefAccess<Simulation, bool>("hasError");
    private static readonly AccessTools.FieldRef<CodeWindow, string> CodeWindowErrorStringRef =
        AccessTools.FieldRefAccess<CodeWindow, string>("errorString");
    private static readonly AccessTools.FieldRef<CodeWindow, int> CodeWindowErrorStartIndexRef =
        AccessTools.FieldRefAccess<CodeWindow, int>("errorStartIndex");
    private static readonly AccessTools.FieldRef<CodeWindow, int> CodeWindowErrorEndIndexRef =
        AccessTools.FieldRefAccess<CodeWindow, int>("errorEndIndex");

    private OracleRunnerConfig runnerConfig = null!;
    private RunnerStateStore stateStore = null!;
    private Harmony? harmony;
    private int startingRequestId = -1;
    private float startingRequestAt;
    private float stateFailureSince = -1f;
    private float nextStatePollAt;
    private float nextStateWarningAt;
    private float lastProgressLogAt;
    private float lastItemSnapshotLogAt;
    private float activeRequestStartedAt;
    private float stopRequestedAt;
    private readonly LeaderboardResultAutoCloseGate leaderboardResultAutoCloseGate = new LeaderboardResultAutoCloseGate();
    private bool playInvoked;
    private StopReason stopReason = StopReason.None;
    private OracleRunnerStateFile? activeRequest;
    private OracleRunnerStateFile? pendingRequest;
    private int lastHandledRequestId;
    private bool wasLeaderboardRunning;
    private int observedLeaderboardRuns;
    private TimeSpan observedLeaderboardTotalTime = TimeSpan.Zero;
    private string observedLeaderboardScriptName = string.Empty;

    private ManualLogSource Log => Logger;

    private static Plugin? Instance => instance;

    private void Awake()
    {
        instance = this;
        runnerConfig = new OracleRunnerConfig(Config);
        stateStore = new RunnerStateStore(Path.Combine(Paths.ConfigPath, RunnerStateProtocol.StateFileName));
        lastProgressLogAt = Time.realtimeSinceStartup;

        harmony = new Harmony(PluginGuid);
        harmony.PatchAll();

        Log.LogInfo(
            $"enabled={runnerConfig.Enabled.Value} state_file={stateStore.StateFilePath} " +
            $"poll_ms={runnerConfig.StartupPollIntervalMs.Value} default_timeout={runnerConfig.DefaultRequestTimeoutSeconds.Value}s");
    }

    private void OnDestroy()
    {
        harmony?.UnpatchSelf();
        if (instance == this)
        {
            instance = null;
        }
    }

    private void Update()
    {
        if (!runnerConfig.Enabled.Value)
        {
            return;
        }

        MainSim? mainSim = MainSim.Inst;
        if (mainSim == null)
        {
            MaybeLogProgress("等待 MainSim 初始化");
            return;
        }

        if (!playInvoked &&
            runnerConfig.AutoPlayMainMenu.Value &&
            mainSim.menu != null &&
            mainSim.menu.gameObject.activeInHierarchy)
        {
            // 核心要求之一：不做 UI 坐标点击，而是直接走真实 Menu.Play() 入口。
            mainSim.menu.Play();
            playInvoked = true;
            Log.LogInfo("已调用 Menu.Play() 进入游戏工作区");
        }

        ObserveLeaderboardTiming(mainSim);
        PollState(mainSim);

        MonitorExecution(mainSim);
    }

    /// <summary>按配置间隔同步控制文件；临时 I/O 失败留到下一轮，不执行阻塞重试。</summary>
    /// <param name="mainSim">当前真实游戏模拟器。</param>
    private void PollState(MainSim mainSim)
    {
        float now = Time.realtimeSinceStartup;
        if (now < nextStatePollAt)
        {
            return;
        }
        nextStatePollAt = now + Mathf.Max(0.05f, runnerConfig.StartupPollIntervalMs.Value / 1000f);
        try
        {
            // BepInEx 默认每两秒刷盘；先刷新日志，再发布终态，避免短请求返回空日志。
            foreach (ILogListener listener in BepInEx.Logging.Logger.Listeners)
            {
                if (listener is DiskLogListener disk)
                {
                    disk.LogWriter?.Flush();
                }
            }
            OracleRunnerStateFile? current = stateStore.Read();
            stateFailureSince = -1f;
            EnsureStateFileReady(mainSim, current);
            if (current != null)
            {
                ObserveStopRequestedState(mainSim, current);
                ObserveRequestedState(mainSim, current);
            }
        }
        catch (Exception ex) when (ex is IOException || ex is UnauthorizedAccessException || ex is SerializationException)
        {
            // 正常客户端事务会短暂持锁；连续失败五秒才提示，仍不抢锁或阻塞主线程。
            if (stateFailureSince < 0f)
            {
                stateFailureSince = now;
            }
            if (now - stateFailureSince >= 5f && now >= nextStateWarningAt)
            {
                nextStateWarningAt = now + 5f;
                Log.LogWarning($"状态文件同步失败，将在下次轮询重试：{stateStore.StateFilePath}；{ex.Message}");
            }
        }
    }

    /// <summary>只初始化缺失状态或恢复插件重载前遗留的 running 状态。</summary>
    /// <param name="mainSim">当前真实游戏模拟器。</param>
    /// <param name="current">本轮唯一一次文件读取的结果。</param>
    private void EnsureStateFileReady(MainSim mainSim, OracleRunnerStateFile? current)
    {
        if (current == null)
        {
            stateStore.Write(RunnerStateProtocol.CreateIdle(lastHandledRequestId));
            return;
        }

        if (activeRequest == null &&
            !mainSim.IsExecuting() &&
            current.Status == RunnerRequestStatus.Running)
        {
            stateStore.Write(RunnerStateProtocol.CreateIdle(current.RequestId));
        }
    }

    private void ObserveRequestedState(MainSim mainSim, OracleRunnerStateFile observedState)
    {
        if (observedState.Status != RunnerRequestStatus.Requested)
        {
            return;
        }

        if (activeRequest == null)
        {
            if (observedState.RequestId <= lastHandledRequestId)
            {
                return;
            }

            TryStartRequest(mainSim, observedState);
            return;
        }

        if (observedState.RequestId <= activeRequest.RequestId)
        {
            return;
        }

        pendingRequest = observedState;
        if (stopReason == StopReason.None)
        {
            BeginStop(mainSim, StopReason.Superseded);
        }
    }

    private void ObserveStopRequestedState(MainSim mainSim, OracleRunnerStateFile observedState)
    {
        if (observedState.Status != RunnerRequestStatus.StopRequested)
        {
            return;
        }

        if (activeRequest == null)
        {
            MarkFailedWithOutput(observedState, observedState.LastError ?? "stop requested before start", DateTimeOffset.UtcNow);
            stateStore.Write(observedState);
            lastHandledRequestId = Math.Max(lastHandledRequestId, observedState.RequestId);
            return;
        }
        if (observedState.RequestId != activeRequest.RequestId)
        {
            return;
        }

        activeRequest.LastError = string.IsNullOrWhiteSpace(observedState.LastError)
            ? "stop requested"
            : observedState.LastError;
        if (stopReason == StopReason.None)
        {
            BeginStop(mainSim, StopReason.StopRequested);
        }
    }

    /// <summary>在单次请求期限内等待工作区、窗口及空闲执行器，再启动目标脚本。</summary>
    /// <param name="mainSim">真实游戏执行器。</param>
    /// <param name="requestedState">当前仍待启动的请求。</param>
    private void TryStartRequest(MainSim mainSim, OracleRunnerStateFile requestedState)
    {
        if (startingRequestId != requestedState.RequestId)
        {
            startingRequestId = requestedState.RequestId;
            startingRequestAt = Time.realtimeSinceStartup;
        }
        // 外部请求接管前确认已有结果页；手动游玩期间不主动确认。
        CloseLeaderboardResultScreen(mainSim, "request_start");
        leaderboardResultAutoCloseGate.Clear();
        string targetScriptName = RunnerStateProtocol.NormalizeTargetScriptName(
            requestedState.TargetScript ?? runnerConfig.TargetScriptName.Value
        );
        CodeWindow? targetWindow = mainSim.workspace == null ? null : FindTargetWindow(mainSim.workspace, targetScriptName);
        string? waiting = mainSim.workspace == null || !mainSim.workspace.gameObject.activeInHierarchy
            ? "workspace is not active"
            : targetWindow == null ? $"script window not found: {targetScriptName}"
            : mainSim.IsExecuting() ? "another script is still executing" : null;
        if (waiting != null)
        {
            if (Time.realtimeSinceStartup - startingRequestAt >= runnerConfig.ScriptReadyTimeoutSeconds.Value)
            {
                MarkFailedWithOutput(requestedState, waiting, DateTimeOffset.UtcNow);
                stateStore.Write(requestedState);
                lastHandledRequestId = Math.Max(lastHandledRequestId, requestedState.RequestId);
            }
            else
            {
                MaybeLogProgress($"等待请求启动 request_id={requestedState.RequestId}: {waiting}");
            }
            return;
        }

        Node? syntaxTree = targetWindow!.Parse();
        if (syntaxTree == null)
        {
            MarkFailedWithOutput(
                requestedState,
                BuildParseFailureMessage(targetWindow, targetScriptName),
                DateTimeOffset.UtcNow
            );
            stateStore.Write(requestedState);
            lastHandledRequestId = Math.Max(lastHandledRequestId, requestedState.RequestId);
            return;
        }

        RunnerStateProtocol.MarkRunning(requestedState, DateTimeOffset.UtcNow);
        stateStore.Write(requestedState);
        mainSim.StartMainExecution(targetWindow, syntaxTree);

        activeRequest = requestedState;
        pendingRequest = null;
        activeRequestStartedAt = Time.realtimeSinceStartup;
        lastHandledRequestId = Math.Max(lastHandledRequestId, requestedState.RequestId);
        stopReason = StopReason.None;
        Log.LogInfo($"已启动脚本 {targetWindow.fileName} request_id={requestedState.RequestId}");
    }

    private void MonitorExecution(MainSim mainSim)
    {
        if (activeRequest == null)
        {
            return;
        }

        if (stopReason != StopReason.None)
        {
            CloseLeaderboardResultScreen(mainSim, "request_stop");

            if (!mainSim.IsExecuting())
            {
                FinishStopping(mainSim);
                return;
            }

            float stopElapsed = Time.realtimeSinceStartup - stopRequestedAt;
            if (stopElapsed >= runnerConfig.RequestStopGracePeriodSeconds.Value)
            {
                MaybeLogItemSnapshot(
                    mainSim,
                    status: "stopping",
                    detail: $"stop_elapsed={stopElapsed.ToString("0.0", CultureInfo.InvariantCulture)}"
                );
            }
            return;
        }

        if (HasSimulationError(mainSim))
        {
            MarkFailedWithOutput(activeRequest, "script runtime error; see output.txt Error block", DateTimeOffset.UtcNow);
            stateStore.Write(activeRequest);
            mainSim.StopMainExecution();
            activeRequest = null;
            stopReason = StopReason.None;
            return;
        }

        if (!mainSim.IsExecuting())
        {
            FinishDone();
            return;
        }

        double timeoutSeconds = activeRequest.TimeoutSeconds ?? runnerConfig.DefaultRequestTimeoutSeconds.Value;
        if (timeoutSeconds > 0 &&
            Time.realtimeSinceStartup - activeRequestStartedAt >= timeoutSeconds)
        {
            BeginStop(mainSim, StopReason.Timeout);
            return;
        }

        MaybeLogItemSnapshot(
            mainSim,
            status: "running",
            detail: $"timeout={timeoutSeconds.ToString("0.0", CultureInfo.InvariantCulture)}"
        );
    }

    private void MaybeLogProgress(string message)
    {
        float now = Time.realtimeSinceStartup;
        const float minInterval = 5f;
        if (now - lastProgressLogAt < minInterval)
        {
            return;
        }

        lastProgressLogAt = now;
        Log.LogInfo(message);
    }

    private void MaybeLogItemSnapshot(MainSim mainSim, string status, string detail)
    {
        if (activeRequest == null)
        {
            return;
        }

        float now = Time.realtimeSinceStartup;
        if (now - lastItemSnapshotLogAt < 1.0f)
        {
            return;
        }

        lastItemSnapshotLogAt = now;
        Log.LogInfo(BuildItemSnapshotLine(mainSim, status, detail));
    }

    private string BuildItemSnapshotLine(MainSim mainSim, string status, string detail)
    {
        StringBuilder builder = new StringBuilder();
        builder.Append("item_snapshot request_id=");
        builder.Append(activeRequest?.RequestId ?? 0);
        builder.Append(" status=");
        builder.Append(status);
        if (!string.IsNullOrWhiteSpace(detail))
        {
            builder.Append(' ');
            builder.Append(detail);
        }
        builder.Append(" real_elapsed=");
        builder.Append((Time.realtimeSinceStartup - activeRequestStartedAt).ToString("0.0", CultureInfo.InvariantCulture));
        Simulation? sim = SimRef(mainSim);
        if (sim != null)
        {
            builder.Append(" game_time=");
            builder.Append(sim.CurrentTime.Seconds.ToString("0.###", CultureInfo.InvariantCulture));
            if (sim.Execution != null)
            {
                builder.Append(" game_tick=");
                builder.Append(sim.Execution.GlobalOpCount.ToString("0.###", CultureInfo.InvariantCulture));
            }
        }
        builder.Append(" leaderboard_runs=");
        builder.Append(mainSim.numLeaderboardRuns.ToString(CultureInfo.InvariantCulture));
        builder.Append(" leaderboard_total_time=");
        builder.Append(mainSim.totalLeaderboardTime.Seconds.ToString("0.###", CultureInfo.InvariantCulture));
        if (!string.IsNullOrWhiteSpace(observedLeaderboardScriptName))
        {
            builder.Append(" leaderboard_script=");
            builder.Append(observedLeaderboardScriptName);
        }

        ItemBlock inventory = mainSim.GetInventory();
        foreach (ItemSO item in ResourceManager.GetAllItems())
        {
            builder.Append(' ');
            builder.Append(item.itemName);
            builder.Append('=');
            builder.Append(inventory.GetNumber(item.itemId).ToString("0.###", CultureInfo.InvariantCulture));
        }

        return builder.ToString();
    }

    private void ObserveLeaderboardTiming(MainSim mainSim)
    {
        if (mainSim.leaderboardManager == null)
        {
            return;
        }

        bool isRunning = mainSim.leaderboardManager.IsRunning;
        Simulation sim = SimRef(mainSim);

        if (isRunning)
        {
            // simulate() 也会打开运行浮层，但结束时没有结果页，不能在此授权自动关闭。
            if (!wasLeaderboardRunning)
            {
                wasLeaderboardRunning = true;
                observedLeaderboardRuns = 0;
                observedLeaderboardTotalTime = TimeSpan.Zero;
                observedLeaderboardScriptName = ResolveLeaderboardScriptName(mainSim, sim);
                LogLeaderboardLine(LeaderboardLogFormatter.FormatStartLine(observedLeaderboardScriptName));
            }

            if (mainSim.numLeaderboardRuns > observedLeaderboardRuns)
            {
                TimeSpan currentTotalTime = mainSim.totalLeaderboardTime.ToTimeSpan();
                TimeSpan runTime = currentTotalTime - observedLeaderboardTotalTime;
                string runLine = LeaderboardLogFormatter.FormatRunLine(
                    observedLeaderboardScriptName,
                    mainSim.numLeaderboardRuns,
                    runTime
                );
                LogLeaderboardLine(runLine);

                observedLeaderboardRuns = mainSim.numLeaderboardRuns;
                observedLeaderboardTotalTime = currentTotalTime;
            }

            return;
        }

        if (stopReason != StopReason.None)
        {
            TryCloseExternalLeaderboardResultScreen(mainSim, "request_stop");
            return;
        }
        if (!wasLeaderboardRunning)
        {
            TryCloseExternalLeaderboardResultScreen(mainSim, "external_result_idle");
            return;
        }

        if (observedLeaderboardRuns > 0)
        {
            bool finished = !RunCancelledRef(mainSim.leaderboardManager).activeSelf;
            TimeSpan averageTime = TimeSpan.FromTicks(observedLeaderboardTotalTime.Ticks / observedLeaderboardRuns);
            string summaryLine = LeaderboardLogFormatter.FormatSummaryLine(
                observedLeaderboardScriptName,
                finished,
                observedLeaderboardRuns,
                averageTime
            );
            LogLeaderboardLine(summaryLine);

            if (activeRequest != null)
            {
                leaderboardResultAutoCloseGate.MarkExternalLeaderboardObserved();
                if (finished)
                {
                    RunnerStateProtocol.MarkDone(activeRequest, DateTimeOffset.UtcNow);
                }
                else
                {
                    MarkFailedWithOutput(activeRequest, "leaderboard cancelled", DateTimeOffset.UtcNow);
                }
                stateStore.Write(activeRequest);
                activeRequest = null;
            }

            TryCloseExternalLeaderboardResultScreen(mainSim, "external_result_complete");
        }
        else if (mainSim.leaderboardManager.IsLeaderBoardScreenOpen)
        {
            bool finished = !RunCancelledRef(mainSim.leaderboardManager).activeSelf;
            if (finished)
            {
                string scriptName = string.IsNullOrWhiteSpace(observedLeaderboardScriptName)
                    ? ResolveLeaderboardScriptName(mainSim, sim)
                    : observedLeaderboardScriptName;
                TimeSpan averageTime = ParseLeaderboardFinishTime(mainSim.leaderboardManager);
                string summaryLine = LeaderboardLogFormatter.FormatSummaryLine(
                    scriptName,
                    finished: true,
                    runCount: 1,
                    averageTime
                );
                LogLeaderboardLine(summaryLine);

                if (activeRequest != null)
                {
                    leaderboardResultAutoCloseGate.MarkExternalLeaderboardObserved();
                    RunnerStateProtocol.MarkDone(activeRequest, DateTimeOffset.UtcNow);
                    stateStore.Write(activeRequest);
                    activeRequest = null;
                }

                TryCloseExternalLeaderboardResultScreen(mainSim, "external_result_complete");
            }
            else
            {
                if (activeRequest != null)
                {
                    leaderboardResultAutoCloseGate.MarkExternalLeaderboardObserved();
                    MarkFailedWithOutput(activeRequest, "leaderboard finished without completed runs", DateTimeOffset.UtcNow);
                    stateStore.Write(activeRequest);
                    activeRequest = null;
                }

                TryCloseExternalLeaderboardResultScreen(mainSim, "external_result_cancelled");
            }
        }

        wasLeaderboardRunning = false;
        observedLeaderboardRuns = 0;
        observedLeaderboardTotalTime = TimeSpan.Zero;
        observedLeaderboardScriptName = string.Empty;
    }

    private void TryCloseExternalLeaderboardResultScreen(MainSim mainSim, string reason)
    {
        if (!leaderboardResultAutoCloseGate.ExternalResultPendingClose)
        {
            return;
        }

        CloseLeaderboardResultScreen(mainSim, reason);
    }

    private bool CloseLeaderboardResultScreen(MainSim mainSim, string reason)
    {
        if (mainSim.leaderboardManager == null || !mainSim.leaderboardManager.IsLeaderBoardScreenOpen)
        {
            return false;
        }

        mainSim.leaderboardManager.OkPressed();
        leaderboardResultAutoCloseGate.Clear();
        Log.LogInfo($"已自动确认 leaderboard 结果页面 reason={reason}");
        return true;
    }

    private static TimeSpan ParseLeaderboardFinishTime(LeaderboardManager leaderboardManager)
    {
        string rawText = FinishTimeTextRef(leaderboardManager).text.Trim();
        string[] minuteAndRest = rawText.Split(':', 2);
        if (minuteAndRest.Length != 2 ||
            !int.TryParse(minuteAndRest[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int minutes) ||
            !double.TryParse(minuteAndRest[1], NumberStyles.Float, CultureInfo.InvariantCulture, out double seconds))
        {
            return TimeSpan.Zero;
        }

        return TimeSpan.FromMinutes(minutes) + TimeSpan.FromSeconds(seconds);
    }

    private void ObserveLeaderboardStopped(
        MainSim mainSim,
        bool finished,
        string leaderboardName,
        TimeSpan averageTime,
        int runCount
    )
    {
        if (activeRequest == null)
        {
            leaderboardResultAutoCloseGate.Clear();
            Log.LogInfo($"手动 leaderboard 结束，保留结果页面 leaderboard={leaderboardName}");
            return;
        }

        // 只有外部请求确实产生了结果页，才允许后续 Update 自动确认。
        leaderboardResultAutoCloseGate.MarkExternalLeaderboardObserved();
        string scriptName = string.IsNullOrWhiteSpace(observedLeaderboardScriptName)
            ? ResolveLeaderboardScriptName(mainSim, SimRef(mainSim))
            : observedLeaderboardScriptName;
        // 最后一轮会在原生方法内清零计数，Update 来不及观察；在清零前记录真实完成轮。
        if (finished && runCount > observedLeaderboardRuns)
        {
            TimeSpan finalRunTime = mainSim.totalLeaderboardTime.ToTimeSpan() - observedLeaderboardTotalTime;
            LogLeaderboardLine(LeaderboardLogFormatter.FormatRunLine(scriptName, runCount, finalRunTime));
        }
        int normalizedRunCount = Math.Max(1, runCount);
        string summaryLine = LeaderboardLogFormatter.FormatSummaryLine(
            scriptName,
            finished,
            normalizedRunCount,
            averageTime
        );
        LogLeaderboardLine(summaryLine);

        // 停止流程仍拥有请求，须等结果页关闭并恢复 workspace 后才能发布终态或启动替代请求。
        if (stopReason != StopReason.None)
        {
            return;
        }
        if (finished)
        {
            RunnerStateProtocol.MarkDone(activeRequest, DateTimeOffset.UtcNow);
        }
        else
        {
            MarkFailedWithOutput(
                activeRequest,
                $"leaderboard cancelled: {leaderboardName}",
                DateTimeOffset.UtcNow
            );
        }
        stateStore.Write(activeRequest);
        activeRequest = null;
        wasLeaderboardRunning = false;
        observedLeaderboardRuns = 0;
        observedLeaderboardTotalTime = TimeSpan.Zero;
        observedLeaderboardScriptName = string.Empty;
    }

    private void BeginStop(MainSim mainSim, StopReason reason)
    {
        if (activeRequest == null)
        {
            return;
        }

        stopReason = reason;
        stopRequestedAt = Time.realtimeSinceStartup;
        mainSim.StopMainExecution();
        Log.LogInfo(
            $"请求停止当前执行 request_id={activeRequest.RequestId} reason={reason} " +
            $"pending={(pendingRequest != null ? pendingRequest.RequestId : -1)}"
        );
    }

    private void FinishStopping(MainSim mainSim)
    {
        if (activeRequest == null)
        {
            stopReason = StopReason.None;
            return;
        }

        if (stopReason == StopReason.Timeout || stopReason == StopReason.StopRequested)
        {
            MarkFailedWithOutput(
                activeRequest,
                stopReason == StopReason.Timeout
                    ? $"request timed out after {(activeRequest.TimeoutSeconds ?? runnerConfig.DefaultRequestTimeoutSeconds.Value):0.###}s"
                    : activeRequest.LastError ?? "stop requested",
                DateTimeOffset.UtcNow
            );
            stateStore.Write(activeRequest);
        }

        activeRequest = null;
        pendingRequest = null;
        stopReason = StopReason.None;
        wasLeaderboardRunning = false;
        observedLeaderboardRuns = 0;
        observedLeaderboardTotalTime = TimeSpan.Zero;
        observedLeaderboardScriptName = string.Empty;
        // 替代请求必须由下一次 PollState 从文件重读，不能执行可能已经被取消的旧快照。
    }

    private void FinishDone()
    {
        if (activeRequest == null)
        {
            return;
        }

        RunnerStateProtocol.MarkDone(activeRequest, DateTimeOffset.UtcNow);
        stateStore.Write(activeRequest);
        Log.LogInfo($"脚本执行完成 request_id={activeRequest.RequestId}");
        activeRequest = null;
    }

    private static bool HasSimulationError(MainSim mainSim)
    {
        Simulation? sim = SimRef(mainSim);
        return sim != null && SimulationHasErrorRef(sim);
    }

    private static string BuildParseFailureMessage(CodeWindow targetWindow, string targetScriptName)
    {
        string error = CodeWindowErrorStringRef(targetWindow);
        int startIndex = CodeWindowErrorStartIndexRef(targetWindow);
        int endIndex = CodeWindowErrorEndIndexRef(targetWindow);
        if (string.IsNullOrWhiteSpace(error))
        {
            return $"parse failed: {targetScriptName}";
        }

        return $"parse failed: {targetScriptName} error={error} start={startIndex} end={endIndex}";
    }

    private static void MarkFailedWithOutput(
        OracleRunnerStateFile state,
        string message,
        DateTimeOffset finishedAt
    )
    {
        RunnerStateProtocol.MarkFailed(state, message, finishedAt);
        WriteOracleErrorToOutput(state.RequestId, message);
    }

    private static void WriteOracleErrorToOutput(int requestId, string message)
    {
        string normalizedMessage = message
            .Replace('\r', ' ')
            .Replace('\n', ' ');
        Instance?.Log.LogError($"oracle_error request_id={requestId} {normalizedMessage}");
        WriteGameLog($"oracle_error request_id={requestId} {normalizedMessage}");
    }

    private void LogLeaderboardLine(string line)
    {
        line += $" request_id={activeRequest?.RequestId ?? 0}";
        Log.LogInfo(line);
        WriteGameLog(line);
    }

    /// <summary>与游戏执行线程同步写入原生输出；执行外打开的写入器在本次写入后关闭。</summary>
    /// <param name="line">保留在游戏输出中的模组诊断或榜单记录。</param>
    private static void WriteGameLog(string line)
    {
        MainSim? mainSim = MainSim.Inst;
        if (mainSim == null)
        {
            return;
        }
        // Logger.Clear 不 Dispose 旧 writer。停止后追加错误必须关闭，否则下一次 Clear 会共享冲突。
        lock (SimulationLockRef(mainSim))
        {
            try
            {
                global::Logger.Log(line);
            }
            finally
            {
                if (!SimRef(mainSim).IsExecuting())
                {
                    global::Logger.Close();
                }
            }
        }
    }

    private CodeWindow? FindTargetWindow(Workspace workspace, string targetScriptName)
    {
        if (workspace.codeWindows.TryGetValue(targetScriptName, out CodeWindow? exact))
        {
            return exact;
        }

        foreach (var item in workspace.codeWindows)
        {
            if (string.Equals(item.Key, targetScriptName, StringComparison.OrdinalIgnoreCase))
            {
                return item.Value;
            }
        }

        return null;
    }

    private void MarkMenuPlayed()
    {
        playInvoked = true;
    }

    private static string ResolveLeaderboardScriptName(MainSim mainSim, Simulation? sim)
    {
        MainSim.LeaderboardStartArgs startArgs = PrevLeaderboardStartRef(mainSim);
        if (!string.IsNullOrWhiteSpace(startArgs?.fileName))
        {
            return startArgs.fileName;
        }

        if (!string.IsNullOrWhiteSpace(sim?.leaderboardName))
        {
            return sim.leaderboardName;
        }

        return "leaderboard";
    }

    [HarmonyPatch(typeof(Menu), nameof(Menu.Play))]
    private static class MenuPlayPatch
    {
        private static void Postfix()
        {
            Instance?.MarkMenuPlayed();
        }
    }

    [HarmonyPatch(typeof(SteamLeaderboard), nameof(SteamLeaderboard.Load))]
    private static class SteamLeaderboardLoadPatch
    {
        private static void Prefix(string ___leaderboardName)
        {
            if (!SteamManager.Initialized)
            {
                Instance?.Log.LogWarning($"steam_leaderboard load board={___leaderboardName} initialized=False；Steam 未初始化，游戏不会请求榜单，请检查 Steam 客户端及游戏启动方式。");
                return;
            }

            Instance?.Log.LogInfo($"steam_leaderboard load board={___leaderboardName} initialized=True");
        }
    }

    [HarmonyPatch(typeof(SteamLeaderboard), "OnLeaderboardFindResult")]
    private static class SteamLeaderboardFindPatch
    {
        private static void Prefix(Steamworks.LeaderboardFindResult_t callback, bool failure, string ___leaderboardName)
        {
            Instance?.Log.LogInfo($"steam_leaderboard find board={___leaderboardName} failure={failure} found={callback.m_bLeaderboardFound}");
        }
    }

    [HarmonyPatch(typeof(SteamLeaderboard), "OnTopEntriesLoaded")]
    private static class SteamLeaderboardEntriesPatch
    {
        private static void Prefix(Steamworks.LeaderboardScoresDownloaded_t callback, bool failure, string ___leaderboardName)
        {
            Instance?.Log.LogInfo($"steam_leaderboard entries board={___leaderboardName} failure={failure} count={callback.m_cEntryCount}");
        }
    }

    [HarmonyPatch(typeof(LeaderboardManager), nameof(LeaderboardManager.StartLeaderboardRun))]
    private static class LeaderboardStartPatch
    {
        private static void Postfix()
        {
            // 新一轮执行不得继承上一页的关闭权限，包括手动启动和 simulate()。
            Instance?.leaderboardResultAutoCloseGate.Clear();
        }
    }

    [HarmonyPatch(typeof(LeaderboardManager), nameof(LeaderboardManager.OkPressed))]
    private static class LeaderboardOkPatch
    {
        private static void Postfix()
        {
            Instance?.leaderboardResultAutoCloseGate.Clear();
        }
    }

    [HarmonyPatch(typeof(LeaderboardManager), nameof(LeaderboardManager.StopLeaderboardRun))]
    private static class LeaderboardStopPatch
    {
        private static void Prefix(
            LeaderboardManager __instance,
            bool finished,
            string leaderboardName,
            TimeSpan timeSpan
        )
        {
            MainSim? mainSim = MainSim.Inst;
            if (mainSim == null)
            {
                return;
            }

            Instance?.ObserveLeaderboardStopped(
                mainSim,
                finished,
                leaderboardName,
                timeSpan,
                mainSim.numLeaderboardRuns
            );
        }
    }
}
