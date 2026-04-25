namespace TFWROracleRunner;

public enum RunnerRequestStatus
{
    Idle,
    Requested,
    Running,
    StopRequested,
    Done,
    Failed,
    Superseded,
}
