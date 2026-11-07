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
    /// <summary>模组支持的协议版本；版本2支持prepare与quit控制命令。</summary>
    [DataMember(Name = "protocol_version")]
    public int ProtocolVersion { get; set; } = 2;

    /// <summary>run执行脚本，prepare准备工作区，quit保存后退出；缺省为run。</summary>
    [DataMember(Name = "command")]
    public string? Command { get; set; }

    /// <summary>游戏内已有脚本窗口的名称。</summary>
    [DataMember(Name = "target_script")]
    public string? TargetScript { get; set; }

    /// <summary>请求的墙钟超时秒数；零表示不限制执行时间。</summary>
    [DataMember(Name = "timeout_seconds")]
    public double? TimeoutSeconds { get; set; }

    /// <summary>执行开始的 ISO 8601 时间。</summary>
    [DataMember(Name = "started_at")]
    public string? StartedAt { get; set; }

    /// <summary>执行结束的 ISO 8601 时间。</summary>
    [DataMember(Name = "finished_at")]
    public string? FinishedAt { get; set; }

    /// <summary>失败或取消原因。</summary>
    [DataMember(Name = "last_error")]
    public string? LastError { get; set; }
}
