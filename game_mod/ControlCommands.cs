using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

namespace TFWROracleRunner;

// 控制命令：保存、排行榜结果页、脚本窗口管理；与 run/prepare/quit 共用请求 ID、文件锁与终态确认。
public sealed partial class Plugin
{
    // open 读取的源码上限，避免误把大文件读进存档窗口。
    private const long MaxCodeFileBytes = 1L << 20;

    // 所有保存操作共用句柄；quit 额外等待同一请求的 done 落盘。
    private OracleRunnerStateFile? savingRequest;
    private Task<bool>? saveTask;
    private float saveStartedAt;

    private static bool IsImmediateCommand(string command) =>
        command is "play" or "stop" or "ok" or "list" or "minimize" or "unminimize";

    private static bool IsKnownCommand(string command) => command is
        "run" or "prepare" or "quit" or "save" or "play" or "stop" or "ok"
        or "open" or "close" or "dock" or "arrange" or "list" or "minimize" or "unminimize";

    /// <summary>执行不等待空闲的即时命令；stop 主动停止当前脚本。</summary>
    private void ExecuteImmediateCommand(MainSim mainSim, OracleRunnerStateFile request, string command)
    {
        try
        {
            RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
            request.ResultText = command switch
            {
                "play" => Play(mainSim),
                "stop" => Stop(mainSim),
                "ok" => CloseLeaderboardResult(mainSim),
                "list" => ListWindows(mainSim),
                "minimize" => SetWindowMinimized(mainSim, request, true),
                "unminimize" => SetWindowMinimized(mainSim, request, false),
                _ => null
            };
            RunnerStateProtocol.MarkDone(request, DateTimeOffset.UtcNow);
            Log.LogInfo($"控制请求完成 command={command} request_id={request.RequestId}" +
                        (string.IsNullOrEmpty(request.ResultText) ? string.Empty : $" result={request.ResultText}"));
        }
        catch (Exception ex)
        {
            MarkFailedWithOutput(request, $"control command failed: {ex.Message}", DateTimeOffset.UtcNow);
        }
        stateStore.Write(request);
        lastHandledRequestId = Math.Max(lastHandledRequestId, request.RequestId);
    }

    /// <summary>工作区变更完成后统一保存；prepare 只确认工作区已就绪。</summary>
    private void ExecuteIdleCommand(MainSim mainSim, OracleRunnerStateFile request, string command)
    {
        try
        {
            switch (command)
            {
                case "prepare":
                    RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
                    RunnerStateProtocol.MarkDone(request, DateTimeOffset.UtcNow);
                    stateStore.Write(request);
                    Log.LogInfo($"控制请求完成 command=prepare workspace_ready=True request_id={request.RequestId}");
                    return;
                case "quit":
                case "save":
                    break;
                case "open":
                    OpenWindow(mainSim, request);
                    break;
                case "close":
                    CloseWindow(mainSim, request);
                    break;
                case "dock":
                    DockWindow(mainSim, request);
                    break;
                case "arrange":
                    ArrangeWindows(mainSim, request);
                    break;
                default:
                    throw new InvalidOperationException($"unknown command: {command}");
            }
            saveTask = Saver.Save(mainSim);
            savingRequest = request;
            saveStartedAt = Time.realtimeSinceStartup;
            RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
            stateStore.Write(request);
            Log.LogInfo($"等待游戏保存 request_id={request.RequestId} command={command}");
        }
        catch (Exception ex)
        {
            savingRequest = null;
            saveTask = null;
            MarkFailedWithOutput(request, $"control command failed: {ex.Message}", DateTimeOffset.UtcNow);
            stateStore.Write(request);
        }
    }

