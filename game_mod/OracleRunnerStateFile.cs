using System.Runtime.Serialization;

namespace TFWROracleRunner;

/// <summary>文件协议中的请求与执行状态，字段名与 Python 客户端保持一致。</summary>
[DataContract]
public sealed class OracleRunnerStateFile
{
    /// <summary>同一状态文件内递增的请求编号。</summary>
    [DataMember(Name = "request_id", IsRequired = true)]
    public int RequestId { get; set; }

    /// <summary>执行器内部使用的状态枚举。</summary>
    public RunnerRequestStatus Status { get; set; }

    // JSON 使用字符串状态，避免把枚举的数值顺序暴露给客户端。
    [DataMember(Name = "status", IsRequired = true)]
    private string StatusText
    {
        get => RunnerStateProtocol.ToStatusText(Status);
        set => Status = RunnerStateProtocol.ParseStatusText(value);
    }
    /// <summary>模组支持的协议版本；版本2支持prepare与quit，版本3增加save、ok、list等控制命令，版本4取消运行时限并允许终态直接被新请求替换。只由模组写入，客户端只读。</summary>
    [DataMember(Name = "protocol_version")]
    public int ProtocolVersion { get; set; } = RunnerStateProtocol.CurrentProtocolVersion;

    /// <summary>游戏自己的后台保存是否仍在进行；与请求终态无关，客户端据此阻止覆盖可能被旧快照写回的存档脚本。</summary>
    [DataMember(Name = "saving")]
    public bool Saving { get; set; }

    /// <summary>run执行脚本，prepare准备工作区，quit保存后退出；缺省为run。</summary>
    [DataMember(Name = "command")]
    public string? Command { get; set; }

    /// <summary>游戏内已有脚本窗口的名称。</summary>
    [DataMember(Name = "target_script")]
    public string? TargetScript { get; set; }

    /// <summary>执行开始的 ISO 8601 时间。</summary>
    [DataMember(Name = "started_at")]
    public string? StartedAt { get; set; }

    /// <summary>执行结束的 ISO 8601 时间。</summary>
    [DataMember(Name = "finished_at")]
    public string? FinishedAt { get; set; }

    /// <summary>dock 的锚点窗口；open 缺省停靠到 stand。</summary>
    [DataMember(Name = "second_script", EmitDefaultValue = false)]
    public string? SecondScript { get; set; }

    /// <summary>open 命令读取的代码文件绝对路径；省略时创建空窗口。</summary>
    [DataMember(Name = "code_file", EmitDefaultValue = false)]
    public string? CodeFile { get; set; }

    /// <summary>游戏当前是否有程序在运行；结果页打开时游戏仍报告执行中。</summary>
    [DataMember(Name = "executing", EmitDefaultValue = false)]
    public bool? Executing { get; set; }

    /// <summary>排行榜统计是否在跑。</summary>
    [DataMember(Name = "leaderboard_running", EmitDefaultValue = false)]
    public bool? LeaderboardRunning { get; set; }

    /// <summary>排行榜结果页是否打开。</summary>
    [DataMember(Name = "leaderboard_screen", EmitDefaultValue = false)]
    public bool? LeaderboardScreen { get; set; }

    /// <summary>正在执行的脚本窗口；执行期间改它的文件会让游戏停止程序。</summary>
    [DataMember(Name = "busy_windows", EmitDefaultValue = false)]
    public string[]? BusyWindows { get; set; }

    /// <summary>命令返回的文本结果，例如 list 的窗口清单。</summary>
    [DataMember(Name = "result_text", EmitDefaultValue = false)]
    public string? ResultText { get; set; }

    /// <summary>失败或取消原因。</summary>
    [DataMember(Name = "last_error")]
    public string? LastError { get; set; }
}
