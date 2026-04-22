using System;
using System.Globalization;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;

namespace TFWROracleRunner;

public sealed class RunnerStateStore
{
    private const int MaxAttempts = 20;
    private const int RetryDelayMilliseconds = 50;
    private readonly string stateFilePath;
    private readonly object gate = new();

    public RunnerStateStore(string stateFilePath)
    {
        this.stateFilePath = stateFilePath;
    }

    public string StateFilePath => stateFilePath;

    public OracleRunnerStateFile? Read()
    {
        lock (gate)
        {
            if (!File.Exists(stateFilePath))
            {
                return null;
            }

            try
            {
                for (int attempt = 0; attempt < MaxAttempts; attempt++)
                {
                    try
                    {
                        using FileStream stream = new FileStream(
                            stateFilePath,
                            FileMode.Open,
                            FileAccess.Read,
                            FileShare.ReadWrite | FileShare.Delete
                        );
                        using StreamReader reader = new StreamReader(stream, Encoding.UTF8, true);
                        string json = reader.ReadToEnd();
                        return new OracleRunnerStateFile
                        {
                            RequestId = ReadInt(json, "request_id"),
                            Status = RunnerStateProtocol.ParseStatusText(ReadString(json, "status")),
                            TargetScript = ReadString(json, "target_script"),
                            TimeoutSeconds = ReadNullableDouble(json, "timeout_seconds"),
                            StartedAt = ReadString(json, "started_at"),
                            FinishedAt = ReadString(json, "finished_at"),
                            LastError = ReadString(json, "last_error"),
                        };
                    }
                    catch (IOException) when (attempt + 1 < MaxAttempts)
                    {
                        Thread.Sleep(RetryDelayMilliseconds);
                    }
                    catch (UnauthorizedAccessException) when (attempt + 1 < MaxAttempts)
                    {
                        Thread.Sleep(RetryDelayMilliseconds);
                    }
                }
                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }
    }

    public void Write(OracleRunnerStateFile state)
    {
        lock (gate)
        {
            string? directory = Path.GetDirectoryName(stateFilePath);
            if (!string.IsNullOrWhiteSpace(directory))
            {
                Directory.CreateDirectory(directory);
            }

            string json = BuildJson(state);
            string tempPath = $"{stateFilePath}.{Guid.NewGuid():N}.tmp";
            Exception? lastError = null;

            try
            {
                for (int attempt = 0; attempt < MaxAttempts; attempt++)
                {
                    try
                    {
                        File.WriteAllText(tempPath, json);
                        if (File.Exists(stateFilePath))
                        {
                            File.Replace(tempPath, stateFilePath, null, ignoreMetadataErrors: true);
                        }
                        else
                        {
                            File.Move(tempPath, stateFilePath);
                        }
                        return;
                    }
                    catch (IOException ex) when (attempt + 1 < MaxAttempts)
                    {
                        lastError = ex;
                        Thread.Sleep(RetryDelayMilliseconds);
                    }
                    catch (UnauthorizedAccessException ex) when (attempt + 1 < MaxAttempts)
                    {
                        lastError = ex;
                        Thread.Sleep(RetryDelayMilliseconds);
                    }
                }
            }
            finally
            {
                if (File.Exists(tempPath))
                {
                    try
                    {
                        File.Delete(tempPath);
                    }
                    catch (IOException)
                    {
                    }
                }
            }

            throw new IOException($"写入状态文件失败: {stateFilePath}", lastError);
        }
    }

    private static string BuildJson(OracleRunnerStateFile state)
    {
        StringBuilder builder = new StringBuilder();
        builder.AppendLine("{");
        AppendField(builder, "request_id", state.RequestId.ToString(CultureInfo.InvariantCulture), quote: false, trailingComma: true);
        AppendField(builder, "status", RunnerStateProtocol.ToStatusText(state.Status), quote: true, trailingComma: true);
        AppendField(builder, "target_script", state.TargetScript, quote: true, trailingComma: true);
        AppendField(
            builder,
            "timeout_seconds",
            state.TimeoutSeconds?.ToString(CultureInfo.InvariantCulture),
            quote: false,
            trailingComma: true
        );
        AppendField(builder, "started_at", state.StartedAt, quote: true, trailingComma: true);
        AppendField(builder, "finished_at", state.FinishedAt, quote: true, trailingComma: true);
        AppendField(builder, "last_error", state.LastError, quote: true, trailingComma: false);
        builder.AppendLine("}");
        return builder.ToString();
    }

    private static void AppendField(StringBuilder builder, string key, string? value, bool quote, bool trailingComma)
    {
        builder.Append("  \"");
        builder.Append(key);
        builder.Append("\": ");
        if (value == null)
        {
            builder.Append("null");
        }
        else if (quote)
        {
            builder.Append('"');
            builder.Append(EscapeJsonString(value));
            builder.Append('"');
        }
        else
        {
            builder.Append(value);
        }

        if (trailingComma)
        {
            builder.Append(',');
        }

        builder.AppendLine();
    }

    private static string EscapeJsonString(string value)
    {
        return value.Replace("\\", "\\\\").Replace("\"", "\\\"");
    }

    private static int ReadInt(string json, string key)
    {
        string? value = ReadRawValue(json, key);
        return int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int result) ? result : 0;
    }

    private static double? ReadNullableDouble(string json, string key)
    {
        string? value = ReadRawValue(json, key);
        if (string.IsNullOrWhiteSpace(value) || value == "null")
        {
            return null;
        }

        return double.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out double result)
            ? result
            : null;
    }

    private static string? ReadString(string json, string key)
    {
        string? value = ReadRawValue(json, key);
        if (string.IsNullOrWhiteSpace(value) || value == "null")
        {
            return null;
        }

        if (value.Length >= 2 && value[0] == '"' && value[^1] == '"')
        {
            return value[1..^1].Replace("\\\"", "\"").Replace("\\\\", "\\");
        }

        return value;
    }

    private static string? ReadRawValue(string json, string key)
    {
        Match match = Regex.Match(
            json,
            $"\"{Regex.Escape(key)}\"\\s*:\\s*(null|\"(?:\\\\.|[^\"])*\"|-?[0-9]+(?:\\.[0-9]+)?)",
            RegexOptions.Multiline
        );
        return match.Success ? match.Groups[1].Value : null;
    }
}
