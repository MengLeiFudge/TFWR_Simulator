using System;
using System.Globalization;

namespace TFWROracleRunner;

public static class LeaderboardLogFormatter
{
    public static string FormatStartLine(string scriptName)
    {
        return string.Format(
            CultureInfo.InvariantCulture,
            "[{0}] start",
            RunnerStateProtocol.NormalizeTargetScriptName(scriptName)
        );
    }

    public static string FormatRunLine(string scriptName, int runIndex, TimeSpan timeSpan)
    {
        return string.Format(
            CultureInfo.InvariantCulture,
            "[{0}] run={1} time={2}",
            RunnerStateProtocol.NormalizeTargetScriptName(scriptName),
            runIndex,
            FormatClock(timeSpan)
        );
    }

    public static string FormatSummaryLine(string scriptName, bool finished, int runCount, TimeSpan averageTime)
    {
        return string.Format(
            CultureInfo.InvariantCulture,
            "[{0}] finished={1} runs={2} average={3}",
            RunnerStateProtocol.NormalizeTargetScriptName(scriptName),
            finished ? "true" : "false",
            runCount,
            FormatClock(averageTime)
        );
    }

    public static string FormatClock(TimeSpan timeSpan)
    {
        int totalMinutes = (int)Math.Floor(timeSpan.TotalMinutes);
        return string.Format(
            CultureInfo.InvariantCulture,
            "{0}:{1:00}.{2:000}",
            totalMinutes,
            timeSpan.Seconds,
            timeSpan.Milliseconds
        );
    }
}
