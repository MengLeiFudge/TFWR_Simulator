using Xunit;

namespace TFWROracleRunner;

public sealed class LeaderboardResultAutoCloseGateTests
{
    [Fact]
    public void NewGate_DoesNotAllowManualResultAutoClose()
    {
        LeaderboardResultAutoCloseGate gate = new LeaderboardResultAutoCloseGate();

        Assert.False(gate.ExternalResultPendingClose);
    }

    [Fact]
    public void MarkExternalLeaderboardObserved_AllowsExternalResultAutoClose()
    {
        LeaderboardResultAutoCloseGate gate = new LeaderboardResultAutoCloseGate();

        gate.MarkExternalLeaderboardObserved();

        Assert.True(gate.ExternalResultPendingClose);
    }

    [Fact]
    public void Clear_RemovesExternalResultAutoClosePermission()
    {
        LeaderboardResultAutoCloseGate gate = new LeaderboardResultAutoCloseGate();
        gate.MarkExternalLeaderboardObserved();

        gate.Clear();

        Assert.False(gate.ExternalResultPendingClose);
    }
}
