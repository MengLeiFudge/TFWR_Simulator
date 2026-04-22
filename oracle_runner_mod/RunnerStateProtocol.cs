using System;

namespace TFWROracleRunner;

public static class RunnerStateProtocol
{
    public const string StateFileName = "mlj.tfwr.oracle-runner.state.json";

    public static string NormalizeTargetScriptName(string? configuredName)
    {
        string raw = (configuredName ?? string.Empty).Trim();
        if (raw.EndsWith(".py", StringComparison.OrdinalIgnoreCase))
        {
            raw = raw[..^3];
        }

        return string.IsNullOrWhiteSpace(raw) ? "lb_start" : raw;
    }

    public static OracleRunnerStateFile CreateIdle(int requestId)
    {
        return new OracleRunnerStateFile
        {
            RequestId = requestId,
            Status = RunnerRequestStatus.Idle,
            TargetScript = null,
            TimeoutSeconds = null,
            StartedAt = null,
            FinishedAt = null,
            LastError = null,
        };
    }

    public static OracleRunnerStateFile CreateRequested(int requestId, string targetScript, double timeoutSeconds)
    {
        return new OracleRunnerStateFile
        {
            RequestId = requestId,
            Status = RunnerRequestStatus.Requested,
            TargetScript = NormalizeTargetScriptName(targetScript),
            TimeoutSeconds = timeoutSeconds,
            StartedAt = null,
            FinishedAt = null,
            LastError = null,
        };
    }

    public static void MarkSuperseded(OracleRunnerStateFile state, int supersededByRequestId, DateTimeOffset finishedAt)
    {
        state.Status = RunnerRequestStatus.Superseded;
        state.FinishedAt = ToIso8601(finishedAt);
        state.LastError = $"superseded by request_id={supersededByRequestId}";
    }

    public static void MarkRunning(OracleRunnerStateFile state, DateTimeOffset startedAt)
    {
        state.Status = RunnerRequestStatus.Running;
        state.StartedAt = ToIso8601(startedAt);
        state.FinishedAt = null;
        state.LastError = null;
    }

    public static void MarkDone(OracleRunnerStateFile state, DateTimeOffset finishedAt)
    {
        state.Status = RunnerRequestStatus.Done;
        state.FinishedAt = ToIso8601(finishedAt);
        state.LastError = null;
    }

    public static void MarkFailed(OracleRunnerStateFile state, string message, DateTimeOffset finishedAt)
    {
        state.Status = RunnerRequestStatus.Failed;
        state.FinishedAt = ToIso8601(finishedAt);
        state.LastError = message;
    }

    public static string ToIso8601(DateTimeOffset value)
    {
        return value.ToString("O");
    }

    public static string ToStatusText(RunnerRequestStatus status)
    {
        return status.ToString().ToLowerInvariant();
    }

    public static RunnerRequestStatus ParseStatusText(string? text)
    {
        return (text ?? string.Empty).Trim().ToLowerInvariant() switch
        {
            "idle" => RunnerRequestStatus.Idle,
            "requested" => RunnerRequestStatus.Requested,
            "running" => RunnerRequestStatus.Running,
            "done" => RunnerRequestStatus.Done,
            "failed" => RunnerRequestStatus.Failed,
            "superseded" => RunnerRequestStatus.Superseded,
            _ => RunnerRequestStatus.Idle,
        };
    }
}
