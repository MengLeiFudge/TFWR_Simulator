using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

namespace TFWROracleRunner;

// 控制命令：保存、排行榜结果页、脚本窗口管理；与 run/prepare/quit 共用请求 ID、文件锁与终态确认。
public sealed partial class Plugin
{
    // open 读取的源码上限，避免误把大文件读进存档窗口。
    private const long MaxCodeFileBytes = 1L << 20;

    // 等待沙箱保存完成的请求；窗口变更和保存命令共用。
    private int saveRequestId = -1;
    private Task<bool>? saveTask;

    private static bool IsImmediateCommand(string command) =>
        command is "play" or "stop" or "ok" or "list" or "minimize" or "unminimize";

    /// <summary>0.3.0 新增的控制命令要求调用方声明协议 3。</summary>
    private static bool RequiresProtocol3(string command) =>
        command is "save" or "open" or "close" or "dock" or "arrange" or "play" or "stop" or "ok"
            or "list" or "minimize" or "unminimize";

    private static bool IsKnownCommand(string command) =>
        command is "run" or "prepare" or "quit" or "save" or "open" or "close" or "dock" or "arrange"
        || IsImmediateCommand(command);

    /// <summary>执行不打断脚本即时的命令；状态写入与终态确认由本方法负责。</summary>
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

    /// <summary>执行需要工作区空闲的命令；需要保存的请求由轮询继续确认终态。</summary>
    private void ExecuteIdleCommand(MainSim mainSim, OracleRunnerStateFile request, string command)
    {
        try
        {
            switch (command)
            {
                case "quit":
                    QuitGame(mainSim, request);
                    return;
                case "prepare":
                    RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
                    RunnerStateProtocol.MarkDone(request, DateTimeOffset.UtcNow);
                    Log.LogInfo($"控制请求完成 command=prepare workspace_ready=True request_id={request.RequestId}");
                    break;
                case "save":
                    BeginSave(mainSim, request);
                    return;
                case "open":
                    OpenWindow(mainSim, request);
                    return;
                case "close":
                    CloseWindow(mainSim, request);
                    return;
                case "dock":
                    DockWindow(mainSim, request);
                    return;
                case "arrange":
                    ArrangeWindows(mainSim, request);
                    return;
                default:
                    throw new InvalidOperationException($"unknown command: {command}");
            }
        }
        catch (Exception ex)
        {
            MarkFailedWithOutput(request, $"control command failed: {ex.Message}", DateTimeOffset.UtcNow);
        }
        stateStore.Write(request);
    }

    /// <summary>quit 与保存命令共用异步保存句柄；保存确认后发布终态，quit 再退出游戏。</summary>
    private void QuitGame(MainSim mainSim, OracleRunnerStateFile request)
    {
        quitSaveTask = Saver.Save(mainSim);
        quitRequestId = request.RequestId;
        RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
        stateStore.Write(request);
        lastHandledRequestId = request.RequestId;
        Log.LogInfo($"等待游戏保存 request_id={request.RequestId}");
    }

    private void BeginSave(MainSim mainSim, OracleRunnerStateFile request)
    {
        RunnerStateProtocol.MarkRunning(request, DateTimeOffset.UtcNow);
        stateStore.Write(request);
        saveRequestId = request.RequestId;
        saveTask = Saver.Save(mainSim);
        lastHandledRequestId = Math.Max(lastHandledRequestId, request.RequestId);
        Log.LogInfo($"等待游戏保存 request_id={request.RequestId} command={request.Command}");
    }

    /// <summary>逐帧观察保存完成情况；失败时保留现场并报告，不提前确认成功。</summary>
    private void ObservePendingSave(MainSim mainSim, OracleRunnerStateFile? current)
    {
        if (saveRequestId < 0)
        {
            return;
        }
        int requestId = saveRequestId;
        if (current?.RequestId != requestId ||
            (current.Status != RunnerRequestStatus.Running && current.Status != RunnerRequestStatus.Done))
        {
            saveRequestId = -1;
            saveTask = null;
            return;
        }
        if (saveTask == null)
        {
            saveRequestId = -1;
            return;
        }
        if (!saveTask.IsCompleted)
        {
            MaybeLogProgress($"等待游戏保存 request_id={requestId}");
            return;
        }

        Task<bool> save = saveTask;
        saveTask = null;
        saveRequestId = -1;
        if (save.Status != TaskStatus.RanToCompletion || !save.Result ||
            (mainSim.warningPopup != null && mainSim.warningPopup.gameObject.activeInHierarchy))
        {
            string reason = save.Exception?.GetBaseException().Message
                            ?? "game save was not confirmed; see game dialog and logs";
            MarkFailedWithOutput(current, $"control command failed: {reason}", DateTimeOffset.UtcNow);
            Log.LogWarning($"游戏保存未确认 command={current.Command} request_id={requestId}：{reason}");
        }
        else
        {
            RunnerStateProtocol.MarkDone(current, DateTimeOffset.UtcNow);
            Log.LogInfo($"控制请求完成 command={current.Command} request_id={requestId}");
        }
        stateStore.Write(current);
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
        BeginSave(mainSim, request);
    }

    private void CloseWindow(MainSim mainSim, OracleRunnerStateFile request)
    {
        if (mainSim.IsExecuting())
        {
            throw new InvalidOperationException("program is executing");
        }
        RequireWindow(mainSim, request.TargetScript, "close").Close();
        BeginSave(mainSim, request);
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
        BeginSave(mainSim, request);
    }

    private void ArrangeWindows(MainSim mainSim, OracleRunnerStateFile request)
    {
        Workspace workspace = mainSim.workspace
                              ?? throw new InvalidOperationException("workspace not ready");
        Window head = RequireWindow(mainSim, string.IsNullOrEmpty(request.TargetScript) ? "stand" : request.TargetScript, "arrange");
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
        BeginSave(mainSim, request);
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
