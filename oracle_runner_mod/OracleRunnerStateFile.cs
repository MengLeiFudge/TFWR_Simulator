namespace TFWROracleRunner;

public sealed class OracleRunnerStateFile
{
    public int RequestId { get; set; }

    public RunnerRequestStatus Status { get; set; }

    public string? TargetScript { get; set; }

    public double? TimeoutSeconds { get; set; }

    public string? StartedAt { get; set; }

    public string? FinishedAt { get; set; }

    public string? LastError { get; set; }
}