    /// <summary>保存期间占用请求；quit 只在同一请求的成功终态落盘后退出。</summary>
    private bool ObservePendingSave(MainSim mainSim, OracleRunnerStateFile? current)
    {
        if (savingRequest == null)
        {
            return false;
        }
        bool quitConfirmed = saveTask == null && savingRequest.Status == RunnerRequestStatus.Done && savingRequest.Command == "quit";
        if (current?.RequestId != savingRequest.RequestId ||
            (current.Status != RunnerRequestStatus.Running && current.Status != RunnerRequestStatus.Done &&
             !(quitConfirmed && current.Status == RunnerRequestStatus.Idle)))
        {
            // 取消或替换撤销后续退出，不回滚游戏已经开始的磁盘保存。
            if (current == null)
            {
                Log.LogWarning($"保存期间状态文件丢失，撤销后续退出 command={savingRequest.Command} request_id={savingRequest.RequestId}；磁盘保存可能仍在进行");
            }
            savingRequest = null;
            saveTask = null;
            return false;
        }
        if (saveTask == null)
        {
            savingRequest = null;
            if (quitConfirmed)
            {
                Log.LogInfo($"正常退出游戏 request_id={current.RequestId}");
                mainSim.menu.Quit();
            }
            return true;
        }

        double timeout = runnerConfig.SaveTimeoutSeconds.Value;
        if (!saveTask.IsCompleted && (timeout == 0 || Time.realtimeSinceStartup - saveStartedAt < timeout))
        {
            MaybeLogProgress($"等待游戏保存 request_id={current.RequestId}");
            return true;
        }

        Task<bool> save = saveTask;
        saveTask = null;
        if (!save.IsCompleted || save.Status != TaskStatus.RanToCompletion || !save.Result ||
            (mainSim.warningPopup != null && mainSim.warningPopup.gameObject.activeInHierarchy))
        {
            string reason = !save.IsCompleted ? "game save timed out; save may still finish in background"
                : save.Exception?.GetBaseException().Message ?? "game save was not confirmed; see game dialog and logs";
            MarkFailedWithOutput(current, $"control command failed: {reason}", DateTimeOffset.UtcNow);
            savingRequest = null;
            Log.LogWarning($"游戏保存未确认 command={current.Command} request_id={current.RequestId}：{reason}");
        }
        else
        {
            RunnerStateProtocol.MarkDone(current, DateTimeOffset.UtcNow);
            savingRequest = current.Command == "quit" ? current : null;
            Log.LogInfo($"控制请求完成 command={current.Command} request_id={current.RequestId}");
        }
        stateStore.Write(current);
        return true;
    }

    private string? Play(MainSim mainSim)
    {
        if (mainSim.workspace != null && mainSim.workspace.gameObject.activeInHierarchy)
        {
            return "already in workspace";
        }
        if (mainSim.menu == null || !mainSim.menu.gameObject.activeInHierarchy)
        {
            return "main menu not visible";
        }
        mainSim.menu.Play();
        MarkMenuPlayed();
        return "enter workspace";
    }

    private string? Stop(MainSim mainSim)
    {
        if (!mainSim.IsExecuting())
        {
            return "not executing";
        }
        mainSim.StopMainExecution();
        return "stop requested";
    }

    private string? CloseLeaderboardResult(MainSim mainSim)
    {
        if (mainSim.leaderboardManager == null || !mainSim.leaderboardManager.IsLeaderBoardScreenOpen)
        {
            return "no result screen";
        }
        mainSim.leaderboardManager.OkPressed();
        return "result screen closed";
    }

    private string? ListWindows(MainSim mainSim)
    {
        if (mainSim.workspace == null)
        {
            return string.Empty;
        }
        var names = new StringBuilder();
        foreach (var item in mainSim.workspace.codeWindows)
        {
            names.Append(item.Key);
            if (item.Value != null && item.Value.GetComponent<Window>()?.isMinimized == true)
            {
                names.Append("(min)");
            }
            names.Append(' ');
        }
        return names.ToString().Trim();
    }

    private string? SetWindowMinimized(MainSim mainSim, OracleRunnerStateFile request, bool minimize)
    {
        Window window = RequireWindow(mainSim, request.TargetScript, "minimize");
        window.SetMinmized(minimize);
        return minimize ? "minimized" : "unminimized";
    }

