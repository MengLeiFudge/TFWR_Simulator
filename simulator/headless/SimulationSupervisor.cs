using System.Diagnostics;
using System.Reflection;
using System.Text.Json.Nodes;

// 每个seed使用独立进程：原版静态资源不会在线程间串扰，长API也受墙钟硬限制。
public static class SimulationSupervisor
{
    public static async Task<JsonObject> Run(SimulationOptions options)
    {
        var clock = Stopwatch.StartNew();
        using var slots = new SemaphoreSlim(Math.Min(options.Jobs, options.Seeds.Length));
        var tasks = options.Seeds.Select(async seed =>
        {
            await slots.WaitAsync();
            try
            {
                double remaining = options.WallSeconds - clock.Elapsed.TotalSeconds;
                return remaining <= 0 ? Failure(seed, "not_started", "Shared wall budget exhausted") : await RunOne(options, seed, remaining);
            }
            finally { slots.Release(); }
        });
        JsonObject[] reports = await Task.WhenAll(tasks);
        if (reports.Length == 1) return reports[0];
        return new JsonObject
        {
            ["backend"] = "csharp-native", ["kind"] = "seed_batch", ["wall_seconds"] = clock.Elapsed.TotalSeconds,
            ["shared_wall_limit"] = options.WallSeconds,
            ["reports"] = new JsonArray(reports.Select(r => (JsonNode)r).ToArray())
        };
    }

    private static async Task<JsonObject> RunOne(SimulationOptions options, int seed, double seconds)
    {
        string executable = Environment.ProcessPath ?? throw new InvalidOperationException("Cannot locate the simulator process");
        var start = new ProcessStartInfo(executable)
        {
            UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8, StandardErrorEncoding = System.Text.Encoding.UTF8
        };
        if (Path.GetFileNameWithoutExtension(executable).Equals("dotnet", StringComparison.OrdinalIgnoreCase))
            start.ArgumentList.Add(Assembly.GetExecutingAssembly().Location);
        foreach (string arg in options.WorkerArguments(seed, seconds)) start.ArgumentList.Add(arg);
        using var process = Process.Start(start) ?? throw new InvalidOperationException("Cannot start simulation worker");
        Task<string> output = process.StandardOutput.ReadToEndAsync();
        var errors = new List<string>();
        Task errorPump = Task.Run(async () =>
        {
            while (await process.StandardError.ReadLineAsync() is string line)
            {
                if (errors.Count < 20) errors.Add(line);
                if (line.StartsWith("progress ", StringComparison.Ordinal)) Console.Error.WriteLine($"seed={seed} {line}");
            }
        });
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(seconds + 1));
        try { await process.WaitForExitAsync(timeout.Token); }
        catch (OperationCanceledException)
        {
            if (!process.HasExited) process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            await errorPump;
            await output;
            return Failure(seed, "hard_timeout", "Worker exceeded the wall budget; no complete state snapshot");
        }
        await errorPump;
        string text = await output;
        try
        {
            var result = JsonNode.Parse(text)?.AsObject() ?? throw new InvalidDataException("Empty worker report");
            result["worker_exit_code"] = process.ExitCode;
            return result;
        }
        catch (Exception ex) when (ex is System.Text.Json.JsonException or InvalidDataException)
        {
            return Failure(seed, "worker_error", string.Join("\n", errors.Append(ex.Message)));
        }
    }
    private static JsonObject Failure(int seed, string reason, string message) => new()
    {
        ["backend"] = "csharp-native", ["seed"] = seed, ["stop_reason"] = reason,
        ["error"] = message, ["state_complete"] = false, ["worker_exit_code"] = 1
    };
}
