using BepInEx.Configuration;

namespace TFWROracleRunner;

internal sealed class OracleRunnerConfig
{
    public OracleRunnerConfig(ConfigFile config)
    {
        Enabled = config.Bind(
            "General",
            "Enabled",
            true,
            "是否启用自动权威执行器。");
        TargetScriptName = config.Bind(
            "General",
            "TargetScriptName",
            "lb_start",
            "目标脚本窗口名，不带 .py。");
        AutoPlayMainMenu = config.Bind(
            "General",
            "AutoPlayMainMenu",
            false,
            "是否在没有外部请求时自动进入游戏。外部请求会自行进入工作区，不受此项限制。");
        StartupPollIntervalMs = config.Bind(
            "Timing",
            "StartupPollIntervalMs",
            250,
            "轮询主菜单、工作区和 state.json 的时间间隔（毫秒）。");
        ScriptReadyTimeoutSeconds = config.Bind(
            "Timing",
            "ScriptReadyTimeoutSeconds",
            30f,
            "等待脚本窗口出现的最长时间（秒）。仅用于单次 requested 请求启动期。");
        DefaultRequestTimeoutSeconds = config.Bind(
            "Timing",
            "DefaultRequestTimeoutSeconds",
            20f,
            "state.json 未显式提供 timeout_seconds 时，单次请求的默认执行超时（秒）。");
        AutoOkLeaderboardResult = config.Bind(
            "General",
            "AutoOkLeaderboardResult",
            false,
            "排行榜结果页一出现就按 OK。外部队列等待运行结束时，结果页会继续让游戏报告 executing=true。");
        RequestStopGracePeriodSeconds = config.Bind(
            "Timing",
            "RequestStopGracePeriodSeconds",
            3f,
            "收到覆盖请求或超时停止后，等待 StopMainExecution() 生效的提示窗口（秒）。");
    }

    public ConfigEntry<bool> Enabled { get; }

    public ConfigEntry<string> TargetScriptName { get; }

    public ConfigEntry<bool> AutoPlayMainMenu { get; }

    public ConfigEntry<int> StartupPollIntervalMs { get; }

    public ConfigEntry<float> ScriptReadyTimeoutSeconds { get; }

    public ConfigEntry<float> DefaultRequestTimeoutSeconds { get; }

    public ConfigEntry<float> RequestStopGracePeriodSeconds { get; }

    public ConfigEntry<bool> AutoOkLeaderboardResult { get; }
}
