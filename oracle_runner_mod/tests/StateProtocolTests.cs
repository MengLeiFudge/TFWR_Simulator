using System;
using System.IO;
using System.Threading.Tasks;
using Xunit;

namespace TFWROracleRunner;

public sealed class StateProtocolTests
{
    [Fact]
    public void NormalizeTargetScriptName_RemovesPySuffix()
    {
        Assert.Equal("lb_start", RunnerStateProtocol.NormalizeTargetScriptName("lb_start.py"));
        Assert.Equal("simulate", RunnerStateProtocol.NormalizeTargetScriptName(" simulate "));
    }

    [Fact]
    public void CreateRequested_UsesRequestedStatusAndNullTimestamps()
    {
        OracleRunnerStateFile state = RunnerStateProtocol.CreateRequested(7, "lb_start.py", 20.0);

        Assert.Equal(7, state.RequestId);
        Assert.Equal(RunnerRequestStatus.Requested, state.Status);
        Assert.Equal("lb_start", state.TargetScript);
        Assert.Equal(20.0, state.TimeoutSeconds);
        Assert.Null(state.StartedAt);
        Assert.Null(state.FinishedAt);
        Assert.Null(state.LastError);
    }

    [Fact]
    public void MarkSuperseded_UsesDedicatedStatusAndIsoTime()
    {
        OracleRunnerStateFile state = RunnerStateProtocol.CreateRequested(3, "lb_start", 25.0);
        DateTimeOffset finishedAt = new DateTimeOffset(2026, 4, 22, 12, 0, 1, TimeSpan.Zero);

        RunnerStateProtocol.MarkSuperseded(state, 4, finishedAt);

        Assert.Equal(RunnerRequestStatus.Superseded, state.Status);
        Assert.Equal("superseded by request_id=4", state.LastError);
        Assert.Equal("2026-04-22T12:00:01.0000000+00:00", state.FinishedAt);
    }

    [Fact]
    public void RunnerStateStore_RoundTripsTimeoutSeconds()
    {
        string statePath = Path.Combine(Path.GetTempPath(), $"tfwr-state-{Guid.NewGuid():N}.json");
        try
        {
            RunnerStateStore store = new RunnerStateStore(statePath);
            OracleRunnerStateFile requested = RunnerStateProtocol.CreateRequested(5, "lb_start", 600.0);

            store.Write(requested);
            OracleRunnerStateFile? restored = store.Read();

            Assert.NotNull(restored);
            Assert.Equal(600.0, restored!.TimeoutSeconds);
            Assert.Equal("lb_start", restored.TargetScript);
            Assert.Equal(RunnerRequestStatus.Requested, restored.Status);
        }
        finally
        {
            if (File.Exists(statePath))
            {
                File.Delete(statePath);
            }
        }
    }

    [Fact]
    public async Task RunnerStateStore_WriteRetriesWhenFileIsTemporarilyLocked()
    {
        string statePath = Path.Combine(Path.GetTempPath(), $"tfwr-lock-{Guid.NewGuid():N}.json");
        File.WriteAllText(statePath, "{}");
        FileStream lockStream = new FileStream(statePath, FileMode.Open, FileAccess.ReadWrite, FileShare.None);

        try
        {
            RunnerStateStore store = new RunnerStateStore(statePath);
            OracleRunnerStateFile requested = RunnerStateProtocol.CreateRequested(6, "lb_start", 600.0);

            Task releaseTask = Task.Run(async () =>
            {
                await Task.Delay(100);
                lockStream.Dispose();
            });

            store.Write(requested);
            await releaseTask;

            OracleRunnerStateFile? restored = store.Read();
            Assert.NotNull(restored);
            Assert.Equal(600.0, restored!.TimeoutSeconds);
        }
        finally
        {
            lockStream.Dispose();
            if (File.Exists(statePath))
            {
                File.Delete(statePath);
            }
        }
    }
}
