using System;
using System.Globalization;
using System.IO;
using System.Text;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.Mono;
using HarmonyLib;
using UnityEngine;

namespace TFWROracleRunner;

[BepInPlugin(PluginGuid, PluginName, PluginVersion)]
public sealed class Plugin : BaseUnityPlugin
{
    internal const string PluginGuid = "mlj.tfwr.oracle-runner";
    internal const string PluginName = "TFWR Oracle Runner";
    internal const string PluginVersion = "0.1.0";

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
    private static readonly AccessTools.FieldRef<MainSim, MainSim.LeaderboardStartArgs> PrevLeaderboardStartRef =
        AccessTools.FieldRefAccess<MainSim, MainSim.LeaderboardStartArgs>("prevLeaderboardStart");
    private static readonly AccessTools.FieldRef<LeaderboardManager, GameObject> RunCancelledRef =
        AccessTools.FieldRefAccess<LeaderboardManager, GameObject>("runCancelled");

    private OracleRunnerConfig runnerConfig = null!;
    private RunnerStateStore stateStore = null!;
    private Harmony? harmony;
    private float pluginStartedAt;
    private float lastProgressLogAt;
    private float lastItemSnapshotLogAt;
    private float activeRequestStartedAt;
    private float stopRequestedAt;
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
        pluginStartedAt = Time.realtimeSinceStartup;
        lastProgressLogAt = pluginStartedAt;

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

        EnsureStateFileReady(mainSim);
        ObserveLeaderboardTiming(mainSim);

        OracleRunnerStateFile? observedState = stateStore.Read();
        if (observedState != null)
        {
            ObserveStopRequestedState(mainSim, observedState);
            ObserveRequestedState(mainSim, observedState);
        }

