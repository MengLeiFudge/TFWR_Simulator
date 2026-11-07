using System;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;

namespace TFWROracleRunner;

/// <summary>
/// 协调状态文件的原子读改写。两端独占创建同名 .lock 文件；锁内只做文件操作。
/// 写入先保存独立快照，由下一次 Read 落盘，失败后保留快照等待后续轮询。
/// </summary>
public sealed class RunnerStateStore
{
    private readonly string stateFilePath;
    private readonly object gate = new();
    private OracleRunnerStateFile? pendingState;

    /// <summary>创建状态存储，不执行文件 I/O。</summary>
    /// <param name="stateFilePath">当前 BepInEx profile 的状态文件路径。</param>
    public RunnerStateStore(string stateFilePath)
    {
        this.stateFilePath = stateFilePath;
    }

    /// <summary>客户端连接时使用的状态文件路径。</summary>
    public string StateFilePath => stateFilePath;

    /// <summary>
    /// 尝试一次加锁、读取和刷新待写状态。文件缺失返回 null；锁占用或读取失败抛出异常，
    /// 调用方应等待下一次轮询，不得把失败当成缺失并重置状态。
    /// </summary>
    /// <returns>刷新后的状态；仅文件尚未创建时为 null。</returns>
    public OracleRunnerStateFile? Read()
    {
        lock (gate)
        {
            string? directory = Path.GetDirectoryName(stateFilePath);
            if (!string.IsNullOrWhiteSpace(directory))
            {
                Directory.CreateDirectory(directory);
            }

            string lockPath = stateFilePath + ".lock";
            // CreateNew 与 Python 的 O_EXCL 共用文件系统原子性，适用于 Windows/WSL。
            using FileStream lease = new FileStream(lockPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            try
            {
                OracleRunnerStateFile? current = ReadCurrent();
                if (pendingState == null)
                {
                    return current;
                }

                // 新请求由客户端拥有。旧请求的终态不能覆盖它；同一请求的停止指令
                // 也不能被较早排队的 running 状态覆盖，但允许正常终态完成该请求。
                bool canWrite = current == null ||
                    (current.RequestId == pendingState.RequestId &&
                     !(pendingState.Status == RunnerRequestStatus.Running &&
                       current.Status != RunnerRequestStatus.Requested &&
                       current.Status != RunnerRequestStatus.Running));
                if (canWrite)
                {
                    WriteCurrent(pendingState);
                    current = pendingState;
                }
                pendingState = null;
                return current;
            }
            finally
            {
                lease.Dispose();
                File.Delete(lockPath);
            }
        }
    }

    /// <summary>保存待写快照，不阻塞游戏线程；后续 Read 负责持锁落盘。</summary>
    /// <param name="state">当前请求的新状态，后续修改原对象不会改变已排队快照。</param>
    public void Write(OracleRunnerStateFile state)
    {
        lock (gate)
        {
            pendingState = new OracleRunnerStateFile
            {
                RequestId = state.RequestId,
                Status = state.Status,
                Command = state.Command,
                TargetScript = state.TargetScript,
                TimeoutSeconds = state.TimeoutSeconds,
                StartedAt = state.StartedAt,
                FinishedAt = state.FinishedAt,
                LastError = state.LastError,
            };
        }
    }

    /// <summary>读取锁内状态，使用标准 JSON 序列化器处理 Unicode 和控制字符。</summary>
    /// <returns>当前状态；文件缺失时为 null。</returns>
    private OracleRunnerStateFile? ReadCurrent()
    {
        try
        {
            using FileStream stream = new FileStream(
                stateFilePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            var serializer = new DataContractJsonSerializer(typeof(OracleRunnerStateFile));
            var state = serializer.ReadObject(stream) as OracleRunnerStateFile
                ?? throw new SerializationException("状态文件必须是 JSON 对象。");
            if (state.RequestId < 0 ||
                (state.TimeoutSeconds.HasValue &&
                 (double.IsNaN(state.TimeoutSeconds.Value) || double.IsInfinity(state.TimeoutSeconds.Value) ||
                  state.TimeoutSeconds.Value < 0)))
            {
                throw new SerializationException("request_id 和 timeout_seconds 必须是非负有限数值。");
            }
            return state;
        }
        catch (FileNotFoundException)
        {
            return null;
        }
    }

    /// <summary>锁内使用同目录临时文件原子替换状态，不重试或等待。</summary>
    /// <param name="state">要持久化的完整状态。</param>
    private void WriteCurrent(OracleRunnerStateFile state)
    {
        string tempPath = $"{stateFilePath}.{Guid.NewGuid():N}.tmp";
        try
        {
            using (FileStream stream = new FileStream(tempPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                var serializer = new DataContractJsonSerializer(typeof(OracleRunnerStateFile));
                serializer.WriteObject(stream, state);
            }
            if (File.Exists(stateFilePath))
            {
                File.Replace(tempPath, stateFilePath, null, ignoreMetadataErrors: true);
            }
            else
            {
                File.Move(tempPath, stateFilePath);
            }
        }
        finally
        {
            File.Delete(tempPath);
        }
    }
}
