using System;
using Xunit;

namespace TFWROracleRunner;

public sealed class LeaderboardLogFormatterTests
{
    [Fact]
    public void FormatStartLine_FormatsBracketedScriptName()
    {
        string line = LeaderboardLogFormatter.FormatStartLine("lb_hay_single.py");

        Assert.Equal("[lb_hay_single] start", line);
    }

    [Fact]
    public void FormatRunLine_FormatsSingleRunTime()
    {
        string line = LeaderboardLogFormatter.FormatRunLine("lb_hay_single.py", 3, TimeSpan.FromMilliseconds(174342));

        Assert.Equal("[lb_hay_single] run=3 time=2:54.342", line);
    }

    [Fact]
    public void FormatSummaryLine_FormatsAverageTime()
    {
        string line = LeaderboardLogFormatter.FormatSummaryLine("lb_hay_single.py", true, 4, TimeSpan.FromMilliseconds(166476));

        Assert.Equal("[lb_hay_single] finished=true runs=4 average=2:46.476", line);
    }
}
