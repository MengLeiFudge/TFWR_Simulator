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
            "Advanced",
            "DefaultTargetScript",
            "lb_start",
            "请求没有给 target_script 时使用的窗口名，不带 .py。");
        AutoPlayMainMenu = config.Bind(
            "General",
            "AutoPlayMainMenu",
            false,
            "是否在没有外部请求时自动进入游戏。外部请求会自行进入工作区，不受此项限制。");
        StartupPollIntervalMs = config.Bind(
            "Advanced",
            "StartupPollIntervalMs",
            250,
            "轮询主菜单、工作区和 state.json 的时间间隔（毫秒），一般不用改。");
        ScriptReadyTimeoutSeconds = config.Bind(
            "Advanced",
            "ScriptReadyTimeoutSeconds",
            30f,
            "等待脚本窗口出现的最长时间（秒），一般不用改。");
        DefaultRequestTimeoutSeconds = config.Bind(
            "Advanced",
            "DefaultRequestTimeoutSeconds",
            20f,
            "请求未给 timeout_seconds 时的默认执行超时（秒），一般不用改。");
        SaveTimeoutSeconds = config.Bind(
            "Advanced",
            "SaveTimeoutSeconds",
            30f,
            new ConfigDescription(
                "等待游戏保存的独立上限（秒，1至300）；请求 timeout_seconds=0 时仍生效。",
                new AcceptableValueRange<float>(1f, 300f)));
        AutoOkLeaderboardResult = config.Bind(
            "General",
            "AutoOkLeaderboardResult",
            false,
            "排行榜结果页一出现就按 OK。外部队列等待运行结束时，结果页会继续让游戏报告 executing=true。");
        RequestStopGracePeriodSeconds = config.Bind(
            "Advanced",
            "RequestStopGracePeriodSeconds",
            3f,
            "停止后等待 StopMainExecution() 生效的观察窗口（秒），一般不用改。");
    }

    public ConfigEntry<bool> Enabled { get; }

    public ConfigEntry<string> TargetScriptName { get; }

    public ConfigEntry<bool> AutoPlayMainMenu { get; }

    public ConfigEntry<int> StartupPollIntervalMs { get; }

    public ConfigEntry<float> ScriptReadyTimeoutSeconds { get; }

    public ConfigEntry<float> DefaultRequestTimeoutSeconds { get; }

    public ConfigEntry<float> SaveTimeoutSeconds { get; }

    public ConfigEntry<float> RequestStopGracePeriodSeconds { get; }

    public ConfigEntry<bool> AutoOkLeaderboardResult { get; }
}