    private void OpenWindow(MainSim mainSim, OracleRunnerStateFile request)
    {
        Workspace workspace = mainSim.workspace
                              ?? throw new InvalidOperationException("workspace not ready");
        string name = NormalizeWindowName(request.TargetScript);
        if (string.IsNullOrEmpty(name) || !workspace.IsValidFileName(name))
        {
            throw new InvalidOperationException($"invalid window name: {request.TargetScript}");
        }
        if (FindWindow(workspace, name) != null)
        {
            throw new InvalidOperationException($"window already exists: {name}");
        }

        string code = ReadCodeFile(request.CodeFile);
        workspace.OpenCodeWindow(name, code, Vector2.zero);
        CodeWindow? created = FindWindow(workspace, name);
        CodeWindow? anchor = FindWindow(workspace, string.IsNullOrEmpty(request.SecondScript) ? "stand" : request.SecondScript);
        if (created != null && anchor != null && anchor != created)
        {
            Window createdWindow = RequireWindowOf(created);
            Window anchorWindow = RequireWindowOf(anchor);
            createdWindow.DockOnto(anchorWindow.LeastDockedChild ?? anchorWindow);
        }
    }

    private void CloseWindow(MainSim mainSim, OracleRunnerStateFile request)
    {
        if (mainSim.IsExecuting())
        {
            throw new InvalidOperationException("program is executing");
        }
        RequireWindow(mainSim, request.TargetScript, "close").Close();
    }

    private void DockWindow(MainSim mainSim, OracleRunnerStateFile request)
    {
        Window source = RequireWindow(mainSim, request.TargetScript, "dock");
        Window anchor = RequireWindow(mainSim, request.SecondScript, "dock");
        if (source == anchor)
        {
            throw new InvalidOperationException("dock needs two different windows");
        }
        source.Undock();
        source.DockOnto(anchor.LeastDockedChild ?? anchor);
    }

    private void ArrangeWindows(MainSim mainSim, OracleRunnerStateFile request)
    {
        Workspace workspace = mainSim.workspace
                              ?? throw new InvalidOperationException("workspace not ready");
        Window head = RequireWindow(mainSim, string.IsNullOrEmpty(request.TargetScript) ? "stand" : request.TargetScript, "arrange");
        head.Undock();
        var others = new List<Window>();
        foreach (var item in workspace.codeWindows)
        {
            if (item.Value == null)
            {
                continue;
            }
            Window? window = item.Value.GetComponent<Window>();
            if (window != null && window != head)
            {
                others.Add(window);
            }
        }
        others.Sort((left, right) => string.CompareOrdinal(left.windowName, right.windowName));
        foreach (Window window in others)
        {
            window.Undock();
        }
        foreach (Window window in others)
        {
            window.DockOnto(head.LeastDockedChild ?? head);
        }
    }

    private Window RequireWindow(MainSim mainSim, string? name, string command)
    {
        CodeWindow? window = FindWindow(mainSim.workspace, name);
        if (window == null)
        {
            throw new InvalidOperationException($"{command}: window not found: {name}");
        }
        return RequireWindowOf(window);
    }

    private static Window RequireWindowOf(CodeWindow codeWindow) =>
        codeWindow.GetComponent<Window>() ?? throw new InvalidOperationException("window component missing");

    private static CodeWindow? FindWindow(Workspace? workspace, string? name)
    {
        string normalized = NormalizeWindowName(name);
        if (workspace == null || string.IsNullOrEmpty(normalized))
        {
            return null;
        }
        if (workspace.codeWindows.TryGetValue(normalized, out CodeWindow? exact))
        {
            return exact;
        }
        foreach (var item in workspace.codeWindows)
        {
            if (string.Equals(item.Key, normalized, StringComparison.OrdinalIgnoreCase))
            {
                return item.Value;
            }
        }
        return null;
    }

    private static string NormalizeWindowName(string? name)
    {
        string value = (name ?? string.Empty).Trim();
        if (value.EndsWith(".py", StringComparison.OrdinalIgnoreCase))
        {
            value = value[..^3];
        }
        return value;
    }

    /// <summary>读入 open 的源码文件；缺失、超限或类型不对时拒绝，避免把存档写坏。</summary>
    private static string ReadCodeFile(string? path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return string.Empty;
        }
        FileInfo info = new(path);
        if (!info.Exists)
        {
            throw new InvalidOperationException($"code file not found: {path}");
        }
        if (info.Length > MaxCodeFileBytes)
        {
            throw new InvalidOperationException($"code file too large: {info.Length} bytes");
        }
        return File.ReadAllText(info.FullName);
    }
}
