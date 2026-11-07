namespace TFWROracleRunner;

public sealed class LeaderboardResultAutoCloseGate
{
    private bool externalResultPendingClose;

    public bool ExternalResultPendingClose => externalResultPendingClose;

    public void MarkExternalLeaderboardObserved()
    {
        externalResultPendingClose = true;
    }

    public void Clear()
    {
        externalResultPendingClose = false;
    }
}
