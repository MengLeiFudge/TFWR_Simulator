// 记录原版解释器实际扣费；各无人机的累计费用不能相加当作世界耗时。
public sealed class ExecutionProfile
{
    private sealed record Location(string Module, int Line, string Source);

    public sealed class Fee
    {
        public required string Module { get; init; }
        public required int Line { get; init; }
        public required string Source { get; init; }
        public required int Drone { get; init; }
        public required string CallPath { get; init; }
        public long Nodes { get; set; }
        public long ApiCalls { get; set; }
        public long CompletedApiCalls { get; set; }
        public double InterpreterTicks { get; set; }
        public double ApiTicks { get; set; }
        public long WaitForNanoseconds { get; set; }
    }

    private readonly Dictionary<BoxedNodeParams, Location> locations = new();
    private readonly Dictionary<CodeWindow, int[]> lineStarts = new();
    private readonly Dictionary<Scope, string> callPaths = new();
    private readonly Dictionary<(Location location, int drone, string path), Fee> fees = new();

    public void CountNode(Node node, ProgramState state) => Point(node, state).Nodes++;

    public void Charge(Node node, ProgramState state, double ticks) => Point(node, state).InterpreterTicks += ticks;

    public Fee Begin(Node node, ProgramState state)
    {
        Fee fee = Point(node, state);
        fee.ApiCalls++;
        return fee;
    }

    /// <summary>保存调用完成时的实际API费用；wait_for时延含调度等待，不能跨机器相加。</summary>
    public static void Complete(Fee fee, string name, double ticks, long elapsedNanoseconds)
    {
        fee.CompletedApiCalls++;
        fee.ApiTicks += ticks;
        if (name == "wait_for") fee.WaitForNanoseconds += Math.Max(0, elapsedNanoseconds);
    }

    private Fee Point(Node node, ProgramState state)
    {
        if (!locations.TryGetValue(node.boxedParams, out Location? location))
        {
            CodeWindow window = node.boxedParams.codeWindow;
            string text = window.CodeInput.text;
            if (!lineStarts.TryGetValue(window, out int[]? starts))
            {
                var offsets = new List<int> { 0 };
                for (int i = 0; i < text.Length; i++) if (text[i] == '\n') offsets.Add(i + 1);
                starts = offsets.ToArray();
                lineStarts.Add(window, starts);
            }
            int offset = Math.Clamp(node.boxedParams.wordStart, 0, text.Length);
            int line = Array.BinarySearch(starts, offset);
            if (line < 0) line = ~line - 1;
            int end = text.IndexOf('\n', starts[line]);
            if (end < 0) end = text.Length;
            location = new Location(window.SourcePath, line + 1, text[starts[line]..end].Trim());
            locations.Add(node.boxedParams, location);
        }
        Scope scope = state.CurrentScope;
        if (!callPaths.TryGetValue(scope, out string? path))
        {
            path = string.Join(" -> ", state.moduleState.callStack.Reverse().Select(frame =>
                $"{frame.functionNode.boxedParams.codeWindow.fileName}.{frame.functionNode.FuncName}"));
            if (path.Length == 0) path = "<module>";
            callPaths.Add(scope, path);
        }
        var key = (location, state.DroneId, path);
        if (!fees.TryGetValue(key, out Fee? fee))
        {
            fee = new Fee { Module = location.Module, Line = location.Line, Source = location.Source,
                            Drone = state.DroneId, CallPath = path };
            fees.Add(key, fee);
        }
        return fee;
    }

    public object Report(Simulation sim, bool stateComplete, IReadOnlyDictionary<string, string> sources, int pendingCalls)
    {
        Fee[] rows = fees.Values.OrderByDescending(fee => fee.InterpreterTicks)
            .ThenBy(fee => fee.Module, StringComparer.Ordinal).ThenBy(fee => fee.Line)
            .ThenBy(fee => fee.Drone).ThenBy(fee => fee.CallPath, StringComparer.Ordinal).ToArray();
        return new
        {
            schema_version = 1, state_complete = stateComplete, execution_finished = !sim.IsExecuting(),
            game_seconds = sim.CurrentTime.Seconds, nanoseconds = sim.CurrentTime.nanoseconds,
            clock_basis = "native_simulation_current_time",
            tick_basis = "exclusive_charged_operations; node_count_is_not_ticks",
            wait_basis = "wait_for_issue_to_return; overlaps_between_drones",
            dependencies = sources, pending_api_calls = pendingCalls,
            totals = new
            {
                interpreter_nodes = rows.Sum(fee => fee.Nodes), interpreter_ticks = rows.Sum(fee => fee.InterpreterTicks),
                api_calls = rows.Sum(fee => fee.ApiCalls), completed_api_calls = rows.Sum(fee => fee.CompletedApiCalls),
                api_ticks = rows.Sum(fee => fee.ApiTicks)
            },
            drones = rows.GroupBy(fee => fee.Drone).OrderBy(group => group.Key).Select(group => new
            {
                drone = group.Key, interpreter_ticks = group.Sum(fee => fee.InterpreterTicks),
                api_ticks = group.Sum(fee => fee.ApiTicks),
                wait_for_latency_game_seconds = group.Sum(fee => fee.WaitForNanoseconds) / 1_000_000_000.0
            }).ToArray(),
            hot_spots = rows.Select(fee => new
            {
                module = fee.Module, line = fee.Line, source = fee.Source, drone = fee.Drone, call_path = fee.CallPath,
                interpreter_nodes = fee.Nodes, interpreter_ticks = fee.InterpreterTicks,
                api_calls = fee.ApiCalls, completed_api_calls = fee.CompletedApiCalls, api_ticks = fee.ApiTicks,
                wait_for_latency_game_seconds = fee.WaitForNanoseconds / 1_000_000_000.0
            }).ToArray()
        };
    }
}