        MonitorExecution(mainSim);
    }

    private void EnsureStateFileReady(MainSim mainSim)
    {
        OracleRunnerStateFile? current = stateStore.Read();
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
        if (activeRequest == null || observedState.Status != RunnerRequestStatus.StopRequested)
        {
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

    private void TryStartRequest(MainSim mainSim, OracleRunnerStateFile requestedState)
    {
        CloseLeaderboardResultScreen(mainSim);
        if (mainSim.workspace == null || !mainSim.workspace.gameObject.activeInHierarchy)
        {
            MaybeLogProgress("等待工作区激活");
            return;
        }

        string targetScriptName = RunnerStateProtocol.NormalizeTargetScriptName(
            requestedState.TargetScript ?? runnerConfig.TargetScriptName.Value
        );
        CodeWindow? targetWindow = FindTargetWindow(mainSim.workspace, targetScriptName);
        if (targetWindow == null)
        {
            if (Time.realtimeSinceStartup - pluginStartedAt > runnerConfig.ScriptReadyTimeoutSeconds.Value)
            {
                RunnerStateProtocol.MarkFailed(
                    requestedState,
                    $"script window not found: {targetScriptName}",
                    DateTimeOffset.UtcNow
                );
                stateStore.Write(requestedState);
                lastHandledRequestId = Math.Max(lastHandledRequestId, requestedState.RequestId);
            }
            else
            {
                MaybeLogProgress($"等待脚本窗口 {targetScriptName}");
            }
            return;
        }

        if (mainSim.IsExecuting())
        {
            MaybeLogProgress("当前已有执行，等待停止后再启动新请求");
            return;
        }

        Node? syntaxTree = targetWindow.Parse();
        if (syntaxTree == null)
        {
            RunnerStateProtocol.MarkFailed(
                requestedState,
                $"parse failed: {targetScriptName}",
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
            CloseLeaderboardResultScreen(mainSim);

            if (!mainSim.IsExecuting())
            {
                FinishStopping(mainSim);
                return;
            }

            float stopElapsed = Time.realtimeSinceStartup - stopRequestedAt;
            if (stopElapsed >= runnerConfig.RequestStopGracePeriodSeconds.Value)
            {
                MaybeLogProgress(
                    $"等待 StopMainExecution 生效 request_id={activeRequest.RequestId} elapsed={stopElapsed:F1}s"
                );
            }
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

        MaybeLogProgress(
            $"脚本运行中 request_id={activeRequest.RequestId} timeout={timeoutSeconds:F1}s"
        );
        MaybeLogItemSnapshot(mainSim);
    }

    private void MaybeLogProgress(string message)
    {
        float now = Time.realtimeSinceStartup;
        float minInterval = Mathf.Max(0.05f, runnerConfig.StartupPollIntervalMs.Value / 1000f);
        if (now - lastProgressLogAt < minInterval)
        {
            return;
        }

        lastProgressLogAt = now;
        Log.LogInfo(message);
    }

    private void MaybeLogItemSnapshot(MainSim mainSim)
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
        Log.LogInfo(BuildItemSnapshotLine(mainSim));
    }

    private string BuildItemSnapshotLine(MainSim mainSim)
    {
        StringBuilder builder = new StringBuilder();
        builder.Append("item_snapshot request_id=");
        builder.Append(activeRequest?.RequestId ?? 0);
        builder.Append(" elapsed=");
        builder.Append((Time.realtimeSinceStartup - activeRequestStartedAt).ToString("0.0", CultureInfo.InvariantCulture));

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
            if (!wasLeaderboardRunning)
            {
                wasLeaderboardRunning = true;
                observedLeaderboardRuns = 0;
                observedLeaderboardTotalTime = TimeSpan.Zero;
                observedLeaderboardScriptName = ResolveLeaderboardScriptName(mainSim, sim);
                global::Logger.Log(LeaderboardLogFormatter.FormatStartLine(observedLeaderboardScriptName));
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
                global::Logger.Log(runLine);

                observedLeaderboardRuns = mainSim.numLeaderboardRuns;
                observedLeaderboardTotalTime = currentTotalTime;
            }

            return;
        }

        if (!wasLeaderboardRunning)
        {
            CloseLeaderboardResultScreen(mainSim);
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
            global::Logger.Log(summaryLine);

            if (activeRequest != null)
            {
                if (finished)
                {
                    RunnerStateProtocol.MarkDone(activeRequest, DateTimeOffset.UtcNow);
                }
                else
                {
                    RunnerStateProtocol.MarkFailed(activeRequest, "leaderboard cancelled", DateTimeOffset.UtcNow);
                }
                stateStore.Write(activeRequest);
                activeRequest = null;
            }

            CloseLeaderboardResultScreen(mainSim);
        }
        else if (mainSim.leaderboardManager.IsLeaderBoardScreenOpen)
        {
            if (activeRequest != null)
            {
                RunnerStateProtocol.MarkFailed(activeRequest, "leaderboard finished without completed runs", DateTimeOffset.UtcNow);
                stateStore.Write(activeRequest);
                activeRequest = null;
            }

            CloseLeaderboardResultScreen(mainSim);
        }

        wasLeaderboardRunning = false;
        observedLeaderboardRuns = 0;
        observedLeaderboardTotalTime = TimeSpan.Zero;
        observedLeaderboardScriptName = string.Empty;
    }

    private void CloseLeaderboardResultScreen(MainSim mainSim)
    {
        if (mainSim.leaderboardManager == null || !mainSim.leaderboardManager.IsLeaderBoardScreenOpen)
        {
            return;
        }

        mainSim.leaderboardManager.OkPressed();
        Log.LogInfo("已自动确认 leaderboard 结果页面");
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
            RunnerStateProtocol.MarkFailed(
                activeRequest,
                stopReason == StopReason.Timeout
                    ? $"request timed out after {(activeRequest.TimeoutSeconds ?? runnerConfig.DefaultRequestTimeoutSeconds.Value):0.###}s"
                    : activeRequest.LastError ?? "stop requested",
                DateTimeOffset.UtcNow
            );
            stateStore.Write(activeRequest);
        }

        OracleRunnerStateFile? nextRequest = pendingRequest;
        activeRequest = null;
        pendingRequest = null;
        stopReason = StopReason.None;
        if (nextRequest != null)
        {
            TryStartRequest(mainSim, nextRequest);
        }
        else
        {
            EnsureStateFileReady(mainSim);
        }
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
}
